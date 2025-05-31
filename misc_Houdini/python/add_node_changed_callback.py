import hou


def parameters_changed(node, event_type, **kwargs):
    parm_tuple = kwargs['parm_tuple']
    if parm_tuple is not None:

        try:
            # change to orange
            node.setColor(hou.Color((0.88, 0.48, 0.3)))
        except:
            pass




node.addEventCallback((hou.nodeEventType.ParmTupleChanged, ), parameters_changed)