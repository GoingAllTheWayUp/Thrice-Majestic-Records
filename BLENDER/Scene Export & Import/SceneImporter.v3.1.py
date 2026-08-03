import bpy
import json
import os

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
IMPORT_ROOT = r"X:/Blender/Project/Path/ExportedData"

# ------------------------------------------------------------
# Utility: Read JSON safely
# ------------------------------------------------------------
def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

# ------------------------------------------------------------
# HARD RESET: Clear entire Blender scene
# ------------------------------------------------------------
def clear_scene():
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Delete all datablocks
    datablocks = [
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.actions,
        bpy.data.curves,
        bpy.data.armatures,
        bpy.data.images,
        bpy.data.node_groups
    ]

    for db in datablocks:
        for block in db:
            try:
                db.remove(block)
            except:
                pass

    # Remove all collections except master
    for coll in bpy.data.collections:
        if coll.name != "Collection":
            bpy.data.collections.remove(coll)

    print("Scene cleared.")

# ------------------------------------------------------------
# Import timeline.json
# ------------------------------------------------------------
def import_timeline():
    timeline_path = os.path.join(IMPORT_ROOT, "timeline.json")
    if not os.path.exists(timeline_path):
        print("No timeline.json found.")
        return

    data = read_json(timeline_path)
    scene = bpy.context.scene

    fps = data.get("fps")
    if fps is not None:
        scene.render.fps = fps

    frame_start = data.get("frame_start")
    frame_end = data.get("frame_end")
    if frame_start is not None:
        scene.frame_start = frame_start
    if frame_end is not None:
        scene.frame_end = frame_end

    print("Timeline imported.")

# ------------------------------------------------------------
# Import Material (matches SceneExporter v4.4)
# ------------------------------------------------------------
def import_material(mat_path):
    data = read_json(mat_path)
    mat_name = data.get("material_name", "Material")

    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = data.get("use_nodes", True)

    nt = mat.node_tree
    nt.nodes.clear()

    node_lookup = {}

    # --- Create nodes ---
    for node_data in data.get("nodes", []):
        props = node_data.get("node_properties", {})
        node_id = props.get("bl_idname")

        # Fallback if bl_idname missing
        if not node_id:
            static_type = node_data.get("type", "")
            node_id = "ShaderNode" + static_type.title().replace("_", "")

        try:
            node = nt.nodes.new(node_id)
        except:
            print(f"WARNING: Could not create node {node_id}, skipping.")
            continue

        node.name = node_data.get("name", node_id)
        node.label = node_data.get("label", "")
        loc = node_data.get("location", [0.0, 0.0])
        try:
            node.location = loc
        except:
            pass

        # Restore node properties (best-effort)
        for prop, val in props.items():
            try:
                setattr(node, prop, val)
            except:
                pass

        # Restore input default values
        inputs_data = node_data.get("inputs", [])
        for inp in node.inputs:
            for inp_data in inputs_data:
                if inp.name == inp_data.get("name"):
                    try:
                        inp.default_value = inp_data.get("default_value")
                    except:
                        pass

        # Restore image textures
        if node.type == "TEX_IMAGE" and "image" in node_data:
            img_info = node_data["image"]
            filepath = img_info.get("filepath", "")
            full_path = os.path.join(IMPORT_ROOT, filepath)

            try:
                if filepath and os.path.exists(full_path):
                    img = bpy.data.images.load(full_path)
                elif filepath:
                    img = bpy.data.images.load(filepath)
                else:
                    img = None

                if img:
                    node.image = img
            except:
                print(f"WARNING: Could not load image {filepath}")

        node_lookup[node.name] = node

    # --- Create links ---
    for link_data in data.get("links", []):
        from_node = node_lookup.get(link_data.get("from_node"))
        to_node = node_lookup.get(link_data.get("to_node"))
        from_socket_name = link_data.get("from_socket")
        to_socket_name = link_data.get("to_socket")

        if not from_node or not to_node:
            continue

        try:
            from_socket = next(s for s in from_node.outputs if s.name == from_socket_name)
            to_socket = next(s for s in to_node.inputs if s.name == to_socket_name)
            nt.links.new(from_socket, to_socket)
        except:
            print(f"WARNING: Could not link {link_data}")

    return mat

# ------------------------------------------------------------
# Import mesh from models/<name>.json
# ------------------------------------------------------------
def import_mesh(obj_name, data_path):
    data = read_json(data_path)

    vertices = data.get("vertices", [])
    faces = data.get("faces", [])
    uvs = data.get("uvs", [])
    materials = data.get("materials", [])
    mesh_name = data.get("mesh_name", obj_name)

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.collection.objects.link(obj)

    # UVs
    if uvs:
        uv_layer = mesh.uv_layers.new(name="UVMap")
        loop_index = 0
        for tri_index, poly in enumerate(mesh.polygons):
            tri_uvs = uvs[tri_index]
            for i in range(poly.loop_total):
                uv_layer.data[loop_index].uv = tri_uvs[i]
                loop_index += 1

    # Materials (names only; full materials handled in import_scene)
    for mat_name in materials:
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            mat = bpy.data.materials.new(name=mat_name)
        obj.data.materials.append(mat)

    return obj

