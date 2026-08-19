import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.graph import Graph
    from src.core.models.tick_models import TickResult


BG_COLOR = (24, 28, 36)
EDGE_COLOR = (80, 90, 105)
NODE_COLOR = (45, 120, 210)
NODE_BORDER = (255, 255, 255)
TEXT_COLOR = (240, 240, 240)
DRONE_COLOR = (220, 50, 50)
UI_COLOR = (200, 200, 200)


class PyGameRenderer:
    def __init__(
        self,
        graph: "Graph",             # type: Graph
        history: list["TickResult"],     # type: list[TickResult]
        width: int = 800,
        height: int = 600,
        tick_duration: float = 0.8,
        scale: int = 100,
        offset: tuple[int, int] = (100, 100)
    ):
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height
        self.graph = graph
        self.history = history
        self.scale = scale
        self.offset_x, self.offset_y = offset
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Drone Simulation — Replay")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.ui_font = pygame.font.SysFont("Arial", 18, bold=True)

        self.tick_duration = tick_duration
        self.current_tick_idx: int = 0
        self.progress: float = 0.0
        self.is_paused: bool = False

    def _get_screen_coords(self, node_x: float, node_y: float) -> tuple[int, int]:
        screen_x = int(node_x * self.scale + self.offset_x)
        screen_y = int(node_y * self.scale + self.offset_y)
        return screen_x, screen_y

    def _draw_graph(self) -> None:
        drawn_edges = set()

        for node in self.graph.nodes.values():
            start_pos = self._get_screen_coords(node.x, node.y)

            for edge in node.edges:
                neighbor = edge.target if edge.source == node else edge.source
                edge_id = frozenset([node.name, neighbor.name])
                
                if edge_id not in drawn_edges:
                    end_pos = self._get_screen_coords(neighbor.x, neighbor.y)
                    pygame.draw.aaline(self.screen, EDGE_COLOR, start_pos, end_pos, blend=1)

                    mid_x = (start_pos[0] + end_pos[0]) // 2
                    mid_y = (start_pos[1] + end_pos[1]) // 2
                    cap_text = self.font.render(f"cap:{edge.max_capacity}", True, EDGE_COLOR)
                    self.screen.blit(cap_text, (mid_x - 15, mid_y - 15))
                    
                    drawn_edges.add(edge_id)

        for node in self.graph.nodes.values():
            x, y = self._get_screen_coords(node.x, node.y)
            
            pygame.draw.circle(self.screen, NODE_BORDER, (x, y), 22)
            pygame.draw.circle(self.screen, NODE_COLOR, (x, y), 20)

            text_surface = self.font.render(node.name, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(x, y + 35))
            self.screen.blit(text_surface, text_rect)

    def _get_drone_positions(self, tick_idx: int) -> dict[int, tuple[int, int]]:
        if not self.history or tick_idx < 0 or tick_idx >= len(self.history):
            return {}

        tick_result = self.history[tick_idx]
        positions = {}

        for drone_info in tick_result.drones:
            node_name = drone_info.node_name
            if node_name in self.graph.nodes:
                node = self.graph.nodes[node_name]
                positions[drone_info.drone_id] = self._get_screen_coords(node.x, node.y)

        return positions

    def _draw_drones(self) -> None:
        if not self.history:
            return

        prev_positions = self._get_drone_positions(self.current_tick_idx - 1)
        curr_positions = self._get_drone_positions(self.current_tick_idx)

        for drone_id, (curr_x, curr_y) in curr_positions.items():
            if drone_id in prev_positions:
                prev_x, prev_y = prev_positions[drone_id]
                x = int(prev_x + (curr_x - prev_x) * self.progress)
                y = int(prev_y + (curr_y - prev_y) * self.progress)
            else:
                x, y = curr_x, curr_y

            pygame.draw.circle(self.screen, NODE_BORDER, (x, y), 12)
            pygame.draw.circle(self.screen, DRONE_COLOR, (x, y), 10)

            text = self.font.render(f"D{drone_id}", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)

    def _draw_ui(self) -> None:
        status = "ПАУЗА" if self.is_paused else "ИГРАЕТ"
        total_ticks = len(self.history)
        current = self.current_tick_idx + 1 if self.history else 0

        info_text = f"Тик: {current} / {total_ticks} | Статус: {status}"
        controls_text = "Пробел - Пауза | <- Пред. тик | -> След. тик"

        self.screen.blit(self.ui_font.render(info_text, True, UI_COLOR), (20, 20))
        self.screen.blit(self.ui_font.render(controls_text, True, UI_COLOR), (20, 45))

    def run(self) -> None:
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_RIGHT:
                        if self.current_tick_idx < len(self.history) - 1:
                            self.current_tick_idx += 1
                            self.progress = 0.0
                    elif event.key == pygame.K_LEFT:
                        if self.current_tick_idx > 0:
                            self.current_tick_idx -= 1
                            self.progress = 0.0

            if not self.is_paused and self.history:
                if self.current_tick_idx < len(self.history) - 1:
                    self.progress += dt / self.tick_duration
                    if self.progress >= 1.0:
                        self.progress = 0.0
                        self.current_tick_idx += 1
                else:
                    self.progress = 1.0
                    self.is_paused = True

            self.screen.fill(BG_COLOR)
            self._draw_graph()
            self._draw_drones()
            self._draw_ui()

            pygame.display.flip()

        pygame.quit()