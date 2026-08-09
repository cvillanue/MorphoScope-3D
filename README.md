# MorphoScope - NeuroViz Exploration
*renamed project :)

## Interactive Visualization of Neuronal Morphology and Simulated Signal Propagation

MorphoScope is a software created for reconstructing, animating, and interactively exploring neuronal morphology from SWC reconstructions.

Built with Python, Blender, and Three.js, MorphoScope combines a procedural three-dimensional reconstruction pipeline with a browser-based visualization environment. The project is intended to support exploratory analysis of neuronal structure.

MorphoScope currently consists of two integrated components:

- **MorphoScope Blender Pipeline**  
  Parses SWC morphology, generates three-dimensional neuron geometry, computes structural statistics, creates simulated signal-propagation animations, and exports browser-compatible GLB models.

- **MorphoScope Web Explorer**  
  Loads exported GLB models into an interactive Three.js scene, allowing users to rotate, zoom, pan, and inspect neuronal reconstructions directly in a web browser.

The current Web Explorer displays a prepared neuron model. Browser-based SWC upload and reconstruction are planned features and are not yet implemented.

---

# Live Demo

**MorphoScope Web Explorer**

https://cvillanue.github.io/neurovis-web-explorer/

---

# Overview

Neuronal morphology is commonly stored in the SWC format as a structured collection of nodes. Each node contains a spatial position, radius, anatomical classification, and parent identifier.

Although this representation is compact and computationally useful, raw SWC files are difficult to interpret visually. NeuroVis transforms this tabular morphology into a navigable three-dimensional reconstruction.


This architecture separates morphology processing, three-dimensional authoring, portable model export, and browser rendering into distinct stages.

---

# Current Features

MorphoScope v1.1 currently supports:

- Parsing neuronal reconstructions from SWC files
- Preserving SWC node and parent-child relationships
- Reconstructing neuronal branches procedurally in Blender
- Representing neuronal processes as three-dimensional curves
- Generating branch thickness from node radii
- Computing morphology statistics
- Displaying a morphology statistics HUD in Blender
- Animating simulated signal propagation
- Exporting neuron geometry and animation as GLB
- Loading GLB models in Three.js
- Interactive orbit, zoom, and pan controls
- Public deployment through GitHub Pages

The following features are not currently available:

- Uploading an SWC file directly through the website
- Reconstructing arbitrary SWC files in the browser
- Selecting individual branches in the Web Explorer
- Performing biophysical membrane simulations
- Editing morphology from the browser

---

# Development Process

Developing MorphoScope required integrating several independent technologies into a unified visualization pipeline.

The overall workflow consists of five principal stages.

## 1. SWC Parsing

Neuronal reconstructions are loaded from SWC morphology files.

An SWC file typically represents each neuronal point as a row containing:

```text
node_id
node_type
x
y
z
radius
parent_id
```

The parser converts these rows into an internal morphology representation.

For each node, MorphoScope stores:

- A unique node identifier
- Anatomical classification
- Three-dimensional coordinates
- Radius
- Parent identifier
- Child relationships

The parent identifier plays a key importance because it defines the topology of the neuron. A node is not treated as an isolated point. It is treated as part of a graph whose edges represent neuronal segments.

During parsing, NeuroVis reconstructs:

- Parent-child relationships
- Connected segments
- Branch points
- Terminal nodes
- Root or soma-associated nodes
- Branch hierarchy

This graph structure is then used by the geometry, statistics, and animation systems.

### Why this stage matters

The SWC file does not directly contain rendered branches. It contains points and relationships.

NeuroVis must determine which pairs of nodes should be connected and preserve the original morphology without introducing artificial connections. Errors at this stage would distort every downstream calculation and visualization.

---

## 2. Geometry Generation

After parsing, MorphoScope converts the morphology graph into Blender geometry.

Each parent-child connection becomes a neuronal segment. These segments are represented using Blender curve objects rather than manually constructed meshes.

