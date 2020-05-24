# Cura PostProcessingPlugin
# Author:   5axes
# Date:     Mars 06 2020
# Modification :     Mars 07 2020
#                    Ajout de l'intégration du fichier RepRapPrintInfos.txt pour image impression
# https://3dprinter.sindoh.com/fr/support/downloads/3dwox1
# Modification :     25/05/2020  add thumbnail_gcode
# Description:  Ajout des infos pour machine RepRap machine 3DWOX

from ..Script import Script


from cura.CuraApplication import CuraApplication
from cura.Snapshot import Snapshot
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QImage
from typing import List

from UM.Logger import Logger
from UM.Message import Message

import string
import os
import textwrap

class RepRapPrintInfos(Script):

    GCODE_LINE_PREFIX = "; "
    GCODE_LINE_WIDTH = 80
    
    def __init__(self):
        super().__init__()

    def _image_to_byte_array(self, image) -> QByteArray:
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, 'png')
        buffer.close()
        return byte_array 

    def _image_to_base64(self, image) -> QByteArray:
        ba = self._image_to_byte_array(image)
        ba64 = ba.toBase64()
        return ba64

    def _txt_to_gcode(self, txt) -> str:
        wrapper = textwrap.TextWrapper(width=self.GCODE_LINE_WIDTH)
        Display_txt = wrapper.fill(txt)
        lines = Display_txt.split("\n")
        _Final_Txt=""
        _Counter = Display_txt.count('\n')+1
        for currentLine in lines:
            line_index = lines.index(currentLine)+1           
            _Final_Txt += ";IMAGE[%d/%d]  %s\n" % (line_index, _Counter, currentLine)
            
        return _Final_Txt
        
    def _create_snapshot(self, width, height):
        # must be called from the main thread because of OpenGL
        Logger.log("d", "Creating thumbnail image...")
        try:
            snapshot = Snapshot.snapshot(width = width, height = height)
            return snapshot
        except Exception:
            Logger.logException("w", "Failed to create snapshot image")
            return None

    def _create_thumbnail_gcode(self, width, height) -> str:
        min_size = min(width,height)
        tmp_snapshot = self._create_snapshot(min_size, min_size)
         # Scale it to the correct size
        if (width != height):
            snapshot = tmp_snapshot.copy(int((min_size-width)/2), int((min_size-height)/2), width, height)
        else:
            snapshot = tmp_snapshot

        ba64 = self._image_to_base64(snapshot)
        b64str = str(ba64, 'utf-8')
        b64gcode = self._txt_to_gcode(b64str)
        gcode = "\n" + self.GCODE_LINE_PREFIX + "\n" + \
            self.GCODE_LINE_PREFIX + "thumbnail begin " + str(width) + "x" + str(height) + " " + str(len(b64str)) + "\n" + \
            b64gcode + "\n" + \
            self.GCODE_LINE_PREFIX + "thumbnail end\n" + self.GCODE_LINE_PREFIX + "\n"

        return gcode
        
    def getSettingDataString(self):
        return """{
            "name": "Add 3DWOX Print Infos",
            "key": "RepRapPrintInfos",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "LayerId":
                {
                    "label": "Utilisation Layer Id G-Code",
                    "description": "Utilise le Layer Id codé dans le fichier G-Code. A utiliser pour impression pièce à pièce",
                    "type": "bool",
                    "default_value": false
                },
                "thumbnail_width":
                {
                    "label": "Thumbnail Width",
                    "description": "Width of the thumbnail",
                    "unit": "pixels",
                    "type": "int",
                    "default_value": 47,
                    "minimum_value": "16",
                    "minimum_value_warning": "16"
                },
                "thumbnail_height":
                {
                    "label": "Thumbnail Height",
                    "description": "Height of the thumbnail",
                    "unit": "pixels",
                    "type": "int",
                    "default_value": 47,
                    "minimum_value": "16",
                    "minimum_value_warning": "16"
                }
            }
        }"""
    
    def execute(self, data):
        max_layer = 0
        total_time = 0
        part = 0
        total_time_string = ""
        total_time_s=0
        current_time_s=0
        current_time_string = ""
        MCode = "M532"
        # Init variable pour éviter erreur si code non présent ou ordre différent
        min_x=0
        min_y=0
        min_z=0
        max_x=0
        max_y=0
        max_z=0
        percent=0
        
        thumbnail_width = self.getSettingValueByKey("thumbnail_width")
        thumbnail_height = self.getSettingValueByKey("thumbnail_height")

        
        
        Id = 1
        for layer in data:
            display_text = MCode + " L" + str(Id) 
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                line_index = lines.index(line)

                if line.startswith(";FLAVOR:"):
                    Logger.log("d", "Adding thumbnail image, resolution=" + str(thumbnail_width) + "x" + str(thumbnail_height))
                    thumbnail_gcode = self._create_thumbnail_gcode(thumbnail_width, thumbnail_height)
                    tablines = thumbnail_gcode.split("\n")
                    Ind=1
                    for Cline in tablines:
                        lines.insert(line_index + Ind, Cline)
                        Ind += 1


                if line.startswith(";MINX:"):
                    min_x = float(line.split(":")[1])   # Recuperation MINX
                if line.startswith(";MINY:"):
                    min_y = float(line.split(":")[1])   # Recuperation MINY
                if line.startswith(";MINZ:"):
                    min_z = float(line.split(":")[1])   # Recuperation MINZ
                if line.startswith(";MAXX:"):
                    max_x = float(line.split(":")[1])   # Recuperation MAXX
                if line.startswith(";MAXY:"):
                    max_y = float(line.split(":")[1])   # Recuperation MAXY
                if line.startswith(";MAXZ:"):
                    max_z = float(line.split(":")[1])   # Recuperation MAXZ

                    dimension_string = "{:05.1f}:{:05.1f}:{:05.1f}".format((max_x-min_x), (max_y-min_y), max_z)
                    display_text = ";DIMENSION: [" + dimension_string + "]"
                    lines.insert(line_index + 1, display_text)

                if line.startswith(";Filament used:"):
                    Filament = line.split(":")[1]   # Recuperation Filament used:
                    Filament = Filament.split("m")[0]
                    
                    Filament_Used=float(Filament)
                    Filament_MM=Filament_Used*1000
                    
                    display_text = ";ESTIMATION_FILAMENT: [" + str(int(Filament_MM))  + "]"
                    lines.insert(line_index + 1, display_text)
                    
                if line.startswith(";LAYER_COUNT:"):
                    max_layer = line.split(":")[1]   # Recuperation Nb Layer Maxi
                    display_text = ";TOTAL_LAYER: ["+ str(max_layer) + "]"
                    lines.insert(line_index + 1, display_text)

                # ECRITURE  M532    
                if line.startswith(";LAYER:"):
                    # Logger.log('d', 'X Pourcentage : {}'.format(percent))
                    percent_string = " X{:d}".format(int(percent))
                    display_text = MCode + percent_string + " L" + str(Id)
                        
                    lines.insert(line_index + 1, display_text)      # Insert du code M532 apres les layers
                    
                    if self.getSettingValueByKey("LayerId"):
                        Id = int(line.split(":")[1])                # Utilise le Layer dans G-Code ;LAYER:1
                        if Id == 0:
                            part += 1                               # Incrémente le numero de pièce       
                        Id += 1
                    else:
                        Id += 1                                     # Incrémente le numero de Layer (sans utiliser celui du Gcode)
                        
                if line.startswith(";TIME:"):
                    total_time = int(line.split(":")[1])
                    m, s = divmod(total_time, 60)    # Decomposition en
                    h, m = divmod(m, 60)             # heures, minutes et secondes
                    total_time_string = "{:04d}:{:02d}:{:02d}".format(int(h), int(m), int(s))
                    total_time_s= (h*3600)+(m*60)+s
                    current_time_string = total_time_string
                    display_text = ";ESTIMATION_TIME: [" + total_time_string  + "]"
                    lines.insert(line_index + 1, display_text)

                    
                elif line.startswith(";TIME_ELAPSED:"):
                    current_time = float(line.split(":")[1])
                    m1, s1 = divmod(current_time, 60)       # Decomposition en
                    h1, m1 = divmod(m1, 60)                 # heures, minutes et secondes
                    current_time_s= (h1*3600)+(m1*60)+s1
                    if total_time_s>0 :
                        percent=(current_time_s/total_time_s)*100
                    if percent>100 :
                        percent=100 
                    current_time_string = "{:04d}:{:04d}:{:02d}".format(int(h1), int(m1), int(s1))
                    # Logger.log('d', 'Pourcentage : {}'.format(percent))
                    
            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
            
        return data
