<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">



</head>
<body>
This README discusses all three python scripts in this folder. Bakery.v1.0 being the proof that we can write keyframes outside the Animation Workspace. And was a process of discovering the Blender v5+ ChannelBag in light of the former fcurve terminology and gaining access to the appropriate handles in the application via Python. And then the formal application of this insight to further develop my Visual Synchronization products. 
  
<h1>Bakery.v1.0 - Procedural Pulse Animation Baker (Proof Of Concept) </h1>

<p>
This script is a standalone Blender script that generates and bakes a procedural scale-based pulse animation on a single object.  
The script also initializes the scene with timeline settings and writes keyframes directly into a Blender Action.</p>
<hr>
<h2>1. Purpose</h2>
<p>
The script applies a periodic scale modulation (“pulse”) to a specified object and inserts keyframes for every frame in the timeline.  
It is intended for deterministic offline animation generation without external data sources.
</p>
<hr>
<h2>2. Object Configuration</h2>
<p>
The script targets a single object by name:
</p>
<pre>OBJECT_NAME = "Model Geometry"</pre>
<p>
Pulse parameters define the animation behavior:
</p>
<ul>
    <li>PULSE_DURATION — length of the pulse event</li>
    <li>PULSE_INTERVAL — time between pulses</li>
    <li>PULSE_SCALE — amplitude of the scale change</li>
</ul>
<p>
Timeline settings are taken from the active Blender scene:
</p>
<ul>
    <li>Frames per second (FPS)</li>
    <li>Total frame count (frame_end)</li>
</ul>
<hr>
<h2>3. Object Preparation</h2>
<p>
The script performs the following steps:
</p>
<ul>
    <li>Locates the object by name</li>
    <li>Selects and activates the object (Imitates user driven Point + Click UI focus targeting) </li>
    <li>Ensures Blender is in OBJECT mode</li>
    <li>Creates animation data and an Action if none exist</li>
    <li>Stores the object’s base scale for reference</li>
</ul>
<hr>
<h2>4. Pulse Animation Logic</h2>
<p>
For each frame in the timeline:
</p>
<ul>
    <li>The scene is set to the current frame</li>
    <li>Time in seconds is computed</li>
    <li>The script determines whether the frame is inside a pulse event</li>
    <li>A scale factor is computed using a sine function</li>
    <li>The object’s scale is updated</li>
    <li>A keyframe is inserted for the scale property</li>
</ul>
<p>
The pulse shape is defined by:
</p>
<pre>scale_factor = 1.0 + PULSE_SCALE * sin(pi * phase)</pre>
<p>
Outside the pulse window, the scale returns to its base value.
</p>
<hr>
<h2>5. Output</h2>
<p>
The script produces a fully baked scale animation stored in the object’s Action.  
Every frame contains an explicit keyframe, ensuring deterministic playback and compatibility with downstream tools.
</p>
<hr>
<h2>6. Execution</h2>
<p>
The script runs immediately when executed.  
Upon completion, it prints:
</p>
<pre>Pulse animation baked successfully.</pre>

<BR>
<hr>

<h1>transient‑detection.v0.py & Bakery_TimeStampDriven.v1.0.py - Audio Transient → Blender Pulse Animation Pipeline</h1>

<p>
These scripts are two‑stage pipeline for converting audio transients into Blender animation keyframes.  
The system consists of:
</p>
<ul>
    <li>A Python transient detection script (offline audio analysis) [transient‑detection.v0.py]</li>
    <li>A Blender Python script that converts detected timestamps into scale‑based pulse animation [Bakery_TimeStampDriven.v1.0.py]</li>
</ul>
<p>
Together, these scripts allow audio events—such as Instrument Note and Percussion Hits —to drive procedural animation inside Blender with intentional timing.
</p>
<hr>
<h2>1. Transient Detection Script</h2>

