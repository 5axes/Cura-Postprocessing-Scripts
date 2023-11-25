# Copyright (c) 2019 5axes
#
# Description:  This Script add Parameters description in the Header of the G-Code file...
#               Please look at the option
#               - Advanced_desc : Advanced description
#               - extruder_nb   : Specify the extruder nb information to output in case of multi-extruder 
#                                   you must use as many script as you have some exturder on your machine
#               - Position      : Position of the Texte in the ISo File : 1 = First line , 2 second line etc ...
#
# Version 1.01 of 20/10/2019 Who  : 5axes What : Addition of the names of the parameters with the label
# Version 1.02 of 21/10/2019 Who  : 5axes What : Addition of new parameters
# Version 1.03 of 21/10/2019 Who  : 5axes What : Info on material and profile + quality
# Version 2.00 of 21/10/2019 Who  : 5axes What : Start adding option Advanced settings
# Version 2.01 of 22/10/2019 Who  : 5axes What : Add option Extruder ID
# Version 2.02 of 22/10/2019 Who  : 5axes What : Adding new options in advanced mode
# Version 2.03 of 24/10/2019 Who  : 5axes What : Add new options hull / speed and meshfix
# Version 2.04 of 24/10/2019 Who  : 5axes What : Add CuraVersion
# Version 2.05 of 24/10/2019 Who  : 5axes What : Display parameter Extruder and not Global
# Version 2.06 of 25/10/2019 Who  : 5axes What : Reduction of base parameter list and addition of retraction distance in base parameter
# Version 3.01 of 07/01/2020 Who  : 5axes What : Switch to subroutine to lighten the code
# Version 4.01 of 15/01/2020 Who  : 5axes What : Version without Search and Replace, added to the Xth line (Option)
# Version 4.02 of 16/01/2020 Who  : 5axes What : Addition and double extrusion test
# Version 5.00 of 07/03/2020 Who  : 5axes What : Add info Number of slower layers (speed_slowdown_layers)
# Version 5.01 of 07/03/2020 Who  : 5axes What : Add info since 4.4 meshfix_maximum_resolution / meshfix_maximum_travel_resolution / meshfix_maximum_deviation
# Version 5.02 of 07/03/2020 Who  : 5axes What : Introduce retraction on Travel
# Version 5.03 of 07/04/2020 Who  : 5axes What : Add line width info
# Version 5.04 of 07/05/2020 Who  : 5axes What : Adding support flow info and info on xy_offset (Version 4.6) 
# Version 5.1.0 of 09/05/2020 Who : 5axes What : Add message for 4.6
# Version 5.2.0 of 13/02/2022 Who : 5axes What : New Settings
# Version 5.4.0 of 13/07/2023 Who : 5axes What : Update for 5.4
#
#
import string
from ..Script import Script
from UM.Application import Application # To get the current printer's settings.
from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Message import Message
from UM.Logger import Logger
from UM.i18n import i18nCatalog # Translation
catalog = i18nCatalog("cura")
        
## 
class GCodeDocumentation(Script):
    version = "5.4.0"
    
    def getSettingDataString(self):
        return """{
            "name": "GCode Documentation",
            "key": "GCodeDocumentation",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "advanced_desc":
                {
                    "label": "Advanced description",
                    "description": "Select for avdvanced description",
                    "type": "bool",
                    "default_value": false
                },
                "extruder_nb":
                {
                    "label": "Extruder Id",
                    "description": "Define extruder Id in case of multi extruders",
                    "unit": "",
                    "type": "int",
                    "default_value": 1
                },
                "position":
                {
                    "label": "Position code",
                    "description": "Specify the code position in the Gcode",
                    "type": "int",
                    "default_value": 1
                }
            }
        }"""

#   Définition des espaces pour aligner le texte
#   Définir avec Dec le décalage en espace
    def SetSpace(self,key,dec=0):
        dec_line = " " * int(dec)
        string_val = dec_line + str(key)
        new_line = "\n; " + '{:55}'.format(string_val) + ": "
        return new_line

    def SetSect(self,key):
        new_line = "\n;" + '{:-^78}'.format(str(key))
        return new_line

