# Working With Dynamic Paint

## Core Concepts: Canvas and Brush

Before we start, understand these two roles:

1.  **Canvas:** This is the surface that will receive the "paint." It can be a mesh, a collection of meshes, or even a particle system. The canvas is where you define *how* the paint is applied (vertex colors, UV maps, image sequences) and *what kind* of effect it has (paint, wet map, waves).
2.  **Brush:** This is the object that interacts with the canvas. It can be a mesh or a particle system. The brush defines *what kind* of paint it applies (color, strength, type) and *how* it interacts (proximity, overlap).

---

## Tutorial 1: Basic Vertex Paint (Creating a "Wet Map" or "Drip" Effect)

This example will show how to make an object leave a "wet" or colored trail on another object using vertex colors.

### Step 1: Set Up the Scene

1.  **Open Blender** and delete the default cube.
2.  **Add a Plane:** `Shift + A > Mesh > Plane`. Scale it up (e.g., `S` then `5`) so it's a good size for interaction.
3.  **Subdivide the Plane:** Select the Plane, go into `Edit Mode` (`Tab`), right-click > `Subdivide`. In the bottom-left `Operator Panel`, set **Number of Cuts** to `10-20` for decent detail. The more vertices, the smoother the paint effect will be.
4.  **Add a Sphere:** `Shift + A > Mesh > UV Sphere`. Move it above the plane (`G` then `Z`). This will be our brush.

### Step 2: Make the Plane the Canvas

