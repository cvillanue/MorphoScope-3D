import bpy


def _set(shader, names, value):
    for name in names:
        socket = shader.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return


def create_material(
    name,
    base_color,
    emission_color=None,
    emission_strength=0.0,
    metallic=0.0,
    roughness=0.35,
):
    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")

    _set(shader, ["Base Color"], (*base_color, 1.0))
    _set(shader, ["Roughness"], roughness)
    _set(shader, ["Metallic"], metallic)

    if emission_color is not None:
        _set(shader, ["Emission Color", "Emission"], (*emission_color, 1.0))
        _set(shader, ["Emission Strength"], emission_strength)

    material.diffuse_color = (*base_color, 1.0)
    return material


def gradient_color(t):
    t = max(0.0, min(1.0, t))

    if t < 0.25:
        local = t / 0.25
        return (0.05, 0.25 + 0.70 * local, 1.0)
    if t < 0.50:
        local = (t - 0.25) / 0.25
        return (0.05 + 0.90 * local, 0.95, 1.0 - 0.85 * local)
    if t < 0.75:
        local = (t - 0.50) / 0.25
        return (0.95, 0.95 - 0.60 * local, 0.15)
    local = (t - 0.75) / 0.25
    return (0.95, 0.35 - 0.25 * local, 0.15 - 0.10 * local)


def create_library(pulse_strength, synapse_strength):
    return {
        0: create_material("NV_Unknown", (0.32, 0.40, 0.58)),
        1: create_material(
            "NV_Soma",
            (0.03, 0.25, 0.95),
            (0.01, 0.10, 1.0),
            2.0,
        ),
        2: create_material(
            "NV_Axon",
            (0.02, 0.90, 0.28),
            (0.01, 0.60, 0.08),
            1.4,
        ),
        3: create_material(
            "NV_BasalDendrite",
            (0.08, 0.32, 0.95),
            (0.02, 0.10, 0.55),
            0.8,
        ),
        4: create_material(
            "NV_ApicalDendrite",
            (0.78, 0.08, 0.92),
            (0.40, 0.02, 0.65),
            0.9,
        ),
        "pulse": create_material(
            "NV_Pulse",
            (1.0, 0.08, 0.005),
            (1.0, 0.015, 0.001),
            pulse_strength,
            roughness=0.12,
        ),
        "synapse": create_material(
            "NV_Synapse",
            (0.01, 1.0, 0.12),
            (0.005, 1.0, 0.03),
            synapse_strength,
            roughness=0.12,
        ),
        "hud": create_material(
            "NV_HUD",
            (0.65, 0.90, 1.0),
            (0.20, 0.70, 1.0),
            3.0,
        ),
    }


def create_heatmap_materials(prefix, count=32):
    result = {}
    for index in range(count):
        t = index / max(count - 1, 1)
        color = gradient_color(t)
        result[index] = create_material(
            f"{prefix}_{index:02d}",
            color,
            tuple(component * 0.30 for component in color),
            0.8,
        )
    return result


def heatmap_index(value, minimum, maximum, count=32):
    if maximum <= minimum:
        return 0
    t = (value - minimum) / (maximum - minimum)
    return min(count - 1, max(0, int(round(t * (count - 1)))))
