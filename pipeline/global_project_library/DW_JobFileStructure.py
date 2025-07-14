import os 
import ast
import re
import json
import shutil

# Initial/default values
_default_job_path = os.environ['DW_SERVER'] + os.environ['DW_JOB']

 # Folder names like Assets and Shots where work can be found.
_default_type_dir_list = os.environ['type_dir_list'] 

 # the folder under which the work scene files go.  i.e. .nk, .hip, ect.
_default_work_dir = "work" 

# List of steps that subfolders are named after, i.e. Comp, Anim, Fx, etc.
_default_step_list = ast.literal_eval(os.environ['step_list'])

# List of existing tasks/elements that subfolders are named after.  These can vary and custom items can be added.
# For example: Main, Roto, Fur, HDRI, etc.
_default_task_list = ["main"]


# Not implemented: support for asset category folders. This can be done by hardcoding those category folder names in the __type_dir_list



def dirLister(path):    # List directories in a directory (non-recursive), exluding files and hidden directories.
    if os.path.exists(path):
        dir_list = os.listdir(path)
        dir_list = [each for each in dir_list if os.path.isdir(os.path.join(path, each))]  
        dir_list = [each for each in dir_list if each[0] != "."]
        dir_list.sort()
    else:
        dir_list = []

    return dir_list


# Flattens any subsequent single keys in a dictionairy so we don't end up with lots of single item menus
def concat_single_keys(old_dict, separator="/"):
 
    if isinstance(old_dict, dict):

        new_dict = {}
        for key, value in old_dict.items():

            processed_value = concat_single_keys(value, separator)

            if isinstance(processed_value, dict) and len(processed_value) == 1:

                nested_key = list(processed_value.keys())[0]
                nested_value = processed_value[nested_key]

                concatenated_key = f"{key}{separator}{nested_key}"
                new_dict[concatenated_key] = nested_value
                
            else:
                new_dict[key] = processed_value
                
        return new_dict

    else:
        return old_dict



def setJobVariables(job_name, full_file_path):

    # C:/Dropbox/_work/jobs/machine_testing/build/cat/scenes/style/female_001/fx_cat_lookdev_female_001_v011_david.wanger.hip
    # C:/Dropbox/_work/jobs/machine_testing/films/the_drop/shots/0010/scenes/fx/main/0010_fx_main_v058.hip


    if job_name in full_file_path:  # If the job_name isn't in the file path then the file isn't part of the current pipeline environment, so do nothing.

        shorter_path = full_file_path.split(job_name, 1)[-1]
        # /build/cat/work/lookdev/female_001/fx_cat_lookdev_female_001_v011_david.wanger.hip
        # /films/the_drop/shots/0010/work/anim/main/0010_fx_main_v058.hip

        split_path = shorter_path.split("/")[1:-1]
        # ['build', 'cat', 'work', 'lookdev', 'female_001']
        # ['films', 'the_drop', 'shots', '0010', 'work', 'anim', 'main']


        token_count = len(split_path)


        if token_count > 4:    # Quick check in case an obviously non-pipeline file is being opened

            pipeline_env = {}

            pipeline_env["DW_VERSION"] = re.search(r'_v\d{3}[._]', shorter_path).group(0)[1:-1]    # v057

            if token_count >= 5 and token_count < 7:  
                pipeline_env["DW_TYPE"] = "BUILD"
                pipeline_env["DW_ELEMENT"] = split_path[-1]    # female_001 
                pipeline_env["DW_DEPT"] = split_path[-2]    # lookdev

                if token_count == 5: 
                    pipeline_env["DW_ASSET"] = split_path[-4]    # cat    

                elif token_count == 6: # In case there is an extra layer of organization i.e. /build/creatures/cat/
                    pipeline_env["DW_ASSET"] = split_path[-5] + "/" + split_path[-4]    # creatures/cat   


            
            elif token_count >= 7:
                pipeline_env["DW_TYPE"] = "SHOT"
                pipeline_env["DW_ELEMENT"] = split_path[-1]    # main 
                pipeline_env["DW_DEPT"] = split_path[-2]    # fx
                pipeline_env["DW_SHOT"] = split_path[-4]    # 0010

                if token_count == 7:            
                    pipeline_env["DW_FILM"] = split_path[-6]    # the_drop

                if token_count == 8: # In case there is an extra layer of organization i.e. /films/the_drop/sequence1/shots        
                    pipeline_env["DW_FILM"] = split_path[-7] + "/" + split_path[-6]    # the_drop/sequence1


            # Are we running Houdini?
            try:
                import hou
                Houdini = True 
            except: 
                Houdini = False

            for each_key in pipeline_env.keys():
                os.environ[each_key] = pipeline_env[each_key]

                if Houdini:  # Houdini needs these extra steps to be thorough
                    hou.allowEnvironmentToOverwriteVariable(each_key, True) 
                    hscript_command = "set -g {} = {}".format(each_key, pipeline_env[each_key])
                    hou.hscript(hscript_command)




