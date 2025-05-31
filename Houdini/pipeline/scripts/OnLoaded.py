
import hou

if hou.isUIAvailable():
    import DW_NodeColors
    # DW Node Colors changes newly keyframed nodes to green and nodes with expressions to blue/green so that they are more obvious in large networks.
    # Green takes precedent over blue/green if both keyframes and expressions exist on the same node.

    node = kwargs["node"]
    node.addEventCallback((hou.nodeEventType.ParmTupleAnimated, ), DW_NodeColors.maybeSetNodeColorCallback)




