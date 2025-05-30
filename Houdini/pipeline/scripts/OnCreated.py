
# This script changes newly keyframed nodes to green and nodes with expressions to blue/green so that they are more obvious in large networks.
# Green takes precedent over blue/green if both keyframes and expressions exist on the same node.

# To set up this callback put it in a /scripts directory that is in your HOUDINI_PATH

import hou

node = kwargs["node"]



def is_parameter_animated(node, event_type, **kwargs):
    parm_tuple = kwargs['parm_tuple']
    if parm_tuple.isTimeDependent():

        # Check if the node is already green. 
        if node.color() != hou.Color((0.3, 0.65, 0.3)):

            value_data = parm_tuple.valueAsData()

            for each in value_data:

                if isinstance(each, dict):
                    type = list(each.keys())[0]

                    if type == "keyframes":
                        try:
                            # change to green
                            node.setColor(hou.Color((0.3, 0.65, 0.3)))
                            break
                            
                        except:
                            pass

                    elif type == "expression":
                        try:
                            # change to blue/green
                            node.setColor(hou.Color((0.275, 0.55, 0.55)))
                        except:
                            pass



# Or maybe ParmTupleChannelChanged, not sure what the difference is?
node.addEventCallback((hou.nodeEventType.ParmTupleAnimated, ), is_parameter_animated)

















