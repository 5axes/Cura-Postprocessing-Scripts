#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     November 07, 2021
#
# Description:  postprocessing script to slowdown the speed according to the Z height
#               https://marlinfw.org/docs/gcode/M220.html
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 07/11/2021 Add slow down using M220 S(SlowDown%)
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
  
def is_z_line(line: str) -> bool:
    """Check if current line is a Z line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a Z line segment
    """
    return "G0" in line and "Z" in line and not "E" in line
    
class SlowZ(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "SlowZ",
            "key": "SlowZ",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "slowz_percentage":
                {
                    "label": "Slow Z percentage",
                    "description": "Positive value to slow the print as the z value rises up to this percentage.",
                    "type": "float",
                    "unit": "%",
                    "default_value": 0,
                    "minimum_value": "0",
                    "maximum_value_warning": "50",
                    "maximum_value": "90"
                },        
                "slowz_height":
                {
                    "label": "Slow Z height",
                    "description": "Positive value to define the start height of the speed reduction.",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 0,
                    "minimum_value": "0"
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

    def execute(self, data):

        SlowZPercentage = float(self.getSettingValueByKey("slowz_percentage")) 
        SlowZHeight = float(self.getSettingValueByKey("slowz_height"))
        UseLcd = self.getSettingValueByKey("lcdfeedback")
        # Logger.log('d', 'SlowZPercentage : {:f}'.format(SlowZPercentage))
        # Logger.log('d', 'SlowZHeight     : {:f}'.format(SlowZHeight))

        idl=0
        currentz=0
        
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
                        currentz=0
                        idl=1
                    
                    if idl == 1 and currentz >= SlowZHeight:
                        idl=2
                        startlayer=currentlayer
                        # Logger.log("w", "Z Height %f", currentz)
                    
                    #Logger.log("w", "LAYER %s", line[7:])
                    if idl >= 2 :
                        speed_value = 100 - int(float(SlowZPercentage)*((currentlayer-startlayer)/(layercount-startlayer)))
                        lines.insert(2,"M220 S" + str(speed_value))
                        if UseLcd == True :
                            lcd_gcode = "M117 Speed {:d}%".format(int(speed_value))
                            lines.insert(3,lcd_gcode)
                
                
                if idl == 1 and is_z_line(line):
                    searchZ = re.search(r"Z(\d*\.?\d*)", line)
                    if searchZ:
                        currentz=float(searchZ.group(1))
                        # Logger.log('d', 'Current Z     : {:f}'.format(currentz))
                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
