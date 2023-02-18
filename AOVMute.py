import bpy
import json

# Main UI
# ===========================================================================================
# アドオンのリストを全部表示に
class AOV_MUTE_OT_show(bpy.types.Operator):
    bl_idname = "aov_mute.show"
    bl_label = "Show All"

    # execute
    def execute(self, context):
        for list in context.scene.aov_list:
            list.mute = False
        return{'FINISHED'}

# アドオンのリストを全部MUTEに
class AOV_MUTE_OT_mute(bpy.types.Operator):
    bl_idname = "aov_mute.mute"
    bl_label = "Mute All"

    # execute
    def execute(self, context):
        for list in context.scene.aov_list:
            list.mute = True
        return{'FINISHED'}


# 同期ボタン(これを押さないと反映されない)
# *************************************************************************************************
class AOV_MUTE_OT_sync(bpy.types.Operator):
    bl_idname = "aov_mute.sync"
    bl_label = "AOV Sync"

    # execute
    def execute(self, context):
        self.sync(context)
        return{'FINISHED'}

    # 同期
    def sync(self, context):
        # カスタムプロパティを取得しておく
        if context.view_layer.get("AOV_MUTE") == None:
            PROPERTY_LIST = {}
        else:
            PROPERTY_LIST = json.loads(context.view_layer.get("AOV_MUTE"))


        # 存在しないAOVをアドオンのリストから除去
        # ---------------------------------------------------------------------
        exists_aovs = {}
        for list in context.scene.aov_list:
            if list == None or list.name == None or list.name == "":  # アドオンのリストがおかしい
                continue  # 除外する
            if context.view_layer.aovs.find(list.name) == -1:  # AOVにない
                if list.name not in PROPERTY_LIST: # プロパティにもない
                    continue  # 除外する
            exists_aovs[list.name] = {"type": list.type, "mute": list.mute}

        # ソートもしておく
        exists_aovs = dict(sorted(exists_aovs.items()))

        # アドオンのリストを存在するAOVのリストに変更
        context.scene.aov_list.clear()
        for aov_name in exists_aovs:
            item = context.scene.aov_list.add()
            item.name = aov_name
            item.type = exists_aovs[aov_name]["type"]
            item.mute = exists_aovs[aov_name]["mute"]


        # マージ処理
        # ---------------------------------------------------------------------
        # 現在のAOVの状態をアドオンのリストに反映
        for aov in context.view_layer.aovs:
            # アドンのリストに無ければ追加
            if context.scene.aov_list.get(aov.name) == None:
                item = context.scene.aov_list.add()
                item.name = aov.name
                item.type = aov.type
                item.mute = False
            # あればtype合わせ
            else:
                context.scene.aov_list.get(aov.name).type = aov.type

        # カスタムプロパティの状態をアドオンのリストに反映
        for prop_name in PROPERTY_LIST:
            # アドンのリストに無ければ追加
            # あれば無視(アドオンのリストが優先)
            if context.scene.aov_list.get(prop_name) == None:
                item = context.scene.aov_list.add()
                item.name = prop_name
                item.type = PROPERTY_LIST[prop_name]["type"]
                item.mute = True


        # アドオンのリストで更新
        # ---------------------------------------------------------------------
        # カスタムプロパティを更新
        AOV_MUTE = {}
        for list in context.scene.aov_list:
            if list.mute:
                AOV_MUTE[list.name] = {"type": list.type}
        context.view_layer["AOV_MUTE"] = json.dumps(AOV_MUTE)

        # AOVを更新
        for list in context.scene.aov_list:
            aov_index = context.view_layer.aovs.find(list.name)
            if list.mute:
                # AOVにあれば削除
                if aov_index != -1:
                    bpy.context.scene.view_layers["ViewLayer"].active_aov_index = aov_index
                    bpy.ops.scene.view_layer_remove_aov()
            else:
                # AOVに無ければ追加
                if aov_index == -1:
                    aov = context.view_layer.aovs.add()
                    aov.name = list.name
                    aov.type = list.type


# AOVの状況UI
# ===========================================================================================
# 3DView Tools Panel
class AOV_MUTE_PT_ui(bpy.types.Panel):
    bl_idname = "AOV_MUTE_PT_UI"
    bl_label = "AOV Mute"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FreePencil"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        row = self.layout.row()
        row.operator("aov_mute.show")
        row.operator("aov_mute.mute")
        self.layout.template_list("AOV_MUTE_UL_aov_list", "", context.scene, "aov_list", context.scene, "aov_list_index")
        self.layout.operator("aov_mute.sync")


# AOVの状況プロパティ表示の仕方
class AOV_MUTE_UL_aov_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # print(data, item, active_data, active_propname)

        layout.prop(item, "name", text="", emboss=False)
        if item.mute == False:
            layout.prop(item, "mute", text="", emboss=False, icon="HIDE_OFF")
        else:
            layout.prop(item, "mute", text="", emboss=False, icon="HIDE_ON")

# AOVの状況プロパティ
class AOVItem(bpy.types.PropertyGroup):
    name:  bpy.props.StringProperty()
    mute:  bpy.props.BoolProperty()
    type:  bpy.props.StringProperty()


# 設定用データ
# =================================================================================================
def register():
    bpy.types.Scene.aov_list = bpy.props.CollectionProperty(type=AOVItem)
    bpy.types.Scene.aov_list_index = bpy.props.IntProperty()  # template_list使うときはこれも必要
