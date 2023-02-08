# Copyright (c) 2023 5@xes
# Insert At Layer Number Add comment 08/02/2023

from ..Script import Script

class InsertAtLayerNumber(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Insert at layer number",
            "key": "InsertAtLayerNumber",
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
                "position_layer":
                {
                    "label": "Layer position",
                    "description": "Layer Position where to add this code",
                    "type": "int",
                    "value": 1,
                    "minimum_value": 1
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
        position = self.getSettingValueByKey("position_layer")
        gcode_to_add = ";Code inserted by script : \n"
        tablines = self.getSettingValueByKey("gcode_to_add").split("<br>")
        for line in tablines:
            gcode_to_add = gcode_to_add + line + "\n"
        
        for layer in data:
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:
                    layer_number = int(line.split(":")[1])+1
                    index = data.index(layer)
                    if position == layer_number :
                        if self.getSettingValueByKey("insert_location") == "before":
                            layer = gcode_to_add + layer
                        else:
                            layer = layer + gcode_to_add
                        data[index] = layer
                    
                    break
        return data
