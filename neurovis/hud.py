import bpy
from mathutils import Vector, Matrix


def create_hud(stats, neuron_name, species_label, material, camera, collection):
    text_data = bpy.data.curves.new("NV_HUDTextData", type="FONT")
    text_data.body = (
        f"{neuron_name}\n"
        f"Species: {species_label}\n\n"
        f"Nodes: {stats.node_count:,}\n"
        f"Segments: {stats.segment_count:,}\n"
        f"Branch points: {stats.branch_points:,}\n"
        f"Terminal leaves: {stats.leaves:,}\n"
        f"Cable length: {stats.cable_length_original:,.1f} µm\n"
        f"Max branch order: {stats.max_branch_order}"
    )
    text_data.align_x = "LEFT"
    text_data.align_y = "TOP"
    text_data.size = 0.18
    text_data.space_line = 1.12
    text_data.extrude = 0.001

    text_object = bpy.data.objects.new("NV_HUD", text_data)
    collection.objects.link(text_object)
    text_object.data.materials.append(material)

    text_object.parent = camera
    text_object.matrix_parent_inverse = Matrix.Identity(4)
    text_object.location = Vector((-1.42, 0.80, -2.25))
    text_object.rotation_euler = (0.0, 0.0, 0.0)
    text_object.hide_select = True
    return text_object
