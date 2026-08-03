import bpy
import math

# ============================================================
# OBJECT CONFIG
# ============================================================

OBJECT_NAME = "ModelGeometry"

# Animation parameters (temporary procedural pulse)
PULSE_DURATION = 3.0
PULSE_INTERVAL = 9.0
PULSE_SCALE = 0.10

# Pull timeline settings from the initialized scene
scene = bpy.context.scene
FPS = scene.render.fps
TOTAL_FRAMES = scene.frame_end

# ============================================================
# GET OBJECT
# ============================================================

obj = bpy.data.objects.get(OBJECT_NAME)
if obj is None:
    raise Exception(f"Object '{OBJECT_NAME}' not found.")

# ============================================================
# SELECT + ACTIVATE OBJECT
# ============================================================

bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Force object mode
bpy.ops.object.mode_set(mode='OBJECT')

# ============================================================
# ENSURE ACTION EXISTS
# ============================================================

if obj.animation_data is None:
    obj.animation_data_create()

if obj.animation_data.action is None:
    obj.animation_data.action = bpy.data.actions.new(name=f"{obj.name}_Action")

# Store base scale
base_scale = obj.scale.copy()

# ============================================================
# ANIMATION BAKER
# ============================================================

for frame in range(1, TOTAL_FRAMES + 1):

    # Set integer frame (subframes handled separately when needed)
    scene.frame_current = frame
    scene.frame_subframe = 0.0

    # Time in seconds
    t = frame / FPS
    cycle_time = t % PULSE_INTERVAL

    # Procedural pulse logic
    if cycle_time <= PULSE_DURATION:
        phase = cycle_time / PULSE_DURATION
        scale_factor = 1.0 + PULSE_SCALE * math.sin(math.pi * phase)
    else:
        scale_factor = 1.0

    # Apply scale and bake keyframe
    obj.scale = base_scale * scale_factor
    obj.keyframe_insert(data_path="scale", frame=frame)

print("Pulse animation baked successfully.")
