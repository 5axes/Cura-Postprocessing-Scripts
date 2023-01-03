# FlowIroning
"""
FlowIroning for 3D prints.

Set Flow value for ironing

Author  : 5axes
Version : 1.0
Date    : 3/01/2023

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

        
class FlowIroning(Script):
    def getSettingDataString(self):
        return """{
            "name": "Flow Ironing",
            "key": "FlowIroning",
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
                },
                "fan_value":
                {
                    "label": "Fan Value",
                    "description": "Fan value during ironing operation.",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 100
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

        ironing_fan_value  = int(self.getSettingValueByKey("fan_value"))*255

        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count

        # Deprecation function
        # extrud = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
   
        ironingenabled = extrud[extruder_id].getProperty("ironing_enabled", "value")
        if ironingenabled == False:
            #
            Logger.log('d', 'Gcode must be generate with ironing mode')
            Message('Gcode must be generate with ironing mode', title = catalog.i18nc("@info:title", "Post Processing")).show()
            return None
        
        """Parse Gcode and modify infill portions with an extrusion width gradient."""
        currentSection = Section.NOTHING
        set_ironing_fan_value = False
        current_flow = 0


        for layer_index, layer in enumerate(data):
            lines = layer.split("\n")
            for line_index, currentLine in enumerate(lines):

                if "M106" in currentLine and not set_ironing_fan_value :
                        searchM106 = re.search(r"S(\d*\.?\d*)", currentLine)
                        if searchM106:
                            current_flow=int(searchM106.group(1))
                            Logger.log('d', 'current_flow :' + str(current_flow))
 
                if is_begin_skin_segment_line(currentLine) and not (currentSection == Section.SKIN):
                    currentSection = Section.SKIN                 
                    continue
                    
                # SKIN After SKIN = Ironing operation
                if currentSection == Section.SKIN:
                    if is_begin_skin_segment_line(currentLine):
                        currentSection = Section.SKIN2
                        set_ironing_fan_value = True
                        outPutLine = "\nM106 S{:d}".format(ironing_fan_value)
                        # Logger.log('d', 'outPutLine :' + str(outPutLine))
                        outPutLine = currentLine + outPutLine 
                        lines[line_index] = outPutLine
                    elif ";TYPE:" in currentLine:
                        currentSection = Section.NOTHING                  
                        if set_ironing_fan_value :
                            set_ironing_fan_value = False
                            outPutLine = "\nM106 S{:d}".format(current_flow)
                            # Logger.log('d', 'Reset A outPutLine :' + str(outPutLine))
                            outPutLine = currentLine + outPutLine 
                            lines[line_index] = outPutLine
                    
                #
                # comment like ;MESH:NONMESH 
                #
                if ";MESH:" in currentLine:
                    currentSection = Section.NOTHING
                    if set_ironing_fan_value :
                        set_ironing_fan_value = False
                        outPutLine = "\nM106 S{:d}".format(current_flow)
                        # Logger.log('d', 'Reset B outPutLine :' + str(outPutLine))
                        outPutLine = currentLine + outPutLine 
                        lines[line_index] = outPutLine                       
                        
                #
                # end of analyse
                #

            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
        return data
