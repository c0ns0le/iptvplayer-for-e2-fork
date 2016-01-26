# -*- coding: utf-8 -*-
#
#from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import XXX
##### permanents
j00zekFork=True
PluginName = 'IPTVPlayer'
PluginGroup = 'Extensions'

##### System Imports
from os import path as os_path, environ as os_environ, listdir as os_listdir, chmod as os_chmod, remove as os_remove, mkdir as os_mkdir, system as os_system

###### openPLI imports
from Components.config import *
from Plugins.Extensions.IPTVPlayer.version import IPTV_VERSION
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG as printDEBUG
from Screens.Screen import Screen
from Tools.Directories import *

from Plugins.Extensions.IPTVPlayer.__init__ import _
# Plugin Paths
PluginFolder = PluginName
PluginPath = resolveFilename(SCOPE_PLUGINS, '%s/%s' %(PluginGroup,PluginFolder))
ExtPluginsPath = resolveFilename(SCOPE_PLUGINS, '%s/' %(PluginGroup))

# Update plugin console script
j00zekRunUpdateList = []
j00zekRunUpdateList.append( ('cp -a %s/j00zekScripts/UpdatePlugin.sh /tmp/PluginUpdate.sh' % PluginPath) ) #to have clear path of updating this script too ;)
j00zekRunUpdateList.append( ('chmod 755 /tmp/PluginUpdate.sh') )
j00zekRunUpdateList.append( ('/tmp/PluginUpdate.sh "%s"' % IPTV_VERSION) )
j00zekRunUpdateList.append( ('rm -f /tmp/PluginUpdate.sh') )
##################################################### LOAD SKIN DEFINITION #####################################################
def AlternateOptionsList(list):
        #we build our own order :)
    list.append( getConfigListEntry(_("Auto check for plugin update"), config.plugins.iptvplayer.autoCheckForUpdate) )
    list.append( getConfigListEntry(_("Update"), config.plugins.iptvplayer.fakeUpdate) )
    #
    list.append( getConfigListEntry(_("--- General options ---"), config.plugins.iptvplayer.j00zekSeparator))
    list.append( getConfigListEntry(_("Detected platform"), config.plugins.iptvplayer.plarform) )
    list.append( getConfigListEntry(_("Services configuration"), config.plugins.iptvplayer.fakeHostsList) )
    list.append( getConfigListEntry(_("Show IPTVPlayer in extension list"), config.plugins.iptvplayer.showinextensions))
    list.append( getConfigListEntry(_("Show IPTVPlayer in main menu"), config.plugins.iptvplayer.showinMainMenu))
    list.append( getConfigListEntry(_("Show update icon in service selection menu"), config.plugins.iptvplayer.AktualizacjaWmenu))
    list.append( getConfigListEntry(_("Enable hosts tree selector"), config.plugins.iptvplayer.j00zekTreeHostsSelector))
    if config.plugins.iptvplayer.j00zekTreeHostsSelector.value == True:
        list.append( getConfigListEntry(_("Use only hosts tree selector"), config.plugins.iptvplayer.j00zekTreeHostsSelectorOnly))
    else:
        list.append( getConfigListEntry(_("Graphic services selector"), config.plugins.iptvplayer.ListaGraficzna))
        if config.plugins.iptvplayer.ListaGraficzna.value == True:
            list.append( getConfigListEntry(_("    Service icon size"), config.plugins.iptvplayer.IconsSize))
            list.append( getConfigListEntry(_("    Number of rows"), config.plugins.iptvplayer.numOfRow))
            list.append( getConfigListEntry(_("    Number of columns"), config.plugins.iptvplayer.numOfCol))
    #
    list.append( getConfigListEntry("", config.plugins.iptvplayer.j00zekSeparator))
    list.append( getConfigListEntry(_("--- Paths to utilities ---"), config.plugins.iptvplayer.j00zekSeparator))
    list.append( getConfigListEntry(_("wgetpath"), config.plugins.iptvplayer.wgetpath))
    list.append( getConfigListEntry(_("rtmpdumppath"), config.plugins.iptvplayer.rtmpdumppath))
    list.append( getConfigListEntry(_("f4mdumppath"), config.plugins.iptvplayer.f4mdumppath))
    list.append( getConfigListEntry(_("uchardetpath"), config.plugins.iptvplayer.uchardetpath))
    list.append( getConfigListEntry(_("exteplayer3path"), config.plugins.iptvplayer.exteplayer3path))
    list.append( getConfigListEntry(_("gstplayerpath"), config.plugins.iptvplayer.gstplayerpath))
    #
    list.append( getConfigListEntry("", config.plugins.iptvplayer.j00zekSeparator))
    list.append( getConfigListEntry(_("--- Debug ---"), config.plugins.iptvplayer.j00zekSeparator))
    list.append( getConfigListEntry(_("Debug logs"), config.plugins.iptvplayer.debugprint))
    list.append( getConfigListEntry(_("Disable host protection (error == GS)"), config.plugins.iptvplayer.devHelper))
    #
    list.append( getConfigListEntry("", config.plugins.iptvplayer.j00zekSeparator))
    list.append( getConfigListEntry(_("--- Other IPTVPlayer Config options ---"), config.plugins.iptvplayer.j00zekSeparator))

