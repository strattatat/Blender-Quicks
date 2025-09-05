import bpy
import random
from bpy.props import FloatVectorProperty

bl_info = {
    "name": "Stratt's Tools",
    "author": "Strattatat",
    "version": (1, 0),
    "blender": (4, 1, 0), # Compatible with Blender 4.1+
    "location": "3D View > Sidebar > Stratt's Tools",
    "description": "Custom tools for scene management, lighting, and camera setup, liberated for maximum control.",
    "category": "Tools",
}

# --- OPERATORS: The Core Mechanics of Stratt's Power ---

class STRATT_OT_PurgeUnusedData(bpy.types.Operator):
    """Purge all unused data blocks from the blend file, clearing the digital clutter."""
    bl_idname = "stratt.purge_unused_data"
    bl_label = "Purge Unused Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # The 'orphans_purge' operator is a direct and efficient command to eradicate all
        # unlinked data, including meshes, materials, textures, and more, that are not
        # actively referenced by any scene objects. This is critical for maintaining
        # lean, performant Blender files.
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, "Unused data blocks purged with extreme prejudice.")
        return {'FINISHED'}

class STRATT_OT_AddTriLighting(bpy.types.Operator):
    """Add a perfectly balanced three-point lighting setup to your scene, illuminating your creations with authority."""
    bl_idname = "stratt.add_tri_lighting"
    bl_label = "Add Tri-Lighting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        # Key Light: The primary source, establishing the dominant illumination and shadows.
        # Positioned to provide definition and form.
        key_light_data = bpy.data.lights.new(name="Key_Light", type='AREA')
        key_light_data.energy = 1000  # High intensity for a strong primary light.
        key_light_data.size = 1.0     # Defines the soft/hard quality of shadows.
        key_light_data.color = (1.0, 0.95, 0.9) # A subtle warm tint for natural light.
        key_light_obj = bpy.data.objects.new(name="Key_Light", object_data=key_light_data)
        scene.collection.objects.link(key_light_obj)
        key_light_obj.location = (5, -7, 5) # Offset for dramatic effect.
        key_light_obj.rotation_euler = (0.7, 0.0, 0.7) # Angled towards the origin.

        # Fill Light: Softens shadows cast by the key light, providing detail in darker areas.
        # It's less intense than the key light and often has a slightly cooler tint.
        fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
        fill_light_data.energy = 400 # Approximately 1/2 to 1/3 the key light's energy.
        fill_light_data.size = 1.5   # Larger area for softer shadows.
        fill_light_data.color = (0.9, 0.95, 1.0) # A slight cool tint.
        fill_light_obj = bpy.data.objects.new(name="Fill_Light", object_data=fill_light_data)
        scene.collection.objects.link(fill_light_obj)
        fill_light_obj.location = (-7, -5, 4) # Opposite side of the key light.
        fill_light_obj.rotation_euler = (0.8, 0.0, -0.8)

        # Back/Rim Light: Separates the subject from the background, adding a highlight to edges.
        # Often placed directly behind the subject, slightly above.
        rim_light_data = bpy.data.lights.new(name="Rim_Light", type='AREA')
        rim_light_data.energy = 600 # Brighter than fill, but less than key.
        rim_light_data.size = 0.7   # Smaller area for a more focused highlight.
        rim_light_data.color = (1.0, 1.0, 0.95) # Near white, or a complementary color.
        rim_light_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_light_data)
        scene.collection.objects.link(rim_light_obj)
        rim_light_obj.location = (0, 7, 6) # Behind and above.
        rim_light_obj.rotation_euler = (0.3, 0.0, 0.0)

        # Encapsulate all lights into a dedicated collection for organized scene management.
        lights_collection = bpy.data.collections.new("Tri_Lights")
        scene.collection.children.link(lights_collection)
        lights_collection.objects.link(key_light_obj)
        lights_collection.objects.link(fill_light_obj)
        lights_collection.objects.link(rim_light_obj)

        self.report({'INFO'}, "Balanced tri-lighting setup added, illuminating your scene with mastery.")
        return {'FINISHED'}