# ------------------------------------------------------------
# Import camera
# ------------------------------------------------------------
def import_camera(obj_name, data_path):
    data = read_json(data_path)

    cam_data = bpy.data.cameras.new(obj_name)
    cam_obj = bpy.data.objects.new(obj_name, cam_data)
    bpy.context.collection.objects.link(cam_obj)

    cam_data.lens = data.get("lens", cam_data.lens)
    cam_data.sensor_width = data.get("sensor_width", cam_data.sensor_width)
    cam_data.sensor_height = data.get("sensor_height", cam_data.sensor_height)
    cam_data.clip_start = data.get("clip_start", cam_data.clip_start)
    cam_data.clip_end = data.get("clip_end", cam_data.clip_end)
    cam_data.type = data.get("type", cam_data.type)
    cam_data.shift_x = data.get("shift_x", cam_data.shift_x)
    cam_data.shift_y = data.get("shift_y", cam_data.shift_y)

    return cam_obj

# ------------------------------------------------------------
# Import light
# ------------------------------------------------------------
def import_light(obj_name, data_path):
    data = read_json(data_path)

    light_type = data.get("light_type", "POINT")
    light_data = bpy.data.lights.new(obj_name, type=light_type)
    light_obj = bpy.data.objects.new(obj_name, light_data)
    bpy.context.collection.objects.link(light_obj)

    color = data.get("color")
    if color is not None:
        light_data.color = color

    energy = data.get("energy")
    if energy is not None:
        light_data.energy = energy

    return light_obj

# ------------------------------------------------------------
# Import transform
# ------------------------------------------------------------
def import_transform(obj, transform_path):
    data = read_json(transform_path)

    loc = data.get("location")
    rot = data.get("rotation")
    scale = data.get("scale")

    if loc is not None:
        obj.location = loc
    if rot is not None:
        obj.rotation_euler = rot
    if scale is not None:
        obj.scale = scale

# ------------------------------------------------------------
# Import animation (baked via keyframe_insert)
# ------------------------------------------------------------
def import_animation(obj, anim_path):
    anim_json = read_json(anim_path)
    if not anim_json:
        return

    scene = bpy.context.scene

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    if obj.animation_data is None:
        obj.animation_data_create()

    action = bpy.data.actions.new(name=f"{obj.name}_Action")
    obj.animation_data.action = action

    for data_path, keyframes in anim_json.items():
        for kf in keyframes:
            frame = kf["frame"]
            vec = kf["value"]

            scene.frame_set(frame)

            if data_path == "scale":
                obj.scale = vec
            elif data_path == "location":
                obj.location = vec
            elif data_path == "rotation_euler":
                obj.rotation_euler = vec
            else:
                try:
                    setattr(obj, data_path, vec)
                except:
                    pass

            obj.keyframe_insert(data_path=data_path, frame=frame)

    print(f"Animation baked for {obj.name}")

# ------------------------------------------------------------
# Import scene.json
# ------------------------------------------------------------
def import_scene():
    scene_index_path = os.path.join(IMPORT_ROOT, "scene.json")
    if not os.path.exists(scene_index_path):
        print("scene.json not found.")
        return

    scene_index = read_json(scene_index_path)
    objects_index = scene_index.get("objects", [])

    created_objects = {}

    # First pass: create objects
    for entry in objects_index:
        name = entry["name"]
        obj_type = entry["type"]
        transform_path = entry["transform"]
        data_path = entry["data"]
        anim_path = entry["animation"]
        parent_name = entry.get("parent")
        material_paths = entry.get("materials", [])

        if obj_type == "MESH" and data_path:
            obj = import_mesh(name, data_path)
        elif obj_type == "CAMERA" and data_path:
            obj = import_camera(name, data_path)
        elif obj_type == "LIGHT" and data_path:
            obj = import_light(name, data_path)
        else:
            obj = bpy.data.objects.new(name, None)
            bpy.context.collection.objects.link(obj)

        if transform_path and os.path.exists(transform_path):
            import_transform(obj, transform_path)

        if anim_path and os.path.exists(anim_path):
            import_animation(obj, anim_path)

        # Import and assign full materials
        if obj_type == "MESH" and material_paths:
            obj.data.materials.clear()
            for mat_path in material_paths:
                if os.path.exists(mat_path):
                    mat = import_material(mat_path)
                    obj.data.materials.append(mat)

        created_objects[name] = {
            "object": obj,
            "parent_name": parent_name
        }

    # Second pass: parenting
    for name, info in created_objects.items():
        obj = info["object"]
        parent_name = info["parent_name"]
        if parent_name and parent_name in created_objects:
            obj.parent = created_objects[parent_name]["object"]

    print("Scene imported.")

# ------------------------------------------------------------
# Run full import
# ------------------------------------------------------------
def run_full_import():
    clear_scene()
    import_timeline()
    import_scene()
    print("Full scene import complete.")

run_full_import()
