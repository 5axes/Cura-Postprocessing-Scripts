#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     March 13, 2023
#
# Description:  SpoonOrder
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 13/03/2023 first prototype right now must be use with the relative extrusion activated 
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
from UM.Message import Message
import re #To perform the search
from UM.i18n import i18nCatalog # Translation
catalog = i18nCatalog("cura")

__version__ = '1.0'

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

    
class SpoonOrder(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "SpoonOrder",
            "key": "SpoonOrder",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "layer":
                {
                    "label": "Layer Analyse",
                    "description": "Number of layer to analyse",
                    "type": "int",
                    "default_value": 1,
                    "minimum_value": 0
                },
                "marker":
                {
                    "label": "Spoon Identificator",
                    "description": "Spoon Tab identificator",
                    "type": "str",
                    "default_value": "SpoonTab"
                }               
            }
        }"""

    def execute(self, data):

        LayerAnalyse = int(self.getSettingValueByKey("layer"))      
        LayerAnalyse -= 1
        Logger.log('d', "LayerAnalyse : {}".format(LayerAnalyse))
        Marker = str(self.getSettingValueByKey("marker"))           
        
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
        relative_extrusion = bool(extrud[0].getProperty("relative_extrusion", "value"))
        
        if not relative_extrusion:
            Message("Must be in mode Relative extrusion", title = catalog.i18nc("@info:title", "Post Processing Spoon Order")).show()
            return data
            
        idl=0

        currentlayer=0
        CurrentE=0
        ResetE=0
        RelativeExtruder = False
        SaveE = -1
        
        for layer in data:
            layer_index = data.index(layer)
            # Logger.log('d', "Layer_index founded : {}".format(layer_index))
            lines_spoon = []
            lines_not_spoon = []
            
            lines = layer.split("\n")
            for line in lines:                  
                # line_index = lines.index(line)
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

                if idl >= 1 and line.startswith(";TIME_ELAPSED:"):
                    idl = 1
                                             
                # ;LAYER:X
                if is_begin_layer_line(line):  
                    Logger.log('d', "layer_lines : {}".format(line))
                    currentlayer=int(line[7:])
                    if currentlayer <= LayerAnalyse :
                        # Logger.log('d', "CurrentLayer : {} / {}".format(currentlayer,LayerAnalyse))
                        idl=2
                    else:
                        idl=0
                        
                if idl >= 1 and is_begin_mesh_line(line) :               
                    if Marker in line :
                        # Logger.log('d', "Marker mesh : {}".format(line))
                        idl = 2
                    else:
                        # Logger.log('d', "Not Marker mesh : {}".format(line))
                        idl = 1
                
                #---------------------------------------
                # Add the Spoon line to the spoon path 
                #---------------------------------------                
                if idl == 2 :
                    lines_spoon.append(line)
                
                if idl == 1 :
                    lines_not_spoon.append(line)
            
            # Logger.log('d', "idl : {}".format(idl))
            if idl>0 :            
                result = ";BEGIN_OF_MODIFICATION"
                for line in lines_spoon:
                    result += "\n"
                    result += line
                for line in lines_not_spoon:
                    result += "\n"
                    result += line                    
                result += ";END_OF_MODIFICATION\n"          
            else:
                result = "\n".join(lines)
            
            data[layer_index] = result

        return data
