for target_node in hou.node("/out").children():
    if "_ctrl" in target_node.name():
        if (target_node.parm("FluffMultiplier") == None):
            parm_group = target_node.parmTemplateGroup()
            parm_group.insertBefore(parm_group.find("rachis_stiff"), hou.FloatParmTemplate("FluffMultiplier", "FluffMultiplier", 1, (0.5,)))
            target_node.setParmTemplateGroup(parm_group)
