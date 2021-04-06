#------------------------------------------------------------------------------------------------------------------------------------
# Cura PostProcessingPlugin
# Author:   5axes
# Date:     February 29, 2020
#
# Description:  postprocessing-script to easily define a Speed Tower 
#           Option for  Speed
#                       Acceleration
#                       Junction Deviation
#
#   Version 1.0 29/02/2020
#   Version 1.1 29/01/2021
#   Version 1.2 05/04/2021 by dotdash32 (https://github.com/dotdash32) for Marlin Linear Advance & RepRap Pressure Adance
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
import re #To perform the search
from UM.Application import Application
from UM.Message import Message

__version__ = '1.1'

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
                        "jerk": "Jerk",
                        "junction": "Junction Deviation",
                        "marlinadv": "Marlin Linear Advance",
                        "rrfpresure": "RepRap Pressure Adance"
                    },
                    "default_value": "acceleration"
                },
                "startValue":
                {
                    "label": "Starting value",
                    "description": "the starting value of the Tower.",
                    "type": "float",
                    "default_value": 8.0
                },
                "valueChange":
                {
                    "label": "Value Increment",
                    "description": "the value change of each block, can be positive or negative. I you want 50 and then 40, you need to set this to -10.",
                    "type": "float",
                    "default_value": 4.0
                },
                "changelayer":
                {
                    "label": "Change Layer",
                    "description": "how many layers needs to be printed before the value should be changed.",
                    "type": "int",
                    "default_value": 30,
                    "minimum_value": 1,
                    "maximum_value": 1000,
                    "maximum_value_warning": 100
                },
                "changelayeroffset":
                {
                    "label": "Change Layer Offset",
                    "description": "if the Tower has a base, put the layer high off it here",
                    "type": "int",
                    "default_value": 4,
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
        Instruction = self.getSettingValueByKey("command")
        StartValue = float(self.getSettingValueByKey("startValue"))
        ValueChange = float(self.getSettingValueByKey("valueChange"))
        ChangeLayer = self.getSettingValueByKey("changelayer")
        ChangeLayerOffset = self.getSettingValueByKey("changelayeroffset")
        ChangeLayerOffset += 1  # Modified to take into account the numbering offset in Gcode

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
                            lcd_gcode = "M117 Acceleration S{:d}".format(int(CurrentValue))
                        if  (Instruction=='jerk'):
                            Command = "M205 X{:d} Y{:d}".format(int(CurrentValue), int(CurrentValue))
                            lcd_gcode = "M117 Jerk X{:d} Y{:d}".format(int(CurrentValue), int(CurrentValue))
                        if  (Instruction=='junction'):
                            Command = "M205 J{:.3f}".format(float(CurrentValue))
                            lcd_gcode = "M117 Junction J{:.3f}".format(float(CurrentValue))     
                        if  (Instruction=='marlinadv'):
                            Command = "M900 K{:.3f}".format(float(CurrentValue))
                            lcd_gcode = "M117 Linear Advance K{:.3f}".format(float(CurrentValue))  
                        if  (Instruction=='rrfpresure'):
                            Command = "M572 D0 S{:.3f}".format(float(CurrentValue))
                            lcd_gcode = "M117 Pressure Advance S{:.3f}".format(float(CurrentValue))   
                            
                        lines.insert(line_index + 1, ";TYPE:CUSTOM LAYER")
                        lines.insert(line_index + 2, Command)
                        if UseLcd == True :               
                            lines.insert(line_index + 3, lcd_gcode)

                    if ((layer_index-ChangeLayerOffset) % ChangeLayer == 0) and ((layer_index-ChangeLayerOffset)>0):
                            CurrentValue += ValueChange
                            if  (Instruction=='acceleration'):
                                Command = "M204 S{:d}".format(int(CurrentValue))
                                lcd_gcode = "M117 Acceleration S{:d}".format(int(CurrentValue))
                            if  (Instruction=='jerk'):
                                Command = "M205 X{:d} Y{:d}".format(int(CurrentValue), int(CurrentValue))
                                lcd_gcode = "M117 Jerk X{:d} Y{:d}".format(int(CurrentValue), int(CurrentValue))
                            if  (Instruction=='junction'):
                                Command = "M205 J{:.3f}".format(float(CurrentValue))
                                lcd_gcode = "M117 Junction J{:.3f}".format(float(CurrentValue))
                            if (Instruction=='marlinadv'):
                                Command = "M900 K{:.3f}".format(float(CurrentValue))
                                lcd_gcode = "M117 Linear Advance K{:.3f}".format(float(CurrentValue))
                            if  (Instruction=='rrfpresure'):
                                Command = "M572 D0 S{:.3f}".format(float(CurrentValue))
                                lcd_gcode = "M117 Pressure Advance S{:.3f}".format(float(CurrentValue)) 
                                
                            lines.insert(line_index + 1, ";TYPE:CUSTOM VALUE")
                            lines.insert(line_index + 2, Command)
                            if UseLcd == True :               
                               lines.insert(line_index + 3, lcd_gcode)                                              
            
            result = "\n".join(lines)
            data[layer_index] = result

        return data
