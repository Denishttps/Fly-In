class SimulationManager:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.current_tick: int = 0

    def step(self, requests: list[MoveRequest]) -> None:
        """
        Исполняет один тик симуляции с учетом ограничений ребер и узлов.
        """
        # 1. Сортируем запросы по приоритету дрона (например, те кто уже долго ждут или в PRIORITY зоне)
        requests.sort(key=lambda req: req.priority, reverse=True)

        approved_moves: list[MoveRequest] = []

        # 2. Фаза проверки и бронирования
        for req in requests:
            # Проверяем 1: Есть ли место на ребре на ТЕКУЩИЙ тик?
            if not req.edge.is_available(self.current_tick):
                continue  # Дрон остается на месте в этом тике

            # Проверяем 2: Будет ли место в цельевом узле (с учетом уже одобренных перемещений)?
            # Учитываем, сколько дронов уйдет из target_node и сколько придет
            if not req.target_node.is_available():
                continue

            # Если всё ок — бронируем ребро
            req.edge.reserve(req.drone_id, self.current_tick)
            approved_moves.append(req)

        # 3. Фаза выполнения одобренных перемещений
        for req in approved_moves:
            req.current_node.remove_drone(req.drone_id)
            req.target_node.add_drone(req.drone_id)

        # 4. Переходим на следующий тик и очищаем старую историю
        self.current_tick += 1
        for edge in self.graph._edges:
            edge.cleanup_old_ticks(self.current_tick)