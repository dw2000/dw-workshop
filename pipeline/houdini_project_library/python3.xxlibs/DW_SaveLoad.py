import hou
import os
import re
import getpass
import DW_JobFileStructure
import DW_SaveFileWindow


# to do: auto-load current shot path


# DW_JobFileStructure.folders_dict is a dictionairy of all the numbered/named shot or asset folders that we might want to save a file into.
# DW_JobFileStructure.LookupData().printFoldersDict() to display a json representation of the structure.
# It should take a form something like this:
# {
#     "C:/Dropbox/_work/_structured_projects/jobs/test_job": {
#         "build": [
#             "cat",
#             "crowd"
#         ],
#         "sequences": {
#             "the_beach": {
#                 "shots": [
#                     "000_asdfasdf_001",
#                     "named_shot"
#                 ]
#             },
#             "the_drop": {
#                 "shots": [
#                     "0010",
#                     "0020",
#                     "0030"
#                 ]
#             }
#         }
#     }
# }
#


def updateTitleBar():

    old_title_bar_text = hou.qt.mainWindow().windowTitle()
    new_title_bar_text = old_title_bar_text

    current_job = hou.getenv("DW_JOB")

    if current_job is not None:
        if current_job in old_title_bar_text: # the text includes a file path that is located in this job
            #if "/" in old_title_bar_text:   
            new_title_bar_text = old_title_bar_text.split(current_job, 1)[1]  # Shorten the file path for readabilty by chopping off the left side

        new_title_bar_text = current_job + " - " + new_title_bar_text
        hou.qt.mainWindow().setWindowTitle(new_title_bar_text)



def getFileExt():
    # Query-ing the license type is important to avoid mismatches between the file's extension and what type of file it actually is.
    license_type = hou.licenseCategory().name()
    if license_type == "Apprentice":
        file_type = "hipnc"
    elif license_type == "Indie":
        file_type = "hiplc"       
    else:
         file_type = "hip" 

    return file_type
    



def saveToJson(output_dictionary):   # Store various data like notes and username to a json file
    json_file_name = output_dictionary["output_dir"] + "/" + output_dictionary["base_name"] + "." + output_dictionary["file_ext"] + ".json"
    version_list = [output_dictionary]
    if os.path.exists(json_file_name):
        version_list += DW_JobFileStructure.readObjectFromJson(json_file_name)

    DW_JobFileStructure.writeObjectToJson(version_list, json_file_name)




def save():

    job_data = DW_JobFileStructure.LookupData()

    file_ext = getFileExt()

    output_dictionary = DW_SaveFileWindow.open_save_dialog(job_data, file_ext, current_file_path=hou.hipFile.path())  # Returns the info needed to save and log the file   

    if output_dictionary is not None:
        if "output_dir" in output_dictionary.keys():

            save_file_path = output_dictionary["output_dir"] + "/" + output_dictionary["output_file"]
            print(save_file_path) 

            # DW_JOB was set when opening Houdini and isn't ever expected to change.
            DW_JobFileStructure.setJobVariables(os.environ["DW_JOB"], save_file_path)

            if not os.path.exists(output_dictionary["output_dir"]):
                os.makedirs(output_dictionary["output_dir"])

            # this next line is the slow part:
            hou.hipFile.save(save_file_path)

            saveToJson(output_dictionary)
            updateTitleBar()



def versionUp():

    current_hip = hou.hipFile.path()
    test = re.search(r'_v\d{3}[._]', current_hip) # Check for valid versioning in the file name 

    if test is not None:

        split_path = current_hip.rsplit("/", 1)
        output_dir = split_path[0]                         # C:/Dropbox/_work/jobs/machine_testing/films/the_drop/shots/0010/scenes/fx/main
                                                         # //ditto/jobs/dw_test_0012/films/main_film/shots/0010/scenes/tracking/main
                                                         
        current_file = split_path[1]                     # main_film_0010_fx_theDrop_v058_wange.hiplc
                                                         # main_film_0010_tracking_main_v004_david.wanger_test.hip
                                                     
        split_file = re.split(r'_v\d{3}', current_file)  # ['main_film_0010_fx_theDrop', '_wange.hiplc']
        file_left_side = split_file[0]

        file_ext = getFileExt()

        # any comments in the file name will be stripped out
        file_right_side = "." + file_ext


        file_list = os.listdir(output_dir)
        file_list = [each for each in file_list if "." in each[1:-1] and each.rsplit(".", 1)[1] == file_ext]
        file_list = [each for each in file_list if "_v" in each and re.split(r'_v\d{3}', each)[0] == split_file[0]]

        version_list = [int(re.search(r'_v\d{3}[._]', each).group(0)[2:-1]) for each in file_list] 
        version_list.sort()
        max_version = version_list[-1]
        new_version_string = "v" + str(max_version + 1).rjust(3, '0')   # v005

        print("Incrementing version number and saving...")
        hou.ui.setStatusMessage("Incrementing version number and saving...")
        "Incrementing version number and saving..."
        output_file = file_left_side + "_" + new_version_string + file_right_side
        new_full_path = output_dir + "/" + output_file

        hou.putenv("DW_VERSION", new_version_string)

        # this next line is the slow part:
        hou.hipFile.save(new_full_path)

        print("Saved to: " + output_file)
        hou.ui.setStatusMessage("Saved to: " + output_file)
   
        output_dictionary = {}
        output_dictionary["file_ext"] = file_ext
        output_dictionary["output_dir"] = output_dir
        output_dictionary["output_file"] = output_file
        output_dictionary["base_name"] = file_left_side
        output_dictionary["version"] = max_version + 1
        output_dictionary["user"] = getpass.getuser() 
        saveToJson(output_dictionary)     

        updateTitleBar()

    else:
        print("Filename is lacking a valid version number of the form: '_v000'")