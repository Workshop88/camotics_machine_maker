#!/usr/bin/python3
'''
    xhtml_reader.py for camotics-machine-maker.py
    By D. Scott Williamson November 2024

    Reads and X3D .xhtml file and hopefully creates a usable Camotics CNC Machine
     
'''
from machine import Machine, Part
import lxml.html
import numpy as np
import os

'''
def rotation_matrix(angle, axis):
    """
    Converts an angle-axis representation to a rotation matrix.

    Args:
        angle (float): Angle of rotation in radians.
        axis (numpy.ndarray): Unit vector representing the axis of rotation (shape (3,)).

    Returns:
        numpy.ndarray: Rotation matrix (shape (3, 3)).
    """

    axis = axis / np.linalg.norm(axis)  # Normalize the axis vector
    x, y, z = axis

    c = np.cos(angle)
    s = np.sin(angle)

    return np.array([
        [c + x**2 * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [y * x * (1 - c) + z * s, c + y**2 * (1 - c), y * z * (1 - c) - x * s],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z**2 * (1 - c)]
    ])
'''    
    
def rotation_matrix(angle, axis):
    """Creates a rotation matrix from an angle and axis."""
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1 - c
    x, y, z = axis
    return np.array([
        [t*x**2 + c, t*x*y - s*z, t*x*z + s*y],
        [t*x*y + s*z, t*y**2 + c, t*y*z - s*x],
        [t*x*z - s*y, t*y*z + s*x, t*z**2 + c]
    ])
    
