#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     July 13, 2022
#
# Description:  postprocessing-script to supress the Fan on First layers
#
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 13/07/2022
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Application import Application # To get the current printer's settings.
from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Message import Message
from UM.Logger import Logger
from UM.i18n import i18nCatalog # Translation
catalog = i18nCatalog("cura")

__version__ = '1.0'

class InhibFan(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "InhibFan",
            "key": "InhibFan",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "inhiblayer":
                {
                    "label": "Layer height Fan inhibition",
                    "description": "Number of Layer where we Inhib the Fan",
                    "type": "int",
                    "default_value": 4,
                    "minimum_value": 1,
                    "maximum_value": 100,
                    "minimum_value_warning": 1,
                    "maximum_value_warning": 100
                }
            }
        }"""

        
    def execute(self, data):
        
        usefan = False
        inhiblayer = 0 
        inhiblayer = int(self.getSettingValueByKey("inhiblayer"))
       
        current_Layer = 0
        idl=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:
 
                if line.startswith(";LAYER:"):
                    current_Layer = int(line.split(":")[1])
                    current_Layer += 1
                    if current_Layer <= inhiblayer :
                        idl=1
                    else : 
                        idl=0
                
                    
                if line.startswith("M106 S") and idl == 1 :
                    line_index = lines.index(line)
                    lines[line_index] = "M107"                

                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