1.  **Select the Plane.**
2.  Go to the **Physics Properties** tab (the icon that looks like a bouncing ball).
3.  Click **Dynamic Paint** and then click **Add Canvas**.
4.  In the `Dynamic Paint` panel:
    *   `Type`: Keep it as `Vertex`. (This will store paint data directly in the mesh's vertices).
    *   `Format`: Change this to **Wet Map**. (This creates a temporary "wetness" effect that fades over time).
    *   Under `Output`:
        *   `Layer Name`: Note the default `dp_wetmap`. This is the name we'll use in the material.
    *   Under `Wetmap`:
        *   `Drip`: Check this if you want "drips" to fall off the wet areas.
        *   `Fade`: Adjust this value (e.g., `0.1` to `0.5`) to control how quickly the wetness disappears.
        *   `Drying Speed`: If using `Wet Map`, this controls how fast it dries.

### Step 3: Make the Sphere the Brush

1.  **Select the Sphere.**
2.  Go to the **Physics Properties** tab.
3.  Click **Dynamic Paint** and then click **Add Brush**.
4.  In the `Dynamic Paint` panel:
    *   `Type`: Keep it as `Paint`.
    *   Under `Paint Source`:
        *   `Source`: `Mesh Volume` is good for solid objects.
    *   Under `Paint`:
        *   `Paint Color`: Choose a color for your "wetness" (e.g., a bright blue or red for visibility).
        *   `Paint Alpha`: Keep at `1.0`.
        *   `Paint Radius`: Adjust to control how wide the brush paints (e.g., `0.5` to `1.0`).
        *   `Strength`: Controls the intensity of the paint.

### Step 4: Animate the Brush

1.  **Select the Sphere.**
2.  Go to **Frame 1** in your timeline.
3.  Move the sphere slightly above the plane. Insert a **Location Keyframe** (`I` then `Location`).
4.  Go to a later frame (e.g., **Frame 50**).
5.  Move the sphere *through* the plane (e.g., `G`, `Z`, then drag down). Insert another **Location Keyframe**.
6.  Go to **Frame 100**. Move the sphere *along* the plane. Insert a **Location Keyframe**.
7.  Go to **Frame 150**. Move the sphere *up and away* from the plane. Insert a **Location Keyframe**.

### Step 5: Visualize the Paint with Materials

The paint data is now being generated, but we need to tell Blender how to display it.

1.  **Select the Plane.**
2.  Go to the **Shading Workspace** or open a **Shader Editor** window.
3.  Create a **New Material** for the Plane.
4.  Add an **Attribute Node**: `Shift + A > Input > Attribute`.
5.  In the `Attribute` Node, type the `Layer Name` you noted from the Canvas settings (e.g., `dp_wetmap`).
6.  Connect the `Color` output of the `Attribute` Node to the `Base Color` input of the `Principled BSDF`.
    *   *Optional:* For a more realistic wet look, you could connect the `Color` output to the `Roughness` or `Transmission` input, perhaps through a `ColorRamp` or `Math` node. For now, color is easiest to see.

### Step 6: Play the Animation

1.  Go back to **Layout Workspace**.
2.  Ensure you are in `Material Preview` or `Rendered` viewport shading (`Z` menu).
3.  **Play the animation** (`Spacebar`). You should see the sphere leave a colored trail on the plane that fades away!

---

## Tutorial 2: Image Sequence Output (Creating Footprints or Displacement)

This example will show how to create an image sequence from Dynamic Paint, which can be used for displacement, decals, or more complex effects. We'll simulate footprints.

### Step 1: Set Up the Scene

1.  **New Blender File** (`File > New > General`).
2.  **Add a Plane:** `Shift + A > Mesh > Plane`. Scale it up (`S` then `5`).
3.  **Subdivide the Plane HEAVILY:** Select the Plane, go into `Edit Mode` (`Tab`), right-click > `Subdivide`. In the bottom-left `Operator Panel`, set **Number of Cuts** to `50-100` (or more, depending on desired detail for displacement). This is crucial for good displacement.
4.  **Add a "Foot" Object:** `Shift + A > Mesh > Cube`. Scale it down (`S`), then stretch it on one axis (`S` then `Y` or `X`) to resemble a foot. Position it above the plane. You can even model a simple foot shape if you like.

### Step 2: Make the Plane the Canvas

1.  **Select the Plane.**
2.  Go to the **Physics Properties** tab.
3.  Click **Dynamic Paint** and then click **Add Canvas**.
4.  In the `Dynamic Paint` panel:
    *   `Type`: Change this to `Image Sequence`.
    *   `Format`: Keep as `Paint Map`.
    *   Under `Output`:
        *   **Important:** Click the folder icon next to `Folder` and choose an empty directory where Blender will save the image sequence. Create a new folder for this if you don't have one.
        *   `Resolution`: Set this to `512` or `1024` for decent image quality. Higher means more detail but larger files and longer bake times.
        *   `Anti-Aliasing`: Increase to `4` or `8` for smoother edges.
        *   `UV Map`: If your plane has a specific UV map you want to use, select it here. (Default `UVMap` is fine for a simple plane).
    *   Under `Paintmap`:
        *   `Displace`: Enable this! This tells Dynamic Paint to use the paint data for displacement.
        *   `Scale`: Set this to a negative value (e.g., `-0.1` to `-0.5`) to make the footprints *indent* rather than bulge.

### Step 3: Make the "Foot" the Brush

1.  **Select the "Foot" object.**
2.  Go to the **Physics Properties** tab.
3.  Click **Dynamic Paint** and then click **Add Brush**.
4.  In the `Dynamic Paint` panel:
    *   `Type`: Keep it as `Paint`.
    *   Under `Paint Source`:
        *   `Source`: `Mesh Volume` works well.
    *   Under `Paint`:
        *   `Paint Color`: Set this to **Black** (`R:0, G:0, B:0`). When used for displacement, black means "no displacement", and white means "full displacement". We want the footprints to be "painted" white.
        *   `Paint Alpha`: Keep at `1.0`.
        *   `Paint Radius`: Adjust.
        *   `Strength`: Controls intensity.
    *   Under `Erase`:
        *   `Enable`: Check this if you want the footprints to eventually fade. Adjust `Threshold` and `Alpha` for the erase speed and intensity. (For permanent footprints, leave this unchecked).

### Step 4: Animate the Brush (Footsteps)

1.  **Select the "Foot" object.**
2.  Go to **Frame 1**. Position the foot above the plane. Insert a **Location Keyframe**.
3.  Go to **Frame 10**. Move the foot down onto the plane. Insert a **Location Keyframe**.
4.  Go to **Frame 20**. Move the foot up from the plane. Insert a **Location Keyframe**.
5.  Go to **Frame 30**. Move the foot to a new position above the plane. Insert a **Location Keyframe**.
6.  Go to **Frame 40**. Move the foot down onto the plane again. Insert a **Location Keyframe**.
7.  Continue this pattern for a few more footsteps.

### Step 5: Bake the Image Sequence

1.  **Select the Plane** (the Canvas).
2.  Go to the **Physics Properties** tab, under `Dynamic Paint`.
3.  Scroll down to the `Dynamic Paint Cache` section.
4.  Set the `End Frame` to match your animation's end frame (e.g., `100` or `150`).
5.  Click **Bake Image Sequence**.
    *   Blender will now calculate the paint data frame by frame and save it as an image sequence in the folder you specified. This might take some time depending on your `Resolution` and animation length.

### Step 6: Visualize Displacement with Materials

Once the bake is complete, we need to set up the material to use these images for displacement.

1.  **Select the Plane.**
2.  Go to the **Shading Workspace** or open a **Shader Editor** window.
3.  Create a **New Material** for the Plane.
4.  Add an **Image Texture Node**: `Shift + A > Texture > Image Texture`.
5.  Click `Open` and navigate to the folder where you baked the image sequence. **Select the *first* image in the sequence** (e.g., `dp_paintmap_0001.png`).
6.  **Crucially:** Check the `Image Sequence` box in the `Image Texture` node. This tells Blender to load the entire sequence.
7.  Set `Color Space` to **Non-Color Data**. (Displacement maps are data, not color).
8.  Add a **Displacement Node**: `Shift + A > Vector > Displacement`.
9.  Connect the `Color` output of the `Image Texture` node to the `Height` input of the `Displacement` node.
10. Connect the `Displacement` output of the `Displacement` node to the `Displacement` input of the `Material Output` node.
11. In the `Displacement` node, set `Scale` to a value that matches your Canvas `Displace Scale` (e.g., `0.1` or `0.05`). Adjust to fine-tune.
12. **Enable Displacement in Material Settings:**
    *   With the Plane still selected, go to the **Material Properties** tab (red sphere icon).
    *   Scroll down to `Settings` > `Surface`.
    *   Change `Displacement` from `Bump Only` to **Displacement and Bump**. (This is essential for true displacement).

### Step 7: Play and See Footprints!

1.  Go back to **Layout Workspace**.
2.  Ensure you are in `Rendered` viewport shading (`Z` menu) for the displacement to be visible.
3.  **Play the animation** (`Spacebar`). You should now see the "foot" object creating real displacement/footprints on the plane!

---

## Key Settings and Tips

### Canvas Settings (Physics Tab > Dynamic Paint > Add Canvas)

*   **Type:**
    *   `Vertex`: Stores paint data directly in vertex colors, UV maps. Good for real-time viewport feedback.
    *   `Image Sequence`: Renders paint to a series of images. Essential for displacement, texture effects, or baking for game engines.
*   **Format:**
    *   `Paint Map`: Basic paint data (black/white or color).
    *   `Wet Map`: Paint that fades over time, with optional drips.
    *   `Waves`: Creates rippling water effects. Requires a highly subdivided mesh.
*   **Output:**
    *   `Layer Name` (Vertex): The name of the vertex color or UV map layer.
    *   `Folder` (Image Sequence): Directory to save images.
    *   `Resolution` (Image Sequence): Pixel dimensions of output images.
    *   `Sub-steps`: How many calculations per frame. Higher for fast-moving brushes to prevent skipped frames.
*   **Wetmap / Paintmap / Waves:** Specific settings for each format, like fade time, drying speed, drip settings, wave properties (damping, spread, speed).
*   **Bake:** Crucial for `Image Sequence` type. Remember to re-bake if you change brush animation or canvas settings.

### Brush Settings (Physics Tab > Dynamic Paint > Add Brush)

*   **Type:**
    *   `Paint`: The default, applies paint data.
    *   `Erase`: Removes paint data.
    *   `Wet`: Simulates wetness, without specific color.
*   **Paint Source:**
    *   `Mesh Volume`: Based on the volume of the brush mesh.
    *   `Proximity`: Based on the distance between the brush and canvas (good for effects like objects *hovering* over snow).
    *   `Particle System`: Uses particles as brushes (e.g., rain drops, confetti).
    *   `Curve`: Uses a curve as a brush (e.g., drawing with a path).
*   **Paint:**
    *   `Paint Color`: The color the brush applies.
    *   `Paint Alpha`: Transparency of the paint.
    *   `Paint Radius`: Size of the brush's influence.
    *   `Strength`: Intensity of the paint.
*   **Erase:**
    *   `Enable`: Makes the brush erase paint.
    *   `Threshold`: How much paint needs to be there before erasing starts.
*   **Dissolve:** Makes the brush dissolve paint over time.

### General Tips for Performance & Quality

*   **Mesh Density:** The canvas needs enough geometry to display detail. For vertex paint or displacement, subdivide it appropriately.
*   **UVs:** If using `Image Sequence`, ensure your canvas has proper UV unwrapping.
*   **Baking:** Always bake image sequences for final renders or if you need to preview complex interactions reliably. Reset the cache before re-baking.
*   **File Paths:** For image sequences, always use a dedicated, empty folder.
*   **Material Setup:** Remember to set up your materials to *use* the Dynamic Paint data via `Attribute` or `Image Texture` nodes.
*   **Viewport Shading:** Use `Material Preview` or `Rendered` mode to see your paint effects. `Solid` mode will not display them.
*   **Updates:** Keep Blender and your GPU drivers updated for optimal performance.

Dynamic Paint is incredibly versatile, so don't hesitate to experiment with different settings and brush/canvas types to achieve unique effects!