A typical generated object follows a naming pattern such as:

```text
NV_Branch_2557_2558
```

This indicates a branch segment connecting parent node `2557` to child node `2558`.

### Curve-based representation

Curves were selected because they are well suited for elongated biological structures.

Each branch contains:

- A start position
- An end position
- A radius or thickness
- A curve data block
- A material assignment
- Animation properties

Blender evaluates the curve and generates visible three-dimensional thickness around its path.

This approach provides several advantages:

- Smooth neuronal processes
- Efficient procedural construction
- Adjustable branch thickness
- Easier animation than manually generated polygon meshes
- Preservation of the original SWC coordinates

### Radius handling

Node radii from the SWC reconstruction are used to influence branch thickness.

This allows thicker proximal structures and thinner distal branches to remain visually distinct.

The generated geometry is therefore not only topologically related to the SWC data, but also reflects local morphological scale.

### Soma and terminal markers

Additional geometry may be generated for:

- Soma-associated structures
- Terminal leaves
- Branch points
- Signal markers
- Synaptic visualization elements

These objects are placed using the same coordinate system as the neuronal branches.

### Blender scene organization

Generated objects are placed inside a dedicated MorphoScope collection.

A typical scene contains:

```text
Scene Collection
├── Camera
├── Light
└── NeuroVis
    ├── NV_Branch_1_2
    ├── NV_Branch_1_3
    ├── NV_Branch_4_5
    ├── ...
    ├── Terminal markers
    ├── Signal markers
    └── HUD objects
```

Organizing the generated objects in a collection makes the reconstruction easier to inspect, animate, export, and remove.

---


## Animation workspace

The signal animation is viewed through Blender's Animation workspace or timeline.

The animation timeline allows the user to:

- Play and pause the signal sequence
- Move to a specific frame
- Inspect activation timing
- Review branch-by-branch propagation
- Adjust the start and end frames

## Blender screenshot

<img width="1495" height="734" alt="Screenshot 2026-08-04 at 5 52 50 PM" src="https://github.com/user-attachments/assets/ed721ded-65cf-4f04-96ea-bd11f1dc1e05" />


> MorphoScope reconstruction displayed in Blender. Individual neuronal branches are represented as procedural curve objects, with branch-specific materials and animated signal markers.

---

## 3. Morphological Analysis

MorphoScope computes structural statistics directly from the parsed morphology. These measurements summarize the complexity and extent of the reconstruction.
Current measurements include:

### Node count

The total number of SWC nodes in the reconstruction.

### Segment count

The number of valid parent-child connections.

For a connected tree, the segment count is often close to the node count minus one, although malformed or disconnected data can alter this relationship.

### Branch points

Nodes with multiple children are classified as branch points. These points represent locations where a neuronal process divides into multiple paths.

### Terminal leaves

Nodes with no children are classified as terminal leaves. These correspond to the distal endpoints of the reconstructed arbor.

### Cable length

Cable length is calculated by summing the Euclidean distance between connected parent-child nodes.

For a segment connecting nodes \(i\) and \(j\):

```text
length = sqrt(
    (xj - xi)^2 +
    (yj - yi)^2 +
    (zj - zi)^2
)
```

The total cable length is the sum of all segment lengths.

### Maximum branch order

Branch order estimates the hierarchical depth of the arbor.

As the morphology progresses away from the root, branching events increase the order assigned to downstream processes.

### Statistics HUD

The computed values are displayed inside Blender using a camera-parented text object.

This ensures that the statistics remain visible while the camera moves through the scene.

A typical HUD includes:

```text
Neuron name
Species

Nodes
Segments
Branch points
Terminal leaves
Cable length
Maximum branch order
```

---

## 4. Spike Propagation Animation

