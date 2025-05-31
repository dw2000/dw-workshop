
# Code for linking parameters on child nodes to the same-named parameters on the parent node

control_node = kwargs["node"]
internal_node_list = control_node.children()
control_parm_list = control_node.parmsInFolder(("Internal Node Parms",))

for current_node in internal_node_list:
	for current_parm in control_parm_list:
		parm_name = current_parm.name()
		if (current_node.parm(parm_name) != None):
			current_node.parm(parm_name).setExpression('ch(\"../' + parm_name + '\")', language=hou.exprLanguage.Python)