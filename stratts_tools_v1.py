bl_info = {
    "name": "Stratts Tools",
    "author": "Stratton Phillips",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "3D View > Sidebar > Stratts Tools",
    "description": "Custom tools for streamlining processes.",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from mathutils import Vector
import math

# --- Operators ---

class STRATTS_OT_PurgeUnused(bpy.types.Operator):
    """Purge all unused data blocks"""
    bl_idname = "stratts_tools.purge_unused"
    bl_label = "Purge Unused Assets"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for i in range(5): # Run multiple times for thorough cleanup
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, "Unused assets purged successfully.")
        return {'FINISHED'}

class STRATTS_OT_AddTriLighting(bpy.types.Operator):
    """Adds a balanced 3-point lighting setup (Key, Fill, Back) around selected objects or 3D cursor."""
    bl_idname = "stratts_tools.add_tri_lighting"
    bl_label = "Add Tri-Lighting Setup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target_location = Vector((0.0, 0.0, 0.0))
        radius = 3.0 # Default radius

        if context.selected_objects:
            # Calculate bounding box center of selected mesh objects
            min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
            max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
            found_mesh = False

            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    found_mesh = True
                    world_matrix = obj.matrix_world
                    for corner in obj.bound_box:
                        world_corner = world_matrix @ Vector(corner)
                        min_x = min(min_x, world_corner.x)
                        min_y = min(min_y, world_corner.y)
                        min_z = min(min_z, world_corner.z)
                        max_x = max(max_x, world_corner.x)
                        max_y = max(max_y, world_corner.y)
                        max_z = max(max_z, world_corner.z)
            
            if found_mesh:
                target_location = Vector([
                    (min_x + max_x) / 2,
                    (min_y + max_y) / 2,
                    (min_z + max_z) / 2
                ])
                # Estimate radius based on selection extent, with a minimum
                diagonal = Vector((max_x - min_x, max_y - min_y, max_z - min_z)).length
                radius = max(diagonal * 1.5, 3.0) 
            else: # No mesh objects selected, fallback to cursor
                target_location = context.scene.cursor.location
                self.report({'INFO'}, "No mesh objects selected. Using 3D Cursor location as lighting target.")
        else:
            target_location = context.scene.cursor.location
            self.report({'INFO'}, "No objects selected. Using 3D Cursor location as lighting target.")


        light_settings = {
            "Key Light": {
                "location": target_location + Vector((radius, -radius, radius * 0.75)),
                "energy": 100, "color": (1.0, 0.98, 0.95), "type": 'AREA', "size": radius * 1
            },
            "Fill Light": {
                "location": target_location + Vector((-radius, -radius * 0.75, radius * 0.5)),
                "energy": 50, "color": (0.95, 0.98, 1.0), "type": 'AREA', "size": radius * 0.8
            },
            "Back Light": {
                "location": target_location + Vector((0, radius * 1.5, radius * 0.75)),
                "energy": 70, "color": (1.0, 1.0, 1.0), "type": 'AREA', "size": radius * 0.50
            },
        }

        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
             bpy.ops.object.mode_set(mode='OBJECT')

        for name, settings in light_settings.items():
            light_data = bpy.data.lights.new(name=name, type=settings["type"])
            light_data.energy = settings["energy"]
            light_data.color = settings["color"]
            if settings["type"] == 'AREA':
                light_data.size = settings["size"] # For area lights

            light_object = bpy.data.objects.new(name=name, object_data=light_data)
            context.collection.objects.link(light_object)
            light_object.location = settings["location"]

            # Orient the light to look at the target location
            direction = target_location - light_object.location
            light_object.rotation_mode = 'XYZ'
            # Blender lights point along their local -Z axis.
            light_object.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

        self.report({'INFO'}, f"Tri-lighting setup added around {target_location}.")
        return {'FINISHED'}

