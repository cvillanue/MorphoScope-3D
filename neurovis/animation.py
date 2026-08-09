import bpy
import math


def set_hidden(obj, hidden, frame):
    obj.hide_viewport = hidden
    obj.hide_render = hidden
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.keyframe_insert(data_path="hide_render", frame=frame)


def segment_frames(start, end, rate, minimum):
    return max(minimum, int(math.ceil((end - start).length * rate)))


def create_pulse(material, collection, radius, location, name):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20,
        ring_count=12,
        radius=radius,
        location=location,
    )
    pulse = bpy.context.object
    pulse.name = name

    for old_collection in list(pulse.users_collection):
        old_collection.objects.unlink(pulse)
    collection.objects.link(pulse)

    pulse.data.materials.append(material)
    return pulse


def animate_paths(
    paths,
    nodes,
    synapses,
    material,
    collection,
    radius,
    start_frame,
    frames_per_world_unit,
    minimum_frames,
    synapse_flash_frames,
    max_paths,
):
    if max_paths is not None and len(paths) > max_paths:
        step = len(paths) / max_paths
        paths = [paths[int(index * step)] for index in range(max_paths)]

    end_frames = []

    for path_index, path in enumerate(paths):
        pulse = create_pulse(
            material,
            collection,
            radius,
            nodes[path[0]].position,
            f"NV_Pulse_{path_index:04d}",
        )

        frame = start_frame
        pulse.location = nodes[path[0]].position
        set_hidden(pulse, True, max(0, frame - 1))
        set_hidden(pulse, False, frame)
        pulse.keyframe_insert(data_path="location", frame=frame)

        for previous_id, node_id in zip(path, path[1:]):
            frame += segment_frames(
                nodes[previous_id].position,
                nodes[node_id].position,
                frames_per_world_unit,
                minimum_frames,
            )
            pulse.location = nodes[node_id].position
            pulse.keyframe_insert(data_path="location", frame=frame)

        set_hidden(pulse, True, frame + 1)

        synapse = synapses.get(path[-1])
        if synapse is not None:
            synapse.scale = (1.0, 1.0, 1.0)
            synapse.keyframe_insert(data_path="scale", frame=max(1, frame - 1))
            synapse.scale = (3.0, 3.0, 3.0)
            synapse.keyframe_insert(data_path="scale", frame=frame + 1)
            synapse.scale = (1.0, 1.0, 1.0)
            synapse.keyframe_insert(
                data_path="scale",
                frame=frame + synapse_flash_frames,
            )

        end_frames.append(frame + synapse_flash_frames)

    return max(end_frames, default=start_frame + 1)
