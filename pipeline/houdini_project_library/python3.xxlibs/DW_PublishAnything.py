#
#
# Publish Anything is for publishing any Houdini node.
# It also requires OPmenu.xml for right click publishing functionality, and /scripts/externaldragdrop.py for drag and drop node importing.
#
#

import os
import re
import hou

def publishNode(primary_node):

    DW_TYPE = hou.getenv("DW_TYPE")
    DW_SERVER = hou.getenv("DW_SERVER")
    DW_JOB = hou.getenv("DW_JOB")
    DW_FILM = hou.getenv("DW_FILM")
    DW_SHOT = hou.getenv("DW_SHOT")
    DW_ASSET = hou.getenv("DW_ASSET")
    DW_DEPT = hou.getenv("DW_DEPT")
    DW_ELEMENT = hou.getenv("DW_ELEMENT")
    DW_VERSION = hou.getenv("DW_VERSION")

    if DW_VERSION is None:
        hou.ui.displayMessage("This .hip scene has not been properly saved.")
        return None

    if DW_TYPE == "SHOT":
        output_dir = DW_SERVER + DW_JOB + "/films/" + DW_FILM + "/shots/" + DW_SHOT + "/publish/" + DW_DEPT + "/" + DW_ELEMENT
    else:
        output_dir = DW_SERVER + DW_JOB + "/build/" + DW_ASSET + "/publish/" + DW_DEPT + "/" + DW_ELEMENT
    
    os.makedirs(output_dir, exist_ok=True)


    node_list = []
    selected_nodes = hou.selectedNodes()

    # If the primary node is not one of the selected nodes, then assume that those nodes were not selected for any reason and just export the primary.
    # This also works if no nodes were selected.
    if primary_node not in selected_nodes:
        node_list.append(primary_node)

    # If the primary node is one of the selected nodes then we populate our node list with all of the selected and will export each to its own file.
    # This also works if only the primary node was selected.
    else:
        node_list = [each for each in selected_nodes]


    save_message = ""

    for node in node_list:
        category = node.type().category().name()
        publish_name = category + "_" + node.path()[1:].replace("/", "~") + "_" + DW_VERSION

        output_path = output_dir + "/" + publish_name + ".node"



        if node.type().name() == "cam":

            # Check if the camera is linked to another and if so bake it.
            if node.parm("source_cam") is not None:
                if node.parm("source_cam").eval() != "":
                    node.parm("bake").pressButton()

                for each in node.children():
                    if each.type().name() == "rop_alembic" or each.type().name() == "rop_fbx":       
                        each.parm("execute").pressButton()


        node.parent().saveItemsToFile([node], output_path, save_hda_fallbacks = True)  

        save_message += "Node saved to: " + output_path + "\n"

    print(save_message)    
    hou.ui.displayMessage(save_message)




def loadItemsFromFilePath(file_path):
    category = file_path.rsplit("/", 1)[1].split("_", 1)[0]
    node_path = "/" + file_path.rsplit("/", 1)[1].split("_", 1)[1].rsplit("_", 1)[0].replace("~", "/")

    parent_node_path = node_path.rsplit("/", 1)[0]


    # Make sure there is a network editor pane tab to load into.
    pane_tab = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor) 
    if pane_tab is None:
        current_pane = hou.ui.paneUnderCursor()
        if current_pane is None:
            # This part may not be necessary.
            hou.ui.displayMessage("No pane was found. Please navigate to a network editor.")
            return None
        pane_tab = current_pane.createTab(hou.paneTabType.NetworkEditor)


    if hou.node(parent_node_path) is None: 
        parent_node_path = pane_tab.pwd().path()
    

    pane_tab.cd(parent_node_path)
    hou.clearAllSelected()

    try:
        hou.node(parent_node_path).loadItemsFromFile(file_path)
        loaded = True

    except:
        hou.ui.displayMessage("That was the wrong network context. Please navigate to a " + category + " network editor.")
        loaded = False
        pass


    loaded_items = hou.selectedItems()

    if loaded:
 
        #this for each loop isn't actually necessary in the current scheme where only single nodes are being published
        for each_node in loaded_items:
            addImportParameters(each_node, file_path)
            each_node.setPosition(pane_tab.cursorPosition())

    else:
        for each_node in loaded_items:
            each_node.destroy()
                    

# This didn't work I think because SideFX won't let you open this file format from their file browser because then you wouldn't need to buy a Houdini license.
#def importNodeMenu():
#    node_file = hou.ui.selectFile(start_directory=None, title="Select a .node file", pattern="*.node", chooser_mode=hou.fileChooserMode.Read)
#    print(node_file)


def loadFBXsFromFilePath(file_path):

    try:
        loaded_item = hou.hipFile.importFBX(file_path)[0]
        loaded = True

    except:
        hou.ui.displayMessage("FBX import failed!")
        loaded = False
        pass


    if loaded:
        processFBXcamera(loaded_item)
        addImportParameters(loaded_item, file_path, add_version_menu=False)

        # Make sure there is a network editor pane tab to load into.
        pane_tab = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor) 
        if pane_tab is None:
            current_pane = hou.ui.paneUnderCursor()
            pane_tab = current_pane.createTab(hou.paneTabType.NetworkEditor)

        loaded_item.setPosition(pane_tab.cursorPosition())



