# ZMoveIroning
"""
ZMoveIroning for 3D prints.

Z hop for ironing

Author: 5axes
Version: 1.0
Version: 1.1  Remove some useless part of the Code.

"""

import re #To perform the search
from enum import Enum
from ..Script import Script

from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message
from UM.i18n import i18nCatalog

catalog = i18nCatalog("cura")

__version__ = '1.1'

class Section(Enum):
    """Enum for section type."""

    NOTHING = 0
    SKIRT = 1
    INNER_WALL = 2
    OUTER_WALL = 3
    INFILL = 4
    SKIN = 5
    SKIN2 = 6


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

        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        retraction_hop = float(extrud[extruder_id].getProperty("retraction_hop", "value"))
        speed_z_hop = int(extrud[extruder_id].getProperty("speed_z_hop", "value"))
        speed_z_hop = speed_z_hop * 60

        ironingenabled = extrud[extruder_id].getProperty("ironing_enabled", "value")
        if ironingenabled == False:
            #
            Logger.log('d', 'Gcode must be generate with ironing mode')
            Message(catalog.i18nc("@message","Gcode must be generate with ironing mode"), title = catalog.i18nc("@info:title", "Post Processing")).show()
            return None

        retraction_hop_enabled= extrud[extruder_id].getProperty("retraction_hop_enabled", "value")
        if retraction_hop_enabled == True:
            #
            Logger.log('d', 'Mode Z Hop must not be activated')
            Message(catalog.i18nc("@message","Mode Z Hop must not be activated"), title = catalog.i18nc("@info:title", "Post Processing")).show()
            return None
        
        """Parse Gcode and modify infill portions with an extrusion width gradient."""
        currentSection = Section.NOTHING
        in_z_hop = False


        for layer_index, layer in enumerate(data):
            lines = layer.split("\n")
            for line_index, currentLine in enumerate(lines):

                if currentLine.startswith("G0") and "Z" in currentLine :
                        searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                        if searchZ:
                            current_z=float(searchZ.group(1))
                        
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
                            outPutLine = "G1 F{} Z{:.3f}\n".format(speed_z_hop,Output_Z)
                            outPutLine = outPutLine + currentLine
                            lines[line_index] = outPutLine
                    else:
                        if in_z_hop:
                            in_z_hop = False
                            outPutLine = currentLine + "\nG1 F{} Z{:.3f}".format(speed_z_hop,current_z)
                            lines[line_index] = outPutLine
 
                    #
                    # comment like ;MESH:NONMESH 
                    #
                    if currentLine.startswith(";") :
                        currentSection = Section.NOTHING
                #
                # end of analyse
                #

            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
        return data