class STRATT_OT_AddCamera(bpy.types.Operator):
    """Add a new camera to the scene, precisely positioned either to your current viewport or the 3D cursor's active location."""
    bl_idname = "stratt.add_camera"
    bl_label = "Add Camera"
    bl_options = {'REGISTER', 'UNDO'}

    # This property will be dynamically set by the UI to determine the camera's placement logic.
    camera_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('VIEWPORT', "Viewport", "Add camera matching the current viewport's perspective and position"),
            ('CURSOR', "3D Cursor", "Add camera at the 3D cursor's exact active location and orientation"),
        ],
        default='VIEWPORT',
    )

    def execute(self, context):
        scene = context.scene
        cam_data = bpy.data.cameras.new("Camera")
        cam_obj = bpy.data.objects.new("Camera", cam_data)
        scene.collection.objects.link(cam_obj)

        if self.camera_mode == 'VIEWPORT':
            # This complex loop iterates through Blender's current screen layout to find the
            # active 3D viewport, then extracts its precise view location and rotation.
            # This ensures the new camera perfectly replicates the user's current perspective.
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            region = space.region_3d
                            cam_obj.location = region.view_location
                            cam_obj.rotation_euler = region.view_rotation.to_euler()
                            break
                    break
            self.report({'INFO'}, "Camera added, perfectly mirroring your current viewport perspective.")
        elif self.camera_mode == 'CURSOR':
            # Directly applies the 3D cursor's world position and rotation to the new camera.
            # This offers precise placement for specific scene composition.
            cam_obj.location = scene.cursor.location
            cam_obj.rotation_euler = scene.cursor.rotation_euler
            self.report({'INFO'}, "Camera added at the 3D cursor's exact location.")

        # Activate and select the newly created camera for immediate manipulation.
        context.view_layer.objects.active = cam_obj
        cam_obj.select_set(True)
        return {'FINISHED'}

class STRATT_OT_AddCollections(bpy.types.Operator):
    """Add three new, uniquely colored collections to categorize your scene elements with unprecedented organization."""
    bl_idname = "stratt.add_three_collections"
    bl_label = "Add 3 Colored Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        collection_names = ["Geometry_Assets", "Props_Detail", "Environment_Elements"]
        
        # Blender's collection coloring relies on predefined color tags, which are mapped
        # to specific colors in the user's theme settings. We assign distinct tags to
        # ensure visual separation in the Outliner.
        color_tags = ['COLOR_01', 'COLOR_02', 'COLOR_03']

        for i in range(3):
            col = bpy.data.collections.new(collection_names[i])
            scene.collection.children.link(col) # Link to the master scene collection.
            col.color_tag = color_tags[i] # Assign a unique color tag.
            self.report({'INFO'}, f"Collection '{collection_names[i]}' created with color tag '{color_tags[i]}'.")

        self.report({'INFO'}, "Three uniquely colored collections added, empowering your organizational hierarchy.")
        return {'FINISHED'}

class STRATT_OT_AddRigidBodiesCollection(bpy.types.Operator):
    """Add a new collection explicitly named 'Rigid Bodies', dedicated to physics simulations."""
    bl_idname = "stratt.add_rigid_bodies_collection"
    bl_label = "Add Rigid Bodies Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        col_name = "Rigid Bodies"
        # Check if the collection already exists to prevent duplication and maintain scene integrity.
        if col_name not in scene.collection.children:
            col = bpy.data.collections.new(col_name)
            scene.collection.children.link(col)
            self.report({'INFO'}, f"Collection '{col_name}' added for your physics simulations.")
        else:
            self.report({'WARNING'}, f"Collection '{col_name}' already exists. No action taken.")
        return {'FINISHED'}

# --- PROPERTY GROUP: Enabling Dynamic UI Interactions ---

