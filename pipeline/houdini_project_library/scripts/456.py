import os
import hou



# The Houdini allowEnvironmentToOverwriteVariable function does not work as expected, so you have to do this silly dance...
temp_variable = hou.getenv('DW_JOB')
# hou.unsetenv("DW_JOB") # Remove the persistant env var setting stored in the current .hip file but also the system env var.
# os.environ["DW_JOB"] = temp_variable # Restore the system env var, but not the one in the .hip

# hou.allowEnvironmentToOverwriteVariable("DW_JOB", True) # With a system env existing but not one existing in the current .hip, this function will now work properly. 

#hscript_command = "set -g {} = {}".format("DW_JOB", temp_variable)
#hou.hscript(hscript_command)
# Upon opening a new .hip it will store the system env var in it.



if hou.isUIAvailable():    # Checking here to avoid trying to load any pipeline modules when on cloud render farms

    import DW_JobFileStructure
    DW_JobFileStructure.setJobVariables(os.environ["DW_JOB"], hou.hipFile.path())

    import hdefereval
    import DW_SaveLoad
    hdefereval.executeDeferred(DW_SaveLoad.updateTitleBar)

    import DW_Import
    DW_Import.update_nodes()  # Update versioning for any published .node nodes or for any files loaded in an Import node.




