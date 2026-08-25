import pygame
# from src.core.models import Graph

# from src.core.models import TickResult



class PyGameRenderer:
    def __init__(
        self,
        graph: "Graph",
        history: list["TickResult"],
        width: int,
        height: int
    ):
        self.graph = graph
        self.history = history
        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((400, 300), pygame.RESIZABLE)

    def to_screen_coords(self, norm_x, norm_y, width, height, padding=40):
        x = padding + norm_x * (width - 2 * padding)
        y = padding + norm_y * (height - 2 * padding)
        return int(x), int(y)

























import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

# Пример графа: вершины в нормализованных координатах
nodes = [
    {"x": 0.5, "y": 0.5, "radius": 30},
    {"x": 0.2, "y": 0.3, "radius": 30},
    {"x": 0.8, "y": 0.7, "radius": 30},
]
edges = [(0, 1), (0, 2)]


scale = 1
offset_x, offset_y = 0.0, 0.0
old_w, old_h = screen.get_size()

def to_screen(nx, ny, width, height, scale, offset_x, offset_y, padding=40):
    x = padding + nx * (width - 2 * padding)
    y = padding + ny * (height - 2 * padding)

    cx, cy = width / 2, height / 2
    x = cx + (x - cx) * scale + offset_x
    y = cy + (y - cy) * scale + offset_y

    return int(x), int(y)


running = True
is_resized = False

while running:
    width, height = screen.get_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            scale += event.y * 0.1
            scale = max(0.2, min(5.0, scale))



    screen.fill((255, 255, 255))

    # Пересчитываем экранные координаты каждый кадр
    screen_positions = [to_screen(n["x"], n["y"], width, height, scale, offset_x, offset_y) for n in nodes]

    # Рёбра
    for a, b in edges:
        pygame.draw.line(screen, (150, 150, 150), screen_positions[a], screen_positions[b], 2)

    # Вершины
    for pos, n in zip(screen_positions, nodes):
        radius = n["radius"] * min(width / old_w, height / old_h) * scale
        pygame.draw.circle(screen, (0, 100, 200), pos, radius)

    pygame.display.flip()

    print("Old: ", (old_w, old_h))
    print("New: ", (width, height))
    if is_resized:
        old_w, old_h = width, height
        is_resized = False

pygame.quit()