def processFBXcamera(node):
    input1 = node.item("1")
    cam_list = []
    for each in node.children():

        # Wire any unwired nodes to the subnet's input1 so that they can inherit transforms from the top level.
        if len(each.inputConnectors()) > 0:
            if each.input(0) == None:
                each.setInput(0, input1)

        if each.type().name() == "cam":
            cam_list.append(each)
    
    for each_cam in cam_list:
        # This gets rid of the troublesome expression in the aperture that tries to adaptively change that value based on the aspect ratio.
        aperture_parm = each_cam.parm("aperture")
        if len(aperture_parm.keyframes()) > 0:              
            exp = aperture_parm.expression()
            if "*max(" in exp:
                print("Overriding and removing the Aperture parameter expression.")
                value = float(exp.split("*max(", 1)[0])
                aperture_parm.deleteAllKeyframes()
                aperture_parm.set(value)



def addLabel(parm_group, name, label, index=0):

    new_parm = hou.LabelParmTemplate(name, label)
    if label == "":
        new_parm.hideLabel(1)

    parm_group.insertBefore((index,), new_parm)
        
    return parm_group


def addSeperator(parm_group, name, index=0):

    new_parm = hou.SeparatorParmTemplate(name)
    parm_group.insertBefore((index,), new_parm)
        
    return parm_group


def addString(parm_group, name, label, index=0, is_hidden=False):

    new_parm = hou.StringParmTemplate(name, label, 1, is_hidden=is_hidden)
    parm_group.insertBefore((index,), new_parm)
        
    return parm_group


def addScriptedStringMenu(parm_group, name, label, menu_script, callback_script, index=0):

    new_parm = hou.StringParmTemplate(name, label, 1, item_generator_script=menu_script, item_generator_script_language=hou.scriptLanguage.Python, script_callback=callback_script, script_callback_language=hou.scriptLanguage.Python)
    parm_group.insertBefore((index,), new_parm)
        
    return parm_group


def addToggle(parm_group, name, label, index=0, is_hidden=False):

    new_parm = hou.ToggleParmTemplate(name, label, is_hidden=is_hidden)
    parm_group.insertBefore((index,), new_parm)
    
    return parm_group


def lockParameters(node):
    all_parms = node.parms()
    for each in all_parms:
        try:
            each.lock(1)
        except:
            pass



def replaceNode(old_node, new_node):

    inputs = old_node.inputConnections()
    for each_connection in inputs:
        new_node.setInput(each_connection.inputIndex(), each_connection.inputNode(), each_connection.outputIndex())

    outputs = old_node.outputConnections()
    for each_connection in outputs:
        output_node = each_connection.outputNode()
        output_node.setInput(each_connection.inputIndex(), new_node, each_connection.outputIndex())

    new_node.setPosition(old_node.position())

    name = old_node.name() 
    old_node.destroy()
    new_node.setName(name)



def updateNodeFromFile(node, file_path):

    parent_node_path = node.parent().path()

    pane_tab = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    #pane_tab.setCurrentNode(node)
    pane_tab.cd(parent_node_path)
    hou.clearAllSelected()

    try:
        hou.node(parent_node_path).loadItemsFromFile(file_path)
        loaded = True

    except:
        loaded = False
        pass

    loaded_node = hou.selectedItems()[0]

    if loaded:
        addImportParameters(loaded_node, file_path)
        replaceNode(node, loaded_node)

        return loaded_node
   
    else:
        loaded_node.destroy()



def versionMenu(node):

    file_parm = node.parm("import_file_path")
    current_file_path = file_parm.eval()

    menu_list = []

    import os
    import re

    split_path = current_file_path.rsplit("/", 1)
    publish_dir = split_path[0]
    current_file = split_path[1]

    split_file = re.split(r'_v\d{3}', current_file)

    file_list = os.listdir(publish_dir)
    file_list = [each for each in file_list if re.split(r'_v\d{3}', each) == split_file]
    file_list.sort()
    file_list.reverse()

    for each in file_list:
        menu_list.append(publish_dir + "/" + each)
        menu_list.append(each[-9:-5])

    return menu_list



def addImportParameters(node, file_path, add_version_menu=True):

    info_parm_name = "import_001"
    short_path = file_path.split("/jobs", 1)[1].rsplit(".", 1)[0]

    parm_group = node.parmTemplateGroup()

    if node.parm(info_parm_name) is None:
        parm_group = addSeperator(parm_group, info_parm_name + "seperator")

    if node.parm("import_file_path") is None:
        parm_group = addString(parm_group, "import_file_path", "import_file_path", is_hidden=True)

    # if node.parm("is_selected") is None:
    #     parm_group = addToggle(parm_group, "is_selected", "is_selected", is_hidden=True)


    if node.parm("import_version") is not None:
        parm_group.remove("import_version")


    if add_version_menu is True:
        menu_script = "node = kwargs['node']\nimport DW_PublishAnything\nreturn DW_PublishAnything.versionMenu(node)"
        callback_script = "import DW_PublishAnything; DW_PublishAnything.onVersionChanged(kwargs['node'])"
        addScriptedStringMenu(parm_group, "import_version", "Version", menu_script, callback_script)

    if node.parm(info_parm_name) is None:
        parm_group = addLabel(parm_group, info_parm_name, "")

    node.setParmTemplateGroup(parm_group)
    node.parm("import_file_path").set(file_path)
    #node.parm("is_selected").setExpression("hou.pwd().isSelected()", hou.exprLanguage.Python)
    node.parm(info_parm_name).set("Imported from: " + short_path)
    if node.parm("import_version") is not None:
        node.parm("import_version").set(file_path)


def onVersionChanged(node):
    file_path = node.parm("import_version").eval()
    loaded_node = updateNodeFromFile(node, file_path)



