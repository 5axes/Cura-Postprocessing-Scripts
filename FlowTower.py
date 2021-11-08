#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     August 29, 2021
#
# Description:  postprocessing script to easily define a Flow Tower 
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 29/08/2021
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Application import Application
from UM.Logger import Logger
import re #To perform the search

__version__ = '1.0'

class FlowTower(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "FlowTower",
            "key": "FlowTower",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "startValue":
                {
                    "label": "Starting value",
                    "description": "the starting value of the Tower.",
                    "type": "float",
                    "default_value": 110.0
                },
                "valueChange":
                {
                    "label": "Value Increment",
                    "description": "the value change of each block, can be positive or negative. I you want 110 and then 108, you need to set this to -2.",
                    "type": "float",
                    "default_value": -2.0
                },
                "changelayer":
                {
                    "label": "Change Layer",
                    "description": "how many layers needs to be printed before the value should be changed.",
                    "type": "float",
                    "default_value": 40,
                    "minimum_value": 1,
                    "maximum_value": 1000,
                    "maximum_value_warning": 100
                },
                "changelayeroffset":
                {
                    "label": "Change Layer Offset",
                    "description": "if the Tower has a base, put the layer high off it here",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 1000,
                    "maximum_value_warning": 100
                },
                "lcdfeedback":
                {
                    "label": "Display details on LCD",
                    "description": "This setting will insert M117 gcode instructions, to display current modification in the G-Code is being used.",
                    "type": "bool",
                    "default_value": true
                }                
            }
        }"""

    def execute(self, data):

        UseLcd = self.getSettingValueByKey("lcdfeedback")
        StartValue = float(self.getSettingValueByKey("startValue"))
        ValueChange = float(self.getSettingValueByKey("valueChange"))
        ChangeLayer = self.getSettingValueByKey("changelayer")
        ChangeLayerOffset = self.getSettingValueByKey("changelayeroffset")
        ChangeLayerOffset += 2  # Modification to take into account the numbering offset in Gcode
                                # layer_index = 0 for initial Block 1= Start Gcode normaly first layer = 0 

        CurrentValue = StartValue
        Command=""

        idl=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:                  
               
                if line.startswith(";LAYER:"):
                    line_index = lines.index(line)
                    # Logger.log('d', 'Instruction : {}'.format(Instruction))

                    if (layer_index==ChangeLayerOffset):
                        Command = "M221 S{:d}".format(int(CurrentValue))
                        lcd_gcode = "M117 Flow S{:d}".format(int(CurrentValue))  
                            
                        lines.insert(line_index + 1, ";TYPE:CUSTOM LAYER")
                        lines.insert(line_index + 2, Command)
                        if UseLcd == True :               
                            lines.insert(line_index + 3, lcd_gcode)

                    if ((layer_index-ChangeLayerOffset) % ChangeLayer == 0) and ((layer_index-ChangeLayerOffset)>0):
                            CurrentValue += ValueChange
                            Command = "M221 S{:d}".format(int(CurrentValue))
                            lcd_gcode = "M117 Flow S{:d}".format(int(CurrentValue)) 
                                
                            lines.insert(line_index + 1, ";TYPE:CUSTOM VALUE")
                            lines.insert(line_index + 2, Command)
                            if UseLcd == True :               
                               lines.insert(line_index + 3, lcd_gcode)                                              
            
            result = "\n".join(lines)
            data[layer_index] = result

        return data