<p>
The transient detection script analyzes a WAV file and identifies transient events based on RMS energy thresholds.  
Detected transients are written to a CSV file for downstream use. You will run this script in your system python environment, not in the Blender Scripting Environment.
</p>
<h3>1.1 Purpose</h3>
<p>
Extract precise timestamps of transient events (e.g., kick drum hits) from an audio file.  
These timestamps serve as the input for animation generation in Blender.
</p>
<h3>1.2 Processing Steps</h3>
<ul>
    <li>Loads WAV audio using <code>soundfile</code></li>
    <li>Converts stereo to mono if necessary</li>
    <li>Computes an RMS energy envelope using a hop size and window size</li>
    <li>Detects transients using:
        <ul>
            <li>A rising threshold (start condition)</li>
            <li>A hysteresis threshold (end condition)</li>
            <li>A minimum gap between events</li>
        </ul>
    </li>
    <li>For each transient:
        <ul>
            <li>Records timestamp (seconds)</li>
            <li>Records sample index</li>
            <li>Computes duration</li>
            <li>Computes peak amplitude</li>
        </ul>
    </li>
    <li>Writes all transient data to a CSV file</li>
</ul>
<h3>1.3 Output Format</h3>
<p>The CSV contains:</p>
<pre>
index, timestamp_sec, sample_index, duration_sec, peak
</pre>
<p>
Only <code>timestamp_sec</code> is required by the Blender animation script.
</p>
<hr>
<h2>2. Timestamp‑Driven Pulse Baker (Blender)</h2>
<p>
The Blender script reads the transient CSV and converts each timestamp into a scale‑based pulse animation on a specified object.  
Each transient produces a short, deterministic animation window.
</p>
<h3>2.1 Purpose</h3>
<p>
Convert audio‑derived timestamps into Blender keyframes, producing animation synchronized to the original audio transients.
</p>
<h3>2.2 Processing Steps</h3>
<ul>
    <li>Loads the CSV and extracts <code>timestamp_sec</code> values</li>
    <li>Locates the target Blender object</li>
    <li>Ensures animation data and an Action exist</li>
    <li>Stores the object’s base scale</li>
    <li>For each transient:
        <ul>
            <li>Converts timestamp → frame using scene FPS</li>
            <li>Defines a pulse window using <code>PULSE_DURATION_SEC</code></li>
            <li>Computes a scale factor using a sine function</li>
            <li>Applies scale at subframe precision</li>
            <li>Inserts keyframes for every frame in the pulse window</li>
        </ul>
    </li>
</ul>
<h3>2.3 Pulse Shape</h3>
<p>
The pulse animation in this script uses a normalized sine curve:
</p>
<pre>
scale_factor = 1.0 + PULSE_SCALE * sin(pi * phase)
</pre>
<p>
Where <code>phase</code> runs from 0 to 1 across the pulse duration.
</p>
<h3>2.4 Output</h3>
<p>
The script produces a Blender Action containing baked scale keyframes aligned to each transient timestamp.  
This ensures deterministic playback and compatibility with downstream rendering or export pipelines.
</p>
<hr>
<h2>3. Pipeline Overview</h2>
<p>
The two scripts form a complete audio‑driven animation pipeline:
</p>
<ol>
    <li><strong>Audio → CSV</strong>:  
        The transient detection script analyzes the WAV file and outputs timestamps of transient events.</li>
    <li><strong>CSV → Blender Animation</strong>:  
        The Blender script reads the timestamps and generates pulse animation synchronized to the audio.</li>
</ol>
<p>
This workflow enables precise synchronization between audio events and animated motion inside Blender.
</p>
<hr>
<h2>4. Use Cases</h2>
<ul>
    <li>Music‑driven animation</li>
    <li>Audio‑reactive VFX</li>
    <li>Procedural motion synchronized to beats</li>
    <li>Film and motion graphics pipelines</li>
</ul>
<hr>
<h2>5. Summary</h2>
<p>
The transient detection script extracts event timing from audio, and the Blender pulse baker converts those events into animation.  
Together, they provide a deterministic, reproducible method for generating audio‑synchronized motion inside Blender.
</p>

</body>
</html>
