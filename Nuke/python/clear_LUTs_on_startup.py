##### REPLACE existing viewers

##### Running this in all cases to clear out any registered LUTs that may be missing.
for viewer in nuke.allNodes('Viewer', group=nuke.root()):
    name = viewer['name'].value()
    xpos = viewer.xpos()
    ypos = viewer.ypos()
    nuke.delete(viewer)

    new_viewer = nuke.createNode('Viewer')
    new_viewer['name'].setValue(name)
    new_viewer.setXYpos(xpos, ypos)

