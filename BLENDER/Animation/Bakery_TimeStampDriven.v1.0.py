import bpy
import csv
import math

# ============================================================
# CONFIG
# ============================================================

OBJECT_NAME = "ModelGeometry"
CSV_PATH = r"X:\Blender\Project\Path\ExportedData\transient_data\Stem-Track-000_Transients.csv"

FPS = bpy.context.scene.render.fps

PULSE_SCALE = 0.10
PULSE_DURATION_SEC = 0.120  # 120 ms

# ============================================================
# HELPER: SET SUBFRAME
# ============================================================

def set_subframe(scene, frame_float):
    scene.frame_current = int(frame_float)
    scene.frame_subframe = frame_float - int(frame_float)

# ============================================================
# LOAD CSV (ONLY timestamp_sec USED)
# ============================================================

events = []

with open(CSV_PATH, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        timestamp = float(row["timestamp_sec"])
        events.append(timestamp)

print(f"Loaded {len(events)} timestamps from CSV.")

# ============================================================
# GET OBJECT
# ============================================================

scene = bpy.context.scene

obj = bpy.data.objects.get(OBJECT_NAME)
if obj is None:
    raise Exception(f"Object '{OBJECT_NAME}' not found.")

bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='OBJECT')

if obj.animation_data is None:
    obj.animation_data_create()

if obj.animation_data.action is None:
    obj.animation_data.action = bpy.data.actions.new(name=f"{obj.name}_Action")

base_scale = obj.scale.copy()

# ============================================================
# PULSE BAKER (PER EVENT)
# ============================================================

for timestamp_sec in events:

    start_frame_float = timestamp_sec * FPS
    end_frame_float = (timestamp_sec + PULSE_DURATION_SEC) * FPS

    start_frame_int = int(math.floor(start_frame_float))
    end_frame_int = int(math.ceil(end_frame_float))

    for frame in range(start_frame_int, end_frame_int + 1):

        # time within this pulse window
        t = frame / FPS
        cycle_time = t - timestamp_sec  # local time since pulse start

        if 0.0 <= cycle_time <= PULSE_DURATION_SEC:
            phase = cycle_time / PULSE_DURATION_SEC
            scale_factor = 1.0 + PULSE_SCALE * math.sin(math.pi * phase)
        else:
            scale_factor = 1.0

        set_subframe(scene, float(frame))
        obj.scale = base_scale * scale_factor
        obj.keyframe_insert(data_path="scale", frame=scene.frame_current)

print("Timestamp-driven pulse animation baked successfully.")
