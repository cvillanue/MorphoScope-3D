import bpy


def clear_neurovis_scene():
    for obj in list(bpy.data.objects):
        if obj.name.startswith("NV_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    collection = bpy.data.collections.get("NeuroVis")
    if collection is not None:
        bpy.data.collections.remove(collection)


def create_collection():
    collection = bpy.data.collections.new("NeuroVis")
    bpy.context.scene.collection.children.link(collection)
    return collection


def configure_scene(background_color, fps):
    scene = bpy.context.scene

    engines = {
        item.identifier
        for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
    }

    if "BLENDER_EEVEE" in engines:
        scene.render.engine = "BLENDER_EEVEE"
    elif "BLENDER_EEVEE_NEXT" in engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    else:
        scene.render.engine = "BLENDER_WORKBENCH"

    scene.render.fps = fps
    scene.world.color = background_color
    scene.render.film_transparent = False


def enable_material_preview():
    changed = 0

    for window in bpy.context.window_manager.windows:
        screen = window.screen
        if screen is None:
            continue

        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue

            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "MATERIAL"
                    space.shading.use_scene_world = True
                    space.shading.use_scene_lights = True
                    changed += 1

    print(f"Material Preview enabled in {changed} viewport(s).")
