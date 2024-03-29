# ZOffsetBrim
"""
ZOffsetBrim for 3D prints.

Z Offset just on Brim / Skirt

Author: 5axes
Version: 1.0

"""

from ..Script import Script
from UM.Logger import Logger
import re #To perform the search
from enum import Enum
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


def is_extrusion_line(line: str) -> bool:
    """Check if current line is a standard printing segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G1" in line and "X" in line and "Y" in line and "E" in line

def is_not_extrusion_line(line: str) -> bool:
    """Check if current line is a rapid movement with a Z component segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G0" in line and "Z" in line and not "E" in line

def is_retract_line(line: str) -> bool:
    """Check if current line is a speed movement with a Z component segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G1" in line and "Z" in line and not "E" in line

def is_begin_skirt_segment_line(line: str) -> bool:
    """Check if current line is the start of an skirt.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of an skirt section
    """
    return line.startswith(";TYPE:SKIRT")

def is_begin_segment_line(line: str) -> bool:
    """Check if current line is the start of a new Type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a new Type section
    """
    return line.startswith(";TYPE:")

    
class ZOffsetBrim(Script):
    def getSettingDataString(self):
        return """{
            "name": "Z Offset Brim",
            "key": "ZOffsetBrim",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "offset":
                {
                    "label": "Offset Value",
                    "description": "Define the Offset Value to  the brim",
                    "unit": "mm",
                    "type": "float",
                    "default_value": -0.03
                }
            }
        }"""


## -----------------------------------------------------------------------------
#
#  Main Prog
#
## -----------------------------------------------------------------------------

    def execute(self, data):

        v_offset  = self.getSettingValueByKey("offset")
        
        currentSection = Section.NOTHING
        in_Z_offset = False
        current_z = 0
        current_Layer = 0

        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            line_index = -1

            for currentLine in lines:
                #line_index = lines.index(currentLine)
                line_index += 1
                
                if is_begin_layer_line(currentLine) :
                    current_Layer = int(currentLine.split(":")[1])
                    current_Layer += 1
                    continue
                
                if current_Layer == 1 :                        
                    if is_not_extrusion_line(currentLine) or is_retract_line(currentLine) :
                        # Logger.log('d', 'currentLine with Z : {}'.format(currentLine))
                        # Logger.log('d', 'line_index : {}'.format(line_index))
                        searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                        if searchZ :
                            if not in_Z_offset :
                                current_z=float(searchZ.group(1))                            
                            else :
                                save_Z=float(searchZ.group(1)) 
                                Output_Z=save_Z+v_offset
                                instructionZ="Z"+str(searchZ.group(1))
                                outPutZ = "Z{:.3f}".format(Output_Z)
                                # Logger.log('d', 'save_Z       : {:.3f}'.format(save_Z))
                                # Logger.log('d', 'line : {}'.format(currentLine))
                                # Logger.log('d', 'line replace : {}'.format(currentLine.replace(instructionZ,outPutZ)))
                                lines[line_index]=currentLine.replace(instructionZ,outPutZ)
                
                if is_begin_segment_line(currentLine) and currentSection == Section.SKIRT:
                    if in_Z_offset:
                        cLine = lines[line_index+1]
                        # Logger.log('d', 'cLine : {}'.format(cLine))
                        searchZ = re.search(r"Z(\d*\.?\d*)", cLine)
                        if not searchZ :
                            lines.insert(line_index + 1, "G0 Z{:.3f}".format(current_z))
                        in_Z_offset = False
                    currentSection = Section.NOTHING
                    continue
                        
                if is_begin_skirt_segment_line(currentLine) and currentSection != Section.SKIRT :
                    currentSection = Section.SKIRT
                    if not in_Z_offset:
                        # cas avec Z Hop
                        cLine = lines[line_index+1]
                        searchZ = re.search(r"Z(\d*\.?\d*)", cLine)
                        if searchZ :
                            current_z=float(searchZ.group(1))                         
                        else :
                            Output_Z=current_z+v_offset
                            lines.insert(line_index + 1, "G0 Z{:.3f}".format(Output_Z))                            
                        in_Z_offset = True
                #
                # end of analyse
                #

            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
        return data
