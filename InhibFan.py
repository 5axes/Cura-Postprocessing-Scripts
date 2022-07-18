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
#   Version 1.1 13/07/2022
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Application import Application # To get the current printer's settings.
from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Message import Message
from UM.Logger import Logger
from UM.i18n import i18nCatalog # Translation
catalog = i18nCatalog("cura")

__version__ = '1.1'

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
                    "label": "Nb of Layers for Fan inhibition",
                    "description": "Number of Layer where we want to turn off the print cooling fan",
                    "type": "int",
                    "default_value": 4,
                    "minimum_value": 1,
                    "maximum_value": 100,
                    "minimum_value_warning": 1,
                    "maximum_value_warning": 100
                },
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
        
        inhiblayer = 0 
        inhiblayer = int(self.getSettingValueByKey("inhiblayer"))

        extruder_id  = self.getSettingValueByKey("extruder_nb")
        extruder_id = extruder_id -1

        # GEt extrud
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
         #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count
            
        cool_fan_speed = extrud[extruder_id].getProperty("cool_fan_speed", "value")
        Logger.log('d', 'cool_fan_speed : {}'.format(cool_fan_speed)) 
        setfan = int((int(cool_fan_speed)/100)*255)
            
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
                    elif current_Layer == (inhiblayer + 1) :
                        line_index = lines.index(line)
                        next_line=lines[line_index+1]
                        Logger.log('d', 'next_line : {}'.format(next_line))
                        
                        if next_line.startswith("M106 S") :
                            Logger.log('d', 'Keep the S Value layer {}'.format(current_Layer))
                        elif next_line.startswith("M107") :
                            Logger.log('d', 'Keep the Fan OFF layer {}'.format(current_Layer))
                        else :
                            lines.insert(line_index + 1, "M106 S"+str(setfan))                        
                        idl=0
                        
                    else : 
                        idl=0                
                    
                if line.startswith("M106 S") and idl == 1 :
                    line_index = lines.index(line)
                    lines[line_index] = "M107"
                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
