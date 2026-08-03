import bpy
import json
import os
import mathutils
from bpy_extras import anim_utils  # Blender 5.0 channel bag, access fcurve animation data

EXPORT_ROOT = r"X:/Blender/Project/Path/ExportedData"

# ------------------------------------------------------------
# Utility: JSON-safe conversion
# ------------------------------------------------------------
def safe_value(v):
    # Convert Blender arrays (bpy_prop_array) to list
    if hasattr(v, "__class__") and v.__class__.__name__ == "bpy_prop_array":
        return list(v)

    # Convert mathutils types
    if isinstance(v, (mathutils.Vector, mathutils.Color, mathutils.Euler, mathutils.Quaternion)):
        return list(v)

    # Simple types
    if isinstance(v, (int, float, str, bool)):
        return v

    # Lists/tuples recursively
    if isinstance(v, (list, tuple)):
        return [safe_value(x) for x in v]

    # Fallback
    return str(v)

# ------------------------------------------------------------
# Utility: Write JSON safely
# ------------------------------------------------------------
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------------------------------------
# Export Mesh Geometry
# ------------------------------------------------------------
def export_mesh(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()

    vertices = [list(v.co) for v in mesh.vertices]
    normals = [list(v.normal) for v in mesh.vertices]

    faces = []
    for tri in mesh.loop_triangles:
        faces.append([tri.vertices[0], tri.vertices[1], tri.vertices[2]])

    # UVs (if present)
    uvs = []
    if mesh.uv_layers.active:
        uv_layer = mesh.uv_layers.active.data
        for tri in mesh.loop_triangles:
            tri_uvs = []
            for loop_index in tri.loops:
                tri_uvs.append(list(uv_layer[loop_index].uv))
            uvs.append(tri_uvs)

    materials = [slot.material.name for slot in obj.material_slots if slot.material]

    return {
        "mesh_name": mesh.name,
        "vertices": vertices,
        "normals": normals,
        "faces": faces,
        "uvs": uvs,
        "materials": materials
    }

# ------------------------------------------------------------
# Blender 5.0+ Animation Exporter (Channelbag-based)
# ------------------------------------------------------------
def export_animation(obj):
    anim_data = obj.animation_data
    if anim_data is None:
        return {}

    action = anim_data.action
    slot = anim_data.action_slot

    if action is None or slot is None:
        return {}

    channelbag = anim_utils.action_get_channelbag_for_slot(action, slot)
    if channelbag is None:
        return {}

    anim_out = {}

    for fc in channelbag.fcurves:
        path = fc.data_path
        index = fc.array_index

        if path not in anim_out:
            anim_out[path] = []

        for kp in fc.keyframe_points:
            frame = int(kp.co[0])
            value = kp.co[1]

            existing = next((x for x in anim_out[path] if x["frame"] == frame), None)
            if existing:
                existing["value"][index] = value
            else:
                vec = [None, None, None]
                vec[index] = value
                anim_out[path].append({"frame": frame, "value": vec})

    for path in anim_out:
        anim_out[path].sort(key=lambda x: x["frame"])

    return anim_out

# ------------------------------------------------------------
# Export Materials for a single object (diagnostics-accurate)
# ------------------------------------------------------------
def export_object_materials(obj):
    """
    Mirrors Blender 5.1.2 Material Diagnostics Exporter behavior,
    but per object, and writes each material to its own JSON file.
    Returns a list of material JSON paths for this object.
    """
    material_paths = []

    for slot in obj.material_slots:
        mat = slot.material
        if mat is None:
            continue

        mat_entry = {
            "slot_name": slot.name,
            "material_name": mat.name,
            "use_nodes": mat.use_nodes,
            "material_properties": {},
            "nodes": [],
            "links": []
        }

        # Material properties (same logic as diagnostics exporter)
        for attr in dir(mat):
            if attr.startswith("_"):
                continue
            try:
                value = getattr(mat, attr)
                if isinstance(value, (int, float, str, bool, tuple, list, mathutils.Vector)):
                    mat_entry["material_properties"][attr] = safe_value(value)
            except:
                pass

        # Node tree
        if mat.use_nodes and mat.node_tree:
            nt = mat.node_tree

            # Nodes
            for node in nt.nodes:
                node_info = {
                    "name": node.name,
                    "type": node.type,
                    "label": node.label,
                    "location": safe_value(node.location),
                    "inputs": [],
                    "outputs": [],
                    "node_properties": {}
                }

                # Node properties
                for attr in dir(node):
                    if attr.startswith("_"):
                        continue
                    try:
                        value = getattr(node, attr)
                        if isinstance(value, (int, float, str, bool, tuple, list, mathutils.Vector)):
                            node_info["node_properties"][attr] = safe_value(value)
                    except:
                        pass

                # Inputs
                for inp in node.inputs:
                    try:
                        default_val = safe_value(inp.default_value)
                    except:
                        default_val = None

                    node_info["inputs"].append({
                        "name": inp.name,
                        "default_value": default_val,
                        "type": inp.type
                    })

                # Outputs
                for outp in node.outputs:
                    node_info["outputs"].append({
                        "name": outp.name,
                        "type": outp.type
                    })

                # Image Texture Node
                if node.type == "TEX_IMAGE" and node.image:
                    img = node.image
                    node_info["image"] = {
                        "name": img.name,
                        "filepath": img.filepath,
                        "colorspace": img.colorspace_settings.name
                    }

                mat_entry["nodes"].append(node_info)

            # Links
            for link in nt.links:
                mat_entry["links"].append({
                    "from_node": link.from_node.name,
                    "from_socket": link.from_socket.name,
                    "to_node": link.to_node.name,
                    "to_socket": link.to_socket.name
                })

        # Write per-material JSON
        mat_path = os.path.join(EXPORT_ROOT, "materials", f"{mat.name}.json")
        write_json(mat_path, mat_entry)
        material_paths.append(mat_path)

    return material_paths

# ------------------------------------------------------------
# Export Scene
# ------------------------------------------------------------
def export_scene():
    scene_index = {"objects": []}

    # Timeline
    timeline_data = {
        "fps": bpy.context.scene.render.fps,
        "frame_start": bpy.context.scene.frame_start,
        "frame_end": bpy.context.scene.frame_end
    }
    write_json(os.path.join(EXPORT_ROOT, "timeline.json"), timeline_data)

    # Objects
    for obj in bpy.data.objects:
        name = obj.name
        obj_type = obj.type

        # Transform JSON
        transform_path = os.path.join(EXPORT_ROOT, "transforms", f"{name}.json")
        transform_data = {
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale)
        }
        write_json(transform_path, transform_data)

        # Type-specific JSON
        if obj_type == "MESH":
            model_path = os.path.join(EXPORT_ROOT, "models", f"{name}.json")
            model_data = export_mesh(obj)
            write_json(model_path, model_data)
            data_path = model_path

        elif obj_type == "CAMERA":
            cam = obj.data
            cam_path = os.path.join(EXPORT_ROOT, "cameras", f"{name}.json")
            cam_data = {
                "lens": cam.lens,
                "sensor_width": cam.sensor_width,
                "sensor_height": cam.sensor_height,
                "clip_start": cam.clip_start,
                "clip_end": cam.clip_end,
                "type": cam.type,
                "shift_x": cam.shift_x,
                "shift_y": cam.shift_y
            }
            write_json(cam_path, cam_data)
            data_path = cam_path

        elif obj_type == "LIGHT":
            light = obj.data
            light_path = os.path.join(EXPORT_ROOT, "lights", f"{name}.json")
            light_data = {
                "light_type": light.type,
                "color": list(light.color),
                "energy": light.energy
            }
            write_json(light_path, light_data)
            data_path = light_path

        else:
            data_path = None

        # Animation JSON
        anim_path = os.path.join(EXPORT_ROOT, "animations", f"{name}.json")
        anim_data = export_animation(obj)
        write_json(anim_path, anim_data)

        # Materials JSON paths (diagnostics-accurate)
        material_paths = []
        if obj_type == "MESH":
            material_paths = export_object_materials(obj)

        # Scene index entry
        scene_index["objects"].append({
            "name": name,
            "type": obj_type,
            "transform": transform_path,
            "data": data_path,
            "animation": anim_path,
            "materials": material_paths,
            "parent": obj.parent.name if obj.parent else None
        })

    # Master scene.json
    write_json(os.path.join(EXPORT_ROOT, "scene.json"), scene_index)

# ------------------------------------------------------------
# Run Export
# ------------------------------------------------------------
export_scene()