
node = kwargs["node"]


# While we're here let's change the default res from 720 to 1080
node.parmTuple("res").set((1920, 1080))


# The script we will be using as a callback whenever the background image is changed:
callback_script = '''
import os, re

camera = hou.pwd()
unexpanded_image_file_path = camera.parm("vm_background").unexpandedString()

# In case someone pastes a Windows path into the parm:
unexpanded_image_file_path = unexpanded_image_file_path.replace(r"\\ "[0], "/")

# If it is only a directory and not a full path of some sort don't do anything.
if os.path.isdir(unexpanded_image_file_path) is False: 

    update = hou.ui.displayMessage("Update frame range and camera resolution?", buttons=("Yes", "No"), title="DW Camera")

    if update == 0:

        split_path = unexpanded_image_file_path.rsplit("/", 1)
        dir = split_path[0]
        file = split_path[1]
        frame_regex = r"(\\$F\d?)"
        #print(frame_regex)
        
        split_file = re.split(frame_regex, file)

        if len(split_file) == 3:
            
            file_list = os.listdir(dir)
          
            if len(split_file[1]) == 3:
                padding = "{" + split_file[1][2] + "}"
                
            else:
                padding = "*"

            file_regex = "(" + split_file[0] + r"\d" + padding + split_file[2] + ")"
            #print(file_regex)
            
            file_list = [each for each in file_list if re.fullmatch(file_regex, each)]

            if len(file_list) > 0:
                res = hou.imageResolution(dir + "/" + file_list[0])
                camera.parm("resx").set(res[0])
                camera.parm("resy").set(res[1])


                frame_list = [int(each[len(split_file[0]): - len(split_file[2])]) for each in file_list]
                
                frame_list.sort()
                
                start_frame = frame_list[0]
                end_frame = frame_list[-1]

                # What to change? Global frame range? Playback range? Both?
                hou.playbar.setPlaybackRange(start_frame, end_frame)
                #hou.playbar.setFrameRange(start_frame, end_frame)

            else:
            	print("The file path had a confusing format, leaving things unchanged.")
        
        else:
            print("No frame expression was found in the file path, leaving frame range unchanged.")

            image_file_path = camera.parm("vm_background").eval()
            res = hou.imageResolution(image_file_path)
            camera.parm("resx").set(res[0])
            camera.parm("resy").set(res[1])
'''


# Now apply the callback script to the parameter
parm_template_group = node.parmTemplateGroup()
parm_template = parm_template_group.find("vm_background")
parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
parm_template.setScriptCallback(callback_script)
parm_template_group.replace("vm_background", parm_template)
node.setParmTemplateGroup(parm_template_group)


