class STRATTS_OT_AddSpecificMaterial(bpy.types.Operator):
    """Add a specific base material to the active object"""
    bl_idname = "stratts_tools.add_specific_material"
    bl_label = "Add Specific Material"
    bl_options = {'REGISTER', 'UNDO'}

    material_type: bpy.props.EnumProperty(
        items=[
            ('CAR_PAINT', "Smooth Red Car Paint", "Create a smooth red car paint material"),
            ('CLEAR_GLASS', "Clear Glass", "Create a clear glass material"),
            ('TRANSLUCENT_PLASTIC', "Translucent White Plastic", "Create a translucent white plastic material"),
        ],
        name="Material Type",
        description="Type of material to create and apply"
    )

    def execute(self, context):
        mat_name_map = {
            'CAR_PAINT': "Smooth Red Car Paint",
            'CLEAR_GLASS': "Clear Glass",
            'TRANSLUCENT_PLASTIC': "Translucent White Plastic",
        }
        material_name = mat_name_map[self.material_type]

        mat = bpy.data.materials.get(material_name)
        if not mat:
            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            principled_bsdf = mat.node_tree.nodes.get("Principled BSDF")

            if principled_bsdf: # Ensure Principled BSDF node exists
                if self.material_type == 'CAR_PAINT':
                    principled_bsdf.inputs["Base Color"].default_value = (0.8, 0.05, 0.05, 1.0)
                    principled_bsdf.inputs["Metallic"].default_value = 1.0
                    principled_bsdf.inputs["Roughness"].default_value = 0.1
                    principled_bsdf.inputs["Clearcoat"].default_value = 1.0
                    principled_bsdf.inputs["Clearcoat Roughness"].default_value = 0.03
                elif self.material_type == 'CLEAR_GLASS':
                    principled_bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
                    principled_bsdf.inputs["Metallic"].default_value = 0.0
                    principled_bsdf.inputs["Roughness"].default_value = 0.0
                    principled_bsdf.inputs["IOR"].default_value = 1.45
                    principled_bsdf.inputs["Transmission"].default_value = 0.1
                elif self.material_type == 'TRANSLUCENT_PLASTIC':
                    principled_bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
                    principled_bsdf.inputs["Metallic"].default_value = 0.0
                    principled_bsdf.inputs["Roughness"].default_value = 0.5
                    principled_bsdf.inputs["Subsurface"].default_value = 1
                    principled_bsdf.inputs["Subsurface Radius"].default_value = (0.1, 0.05, 0.03)
                    principled_bsdf.inputs["Subsurface Color"].default_value = (0.9, 0.9, 0.9, 1.0)
            else:
                self.report({'ERROR'}, f"Principled BSDF node not found in new material '{material_name}'.")
                return {'CANCELLED'}

        obj = context.active_object
        if obj and obj.type == 'MESH':
            # Assign to the first slot, or add a new slot if none exist or first is taken
            if not obj.data.materials:
                obj.data.materials.append(mat)
            elif obj.data.materials[0] is None:
                obj.data.materials[0] = mat
            else: # First slot is taken, or valid material there, so add a new slot
                obj.data.materials.append(mat)
            
            self.report({'INFO'}, f"Assigned '{material_name}' to active object '{obj.name}'.")
        else:
            self.report({'INFO'}, f"Created '{material_name}'. No active mesh object to assign to.")

        return {'FINISHED'}

class STRATTS_OT_AddBaseMaterial(bpy.types.Operator):
    """Add a default Principled BSDF material to selected objects that are missing one"""
    bl_idname = "stratts_tools.add_base_material"
    bl_label = "Add Default Base Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        default_mat_name = "DefaultBaseMaterial"
        base_mat = bpy.data.materials.get(default_mat_name)
        
        if not base_mat:
            base_mat = bpy.data.materials.new(name=default_mat_name)
            base_mat.use_nodes = True
            principled_bsdf = base_mat.node_tree.nodes.get("Principled BSDF")
            if principled_bsdf:
                principled_bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.7, 1) # Light gray
                principled_bsdf.inputs["Roughness"].default_value = 0.5
                principled_bsdf.inputs["Metallic"].default_value = 0.0

        affected_count = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                has_material = False
                for slot in obj.material_slots:
                    if slot.material:
                        has_material = True
                        break
                
                if not has_material:
                    if not obj.data.materials:
                        obj.data.materials.append(base_mat)
                    else:
                        found_empty_slot = False
                        for i, slot in enumerate(obj.material_slots):
                            if slot.material is None:
                                obj.material_slots[i].material = base_mat
                                found_empty_slot = True
                                break
                        if not found_empty_slot:
                            obj.data.materials.append(base_mat)

                    affected_count += 1
                    self.report({'INFO'}, f"Added material to '{obj.name}'")

        if affected_count > 0:
            self.report({'INFO'}, f"Added '{default_mat_name}' to {affected_count} mesh objects missing materials.")
        else:
            self.report({'INFO'}, "No selected mesh objects were missing materials, or no mesh objects selected.")

        return {'FINISHED'}


