from ..Script import Script
import re

# from cura.Settings.ExtruderManager import ExtruderManager
# Issue History
# Vesrion 1.0 - Inital Release
# Version 2.0 - Fixed error with X and Y axis  directions
#.


class UPPostProcess(Script):

    def __init__(self):
        super().__init__()
        self.Ypattern = re.compile("Y\d+")
        self.Zpattern = re.compile("Z\d+")
        self.Xpattern = re.compile("X\d+")




    def getSettingDataString(self):
        return """{
            "name":"Up PostProcess",
            "key": "UpPostProcess",
            "metadata": {},
            "version": 2,
            "settings": {
                "UP_profile":
                {
                    "label": "Profile",
                    "description": "Convert CURA to UP gcode",
                    "type": "enum",
                    "options": {
                    "UP":"UP"
                    },
                    "default_value": "UP"
                },
                "UP_Zvalue":
                {
                    "label": "Z offset in Up Studio",
                    "description": " Z height when bed at nozzle",
                    "type": "float",
                    "default_value": 205
                }
            }
        }"""

    def execute(self, data: list):

        version = "0.1 C Jackson"

        self.UPProfile = self.getSettingValueByKey("UP_profile")
        self.UPZmax = self.getSettingValueByKey("UP_Zvalue")
        self.selectedTool = ""
        self.valveClosed = True

        index = 0
        for active_layer in data:

            self.output = ""
            #if index == 0:
            self.output += "; Selected profile: " + self.UPProfile + ", ZMax set at " + str(self.UPZmax)
            self.output += "; version " + version + "\n"

            lines = active_layer.split("\n")
            #self.output += "; Number of lines to be processed " + str(lines) +"\n"
            for line in lines:
                commentIndex = line.find(";")
                if commentIndex >= 0:
                    comment = line[commentIndex + 1:]
                    line = line[0:commentIndex]
                else:
                    comment = ""

                if self.UPProfile == "UP":
                    self.UPGcodeParse(line, comment)
                else:
                    self.output += ";" + "\n"

            data[index] = self.output
            index += 1
        return data
#
# End of Main Loop
#
    def UPGcodeParse(self, line, comment):

        hasY = re.search(self.Ypattern, line)
        hasZ = re.search(self.Zpattern, line)
        hasX = re.search(self.Xpattern, line)
        # There is 'Sxxx' in the line and second tool is selected and line doesn't contain both
        if hasX:
            line = line.replace("X","A")  # Replace "Sxxx" with "Txxx "
        if hasY:
            line = line.replace("Y","B")  # Replace "Sxxx" with "Txxx "
        line = line.replace("A","Y-")  # Replace "Sxxx" with "Txxx "
        line = line.replace("B","X")  # Replace "Sxxx" with "Txxx " 
        if hasZ:
        #CBJ Pseudo Code needs to find the Zvlaue on the line i.e. Z0.3
        #CBJ then subtract this value from the UPZvalue provide by the user e.g. 205
        #CBJ replace theZvalue in the line with UPZvalue - Zvalue e.g. 204.7 
             LayerZ = line.rpartition('Z')[-1]
             LayerZ = str(LayerZ)
             A = float(self.UPZmax)
             B = float(LayerZ)
             UPLayerZ = A-B
             UPLayerZ = str(UPLayerZ)
             line = line.partition('Z')[0] + "Z-" +UPLayerZ
        
        # Write the modifed line to file.
        if comment != "":
            self.output += line + ";" + comment + "\n"
        else:
            self.output += line + "\n"

