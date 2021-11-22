#
# Author : CCS86 
# Source initial :  https://forum.duet3d.com/topic/14994/f-r-auto-define-m557-mesh-bounds-from-gcode/5?_=1637506151764
# We have a single parameter (mesh spacing), and it parses the first layer gcode for min/max X and Y coordinates, and then replaces the M557 line in your start gcode.
# You must have a static mesh leveling command in your start gcode, like: M557 X0:200 Y0:200 S20
# This command wil be replace by the new M557 command based on the dimmension in the initial G-Code
#
# M557 : https://reprap.org/wiki/G-code#M557:_Set_Z_probe_point_or_define_probing_grid
#

import re

from ..Script import Script

class LevelingMeshOptimizer(Script):
    def getSettingDataString(self):
        return """{
            "name": "Leveling Mesh Optimizer",
            "key": "LevelingMeshOptimizer",
            "metadata": {},
            "version": 2,
            "settings": {
                "spacing": {
                    "label": "Spacing",
                    "description": "How far apart to space the probe points within the mesh",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 10
                }
            }
        }"""


    ##  Calculates and fills in the bounds of the first layer.
    #   \param data A list of lines of GCODE representing the entire print.
    #   \return A similar list, with the bounds of the mesh filled in.
    def execute(self, data: [str]) -> [str]:
        _DATA_START_GCODE = 1
        _DATA_LAYER_0 = 2

        # Calculate bounds of first layer
        bounds = self.findBounds(data[_DATA_LAYER_0])

        # Fill in bounds in start GCODE
        data[_DATA_START_GCODE] = self.fillBounds(data[_DATA_START_GCODE], bounds)

        return data


    ##  Finds the minimum and maximum X and Y coordinates in a GCODE layer.
    #   \param data A block of GCODE representing the layer.
    #   \return A dict such that [X|Y][min|max] resolves to a float
    def findBounds(self, data: str) -> {str: {str: float}}:
        bounds = {
            "X": {"min": float("inf"), "max": float("-inf")},
            "Y": {"min": float("inf"), "max": float("-inf")},
        }

        for line in data.split("\n"):
            # Get coordinates on this line
            for match in re.findall(r"([XY])([\d.]+)\s", line):
                # Get axis letter
                axis = match[0]

                # Skip axes we don't care about
                if axis not in bounds:
                    continue

                # Parse parameter value
                value = float(match[1])

                # Update bounds
                bounds[axis]["min"] = round(min(bounds[axis]["min"], value),0)
                bounds[axis]["max"] = round(max(bounds[axis]["max"], value),0)

        return bounds


    ##  Replaces the M557 command in the start GCODE so that the bounds are filled in.
    #   \param data The entire start GCODE block.
    #   \return The same GCODE but with the bounds of the mesh filled in.
    def fillBounds(self, data: str, bounds: {str: {str: float}}) -> str:
        # Fill in the level command template
        new_cmd = "M557 X%.1f:%.1f Y%.1f:%.1f S%.1f ; Leveling mesh defined by LevelingMeshOptimizer" % (
            bounds["X"]["min"]-1, bounds["X"]["max"],
            bounds["Y"]["min"]-1, bounds["Y"]["max"],
            self.getSettingValueByKey("spacing"),
        )

        # Replace M557 command in GCODE
        return re.sub(r"^M557 .*$", new_cmd, data, flags=re.MULTILINE)