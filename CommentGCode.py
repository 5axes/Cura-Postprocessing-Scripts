
# Copyright (c) 2019 Lisa Erlingheuser
# This Cura PostProcessing-Script is released under the terms of the AGPLv3 or higher.

# This Cura Postprocessing Script adds comments to the G-Code.
# The user can select or deselect comments for M-Commands and G-Commands separately.

# G0 and G1 commands are only commented if a retract is included.

# Command, description and parameters are read from a CSV file. If a command is not contained, the required data is determined once via the website http://marlinfw.org/docs/gcode/
# and added to the CSV file.

import re #To perform the search and replace.
import string
import os
import urllib.request

from UM.Logger import Logger
from UM.Message import Message
from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

from ..Script import Script


class CommentGCode(Script):

    def getSettingDataString(self):
        return """{
            "name": "Comment G Code",
            "key": "CommentGCode",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "is_MCmd":
                {
                    "label": "M-Commands",
                    "description": "When enabled, M-Commands will be commented.",
                    "type": "bool",
                    "default_value": true
                },
                "is_GCmd":
                {
                    "label": "G-Commands",
                    "description": "When enabled, G-Commands will be commented, except G0 and G1.",
                    "type": "bool",
                    "default_value": true
                }
            }
        }"""

    def getVar(self):
        global bM, bG
        if hasattr(self, 'getSettingValueByKey'):
            bM = self.getSettingValueByKey("is_MCmd")
            bG = self.getSettingValueByKey("is_GCmd")
        else:
            bM = True
            bG = True
        return 
        
    def getCmdParamTab(self, cmdparam):  
        arret = []
        #Logger.log('d', "CommentGCode --> " + 'getCmdParamTab cmdparam: ' + str(cmdparam))
        for cp in cmdparam:
            if cp == '':
                break
            arp = cp.split("-")
            var1 = arp[0].strip()
            var1 = var1.strip('[')
            arp[0] = var1.split('<')[0]
            arp[1] = arp[1].strip()
            arret.append(arp)
        return arret
        
    def getCmdDescP(self, param, cmdparam):        
        arcmd = self.getCmdParamTab(cmdparam)
        ret = ''
        for lp in param:
            for cp in arcmd:
                if lp[0] == cp[0]:
                    if ret != '':
                        ret = ret + ", "
                    ret = ret + str(cp[1]) + '=' + str(lp[1:])                  
        return ret
        
    def _restmit(self, data, text):
        ret = data[data.index(text):]
        return ret
        
    def _restbisohne(self, data, text):
        try:
            ret = data[0:data.index(text)]
        except:
            ret = ""
        return ret
        
    def _restbismit(self, data, text):
        ret = data[0:data.index(text)+len(text)+1]
        return ret
        
    def _restohne(self, data, text):
        try:
            ret = data[data.index(text)+ len(text):]
        except:
            ret = ""
        return ret

        
    def getCmdDescFromHTML(self, htmlData, cmd):
        desc = None
        param = None    
        erg = htmlData
        erg = self._restmit(erg, '<h1>')
        desc = self._restbisohne(erg, "</h1>")
        desc = self._restohne(desc, "-")
        desc = desc.strip()
        retlist = [cmd, desc]
        erg = self._restmit(erg, "<h3>Parameters</h3>")
        erg = self._restmit(erg, "<table ")
        erg = self._restbismit(erg, "</table")
        table = erg.split("<tr>")
        for line in table:
            line = line.replace("&lt;", "<")
            line = line.replace("&gt;", ">")
            p = self._restohne(line, "<code>")
            if p != "":
                p = self._restbisohne(p, "</code>")
                p = p.strip()
                d = self._restohne(line, "<p>")
                d = self._restbisohne(d, "</p>")
                if '.' in d:
                    d = self._restbisohne(d, ".")
                d = d.strip()
                retlist.append(p + " - " + d)
        ret  = ";".join(retlist)
        #Logger.log('d', "CommentGCode --> " + 'getCmdDescFromHTML ret: ' + ret)
        return ret
        
    def getCmdDescUrl(self, cmd):
        result = None
        cmdB = cmd[0]
        cmdI = cmd[1:]
        scmdI = "%03i" % int(cmdI)
        url = "http://marlinfw.org/docs/gcode/" + cmdB + scmdI + ".html"
        #Logger.log('d', "CommentGCode --> " + 'getCmdDescUrl URL: ' + url)
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            result = response.read().decode("utf-8")
            #Logger.log('d', "CommentGCode --> " + 'getCmdDescUrl result: ' + str(result))
        except URLError:
            Logger.log('w', "CommentGCode --> " + 'getCmdDescUrl Error')
            return
        return result
        

    def getCmdDesc(self, cmd, cmdplist):
        global cmdtab, _msg
        cmddesc = ''
        cmdp = ''
        line = ""
        bgef = False
        if cmdtab == None:
            cmddir = os.path.join( os.path.dirname(__file__), 'Cura_GCode.CSV')            
            cmdges = open(cmddir).read()            
            tablines = cmdges.split("\n")
        if cmd + ";" not in cmdges:
            cmdhtml = self.getCmdDescUrl(cmd)
            if cmdhtml != None:
                newline = self.getCmdDescFromHTML(cmdhtml, cmd)
                #Logger.log('d', "CommentGCode --> " + 'getCmdDesc newline: ' + str(newline))
                cmdges += newline
                tablines = cmdges.split("\n")
                try:
                    fobj_out = open(cmddir,'w')
                    fobj_out.write(cmdges)
                    fobj_out.close()
                except:
                    pass 
        for line in tablines:
            cols = line.split(";")
            if cols[0] == cmd:
                bgef = True
                if len(cols) > 1 :
                    cmddesc = cols[1]
                    if len(cols) > 2:
                        cmddp = cols[2:]
                        if cmdplist != []:
                            cmdp = self.getCmdDescP(cmdplist, cmddp)
                    if cmdp != '':
                        cmddesc = cmddesc + ', ' + cmdp
        if bgef == False:
            _msg += 'Command ' +  str(cmd) + ' missing in G-Code file' + '\n'           
        return cmddesc
        
    def addCmd(self, line, cmd, cmdplist):
        desc = self.getCmdDesc(cmd, cmdplist)
        if desc != '':
            line = line + '; --> ' + desc
        return line

    def execute(self, data):
        global bM, bG, bShort, _msg
        global cmdtab
        _msg = ''
        cmdtab = None
        self.getVar()
        lastE = 0
        lineNo = 0
            
        for layer_number, layer in enumerate(data):
            lines = layer.split("\n")
            i1  = 0
            for line in lines:
                lineNo = lineNo +1
                if line != '':
                    if not ';' in line:
                        arline = line.split(' ') 
                        cmd = arline[0]
                        if cmd[0] == 'G':
                            if cmd != 'G1' and cmd != 'G0':
                                if bG == True:
                                    line = self.addCmd(line, cmd, arline[1:])
                            else:
                                actE = Script.getValue(self, line = line, key = 'E')                                
                                if actE != None:
                                    actE = float(actE)
                                    if actE < lastE:
                                        retract = actE - lastE
                                        line = line + '; --> Retract ' + str(round(retract, 2)) + ' mm'
                                        if i1 > 0:
                                            print(' line ' + str(lineNo-1) + ' : ' + lines[i1-1])
                                            print(' line ' + str(lineNo) + ' : ' + line)
                                        else:
                                            print(' line ' + str(lineNo) + ' : ' + line)
                                    lastE = actE
                            if cmd == 'G92':
                                lastE = Script.getValue(self, line = line, key = 'E')
                            if cmd == 'G91':
                                lastE = 0
                        elif cmd[0] == 'M':
                            if bM == True:
                                line = self.addCmd(line, cmd, arline[1:])
                        elif cmd[0] == 'T':
                                line = line + '; --> Activation Extruder ' + cmd[1]
                lines[i1] = line
                i1 = i1 + 1
            sep = '\n'        
            data[layer_number] = sep.join(lines)
        if _msg != None and _msg != '':
            Message("Info Comment G-Code:" + "\n" + _msg, title = catalog.i18nc("@info:title", "Post Processing")).show()
        return data