##################################################### Noew configs definition #####################################################
def RemoveDuplicatesFromList(list):
        #make some options hidden
        myList=[]
        myList.append(config.plugins.iptvplayer.downgradePossible)
        myList.append(config.plugins.iptvplayer.possibleUpdateType)
        myList.append(config.plugins.iptvplayer.skin)
        
        for x in range(len(list)-1,0, -1):
            if list[x][1] in myList:
                list.pop(x)
        
        #remove duplicates
        myList=[]
        myIDs=[]
        for x in range(0, len(list)-1):
            if list[x][1] not in myList or list[x][1] is config.plugins.iptvplayer.j00zekSeparator:
                myIDs.append(x)
                myList.append(list[x][1])

        for x in range(len(list)-1,0, -1):
            if x not in myIDs:
                list.pop(x)

##################################################### Noew configs definition #####################################################
def ExtendConfigsList():
    config.plugins.iptvplayer.j00zekSeparator = NoSave(ConfigNothing())
    config.plugins.iptvplayer.j00zekTreeHostsSelector = ConfigYesNo(default = True)
    config.plugins.iptvplayer.j00zekTreeHostsSelectorOnly = ConfigYesNo(default = False)
    
    #setting default values, we do not need from original plugin
    config.plugins.iptvplayer.downgradePossible.value = False
    config.plugins.iptvplayer.possibleUpdateType.value = 'sourcecode'
    config.plugins.iptvplayer.deleteIcons.value = "0"
    
    config.plugins.iptvplayer.j00zekLastSelectedHost = NoSave(ConfigText(default = "", fixed_size = False))

