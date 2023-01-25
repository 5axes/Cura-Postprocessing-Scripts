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

class GregVCoolingProfile5axes(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "GV and 5axes Cooling profile",
            "key": "GregVCoolingProfile5axes",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "fan_layer_or_feature":
                {
                    "label": "Cooling Profile by:",
                    "description": "By Layer number or by Feature (Walls, Skins, Support, etc.).  Minimum Fan Percentage is 15%.",
                    "type": "enum",
                    "options": {
                        "by_layer": "Layer Numbers",
                        "by_feature": "Feature Type",
                        "supress_fan": "Supress Fan Value"
                        },
                    "default_value": "by_layer"
                },
                "fan_start_layer":
                {
                    "label": "Starting Layer",
                    "description": "Layer to start the insertion at.",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": 0,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_end_layer":
                {
                    "label": "Ending Layer",
                    "description": "Layer to end the insertion at.  Enter -1 for the entire file or enter a layer number.  If using By Feature and you set an End Layer then you must set the Final % that will finish the file",
                    "type": "int",
                    "default_value": -1,
                    "minimum_value": -1,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_first":
                {
                    "label": "Layer/Percent #1",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "3/25",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_second":
                {
                    "label": "Layer/Percent #2",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_third":
                {
                    "label": "Layer/Percent #3",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_fourth":
                {
                    "label": "Layer/Percent #4",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_fifth":
                {
                    "label": "Layer/Percent #5",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_sixth":
                {
                    "label": "Layer/Percent #6",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_seventh":
                {
                    "label": "Layer/Percent #7",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_eighth":
                {
                    "label": "Layer/Percent #8",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_ninth":
                {
                    "label": "Layer/Percent #9",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_tenth":
                {
                    "label": "Layer/Percent #10",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_eleventh":
                {
                    "label": "Layer/Percent #11",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_twelfth":
                {
                    "label": "Layer/Percent #12",
                    "description": "Enter as: 'LAYER / Percent' Ex: 57/100 with the layer first, then a '/' to delimit, and then the fan percentage.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "fan_layer_or_feature == 'by_layer'"
                },
                "fan_skirt":
                {
                    "label": "Skirt/Brim %",
                    "description": "Enter the fan percentage for skirt/brim/raft.",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_wall_inner":
                {
                    "label": "Inner Walls %",
                    "description": "Enter the fan percentage for the Wall-Inner.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_wall_outer":
                {
                    "label": "Outer Walls %",
                    "description": "Enter the fan percentage for the Wall-Outer.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_fill":
                {
                    "label": "Infill %",
                    "description": "Enter the fan percentage for the Infill.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_skin":
                {
                    "label": "Top/Bottom (Skin) %",
                    "description": "Enter the fan percentage for the Skins.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_support":
                {
                    "label": "Support %",
                    "description": "Enter the fan percentage for the Supports.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_support_interface":
                {
                    "label": "Support Interface %",
                    "description": "Enter the fan percentage for the Support Interface.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_prime_tower":
                {
                    "label": "Prime Tower %",
                    "description": "Enter the fan percentage for the Prime Tower.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_bridge":
                {
                    "label": "Bridge %",
                    "description": "Enter the fan percentage for the Bridges.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_layer_or_feature == 'by_feature'"
                },
                "fan_feature_final":
                {
                    "label": "Final %",
                    "description": "Finishing percentage if the profile ends at a layer prior to the end of the gcode file.",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "fan_end_layer > -1 and fan_layer_or_feature == 'by_feature'"
                }
            }
        }"""

    def execute(self, data):
        fan_first_l = "0"
        fan_first_p = "0"
        fan_second_l = "0"
        fan_second_p = "0"
        fan_third_l = "0"
        fan_third_p = "0"
        fan_fourth_l = "0"
        fan_fourth_p = "0"
        fan_fifth_l = "0"
        fan_fifth_p = "0"
        fan_sixth_l = "0"
        fan_sixth_p = "0"
        fan_seventh_l = "0"
        fan_seventh_p = "0"
        fan_eighth_l = "0"
        fan_eighth_p = "0"
        fan_ninth_l = "0"
        fan_ninth_p = "0"
        fan_tenth_l = "0"
        fan_fan_tenth_p = "0"
        fan_eleventh_l = "0"
        fan_eleventh_p = "0"
        fan_twelfth_l = "0"
        fan_twelfth_p = "0"
        fan_mode = True
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        fan_mode = not bool(extrud[0].getProperty("machine_scale_fan_speed_zero_to_one", "value")) #Need to pull the setting {machine_scale_fan_speed_zero_to_one} from Cura  not Application.getInstance().getPrintInformation().machine_scale_fan_speed_zero_to_one   #Need to pull the setting {machine_scale_fan_speed_zero_to_one} from Cura 
            #Fill the variables for Layer Cooling and add them to the "fan_array" list.  "mt" is used as place holder for empty slots.           
        fan_array = []
        for q in range(0,24,1):
            fan_array.append("mt")
        
        by_layer_or_feature = self.getSettingValueByKey("fan_layer_or_feature")
        if  by_layer_or_feature == "by_layer":
            fan_first = self.getSettingValueByKey("fan_first")
            if "/" in fan_first:
                fan_first_l = str(fan_first.split("/")[0])
                if int(fan_first_l) < 0: fan_first_l = "0"
                fan_first_p = str(fan_first.split("/")[1])
                if int(fan_first_p) < 0: fan_first_p = "0"
                if int(fan_first_p) > 100: fan_first_p = "100"
                if (fan_first_l != "mt" and int(fan_first_p) < 15) and int(fan_first_p) != 0:
                    fan_first_p = "15"
                
                fan_array[0] = str(fan_first_l)        
            
                if fan_mode:
                    fan_array[1] = "M106 S" + str(round(int(fan_first_p) * 2.55))            
                else:
                    fan_array[1] = "M106 S" + str(round(int(fan_first_p) / 100, 1))

            fan_second = self.getSettingValueByKey("fan_second")
            if "/" in fan_second:
                fan_second_l = str(fan_second.split("/")[0])
                if int(fan_second_l) < 0: fan_second_l = "0"
                fan_second_p = str(fan_second.split("/")[1])
                if int(fan_second_p) < 0: fan_second_p = "0"
                if int(fan_second_p) > 100: fan_second_p = "100"
                if (fan_second_l != "mt" and int(fan_second_p) < 15) and int(fan_second_p) != 0:
                    fan_second_p = "15"
                    
                fan_array[2] = str(fan_second_l)        
                
                if fan_mode:
                    fan_array[3] = "M106 S" + str(round(int(fan_second_p) * 2.55))
                
                else:
                    fan_array[3] = "M106 S" + str(round(int(fan_second_p) / 100, 1))

            fan_third = self.getSettingValueByKey("fan_third")
            if "/" in fan_third:
                fan_third_l = str(fan_third.split("/")[0])
                if int(fan_third_l) < 0: fan_third_l = "0"
                fan_third_p = str(fan_third.split("/")[1])
                if int(fan_third_p) < 0: fan_third_p = "0"
                if int(fan_third_p) > 100: fan_third_p = "100"
                if (fan_third_l != "mt" and int(fan_third_p) < 15) and int(fan_third_p) != 0:
                    fan_third_p = "15"
                    
                fan_array[4] = str(fan_third_l)
                
                if fan_mode:
                    fan_array[5] = "M106 S" + str(round(int(fan_third_p) * 2.55))
                
                else:
                    fan_array[5] = "M106 S" + str(round(int(fan_third_p) / 100, 1))

            fan_fourth = self.getSettingValueByKey("fan_fourth")
            if "/" in fan_fourth:
                fan_fourth_l = str(fan_fourth.split("/")[0])
                if int(fan_fourth_l) < 0: fan_fourth_l = "0"
                fan_fourth_p = str(fan_fourth.split("/")[1])
                if int(fan_fourth_p) < 0: fan_fourth_p = "0"
                if int(fan_fourth_p) > 100: fan_fourth_p = "100"
                if (fan_fourth_l != "mt" and int(fan_fourth_p) < 15) and int(fan_fourth_p) != 0:
                    fan_fourth_p = "15"
                    
                fan_array[6] = str(fan_fourth_l)
                
                if fan_mode:
                    fan_array[7] = "M106 S" + str(round(int(fan_fourth_p) * 2.55))
                
                else:
                    fan_array[7] = "M106 S" + str(round(int(fan_fourth_p) / 100, 1))

            fan_fifth = self.getSettingValueByKey("fan_fifth")
            if "/" in fan_fifth:
                fan_fifth_l = str(fan_fifth.split("/")[0])
                if int(fan_fifth_l) < 0: fan_fifth_l = "0"
                fan_fifth_p = str(fan_fifth.split("/")[1])
                if int(fan_fifth_p) < 0: fan_fifth_p = "0"
                if int(fan_fifth_p) > 100: fan_fifth_p = "100"
                if (fan_fifth_l != "mt" and int(fan_fifth_p) < 15) and int(fan_fifth_p) != 0:
                    fan_fifth_p = "15"
                    
                fan_array[8] = str(fan_fifth_l)
                
                if fan_mode:
                    fan_array[9] = "M106 S" + str(round(int(fan_fifth_p) * 2.55))
                
                else:
                    fan_array[9] = "M106 S" + str(round(int(fan_fifth_p) / 100, 1))

            fan_sixth = self.getSettingValueByKey("fan_sixth")
            if "/" in fan_sixth:
                fan_sixth_l = str(fan_sixth.split("/")[0])
                if int(fan_sixth_l) < 0: fan_sixth_l = "0"
                fan_sixth_p = str(fan_sixth.split("/")[1])
                if int(fan_sixth_p) < 0: fan_sixth_p = "0"
                if int(fan_sixth_p) > 100: fan_sixth_p = "100"
                if (fan_sixth_l != "mt" and int(fan_sixth_p) < 15) and int(fan_sixth_p) != 0:
                    fan_sixth_p = "15"
                    
                fan_array[10] = str(fan_sixth_l)
                
                if fan_mode:
                    fan_array[11] = "M106 S" + str(round(int(fan_sixth_p) * 2.55))
                
                else:
                    fan_array[11] = "M106 S" + str(round(int(fan_sixth_p) / 100, 1))

            fan_seventh = self.getSettingValueByKey("fan_seventh")
            if "/" in fan_seventh:
                fan_seventh_l = str(fan_seventh.split("/")[0])
                if int(fan_seventh_l) < 0: fan_seventh_l = "0"
                fan_seventh_p = str(fan_seventh.split("/")[1])
                if int(fan_seventh_p) < 0: fan_seventh_p = "0"
                if int(fan_seventh_p) > 100: fan_seventh_p = "100"
                if (fan_seventh_l != "mt" and int(fan_seventh_p) < 15) and int(fan_seventh_p) != 0:
                    fan_seventh_p = "15"
                    
                fan_array[12] = str(fan_seventh_l)
                
                if fan_mode:
                    fan_array[13] = "M106 S" + str(round(int(fan_seventh_p) * 2.55))
                
                else:
                    fan_array[13] = "M106 S" + str(round(int(fan_seventh_p) / 100, 1))

            fan_eighth = self.getSettingValueByKey("fan_eighth")
            if "/" in fan_eighth:
                fan_eighth_l = str(fan_eighth.split("/")[0])
                if int(fan_eighth_l) < 0: fan_eighth_l = "0"
                fan_eighth_p = str(fan_eighth.split("/")[1])
                if int(fan_eighth_p) < 0: fan_eighth_p = "0"
                if int(fan_eighth_p) > 100: fan_eighth_p = "100"
                if (fan_eighth_l != "mt" and int(fan_eighth_p) < 15) and int(fan_eighth_p) != 0:
                    fan_eighth_p = "15"
                    
                fan_array[14] = str(fan_eighth_l)
                
                if fan_mode:
                    fan_array[15] = "M106 S" + str(round(int(fan_eighth_p) * 2.55))
                
                else:
                    fan_array[15] = "M106 S" + str(round(int(fan_eighth_p) / 100, 1))

            fan_ninth = self.getSettingValueByKey("fan_ninth")
            if "/" in fan_ninth:
                fan_ninth_l = str(fan_ninth.split("/")[0])
                if int(fan_ninth_l) < 0: fan_ninth_l = "0"
                fan_ninth_p = str(fan_ninth.split("/")[1])
                if int(fan_ninth_p) < 0: fan_ninth_p = "0"
                if int(fan_ninth_p) > 100: fan_ninth_p = "100"
                if (fan_ninth_l != "mt" and int(fan_ninth_p) < 15) and int(fan_ninth_p) != 0:
                    fan_ninth_p = "15"
                    
                fan_array[16] = str(fan_ninth_l)
                
                if fan_mode:
                    fan_array[17] = "M106 S" + str(round(int(fan_ninth_p) * 2.55))
                
                else:
                    fan_array[17] = "M106 S" + str(round(int(fan_ninth_p) / 100, 1))

            fan_tenth = self.getSettingValueByKey("fan_tenth")
            if "/" in fan_tenth:
                fan_tenth_l = str(fan_tenth.split("/")[0])
                if int(fan_tenth_l) < 0: fan_tenth_l = "0"
                fan_tenth_p = str(fan_tenth.split("/")[1])
                if int(fan_tenth_p) < 0: fan_tenth_p = "0"
                if int(fan_tenth_p) > 100: fan_tenth_p = "100"
                if (fan_tenth_l != "mt" and int(fan_tenth_p) < 15) and int(fan_tenth_p) != 0:
                    fan_tenth_p = "15"
                    
                fan_array[18] = str(fan_tenth_l)
                
                if fan_mode:
                    fan_array[19] = "M106 S" + str(round(int(fan_tenth_p) * 2.55))
                
                else:
                    fan_array[19] = "M106 S" + str(round(int(fan_tenth_p) / 100, 1))

            fan_eleventh = self.getSettingValueByKey("fan_eleventh")
            if "/" in fan_eleventh:
                fan_eleventh_l = str(fan_eleventh.split("/")[0])
                if int(fan_eleventh_l) < 0: fan_eleventh_l = "0"
                fan_eleventh_p = str(fan_eleventh.split("/")[1])
                if int(fan_eleventh_p) < 0: fan_eleventh_p = "0"
                if int(fan_eleventh_p) > 100: fan_eleventh_p = "100"
                if (fan_eleventh_l != "mt" and int(fan_eleventh_p) < 15) and int(fan_eleventh_p) != 0:
                    fan_eleventh_p = "15"
                    
                fan_array[20] = str(fan_eleventh_l)
                
                if fan_mode:
                    fan_array[21] = "M106 S" + str(round(int(fan_eleventh_p) * 2.55))
                
                else:
                    fan_array[21] = "M106 S" + str(round(int(fan_eleventh_p) / 100, 1))

            fan_twelfth = self.getSettingValueByKey("fan_twelfth")
            if "/" in fan_twelfth:
                fan_twelfth_l = str(fan_twelfth.split("/")[0])
                if int(fan_twelfth_l) < 0: fan_twelfth_l = "0"
                fan_twelfth_p = str(fan_twelfth.split("/")[1])
                if int(fan_twelfth_p) < 0: fan_twelfth_p = "0"
                if int(fan_twelfth_p) > 100: fan_twelfth_p = "100"
                if (fan_twelfth_l != "mt" and int(fan_twelfth_p) < 15) and int(fan_twelfth_p) != 0:
                    fan_twelfth_p = "15"
                    
                fan_array[22] = str(fan_twelfth_l)
                
                if fan_mode:
                    fan_array[23] = "M106 S" + str(round(int(fan_twelfth_p) * 2.55))
                
                else:
                    fan_array[23] = "M106 S" + str(round(int(fan_twelfth_p) / 100, 1))
                              
        elif by_layer_or_feature == "by_feature":    #Get the variables for the feature speeds and the start and the end layers  
            the_start_layer = int(self.getSettingValueByKey("fan_start_layer"))
            the_end_layer = int(self.getSettingValueByKey("fan_end_layer"))
            fan_skirt = int(self.getSettingValueByKey("fan_skirt"))
            if fan_mode:
                fan_sp_skirt = "M106 S" + str(round(fan_skirt * 2.55))
            else:
                fan_sp_skirt = "M106 S" + str(round(fan_skirt / 100, 1))

            fan_wall_inner = self.getSettingValueByKey("fan_wall_inner")
            if fan_mode:
                fan_sp_wall_inner = "M106 S" + str(round(fan_wall_inner * 2.55))
            else:
                fan_sp_wall_inner = "M106 S" + str(round(fan_wall_inner / 100, 1))

            fan_wall_outer = self.getSettingValueByKey("fan_wall_outer")
            if fan_mode:
                fan_sp_wall_outer = "M106 S" + str(round(fan_wall_outer * 2.55))
            else:
                fan_sp_wall_outer = "M106 S" + str(round(fan_wall_outer / 100, 1))

            fan_fill = self.getSettingValueByKey("fan_fill")
            if fan_mode:
                fan_sp_fill = "M106 S" + str(round(fan_fill * 2.55))
            else:
                fan_sp_fill = "M106 S" + str(round(fan_fill / 100, 1))

            fan_skin = self.getSettingValueByKey("fan_skin")
            if fan_mode:
                fan_sp_skin = "M106 S" + str(round(fan_skin * 2.55))
            else:
                fan_sp_skin = "M106 S" + str(round(fan_skin / 100, 1))

            fan_support = self.getSettingValueByKey("fan_support")
            if fan_mode:
                fan_sp_support = "M106 S" + str(round(fan_support * 2.55))
            else:
                fan_sp_support = "M106 S" + str(round(fan_support / 100, 1))

            fan_support_interface = self.getSettingValueByKey("fan_support_interface")
            if fan_mode:
                fan_sp_support_interface = "M106 S" + str(round(fan_support_interface * 2.55))
            else:
                fan_sp_support_interface = "M106 S" + str(round(fan_support_interface / 100, 1))

            fan_prime_tower = self.getSettingValueByKey("fan_prime_tower")
            if fan_mode:
                fan_sp_prime_tower = "M106 S" + str(round(fan_prime_tower * 2.55))
            else:
                fan_sp_prime_tower = "M106 S" + str(round(fan_prime_tower / 100, 1))

            fan_bridge = self.getSettingValueByKey("fan_bridge")
            if fan_mode:
                fan_sp_bridge = "M106 S" + str(round(fan_bridge * 2.55))
            else:
                fan_sp_bridge = "M106 S" + str(round(fan_bridge / 100, 1))

            fan_feature_final = self.getSettingValueByKey("fan_feature_final")
            if fan_mode:
                fan_sp_feature_final = "M106 S" + str(round(fan_feature_final * 2.55))
            else:
                fan_sp_feature_final = "M106 S" + str(round(fan_feature_final / 100, 1))

            if the_end_layer > -1 and by_layer_or_feature == "by_feature":
                the_end_is_enabled = True
            else:
                the_end_is_enabled = False

            if the_end_layer == -1 or the_end_is_enabled == False:
                the_end_layer = 9999999999
        
        layer_number = 0
        # supress every M106 present in the Gcode
        for layer in data:
            modified_data = ""
            index = data.index(layer)
            lines = layer.split("\n")            
            for line in lines:
                if not line.startswith("M106"):
                    modified_data += line 
                    modified_data += "\n"
            # Supress the last "\n"
            if modified_data.endswith("\n") :
                modified_data = modified_data[0:len(modified_data)-2]
            data[index] = modified_data

        if by_layer_or_feature == "by_layer":
            layer_number=0
            for layer in data:
                index = data.index(layer)
                fan_lines = layer.split("\n")
                for fan_line in fan_lines:
                    if ";LAYER:" in fan_line:
                        layer_number = int(fan_line.split(":")[1])
                        index = data.index(layer)
                        for num in range(0,23,2):
                            if layer_number == int(fan_array[num]):
                                layer = fan_array[num + 1] + "\n" + layer
                                data[index] = layer
                                
        if by_layer_or_feature == "by_feature":
            layer_number=0
            for layer in data:
                modified_data = ""
                index = data.index(layer)
                Logger.log('d', 'Index : {}'.format(index)) 
                lines = layer.split("\n")
                
                for line in lines:
                    modified_data += line + "\n"
                    if line.startswith(";LAYER:") :
                        index = data.index(layer)
                        layer_number = int(line.split(":")[1])
                        Logger.log('d', 'layer_number : {}'.format(layer_number)) 
                    if layer_number >= the_start_layer and layer_number < the_end_layer:
                        if line.startswith(";TYPE:SKIRT") :
                            modified_data += fan_sp_skirt + "\n"
                        elif line.startswith(";TYPE:WALL-INNER") :
                            modified_data += fan_sp_wall_inner + "\n"
                        elif line.startswith(";TYPE:WALL-OUTER") :
                            modified_data += fan_sp_wall_outer + "\n"
                        elif line.startswith(";TYPE:FILL") :
                            modified_data += fan_sp_fill + "\n"
                        elif line.startswith(";TYPE:SKIN") :
                            modified_data += fan_sp_skin + "\n"
                        elif line.startswith(";TYPE:SUPPORT") :
                            modified_data += fan_sp_support + "\n"
                        elif line.startswith(";TYPE:SUPPORT-INTERFACE") :
                            modified_data += fan_sp_support_interface + "\n"
                        elif line.startswith(";TYPE:PRIME-TOWER") :
                            modified_data += fan_sp_prime_tower + "\n"
                        elif line.startswith(";TYPE:BRIDGE") :
                            modified_data += fan_sp_bridge + "\n"
                        elif layer_number == the_end_layer and the_end_is_enabled == True:
                            modified_data += fan_sp_feature_final + "\n"
                        elif line.startswith(";End of Gcode") :
                            modified_data += "M106 S0" + "\n"
                # Supress the last "\n"
                if modified_data.endswith("\n") :
                    modified_data = modified_data[0:len(modified_data)-2]                
                data[index] = modified_data
                
        
        return data