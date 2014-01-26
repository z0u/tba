
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
    embody_descr = StringProperty()

    rel_scale = FloatProperty(
            name="Scale-Relative",
            default=0.0,
            )
    opacity = FloatProperty(
            name="Opacity",
            default=1.0,
            min=0.0, max=1.0,
            )

    use_alive = BoolProperty(
            name="Living",
            description="Is object living",
            default=True,
            )
    use_move = BoolProperty(
            name="Move",
            description="This object can be moved",
            default=True,
            )
    use_collect = BoolProperty(
            name="Collect",
            description="Can pickup this object",
            default=False,
            )
    solid_state = EnumProperty(
            items=(('SOLID', "Solid", ""),
                   ('LIQUID', "Liquid", ""),
                   ('GAS', "Gas", "")),
            )
    element = EnumProperty(
            name="Element",
            description="Element this this object feels an affinity for",
            items=(('spirit', "Spirit", ""),
                   ('stone', "Stone", ""),
                   ('wood', "Wood", ""),
                   ('water', "Water", ""),
                   ('metal', "Metal", "")),
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

        if obj is None:
            layout.label("No object")
            return

        if obj.type == 'CAMERA':
            adv = obj.adv
            layout.label("Camera object")
            col = layout.column(align=True)
            col.prop(adv, "description", text="")
            layout.operator("advgame.convert")
            return

        if obj.dupli_group:
            obs = obj.dupli_group.objects
            if len(obs) > 1:
                layout.label("Group object! (edit library)")
                return
            layout.label("Group: '%s'" % obj.dupli_group.name)
            obj = obs[0]
            del obs

        adv = obj.adv

        layout.label("Name, Descr:")
        col = layout.column(align=True)
        col.prop(obj, "name", text="")
        col.prop(adv, "description", text="")

        layout.label("Embody Text:")
        layout.prop(adv, "embody_descr", text="")

        layout.label("Physical:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(adv, "solid_state", expand=True)
        row = col.row(align=True)
        row.prop(adv, "element", expand=True)
        col.prop(adv, "rel_scale")
        col.prop(adv, "opacity")

        layout.label("Interact:")
        col = layout.column(align=True)
        col.prop(adv, "use_collect")
        col.prop(adv, "use_alive")
        col.prop(adv, "use_move")

        layout.operator("advgame.convert")


class AdvGameConvert(bpy.types.Operator):
    bl_label = "Setup"
    bl_idname = "advgame.convert"

    @staticmethod
    def obj_to_game_props(obj):
        game_props = obj.game.properties

        # CLEAR?
        while game_props:
            bpy.ops.object.game_property_remove({"active_object": obj}, index=0)

        for prop_identifier, prop in bpy.types.AdvGameObject.bl_rna.properties.items():
            print("PROP:", prop_identifier)
            if prop_identifier in {"rna_type", "name"}:
                continue

            gprop = game_props.get(prop_identifier)
            if gprop:
                bpy.ops.object.game_property_remove({"active_object": obj}, index=game_props.find(gprop.name))
                gprop = None

            if gprop is None:
                bpy.ops.object.game_property_new({"active_object": obj}, name=prop_identifier)
                gprop = game_props[-1]

            prop_type = prop.type
            # print(prop.type)
            value = getattr(obj.adv, prop_identifier)
            if prop_type == 'STRING':
                gprop.type = 'STRING'
                gprop = gprop.type_recast()

                if len(value) < 127:
                    gprop.value = value
                else:
                    value_rem = value
                    n = -1
                    while value_rem:
                        value = value_rem[0:127]
                        value_rem = value_rem[127:]
                        if n != -1:
                            bpy.ops.object.game_property_new({"active_object": obj}, name=prop_identifier + "." + str(n))
                            gprop = game_props[-1]
                            gprop.type = 'STRING'
                            gprop = gprop.type_recast()

                        gprop.value = value
                        n += 1

            elif prop_type == 'ENUM':
                gprop.type = 'STRING'
                gprop = gprop.type_recast()
                gprop.value = value
            elif prop_type == 'FLOAT':
                gprop.type = 'FLOAT'
                gprop = gprop.type_recast()
                gprop.value = value
            elif prop_type == 'INT':
                gprop.type = 'INT'
                gprop = gprop.type_recast()
                gprop.value = value
            elif prop_type == 'BOOLEAN':
                gprop.type = 'BOOL'
                gprop = gprop.type_recast()
                gprop.value = value


    def execute(self, context):
        scene = context.scene
        for obj in scene.objects:
            if obj.dupli_group is None:
                self.obj_to_game_props(obj)
        return {'FINISHED'}


classes = (
    AdvGameObject,
    AdvGamePanel,
    AdvGameConvert,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.adv = bpy.props.PointerProperty(type=AdvGameObject)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.adv

