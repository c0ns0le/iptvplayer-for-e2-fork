# -*- coding: utf-8 -*-
#
#from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import XXX
##### permanents
j00zekFork=True
PluginName = 'IPTVPlayer'
PluginGroup = 'Extensions'

##### System Imports
from os import path as os_path, environ as os_environ, listdir as os_listdir, chmod as os_chmod, remove as os_remove, mkdir as os_mkdir

###### openPLI imports
from Components.config import *
from Plugins.Extensions.IPTVPlayer.version import IPTV_VERSION
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG
from Screens.Screen import Screen
from Tools.Directories import *

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
        myConfig=config.plugins.iptvplayer
        #
        list.append(getConfigListEntry(_("--- General options ---"), myConfig.j00zekSeparator))
        list.append( getConfigListEntry(_("Detected platform"), myConfig.plarform) )
        list.append( getConfigListEntry(_("Services configuration"), myConfig.fakeHostsList) )
        list.append(getConfigListEntry(_("Show IPTVPlayer in extension list"), myConfig.showinextensions))
        list.append(getConfigListEntry(_("Show IPTVPlayer in main menu"), myConfig.showinMainMenu))
        list.append(getConfigListEntry(_("Show update icon in service selection menu"), myConfig.AktualizacjaWmenu))
        list.append(getConfigListEntry(_("Enable hosts tree selector"), myConfig.j00zekTreeHostsSelector))
        if myConfig.j00zekTreeHostsSelector.value == False:
            list.append(getConfigListEntry(_("Graphic services selector"), myConfig.ListaGraficzna))
            if myConfig.ListaGraficzna.value == True:
                list.append(getConfigListEntry(_("    Service icon size"), config.plugins.iptvplayer.IconsSize))
                list.append(getConfigListEntry(_("    Number of rows"), config.plugins.iptvplayer.numOfRow))
                list.append(getConfigListEntry(_("    Number of columns"), config.plugins.iptvplayer.numOfCol))
        #
        list.append(getConfigListEntry("", myConfig.j00zekSeparator))
        list.append(getConfigListEntry(_("--- Paths to utilities ---"), myConfig.j00zekSeparator))
        
        list.append(getConfigListEntry(_("VFD set current title:"), config.plugins.iptvplayer.set_curr_title))
        
        list.append(getConfigListEntry(_("Write current title to file:"), config.plugins.iptvplayer.curr_title_file))
        list.append(getConfigListEntry(_("External movie player default aspect ratio:"), config.plugins.iptvplayer.hidden_ext_player_def_aspect_ratio))
            
        
        list.append( getConfigListEntry(_("Auto check for plugin update"), config.plugins.iptvplayer.autoCheckForUpdate) )
        list.append( getConfigListEntry(_("Update"), config.plugins.iptvplayer.fakeUpdate) )
        list.append( getConfigListEntry(_("Disable live at plugin start"), config.plugins.iptvplayer.disable_live))
        list.append( getConfigListEntry(_("Pin protection for plugin"), config.plugins.iptvplayer.pluginProtectedByPin))
        list.append( getConfigListEntry(_("Pin protection for configuration"), config.plugins.iptvplayer.configProtectedByPin) )
        if config.plugins.iptvplayer.pluginProtectedByPin.value or config.plugins.iptvplayer.configProtectedByPin.value:
            list.append( getConfigListEntry(_("Set pin code"), config.plugins.iptvplayer.fakePin) )
        
        list.append(getConfigListEntry(_("Display thumbnails"), config.plugins.iptvplayer.showcover))
        #if config.plugins.iptvplayer.showcover.value:
            #list.append(getConfigListEntry(_("    Allowed formats of thumbnails"), config.plugins.iptvplayer.allowedcoverformats))
            #list.append(getConfigListEntry(_("    Remove thumbnails"), config.plugins.iptvplayer.deleteIcons))
        #list.append(getConfigListEntry("Sort lists?", config.plugins.iptvplayer.sortuj))            
        
        list.append(getConfigListEntry(_("https - validate SSL certificates"), config.plugins.iptvplayer.httpssslcertvalidation))
        list.append(getConfigListEntry(_("Polish proxy server url"), config.plugins.iptvplayer.proxyurl))
        list.append(getConfigListEntry(_("German proxy server url"), config.plugins.iptvplayer.german_proxyurl))
        
        list.append(getConfigListEntry(_("Folder for cache data"), config.plugins.iptvplayer.SciezkaCache))
        list.append(getConfigListEntry(_("Folder for temporary data"), config.plugins.iptvplayer.NaszaTMP))
        
        # BUFFERING
        list.append(getConfigListEntry(_("[HTTP] buffering"), config.plugins.iptvplayer.buforowanie))
        list.append(getConfigListEntry(_("[HLS/M3U8] buffering"), config.plugins.iptvplayer.buforowanie_m3u8))
        list.append(getConfigListEntry(_("[RTMP] buffering (rtmpdump required)"), config.plugins.iptvplayer.buforowanie_rtmp)) 
        
        if config.plugins.iptvplayer.buforowanie.value or config.plugins.iptvplayer.buforowanie_m3u8.value or config.plugins.iptvplayer.buforowanie_rtmp.value:
            list.append(getConfigListEntry(_("    Video buffer size [MB]"), config.plugins.iptvplayer.requestedBuffSize))
            list.append(getConfigListEntry(_("    Audio buffer size [KB]"), config.plugins.iptvplayer.requestedAudioBuffSize))
            list.append(getConfigListEntry(_("Buffer path"), config.plugins.iptvplayer.bufferingPath))
            
        list.append(getConfigListEntry(_("Records path"), config.plugins.iptvplayer.NaszaSciezka))           
        list.append(getConfigListEntry(_("Start download manager per default"), config.plugins.iptvplayer.IPTVDMRunAtStart))
        list.append(getConfigListEntry(_("Show download manager after adding new item"), config.plugins.iptvplayer.IPTVDMShowAfterAdd))
        list.append(getConfigListEntry(_("Number of downloaded files simultaneously"), config.plugins.iptvplayer.IPTVDMMaxDownloadItem))
        
        list.append(getConfigListEntry("opensubtitles.org " + _("login"), config.plugins.iptvplayer.opensuborg_login))
        list.append(getConfigListEntry("opensubtitles.org " + _("password"), config.plugins.iptvplayer.opensuborg_password))
        
        #list.append(getConfigListEntry("HD3D " + _("login"), config.plugins.iptvplayer.hd3d_login))
        #list.append(getConfigListEntry("HD3D " + _("password"), config.plugins.iptvplayer.hd3d_password))
        
        players = []
        bufferingMode = config.plugins.iptvplayer.buforowanie.value or config.plugins.iptvplayer.buforowanie_m3u8.value or config.plugins.iptvplayer.buforowanie_rtmp.value
        if 'sh4' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First move player without buffering mode"), config.plugins.iptvplayer.defaultSH4MoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultSH4MoviePlayer0)
            list.append(getConfigListEntry(_("Second move player without buffering mode"), config.plugins.iptvplayer.alternativeSH4MoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeSH4MoviePlayer0)
        
            list.append(getConfigListEntry(_("First move player in buffering mode"), config.plugins.iptvplayer.defaultSH4MoviePlayer))
            players.append(config.plugins.iptvplayer.defaultSH4MoviePlayer)
            list.append(getConfigListEntry(_("Second move player in buffering mode"), config.plugins.iptvplayer.alternativeSH4MoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeSH4MoviePlayer)
            
        elif 'mipsel' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First move player without buffering mode"), config.plugins.iptvplayer.defaultMIPSELMoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultMIPSELMoviePlayer0)
            list.append(getConfigListEntry(_("Second move player without buffering mode"), config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0)
            
            list.append(getConfigListEntry(_("First move player in buffering mode"), config.plugins.iptvplayer.defaultMIPSELMoviePlayer))
            players.append(config.plugins.iptvplayer.defaultMIPSELMoviePlayer)
            list.append(getConfigListEntry(_("Second move player in buffering mode"), config.plugins.iptvplayer.alternativeMIPSELMoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeMIPSELMoviePlayer)
            
        elif 'i686' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First move player without buffering mode"), config.plugins.iptvplayer.defaultI686MoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultI686MoviePlayer0)
            list.append(getConfigListEntry(_("Second move player without buffering mode"), config.plugins.iptvplayer.alternativeI686MoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeI686MoviePlayer0)
            
            list.append(getConfigListEntry(_("First move player in buffering mode"), config.plugins.iptvplayer.defaultI686MoviePlayer))
            players.append(config.plugins.iptvplayer.defaultI686MoviePlayer)
            list.append(getConfigListEntry(_("Second move player in buffering mode"), config.plugins.iptvplayer.alternativeI686MoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeI686MoviePlayer)
            
        else: 
            list.append(getConfigListEntry(_("Movie player"), config.plugins.iptvplayer.NaszPlayer))
        
        playersValues = [player.value for player in players]
        if 'exteplayer' in playersValues or 'extgstplayer' in playersValues or 'auto' in playersValues:
            list.append(getConfigListEntry(_("External movie player config"), config.plugins.iptvplayer.fakExtMoviePlayerList))
        
        list.append(getConfigListEntry(_("The number of items in the search history"), config.plugins.iptvplayer.search_history_size))
        list.append(getConfigListEntry(_("Block wmv files"), config.plugins.iptvplayer.ZablokujWMV))
        #
        list.append(getConfigListEntry("", myConfig.j00zekSeparator))
        list.append(getConfigListEntry(_("--- Paths to utilities ---"), myConfig.j00zekSeparator))
        list.append(getConfigListEntry("wgetpath", config.plugins.iptvplayer.wgetpath))
        list.append(getConfigListEntry("rtmpdumppath", config.plugins.iptvplayer.rtmpdumppath))
        list.append(getConfigListEntry("f4mdumppath", config.plugins.iptvplayer.f4mdumppath))
        list.append(getConfigListEntry("uchardetpath", config.plugins.iptvplayer.uchardetpath))
        list.append(getConfigListEntry("exteplayer3path", config.plugins.iptvplayer.exteplayer3path))
        list.append(getConfigListEntry("gstplayerpath", config.plugins.iptvplayer.gstplayerpath))
        #
        list.append(getConfigListEntry("", myConfig.j00zekSeparator))
        list.append(getConfigListEntry(_("--- Debug ---"), myConfig.j00zekSeparator))
        list.append(getConfigListEntry(_("Debug logs"), config.plugins.iptvplayer.debugprint))
        list.append(getConfigListEntry(_("Disable host protection (error == GS)"), config.plugins.iptvplayer.devHelper))

def ExtendConfigsList():
    myConfig=config.plugins.iptvplayer
    myConfig.j00zekSeparator = NoSave(ConfigNothing())
    myConfig.j00zekTreeHostsSelector = ConfigYesNo(default = True)
    
    #setting default values, we do not need from original plugin
    myConfig.downgradePossible.value = False
    myConfig.possibleUpdateType.value = 'sourcecode'
    myConfig.deleteIcons.value = "0"
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
##################################################### translated Console #####################################################
class j00zekIPTVPlayerConsole(Screen):
#TODO move this to skin.xml
    skin = """
        <screen name="j00zekIPTVPlayerConsole" position="center,center" size="550,400" title="Updating ..." >
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
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

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
