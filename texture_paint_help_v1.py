import bpy

bl_info = {
    "name": "Texture Paint Helper",
    "author": "Stratton Phillips",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "Image Editor > N-panel > Texture Paint Helper Tab\n3D Viewport > N-panel > Texture Paint Helper Tab",
    "description": "Adds a custom UI panel with shortcuts for texture painting.",
    "warning": "",
    "doc_url": "",
    "category": "Paint",
}

# -------------------------------------------------------------------
#   Panel
# -------------------------------------------------------------------

class TEXTURE_PT_PaintHelper(bpy.types.Panel):
    """Creates a Texture Paint Helper Panel in the Image Editor and 3D Viewport"""
    bl_label = "Texture Paint Helper"
    bl_idname = "TEXTURE_PT_PaintHelper"
    bl_space_type = 'IMAGE_EDITOR' # Primary location
    bl_region_type = 'UI' # N-panel
    bl_category = "Paint Helper"

    # You can also make it appear in the 3D Viewport N-panel
    @classmethod
    def poll(cls, context):
        is_image_editor = context.area.type == 'IMAGE_EDITOR'
        is_3d_view = context.area.type == 'VIEW_3D'
        return is_image_editor or is_3d_view

    def draw(self, context):
        layout = self.layout
        tool_settings = context.tool_settings
        image_paint = tool_settings.image_paint
        brush = image_paint.brush if image_paint else None
        
        # Check if we are in texture paint mode in 3D View or Image Editor
        is_texture_paint_mode = context.mode == 'PAINT_TEXTURE'
        is_in_image_editor = context.area.type == 'IMAGE_EDITOR'
        
        # Only show most controls if in texture paint mode or image editor
        if not brush and not is_in_image_editor:
            layout.label(text="Switch to Texture Paint Mode or Image Editor!", icon='ERROR')
            return

        # --- Active Image (relevant in Image Editor) ---
        if is_in_image_editor and context.space_data.image:
            box = layout.box()
            box.label(text="Active Image", icon='IMAGE_DATA')
            box.prop(context.space_data.image, "name", text="Name")
            
            row = box.row(align=True)
            row.operator("image.new", text="New Image", icon='ADD')
            row.operator("image.save_as", text="Save Image", icon='SAVE_AS')
            
            # Show save button only if image is not saved
            if context.space_data.image.is_dirty:
                box.operator("image.save", text="Save Current", icon='SAVE')
            
            layout.separator()

        # --- Brush Settings (if brush is available) ---
        if brush:
            box = layout.box()
            box.label(text="Brush Settings", icon='BRUSH_DATA')
            
            # Brush Type (selection)
            row = box.row(align=True)
            row.operator("paint.brush_select", text="Draw", icon='BRUSH_DATA').name = 'Draw'
            row.operator("paint.brush_select", text="Soften", icon='BRUSH_SOFTEN').name = 'Soften'
            row.operator("paint.brush_select", text="Sharpen", icon='BRUSH_SHARPEN').name = 'Sharpen'
            row.operator("paint.brush_select", text="Smear", icon='BRUSH_SMEAR').name = 'Smear'
            
            row = box.row(align=True)
            row.operator("paint.brush_select", text="Fill", icon='BRUSH_FILL').name = 'Fill'
            row.operator("paint.brush_select", text="Sample", icon='BRUSH_GRAB').name = 'Sample'
            row.operator("paint.brush_select", text="Clone", icon='BRUSH_CLONE').name = 'Clone'
            
            box.separator()

            # Core Brush Properties
            box.prop(brush, "color", text="Color")
            box.prop(brush, "size", text="Size")
            box.prop(brush, "strength", text="Strength")
            box.prop(brush, "blend", text="Blend Mode")
            box.prop(brush, "hardness", text="Hardness")

            # Falloff Curve
            box.prop(brush, "use_custom_curve", text="Custom Falloff Curve")
            if brush.use_custom_curve:
                box.template_curve_mapping(brush, "falloff_curve")

            layout.separator()

            # --- Tools ---
            box = layout.box()
            box.label(text="Tools", icon='TOOLS')
            
            row = box.row(align=True)
            row.operator("paint.sample_color", text="Sample Color", icon='COLOR_AREA')
            row.operator("image.paint_fill", text="Fill Layer", icon='FULLSCREEN_ENTER')
            
            box.separator()
            
            # Symmetry
            box.label(text="Symmetry", icon='MOD_MIRROR')
            row = box.row(align=True)
            row.prop(brush, "use_symmetry_x", text="X", toggle=True)
            row.prop(brush, "use_symmetry_y", text="Y", toggle=True)
            row.prop(brush, "use_symmetry_z", text="Z", toggle=True)
            
            layout.separator()

        # --- Undo/Redo ---
        box = layout.box()
        box.label(text="History", icon='TIME')
        row = box.row(align=True)
        row.operator("ed.undo", text="Undo", icon='UNDO')
        row.operator("ed.redo", text="Redo", icon='REDO')

