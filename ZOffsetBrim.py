# ZOffsetBrim
"""
ZOffsetBrim for 3D prints.

Z Offset Brim

Author: 5axes
Version: 1.0

"""

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

        
        """Parse Gcode and modify infill portions with an extrusion width gradient."""
        currentSection = Section.NOTHING
        in_Z_offset = False


        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for currentLine in lines:
                line_index = lines.index(currentLine)

                if "Z" in currentLine and not in_Z_offset :
                        searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                        if searchZ:
                            current_z=float(searchZ.group(1))
                        # Logger.log('d', 'CurZ :' + str(current_z))
                if "Z" in currentLine and  in_Z_offset :
                        searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                        if searchZ:
                            save_Z=float(searchZ.group(1)) 
                            Output_Z=save_Z+v_offset
                            instructionZ="Z"+str(searchZ.group(1))
                            Logger.log('d', 'save_Z       : {:f}'.format(save_F))
                            Logger.log('d', 'line : {}'.format(currentLine))
                            Logger.log('d', 'line replace : {}'.format(currentLine.replace(instructionF,instructionZ)))
                            lines[line_index]=currentLine.replace(instructionZ,instructionZ)

                        
                if is_begin_skirt_segment_line(currentLine) and not (currentSection == Section.SKIRT):
                    currentSection = Section.SKIRT
                    if not in_Z_offset:
                        in_Z_offset = True
                        Output_Z=current_z+v_offset
                        outPutLine = "G1 Z{}\n".format(Output_Z)
                        outPutLine = outPutLine + currentLine
                        lines[line_index] = outPutLine                    
                    continue

                if is_begin_segment_line(currentLine) and currentSection == Section.SKIRT:
                    if in_Z_offset:
                        outPutLine = currentLine + "\nG1 Z{}".format(current_z)
                        lines[line_index] = outPutLine
                    currentSection = Section.NOTHING
                    continue
                                     

                if currentSection == Section.SKIRT:
                    if is_not_extrusion_line(currentLine):
                        if not in_Z_offset:
                            in_Z_offset = True
                            Output_Z=current_z+v_offset
                            outPutLine = "G1 Z{}\n".format(Output_Z)
                            outPutLine = outPutLine + currentLine
                            lines[line_index] = outPutLine
                    else:
                        if in_Z_offset:
                            in_Z_offset = False
                            outPutLine = currentLine + "\nG1 Z{}".format(current_z)
                            lines[line_index] = outPutLine

                #
                # end of analyse
                #

            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
        return data
