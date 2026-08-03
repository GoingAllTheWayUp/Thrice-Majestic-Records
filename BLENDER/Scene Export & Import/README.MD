<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
</head>

<body>

<h1>Blender 5.x Scene Exporter & Importer</h1>

<p>
This document describes two scripts: a Blender 5.x JSON Scene Exporter and a Blender 5.x JSON Scene Importer.  
Together, they provide a deterministic offline pipeline for exporting a complete Blender scene to JSON and reconstructing it later.
</p>

<hr>

<h2>1. Scene Exporter</h2>

<p>
The Scene Exporter walks through every object in the Blender file and writes structured JSON describing geometry, animation, materials, cameras, lights, transforms, and timeline settings.  
All output is written into a folder structure under:
</p>

<pre>X:/Blender/Project/Path/ExportedData</pre>

<h3>1.1 Exported Files</h3>

<pre>
ExportedData/
    timeline.json
    scene.json

    transforms/
        <ObjectName>.json

    models/
        <MeshName>.json

    cameras/
        <CameraName>.json

    lights/
        <LightName>.json

    animations/
        <ObjectName>.json

    materials/
        <MaterialName>.json
</pre>

<h3>1.2 Mesh Export</h3>

<p>Each mesh JSON contains:</p>
<ul>
    <li>Vertices</li>
    <li>Normals</li>
    <li>Triangle faces</li>
    <li>UV coordinates</li>
    <li>Material slot names</li>
</ul>

<h3>1.3 Animation Export (Blender 5.x Channelbag)</h3>

<p>
Animation data is extracted using Blender’s channelbag system:
</p>

<pre>anim_utils.action_get_channelbag_for_slot(action, slot)</pre>

<p>Each animation JSON includes:</p>
<ul>
    <li>Keyframe frame numbers</li>
    <li>Values per array index (XYZ, RGB, etc.)</li>
    <li>Entries sorted by frame</li>
</ul>

<h3>1.4 Material Export</h3>

<p>
Each material is written to its own JSON file. The export includes:
</p>

<ul>
    <li>Material properties</li>
    <li>Node tree</li>
    <li>Node properties</li>
    <li>Input sockets</li>
    <li>Output sockets</li>
    <li>Image texture metadata</li>
    <li>Node links</li>
</ul>

<h3>1.5 Scene Index</h3>

<p>
The master <code>scene.json</code> file contains references to all exported data:
</p>

<ul>
    <li>Object name</li>
    <li>Object type</li>
    <li>Transform JSON path</li>
    <li>Data JSON path (mesh, camera, light)</li>
    <li>Animation JSON path</li>
    <li>Material JSON paths</li>
    <li>Parent object</li>
</ul>

<h3>1.6 Execution</h3>

<p>
The exporter runs immediately when executed:
</p>

<pre>export_scene()</pre>

<hr>

<h2>2. Scene Importer</h2>

<p>
The Scene Importer reconstructs a Blender scene from the JSON files produced by the exporter.  
It performs a full reset of the Blender environment before importing.
</p>

<h3>2.1 Hard Reset</h3>

<p>The importer clears the entire Blender scene:</p>

<ul>
    <li>Deletes all objects</li>
    <li>Deletes all meshes, materials, cameras, lights, images, node groups, actions</li>
    <li>Removes all collections except the master collection</li>
</ul>

<h3>2.2 Timeline Import</h3>

<p>Restores:</p>

<ul>
    <li>FPS</li>
    <li>Frame start</li>
    <li>Frame end</li>
</ul>

<h3>2.3 Material Import</h3>

<p>
Reconstructs materials from diagnostics JSON:
</p>

<ul>
    <li>Creates nodes</li>
    <li>Restores node properties</li>
    <li>Restores input default values</li>
    <li>Loads image textures</li>
    <li>Recreates node links</li>
</ul>

<h3>2.4 Mesh Import</h3>

<p>Rebuilds mesh geometry:</p>

<ul>
    <li>Vertices</li>
    <li>Faces</li>
    <li>UVs</li>
    <li>Material assignments</li>
</ul>

<h3>2.5 Camera Import</h3>

<p>Restores:</p>

<ul>
    <li>Lens</li>
    <li>Sensor size</li>
    <li>Clip start/end</li>
    <li>Camera type</li>
    <li>Shift X/Y</li>
</ul>

<h3>2.6 Light Import</h3>

<p>Restores:</p>

<ul>
    <li>Light type</li>
    <li>Color</li>
    <li>Energy</li>
</ul>

<h3>2.7 Transform Import</h3>

<p>Restores:</p>

<ul>
    <li>Location</li>
    <li>Rotation</li>
    <li>Scale</li>
</ul>

<h3>2.8 Animation Import</h3>

<p>
Animations are baked using keyframe insertion.  
For each keyframe:
</p>

<ul>
    <li>The frame is set</li>
    <li>The transform is applied</li>
    <li>A keyframe is inserted</li>
</ul>

<h3>2.9 Parenting</h3>

<p>
After all objects are created, parent relationships are restored.
</p>

<h3>2.10 Execution</h3>

<p>
The importer runs the full pipeline automatically:
</p>

<pre>run_full_import()</pre>

<hr>

<h2>3. Summary</h2>

<p>
The Scene Exporter and Scene Importer together form a Blender → JSON → Blender pipeline.  
The exporter serializes the entire scene into structured JSON files, and the importer reconstructs the scene exactly from those files.
</p>

</body>
</html>