# -------------------------------------------------------------------
#   Keymap (Shortcuts)
# -------------------------------------------------------------------

addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    # Image Paint Keymap
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='IMAGE_EDITOR')
    addon_keymaps.append(km)

    # 3D View Keymap (useful for quick access while looking at model)
    km_3d = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    addon_keymaps.append(km_3d)

    # List of (operator_id, key_type, value, shift, ctrl, alt, keymap_target)
    # value can be 'PRESS', 'CLICK', 'DOUBLE_CLICK', etc.
    # Note: Many common operations (like brush size F, Shift+F) are built-in.
    # We'll add some custom ones.
    keymap_items_data = [
        # Image Editor Specific
        ("image.new", 'N', 'PRESS', True, False, False, km),          # Shift+N: New Image
        ("image.save_as", 'S', 'PRESS', True, False, False, km),      # Shift+S: Save Image As
        ("paint.sample_color", 'K', 'PRESS', False, False, False, km), # K: Sample Color
        ("image.paint_fill", 'G', 'PRESS', True, False, False, km),    # Shift+G: Fill Layer

        # Brush Selection (common across Image Paint & 3D View when relevant)
        ("paint.brush_select", 'Q', 'PRESS', False, False, False, km), # Q: Draw Brush (Name set below)
        ("paint.brush_select", 'Q', 'PRESS', False, False, False, km_3d), # Q: Draw Brush in 3D View
        
        ("paint.brush_select", 'W', 'PRESS', False, False, False, km), # W: Soften Brush
        ("paint.brush_select", 'W', 'PRESS', False, False, False, km_3d), # W: Soften Brush in 3D View

        ("paint.brush_select", 'E', 'PRESS', False, False, False, km), # E: Sharpen Brush
        ("paint.brush_select", 'E', 'PRESS', False, False, False, km_3d), # E: Sharpen Brush in 3D View

        ("paint.brush_select", 'R', 'PRESS', False, False, False, km), # R: Smear Brush
        ("paint.brush_select", 'R', 'PRESS', False, False, False, km_3d), # R: Smear Brush in 3D View

        ("paint.brush_select", 'T', 'PRESS', False, False, False, km), # T: Fill Brush
        ("paint.brush_select", 'T', 'PRESS', False, False, False, km_3d), # T: Fill Brush in 3D View
    ]

    for op_id, key_type, value, shift, ctrl, alt, target_km in keymap_items_data:
        kmi = target_km.keymap_items.new(op_id, key_type, value, shift=shift, ctrl=ctrl, alt=alt)
        
        # Set specific brush names for the brush_select operator
        if op_id == "paint.brush_select":
            if key_type == 'Q':
                kmi.properties.name = 'Draw'
            elif key_type == 'W':
                kmi.properties.name = 'Soften'
            elif key_type == 'E':
                kmi.properties.name = 'Sharpen'
            elif key_type == 'R':
                kmi.properties.name = 'Smear'
            elif key_type == 'T':
                kmi.properties.name = 'Fill'
        
        addon_keymaps.append((target_km, kmi)) # Store (keymap, keymap_item) tuple for unregister

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

# -------------------------------------------------------------------
#   Registration
# -------------------------------------------------------------------

classes = (
    TEXTURE_PT_PaintHelper,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()
    print("Texture Paint Helper UI Registered.")

def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Texture Paint Helper UI Unregistered.")

if __name__ == "__main__":
    register()
