# Cura PostProcessingPlugin
# Author:   5axes
# Date:     February 29, 2020
#
# Description:  postprocessing-script to easily define a Speed Tower
#
#
#   Version 1.0 29/02/2020
#

from ..Script import Script
from UM.Logger import Logger
import re #To perform the search
from UM.Application import Application
from UM.Message import Message

class SpeedTower(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "SpeedTower",
            "key": "SpeedTower",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "command": {
                    "label": "Command",
                    "description": "GCode Commande",
                    "type": "enum",
                    "options": {
                        "acceleration": "Acceleration",
                        "jerk": "Jerk"
                    },
                    "default_value": "acceleration"
                },
                "startValue":
                {
                    "label": "Starting value",
                    "description": "the starting value of the Tower.",
                    "type": "int",
                    "default_value": 8
                },
                "valueChange":
                {
                    "label": "Value Increment",
                    "description": "the value change of each block, can be positive or negative. I you want 220 and then 210, you need to set this to -10.",
                    "type": "int",
                    "default_value": 4
                },
                "changelayer":
                {
                    "label": "Change Layer",
                    "description": "how many layers needs to be printed before the value should be changed.",
                    "type": "float",
                    "default_value": 30,
                    "minimum_value": 1,
                    "maximum_value": 1000,
                    "minimum_value_warning": 5,
                    "maximum_value_warning": 100
                },
                "changelayeroffset":
                {
                    "label": "Change Layer Offset",
                    "description": "if the Tower has a base, put the layer high off it here",
                    "type": "float",
                    "default_value": 10,
                    "minimum_value": 0,
                    "maximum_value": 1000,
                    "maximum_value_warning": 100
                }
            }
        }"""

    def execute(self, data):

        Instruction = self.getSettingValueByKey("command")
        StartValue = self.getSettingValueByKey("startValue")
        ValueChange = self.getSettingValueByKey("valueChange")
        ChangeLayer = self.getSettingValueByKey("changelayer")
        ChangeLayerOffset = self.getSettingValueByKey("changelayeroffset")
        ChangeLayerOffset += 1  # Modif pour tenir compte du décalage de numérotation dans Gcode

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
                        if  (Instruction=='acceleration'):
                            Command = "M204 S{:d}".format(int(CurrentValue))
                        if  (Instruction=='jerk'):
                            Command = "M205 X{:d} Y{:d}".format(int(CurrentValue), int(CurrentValue))
                        lines.insert(line_index + 1, ";TYPE:CUSTOM LAYER")
                        lines.insert(line_index + 2, Command)

                    if ((layer_index-ChangeLayerOffset) % ChangeLayer == 0) and ((layer_index-ChangeLayerOffset)>0):
                            CurrentValue += ValueChange
                            if  (Instruction=='acceleration'):
                                Command = "M204 S{:d}".format(int(CurrentValue))
                            if  (Instruction=='jerk'):
                                Command = "M205 X{:d} Y{:d}".format(int(CurrentValue), int(CurrentValue))
                            lines.insert(line_index + 1, ";TYPE:CUSTOM VALUE")
                            lines.insert(line_index + 2, Command)
                                               
            
            result = "\n".join(lines)
            data[layer_index] = result

        return data