def writeObjectToJson(obj, file_path, backup_copy=True):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(obj, json_file, indent=4)
        #print(f"Written to '{file_path}'")

        if backup_copy:  # Make a backup copy, good for when this is a non-versioned file that will be re-written to multiple times.
            try:
                backup_dir = file_path.rsplit("/" , 1)[0] + "/backup"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                shutil.copy(file_path, backup_dir)
            except IOError as b:
                print(f"Error writing to backup file: {b}")

    except IOError as f:
        print(f"Error writing to file: {f}")



def readObjectFromJson(file_path):

    try:
        with open(file_path, 'r') as json_file:
            loaded_obj = json.load(json_file)
        #print(f"Loaded from '{file_path}':")

        return loaded_obj

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")




    

class LookupData:


    def __init__(self, job_path=_default_job_path, type_dir_list=_default_type_dir_list, work_dir=_default_work_dir, step_list=_default_step_list, task_list=_default_task_list):

        self.job_path = job_path
        self.type_dir_list = type_dir_list
        self.work_dir = work_dir
        self.step_list = step_list
        self.__task_list = task_list

        self.__default_scan_depth = 3
        self.folders_dict = {}

        self.updateFoldersDict()



    # folders_dict contains all the numbered/named shot or asset folders that we might want to save a file into.
    def updateFoldersDict(self, job_path=None, type_dir_list=None, max_scan_depth=None, concat=True):
        if not job_path: job_path = self.job_path
        if not type_dir_list: type_dir_list = self.type_dir_list
        if not max_scan_depth: max_scan_depth = self.__default_scan_depth

        self.folders_dict[job_path] = self.__recursive_item_search(job_path, type_dir_list, max_scan_depth)

        if concat:
            self.folders_dict = concat_single_keys(self.folders_dict)

        return self.folders_dict



    def __recursive_item_search(self, job_path, type_dir_list, max_scan_depth, current_depth=0):
        item_dict = {}

        if current_depth <= max_scan_depth:

            for each_dir in dirLister(job_path):
                if each_dir in type_dir_list:
                    item_list = dirLister(job_path + "/" + each_dir)
                    item_dict[each_dir] = item_list
                else:
                    next_dict = self.__recursive_item_search(job_path + "/" + each_dir, type_dir_list, max_scan_depth, current_depth + 1)
                    if next_dict is not None: 
                        item_dict[each_dir] = next_dict
        
        if len(item_dict) > 0:        
            return item_dict
        else:
            return None
        

    def printFoldersDict():
    # Using json to visualize the tree structure of folders_dict...
        print(json.dumps(self.folders_dict, indent=4))
     


    def updateTaskList(self, search_dir=None, add_item=None):
        top_item = self.__task_list[0]    # Store the top/default menu selection so we can keep it on top.
        temp_list = self.__task_list[1:]  # If there were already some items in the list they will be preserved. This is handy when switching between similar shots.

        if search_dir is not None:
            temp_list = temp_list + dirLister(search_dir)

        if add_item is not None:
            temp_list = temp_list + [add_item]

        temp_list = list(set(temp_list)) # Keep unique items only
        if top_item in temp_list:
            temp_list.remove(top_item)
        temp_list.sort()
        self.__task_list = [top_item] + temp_list

        return self.__task_list



    def getLatestVersion(self, full_path):

        split_path = full_path.rsplit("/", 1)
        save_dir = split_path[0]                         # C:/Dropbox/_work/jobs/machine_testing/films/the_drop/shots/0010/scenes/fx/main                       
        current_file = split_path[1]                     # main_film_0010_fx_theDrop_v058_wange.hiplc
        file_type = current_file.rsplit(".", 1)[1]

        split_file = re.split(r'_v\d{3}', current_file)  # ['main_film_0010_fx_theDrop', '_wange.hiplc']
        file_left_side = split_file[0]

        max_version = 0

        if(os.path.isdir(save_dir)):
            file_list = os.listdir(save_dir)
            file_list = [each for each in file_list if "." in each[1:-1] and each.rsplit(".", 1)[1] == file_type]
            file_list = [each for each in file_list if "_v" in each and re.split(r'_v\d{3}', each)[0] == split_file[0]]

            version_list = [int(re.search(r'_v\d{3}[._]', each).group(0)[2:-1]) for each in file_list] 
            if len(version_list) > 0:
                version_list.sort()
                max_version = version_list[-1]
                
        return max_version
