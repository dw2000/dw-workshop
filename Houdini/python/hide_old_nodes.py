# Hide the old DW filecache node without breaking any scenes that still use it:
hou.sopNodeTypeCategory().nodeType("DW::DW_filecache::1.1").setHidden(True)