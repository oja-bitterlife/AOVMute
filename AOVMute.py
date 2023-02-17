import bpy

# Main UI
# ===========================================================================================
class AOV_MUTE_OT_setup(bpy.types.Operator):
    bl_idname = "aov_mute.setup"
    bl_label = "Update List"

    # execute
    def execute(self, context):
        context.scene.aov_list.clear()

        # AOVのリスト復活
        AOV_MUTE = context.view_layer.get("AOV_MUTE")
        if AOV_MUTE == None:
            AOV_MUTE = {}

        for aov in context.view_layer.aovs:
            if aov.name not in AOV_MUTE:
                AOV_MUTE[aov.name] = {"type": aov.type, "mute": False}

        print(AOV_MUTE)

        for aov_name in AOV_MUTE:
            item = context.scene.aov_list.add()
            item.name = aov_name
            item.mute = AOV_MUTE[aov_name]["mute"]
            item.type = AOV_MUTE[aov_name]["type"]

        return{'FINISHED'}


# 3DView Tools Panel
class AOV_MUTE_PT_ui(bpy.types.Panel):
    bl_idname = "AOV_MUTE_PT_UI"
    bl_label = "AOV Mute"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FreePencil"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        self.layout.label(text="AOV List:")
        self.layout.operator("aov_mute.setup")
        self.layout.template_list("AOV_MUTE_UL_aov_list", "", context.scene, "aov_list", context.scene, "aov_list_index")


class AOV_MUTE_UL_aov_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # print(data, item, active_data, active_propname)

        layout.prop(item, "name", text="", emboss=False)
        if item.mute == False:
            layout.prop(item, "mute", text="", emboss=False, icon="HIDE_OFF")
        else:
            layout.prop(item, "mute", text="", emboss=False, icon="HIDE_ON")

# AOVの状況更新
def update_prop(self, context):
    # 現在のリストの状態を取得
    AOV_MUTE = {}
    for item in context.scene.aov_list:
        AOV_MUTE[item.name] = {"type": item.type, "mute": item.mute}

    # 保存されている状態を取得
    OLD_AOV_MUTE = context.view_layer.get("AOV_MUTE")

    # 違えば更新
    if AOV_MUTE != OLD_AOV_MUTE:
        context.view_layer["AOV_MUTE"] = AOV_MUTE

    # AOVの状態更新
    for aov in context.view_layer.aovs:
        if aov.name in AOV_MUTE and AOV_MUTE[aov.name]["mute"]:
            context.view_layer.aovs.remove(aov)  # MUTEなら消す

    for aov_name in AOV_MUTE:
        if not AOV_MUTE[aov_name]["mute"] and context.view_layer.aovs.find(aov_name) == None:
            aov = context.view_layer.aovs.add()
            aov.name = AOV_MUTE[aov_name]["name"]
            aov.type = AOV_MUTE[aov_name]["type"]


class AOVItem(bpy.types.PropertyGroup):
    name:  bpy.props.StringProperty()
    mute:  bpy.props.BoolProperty(update=update_prop)
    type:  bpy.props.StringProperty()


# ペアレント設定用データ
# =================================================================================================
def register():
    bpy.types.Scene.aov_list = bpy.props.CollectionProperty(type=AOVItem)
    bpy.types.Scene.aov_list_index = bpy.props.IntProperty()
