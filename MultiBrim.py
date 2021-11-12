#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     November 10, 2021
#
# Description:  MultiBrim
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 10/11/2021 first prototype right now must be use with the relative extrusion activated and no Zhop
#   Version 1.1 11/11/2021 first prototype tested on Ender3
#   Version 1.2 12/11/2021 Adding Speed value for the subsequent brim print
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search
from enum import Enum
from collections import namedtuple
from typing import List, Tuple

__version__ = '1.2'

Point2D = namedtuple('Point2D', 'x y')

class Section(Enum):
    """Enum for section type."""

    NOTHING = 0
    SKIRT = 1
    BRIM = 2
    INNER_WALL = 3
    OUTER_WALL = 4
    INFILL = 5
    SKIN = 6
    SKIN2 = 7

def is_begin_layer_line(line: str) -> bool:
    """Check if current line is the start of a layer section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a layer section
    """
    return line.startswith(";LAYER:")

def is_begin_skirt_line(line: str) -> bool:
    """Check if current line is the start of a SKIRT section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a SKIRT section
    """
    return line.startswith(";TYPE:SKIRT")

def is_begin_type_line(line: str) -> bool:
    """Check if current line is the start of a type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a type section
    """
    return line.startswith(";TYPE")

def is_begin_mesh_line(line: str) -> bool:
    """Check if current line is the start of a new MESH.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a new MESH
    """
    return line.startswith(";MESH:")

    
def is_z_line(line: str) -> bool:
    """Check if current line is a Z line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a Z line segment
    """
    return "G0" in line and "Z" in line and not "E" in line

def is_e_line(line: str) -> bool:
    """Check if current line is a an Extruder line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is an Extruder line segment
    """
    return "G1" in line  and "E" in line
    
    
def is_only_extrusion_line(line: str) -> bool:
    """Check if current line is a pure extrusion command.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a pure extrusion command
    """
    return "G1" in line and not "X" in line and not "Y" in line and "E" in line
    
def getXY(currentLine: str) -> Point2D:
    """Create a ``Point2D`` object from a gcode line.

    Args:
        currentLine (str): gcode line

    Raises:
        SyntaxError: when the regular expressions cannot find the relevant coordinates in the gcode

    Returns:
        Point2D: the parsed coordinates
    """
    searchX = re.search(r"X(\d*\.?\d*)", currentLine)
    searchY = re.search(r"Y(\d*\.?\d*)", currentLine)
    if searchX and searchY:
        elementX = searchX.group(1)
        elementY = searchY.group(1)
    else:
        raise SyntaxError('Gcode file parsing error for line {currentLine}')

    return Point2D(float(elementX), float(elementY))
    