class STRATTS_OT_MakeRigidBodyActive(bpy.types.Operator):
    """Make selected objects active rigid bodies"""
    bl_idname = "stratts_tools.make_rigid_body_active"
    bl_label = "Make Active Rigid Body"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.selected_objects:
            self.report({'WARNING'}, "No objects selected to make rigid bodies.")
            return {'CANCELLED'}

        affected_count = 0
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
             bpy.ops.object.mode_set(mode='OBJECT')

        for obj in context.selected_objects:
            if not obj.rigid_body:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_add()
            
            obj.rigid_body.type = 'ACTIVE'
            obj.rigid_body.collision_shape = 'CONVEX_HULL'
            obj.rigid_body.use_margin = True
            
            affected_count += 1
        
        self.report({'INFO'}, f"Made {affected_count} selected objects active rigid bodies.")
        return {'FINISHED'}

class STRATTS_OT_ToggleQuadView(bpy.types.Operator):
    """Toggle Quad View (Ctrl+Alt+Q)"""
    bl_idname = "stratts_tools.toggle_quad_view"
    bl_label = "Toggle Quad View"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.screen.screen_full_area(state='TOGGLE')
        self.report({'INFO'}, "Toggled Quad View.")
        return {'FINISHED'}

# --- Panel ---

class STRATTS_PT_CustomTools(bpy.types.Panel):
    """Creates a Custom Tools Panel in the 3D Viewport Sidebar"""
    bl_label = "Stratts Tools" # Panel Header
    bl_idname = "STRATTS_PT_CustomTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stratts Tools' # Tab name in the N-panel

    def draw(self, context):
        layout = self.layout

        # Scene Cleanup Section
        box = layout.box()
        box.label(text="Scene Cleanup", icon='BRUSH_DATA')
        box.operator(STRATTS_OT_PurgeUnused.bl_idname)

        # Lighting Section
        box = layout.box()
        box.label(text="Lighting Setup", icon='LIGHT')
        box.operator(STRATTS_OT_AddTriLighting.bl_idname)

        # Material Management Section
        box = layout.box()
        box.label(text="Material Management", icon='MATERIAL')
        box.operator(STRATTS_OT_AddBaseMaterial.bl_idname)
        
        row = box.row(align=True)
        row.operator(STRATTS_OT_AddSpecificMaterial.bl_idname, text="Red Car Paint").material_type = 'CAR_PAINT'
        row.operator(STRATTS_OT_AddSpecificMaterial.bl_idname, text="Clear Glass").material_type = 'CLEAR_GLASS'
        row.operator(STRATTS_OT_AddSpecificMaterial.bl_idname, text="Translucent Plastic").material_type = 'TRANSLUCENT_PLASTIC'

        # Rigid Body Tools Section
        box = layout.box()
        box.label(text="Rigid Body Tools", icon='PHYSICS')
        box.operator(STRATTS_OT_MakeRigidBodyActive.bl_idname)
        
        # Viewport Tools Section
        box = layout.box()
        box.label(text="Viewport Tools", icon='SPLITSCREEN')
        box.operator(STRATTS_OT_ToggleQuadView.bl_idname)


# --- Registration ---

classes = (
    STRATTS_OT_PurgeUnused,
    STRATTS_OT_AddTriLighting,
    STRATTS_OT_AddBaseMaterial,
    STRATTS_OT_AddSpecificMaterial,
    STRATTS_OT_MakeRigidBodyActive,
    STRATTS_OT_ToggleQuadView,
    STRATTS_PT_CustomTools,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("Stratts Tools Registered!")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Stratts Tools Unregistered!")

if __name__ == "__main__":
    try:
        unregister()
    except Exception:
        pass
    register()
