#
##### permanents
PluginName = 'IPTVPlayer'
PluginGroup = 'Extensions'

##### System Imports
from os import path as os_path, environ as os_environ, listdir as os_listdir, chmod as os_chmod, remove as os_remove, mkdir as os_mkdir

###### openPLI imports
from Tools.Directories import *
from Components.config import *
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG

# Plugin Paths
PluginFolder = PluginName
PluginPath = resolveFilename(SCOPE_PLUGINS, '%s/%s' %(PluginGroup,PluginFolder))
ExtPluginsPath = resolveFilename(SCOPE_PLUGINS, '%s/' %(PluginGroup))

##################################################### LOAD SKIN DEFINITION #####################################################
def LoadSkin(SkinName):
    from enigma import getDesktop
    
    if SkinName.endswith('.xml'):
        SkinName=SkinName[:-4]
    skinDef=None
    
    if getDesktop(0).size().width() == 1920 and os_path.exists("%s/skins/%sFHD.xml" % (PluginPath,SkinName) ):
        printDBG('LoadSkin %sFHD.xml' %SkinName )
        with open("%s/skins/%sFHD.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif os_path.exists("%s/skins/%s.xml" % (PluginPath,SkinName)):
        printDBG('LoadSkin %s.xml' %SkinName )
        with open("%s/skins/%s.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    else:
        printDBG('LoadSkin %s/skins/%s.xml not found!!!' % (PluginPath,SkinName) )
    return skinDef

##################################################### CLEAR CACHE - tuners with small amount of memory need it #####################################################
def ClearMemory(): #avoid GS running os.* (e.g. os.system) on tuners with small amount of RAM
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
    
##################################################### getPlatform #####################################################
def getPlatform():
    fc=''
    with open('/proc/cpuinfo', 'r') as f:
        fc=f.read()
        f.close()
    if fc.find('sh4') > -1:
        return 'sh4'
    elif fc.find('BMIPS') > -1:
        return 'mipsel'
    elif fc.find('GenuineIntel') > -1:
        return 'i686'
    elif fc.find('ARMv') > -1:
        return 'arm'
    else:
       return 'unknown'
##################################################### getPlatform #####################################################
