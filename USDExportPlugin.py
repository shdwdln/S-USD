# USDExportPlugin
# Initial code generated by Softimage SDK Wizard
# Executed Mon May 4 17:54:03 UTC+0500 2020 by Shekn
#
# Tip: To add a command to this plug-in, right-click in the
# script editor and choose Tools > Add Command.
import win32com.client
from win32com.client import constants
import sys
import os
if __sipath__ not in sys.path:
    sys.path.append(__sipath__)
import export_processor
import utils
import imp

null = None
false = 0
true = 1
app = Application
DEBUG_MODE = True


def log(message):
    app.LogMessage(message)


def get_play_control_parameter(key):
    prop_list = app.ActiveProject.Properties
    play_ctrl = prop_list("Play Control")
    frame_param = play_ctrl.Parameters(key)
    return int(frame_param.Value)


def get_current_frame():
    return get_play_control_parameter("Current")


def get_start_timeline_frame():
    return get_play_control_parameter("In")


def get_end_timeline_frame():
    return get_play_control_parameter("Out")


def XSILoadPlugin(in_reg):
    in_reg.Author = "Shekn"
    in_reg.Name = "USDExportPlugin"
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterCommand("USDExportCommand", "USDExportCommand")
    in_reg.RegisterCommand("USDExportOpen", "USDExportOpen")
    in_reg.RegisterMenu(constants.siMenuMainFileExportID, "USD Export", False, False)
    # RegistrationInsertionPoint - do not remove this line

    return True


def USDExport_Init(ctxt):
    menu = ctxt.source
    menu.AddCommandItem("USD file...", "USDExportOpen")


def XSIUnloadPlugin(in_reg):
    strPluginName = in_reg.Name
    app.LogMessage(str(strPluginName) + str(" has been unloaded."), constants.siVerbose)
    return true


def USDExportCommand_Init(in_ctxt):
    command = in_ctxt.Source
    args = command.Arguments
    # init parameters of the command
    args.Add("file_path")  # string
    args.AddWithHandler("objects", "Collection")    # [obj1, obj2, ...] where obji - X3DObject
    args.Add("animation")  # None if no animation, (start, end) for export animation interval
    args.Add("types")  # [type1, type2, ...]
    args.Add("attributes")  # [attr1, attr2, ...] each attr is a string ("normal", "uv", ...)
    args.Add("is_materials")
    args.Add("use_subdiv")
    args.Add("ignore_unknown")
    args.Add("force_change_frame")

    return True


def USDExportCommand_Execute(*args):
    if DEBUG_MODE:
        imp.reload(utils)

    app.LogMessage("USDExportCommand_Execute called", constants.siVerbose)
    scene = app.ActiveProject2.ActiveScene
    # read arguments of the command
    file_path = utils.verify_extension(app, args[0] if args[0] is not None and len(args[0]) > 0 else utils.from_scene_path_to_models_path(scene.Parameters("Filename").Value))
    objects_list = [scene.Root] if args[1] is None or len(args[1]) == 0 or (str(args[1]) == "Plugin Manager") else args[1]
    animation = args[2]
    object_types = args[3] if args[3] is not None else ("strands", "hair", constants.siModelType, constants.siNullPrimType, constants.siPolyMeshType, constants.siLightPrimType, constants.siCameraPrimType, "pointcloud")  # for empty arg use full list of object types
    attr_list = args[4] if args[4] is not None else ('uvmap', 'normal', 'color', 'weightmap', 'cluster', 'vertex_creases', 'edge_creases')  # for empty arg use full list of attributes
    is_materials = args[5] if args[5] is not None else True
    use_subdiv = args[6] if args[6] is not None else False
    ignore_unknown = args[7] if args[7] is not None else True
    force_change_frame = args[8] if args[8] is not None else False

    params = {"animation": animation,
              "objects_list": objects_list,
              "object_types": object_types,
              "attr_list": attr_list,
              "options": {"use_subdiv": use_subdiv,
                          "ignore_unknown": ignore_unknown,
                          "force_change_frame": force_change_frame},
              "materials": {"is_materials": is_materials}}
    if DEBUG_MODE:
        imp.reload(export_processor)

    export_processor.export(app, file_path, params, XSIUIToolkit)

    return True


