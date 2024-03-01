#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   Ricardo Ortega
# Date:     March 01, 2024
#
# Description:  Modify M190 line
#               
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 01/03/2024 Change the M190 temperature to a percentage to start heating the nozzle
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application

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

    
class startHeatingAtPercentage(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "startHeatingAtPercentage",
            "key": "startHeatingAtPercentage",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "bedTempPercentage":
                {
                    "label": "Nozzle temperature percentage to start heating the nozzle",
                    "description": "What is the percentage of bed heating to start heating the nozzle.",
                    "type": "float",
                    "unit": "%",
                    "default_value": 100,
                    "minimum_value": "50",
                    "maximum_value": "100"
                }                     
            }
        }"""

    def execute(self, data):

        bedTempPercentage = float(self.getSettingValueByKey("bedTempPercentage")) 
        OnlyFirst=True
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            resLines=[]
            for line in lines:                  
               
                if ("M190" in line) and OnlyFirst:
                    temp=line.split("S")
                    if(len(temp)==2):
                        percTemp=int((float(temp[1])*bedTempPercentage)/100)
                        resLines.append(f"M190 S{percTemp}")
                        OnlyFirst=False
                else:
                    resLines.append(line)
                    
               
                
                
                       
            result = "\n".join(resLines)
            data[layer_index] = result

        return data