# This PropertyGroup is essential for making the camera mode selection interactive
# within the UI panel, allowing the user to choose between "Viewport" and "3D Cursor"
# before executing the camera creation operator.
class StrattCameraSettings(bpy.types.PropertyGroup):
    camera_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('VIEWPORT', "Viewport", "Add camera matching the current viewport"),
            ('CURSOR', "3D Cursor", "Add camera at the 3D cursor's active location"),
        ],
        default='VIEWPORT',
    )

# --- PANEL: The Command Interface ---

class STRATT_PT_ToolsPanel(bpy.types.Panel):
    """A custom panel for Stratt's Tools, your centralized command center for Blender."""
    bl_label = "Stratt's Tools"
    bl_idname = "STRATT_PT_ToolsPanel"
    bl_space_type = 'VIEW_3D' # Appears in the 3D viewport.
    bl_region_type = 'UI'     # Specifically in the N-panel (sidebar).
    bl_category = "Stratt's Tools" # Creates a dedicated tab in the N-panel.

    def draw(self, context):
        layout = self.layout
        stratt_settings = context.window_manager.stratt_camera_settings # Access the property group.

        # Each row represents a distinct, powerful command at your fingertips.
        row = layout.row()
        row.label(text="Scene Management:")
        row = layout.row()
        row.operator(STRATT_OT_PurgeUnusedData.bl_idname, icon='REMOVE') # Purge button.

        row = layout.row()
        row.label(text="Lighting:")
        row = layout.row()
        row.operator(STRATT_OT_AddTriLighting.bl_idname, icon='LIGHT_AREA') # Tri-lighting button.

        # The camera section uses a box for better visual grouping and includes the
        # dynamic enum property for mode selection.
        box = layout.box()
        box.label(text="Camera Placement:")
        row = box.row()
        row.prop(stratt_settings, "camera_mode", expand=True) # Display the EnumProperty as radio buttons.
        row = box.row()
        # The operator is called, and its 'camera_mode' property is directly set by the
        # value from our persistent PropertyGroup.
        # CORRECTED: Changed 'CAMERA' to 'CAMERA_DATA'
        op = row.operator(STRATT_OT_AddCamera.bl_idname, icon='CAMERA_DATA') 
        op.camera_mode = stratt_settings.camera_mode

        row = layout.row()
        row.label(text="Collection Control:")
        row = layout.row()
        row.operator(STRATT_OT_AddCollections.bl_idname, icon='COLLECTION_NEW') # 3 Collections button.
        row = layout.row()
        row.operator(STRATT_OT_AddRigidBodiesCollection.bl_idname, icon='PHYSICS') # Rigid Bodies collection button.

# --- REGISTRATION: Activating Stratt's Tools in Blender ---

classes = (
    STRATT_OT_PurgeUnusedData,
    STRATT_OT_AddTriLighting,
    STRATT_OT_AddCamera,
    STRATT_OT_AddCollections,
    STRATT_OT_AddRigidBodiesCollection,
    StrattCameraSettings, # Crucial for the dynamic camera option.
    STRATT_PT_ToolsPanel,
)

def register():
    """Registers all classes and properties, making the add-on available in Blender."""
    for cls in classes:
        bpy.utils.register_class(cls)
    # Register the PropertyGroup with the WindowManager to make it globally accessible for UI.
    bpy.types.WindowManager.stratt_camera_settings = bpy.props.PointerProperty(type=StrattCameraSettings)

def unregister():
    """Unregisters all components, cleaning up the Blender environment."""
    for cls in reversed(classes): # Unregister in reverse order to avoid dependency issues.
        bpy.utils.unregister_class(cls)
    # Clean up the registered PropertyGroup.
    del bpy.types.WindowManager.stratt_camera_settings

if __name__ == "__main__":
    # This block ensures that the 'register()' function is called only when the script
    # is run directly (e.g., from Blender's text editor) and not when it's imported
    # as a module.
    register()
