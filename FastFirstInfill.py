#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     November 06, 2021
#
# Description:  postprocessing script to modifiy FastFirstInfill 
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 29/02/2020
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
    INNER_WALL = 2
    OUTER_WALL = 3
    INFILL = 4
    SKIN = 5
    SKIN2 = 6

def is_begin_layer_line(line: str) -> bool:
    """Check if current line is the start of a layer section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a layer section
    """
    return line.startswith(";LAYER:")

def is_retract_line(line: str) -> bool:
    """Check if current line is a retract segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a retract segment
    """
    return "G1" in line and "F" in line and "E" in line and not "X" in line and not "Y" in line and not "Z" in line
    
def is_extrusion_line(line: str) -> bool:
    """Check if current line is a standard printing segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G1" in line and "X" in line and "Y" in line and "E" in line

def is_not_extrusion_line(line: str) -> bool:
    """Check if current line is a rapid movement segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G0" in line and "X" in line and "Y" in line and not "E" in line

def is_relative_instruction_line(line: str) -> bool:
    """Check if current line contain a M83 / G91 instruction

    Args:
        line (str): Gcode line

    Returns:
        bool: True contain a M83 / G91 instruction
    """
    return "G91" in line or "M83" in line

def is_not_relative_instruction_line(line: str) -> bool:
    """Check if current line contain a M82 / G90 instruction

    Args:
        line (str): Gcode line

    Returns:
        bool: True contain a M82 / G90 instruction
    """
    return "G90" in line or "M82" in line

def is_reset_extruder_line(line: str) -> bool:
    """Check if current line contain a G92 E0

    Args:
        line (str): Gcode line

    Returns:
        bool: True contain a G92 E0 instruction
    """
    return "G92" in line and "E0" in line

class FastFirstInfill(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "FastFirstInfill",
            "key": "FastFirstInfill",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "infillspeed":
                {
                    "label": "Infill speed",
                    "description": "Infill speed value.",
                    "type": "float",
                    "unit": "mm/s",
                    "default_value": 30,
                    "minimum_value": 1,
                    "maximum_value": 100,
                    "maximum_value_warning": 30
                }              
            }
        }"""

    def execute(self, data):

        InfillSpeed = float(self.getSettingValueByKey("infillspeed")) * 60

        idl=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:                  
               
                if line.startswith(";LAYER:"):
                    line_index = lines.index(line)

                    Logger.log('d', 'layer_index : {%d}'.format(layer_index))
                    
                    if (layer_index==1):
                        idl=1
                    else :
                        idl=0
                
                if line.startswith(";TYPE") and idl >= 0:
                    if line.startswith(";TYPE:SKIN"):
                        idl=2
                    else :
                        idl=1
                
                if idl >= 2 and is_extrusion_line(line):
                    searchF = re.search(r"F([-+]?\d*\.?\d*)", line)
                    if searchF:
                        save_F=float(searchF.group(1))     
                        Logger.log('d', 'layer_index : {%save_F}'.format(save_F))
            
            result = "\n".join(lines)
            data[layer_index] = result

        return data
