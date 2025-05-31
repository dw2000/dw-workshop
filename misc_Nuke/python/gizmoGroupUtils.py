#gizmoGroupUtils_v01

import os, nuke, nukescripts

#====================================================================
def importGizmoAsGroup(fileName = ''):


    if len(fileName) == 0:
        fileName = nuke.getFilename('Import a Gizmo as a Group', '*.gizmo', "", "", 'open')


    TEMP_FILE = os.path.join(os.environ['NUKE_TEMP_DIR'], 'tempGroup.txt') 
    nodeName = os.path.basename(fileName).rsplit('.', 1)[0]


    try:

        TEMP = open(TEMP_FILE, 'w')

        for line in open(fileName, 'r'):

            if line.startswith('Gizmo'):
                line = line.replace('Gizmo','Group')

            TEMP.write(line)


        TEMP.close()
        theGroup = nuke.nodePaste(TEMP_FILE)
        theGroup.setName(nodeName, uncollide=True)

        return theGroup

    except:
        print "File read/write error"





#====================================================================
def exportGroupAsGizmo(theGroup, fileName = ''):


    if len(fileName) == 0:
        fileName = nuke.getFilename('Export a Group as a Gizmo', '*.gizmo', "", "", 'save')


    TEMP_FILE = os.path.join(os.environ['NUKE_TEMP_DIR'], 'tempGizmo.txt') 
    header = "#! " + nuke.env['ExecutablePath'] +" -nx\n"



    nukescripts.misc.clear_selection_recursive()
    theGroup.setSelected(True)


    try:

        nuke.nodeCopy(TEMP_FILE)

        theGizmo = open(fileName, 'w')

        i = 0
        for line in open(TEMP_FILE, 'r'):

            if i != 2:
                if i == 0:
                    line = header

                if i == 3:
                    line = line.replace('Group','Gizmo')

                theGizmo.write(line)
            i +=1


        theGizmo.close()
        return True

    except:
        print "File read/write error"




#====================================================================
# GrizmoGoupFileConvert() converts Gizmos files to .nk Group files or vice versa, doesn't require Nuke Python API.  
# Will take a complete output file path for the second argument, or just a dir path, or nothing, and then fills in any missing info based on the input file's path. 
#
def GrizmoGoupFileConvert(in_path, out_path = ''):

    in_file_ext = os.path.splitext(in_path)[1].lower()

    if (in_file_ext == ".gizmo" or in_file_ext == ".nk") and in_path[0] != ".":

        if os.path.splitext(out_path)[1] == '':
            if in_file_ext == '.gizmo':
                out_file_ext = '.nk'

            if in_file_ext == '.nk':
                out_file_ext = '.gizmo'


            if os.path.splitext(out_path)[0] != '':
                if out_path[-1] == '/' or out_path[-1] == '\\':
                    out_path = out_path + os.path.splitext(os.path.basename(in_path))[0] + out_file_ext
                else:
                    out_path = out_path + os.sep + os.path.splitext(os.path.basename(in_path))[0] + out_file_ext

            else:
                out_path = os.path.splitext(in_path)[0] + out_file_ext

        else:
            out_file_ext = os.path.splitext(out_path)[1]
            

        print "Converting " + in_path + " to " + out_path


        try:
            out_file_object = open(out_path, 'w')

        except:
            print "File write error: " + out_path

         
        if out_file_ext == '.nk':

            i = 0
            for line in open(in_path, 'r'):

                if i == 0:               
                    line = 'set cut_paste_input [stack 0]\n'

                if i == 2:                    
                    out_file_object.write('push $cut_paste_input\n')
                    line = line.replace('Gizmo','Group')

                out_file_object.write(line)
                i +=1


        if out_file_ext == '.gizmo':
            i = 0
            for line in open(in_path, 'r'):

                if i != 2:
                    if i == 0:
                        line = '#!\n'

                    if i == 3:
                        line = line.replace('Group','Gizmo')

                    out_file_object.write(line)
                i +=1




        out_file_object.close()



        return out_path
         