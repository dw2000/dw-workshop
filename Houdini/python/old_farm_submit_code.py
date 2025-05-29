
#
#  This is some old code for a Houdini Mantra farm render system with support for Rop depedencies.
#  The getInputsRecursive function is still useful, the rest probably not so much. 
#



# getInputsRecursive returns a list of a node's upstream input node paths paired with int values representing each node's recusion depth.

def getInputsRecursive(node, ingore_bypassed=True, ignore_node_types=[]):



    input_node_list = []



    for each_node in node.inputs():

        if each_node is not None:

            more_nodes = getInputsRecursive(each_node, ingore_bypassed, ignore_node_types)



            # Add current level nodes with an initial recursion depth of 1 if valid

            if each_node.isBypassed() is False or ingore_bypassed is False:

                if each_node.type().name() not in ignore_node_types:

                    input_node_list.append([each_node.path(), 1])



                    # And increment upstream nodes

                    for each in more_nodes:

                        each[1] = each[1] + 1



            input_node_list = input_node_list + more_nodes



    return input_node_list







def filterNonRenderableNodes(ROP_list):

    errors = ''

    unsupported_ROPs = ['batch', 'framecontainer', 'framedep', 'netbarrier', 'prepost', 'switch']



    renderable_ROPs = []



    for each_path in ROP_list:

        node = hou.node(each_path)

        node_type_name = node.type().name()



        # Follow any fetch node to get its source path

        if node_type_name == 'fetch':

            renderable_ROPs.append(node.parm('source').eval())



        elif node_type_name in unsupported_ROPs:

            errors = errors + '\n' + node_type_name + ' ROPs are not currently supported for farm submission.'



        # Give error for subnets without frame ranges.

        elif node_type_name == 'subnet' and node.parm('f1') == None and hou.pwd().parm('override_frames').eval() == 0:

            errors = errors + '\nSubnet ROPs require a float size 3 frame range parm, f1 f2, f3 in order to be rendered on the farm.  Or alternately you can use Override Frame Range on the LFX FarmRender ROP.'



        # elif node.type().name() == 'geometry':

        #     sop = node.parm('soppath').eval()

        #     if hou.node(sop) is None:

        #         errors = errors + '\nBad geo reference: ' + sop + ' in ' + node.path() + '.'



        elif node.type().name() == 'ifd':

            cam = node.parm('camera').eval()

            if hou.node(cam) is None or hou.node(cam).type().name() != 'cam':

                errors = errors + '\nBad camera reference: ' + cam + ' in ' + node.path() + '.'





        renderable_ROPs.append(each_path)





    if len(errors) > 0:

        raise Exception(errors)



    return renderable_ROPs






def preFlight(node):

    python_string = node.parm('preflight_script').eval()

    if python_string.strip() != '':

        exec python_string





def submitToFarm(node):

    import os 

    import chainlink

    from chainlink import Chainlink

    from links import Link, MantraLink





    if hou.hipFile.hasUnsavedChanges() is True and node.parm('save_first').eval() == 1:

        print 'Saving .hip file...'

        hou.hipFile.save()







    if node.parm('override_trange').eval() == 2 and node.parm('override_frames').eval() == 1:                                

        frame_iterations = len(node.parm("frames").eval().replace(',', ' ').strip().split())

                           

    else:

        frame_iterations = 1



    # The top-level for loop is a crappy temporary method for queuing individual frames on the farm by iterrating through everything and submitting each as a separtate job

    for frame_index in xrange(frame_iterations):



        for each_input_node in node.inputs():



            if each_input_node is not None:

                dependency_list = getInputsRecursive(each_input_node, ingore_bypassed=True, ignore_node_types=['null', 'merge'])



                # Create a dictionairy with a key for each recursion depth, also find max recursion depth.  

                # There's probably a more elegant way to do this.

                dependency_dict = {}

                max_recursion_depth = 0



                # Populate dictionairy starting with the initial node

                dependency_dict[0] = [each_input_node.path()]



                # and then all of its upstream nodes

                for each in dependency_list:

                    if each[1] not in dependency_dict.keys():

                        max_recursion_depth = max(each[1], max_recursion_depth)

                        dependency_dict[each[1]] = [each[0]]

                    else:

                        dependency_dict[each[1]].append(each[0])





                # Create a chain object to which links will be added.

                render_chain = Chainlink(hou.hipFile.path())


                #

                # Create a chain link for each recursion depth-

                #

                # Generaly speaking, every ROP with the same recursion depth will get rendered at the same time.

                # Mantra nodes will be queued on their own as each is encountered rather than running in parallel.  They

                # will need to finish both ifd and mantra and before any other nodes on the same recursion depth get rendered. 

                # 



                i = max_recursion_depth

                while i>=0:

                    ROP_list = filterNonRenderableNodes(dependency_dict[i])

                    if len(ROP_list) > 0:

                        link = Link()

                        link.setPriority(node.parm('priority').eval())

                        for each_ROP_path in ROP_list:

                            ROP_node = hou.node(each_ROP_path)



                            if node.parm('override_frames').eval() == 0:

                                f1 = ROP_node.parm("f1").eval()

                                f2 = ROP_node.parm("f2").eval()

                                f3 = ROP_node.parm("f3").eval()



                            else:

                                # for current frame mode

                                if node.parm('override_trange').eval() == 0:

                                    f1 = f2 = hou.frame()

                                    f3 = 1



                                # for frame range mode

                                if node.parm('override_trange').eval() == 1:                                

                                    f1 = node.parm("override_f1").eval()

                                    f2 = node.parm("override_f2").eval()

                                    f3 = node.parm("override_f3").eval()



                                # for frame list mode

                                # this is the temporary workaround mentioned above

                                if node.parm('override_trange').eval() == 2:                                

                                    f1 = f2 = float(node.parm("frames").eval().replace(',', ' ').strip().split()[frame_index])

                                    f3 = 1                       


                            # check for ifd -> mantra render combo which gets handled completely differently

                            if ROP_node.type().name() == 'ifd' and ROP_node.parm('soho_outputmode').eval() == 0:

                                 mantra_link = MantraLink(each_ROP_path, f1, f2, f3)

                                 mantra_link.setPriority(node.parm('priority').eval())

                                 mantra_link.setImage(os.path.dirname(os.path.abspath(ROP_node.parm('vm_picture').eval().replace('\\', '/'))))                             

                                 render_chain.addLink(mantra_link)

                            else:

                                link.addNode(each_ROP_path, f1, f2, f3)





                        # In case there was only a mantra/ifd combo then the link will be empty

                        if len(link.nodes) > 0:

                            render_chain.addLink(link)

                    i-=1




                if len(render_chain.links) > 0:

                    print 'Submiting render chain...'

                    for each_link in render_chain:

                        print 'chain link: ' + str(each_link.nodes)[11:]

                        print ''



                    if node.parm('debug').eval() == 0:

                        render_chain.disableIRush()

                        render_chain.start()






def postFlight(node):

    if node.parm('open_iRush').eval() == 1:

        import subprocess

        subprocess.Popen('C:/rush/bin/irush.exe')





def submissionSteps(node):

    preFlight(node)

    submitToFarm(node)

    postFlight(node)

