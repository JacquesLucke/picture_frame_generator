bl_info = {
    "name":        "Picture Frame Generator",
    "description": "Generate picture frames for images.",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 1),
    "blender":     (2, 79, 0),
    "location":    "3D View",
    "category":    "3D View",
    "warning":     "This version is still in development."
}

import os
import bpy
import bmesh
from . generator import createFrameBM, bmeshFromObject

class GeneratePictureFrameOperator(bpy.types.Operator):
    bl_idname = "object.generate_picture_frame"
    bl_label = "Generate Picture Frame"
    bl_description = "Create a frame for each selected object except for the active object which is used as corner piece."

    def execute(self, context):
        selectedObjects = set(context.selected_objects)
        corner = context.active_object
        selectedObjects.discard(corner)

        if corner is None:
            raise Exception("no corner selected")
        if len(selectedObjects) == 0:
            raise Exception("no object selected")

        for object in selectedObjects:
            self.createFrame(object, corner)

        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}

    def createFrame(self, object, corner):
        frameBM = createFrameBMForObject(object, corner)

        newMesh = bpy.data.meshes.new("Picture Frame")
        newObject = bpy.data.objects.new("Picture Frame", newMesh)
        frameBM.to_mesh(newMesh)

        newObject.location = object.location
        newObject.rotation_euler = object.rotation_euler
        bpy.context.scene.objects.link(newObject)

class LoadCornerExamplesOperator(bpy.types.Operator):
    bl_idname = "object.load_picture_frame_corner_examples"
    bl_label = "Load Picture Frame Corner Examples"

    def execute(self, context):
        filepath = os.path.join(os.path.dirname(__file__), "corner_examples.blend")
        with bpy.data.libraries.load(filepath) as (dataFrom, dataTo):
            dataTo.groups = ["Picture Frame Corners"]
        for object in dataTo.groups[0].objects:
            bpy.context.scene.objects.link(object)
        return {"FINISHED"}

class PictureFrameGeneratorPanel(bpy.types.Panel):
    bl_idname = "PictureFrameGeneratorPanel"
    bl_label = "Picture Frames"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"

    def draw(self, contex):
        layout = self.layout
        layout.operator("object.load_picture_frame_corner_examples", text = "Load Corners", icon = "MOD_BOOLEAN")
        layout.operator("object.generate_picture_frame", text = "Generate", icon = "RENDER_RESULT")

def createFrameBMForObject(object, corner):
    width, height = object.dimensions[:2]
    return createFrameBM(bmeshFromObject(corner), width, height)


def register():
    bpy.utils.register_class(GeneratePictureFrameOperator)
    bpy.utils.register_class(LoadCornerExamplesOperator)
    bpy.utils.register_class(PictureFrameGeneratorPanel)

def unregister():
    bpy.utils.unregister_class(GeneratePictureFrameOperator)
    bpy.utils.unregister_class(LoadCornerExamplesOperator)
    bpy.utils.unregister_class(PictureFrameGeneratorPanel)