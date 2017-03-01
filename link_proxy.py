bl_info = {
    "name": "Link & Proxy",
    "author": "Pencillati",
    "version": (0, 1),
    "blender": (2, 7, 8),
    "category": "3D View"
}

import os
import bpy
from bpy_extras.io_utils import ExportHelper



class ArmatureData(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    group_name = bpy.props.StringProperty()


    
class LPAddonProperties(bpy.types.PropertyGroup):
    filepath = bpy.props.StringProperty()
    armatures = bpy.props.CollectionProperty(type=ArmatureData)


    
class WMFileSelector(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.file_selector"
    bl_label = "some folder"

    filename_ext = ".blend"

    def execute(self, context):
        
        fdir = self.properties.filepath
        scn = context.scene
        
        context.scene.lp_addon.filepath = fdir
        
        with bpy.data.libraries.load(fdir, link=True) as (data_src, data_dst):
            data_dst.groups = data_src.groups

        for group in data_dst.groups:
            group_new = bpy.data.objects.new(group.name, None)
            group_new.dupli_group = group
            group_new.dupli_type = 'GROUP'
            scn.objects.link(group_new)
            
            for o in group.objects:
                if o.type=='ARMATURE':
                    armt = context.scene.lp_addon.armatures.add()
                    armt.name = o.name
                    armt.group_name = group.name

        return{'FINISHED'}


class LinkProxyOperator(bpy.types.Operator):
    bl_idname = "ops.lp_operator"
    bl_label = "Link Proxy Op"
    
    armt_name = bpy.props.StringProperty()

    def execute(self, context):

        scn = context.scene
        
        a_name = self.armt_name
        g_name = scn.lp_addon.armatures.get(a_name).group_name
        group = bpy.data.objects[g_name]
        
        ####### make active ###########
        scn.objects.active = group
        ###############################
        
        ######### proxying ############
        bpy.ops.object.proxy_make(object=a_name)
        scn.objects.active.name = a_name+'_PROXY'
        ###############################
        
        return {'FINISHED'}
    

class WMFilePanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Link & Proxy"
    bl_idname = "TOOL_PT_Link_Proxy"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # ui
        col = layout.column()
        row = col.row(align=True)
        row.prop(scn.lp_addon, 'filepath', text='Lib:')
        row.operator("wm.file_selector", icon="FILE_FOLDER", text="")

        for a in scn.lp_addon.armatures:
            row=col.row(align=True)
            row.operator("ops.lp_operator",text=a.name).armt_name = a.name
        
        
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.lp_addon = bpy.props.PointerProperty(type=LPAddonProperties)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.lp_addon
