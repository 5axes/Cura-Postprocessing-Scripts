# Cura-Postprocessing-Scripts
Compilation of personnal Ultimaker Cura postprocessing scripts


Installation
--

The files must be stored in the user script directory of the respective Cura version: \AppData\Roaming\cura<version>\scripts

After the next start of Cura the script can be added via Extension / Post-Processing / Modify G-Code Add a script.

![Adding script](./images/plugins.jpg)


DisplayPrintInfosOnLCD.py
-----

Description:  This plugin shows custom messages about your print on the Printer Panel...
              Please look at the option
               - LayerId: Use the Layer ID coded in the Gcode and not an increment starting from 0
               
![DisplayPrintInfosOnLCD.py](./images/PrintInfos.jpg)

GCodeDocumentation.py
-----
Description: Add slicing paramter in the GCode Header

![GCodeDocumentation.py](./images/GcodeDocumentation.jpg)

SpeedTower.py
-----
Description:  postprocessing-script to easily define a Speed Tower.

![SpeedTower.py](./images/speedtower.jpg)

TempFanTower.py
-----

Description:  postprocessing-script to easily use an temptower and not use 10 changeAtZ-scripts

 The default values are for this temptower PLA model [https://www.thingiverse.com/thing:2493504](https://www.thingiverse.com/thing:2493504)
- Temp Tower PLA de 210 à 170

![TempFanTower.py](./images/tempfan.jpg)


ZMoveIroning.py
-----

Description: ZMoveIroning for 3D prints. Z hop for ironing

![ZMoveIroning.py](./images/ZmoveIroning.jpg)
