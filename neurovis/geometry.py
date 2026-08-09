import bpy
from mathutils import Vector


def move_to_collection(obj, collection):
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)
    collection.objects.link(obj)


def create_segment(
    child,
    parent,
    material,
    collection,
    radius_multiplier,
    min_radius,
    curve_resolution,
    bevel_resolution,
):
    curve = bpy.data.curves.new(
        f"NV_Branch_{parent.node_id}_{child.node_id}",
        type="CURVE",
    )
    curve.dimensions = "3D"
    curve.resolution_u = curve_resolution
    curve.bevel_resolution = bevel_resolution
    curve.bevel_depth = max(radius_multiplier, min_radius)

    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (*parent.position, 1.0)
    spline.points[1].co = (*child.position, 1.0)

    denominator = max(radius_multiplier, 1e-9)
    spline.points[0].radius = max(parent.radius, min_radius) / denominator
    spline.points[1].radius = max(child.radius, min_radius) / denominator

    obj = bpy.data.objects.new(curve.name, curve)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def create_soma(nodes, material, collection, soma_scale):
    soma_nodes = [node for node in nodes.values() if node.node_type == 1]

    if not soma_nodes:
        soma_nodes = [
            next(
                node
                for node in nodes.values()
                if node.parent_id == -1 or node.parent_id not in nodes
            )
        ]

    center = sum((node.position for node in soma_nodes), Vector()) / len(soma_nodes)
    radius = max(max(node.radius for node in soma_nodes) * soma_scale, 0.10)

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=4,
        radius=radius,
        location=center,
    )
    soma = bpy.context.object
    soma.name = "NV_Soma"
    move_to_collection(soma, collection)
    soma.data.materials.append(material)
    return soma, center


def create_synapses(nodes, children, material, collection, radius):
    synapses = {}

    for node_id, child_ids in children.items():
        if child_ids:
            continue

        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=radius,
            location=nodes[node_id].position,
        )
        synapse = bpy.context.object
        synapse.name = f"NV_Synapse_{node_id}"
        move_to_collection(synapse, collection)
        synapse.data.materials.append(material)
        synapses[node_id] = synapse

    return synapses