##################################################### LOAD SKIN DEFINITION #####################################################
def LoadSkin(SkinName):
    from enigma import getDesktop
    model=''
    if os_path.exists("/proc/stb/info/vumodel"):
        with open("/proc/stb/info/vumodel", "r") as f:
            model=f.read().strip()
            f.close()
            
    if SkinName.endswith('.xml'):
        SkinName=SkinName[:-4]
    skinDef=None
    
    if getDesktop(0).size().width() == 1920 and os_path.exists("%s/skins/%s%sFHD.xml" % (PluginPath,SkinName,model)):
        with open("%s/skins/%s%sFHD.xml" % (PluginPath,SkinName,model),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif getDesktop(0).size().width() == 1920 and os_path.exists("%s/skins/%sFHD.xml" % (PluginPath,SkinName)):
        with open("%s/skins/%sFHD.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
            
    elif os_path.exists("%s/skins/%s%s.xml" % (PluginPath,SkinName,model)):
        with open("%s/skins/%s%s.xml" % (PluginPath,SkinName,model),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif os_path.exists("%s/skins/%s.xml" % (PluginPath,SkinName)):
        with open("%s/skins/%s.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    else:
        printDEBUG("[LoadSkin] %s does not exists" % SkinName )
    return skinDef

##################################################### CLEAR CACHE - tuners with small amount of memory need it #####################################################
def ClearMemory(): #avoid GS running os.* (e.g. os.system) on tuners with small amount of RAM
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
    
def isGraterlia():
    if path.exists('/etc/init.d/graterlia_init'):
        return True
    else:
        return False
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
##################################################### translated Console #####################################################
class translatedConsole(Screen):
#TODO move this to skin.xml
    skin = """
        <screen position="center,center" size="550,400" title="Updating ..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""
        
    def __init__(self, session, title = "j00zekIPTVPlayerConsole", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
        Screen.__init__(self, session)

        from enigma import eConsoleAppContainer
        from Components.ScrollLabel import ScrollLabel
        from Components.ActionMap import ActionMap
        from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
        
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.errorOcurred = False

        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
        {
            "ok": self.cancel,
            "back": self.cancel,
            "up": self["text"].pageUp,
            "down": self["text"].pageDown
        }, -1)
        
        self.cmdlist = cmdlist
        self.newtitle = title
        
        self.onShown.append(self.updateTitle)
        
        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self["text"].setText("" + "\n\n")
        print "TranslatedConsole: executing in run", self.run, " the command:", self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
            self.runFinished(-1) # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
                self.runFinished(-1) # so we must call runFinished manual
        else:
            #lastpage = self["text"].isAtLastPage()
            #str = self["text"].getText()
            #str += _("\nUse up/down arrows to scroll text. OK closes window");
            #self["text"].setText(str)
            #if lastpage:
            self["text"].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not self.errorOcurred and self.closeOnSuccess:
                self.cancel()

    def cancel(self):
        def rebootQuestionAnswered(ret):
            if ret:
                from enigma import quitMainloop
                quitMainloop(3)
            try: self.close()
            except: pass
            return
        if self.run == len(self.cmdlist):
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)
            if os_path.exists("/tmp/.rebootGUI"):
                from Screens.MessageBox import MessageBox
                self.session.openWithCallback(rebootQuestionAnswered, MessageBox,"Restart GUI now?",  type = MessageBox.TYPE_YESNO, timeout = 10, default = False)
            else:
                self.close()

    def dataAvail(self, str):
        #lastpage = self["text"].isAtLastPage()
        self["text"].setText(self["text"].getText() + self.translate(str))
        #if lastpage:
        self["text"].lastPage()
        
    def translate(self,txt):
        def substring_2_translate(text):
            to_translate = text.split('_(', 2)
            text = to_translate[1]
            to_translate = text.split(')', 2)
            text = to_translate[0]
            return text
    
        if txt.find('_(') == -1:
            txt = _(txt)
        else:
            index = 0
            while txt.find('_(') != -1:
                tmptxt = substring_2_translate(txt)
                translated_tmptxt = _(tmptxt)
                txt = txt.replace('_(' + tmptxt + ')', translated_tmptxt)
                index += 1
                if index == 10:
                    break
        return txt
j00zekIPTVPlayerConsole = translatedConsole
##################################################### List all categories #####################################################
def GetHostsCategories(myDir = PluginPath + '/hosts'):
    HostsCategories = []
    for CH in os_listdir(myDir):
        if os_path.isdir(os_path.join(myDir, CH)):
            HostsCategories.append((CH,CH))
    HostsCategories.sort()
    return HostsCategories
##################################################### assign/remove host from/to category #####################################################
def ManageHostsAndCategories(HostName, CategoryName = ''):
    printDEBUG("j00zekToolSet:ManageHostsAndCategories > HostName=%s,CategoryName=%s" %(HostName, CategoryName))
    ClearMemory()
    hostsDir='%s/hosts' % PluginPath
    categoryDir='%s/hosts/%s' % (PluginPath,CategoryName)
    #first delete, when exists
    if os_path.exists('%s/%s.py' %(categoryDir,HostName[:-4])) or os_path.exists('%s/%s' %(categoryDir,HostName)):
        print "Removing %s from category %s" % (HostName,CategoryName)
        os_system('rm -rf %s/%s*' % (categoryDir,HostName[:-4]) )
    #assign to category
    elif os_path.exists('%s/%s' %(hostsDir,HostName)):
        print "Assigning %s to category %s" % (HostName,CategoryName)
        os_system('ln -sf %s/%s %s/%s' % ( hostsDir, HostName, categoryDir, HostName) )
    else:
        print "unknown " + hostsDir + HostName
