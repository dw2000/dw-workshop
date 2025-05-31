import os
import DW_PublishAnything


def dropAccept(file_list):

    if len(file_list) > 0:   

        # This part will maintain normal Houdini behavior for drag and dropping .hip files.
        if len(file_list) == 1 and os.path.splitext(file_list[0])[1] == ".hip":
            return False

        # This part loads .node files
        for file_path in file_list:

            
            if ":" in file_path:  # in case of Windows Z: drive mounting 
                from pathlib import Path
                file_path = str(Path(file_path).resolve())


            file_path = file_path.replace("\\", "/")


            if ".node" in file_path: # Why is this tested twice and done differently each time?  There must be reason.

                if file_path.rsplit(".", 1)[1].lower() == "node":
                    try:
                        DW_PublishAnything.loadItemsFromFilePath(file_path)
                    except:
                        return False


            elif ".fbx" in file_path.lower():

                if file_path.rsplit(".", 1)[1].lower() == "fbx":
                    try:
                        DW_PublishAnything.loadFBXsFromFilePath(file_path)
                    except:
                        return False

        return True

    return False