MorphoScope creates a visual simulation of neural signal propagation. This animation does not solve the Hodgkin-Huxley equations and does not attempt to reproduce membrane voltage dynamics.
Instead, it uses the neuron graph to create an intuitive temporal visualization of activity moving through the neuronal arbor.

### Propagation sequence

The animation system determines an activation order based on the connectivity of the morphology. Each branch receives an activation time or frame.


### Signal markers

Additional spheres or markers may be placed at branch points and terminal locations. These markers help communicate the progression of the signal across a dense three-dimensional arbor.

### Why use a visual simulation?

A full electrophysiological simulation requires membrane properties, channel conductances, compartmental models, integration methods, and boundary conditions.

Those values are not contained in a standard SWC file.

MorphoScope therefore separates:

- **Morphology-based visualization**
- **Biophysical simulation**

The current animation is intended as an explanatory and exploratory visualization. It should not be interpreted as a quantitative prediction of action-potential velocity, attenuation, or membrane potential.

---

## 5. GLB Export

After reconstruction and animation, the Blender scene is exported as a GLB file.

GLB is the binary form of glTF and is well suited for browser-based three-dimensional applications.

It can contain:

- Geometry
- Object transforms
- Scene hierarchy
- Animation clips
- Cameras
- Lights
- Materials

## Export settings used for NeuroVis

The successful export configuration used:

```text
Format: glTF Binary (.glb)
Selected Objects: enabled when testing individual branches
Animation: enabled
Materials: disabled
```

### Material export issue

During development, the Blender glTF exporter failed with a material lookup error:

```text
KeyError
export_settings['material_identifiers'][id(blender_mat)]
```

The error occurred while Blender attempted to gather materials assigned to procedurally generated curve objects.

The geometry and animation were valid. This was confirmed by exporting a selected branch with materials disabled.

The practical solution was:

```text
Materials: None
Animation: On
```

This preserved the exported geometry and animation while avoiding the incompatible Blender material path.

Materials are then assigned inside the Three.js application.

### Removing helper objects

The first exported model also contained Blender's default cube. This object was removed from the Blender scene before re-exporting.
Only objects intended for the final visualization should be included in the GLB.

---

# MorphoScope Web Explorer

The Web Explorer is a Vite and Three.js application that loads the exported neuron model. Its current role is to provide a portable and interactive browser viewer.
<img width="824" height="695" alt="NeuronModel_Browser" src="https://github.com/user-attachments/assets/d874285a-2e0d-4de5-94cf-f052c324d2f5" />


## Model loading

The GLB file is stored at:

```text
public/models/neuron.glb
```

Vite serves this asset through the application's public path.

The model is loaded with Three.js `GLTFLoader`.

Because the site is deployed under a GitHub repository subpath, the model URL uses Vite's base path:

```javascript
`${import.meta.env.BASE_URL}models/neuron.glb`
```

This allows the model to load correctly both locally and on GitHub Pages.


## Interactive controls

The current browser controls are:

```text
Left mouse drag     Rotate
Mouse wheel         Zoom
Right mouse drag    Pan
Reset button        Restore camera position
```

## Automatic camera framing

After loading, the application computes the model's bounding box.

The bounding box is used to:

- Determine the center of the model
- Move the model to the scene origin
- Estimate an appropriate camera distance
- Adjust the camera clipping planes
- Save the initial orbit-control state

This prevents neurons with different spatial scales from appearing off-screen.



---

# Technical Challenges

The development process involved several practical challenges.

## Blender module organization

The MorphoScope pipeline was separated into focused Python modules, including:

```text
animation.py
camera.py
geometry.py
hud.py
materials.py
morphology.py
scene.py
swc.py
```

This required ensuring that Blender could locate the project package and import the modules correctly.

## Curve-based export

The neuron consisted of thousands of Blender curve objects. During GLB export, Blender converts non-mesh objects into mesh primitives internally.
This introduced performance and material-compatibility concerns.

## Material compatibility

