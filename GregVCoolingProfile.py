# January 2023 by GregValiant (Greg Foresi)
#Design Scope
#    Remove or comment out any existing M106 lines from the file. (I didn't figure that out so there is no code for that yet)
#    Import the {machine_scale_fan_speed_zero_to_one} setting from Cura to set the "fan_mode" variable.
#    Collect the values from the dialog
#    Enter either the Layer fan speeds (at ";LAYER:") or the Feature fan speeds (at ;TYPE:WALL-OUTER, etc.).
#    If the user declares an Ending Layer and By Feature is selected then the final fan speed is entered at that last layer.
#    An M106 S0 would need to be added at the ";End of Gcode" line in the file.
#    It would be nice to have a method to clear all the "By Layer" boxes as "enabled" counts on the previous box having text in it.
#Current state:
#    This loads but doesn't work.

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search

class GregVCoolingProfile(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Add a Cooling Profile",
            "key": "GregVCoolingProfile",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "layer_or_feature":
                {
                    "label": "Cooling Profile by:",
                    "description": "By Layer number or by Feature (Walls, Skins, Support, etc.).  Minimum Fan Percentage is 15%.",
                    "type": "enum",
                    "options": {
                        "by_layer": "Layer Numbers",
                        "by_feature": "Feature Type"},
                    "default_value": "by_layer"
                },
                "start_layer":
                {
                    "label": "Starting Layer",
                    "description": "Layer to start the insertion at.",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": 0,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "end_layer":
                {
                    "label": "Ending Layer",
                    "description": "Layer to end the insertion at.  Enter -1 for the entire file or enter a layer number.  If using By Feature and you set an End Layer then you must set the Final % that will finish the file",
                    "type": "int",
                    "default_value": -1,
                    "minimum_value": -1,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_first":
                {
                    "label": "Layer/Percent #1",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "3/25",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_second":
                {
                    "label": "Layer/Percent #2",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_third":
                {
                    "label": "Layer/Percent #3",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_fourth":
                {
                    "label": "Layer/Percent #4",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_fifth":
                {
                    "label": "Layer/Percent #5",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_sixth":
                {
                    "label": "Layer/Percent #6",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_seventh":
                {
                    "label": "Layer/Percent #7",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_eighth":
                {
                    "label": "Layer/Percent #8",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_ninth":
                {
                    "label": "Layer/Percent #9",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_tenth":
                {
                    "label": "Layer/Percent #10",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_eleventh":
                {
                    "label": "Layer/Percent #11",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_twelfth":
                {
                    "label": "Layer/Percent #12",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "layer_or_feature == 'by_layer'"
                },
                "fan_skirt":
                {
                    "label": "Skirt/Brim %",
                    "description": "Enter the fan percentage for skirt/brim/raft.",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_wall_inner":
                {
                    "label": "Inner Walls %",
                    "description": "Enter the fan percentage for the Wall-Inner.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_wall_outer":
                {
                    "label": "Outer Walls %",
                    "description": "Enter the fan percentage for the Wall-Outer.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_fill":
                {
                    "label": "Infill %",
                    "description": "Enter the fan percentage for the Infill.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_skin":
                {
                    "label": "Top/Bottom (Skin) %",
                    "description": "Enter the fan percentage for the Skins.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_support":
                {
                    "label": "Support %",
                    "description": "Enter the fan percentage for the Supports.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_support_interface":
                {
                    "label": "Support Interface %",
                    "description": "Enter the fan percentage for the Support Interface.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_prime_tower":
                {
                    "label": "Prime Tower %",
                    "description": "Enter the fan percentage for the Prime Tower.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_bridge":
                {
                    "label": "Bridge %",
                    "description": "Enter the fan percentage for the Bridges.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "layer_or_feature == 'by_feature'"
                },
                "fan_feature_final":
                {
                    "label": "Final %",
                    "description": "Finishing percentage if the profile ends at a layer prior to the end of the gcode file.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "end_layer > -1 and layer_or_feature == 'by_feature'"
                }
            }
        }"""

    def execute(self, data):
    
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        fan_mode = not bool(extrud[0].getProperty("machine_scale_fan_speed_zero_to_one", "value")) #Need to pull the setting {machine_scale_fan_speed_zero_to_one} from Cura 
        
        # fan_mode = not Application.getInstance().getPrintInformation().machine_scale_fan_speed_zero_to_one   #Need to pull the setting {machine_scale_fan_speed_zero_to_one} from Cura 
        # Fill the variables for Layer Cooling and add them to the "fan_array" list.  "mt" is used as place holder for empty slots.           
        fan_array = []
        layer_number=0
        by_layer_or_feature = self.getSettingValueByKey("layer_or_feature")
        
        if by_layer_or_feature == "by_layer":
            fan_first = self.getSettingValueByKey("fan_first")
            if fan_first == "": fan_first = "mt/mt"
            fan_first = fan_first.split("/")

            if fan_first[0] != "mt" and int(fan_first[1]) < 15 and int(fan_first[1]) != 0: fan_first[1] = "15"
            fan_array.append(";LAYER:" + fan_first[0])        
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_first[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_first[1]) / 100, 1)))

            fan_second = self.getSettingValueByKey("fan_second")
            if fan_second == "": fan_second = "mt/mt"
            fan_second = fan_second.split("/")
            if fan_second[0] != "mt" and int(fan_second[1]) < 15 and int(fan_second[1]) != 0: fan_second[1] = "15"
            fan_array.append(";LAYER:" + fan_second[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_second[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_second[1]) / 100, 1)))

            fan_third = self.getSettingValueByKey("fan_third")
            if fan_third == "": fan_third = "mt/mt"
            fan_third = fan_third.split("/")
            if fan_third[0] != "mt" and int(fan_third[1]) < 15 and int(fan_third[1]) != 0: fan_third[1] = "15"
            fan_array.append(";LAYER:" + fan_third[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_third[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_third[1]) / 100, 1)))

            fan_fourth = self.getSettingValueByKey("fan_fourth")
            if fan_fourth == "": fan_fourth = "mt/mt"
            fan_fourth = fan_fourth.split("/")
            if fan_fourth[0] != "mt" and int(fan_fourth[1]) < 15 and int(fan_fourth[1]) != 0: fan_fourth[1] = "15"
            fan_array.append(";LAYER:" + fan_fourth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_fourth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_fourth[1]) / 100, 1)))

            fan_fifth = self.getSettingValueByKey("fan_fifth")
            if fan_fifth == "": fan_fifth = "mt/mt"
            fan_fifth = fan_fifth.split("/")
            if fan_fifth[0] != "mt" and int(fan_fifth[1]) < 15 and int(fan_fifth[1]) != 0: fan_fifth[1] = "15"
            fan_array.append(";LAYER:" + fan_fifth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_fifth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_fifth[1]) / 100, 1)))

            fan_sixth = self.getSettingValueByKey("fan_sixth")
            if fan_sixth == "": fan_sixth = "mt/mt"
            fan_sixth = fan_sixth.split("/")
            if fan_sixth[0] != "mt" and int(fan_sixth[1]) < 15 and int(fan_sixth[1]) != 0: fan_sixth[1] = "15"
            fan_array.append(";LAYER:" + fan_sixth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_sixth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_sixth[1]) / 100, 1)))

            fan_seventh = self.getSettingValueByKey("fan_seventh")
            if fan_seventh == "": fan_seventh = "mt/mt"
            fan_seventh = fan_seventh.split("/")
            if fan_seventh[0] != "mt" and int(fan_seventh[1]) < 15 and int(fan_seventh[1]) != 0: fan_seventh[1] = "15"
            fan_array.append(";LAYER:" + fan_seventh[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_seventh[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_seventh[1]) / 100, 1)))

            fan_eighth = self.getSettingValueByKey("fan_eighth")
            if fan_eighth == "": fan_eighth = "mt/mt"
            if fan_eighth[0] != "mt" and int(fan_eighth[1]) < 15 and int(fan_eighth[1]) != 0: fan_eighth[1] = "15"
            fan_array.append(";LAYER:" + fan_eighth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_eighth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_eighth[1]) / 100, 1)))

            fan_ninth = self.getSettingValueByKey("fan_ninth")
            if fan_ninth == "": fan_ninth = "mt/mt"
            fan_ninth = fan_ninth.split("/")
            if fan_ninth[0] != "mt" and int(fan_ninth[1]) < 15 and int(fan_ninth[1]) != 0: fan_ninth[1] = "15"
            fan_array.append(";LAYER:" + fan_ninth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_ninth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_ninth[1]) / 100, 1)))

            fan_tenth = self.getSettingValueByKey("fan_tenth")
            if fan_tenth == "": fan_tenth = "mt/mt"
            fan_tenth = fan_tenth.split("/")
            if fan_tenth[0] != "mt" and int(fan_tenth[1]) < 15 and int(fan_tenth[1]) != 0: fan_tenth[1] = "15"
            fan_array.append(";LAYER:" + fan_tenth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_tenth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_tenth[1]) / 100, 1)))

            fan_eleventh = self.getSettingValueByKey("fan_eleventh")
            if fan_eleventh == "": fan_eleventh = "mt/mt"
            fan_eleventh = fan_eleventh.split("/")
            if fan_eleventh[0] != "mt" and int(fan_eleventh[1]) < 15 and int(fan_eleventh[1]) != 0: fan_eleventh[1] = "15"
            fan_array.append(";LAYER:" + fan_eleventh[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_eleventh[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_eleventh[1]) / 100, 1)))

            fan_twelfth = self.getSettingValueByKey("fan_twelfth")
            if fan_twelfth == "": fan_twelfth = "me/mt"
            fan_twelfth = fan_twelfth.split("/")
            if fan_twelfth[0] != "mt" and int(fan_twelfth[1]) < 15 and int(fan_twelfth[1]) != 0: fan_twelfth[1] = "15"
            fan_array.append(";LAYER:" + fan_twelfth[0])
            if fan_mode:
                fan_array.append("M106 S" + str(round(int(fan_twelfth[1]) * 2.55)))

            else:
                fan_array.append("M106 S" + str(round(int(fan_twelfth[1]) / 100, 1)))
                
                #Get the variables for the feature speeds and the start and the end layers                
        elif by_layer_or_feature == "by_feature":    
            the_start_layer = self.getSettingValueByKey("start_layer")
            the_end_layer = self.getSettingValueByKey("end_layer")
            fan_skirt = self.getSettingValueByKey("fan_skirt")

            if fan_mode:
                fan_sp_skirt = "M106 S" + str(round(int(fan_skirt) * 2.55))

            else:
                fan_sp_skirt = "M106 S" + str(round(int(fan_skirt) / 100, 1))

            fan_wall_inner = self.getSettingValueByKey("fan_wall_inner")

            if fan_mode:
                fan_sp_wall_inner = "M106 S" + str(round(int(fan_wall_inner) * 2.55))

            else:
                fan_sp_wall_inner = "M106 S" + str(round(int(fan_wall_inner) / 100, 1))

            fan_wall_outer = self.getSettingValueByKey("fan_wall_outer")

            if fan_mode:
                fan_sp_wall_outer = "M106 S" + str(round(int(fan_wall_outer) * 2.55))

            else:
                fan_sp_wall_outer = "M106 S" + str(round(int(fan_wall_outer) / 100, 1))

            fan_fill = self.getSettingValueByKey("fan_fill")

            if fan_mode:
                fan_sp_fill = "M106 S" + str(round(int(fan_fill) * 2.55))

            else:
                fan_sp_fill = "M106 S" + str(round(int(fan_fill) / 100, 1))

            fan_skin = self.getSettingValueByKey("fan_skin")

            if fan_mode:
                fan_sp_skin = "M106 S" + str(round(int(fan_skin) * 2.55))

            else:
                fan_sp_skin = "M106 S" + str(round(int(fan_skin) / 100, 1))

            fan_support = self.getSettingValueByKey("fan_support")

            if fan_mode:
                fan_sp_support = "M106 S" + str(round(int(fan_support) * 2.55))

            else:
                fan_sp_support = "M106 S" + str(round(int(fan_support) / 100, 1))

            fan_support_interface = self.getSettingValueByKey("fan_support_interface")

            if fan_mode:
                fan_sp_support_interface = "M106 S" + str(round(int(fan_support_interface) * 2.55))

            else:
                fan_sp_support_interface = "M106 S" + str(round(int(fan_support_interface) / 100, 1))

            fan_prime_tower = self.getSettingValueByKey("fan_prime_tower")

            if fan_mode:
                fan_sp_prime_tower = "M106 S" + str(round(int(fan_prime_tower) * 2.55))

            else:
                fan_sp_prime_tower = "M106 S" + str(round(int(fan_prime_tower) / 100, 1))

            fan_bridge = self.getSettingValueByKey("fan_bridge")

            if fan_mode:
                fan_sp_bridge = "M106 S" + str(round(int(fan_bridge) * 2.55))

            else:
                fan_sp_bridge = "M106 S" + str(round(int(fan_bridge) / 100, 1))

            fan_feature_final = self.getSettingValueByKey("fan_feature_final")

            if fan_mode:
                fan_sp_feature_final = "M106 S" + str(round(int(fan_feature_final) * 2.55))

            else:
                fan_sp_feature_final = "M106 S" + str(round(int(fan_feature_final) / 100, 1))

            if the_end_layer > -1 and by_layer_or_feature == "by_feature":
                the_end_is_enabled = True

            else:
                the_end_is_enabled = False

            if the_end_layer == -1 or the_end_is_enabled == False:
                the_end_layer = "299792458000"
     
        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")            
            for line in lines:
                line_index = lines.index(line)
                #Remove all the existing M106 lines from the gcode.
                if line.startswith("M106"):
                    lines[line_index]=""
                          
                            
                if by_layer_or_feature == "by_layer":
                    if ";LAYER:" in line:
                        layer_number = int(line.split(":")[1])
                        if (layer_number >= int(the_start_layer)) and layer_number <= int(the_end_layer):  
                            index = data.index(layer)
                            for num in range(0, 23, 2):
                                if fan_array[num] in line:
                                    layer += "\n" + fan_array[num + 1]
                                    data[index] = layer
                                    
                elif by_layer_or_feature == "by_feature":
                    if ";LAYER:" in line:
                        layer_number = int(line.split(":")[1])
                        
                    if layer_number >= int(the_start_layer) and layer_number < int(the_end_layer):  
                        index = data.index(layer)
                        if ";TYPE:SKIRT" in line:
                            lines[line_index] += "\n" + fan_sp_skirt

                        elif ";TYPE:WALL-INNER" in line:    
                            lines[line_index] += "\n" + fan_sp_wall_inner

                        elif ";TYPE:WALL-OUTER" in line: 
                            # Logger.log('d', 'line_index : {}'.format(lines[line_index]))                        
                            lines[line_index] += "\n" + fan_sp_wall_outer
                            # Logger.log('d', 'line_index : {}'.format(lines[line_index]))

                        elif ";TYPE:FILL" in line:    
                            lines[line_index] += "\n" + fan_sp_fill

                        elif ";TYPE:SKIN" in line:    
                            lines[line_index] += "\n" + fan_sp_skin

                        elif ";TYPE:SUPPORT" in line:    
                            lines[line_index] += "\n" + fan_sp_support

                        elif ";TYPE:SUPPORT-INTERFACE" in line:    
                            lines[line_index] += "\n" + fan_sp_support_interface

                        elif ";TYPE:PRIME-TOWER" in line:    
                            lines[line_index] += "\n" + fan_sp_prime_tower

                        elif ";TYPE:BRIDGE" in line:    
                            lines[line_index] += "\n" + fan_sp_bridge
                                                  
                    elif layer_number == int(the_end_layer) and the_end_is_enabled == True:
                        lines[line_index] += "\n" + fan_sp_feature_final
                        
                    if ";End of gcode" in line:
                        lines[line_index] += "\n" + "M106 S0"

            result = "\n".join(lines)
            data[layer_index] = result
        return data