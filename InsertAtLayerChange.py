# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
# Created by Wayne Porter
# Modification 5@xes 12/2020 Option increment_layer

from ..Script import Script

class InsertAtLayerChange(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Insert at layer change",
            "key": "InsertAtLayerChange",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "insert_location":
                {
                    "label": "When to insert",
                    "description": "Whether to insert code before or after layer change.",
                    "type": "enum",
                    "options": {"before": "Before", "after": "After"},
                    "default_value": "before"
                },
                "increment_layer":
                {
                    "label": "Layer increment",
                    "description": "Number of layer increment to add this code",
                    "type": "int",
                    "value": "1",
                    "minimum_value": "1"
                },
                "gcode_to_add":
                {
                    "label": "G-code to insert.",
                    "description": "G-code to add before or after layer change.",
                    "type": "str",
                    "default_value": ""
                }
            }
        }"""

    def execute(self, data):
        increment = self.getSettingValueByKey("increment_layer")
        gcode_to_add = ";Code inserted by script : \n"
        tablines = self.getSettingValueByKey("gcode_to_add").split("<br>")
        for line in tablines:
            gcode_to_add = gcode_to_add + line + "\n"
        cur_inc=1
        
        for layer in data:
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:
                    index = data.index(layer)
                    if increment == cur_inc :
                        if self.getSettingValueByKey("insert_location") == "before":
                            layer = gcode_to_add + layer
                        else:
                            layer = layer + gcode_to_add
                        data[index] = layer
                        cur_inc=1
                    else :
                       cur_inc+=1 
                    
                    break
        return data
