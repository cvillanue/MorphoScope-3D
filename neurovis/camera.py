import bpy
import math
from mathutils import Vector


def create_camera(stats, collection, margin=1.18, elevation=0.28):
    dimensions = stats.bounds_max - stats.bounds_min
    horizontal_span = max(dimensions.x, dimensions.y, 1.0)
    vertical_span = max(dimensions.z, 1.0)
    span = max(horizontal_span, vertical_span)

    camera_data = bpy.data.cameras.new("NV_CameraData")
    camera = bpy.data.objects.new("NV_Camera", camera_data)
    collection.objects.link(camera)

    camera_data.type = "PERSP"
    camera_data.lens = 55
    camera_data.sensor_width = 36

    # Use field of view to estimate a framing distance.
    fov = camera_data.angle
    distance = (span * 0.5 * margin) / max(math.tan(fov * 0.5), 1e-6)

    camera.location = stats.center + Vector((
        span * 0.12,
        -distance,
        span * elevation,
    ))

    target = bpy.data.objects.new("NV_CameraTarget", None)
    target.location = stats.center
    collection.objects.link(target)

    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    bpy.context.scene.camera = camera
    return camera, target


def animate_camera_orbit(camera, target, start_frame, end_frame, orbit_degrees):
    camera.keyframe_insert(data_path="location", frame=start_frame)

    angle = math.radians(orbit_degrees)
    offset = camera.location - target.location
    rotated = Vector((
        offset.x * math.cos(angle) - offset.y * math.sin(angle),
        offset.x * math.sin(angle) + offset.y * math.cos(angle),
        offset.z,
    ))

    camera.location = target.location + rotated
    camera.keyframe_insert(data_path="location", frame=end_frame)
