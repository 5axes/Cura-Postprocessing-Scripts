#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     January 13, 2020
#
# Description:  postprocessing-script to manage Fan Value
#
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.1 9/01/2020
#
#------------------------------------------------------------------------------------------------------------------------------------

import string
from ..Script import Script
from UM.Application import Application # To get the current printer's settings.
from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Message import Message
from UM.Logger import Logger
from UM.i18n import i18nCatalog # Translation
catalog = i18nCatalog("cura")

__version__ = '1.1'

class ChangeFanValue(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "ChangeFanValue",
            "key": "ChangeFanValue",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "usefanvalue":
                {
                    "label": "Set Fan Value on Minimum Time",
                    "description": "Change the Fan Value on minimum Time situation",
                    "type": "bool",
                    "default_value": false
                },
                "fanchange":
                {
                    "label": "Fan values in %",
                    "description": "The fan speed change of each block, list value separated by a comma ';' ",
                    "type": "int",
                    "unit": "%",
                    "default_value": 100,
                    "minimum_value": 1,
                    "maximum_value": 100,
                    "minimum_value_warning": 50,
                    "maximum_value_warning": 100
                }
            }
        }"""

    # Get the value
    def GetDataExtruder(self,id_ex,key,dec=0):
        
        # Deprecation Warning
        # extrud = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        extruder_stack = Application.getInstance().getExtruderManager().getActiveExtruderStacks()
        GetVal = extruder_stack[id_ex].getProperty(key, "value")
        #GetLabel = Application.getInstance().getGlobalContainerStack().getProperty(key, "label")
        #GetType = Application.getInstance().getGlobalContainerStack().getProperty(key, "type")
        #GetUnit = Application.getInstance().getGlobalContainerStack().getProperty(key, "unit")
                
        return GetVal
        
    def execute(self, data):
        
        usefan = False
        fanvalues = 0 
        usefan = bool(self.getSettingValueByKey("usefanvalue"))
        fanvalues = int(self.getSettingValueByKey("fanchange"))

        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        extruder_id=extruder_count

        #   cool_min_layer_time 
        self._cool_min_layer_time = float(self.GetDataExtruder(extruder_id,"cool_min_layer_time"))
        Logger.log('d', "cool_min_layer_time --> " + str(self._cool_min_layer_time) )
        
        currentfan = 0
        Current_Fan_Value = 0
        Current_Layer = 0
        setfan = int((int(fanvalues)/100)*255)  #  100% = 255 pour ventilateur
        #Logger.log('d', "setfan --> " + str(setfan) )
        
        save_time=0
        Just_Modi=0
        idl=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:
                if line.startswith(";LAYER:0"):
                    idl=0
 
                if line.startswith(";LAYER:"):
                    Current_Layer = int(line.split(":")[1])
                
                if line.startswith("; MODI_FAN"): 
                    Just_Modi=1
                    
                if line.startswith("M106 S") and usefan :
                    if Just_Modi==1 :
                        Just_Modi=0
                    else :
                        line_index = lines.index(line)
                        Current_Fan_Value = int(line.split("S")[1])
                        #Logger.log('d', "Current_Fan_Value --> " + str(Current_Fan_Value) )      
                        if idl==1:
                            lines[line_index] = "; " + line
                        
                # M107: Eteindre les ventilateurs
                if line.startswith("M107") and (usefan):
                    line_index = lines.index(line)
                    Current_Fan_Value=0
                    if idl==1:
                        lines[line_index] = "; " + line                   

                if line.startswith(";TIME_ELAPSED:"):
                    line_index = lines.index(line)
                    total_time = float(line.split(":")[1])
                    Layer_time=total_time-save_time
                    
                    if Layer_time<=self._cool_min_layer_time :
                        if idl==0:
                            #Logger.log('d', "Time MODI --> " + str(Layer_time))
                            #Logger.log('d', "MODI LAYER--> " + str(Current_Layer))
                            lines.insert(line_index + 1, "; MODI_FAN")
                            lines.insert(line_index + 2, "M106 S"+str(setfan))
                            idl=1
                            Just_Modi=1
                    else:
                        
                        if idl==1:
                            #Logger.log('d', "Reset Time --> " + str(Layer_time) )
                            #Logger.log('d', "Reset FAN VALUE --> " + str(Current_Fan_Value))
                            Cline=lines[line_index]
                            if Current_Fan_Value == 0:
                                lines.insert(line_index + 1, "M107")
                            else:
                                lines.insert(line_index + 1, "M106 S"+str(Current_Fan_Value))
                            idl=0

                    save_time=total_time

                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