def xhtml_read(filespec):
    # new blank machine definition
    machine=Machine()
    
    # Use base filename without path or extension as machine name
    machine.name=os.path.basename(filespec).split(".")[0]

    # Open the file and parse the XML     
    with open(filespec, "rb") as f:
        file = f.read()
    tree = lxml.html.fromstring(file)

    # Find the shapes that have indexfaceset     
    xmlshapes=tree.xpath("//shape[./indexedfaceset]")

    # create machine parts from xhtml shapes    
    parts=[]
    for xmlshape in xmlshapes:
        # get shape name
        shapename=xmlshape.get("def")

        # parse part color 
        color=[64,64,64] #default color
        #color=np.random.randint(0, 255, 3) # random color
        xmlfacematerial=xmlshape.xpath("./appearance/material")
        if len(xmlfacematerial)==1:
            colorstring=xmlfacematerial[0].get("diffusecolor")
            if colorstring!=None:
                colorvalues=colorstring.split(" ")
                for i in range(len(colorvalues)):
                    color[i]=int(float(colorvalues[i])*255)

        # get the indexfaceset
        xmlfaceset=xmlshape.xpath("./indexedfaceset")[0]

        # get point coordinates for indexfaceset        
        xmlfacecoordinates=xmlfaceset.xpath("./coordinate")[0]
        # handle USE vs DEF
        xmlfacecoordinatesreference=xmlfacecoordinates.get("use")
        if xmlfacecoordinatesreference!=None:
            xmlfacedoordinatesxpath='//*[@def="%s"]'%xmlfacecoordinatesreference
            xmlfacecoordinates=tree.xpath(xmlfacedoordinatesxpath)[0]

        # Calculate the vertex transform for this shape from all hierarchical transforms
        
        # reference https://edutechwiki.unige.ch/en/X3D_grouping_and_transforms#Order_of_execution
        # Transformations are applied in the following order from the inside out
        #    a (possibly) non-uniform scale about an arbitrary point;
        #    a rotation about an arbitrary point and axis;
        #    a translation.
        # P' = T * C * R * SR * S * -SR * -C * P
        
        # collect transform elements in reverse order
        element=xmlshape
        elements=[]
        while element.tag!="scene":
            #print (element.tag)
            if element.tag=='transform':
                elements.append(element)
            element=element.getparent()
       
        # Start with identity matrix
        transform_matrix=np.identity(4)
        for element in reversed(elements):
            translationstrings=element.get("translation").split(' ')
            translationmatrix=np.identity(4)
            translationmatrix[0,3]=float(translationstrings[0])
            translationmatrix[1,3]=float(translationstrings[1])
            translationmatrix[2,3]=float(translationstrings[2])
            
            centerstrings=element.get("center").split(' ')
            centermatrix=np.identity(4)
            centermatrix[0,3]=float(centerstrings[0])
            centermatrix[1,3]=float(centerstrings[1])
            centermatrix[2,3]=float(centerstrings[2])
            ncentermatrix=centermatrix.copy()
            ncentermatrix[0,3]=-centermatrix[0,3]
            ncentermatrix[1,3]=-centermatrix[1,3]
            ncentermatrix[2,3]=-centermatrix[2,3]
            
            scaleorientationstrings=element.get("scaleorientation").split(' ')
            scaleaxis=np.array([float(scaleorientationstrings[0]),float(scaleorientationstrings[1]),float(scaleorientationstrings[2])])
            scaleangle=float(scaleorientationstrings[4])
            scaleorientationmatrix=np.identity(4)
            scaleorientationmatrix[:3, :3] = rotation_matrix(scaleangle,scaleaxis)
            nscaleorientationmatrix=np.identity(4)
            nscaleorientationmatrix[:3, :3] = rotation_matrix(-scaleangle,scaleaxis)
            
            scalestrings=element.get("scale").split(' ')
            scalematrix=np.identity(4)
            scalematrix[0,0]=float(scalestrings[0])
            scalematrix[1,1]=float(scalestrings[1])
            scalematrix[2,2]=float(scalestrings[2])
            
            rotationstrings=element.get("rotation").split(' ')
            rotationaxis=np.array([float(rotationstrings[0]),float(rotationstrings[1]),float(rotationstrings[2])])
            rotationangle=float(rotationstrings[4])
            rotationmatrix=np.identity(4)
            rotationmatrix[:3, :3]=rotation_matrix(rotationangle,rotationaxis)
            
            # P' = T * C * R * SR * S * -SR * -C * P
            transform_matrix=np.matmul(transform_matrix,translationmatrix)
            transform_matrix=np.matmul(transform_matrix,ncentermatrix)
            transform_matrix=np.matmul(transform_matrix,rotationmatrix)
            transform_matrix=np.matmul(transform_matrix,scaleorientationmatrix)
            transform_matrix=np.matmul(transform_matrix,scalematrix)
            transform_matrix=np.matmul(transform_matrix,nscaleorientationmatrix)
            transform_matrix=np.matmul(transform_matrix,ncentermatrix)
                                      
        # parse vertices from indexfaceset and apply shape transform 
        vertices=[]
        coordinatestring=xmlfacecoordinates.get("point")
        coordinatestrings=coordinatestring.split(', ')
        for i in range(len(coordinatestrings)):
            valuestrings=coordinatestrings[i].split(' ')
            vertex=[]
            for value in valuestrings:
                vertex.append(float(value))
            vertex.append(float(1.0))
            transformed_vertex = np.dot(transform_matrix,vertex )
            vertices.append(transformed_vertex)    
            
        # parse indices for faces
        faceindices=[]
        faceindexstrings=xmlfaceset.get("coordindex").split(",")
        face=[]
        for i in range(len(faceindexstrings)):
            value=int(faceindexstrings[i])
            if value==-1:
                faceindices.append(face)
                face=[] 
            else:
                face.append(value)
        
        # parse indices for lines (optional, assumes same vertex list as faces)
        # note: indexedlinesets are in a neighboring group/shape
        xmlshapeparentgroup=xmlshape.getparent().getparent()
        xmllineset=xmlshapeparentgroup.xpath("./group/shape/indexedlineset")
        lineindices=[]
        if len(xmllineset)==1:
            #xmllinecoordinates=xmllineset.xpath("./coordinate")[0] # duplicate of face vertices
            lineindexstrings=xmllineset[0].get("coordindex").split(",")
            line=[]
            for i in range(len(lineindexstrings)):
                value=int(lineindexstrings[i])
                if value==-1:
                    lineindices.append(line)
                    line=[] 
                else:
                    line.append(value)

        # Add data to a new machine Part                
        part=Part()
        part.name=shapename
        part.vertices=vertices
        part.lines=lineindices
        part.triangles=faceindices
        part.color=color
        parts.append(part)
    
    # Add parts to the machine 
    machine.parts=parts
    
    # Return the constructed machine
    return machine
    
 
       