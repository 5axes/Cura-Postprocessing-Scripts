# Cura PostProcessingPlugin
# Author:   5axes
# Date:     November 29 2020
#
# Description:  postprocessing-script to easily define a Speed Tower
#
#
#   Version 1.0 29/11/2020
#

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search
from cura.Settings.ExtruderManager import ExtruderManager
from collections import namedtuple
from enum import Enum
from typing import List, Tuple
from UM.Message import Message
from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

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

def is_begin_skin_segment_line(line: str) -> bool:
    """Check if current line is the start of an skin.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of an skin section
    """
    return line.startswith(";TYPE:SKIN")
    
    
class RetractTower(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "RetractTower",
            "key": "RetractTower",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "command": {
                    "label": "Command",
                    "description": "GCode Commande",
                    "type": "enum",
                    "options": {
                        "speed": "Speed",
                        "retract": "Retract"
                    },
                    "default_value": "speed"
                },
                "startValue":
                {
                    "label": "Starting value",
                    "description": "the starting value of the Tower.",
                    "type": "int",
                    "default_value": 8
                },
                "valueChange":
                {
                    "label": "Value Increment",
                    "description": "the value change of each block, can be positive or negative.",
                    "type": "int",
                    "default_value": 4
                },
                "changelayer":
                {
                    "label": "Change Layer",
                    "description": "how many layers needs to be printed before the value should be changed.",
                    "type": "float",
                    "default_value": 43,
                    "minimum_value": 1
                },
                "changelayeroffset":
                {
                    "label": "Change Layer Offset",
                    "description": "if the Tower has a base, put the layer high off it here",
                    "type": "float",
                    "default_value": 3,
                    "minimum_value": 0
                }
            }
        }"""


## -----------------------------------------------------------------------------
#
#  Main Prog
#
## -----------------------------------------------------------------------------
    
    def execute(self, data):

        Instruction = self.getSettingValueByKey("command")
        StartValue = self.getSettingValueByKey("startValue")
        ValueChange = self.getSettingValueByKey("valueChange")
        ChangeLayer = self.getSettingValueByKey("changelayer")
        ChangeLayerOffset = self.getSettingValueByKey("changelayeroffset")
        ChangeLayerOffset += 1  # Modif pour tenir compte du décalage de numérotation dans Gcode

        CurrentValue = 0
        save_e = 0
        Command=""
 
        if  (Instruction=='speed'):
            StartValue = StartValue*60
            ValueChange = ValueChange*60
                                
        # Logger.log('d', 'Instruction : {}'.format(Instruction))

        idl=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:                  
                line_index = lines.index(line)
                
                # If we have define a value
                if CurrentValue>0:
                    if is_retract_line(line):
                        # Logger.log('d', 'Retract_line : {}'.format(line))
                        searchF = re.search(r"F(\d*)", line)
                        if searchF:
                            current_f=float(searchF.group(1))
                            # Logger.log('d', 'CurF :' + str(current_f))
                            
                        searchE = re.search(r"E([-+]?\d*\.?\d*)", line)
                        if searchE:
                            current_e=float(searchE.group(1))
                            # Logger.log('d', 'CurE :' + str(current_e))
                            if save_e>current_e:
                                # Logger.log('d', 'Mode retract')
                                if  (Instruction=='speed'):
                                    lines[line_index] = "G1 F{:d} E{:f}".format(int(CurrentValue), current_e)
                                if  (Instruction=='retract'):
                                    current_e = save_e - CurrentValue
                                    lines[line_index] = "G1 F{:d} E{:f}".format(int(current_f), current_e)                          
                            else:
                                # Logger.log('d', 'Mode reset')
                                if  (Instruction=='speed'):
                                    lines[line_index] = "G1 F{:d} E{:f}".format(int(CurrentValue), current_e)  

                if is_extrusion_line(line):
                    searchE = re.search(r"E([-+]?\d*\.?\d*)", line)
                    if searchE:
                        save_e=float(searchE.group(1))             
                                             
                if line.startswith(";LAYER:"):
                    # 
                    if (layer_index==ChangeLayerOffset):
                        CurrentValue = StartValue

                    if ((layer_index-ChangeLayerOffset) % ChangeLayer == 0) and ((layer_index-ChangeLayerOffset)>0):
                        CurrentValue += ValueChange
                                               
            
            result = "\n".join(lines)
            data[layer_index] = result

        return data
