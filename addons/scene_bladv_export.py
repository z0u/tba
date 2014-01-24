
bl_info = {
    "name": "AdventureGame Props",
    "description": "Single line explaining what this script exactly does.",
    "author": "Campbell Barton",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "View3D > Add > Mesh",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/My_Script",
    "category": "Add Mesh",
    }

import bpy
from bpy.props import (
        FloatProperty,
        BoolProperty,
        StringProperty,
        EnumProperty,
        )


class AdvGameObject(bpy.types.PropertyGroup):

    description = StringProperty()

    scale_relative = FloatProperty(
            name="Scale-Relative",
            default=0.0,
            )
    opacity = FloatProperty(
            name="Opacity",
            default=1.0,
            min=0.0, max=1.0,
            )

    use_collect = BoolProperty(
            name="Collect",
            description="Can pickup this object",
            default=False,
            )
    state = EnumProperty(
            items=(('SOLID', "Solid", ""),
                   ('LIQUID', "Liquid", ""),
                   ('GAS', "Gas", "")),
            )


class AdvGamePanel(bpy.types.Panel):
    bl_category = "AdvGame"
    bl_context = "objectmode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "AdvGame"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        adv = obj.adv

        layout.label("Name, Descr:")
        col = layout.column(align=True)
        col.prop(obj, "name", text="")
        col.prop(adv, "description", text="")

        layout.label("Physical:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(adv, "state", expand=True)
        col.prop(adv, "scale_relative")
        col.prop(adv, "opacity")

        layout.label("Interact:")
        col = layout.column(align=True)
        col.prop(adv, "use_collect")

classes = (
    AdvGameObject,
    AdvGamePanel,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.adv = bpy.props.PointerProperty(type=AdvGameObject)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.adv

