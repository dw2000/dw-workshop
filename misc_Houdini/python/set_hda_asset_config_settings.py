


# Asset Manager config settings for otls and hdas
# commands from https://www.sidefx.com/docs/houdini/commands/otconfig.html

# Set these in a startup script to make sure everyone is playing by the same rules

# Turn off Preference to Definitions Saved in Hip File
hou.hscript("otconfig -i 0")

# Turn off Preference to Definitions with Latest Date
hou.hscript("otconfig -l 0")

# Turn off Save Operator Definitions to Hip File
hou.hscript("otconfig -s 0")

# Turn off Save Definitions of Unlocked Assets to Hip File
hou.hscript("otconfig -S 0")

# Turn on Leave Values When Defaults Change
hou.hscript("otconfig -u 1")

# Turn off Use OPlibraries files to find HDAs
hou.hscript("otconfig -o 0")