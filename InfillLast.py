#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     March 13, 2023
#
# Description:  InfillLast
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 13/03/2023 first prototype right now must be use with the relative extrusion activated 
#                          Zhop Management must be include in this script
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
from UM.Message import Message
import re #To perform the search
from enum import Enum

from UM.i18n import i18nCatalog # Translation
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
    
def is_begin_skirt_line(line: str) -> bool:
    """Check if current line is the start of a SKIRT section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a SKIRT section
    """
    return line.startswith(";TYPE:SKIRT")

def is_begin_type_line(line: str) -> bool:
    """Check if current line is the start of a type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a type section
    """
    return line.startswith(";TYPE")

def is_begin_mesh_line(line: str) -> bool:
    """Check if current line is the start of a new MESH.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a new MESH
    """
    return line.startswith(";MESH:")

def is_e_line(line: str) -> bool:
    """Check if current line is a an Extruder line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is an Extruder line segment
    """
    return "G1" in line  and "E" in line

def is_relative_extrusion_line(line: str) -> bool:
    """Check if current line is a relative extrusion line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a relative extrusion line
    """
    return "M83" in line  

def is_absolute_extrusion_line(line: str) -> bool:
    """Check if current line is an absolute extrusion line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is an absolute  extrusion line
    """
    return "M82" in line  

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

def is_begin_skin_segment_line(line: str) -> bool:
    """Check if current line is the start of an skin.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of an skin section
    """
    return line.startswith(";TYPE:SKIN")
    
class InfillLast(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "InfillLast",
            "key": "InfillLast",
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

    def execute(self, data):
    
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
        relative_extrusion = bool(extrud[0].getProperty("relative_extrusion", "value"))
        
        
        
        if not relative_extrusion:
            Message("Must be in mode Relative extrusion", title = catalog.i18nc("@info:title", "Post Processing Skin Last")).show()
            return data

        extruder_id  = self.getSettingValueByKey("extruder_nb")
        extruder_id = extruder_id -1

        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count

        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        # Check if Z hop is desactivated
        retraction_hop_enabled= extrud[extruder_id].getProperty("retraction_hop_enabled", "value")  
        
        # Get the Cura retraction_hop and speed_z_hop as Zhop parameter
        retraction_hop = float(extrud[extruder_id].getProperty("retraction_hop", "value"))
        speed_z_hop = int(extrud[extruder_id].getProperty("speed_z_hop", "value"))
        speed_z_hop = speed_z_hop * 60
        speed_travel = extrud[0].getProperty("speed_travel", "value")
        speed_travel = speed_travel * 60 
       
        idl=0

        current_z = 0
        Zr = "Z0"
        Zc = "Z0"
        
        currentlayer=0
        CurrentE=0
        ResetE=0
        RelativeExtruder = False
        SaveE = -1
        In_G0 = False
        
        for layer in data:
            layer_index = data.index(layer)
            # Logger.log('d', "Layer_index founded : {}".format(layer_index))
            lines_skin = []
            lines_not_skin = []
            
            lines = layer.split("\n")

            for line_index, line in enumerate(lines):            

                if currentLine.startswith("G0") and "Z" in currentLine :
                    searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                    if searchZ:
                        current_z=float(searchZ.group(1))
                        Zc = "Z"+searchZ.group(1)
                        
                # Check if the line start with the Comment Char
                if is_relative_instruction_line(line) and line[0] != ";" :
                    relative_extrusion = True
                    # Logger.log('d', "Relative_extrusion founded : {}".format(line))
                
                # Check if the line start with the Comment Char                
                if is_not_relative_instruction_line(line) and line[0] != ";" :
                    relative_extrusion = False
                    
                if is_reset_extruder_line(line) and line[0] != ";" :
                    # Logger.log('d', "Reset_extruder :" + str(CurrentE))
                    CurrentE = 0
                    SaveE = 0
                    
                if is_relative_extrusion_line(line):
                    RelativeExtruder = True
                
                if is_absolute_extrusion_line(line):
                    RelativeExtruder = False
                    
                if line.startswith(";LAYER_COUNT:"):
                    # Logger.log("w", "found LAYER_COUNT %s", line[13:])
                    layercount=int(line[13:])                    
                                             
                # ;LAYER:X
                if is_begin_layer_line(line):  
                    Logger.log('d', "layer_lines : {}".format(line))
                    currentlayer=int(line[7:])
                    if currentlayer == 0 :
                        # Logger.log('d', "CurrentLayer : {}".format(currentlayer))
                        idl=2
                    else:
                        idl=0
 
                if is_begin_type_line(line) and idl > 0:
                    if is_begin_skin_segment_line(line):
                        idl=2
                        Logger.log('d', 'layer_lines : {}'.format(line))
                        if retraction_hop_enabled :
                            Logger.log('d', 'Output_Z : {}'.format(Output_Z))
                            Output_Z=current_z+retraction_hop
                            outPutLine = "G1 F{} Z{:.3f}\n".format(speed_z_hop,Output_Z)
                            lines_skin.append(outPutLine)
                            In_G0 = True                        
                        # Must integrate Zhop Management
                    else :
                        idl=1
                        
                #---------------------------------------
                # Add the Skin line to the Skin path 
                #---------------------------------------                
                if idl == 2 :
                    if line.startswith("G1") and In_G0 :
                            Output_Z=current_z+retraction_hop
                            Logger.log('d', 'Current_z : {}'.format(current_z))
                            outPutLine = "G0 F{} Z{:.3f}\n".format(speed_z_hop,Output_Z)
                            Zr = "Z{:.3f}".format(Output_Z)    
                            currentLine=line.replace(Zc, Zr)
                            outPutLine=currentLine.replace("G1", "G0")
                            lines_skin.append(outPutLine)
                            Output_Z=current_z
                            outPutLine = "G1 F{} Z{:.3f}\n".format(speed_z_hop,Output_Z)
                            lines_skin.append(outPutLine)
                            In_G0 = False
                            
                    lines_skin.append(line)
                
                if idl == 1 :
                    lines_not_skin.append(line)
            
            # Logger.log('d', "idl : {}".format(idl))
            if idl>0 :            
                result = ";BEGIN_OF_MODIFICATION"
                for line in lines_not_skin:
                    result += "\n"
                    result += line  
                    
                for line in lines_skin:
                    result += "\n"
                    result += line
                  
                result += ";END_OF_MODIFICATION\n"          
            else:
                result = "\n".join(lines)
            
            data[layer_index] = result

        return data
