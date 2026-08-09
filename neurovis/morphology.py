from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from mathutils import Vector
from .swc import SWCNode


@dataclass
class MorphologyStats:
    node_count: int
    segment_count: int
    branch_points: int
    leaves: int
    cable_length_world: float
    cable_length_original: float
    max_branch_order: int
    roots: List[int]
    bounds_min: Vector
    bounds_max: Vector
    center: Vector
    max_distance_from_root: float
    min_radius: float
    max_radius: float


def build_children(nodes: Dict[int, SWCNode]) -> Dict[int, List[int]]:
    children = {node_id: [] for node_id in nodes}
    for node in nodes.values():
        if node.parent_id in children and node.parent_id != node.node_id:
            children[node.parent_id].append(node.node_id)
    return children


def find_roots(nodes: Dict[int, SWCNode]) -> List[int]:
    roots = [
        node.node_id
        for node in nodes.values()
        if node.parent_id == -1 or node.parent_id not in nodes
    ]
    return roots or [min(nodes)]


def branch_orders(nodes, children, roots):
    orders = {}
    stack = [(root, 0) for root in roots]

    while stack:
        node_id, order = stack.pop()
        if node_id in orders:
            continue
        orders[node_id] = order
        increment = 1 if len(children.get(node_id, [])) > 1 else 0
        for child_id in children.get(node_id, []):
            stack.append((child_id, order + increment))

    return orders


def path_distances(nodes, children, roots):
    distances = {}
    stack = [(root, 0.0) for root in roots]

    while stack:
        node_id, distance = stack.pop()
        if node_id in distances and distances[node_id] <= distance:
            continue
        distances[node_id] = distance

        for child_id in children.get(node_id, []):
            segment = (
                nodes[child_id].position - nodes[node_id].position
            ).length
            stack.append((child_id, distance + segment))

    return distances


def root_to_leaf_paths(children, roots, allowed_nodes: Set[int] | None = None):
    paths = []

    def walk(node_id, path):
        if allowed_nodes is not None and node_id not in allowed_nodes:
            return

        new_path = path + [node_id]
        valid_children = [
            child
            for child in children.get(node_id, [])
            if allowed_nodes is None or child in allowed_nodes
        ]

        if not valid_children:
            if len(new_path) > 1:
                paths.append(new_path)
            return

        for child_id in valid_children:
            walk(child_id, new_path)

    for root in roots:
        walk(root, [])

    return paths


def calculate_stats(nodes, children, roots, world_scale):
    cable_length = 0.0
    segment_count = 0

    for node in nodes.values():
        parent = nodes.get(node.parent_id)
        if parent is None or parent.node_id == node.node_id:
            continue
        cable_length += (node.position - parent.position).length
        segment_count += 1

    points = [node.position for node in nodes.values()]
    bounds_min = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    bounds_max = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))

    orders = branch_orders(nodes, children, roots)
    distances = path_distances(nodes, children, roots)
    radii = [node.radius for node in nodes.values()]

    return MorphologyStats(
        node_count=len(nodes),
        segment_count=segment_count,
        branch_points=sum(len(value) > 1 for value in children.values()),
        leaves=sum(len(value) == 0 for value in children.values()),
        cable_length_world=cable_length,
        cable_length_original=cable_length / world_scale,
        max_branch_order=max(orders.values(), default=0),
        roots=roots,
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        center=(bounds_min + bounds_max) * 0.5,
        max_distance_from_root=max(distances.values(), default=0.0),
        min_radius=min(radii, default=0.0),
        max_radius=max(radii, default=1.0),
    )
