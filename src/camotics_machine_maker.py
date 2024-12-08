#!/usr/bin/python3
'''
    camotics-machine-maker.py
    By D. Scott Williamson November 2024

    I hacked this together to import a Workshop 88 makerspace CNC machine built 
    in FreeCAD as an assembly, exported as X3D .xhtml into Camotics' awesome CNC simulator.
    
    https://blog.workshop88.com/
    https://camotics.org/
     
    This program comes with no guarantee it will work, nor warranty that it
    won't do something dumb.  Use it at your own risk.
    
    Usage:
    python3 camotics-machine-maker.py infilespec
    
    This program will read the input file and create a .tco and .json file for 
    a Camotics machine model.
    
    Supported input formats:
        xhtml
    
    I didn't feel like writing a convex edge detector to extract meaningful edges from 
    the triangle soup .STL is.  In the end I think that would have been easier and more
    robust than parsing .xhtml.  :-/
    
    This script has been written to accommodate additional file formats, so if you want to 
    write a reader that parses a file and populates a Machine, it should export.  All fields
    in Machine have default values and an uninitialized machine will export a couple colored
    triangles.
    
    When Camotics releases the next version, I think .tco will go away and the Machine.write()
    will need to be updated to export entirely into .json.
'''
import sys
from machine import Machine            
from machine import Part            
from xhtml_reader import xhtml_read 

def showhelp():
    print("camotics-machine-maker.py")
    print("By D. Scott Williamson November 2024")
    print("")
    print("Usage:")
    print("\tpython3 camotics-machine-maker.py infilespec")
    print("")
    print("This program will read the input file and create a .tco and .json file for") 
    print("a Camotics machine model.")
    print("")
    print("Supported input formats:")
    print("\txhtml")

progname=None
infilespec=None

# parse parameters
for arg in sys.argv:
    argl=arg.lower()
    
    if argl[0:2]=='-h':
        showhelp()
        exit(0)
    else:
        if progname==None:
            progname=arg
        elif infilespec==None:
            infilespec=arg
        else:
            # too many arguments
            print("ERROR: Unknown parameter:",arg)
            showhelp()
            exit(1)        

# validate inputs        
if infilespec==None:
    print("ERROR:No input file specified")
    showhelp()
    exit(1)        

print("Input file:%s"%infilespec)

# Parse input file to create a Machine
machine=xhtml_read(infilespec)

# strip ".xhtml" to create a filespec that does not include an extension
extindex=infilespec.lower().rfind(".xhtml")
if extindex>0:
    filebase=infilespec[:extindex]
else:
    filebase=infilespec

# Write the Camotics .json and .tco files for the Machine 
machine.write(filebase)

print("Completed Successfully.")