# Get de value and Label and format the text
    def GetDataExtruder(self,id_ex,key,dec=0):
        
        # Deprecation Warning
        # extrud = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        # extrud = Application.getInstance().getGlobalContainerStack().extruderList
        extrud = Application.getInstance().getExtruderManager().getActiveExtruderStacks()
        
        GetVal = extrud[id_ex].getProperty(key, "value")
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty(key, "label")
        GetType = Application.getInstance().getGlobalContainerStack().getProperty(key, "type")
        GetUnit = Application.getInstance().getGlobalContainerStack().getProperty(key, "unit")

        # Format le texte
        new_line = self.SetSpace(GetLabel,dec)
        if GetUnit:
            if str(GetType)=='float':
                GelValStr="{:.2f}".format(GetVal).replace(".00", "")  # Formatage
            else:
                GelValStr=str(GetVal)
            ## some characters, like 40°C and 800mm/s² aren't ascii-encodable and cause errors
            # filter(lambda x: x in string.printable, GetUnit)
            new_line = new_line + GelValStr + " " + str(GetUnit)
            
        else:
            if str(GetType)=='bool':
                new_line = new_line + "[" + str(GetVal) + "]"
            else:
                new_line = new_line + str(GetVal)
                
        return new_line
    
    
    def execute(self, data):
        pos_insert = int(self.getSettingValueByKey("position"))
        adv_desc = self.getSettingValueByKey("advanced_desc")
        extruder_id  = self.getSettingValueByKey("extruder_nb")
        extruder_id = extruder_id -1
        extrud = Application.getInstance().getGlobalContainerStack().extruderList
        _msg = ''
        VersC=1.0


        # Test version for futur release 4.9
        if "master" in CuraVersion or "beta" in CuraVersion or "BETA" in CuraVersion:
            # Master is always a developement version.
            Major=4
            Minor=9

        else:
            try:
                Major = int(CuraVersion.split(".")[0])
                Minor = int(CuraVersion.split(".")[1])
            except:
                pass
        
        Logger.log('d', "Info G-Code Documentation --> " + str(Major) + " / " + str(Minor))
        
        
        # test depuis 3.6
        if Major < 4 and Minor < 6 :
            _msg = "Attention Version Cura " + str(CuraVersion)
        
        if _msg != None and _msg != '':
            Message("Info G-Code Documentation :" + "\n" + _msg, title = catalog.i18nc("@info:title", "Post Processing")).show()

        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count

        replace_string = ";==============================================================================="
        replace_string = replace_string + "\n;  Documentation"
        if extruder_count>0:
            replace_string = replace_string + " extruder : " + str(extruder_id+1)
        replace_string = replace_string + "\n;==============================================================================="
        
        # add extruder specific data to slice info
        # extruders = list(Application.getInstance().getGlobalContainerStack().extruders.values())
        extruders = Application.getInstance().getExtruderManager().getActiveExtruderStacks()
        
        #   Profile
        GetValStr = extruders[extruder_id].qualityChanges.getMetaData().get("name", "")
        GetLabel = "Profile ( Version Cura " + CuraVersion + " )"
        replace_string = replace_string + self.SetSpace(GetLabel) + GetValStr
        #   Quality
        GetValStr = extruders[extruder_id].quality.getMetaData().get("name", "")
        GetLabel = "Quality"
        replace_string = replace_string + self.SetSpace(GetLabel) + GetValStr        
        #   Material
        GetValStr = extruders[extruder_id].material.getMetaData().get("material", "")
        GetLabel = "Material"
        replace_string = replace_string + self.SetSpace(GetLabel) + GetValStr
        #   material_diameter 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_diameter")       
        #   machine_nozzle_size
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"machine_nozzle_size")

        #   -----------------------------------  resolution ----------------------------- 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("resolution", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)
        
        #   layer_height
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"layer_height")
        #   layer_height_0
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"layer_height_0")          
        #   line_width
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"line_width") 
        #   wall_line_width_0 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"wall_line_width_0")   
        #   wall_line_width_x 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"wall_line_width_x")             
        #   initial_layer_line_width_factor 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"initial_layer_line_width_factor")

        #   -----------------------------------  shell ----------------------------- 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("shell", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        #   wall_thickness 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"wall_thickness")
        #   wall_line_count 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"wall_line_count",10)
        #   wall_0_wipe_dist
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"wall_0_wipe_dist")  
        #   xy_offset
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"xy_offset")   
        #   xy_offset_layer_0 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"xy_offset_layer_0")  
        #   hole_xy_offset 
        if adv_desc :
            if Major > 4 or ( Major == 4 and Minor >= 6 ) :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"hole_xy_offset")  
        #   z_seam_type 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"z_seam_type")
        #   z_seam_corner 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"z_seam_corner")  
        #   outer_inset_first
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"outer_inset_first")
        #   travel_compensate_overlapping_walls_enabled
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"travel_compensate_overlapping_walls_enabled")
        #   fill_perimeter_gaps 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"fill_perimeter_gaps")
        #   fill_outline_gaps
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"fill_outline_gaps")

        #   -----------------------------------  top_bottom -----------------------------
        if Major > 4 or ( Major == 4 and Minor >= 9 ) :
            GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("top_bottom", "label") 
            if adv_desc :
                replace_string = replace_string + self.SetSect(GetLabel)
            
        #   top_layers
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"top_layers",10)
        #   bottom_layers
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"bottom_layers",10)
        #   top_bottom_pattern 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"top_bottom_pattern")    
        #   skin_monotonic
        if adv_desc :
            if Major > 4 or ( Major == 4 and Minor >= 9 ) :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"skin_monotonic")
        #   ironing_enabled
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"ironing_enabled")
        ironing_enabled = bool(extrud[extruder_id].getProperty("ironing_enabled", "value"))
        
        if adv_desc and ironing_enabled :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"ironing_pattern") 
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"ironing_only_highest_layer") 
       
        if adv_desc :
            if Major > 4 or ( Major == 4 and Minor >= 9 ) :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"ironing_monotonic")
        
        #   -----------------------------------  infill ------------------------------ 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("infill", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        #   infill_sparse_density 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"infill_sparse_density")
        #   infill_pattern
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"infill_pattern")
        #   infill_overlap
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"infill_overlap")        
        #   gradual_infill_steps
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"gradual_infill_steps")
            
        #   ------------------------------------  material ------------------------------- 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("material", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)
        #   material_flow 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_flow")
        #   material_flow_layer_0
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_flow_layer_0")
        #   support_material_flow
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_material_flow")            

        #   material_print_temperature 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_print_temperature")
        #   material_print_temperature_layer_0
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_print_temperature_layer_0")
        #   material_bed_temperature
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_bed_temperature")
        #   material_bed_temperature_layer_0
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"material_bed_temperature_layer_0")

        #   ------------------------------------  speed ------------------------------ 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("speed", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        #   speed_print 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_print")
        #   speed_infill 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_infill")       
        #   speed_wall 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_wall",5)        
        #   speed_wall_0 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_wall_0",10)        
        #   speed_wall_x 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_wall_x",10)        
        #   speed_topbottom 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_topbottom",5)         
        #   speed_support 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_support",5)
        #   speed_layer_0 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_layer_0")        
        #   skirt_brim_speed 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"skirt_brim_speed")
        #   speed_slowdown_layers
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"speed_slowdown_layers")
        #   acceleration_enabled
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"acceleration_enabled")
        #   acceleration_print 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"acceleration_print",10)
        #   acceleration_travel 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"acceleration_travel",10)
        #   jerk_enabled 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"jerk_enabled")
        #   jerk_print 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"jerk_print",10)           
            
        #   -----------------------------------  travel ----------------------------- 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("travel", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        # Changement depuis 4.5
        #   retraction_enable 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"retraction_enable")
        #   retract_at_layer_change
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"retract_at_layer_change")        
        #   retraction_amount 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"retraction_amount")
        #   retraction_speed 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"retraction_speed")
        
        #   retraction_combing
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"retraction_combing")
        #   travel_retract_before_outer_wall
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"travel_retract_before_outer_wall",20)
        #   travel_avoid_other_parts
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"travel_avoid_other_parts",20)
        #   travel_avoid_supports
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"travel_avoid_supports",20)
        #   travel_avoid_distance
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"travel_avoid_distance",20)                                                                                                
        #   retraction_hop_enabled
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"retraction_hop_enabled",20)  
        #   retraction_hop
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"retraction_hop",20)
            
        #   -----------------------------------  cooling ----------------------------- 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("cooling", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        #   cool_fan_enabled
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_fan_enabled")           
        #   cool_fan_speed
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_fan_speed")    
        #   cool_fan_speed_0
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_fan_speed_0") 		
        #   cool_fan_full_layer
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_fan_full_layer")
        #   cool_min_layer_time
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_min_layer_time")
        #   cool_min_speed
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_min_speed")      
        #   cool_lift_head
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"cool_lift_head")
            
        #   -----------------------------------  support ------------------------------ 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("support", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)
            
        #   support_enable 
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_enable")
        
        #   support_structure
        support_structure=Application.getInstance().getGlobalContainerStack().getProperty("support_structure", "value")
        Logger.log('d', "Info G-Code Documentation support_structure --> " + str(support_structure))
        
        if Major > 4 or ( Major == 4 and Minor >= 8 ) :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_structure")
 
        #   support_tree_enable 
        if Major < 4 or ( Major == 4 and Minor <= 9 ) : 
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_enable")

        #   support_angle
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_angle")
        #   support_type
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_type")        
        if support_structure == "tree" :
            if adv_desc :
                #   support_tree_angle
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_angle",5)
                #   support_tree_branch_diameter
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_branch_diameter",5)
                #   support_tree_branch_diameter_angle
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_branch_diameter_angle",5)
                if ( Major >= 5 and Minor >= 4 ) :
                    #   support_tree_max_diameter
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_max_diameter",5)
                    #   support_tree_angle_slow
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_angle_slow",5) 
                    #   support_tree_max_diameter_increase_by_merges_when_support_to_model
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_max_diameter_increase_by_merges_when_support_to_model",5) 
                    #   support_tree_min_height_to_model
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_min_height_to_model",5)  
                    #   support_tree_bp_diameter
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_bp_diameter",5)  
                    #   support_tree_top_rate
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_top_rate",5)  
                    #   support_tree_tip_diameter
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_tip_diameter",5)  
                    #   support_tree_limit_branch_reach
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_limit_branch_reach",5) 
                    #   support_tree_rest_preference
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_rest_preference",5)                 
                else:              
                    #   support_tree_branch_distance
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_branch_distance",5)
                    #   support_tree_branch_diameter
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_branch_diameter",5)
        #   support_pattern
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_pattern")
        #   support_connect_zigzags
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_connect_zigzags")                                                                                                
        #   support_infill_rate
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_infill_rate")
        #   support_wall_count
        #   support_brim_enable
        if adv_desc :
            if Major > 4 or ( Major == 4 and Minor >= 8 ) : 
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_wall_count")
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_brim_enable")
                
        #   support_z_distance
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_z_distance",5)
        #   support_xy_distance
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_xy_distance",5)        
        #   support_xy_overrides_z
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_xy_overrides_z",5)
        #   support_interface_enable
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_interface_enable")
        #   support_roof_enable
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_roof_enable")            
        #   support_interface_height
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_interface_height") 
        #   support_roof_height
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_roof_height") 
        #   support_interface_skip_height
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_interface_skip_height")
        #   support_interface_density
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_interface_density")            
        #   support_interface_pattern
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_interface_pattern")
                             

        #   -----------------------------------  platform_adhesion ----------------------------- 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("platform_adhesion", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)
            
        #   adhesion_type
        adhesion_type = Application.getInstance().getGlobalContainerStack().getProperty("adhesion_type", "value")
        replace_string = replace_string + self.GetDataExtruder(extruder_id,"adhesion_type")
        #   brim_width 
        if adv_desc :
            if adhesion_type == "brim" :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"brim_width")

        if adv_desc :
            if ( Major >= 5 and Minor >= 4 ) :
                if adhesion_type == "brim" :
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"brim_smart_ordering")
                            
        if adv_desc :
            if adhesion_type == "raft" :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"raft_surface_layers")
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"raft_base_thickness",3)
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"raft_base_line_width",3)
                
        #   skirt_gap / brim_gap
        if adv_desc :
            if Major > 4 or ( Major == 4 and Minor >= 8 ) :
                if adhesion_type == "skirt" :
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"skirt_gap")
                if adhesion_type == "brim" :
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"brim_gap")
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"brim_outside_only")
                    
        #   -----------------------------------  dual -----------------------------
        if extruder_count>0:
            GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("dual", "label")
            if adv_desc :
                replace_string = replace_string + self.SetSect(GetLabel)
            #   prime_tower_enable
            if adv_desc :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"prime_tower_enable")
            #   prime_tower_size
            if adv_desc :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"prime_tower_size",5)
            #   prime_tower_position_x
            if adv_desc :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"prime_tower_position_x",5)
            #   prime_tower_position_y
            if adv_desc :
                replace_string = replace_string + self.GetDataExtruder(extruder_id,"prime_tower_position_y",5)


        #   -----------------------------------  meshfix ------------------------------ 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("meshfix", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        #   meshfix_union_all
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"meshfix_union_all")
        #   meshfix_union_all_remove_holes
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"meshfix_union_all_remove_holes")
        #   meshfix_maximum_resolution 
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"meshfix_maximum_resolution")
        #   meshfix_maximum_travel_resolution
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"meshfix_maximum_travel_resolution")
        #   meshfix_maximum_deviation
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"meshfix_maximum_deviation")
            
        #   -----------------------------------  blackmagic ------------------------------ 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("blackmagic", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)

        #   print_sequence
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"print_sequence")
        #   magic_spiralize
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"magic_spiralize")

        #   -----------------------------------  experimental ------------------------------ 
        GetLabel = Application.getInstance().getGlobalContainerStack().getProperty("experimental", "label")
        if adv_desc :
            replace_string = replace_string + self.SetSect(GetLabel)
 
        #   support_tree_enable 
        if Major < 4 or ( Major == 4 and Minor <= 9 ) : 
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"support_tree_enable")
            
         #   skin_monotonic
        if adv_desc :
            if Major > 4 or ( Major == 4 and Minor >= 9 ) :
                skin_monotonic = bool(extrud[extruder_id].getProperty("skin_monotonic", "value"))
                if skin_monotonic :
                    replace_string = replace_string + self.GetDataExtruder(extruder_id,"roofing_monotonic")
        
        #   coasting_enable
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"coasting_enable")
        #   coasting_volume
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"coasting_volume",5)
        #   coasting_speed
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"coasting_speed",5)
        # adaptive_layer_height_enabled
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"adaptive_layer_height_enabled")
        #   adaptive_layer_height_variation
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"adaptive_layer_height_variation",5)
        #   adaptive_layer_height_variation_step
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"adaptive_layer_height_variation_step",5)
        #   bridge_settings_enabled
        if adv_desc :
            replace_string = replace_string + self.GetDataExtruder(extruder_id,"bridge_settings_enabled")

        #   Fin de commentaire 
        replace_string = replace_string + "\n;==============================================================================="

        # Ajoute en début de GCode les infos
        layer = data[0]
        layer_index = data.index(layer)
        lines = layer.split("\n")
        # Ajoute en deuxieme ligne
        lines.insert( pos_insert, replace_string)
        final_lines = "\n".join(lines)
        data[layer_index] = final_lines

        return data
   
