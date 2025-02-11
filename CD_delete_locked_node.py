from maya import cmds

listNodes = cmds.ls(selection=True)
for node in listNodes:
    cmds.lockNode( node, lock=False )
    cmds.delete(node)