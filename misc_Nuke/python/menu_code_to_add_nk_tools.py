###########################################################################################
##### Add .nk tools to the toolbar (and tab menu)
##### These are nodes or sets of nodes saved as .nk scripts that can be loaded into the active scene as some sort of a tool.

nk_tool_path = nuke.filenameFilter("/xxx/yyyy/zzzzz/nk_tools")

nuke.menu( 'Nodes' ).addMenu( 'DW/.nk tools', icon="dw-logo.png")

# Find all .nk tools and add them to the toolbar.
dir_list = os.listdir(nk_tool_path)
dir_list.sort()
for nk_file in dir_list:
    name, ext = os.path.splitext(nk_file)
    if ext.lower() == ".nk" and name[0] != ".":
        name = name.replace("_", " ")
        menuBar.addCommand('DW/.nk tools/' + name, "nuke.nodePaste('" + nk_tool_path + "/" + nk_file + "')")

###########################################################################################