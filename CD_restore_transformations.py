'''

This project is licensed under the Modified MIT License.
Copyright (c) 2024 Clement Daures. All rights reserved.

HOW TO USE :

Select at least one face and run the script

'''

import maya.cmds as cmds

def restore_transform_verif(*args):
    
    '''Check if user selected a face using verify_face_selection() and return a message'''
    
    #Condition face selected
    if verify_face_selection():
        restore_transform()
    else :
        print("No face selected, please select at least one face")

def verify_face_selection():
    
    '''Verify if at least one face have been selected'''
    
    # Get selected objects
    selected_objects = cmds.ls(selection=True, flatten=True)
    
    # Check if any selected object is a mesh and has face components
    for obj in selected_objects:
        if cmds.objectType(obj) == "mesh" and cmds.filterExpand(obj, selectionMask=34):  # 34 represents face component type
            return True
    
    return False

def restore_transform():
    
    '''Restore Transformations: Restores the transformations to their original state before freezing'''
    
    # Create lists
    del_uv = []
    projection = []
    objs = []
    targets = cmds.ls(sl=True) 
    objs2 = cmds.ls(sl=True, type="transform")
    
    # Exclude objects of type 'transform' from component selection
    targets = list(set(targets) - set(objs2))
    
    for target in targets:
        objs.append(target.split('.')[0])

    cmds.constructionHistory(toggle=True)

    if not cmds.objExists("zLocator"):
        cmds.spaceLocator(n="zLocator", p=(0, 0, 0))
    
    # Process component-selected objects
    if objs:
        for i in range(len(objs)):
            # Snap locator to selected object
            cmds.makeIdentity(objs[i], apply=True, t=True, r=True, s=True, n=False)
            del_uv.append(cmds.polyMapDel(objs[i], ch=True))
            cmds.select(targets[i])
            projection.append(cmds.polyProjection(ch=True, type="Planar", ibd=True, kir=True, md="b"))
            cmds.select(targets[i], "zLocator")
            cmds.pointOnPolyConstraint(targets[i], "zLocator", maintainOffset=False)
            cmds.delete(cmds.listRelatives("zLocator", typ="constraint"))
            cmds.setAttr("zLocator.rotateX", cmds.getAttr("zLocator.rotateX") - 90)
            
            # Snap locator to selected object's pivot
            pivot = cmds.xform(objs[i], q=True, rp=True)
            cmds.move(pivot[0], pivot[1], pivot[2], "zLocator", rpr=True)
            
            # Snap object to world origin
            translate = cmds.getAttr("zLocator.translate")[0]
            rotate = cmds.getAttr("zLocator.rotate")[0]
            cmds.parentConstraint("zLocator", objs[i], mo=True, w=1)
            cmds.move(0, 0, 0, "zLocator", a=True)
            cmds.rotate(0, 0, 0, "zLocator", a=True)
            
            # Restore object's transform
            cmds.select(objs[i])
            cmds.delete(cmds.listRelatives(objs[i], typ="constraint"))
            cmds.makeIdentity(objs[i], apply=True, t=True, r=True, s=True, n=False)
            cmds.move(translate[0], translate[1], translate[2], objs[i], a=True)
            cmds.rotate(rotate[0], rotate[1], rotate[2], objs[i], a=True)
        
        # Clean up data
        flat_projection = [item for sublist in projection for item in sublist]
        flat_del_uv = [item for sublist in del_uv for item in sublist]
        cmds.delete(flat_projection)
        cmds.delete(flat_del_uv)
        cmds.delete(objs, ch=True)

    # Process transform-selected objects
    if objs2:
        for ob in objs2:
            cmds.makeIdentity(ob, apply=True, t=True, r=True, s=True, n=False)
            cmds.select(ob, "zLocator")
            cmds.delete(cmds.pointConstraint("zLocator", ob, offset=[0, 0, 0], weight=1))
            cmds.move(0, 0, 0, ob, rpr=True)
            cmds.makeIdentity(ob, apply=True, t=True, r=True, s=True, n=False)
            cmds.select("zLocator", ob)
            cmds.delete(cmds.pointConstraint("zLocator", ob, offset=[0, 0, 0], weight=1))

    cmds.delete("zLocator")

restore_transform()

