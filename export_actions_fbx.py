bl_info = {
    "name": "Vizor NPC FBX Exporter",
    "author": "AI Assistant with Mikhail Lebedev",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Batch Export",
    "description": "Exports Model and NLA with Vizor script settings",
    "category": "Import-Export",
}

import bpy
import os

GLOBAL_SCALE=0.74 #scale of the model exported

class EXPORT_OT_vizor_model_precise(bpy.types.Operator):
    """Export Model using (mob_clon2) settings"""
    bl_idname = "export.vizor_model_precise"
    bl_label = "Export Model (mob_clon2)"

    @classmethod
    def poll(cls, context):
        # Check if selection contains both an Armature and a Mesh
        selected = context.selected_objects
        has_armature = any(obj.type == 'ARMATURE' for obj in selected)
        has_mesh = any(obj.type == 'MESH' for obj in selected)
        return has_armature and has_mesh

    def execute(self, context):
        obj = context.active_object

        # Use the name of the first armature found in selection for the filename
        naming_obj = next((o for o in context.selected_objects if o.type == 'ARMATURE'), None)
        if not naming_obj:
            self.report({'ERROR'}, "No Armature found")
            return {'CANCELLED'}

        
        if not context.scene.export_path:
            self.report({'ERROR'}, "Set export path first")
            return {'CANCELLED'}

        export_path = bpy.path.abspath(context.scene.export_path)
        file_path = os.path.join(export_path, naming_obj.name + "_Model.fbx")

        # Settings from mob_clon2.py
        bpy.ops.export_scene.vizor_fbx(
            filepath=file_path,
            use_selection=True,
            use_visible=False,
            use_active_collection=False,
            global_scale=GLOBAL_SCALE, #scale of the model exported
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_UNITS',
            use_space_transform=True,
            bake_space_transform=True,
            object_types={'ARMATURE', 'MESH'},
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            mesh_smooth_type='OFF',
            colors_type='SRGB',
            prioritize_active_color=False,
            use_subsurf=False,
            use_mesh_edges=False,
            use_tspace=False,
            use_triangles=False,
            use_custom_props=False,
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=True,
            armature_nodetype='NULL',
            bake_anim=False,
            bake_anim_use_all_bones=False,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=False,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=0.0,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            axis_forward='-Z',
            axis_up='Y'
        )

        self.report({'INFO'}, f"Model Exported: {obj.name}_Model.fbx")
        return {'FINISHED'}

class EXPORT_OT_vizor_nla_precise(bpy.types.Operator):
    """Export NLA Tracks using (my_HH_export_animation) settings"""
    bl_idname = "export.vizor_nla_precise"
    bl_label = "Export NLA Tracks (my_HH)"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE' or not obj.animation_data:
            self.report({'ERROR'}, "Select Armature with NLA tracks")
            return {'CANCELLED'}

        if not context.scene.export_path:
            self.report({'ERROR'}, "Set export path first")
            return {'CANCELLED'}

        export_path = bpy.path.abspath(context.scene.export_path)
        if not os.path.exists(export_path): os.makedirs(export_path)

        # Cache state
        original_mute_states = [t.mute for t in obj.animation_data.nla_tracks]
        original_frame_start = context.scene.frame_start
        original_frame_end = context.scene.frame_end

        # Only select the Armature (as per settings: object_types={'ARMATURE'})
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)

        tracks = obj.animation_data.nla_tracks
        for track in tracks:
            if not track.strips: continue
            
            # Solo the track
            for t in tracks: t.mute = True
            track.mute = False
            
            # Set frames
            start_f = min(s.frame_start for s in track.strips)
            end_f = max(s.frame_end for s in track.strips)
            context.scene.frame_start, context.scene.frame_end = int(start_f), int(end_f)
            
            file_name = "".join([c for c in track.name if c.isalnum() or c in (' ', '.', '_')]).rstrip()
            file_path = os.path.join(export_path, file_name + ".fbx")

            # Settings from my_HH_export_animation.py
            bpy.ops.export_scene.vizor_fbx(
                filepath=file_path,
                use_selection=True,
                use_visible=False,
                use_active_collection=False,
                global_scale=GLOBAL_SCALE,
                apply_unit_scale=False,
                apply_scale_options='FBX_SCALE_UNITS',
                use_space_transform=False,
                bake_space_transform=False,
                object_types={'ARMATURE'},
                use_mesh_modifiers=True,
                use_mesh_modifiers_render=True,
                mesh_smooth_type='OFF',
                colors_type='SRGB',
                prioritize_active_color=False,
                use_subsurf=False,
                use_mesh_edges=False,
                use_tspace=False,
                use_triangles=False,
                use_custom_props=False,
                add_leaf_bones=False,
                primary_bone_axis='Y',
                secondary_bone_axis='X',
                use_armature_deform_only=True,
                armature_nodetype='REMOVE_GHOST',
                bake_anim=True,
                bake_anim_use_all_bones=True,
                bake_anim_use_nla_strips=True,
                bake_anim_use_all_actions=False,
                bake_anim_force_startend_keying=True,
                bake_anim_step=1.0,
                bake_anim_simplify_factor=0.0,
                path_mode='AUTO',
                embed_textures=False,
                batch_mode='OFF',
                use_batch_own_dir=True,
                axis_forward='Y',
                axis_up='Z'
            )

        # Restore
        for i, track in enumerate(obj.animation_data.nla_tracks):
            track.mute = original_mute_states[i]
        context.scene.frame_start, context.scene.frame_end = original_frame_start, original_frame_end

        self.report({'INFO'}, f"Exported {len(tracks)} Animations")
        return {'FINISHED'}

class VIEW3D_PT_vizor_exporter_precise(bpy.types.Panel):
    bl_label = "Vizor Batch Exporter"
    bl_idname = "VIEW3D_PT_vizor_exporter_precise"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Batch Export'


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "export_path", text="Folder")

        layout.label(text=f"Global Scale={GLOBAL_SCALE}")
        
        layout.label(text=f"Export Model:")
        layout.operator("export.vizor_model_precise", icon='MESH_DATA')
        
        layout.separator()
        
        layout.label(text="Export Animations:")
        layout.operator("export.vizor_nla_precise", icon='ANIM_DATA')

def register():
    bpy.utils.register_class(EXPORT_OT_vizor_model_precise)
    bpy.utils.register_class(EXPORT_OT_vizor_nla_precise)
    bpy.utils.register_class(VIEW3D_PT_vizor_exporter_precise)
    bpy.types.Scene.export_path = bpy.props.StringProperty(name="Export Path", subtype='DIR_PATH')

def unregister():
    bpy.utils.unregister_class(EXPORT_OT_vizor_model_precise)
    bpy.utils.unregister_class(EXPORT_OT_vizor_nla_precise)
    bpy.utils.unregister_class(VIEW3D_PT_vizor_exporter_precise)
    del bpy.types.Scene.export_path

if __name__ == "__main__":
    register()