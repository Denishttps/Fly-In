from ..models.node import Node, Edge


def calculate_cost(
    target_node: Node, 
    edge: Edge, 
    paths_already_using: int = 0
) -> float:
    base = target_node.base_cost

    capacity = min(target_node.effective_capacity, edge.max_capacity)

    capacity_factor = base / max(capacity, 1)

    congestion_penalty = (paths_already_using / capacity) * 1.5

    return capacity_factor + congestion_penalty