class MultiBrim(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "MultiBrim",
            "key": "MultiBrim",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "multiply":
                {
                    "label": "Brim multiply",
                    "description": "Number of brim to multiply",
                    "type": "int",
                    "default_value": 2,
                    "minimum_value": "1",
                    "maximum_value_warning": "3",
                    "maximum_value": "5"
                },
                "speed":
                {
                    "label": "Brim speed",
                    "description": "Speed for the subsequent brim",
                    "type": "float",
                    "unit": "mm/s",
                    "default_value": 30,
                    "minimum_value": "0",
                    "maximum_value_warning": "50",
                    "maximum_value": "100"
                }                
            }
        }"""

    def execute(self, data):

        BrimMultiply = int(self.getSettingValueByKey("multiply")) 
        BrimSpeed = int(self.getSettingValueByKey("speed"))*60
        BrimReplaceSpeeed = "F" + str(BrimSpeed)        

        idl=0
        lines_brim =[]
        startline=''
        BrimF='F0'
        FirstZ=''
        StartZ=0
        BrimZ=0
        xyline=''
        nb_line=0
        currentlayer=0
        lastE='G92 E0'
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:                  
               
                if line.startswith(";LAYER_COUNT:"):
                    # Logger.log("w", "found LAYER_COUNT %s", line[13:])
                    layercount=int(line[13:])                    
               
                if is_begin_layer_line(line):
                    line_index = lines.index(line)    
                    # Logger.log('d', 'layer_lines : {}'.format(line))
                    currentlayer=int(line[7:])
                    # Logger.log('d', 'currentlayer : {:d}'.format(currentlayer))
                    if line.startswith(";LAYER:0"):
                        idl=1
                    
                    # Copy the Original Brim
                    elif currentlayer <= BrimMultiply :
                        # Logger.log('d', 'Insert Here : {:d}'.format(currentlayer))
                        # Logger.log('d', 'First   Z   : {}'.format(FirstZ))
                        line_index = lines.index(line)
                        xyline=lines[line_index-3]
                        
                        #----------------------------
                        #    Begin of modification
                        #----------------------------
                        lines.insert(line_index + 1, ";BEGIN_OF_MODIFICATION")
                        # Logger.log('d', 'xyline   : {}'.format(xyline))
                        # Reset the Extruder position
                        lines.insert(line_index + 2, "G92 E0")
                        BrimZ+=StartZ
                        ModiZ="Z"+str(BrimZ)
                        BeginLine=startline.replace(FirstZ, ModiZ)
                        lines.insert(line_index + 3, BeginLine)
                        nb_line=3
                        for aline in lines_brim:
                            nb_line+=1
                            searchZ = re.search(r"Z(\d*\.?\d*)", aline)
                            if searchZ:
                                cz="Z"+searchZ.group(1)
                                ModiZ="Z"+str(currentz)
                                # Logger.log('d', 'Current Z   : {}'.format(cz))
                                # Logger.log('d', 'Modi    Z   : {}'.format(ModiZ))
                                InsertLine=aline.replace(cz, ModiZ)
                            else:
                                InsertLine=aline
                            lines.insert(line_index + nb_line, InsertLine)
                        nb_line+=1
                        lines.insert(line_index + nb_line, xyline)
                        
                        nb_line+=1
                        lines.insert(line_index + nb_line, lastE)
                        
                        #----------------------------
                        #    End of modification
                        #----------------------------
                        nb_line+=1
                        lines.insert(line_index + nb_line, ";END_OF_MODIFICATION")
     
                if idl == 2 and is_begin_type_line(line):
                    idl = 0
                    
                if idl == 2 and is_begin_mesh_line(line) :
                    idl = 0
                
                #---------------------------------------
                # Add the Brim line to the brim path 
                #---------------------------------------                
                if idl == 2 :
                    # if not is_only_extrusion_line(line):
                    if BrimSpeed >0 :
                            cline = line.replace(BrimF,BrimReplaceSpeeed)
                    else :
                            cline = line
                    lines_brim.append(cline)
                
                #---------------------------------------
                # Init copy of the BRIM extruding path
                #---------------------------------------
                if idl == 1 and is_begin_skirt_line(line):
                    idl=2
                    line_index = lines.index(line)-1
                    startline=lines[line_index]
                    searchZ = re.search(r"Z(\d*\.?\d*)", startline)
                    if searchZ:
                        StartZ=float(searchZ.group(1))
                        FirstZ="Z"+searchZ.group(1)
                    
                    speedline=lines[line_index+3]
                    Logger.log('d', 'speedline   : {}'.format(speedline))
                    searchF = re.search(r"F(\d*\.?\d*)", speedline)
                    if searchF:
                        BrimF="F"+searchF.group(1)                    
                        Logger.log('d', 'BrimF     : {}'.format(BrimF))
                        
                    lines_brim =[]
                    startlayer=currentlayer
                    lines_brim.append(line)
                     
                
                if currentlayer <= BrimMultiply and is_z_line(line):
                    searchZ = re.search(r"Z(\d*\.?\d*)", line)
                    if searchZ:
                        currentz=float(searchZ.group(1))

                if currentlayer <= BrimMultiply and is_e_line(line):
                    searchE = re.search(r"E([-+]?\d*\.?\d*)", line)
                    if searchE:
                        lastE="G92 E"+searchE.group(1)

                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
