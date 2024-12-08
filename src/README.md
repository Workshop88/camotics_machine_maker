# Camotics Machine Maker
A Python script to create a **Camotics** CNC Simulator machines from X3D .xhtml files.
## Usage
`python camotics_machine_maker.py filespec.xhtml`

This will parse `filespec.xhtml` then generate `filespec.json`, and `filespec.tco` in the same location as `filespec.xhtml`.  The script will silently overwrite preexisting files.

**Note:** `filespec.json` will require additional manual editing to tell **Camotics** which components move with X, Y, and Z movement of the tool in the simulated gcode.  See [/example/data/Camotics](/example/data/Camotics/README.md) for detailed instructions.

### Example commandline
`python src\camotics_machine_maker.py "example\data\Wooden CNC.xhtml"`

This will run the included script on the included example data to recreate the `.json` and `.tco` files in the `example\data folder`.  This can be used to validate the script works on your machine and generates output that agrees with the files in source control.