# Custom Time Lapse

from ..Script import Script

class CustomTimeLapse(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Custom Time Lapse",
            "key": "CustomTimeLapse",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "first_gcode":
                {
                    "label": "GCODE for the first position(display position).",
                    "description": "GCODE to add before or after layer change.",
                    "type": "str",
                    "default_value": "G0 Y235"
                },
                "second_gcode":
                {
                    "label": "GCODE for the second position(trigger position).",
                    "description": "GCODE to add before or after layer change.",
                    "type": "str",
                    "default_value": "G0 X235"
                },
                "pause_length":
                {
                    "label": "Pause length",
                    "description": "How long to wait (in ms) after camera was triggered.",
                    "type": "int",
                    "default_value": 700,
                    "minimum_value": 0,
                    "unit": "ms"
                },
                "z_retract":
                {
                    "label": "Z retract",
                    "description": "Z retraction (in mm).",
                    "type": "float",
                    "default_value": 1,
                    "minimum_value": 0,
                    "unit": "mm"
                },
                "enable_retraction":
                {
                    "label": "Enable retraction",
                    "description": "Retract the filament before moving the head",
                    "type": "bool",
                    "default_value": true
                },
                "retraction_distance":
                {
                    "label": "Retraction distance",
                    "description": "How much to retract the filament.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5,
                    "enabled": "enable_retraction"
                },
                "retraction_speed":
                {
                    "label": "Retraction speed",
                    "description": "Define retraction speed to retract the filament.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 50,
                    "enabled": "enable_retraction"
                },
                "display_photo_number":
                {
                    "label": "Display current photo number",
                    "description": "Display the current photo number on the panel during the shots",
                    "type": "bool",
                    "default_value": false
                },
                "send_photo_command":
                {
                    "label": "Send camera command",
                    "description": "Send camera command defined in Trigger camera command",
                    "type": "bool",
                    "default_value": false
                },
                "trigger_command":
                {
                    "label": "Trigger camera command",
                    "description": "Gcode command used to trigger camera.",
                    "type": "str",
                    "default_value": "M240",
                    "enabled": "send_photo_command"
                }
            }
        }"""
        
    # Note : This function and some other bits of code comes from PauseAtHeight.py
    ##  Get the X and Y values for a layer (will be used to get X and Y of the
    #   layer after the pause).
    def getNextXY(self, layer):
        lines = layer.split("\n")
        for line in lines:
            if self.getValue(line, "X") is not None and self.getValue(line, "Y") is not None:
                x = self.getValue(line, "X")
                y = self.getValue(line, "Y")
                return x, y
        return 0, 0

    def execute(self, data):
        max_layer = 0
        first_gcode = self.getSettingValueByKey("first_gcode")
        second_gcode = self.getSettingValueByKey("second_gcode")
        pause_length = self.getSettingValueByKey("pause_length")
        z_retraction = self.getSettingValueByKey("z_retract")
        enable_retraction = self.getSettingValueByKey("enable_retraction")
        retraction_distance = self.getSettingValueByKey("retraction_distance")
        retraction_speed = self.getSettingValueByKey("retraction_speed")
        retraction_speed = retraction_speed * 60
        
        display_photo_number = self.getSettingValueByKey("display_photo_number")
        send_photo_command = self.getSettingValueByKey("send_photo_command")
        trigger_command = self.getSettingValueByKey("trigger_command")

        for layerIndex, layer in enumerate(data):
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if line.startswith(";LAYER_COUNT:"):
                    max_layer = int(line.split(":")[1])   # Recuperation Nb Layer Maxi
                    
                if ";LAYER:" in line:
                    index = data.index(layer)

                    next_layer = data[layerIndex + 1]
                    x, y = self.getNextXY(next_layer)

                    gcode_to_append = ""

                    gcode_to_append += "; CustomTimelapse Begin\n"

                    if display_photo_number:
                        gcode_to_append += "M117 Photo " + str(layerIndex) + "\n"
                    
                    if enable_retraction:
                        gcode_to_append += "; STEP 1 : retraction\n"
                        gcode_to_append += self.putValue(M = 83) + " ; Switch to relative E values for any needed retraction\n"
                        gcode_to_append += self.putValue(G = 1, F = retraction_speed, E = -retraction_distance) + " ; Retraction\n"
                        gcode_to_append += self.putValue(M = 82) + " ; Switch back to absolute E values\n"

                    gcode_to_append += "; STEP 2 : Move the head up a bit\n"
                    gcode_to_append += self.putValue(G = 91) + " ; Switch to relative positioning\n"
                    gcode_to_append += self.putValue(G = 0, Z = z_retraction) + " ; Move Z axis up a bit\n"
                    gcode_to_append += self.putValue(G = 90) + " ; Switch back to absolute positioning\n"

                    gcode_to_append += "; STEP 3 : Move the head to \"display\" position and wait\n"
                    gcode_to_append += first_gcode + " ; GCODE for the first position(display position)\n"
                    gcode_to_append += second_gcode + " ; GCODE for the second position(trigger position)\n"
                    gcode_to_append += self.putValue(M = 400) + " ; Wait for moves to finish\n"
                    gcode_to_append += self.putValue(G = 4, P = pause_length) + " ; Pause\n"

                    gcode_to_append += "; STEP 4 : send photo trigger command if set\n"
                    if send_photo_command:
                        gcode_to_append += trigger_command + " ; Snap Photo\n"
                        gcode_to_append += self.putValue(G = 4, P = pause_length) + " ; Wait for camera\n"

                    gcode_to_append += self.putValue(M = 211, S=1) + " ; Turn on soft stops\n"

                    # Skip steps 5 and 6 for the last layer
                    if layerIndex <= max_layer :
                        gcode_to_append += "; STEP 5 : Move the head back in its original place\n"
                        gcode_to_append += self.putValue(G = 0, X = x, Y = y) + "\n"

                        gcode_to_append += "; STEP 6 : Move the head height back down\n"
                        gcode_to_append += self.putValue(G = 91) + " ; Switch to relative positioning\n"
                        gcode_to_append += self.putValue(G = 0, Z = -z_retraction) + " ; Restore Z axis position\n"
                        gcode_to_append += self.putValue(G = 90) + " ; Switch back to absolute positioning\n"

                        if enable_retraction:
                            gcode_to_append += "; STEP 7 : reset extruder position\n"
                            gcode_to_append += self.putValue(M = 83) + " ; Switch to relative E values to reset extruder position\n"
                            gcode_to_append += self.putValue(G = 1, F = retraction_speed, E = retraction_distance) + " ; Reset extruder position\n"
                            gcode_to_append += self.putValue(M = 82) + " ; Switch back to absolute E values\n"
                    
                    gcode_to_append += "; CustomTimelapse End\n"


                    layer += gcode_to_append

                    data[index] = layer
                    break
        return data
