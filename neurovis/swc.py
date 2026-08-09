from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from mathutils import Vector


@dataclass(frozen=True)
class SWCNode:
    node_id: int
    node_type: int
    position: Vector
    radius: float
    parent_id: int


def load_swc(path: Path, world_scale: float) -> Dict[int, SWCNode]:
    path = Path(path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"SWC file not found: {path}")

    nodes: Dict[int, SWCNode] = {}

    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 7:
                print(f"Skipping malformed line {line_number}: {line}")
                continue

            try:
                node_id = int(float(parts[0]))
                node_type = int(float(parts[1]))
                x, y, z = (float(parts[index]) * world_scale for index in (2, 3, 4))
                radius = abs(float(parts[5]) * world_scale)
                parent_id = int(float(parts[6]))
            except ValueError as exc:
                print(f"Skipping unreadable line {line_number}: {exc}")
                continue

            nodes[node_id] = SWCNode(
                node_id=node_id,
                node_type=node_type,
                position=Vector((x, y, z)),
                radius=radius,
                parent_id=parent_id,
            )

    if not nodes:
        raise ValueError("The SWC file contains no readable morphology nodes.")

    return nodes
