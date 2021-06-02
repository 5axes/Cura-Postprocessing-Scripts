#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessingPlugin
# Author:   5axes
# Date:     November 29 2020
#
# Description:  postprocessing-script to easily define a Retract Tower
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 29/11/2020
#   Version 1.1 29/01/2021
#   Version 1.2 19/02/2021  : First instruction output
#   Version 1.3 18/04/2021  : ChangeLayerOffset += 2
#   Version 1.4 01/06/2021  : Detect G91/G90 M82/M83 in G-Code
#                               https://github.com/5axes/Calibration-Shapes/issues/28
#   Version 1.5 02/06/2021  : Detect G92 E0 in G-Code
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search
from enum import Enum

__version__ = '1.5'

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
                        "distance": "Distance"
                    },
                    "default_value": "speed"
                },
                "startValue":
                {
                    "label": "Starting value",
                    "description": "the starting value of the Tower (speed/distance).",
                    "type": "float",
                    "default_value": 10
                },
                "valueChange":
                {
                    "label": "Value Increment",
                    "description": "the value change of each block, can be positive or negative (speed/distance).",
                    "type": "float",
                    "default_value": 10
                },
                "changelayer":
                {
                    "label": "Change Layer",
                    "description": "how many layers needs to be printed before the value should be changed.",
                    "type": "float",
                    "default_value": 38,
                    "minimum_value": 1
                },
                "changelayeroffset":
                {
                    "label": "Change Layer Offset",
                    "description": "if the Tower has a base, put the layer high off it here",
                    "type": "float",
                    "default_value": 5,
                    "minimum_value": 0
                },
                "lcdfeedback":
                {
                    "label": "Display details on LCD",
                    "description": "This setting will insert M117 gcode instructions, to display current modification in the G-Code is being used.",
                    "type": "bool",
                    "default_value": true
                }                 
            }
        }"""


## -----------------------------------------------------------------------------
#
#  Main Prog
#
## -----------------------------------------------------------------------------
    
    def execute(self, data):

        # Deprecation function
        # extrud = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        relative_extrusion = bool(extrud[0].getProperty("relative_extrusion", "value"))
         # Logger.log('d', 'Relative_extrusion : {}'.format(relative_extrusion))

        UseLcd = self.getSettingValueByKey("lcdfeedback")
        Instruction = self.getSettingValueByKey("command")
        StartValue = self.getSettingValueByKey("startValue")
        ValueChange = self.getSettingValueByKey("valueChange")
        ChangeLayer = self.getSettingValueByKey("changelayer")
        ChangeLayerOffset = self.getSettingValueByKey("changelayeroffset")
        ChangeLayerOffset += 2  # Modification to take into account the numbering offset in Gcode
                                # layer_index = 0 for initial Block 1= Start Gcode normaly first layer = 0 

        CurrentValue = -1
        save_e = -1
        Command=""

        # Logger.log('d', 'Change Layer Offset : {}'.format(ChangeLayerOffset))
        lcd_gcode = "M117 {:s} ({:.1f}/{:.1f})".format(Instruction,StartValue,ValueChange)
        
        if  (Instruction=='speed'):
            StartValue = StartValue*60
            ValueChange = ValueChange*60

        idl=0
        current_e = 0
        
        for layer in data:
            layer_index = data.index(layer)
            # Logger.log('d', 'layer_index : {}'.format(layer_index))
            
            lines = layer.split("\n")
            for line in lines:                  
                line_index = lines.index(line)
                
                if is_relative_instruction_line(line):
                    relative_extrusion = True
                if is_not_relative_instruction_line(line):
                    relative_extrusion = False
                if is_reset_extruder_line(line):
                    # Logger.log('d', 'Reset_extruder :' + str(current_e))
                    current_e = 0
                    
                # If we have define a value
                if CurrentValue>=0:
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
                            if relative_extrusion:
                                if current_e<0:
                                    # Logger.log('d', 'Mode retract')
                                    if  (Instruction=='speed'):
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(CurrentValue), current_e)
                                        lcd_gcode = "M117 speed F{:d}".format(int(CurrentValue))
                                    if  (Instruction=='distance'):
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(current_f), -CurrentValue)
                                        lcd_gcode = "M117 retract E{:.3}".format(float(CurrentValue))
                                else:
                                    # Logger.log('d', 'Mode reset')
                                    if  (Instruction=='speed'):
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(CurrentValue), current_e)
                                        lcd_gcode = "M117 speed F{:d}".format(int(CurrentValue))
                                    if  (Instruction=='distance'):
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(current_f), CurrentValue)
                                        lcd_gcode = "M117 retract E{:.3}".format(float(CurrentValue))                                        
                            else:
                                if save_e>current_e:
                                    # Logger.log('d', 'Mode retract')
                                    if  (Instruction=='speed'):
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(CurrentValue), current_e)
                                        lcd_gcode = "M117 speed F{:d}".format(int(CurrentValue))
                                    if  (Instruction=='distance'):
                                        current_e = save_e - CurrentValue
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(current_f), current_e)
                                        lcd_gcode = "M117 retract E{:.3}".format(float(CurrentValue))
                                else:
                                    # Logger.log('d', 'Mode reset')
                                    if  (Instruction=='speed'):
                                        lines[line_index] = "G1 F{:d} E{:.5f}".format(int(CurrentValue), current_e)
                                        lcd_gcode = "M117 speed F{:d}".format(int(CurrentValue))

                if is_extrusion_line(line):
                    searchE = re.search(r"E([-+]?\d*\.?\d*)", line)
                    if searchE:
                        save_e=float(searchE.group(1))             
                
                # Logger.log('d', 'L : {}'.format(line))
                if line.startswith(";LAYER:"):
                    # Initialize the change
                    if (layer_index==ChangeLayerOffset):
                        CurrentValue = StartValue
                        lcd_gcode = "M117 START {:s} ({:.1f}/{:.1f})".format(Instruction,StartValue,ValueChange)
                        # Logger.log('d', 'Start Layer Layer_index : {}'.format(layer_index))
                    # Change the current value   
                    if ((layer_index-ChangeLayerOffset) % ChangeLayer == 0) and ((layer_index-ChangeLayerOffset)>0):
                        CurrentValue += ValueChange
                    # Add M117 to add message on LCD
                    if UseLcd == True :
                        lines.insert(line_index + 1, lcd_gcode)
                                               
            result = "\n".join(lines)
            data[layer_index] = result

        return data
