'''
    Camotics machine data
    This file provides the abstraction and interfaces for 
    the data needed to output a Camotics compatible machine
'''
import os

class Machine:
    name="Undefined"
    tool=[1,1,1]
    workpiece=[0,0,0]
    reverse_winding=False
    transform=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    parts=[]
    
    # Machine initialization
    def __init__(self):
        # Default initialization is a red and green triangle for testing purposes
        part1=Part()
        part1.name="part1"
        part1.color=[255,0,0]
        part2=Part()
        part2.name="part2"
        part2.color=[0,255,0]
        part2.init=[10,10,10]
        self.parts=[part1,part2]
   
    # Write machine files 
    def write(self,basefilespec):
        # Create tco filespec from basefilespec and create .tco file
        tcofilespec="%s.tco"%basefilespec
        tcofile=open(tcofilespec, "w")
        
        # Create json filespec from basefilespec and create .json file
        jsonfilespec="%s.json"%basefilespec
        jsonfile=open(jsonfilespec, "w")
        
        # Isolate the .tco filename to include in the .json file
        slashindex=tcofilespec.lower().rfind(os.path.sep)
        if slashindex>0:
            tcofilename=tcofilespec[slashindex+1:]
        else:
            tcofilename=tcofilespec
        
        # Write base machine .json data
        jsonfile.write("{\n")
        jsonfile.write('\t"name": "%s",\n'%self.name)
        jsonfile.write('\t"model": "%s",\n'%tcofilename)
        jsonfile.write('\t"tool": %s,\n'%self.tool)
        jsonfile.write('\t"workpiece": %s,\n'%self.workpiece)
        jsonfile.write('\t"reverse_winding": %s,\n'%('true' if self.reverse_winding else 'false'))
        jsonfile.write('\t"transform": %s,\n'%self.transform)
        jsonfile.write('\t"parts": {\n')     

        # Write tco and json contents for each part in the machine
        for i in range(len(self.parts)):
            part=self.parts[i]
            part.writetco(tcofile)
            part.writejson(jsonfile,i==len(self.parts)-1)
        
        # Close .tco file
        tcofile.close()

        # Conclude and close .json file
        jsonfile.write("\t}\n")
        jsonfile.write("}\n")
        jsonfile.close()

class Part():
    # Initial values for all fields of a machine part
    name="Undefined"
    transform=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    color=[1,1,1]
    vertices=[[0,0,0],[10,10,0],[0,10,10]]
    lines=[[0,1],[1,2],[2,0]]
    triangles=[[0,1,2]]
    init=[0,0,0]
    home=[0,0,0]
    min=[0,0,0]
    max=[0,0,0]
    movement=[0,0,0]
    
    # Write the tco file containing mesh and line information for each part
    def writetco(self, tcofile):
        #write [name]
        tcofile.write("[%s]\n"%self.name)
        #write KeyFormat=D4
        tcofile.write("KeyFormat=D4\n")
        #write lines
        for i in range(len(self.lines)):
            tcofile.write("l%04d=%d,%d\n"%(i,self.lines[i][0],self.lines[i][1]))
        #write nl,nt,nv
        tcofile.write("nl=%d\n"%len(self.lines))
        tcofile.write("nt=%d\n"%len(self.triangles))
        tcofile.write("nv=%d\n"%len(self.vertices))
        #write triangles
        for i in range(len(self.triangles)):
            tcofile.write("t%04d=%d,%d,%d\n"%(i,self.triangles[i][0],self.triangles[i][1],self.triangles[i][2]))
        #write vertices
        for i in range(len(self.vertices)):
                tcofile.write("v%04d=%0.3f,%0.3f,%0.3f\n"%(i,self.vertices[i][0],self.vertices[i][1],self.vertices[i][2]))
        #write newline
        tcofile.write("\n")

    # Write the .json file that describes the arrangements of parts that make a machine
    def writejson(self, jsonfile,lastpart):
        #write        "x": {
        jsonfile.write('\t\t"%s": {\n'%self.name)
        #write        "color": [0, 250, 0],
        jsonfile.write('\t\t\t"color": %s,\n'%self.color)
        #write        "init": [58, 250, 0],
        jsonfile.write('\t\t\t"init": %s,\n'%self.init)
        #write        "home": [225, 194, 0],
        jsonfile.write('\t\t\t"home": %s,\n'%self.home)
        #write        "min": [-165, 0, 0],
        jsonfile.write('\t\t\t"min": %s,\n'%self.min)
        #write        "max": [165, 0, 0],
        jsonfile.write('\t\t\t"max": %s,\n'%self.max)
        #write        "movement": [1, 1, 0]
        jsonfile.write('\t\t\t"movement": %s\n'%self.movement)
        #write         },
        jsonfile.write('\t\t}%s\n'%('' if lastpart else ","))
