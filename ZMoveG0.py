# ZMoveG0
"""
ZMoveG0 for 3D prints.

Z hop for every G0

Author: 5axes
Version: 1.0
Version: 1.1  Remove some useless part of the Code.

"""

import re #To perform the search

from ..Script import Script

from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message
from UM.i18n import i18nCatalog

catalog = i18nCatalog("cura")

__version__ = '1.1'
       
class ZMoveG0(Script):
    def getSettingDataString(self):
        return """{
            "name": "Z Move G0",
            "key": "ZMoveG0",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "extruder_nb":
                {
                    "label": "Extruder Id",
                    "description": "Define extruder Id in case of multi extruders",
                    "unit": "",
                    "type": "int",
                    "default_value": 1
                }
            }
        }"""

## -----------------------------------------------------------------------------
#
#  Main Prog
#
## -----------------------------------------------------------------------------

    def execute(self, data):

        current_z = 0
        Zr = "Z0"
        Zc = "Z0"
        
        extruder_id  = self.getSettingValueByKey("extruder_nb")
        extruder_id = extruder_id -1

        #   machine_extruder_count
        extruder_count=Application.getInstance().getGlobalContainerStack().getProperty("machine_extruder_count", "value")
        extruder_count = extruder_count-1
        if extruder_id>extruder_count :
            extruder_id=extruder_count

        extrud = Application.getInstance().getGlobalContainerStack().extruderList
 
        retraction_hop = float(extrud[extruder_id].getProperty("retraction_hop", "value"))
        speed_z_hop = int(extrud[extruder_id].getProperty("speed_z_hop", "value"))
        speed_z_hop = speed_z_hop * 60

        retraction_hop_enabled= extrud[extruder_id].getProperty("retraction_hop_enabled", "value")
        if retraction_hop_enabled == True:
            #
            Logger.log('d', 'Mode Z Hop must not be activated')
            Message(catalog.i18nc("@message", "Mode Z Hop must not be activated"), title = catalog.i18nc("@info:title", "Post Processing")).show()
            return data
            
        In_G0 = False
        for layer_index, layer in enumerate(data):
            lines = layer.split("\n")
            
            for line_index, currentLine in enumerate(lines):

                if currentLine.startswith("G0") and "Z" in currentLine :
                    searchZ = re.search(r"Z(\d*\.?\d*)", currentLine)
                    if searchZ:
                        current_z=float(searchZ.group(1))
                        Zc = "Z"+searchZ.group(1)


                if currentLine.startswith("G0") and not In_G0 :
                    Output_Z=current_z+retraction_hop
                    outPutLine1 = "G1 F{} Z{:.3f}\n".format(speed_z_hop,Output_Z)
                    # Logger.log('d', "Zc Zr : {} {}".format(Zc,Zr))
                    Zr = "Z{:.3f}".format(Output_Z)    
                    currentLine=currentLine.replace(Zc, Zr)
                    outPutLine = outPutLine1 + currentLine 
                    lines[line_index] = outPutLine
                    In_G0 = True
                
                if currentLine.startswith("G1") and In_G0 :  
                    outPutLine2 = "G1 F{} Z{:.3f}\n".format(speed_z_hop,current_z)                
                    outPutLine = outPutLine2 + currentLine
                    lines[line_index] = outPutLine
                    In_G0 = False
                #
                # end of analyse
                #

            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
        return data
