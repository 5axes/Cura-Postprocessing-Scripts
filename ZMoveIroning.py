# ZMoveIroning
"""
ZMoveIroning for 3D prints.

Z hop for ironing

Author: Laurent LALLIARD
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

        
class ZMoveIroning(Script):
    def getSettingDataString(self):
        return """{
            "name": "Z Move Ironing",
            "key": "ZMoveIroning",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "extruder_nb":
                {
                    "label": "Extruder Id",
                    "description": "Define extruder Id in case of multi extruders",
                    "unit": "",
                    "type": "int",
                    "default_value": 1
                }
            }
        }"""


## -----------------------------------------------------------------------------
#
#  Main Prog
#
## -----------------------------------------------------------------------------

    def execute(self, data):

        extruder_id  = self.getSettingValueByKey("extruder_nb")
        extruder_id = extruder_id -1

        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count

        # Deprecation function
        # extrud = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        retraction_hop = float(extrud[extruder_id].getProperty("retraction_hop", "value"))
        speed_z_hop = int(extrud[extruder_id].getProperty("speed_z_hop", "value"))
        speed_z_hop = speed_z_hop * 60

        relativeextrusion = extrud[extruder_id].getProperty("relative_extrusion", "value")
        ironingenabled = extrud[extruder_id].getProperty("ironing_enabled", "value")
        if ironingenabled == False:
            #
            Logger.log('d', 'Gcode must be generate with ironing mode')
            Message('Gcode must be generate with ironing mode', title = catalog.i18nc("@info:title", "Post Processing")).show()
            return None

        retraction_hop_enabled= extrud[extruder_id].getProperty("retraction_hop_enabled", "value")
        if retraction_hop_enabled == True:
            #
            Logger.log('d', 'Mode Z Hop mustnt be activated')
            Message('Mode Z Hop mustn"t be activated', title = catalog.i18nc("@info:title", "Post Processing")).show()
            return None
        
        """Parse Gcode and modify infill portions with an extrusion width gradient."""
        currentSection = Section.NOTHING
        in_z_hop = False


        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for currentLine in lines:
                line_index = lines.index(currentLine)

                if "Z" in currentLine and "G0" in currentLine:
                        searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                        if searchZ:
                            current_z=float(searchZ.group(1))
                        # Logger.log('d', 'CurZ :' + str(current_z))
                        
                if is_begin_skin_segment_line(currentLine) and not (currentSection == Section.SKIN):
                    currentSection = Section.SKIN
                    continue

                # SKIN After SKIN = Ironing operation
                if currentSection == Section.SKIN:
                    if is_begin_skin_segment_line(currentLine):
                        currentSection = Section.SKIN2
                        continue
                    elif ";" in currentLine:
                        currentSection = Section.NOTHING                  

                if currentSection == Section.SKIN2:
                    if is_not_extrusion_line(currentLine):

                        if not in_z_hop:
                            in_z_hop = True
                            Output_Z=current_z+retraction_hop
                            outPutLine = "G1 F{} Z{}\n".format(speed_z_hop,Output_Z)
                            outPutLine = outPutLine + currentLine
                            lines[line_index] = outPutLine
                    else:
                        if in_z_hop:
                            in_z_hop = False
                            outPutLine = currentLine + "\nG1 F{} Z{}".format(speed_z_hop,current_z)
                            lines[line_index] = outPutLine
 
                    #
                    # comment like ;MESH:NONMESH 
                    #
                    if ";" in currentLine:
                        currentSection = Section.NOTHING
                #
                # end of analyse
                #

            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
        return data
