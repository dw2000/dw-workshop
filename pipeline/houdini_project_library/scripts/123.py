import os 
import hou


DW_SERVER = hou.getenv("JOB").rsplit("/", 3)[0] + "/"
print("")
print("Setting DW_SERVER to " + DW_SERVER)
os.environ["DW_SERVER"] = DW_SERVER
hou.allowEnvironmentToOverwriteVariable("DW_SERVER", True) 
hscript_command = "set {} = {}".format("DW_SERVER", DW_SERVER)
hou.hscript(hscript_command)


DW_JOB = hou.getenv("JOB").rsplit("/", 3)[1]
print("")
print("Setting DW_JOB to " + DW_JOB)
os.environ["DW_JOB"] = DW_JOB
hou.allowEnvironmentToOverwriteVariable("DW_JOB", True) 
hscript_command = "set {} = {}".format("DW_JOB", DW_JOB)
hou.hscript(hscript_command)


hou.playbar.setRestrictRange(0)


fps = float(os.environ["project_FPS"])
print("")
print("Setting FPS to " + str(fps))
hou.setFps(fps)


start_frame = 1001
end_frame = 1200
print("")
print("Initializing frame range to " + str(start_frame) + "-" + str(end_frame))
hou.playbar.setPlaybackRange(start_frame, end_frame)
hou.playbar.setFrameRange(start_frame, end_frame)


hou.setFrame(start_frame)




# This isn't entirely necessary but is nice to have
hscript_command = "set -g {} = {}".format("JOB", DW_SERVER + DW_JOB)
hou.hscript(hscript_command)
hscript_command = "set -g {} = {}".format("HIP", DW_SERVER + DW_JOB)
hou.hscript(hscript_command)