def USDExportOpen_Execute():
    if DEBUG_MODE:
        imp.reload(utils)

    scene_root = app.ActiveProject2.ActiveScene.Root

    # read settings from previous opened window
    plugin_path = utils.get_plugin_path(app, "USDExportPlugin")
    props_path = plugin_path + "export.props"
    if os.path.isfile(props_path):
        with open(props_path, "r") as file:
            export_props = eval(file.read())
    else:  # set default values
        export_props = {"is_selection": False,
                        "is_animation": False,
                        "is_polymesh": True,
                        "is_lights": True,
                        "is_cameras": True,
                        "is_strands": True,
                        "is_hairs": True,
                        "is_pointclouds": True,
                        "is_nulls": True,
                        "is_models": True,
                        "is_uv_maps": True,
                        "is_normals": True,
                        "is_weightmaps": True,
                        "is_clusters": True,
                        "is_vertex_creases": True,
                        "is_edge_creases": True,
                        "is_vertex_color": True,
                        "is_materials": True,
                        "start_frame": get_start_timeline_frame(),
                        "end_frame": get_end_timeline_frame(),
                        "opt_subdiv": False,
                        "opt_ignore_unknown": True,
                        "opt_force_key_change": False}

    # create property
    prop = scene_root.AddProperty("CustomProperty", False, "USD_Export")

    # add parameters
    prop.AddParameter3("file_path", constants.siString, "", "", "", False, False)
    param = prop.AddParameter3("is_selection", constants.siBool, export_props["is_selection"])
    param.Animatable = False
    param = prop.AddParameter3("is_animation", constants.siBool, export_props["is_animation"])
    param.Animatable = False
    # object types
    param = prop.AddParameter3("is_polymesh", constants.siBool, export_props["is_polymesh"])
    param.Animatable = False
    param = prop.AddParameter3("is_lights", constants.siBool, export_props["is_lights"])
    param.Animatable = False
    param = prop.AddParameter3("is_cameras", constants.siBool, export_props["is_cameras"])
    param.Animatable = False
    param = prop.AddParameter3("is_strands", constants.siBool, export_props["is_strands"])
    param.Animatable = False
    param = prop.AddParameter3("is_hairs", constants.siBool, export_props["is_hairs"])
    param.Animatable = False
    param = prop.AddParameter3("is_pointclouds", constants.siBool, export_props["is_pointclouds"])
    param.Animatable = False
    param = prop.AddParameter3("is_nulls", constants.siBool, export_props["is_nulls"])
    param.Animatable = False
    param = prop.AddParameter3("is_models", constants.siBool, export_props["is_models"])
    param.Animatable = False
    # attributes
    param = prop.AddParameter3("is_uv_maps", constants.siBool, export_props["is_uv_maps"])
    param.Animatable = False
    param = prop.AddParameter3("is_normals", constants.siBool, export_props["is_normals"])
    param.Animatable = False
    param = prop.AddParameter3("is_weightmaps", constants.siBool, export_props["is_weightmaps"])
    param.Animatable = False
    param = prop.AddParameter3("is_clusters", constants.siBool, export_props["is_clusters"])
    param.Animatable = False
    param = prop.AddParameter3("is_vertex_creases", constants.siBool, export_props["is_vertex_creases"])
    param.Animatable = False
    param = prop.AddParameter3("is_edge_creases", constants.siBool, export_props["is_edge_creases"])
    param.Animatable = False
    param = prop.AddParameter3("is_vertex_color", constants.siBool, export_props["is_vertex_color"])
    param.Animatable = False
    param = prop.AddParameter3("is_materials", constants.siBool, export_props["is_materials"])
    param.Animatable = False
    prop.AddParameter2("start_frame", constants.siInt4, export_props["start_frame"], -2147483648, 2147483647, export_props["start_frame"], export_props["end_frame"])
    prop.AddParameter2("end_frame", constants.siInt4, export_props["end_frame"], -2147483648, 2147483647, export_props["start_frame"], export_props["end_frame"])

    param = prop.AddParameter3("opt_subdiv", constants.siBool, export_props["opt_subdiv"])
    param.Animatable = False
    param = prop.AddParameter3("opt_ignore_unknown", constants.siBool, export_props["opt_ignore_unknown"])
    param.Animatable = False
    param = prop.AddParameter3("opt_force_key_change", constants.siBool, export_props["opt_force_key_change"])
    param.Animatable = False

    # define layout
    layout = prop.PPGLayout
    layout.Clear()
    layout.AddGroup("File Path")
    layout.AddItem("file_path", "File", constants.siControlFilePath)
    layout.EndGroup()

    layout.AddGroup("Objects to Export")
    layout.AddItem("is_selection", "Selection Only")
    layout.AddRow()
    layout.AddItem("is_nulls", "Null")
    layout.AddItem("is_polymesh", "Polygon Mesh")
    layout.AddItem("is_lights", "Lights")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_cameras", "Cameras")
    layout.AddItem("is_strands", "Strands")
    layout.AddItem("is_pointclouds", "Pointclouds")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_models", "Model")
    layout.AddItem("is_hairs", "Hairs")
    layout.AddSpacer()
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Animation")
    layout.AddItem("is_animation", "Export Animation")
    layout.AddItem("start_frame", "Start Frame")
    layout.AddItem("end_frame", "End Frame")
    layout.EndGroup()

    layout.AddGroup("Mesh Attributes")
    layout.AddRow()
    layout.AddItem("is_uv_maps", "UV Map")
    layout.AddItem("is_normals", "Normals")
    layout.AddItem("is_vertex_color", "Vertex Color")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_weightmaps", "Weightmaps")
    layout.AddItem("is_clusters", "Polygon Clusters")
    layout.AddItem("is_vertex_creases", "Vertex Creases")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_edge_creases", "Edge Creases")
    layout.AddSpacer()
    layout.AddSpacer()
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Material")
    layout.AddItem("is_materials", "Export Materials")
    layout.EndGroup()

    layout.AddGroup("Options")
    layout.AddItem("opt_subdiv", "Activate Subdivision")
    layout.AddItem("opt_ignore_unknown", "Ignore Unexported Objects")
    layout.AddItem("opt_force_key_change", "Change Frames in Animation Export")
    layout.EndGroup()

    rtn = app.InspectObj(prop, "", "Export *.usd file...", constants.siModal, False)
    if rtn is False:
        # click "ok", execute export command
        # save props file
        # set it
        export_props["is_selection"] = prop.Parameters("is_selection").Value
        export_props["is_animation"] = prop.Parameters("is_animation").Value
        export_props["is_polymesh"] = prop.Parameters("is_polymesh").Value
        export_props["is_lights"] = prop.Parameters("is_lights").Value
        export_props["is_cameras"] = prop.Parameters("is_cameras").Value
        export_props["is_strands"] = prop.Parameters("is_strands").Value
        export_props["is_hairs"] = prop.Parameters("is_hairs").Value
        export_props["is_pointclouds"] = prop.Parameters("is_pointclouds").Value
        export_props["is_nulls"] = prop.Parameters("is_nulls").Value
        export_props["is_models"] = prop.Parameters("is_models").Value
        export_props["is_uv_maps"] = prop.Parameters("is_uv_maps").Value
        export_props["is_normals"] = prop.Parameters("is_normals").Value
        export_props["is_weightmaps"] = prop.Parameters("is_weightmaps").Value
        export_props["is_clusters"] = prop.Parameters("is_clusters").Value
        export_props["is_vertex_creases"] = prop.Parameters("is_vertex_creases").Value
        export_props["is_edge_creases"] = prop.Parameters("is_edge_creases").Value
        export_props["is_vertex_color"] = prop.Parameters("is_vertex_color").Value
        export_props["is_materials"] = prop.Parameters("is_materials").Value
        export_props["start_frame"] = prop.Parameters("start_frame").Value
        export_props["end_frame"] = prop.Parameters("end_frame").Value
        export_props["opt_subdiv"] = prop.Parameters("opt_subdiv").Value
        export_props["opt_ignore_unknown"] = prop.Parameters("opt_ignore_unknown").Value
        export_props["opt_force_key_change"] = prop.Parameters("opt_force_key_change").Value
        # write it
        with open(props_path, "w") as file:
            file.write(str(export_props))

        objects_types = []
        if prop.Parameters("is_nulls").Value:
            objects_types.append(constants.siNullPrimType)
        if prop.Parameters("is_polymesh").Value:
            objects_types.append(constants.siPolyMeshType)
        if prop.Parameters("is_lights").Value:
            objects_types.append(constants.siLightPrimType)
        if prop.Parameters("is_cameras").Value:
            objects_types.append(constants.siCameraPrimType)
        if prop.Parameters("is_strands").Value:
            objects_types.append("strands")
        if prop.Parameters("is_hairs").Value:
            objects_types.append("hair")
        if prop.Parameters("is_pointclouds").Value:
            objects_types.append("pointcloud")
        if prop.Parameters("is_models").Value:
            objects_types.append(constants.siModelType)

        attributes = []
        if prop.Parameters("is_uv_maps").Value:
            attributes.append("uvmap")
        if prop.Parameters("is_normals").Value:
            attributes.append("normal")
        if prop.Parameters("is_vertex_color").Value:
            attributes.append("color")
        if prop.Parameters("is_weightmaps").Value:
            attributes.append("weightmap")
        if prop.Parameters("is_clusters").Value:
            attributes.append("cluster")
        if prop.Parameters("is_vertex_creases").Value:
            attributes.append("vertex_creases")
        if prop.Parameters("is_edge_creases").Value:
            attributes.append("edge_creases")

        objects = [o for o in app.Selection] if prop.Parameters("is_selection").Value else [app.ActiveProject2.ActiveScene.Root]
        app.USDExportCommand(prop.Parameters("file_path").Value,
                             objects,
                             (prop.Parameters("start_frame").Value, prop.Parameters("end_frame").Value) if prop.Parameters("is_animation").Value else None,
                             objects_types,
                             attributes,
                             prop.Parameters("is_materials").Value,
                             prop.Parameters("opt_subdiv").Value,
                             prop.Parameters("opt_ignore_unknown").Value,
                             prop.Parameters("opt_force_key_change").Value)

    # delete dialog
    app.DeleteObj(prop)

    return True
