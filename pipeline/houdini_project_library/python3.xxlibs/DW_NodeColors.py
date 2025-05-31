#
# DW Node Colors
# This script changes newly keyframed nodes to green and nodes with expressions to blue/green so that they are more obvious in large networks.
# Green takes precedent over blue/green if both keyframes and expressions exist on the same node.
#

# Set up this up as a callback in OnCreated.py and OnLoaded.py in a /scripts directory that is in your HOUDINI_PATH
# The callback is not stored in the nodes in the .hip file, so must be added once again every time a scene is opened.


import hou


def maybeSetNodeColor(node, parm_tuple):

    if parm_tuple.isTimeDependent():

        green = hou.Color((0.3, 0.65, 0.3))
        blue_green = hou.Color((0.275, 0.55, 0.55))

        # Check if the node is already green. 
        if node.color() != green:

            value_data = parm_tuple.valueAsData()
            
            # First, deal with nodes that simply have a single dictionary
            if isinstance(value_data, dict):
                type = list(value_data.keys())[0]

                if type == "keyframes":
                    try:
                        # change to green
                        node.setColor(green)
                                                    
                    except:
                        pass

                elif type == "expression":
                    try:
                        # change to blue/green
                        node.setColor(blue_green)
                    except:
                        pass

            # Next deal with nodes that have a list of dictionaries
            else:            
                for each in value_data:

                    if isinstance(each, dict):
                        type = list(each.keys())[0]

                        if type == "keyframes":
                            try:
                                # change to green
                                node.setColor(green)
                                break
                                
                            except:
                                pass

                        elif type == "expression":
                            try:
                                # change to blue/green
                                node.setColor(blue_green)
                            except:
                                pass


def maybeSetNodeColorCallback(node, event_type, **kwargs):
    parm_tuple = kwargs['parm_tuple']
    maybeSetNodeColor(node, parm_tuple)


# For reference, here is the code that should go into the OnCreated.py and OnLoaded.py...
# import hou
# if hou.isUIAvailable():
#     import DW_NodeColors
#     node = kwargs["node"]
#     node.addEventCallback((hou.nodeEventType.ParmTupleAnimated, ), DW_NodeColors.maybeSetNodeColorCallback)