Procedural and animated materials triggered a glTF exporter error. Disabling material export provided a reliable geometry and animation pipeline.

## Browser asset paths

The model initially loaded locally but failed under the Vite production preview path. The issue was caused by using an absolute root path:

```javascript
"/models/neuron.glb"
```

The corrected path uses:

```javascript
`${import.meta.env.BASE_URL}models/neuron.glb`
```

## GitHub authentication

GitHub no longer supports password authentication for Git operations over HTTPS. ;___;

The repository was authenticated using GitHub CLI:

```bash
gh auth login
```

---

# Repository Structure

```text
NeuroVis_v1_1/
├── config.py
├── run_neurovis.py
├── neurovis/
│   ├── __init__.py
│   ├── animation.py
│   ├── camera.py
│   ├── geometry.py
│   ├── hud.py
│   ├── materials.py
│   ├── morphology.py
│   ├── scene.py
│   └── swc.py
│
└── neurovis-web-explorer/
    ├── .github/
    │   └── workflows/
    │       └── deploy.yml
    ├── public/
    │   └── models/
    │       └── neuron.glb
    ├── src/
    │   ├── main.js
    │   └── style.css
    ├── index.html
    ├── package.json
    ├── package-lock.json
    └── vite.config.js
```

---

# Running the Web Explorer Locally

Navigate to the web project:

```bash
cd neurovis-web-explorer
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:5173/
```

To test the production build:

```bash
npm run build
npm run preview
```

With the GitHub Pages base path configured, the preview URL may resemble:

```text
http://localhost:4173/neurovis-web-explorer/
```

---

# Updating the Displayed Neuron

After exporting a new GLB from Blender, copy it into the web project:

```bash
cp /path/to/new-export.glb public/models/neuron.glb
```

Then rebuild or refresh the development server.

For production deployment:

```bash
git add .
git commit -m "Update neuron model"
git push
```

The GitHub Actions workflow will rebuild and redeploy the site automatically.

---

# Research Motivation

Modern neuroscience increasingly relies on digital neuronal reconstructions to investigate the relationship between anatomy and function.
Although SWC datasets provide detailed morphology, the format itself is not designed for intuitive visual exploration. Static figures can communicate overall structure, but they limit inspection of depth and spatial organization.
The project demonstrates how neuronal structure can be transformed from a coordinate graph into an accessible computational object that can be animated, and shared.

---

# Planned Development

The following capabilities are planned but are not currently implemented:

- Browser-based SWC file upload
- Client-side SWC parsing
- Automatic browser-side neuron reconstruction
- Branch hover highlighting
- Branch selection and metadata inspection
- Play, pause, and speed controls
- Timeline scrubbing
- Branch-order color mapping
- Radius-based color mapping
- Distance-from-soma visualization
- Axon and dendrite classification
- Multiple neuron comparison
- Synapse visualization
- Screenshot export
- NeuroMorpho.Org integration
- Morphological measurement tools
- WebXR or virtual-reality exploration

---

# Status

MorphoScope v1.1 is an active prototype. The current release demonstrates the full pipeline from SWC morphology to an interactive browser visualization:

```text
SWC
-> Python
-> Blender
-> GLB
-> Three.js
-> GitHub Pages
```

Future releases will focus on moving more morphology processing and interactivity directly into the browser.

---
# Data Source and References

## Neuronal Morphology Data

The neuronal reconstruction used in the current NeuroVis Web Explorer is **L20N4**, a turtle cortical neuron obtained from NeuroMorpho.Org.

The dataset is part of the **Laurent Archive** and includes three-dimensional morphological information describing the soma, dendrites, and axon. NeuroMorpho.Org classifies the neuron as a turtle principal cell with pyramidal morphology from the dorsal cortex. The archive notes moderate dendritic physical integrity and an incomplete axonal reconstruction.

Dataset page:

```text
https://neuromorpho.org/neuron_info.jsp?neuron_name=L20N4
