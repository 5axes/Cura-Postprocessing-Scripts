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
#   Version 1.0 10/11/2021 first prototype
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search
from enum import Enum

__version__ = '1.0'

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

def is_begin_brim_line(line: str) -> bool:
    """Check if current line is the start of a brim section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a brim section
    """
    return line.startswith(";TYPE:BRIM")

def is_begin_type_line(line: str) -> bool:
    """Check if current line is the start of a type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a type section
    """
    return line.startswith(";TYPE")
    
def is_z_line(line: str) -> bool:
    """Check if current line is a Z line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a Z line segment
    """
    return "G0" in line and "Z" in line and not "E" in line
    
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
                    "description": "Number of Brim to Multiply",
                    "type": "int",
                    "default_value": 2,
                    "minimum_value": "1",
                    "maximum_value_warning": "3",
                    "maximum_value": "5"
                }                 
            }
        }"""

    def execute(self, data):

        BrimMultiply = int(self.getSettingValueByKey("multiply")) 

        idl=0
        
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
                    
                    if idl == 1 and is_begin_brim_line(line):
                        idl=2
                        startlayer=currentlayer
                        lines_brim.insert(1,line)
                        nb_line=2
                        # Logger.log("w", "Z Height %f", currentz)
                    
                    if idl == 2 and is_begin_type_line(line):
                        idl == 1
                        for aline in lines_brim:
                            Logger.log('d', 'brim_lines : {}'.format(aline))
                    else :
                        lines_brim.insert(nb_line,line)
                        nb_line+=1
                
                
                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
