# -*- coding: utf-8 -*-
#
#  Konfigurator dla iptv 2013
#  autorzy: j00zek, samsamsam
#

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, GetSkinsList, GetHostsList, GetEnabledHostsList, \
                                                          IsHostEnabled, IsExecutable, CFakeMoviePlayerOption, GetAvailableIconSize, GetBinDir
from Plugins.Extensions.IPTVPlayer.iptvupdate.updatemainwindow import IPTVUpdateWindow, UpdateMainAppImpl
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, IPTVPlayerNeedInit
from Plugins.Extensions.IPTVPlayer.components.configbase import ConfigBaseWidget
from Plugins.Extensions.IPTVPlayer.components.confighost import ConfigHostsMenu
from Plugins.Extensions.IPTVPlayer.setup.iptvsetupwidget import IPTVSetupMainWidget
###################################################

###################################################
# FOREIGN import
###################################################
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigYesNo, ConfigOnOff, Config, ConfigInteger, ConfigSubList, ConfigText, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from Tools.BoundFunction import boundFunction
###################################################


###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer = ConfigSubsection()

from Plugins.Extensions.IPTVPlayer.components.configextmovieplayer import ConfigExtMoviePlayer

config.plugins.iptvplayer.exteplayer3path = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.gstplayerpath   = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.wgetpath        = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.rtmpdumppath    = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.f4mdumppath     = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.uchardetpath    = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.set_curr_title  = ConfigYesNo(default = False)
config.plugins.iptvplayer.curr_title_file = ConfigText(default = "", fixed_size = False) 
config.plugins.iptvplayer.plarform        = ConfigSelection(default = "auto", choices = [("auto", "auto"),("mipsel", _("mipsel")),("sh4", _("sh4")),("i686", _("i686")), ("armv7", _("armv7")),("arm", _("arm")),("unknown", _("unsupported"))])

config.plugins.iptvplayer.showcover          = ConfigYesNo(default = True)
config.plugins.iptvplayer.deleteIcons        = ConfigSelection(default = "3", choices = [("0", _("after closing")),("1", _("after day")),("3", _("after three days")),("7", _("after a week"))]) 
config.plugins.iptvplayer.allowedcoverformats= ConfigSelection(default = "jpeg,png", choices = [("jpeg,png,gif", _("jpeg,png,gif")),("jpeg,png", _("jpeg,png")),("jpeg", _("jpeg")),("all", _("all"))]) 
config.plugins.iptvplayer.showinextensions   = ConfigYesNo(default = True)
config.plugins.iptvplayer.showinMainMenu     = ConfigYesNo(default = False)
config.plugins.iptvplayer.ListaGraficzna     = ConfigYesNo(default = True)
config.plugins.iptvplayer.NaszaSciezka       = ConfigDirectory(default = "/hdd/movie/") #, fixed_size = False)
config.plugins.iptvplayer.bufferingPath      = ConfigDirectory(default = config.plugins.iptvplayer.NaszaSciezka.value) #, fixed_size = False)
config.plugins.iptvplayer.buforowanie        = ConfigYesNo(default = False)
config.plugins.iptvplayer.buforowanie_m3u8   = ConfigYesNo(default = True)
config.plugins.iptvplayer.buforowanie_rtmp   = ConfigYesNo(default = False)
config.plugins.iptvplayer.requestedBuffSize  = ConfigInteger(5, (1,120))
config.plugins.iptvplayer.requestedAudioBuffSize  = ConfigInteger(256, (1,10240))

config.plugins.iptvplayer.IPTVDMRunAtStart      = ConfigYesNo(default = False)
config.plugins.iptvplayer.IPTVDMShowAfterAdd    = ConfigYesNo(default = True)
config.plugins.iptvplayer.IPTVDMMaxDownloadItem = ConfigSelection(default = "1", choices = [("1", "1"),("2", "2"),("3", "3"),("4", "4")])

config.plugins.iptvplayer.AktualizacjaWmenu = ConfigYesNo(default = True)
config.plugins.iptvplayer.sortuj = ConfigYesNo(default = True)
config.plugins.iptvplayer.remove_diabled_hosts = ConfigYesNo(default = False)

def GetMoviePlayerName(player):
    map = {"auto":_("auto"), "mini": _("internal"), "standard":_("standard"), 'exteplayer': _("external eplayer3"), 'extgstplayer': _("external gstplayer")}
    return map.get(player, _('unknown'))
    
def ConfigPlayer(player):
    return (player, GetMoviePlayerName(player))

config.plugins.iptvplayer.NaszPlayer = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer('extgstplayer'), ConfigPlayer("standard")])

# without buffering mode
#sh4
config.plugins.iptvplayer.defaultSH4MoviePlayer0         = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('exteplayer'),ConfigPlayer('extgstplayer')]) 
config.plugins.iptvplayer.alternativeSH4MoviePlayer0     = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('exteplayer'),ConfigPlayer('extgstplayer')]) 

#mipsel
config.plugins.iptvplayer.defaultMIPSELMoviePlayer0      = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])
config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0  = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])

#i686
config.plugins.iptvplayer.defaultI686MoviePlayer0        = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])
config.plugins.iptvplayer.alternativeI686MoviePlayer0    = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])

#arm
config.plugins.iptvplayer.defaultARMMoviePlayer0        = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])
config.plugins.iptvplayer.alternativeARMMoviePlayer0    = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])
# end without buffering mode players

#armv7
config.plugins.iptvplayer.defaultARMV7MoviePlayer0      = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])
config.plugins.iptvplayer.alternativeARMV7MoviePlayer0  = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])

# with buffering mode
#sh4
config.plugins.iptvplayer.defaultSH4MoviePlayer         = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('exteplayer'),ConfigPlayer('extgstplayer')]) 
config.plugins.iptvplayer.alternativeSH4MoviePlayer     = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('exteplayer'),ConfigPlayer('extgstplayer')]) 

#mipsel
config.plugins.iptvplayer.defaultMIPSELMoviePlayer      = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])
config.plugins.iptvplayer.alternativeMIPSELMoviePlayer  = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])

#i686
config.plugins.iptvplayer.defaultI686MoviePlayer        = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])
config.plugins.iptvplayer.alternativeI686MoviePlayer    = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])

#armv7
config.plugins.iptvplayer.defaultARMV7MoviePlayer      = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])
config.plugins.iptvplayer.alternativeARMV7MoviePlayer  = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer'),ConfigPlayer('exteplayer')])
#arm
config.plugins.iptvplayer.defaultARMMoviePlayer        = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])
config.plugins.iptvplayer.alternativeARMMoviePlayer    = ConfigSelection(default = "auto", choices = [ConfigPlayer("auto"),ConfigPlayer("mini"),ConfigPlayer("standard"),ConfigPlayer('extgstplayer')])
# end with buffering mode players

config.plugins.iptvplayer.SciezkaCache = ConfigDirectory(default = "/hdd/IPTVCache/") #, fixed_size = False)
config.plugins.iptvplayer.NaszaTMP = ConfigDirectory(default = "/tmp/") #, fixed_size = False)
config.plugins.iptvplayer.ZablokujWMV = ConfigYesNo(default = True)

#config.plugins.iptvplayer.hd3d_login    = ConfigText(default="", fixed_size = False)
#config.plugins.iptvplayer.hd3d_password = ConfigText(default="", fixed_size = False)

config.plugins.iptvplayer.opensuborg_login    = ConfigText(default="", fixed_size = False)
config.plugins.iptvplayer.opensuborg_password = ConfigText(default="", fixed_size = False)

config.plugins.iptvplayer.debugprint = ConfigSelection(default = "", choices = [("", _("no")),("console", _("yes, to console")),("debugfile", _("yes, to file /hdd/iptv.dbg"))]) 

#icons
config.plugins.iptvplayer.IconsSize = ConfigSelection(default = "135", choices = [("135", "135x135"),("120", "120x120"),("100", "100x100")]) 
config.plugins.iptvplayer.numOfRow = ConfigSelection(default = "0", choices = [("1", "1"),("2", "2"),("3", "3"),("4", "4"),("0", "auto")])
config.plugins.iptvplayer.numOfCol = ConfigSelection(default = "0", choices = [("1", "1"),("2", "2"),("3", "3"),("4", "4"),("5", "5"),("6", "6"),("7", "7"),("8", "8"),("0", "auto")])

config.plugins.iptvplayer.skin = ConfigSelection(default = "Default", choices = GetSkinsList())

#Pin code
from iptvpin import IPTVPinWidget
config.plugins.iptvplayer.fakePin = ConfigSelection(default = "fake", choices = [("fake", "****")])
config.plugins.iptvplayer.pin = ConfigText(default = "0000", fixed_size = False)
config.plugins.iptvplayer.disable_live = ConfigYesNo(default = False)
config.plugins.iptvplayer.configProtectedByPin = ConfigYesNo(default = False)
config.plugins.iptvplayer.pluginProtectedByPin = ConfigYesNo(default = False)

config.plugins.iptvplayer.httpssslcertvalidation = ConfigYesNo(default = False)

#PROXY
config.plugins.iptvplayer.proxyurl = ConfigText(default = "http://PROXY_IP:PORT", fixed_size = False)
config.plugins.iptvplayer.german_proxyurl = ConfigText(default = "http://PROXY_IP:PORT", fixed_size = False)
config.plugins.iptvplayer.russian_proxyurl = ConfigText(default = "http://PROXY_IP:PORT", fixed_size = False)

# Update
config.plugins.iptvplayer.autoCheckForUpdate = ConfigYesNo(default = True)
config.plugins.iptvplayer.updateLastCheckedVersion = ConfigText(default = "00.00.00.00", fixed_size = False)
config.plugins.iptvplayer.fakeUpdate               = ConfigSelection(default = "fake", choices = [("fake", "  ")])
config.plugins.iptvplayer.downgradePossible        = ConfigYesNo(default = False)
config.plugins.iptvplayer.possibleUpdateType       = ConfigSelection(default = "precompiled", choices = [("sourcecode", _("with source code")),("precompiled", _("precompiled")), ("all", _("all types"))]) 

# Hosts lists
config.plugins.iptvplayer.fakeHostsList = ConfigSelection(default = "fake", choices = [("fake", "  ")])


# External movie player settings
config.plugins.iptvplayer.fakExtMoviePlayerList = ConfigSelection(default = "fake", choices = [("fake", "  ")])

# hidden options
config.plugins.iptvplayer.hiddenAllVersionInUpdate = ConfigYesNo(default = False)
config.plugins.iptvplayer.hidden_ext_player_def_aspect_ratio = ConfigSelection(default = "-1", choices = [("-1", _("default")), ("0", _("4:3 Letterbox")), ("1", _("4:3 PanScan")), ("2", _("16:9")), ("3", _("16:9 always")), ("4", _("16:10 Letterbox")), ("5", _("16:10 PanScan")), ("6", _("16:9 Letterbox"))] )
        
config.plugins.iptvplayer.search_history_size  = ConfigInteger(50, (0, 1000000))
config.plugins.iptvplayer.autoplay_start_delay  = ConfigInteger(3, (1, 1000000))

###################################################
j00zekFork=True
from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import AlternateOptionsList, ExtendConfigsList, RemoveDuplicatesFromList
ExtendConfigsList()
########################################################
# Generate list of hosts options for Enabling/Disabling
########################################################
class ConfigIPTVHostOnOff(ConfigOnOff):
    def __init__(self, default = False):
        ConfigOnOff.__init__(self, default = default)

gListOfHostsNames = GetHostsList()
for hostName in gListOfHostsNames:
    try:
        # as default all hosts are enabled
        if hostName in ['ipla']:
            enabledByDefault = 'False'
        else:
            enabledByDefault = 'True'
        exec('config.plugins.iptvplayer.host' + hostName + ' = ConfigIPTVHostOnOff(default = ' + enabledByDefault + ')')
    except:
        printExc(hostName)

###################################################

class ConfigMenu(ConfigBaseWidget):

    def __init__(self, session):
        printDBG("ConfigMenu.__init__ -------------------------------")
        self.list = [ ]
        ConfigBaseWidget.__init__(self, session)
        # remember old
        self.showcoverOld = config.plugins.iptvplayer.showcover.value
        self.SciezkaCacheOld = config.plugins.iptvplayer.SciezkaCache.value
        self.platformOld = config.plugins.iptvplayer.plarform.value
        self.remove_diabled_hostsOld = config.plugins.iptvplayer.remove_diabled_hosts.value
        self.enabledHostsListOld = GetEnabledHostsList()

    def __del__(self):
        printDBG("ConfigMenu.__del__ -------------------------------")
        
    def __onClose(self):
        printDBG("ConfigMenu.__onClose -----------------------------")
        ConfigBaseWidget.__onClose(self)

    def layoutFinished(self):
        ConfigBaseWidget.layoutFinished(self)
        self.setTitle(_("IPTV Player - settings"))
        
    @staticmethod
    def fillConfigList(list, hiddenOptions=False):
        if 'j00zekFork' in globals():
            AlternateOptionsList(list)
        if hiddenOptions:
            list.append( getConfigListEntry(_("Last checked version"), config.plugins.iptvplayer.updateLastCheckedVersion) )
            list.append( getConfigListEntry(_("Show all version in the update menu"), config.plugins.iptvplayer.hiddenAllVersionInUpdate) )
            list.append(getConfigListEntry(_("VFD set current title:"), config.plugins.iptvplayer.set_curr_title))
            list.append(getConfigListEntry(_("Write current title to file:"), config.plugins.iptvplayer.curr_title_file))
            list.append(getConfigListEntry(_("External movie player default aspect ratio:"), config.plugins.iptvplayer.hidden_ext_player_def_aspect_ratio))
            
            list.append(getConfigListEntry("exteplayer3path", config.plugins.iptvplayer.exteplayer3path))
            list.append(getConfigListEntry("gstplayerpath", config.plugins.iptvplayer.gstplayerpath))
            list.append(getConfigListEntry("wgetpath", config.plugins.iptvplayer.wgetpath))
            list.append(getConfigListEntry("rtmpdumppath", config.plugins.iptvplayer.rtmpdumppath))
            list.append(getConfigListEntry("f4mdumppath", config.plugins.iptvplayer.f4mdumppath))
            list.append(getConfigListEntry("uchardetpath", config.plugins.iptvplayer.uchardetpath))
        
        list.append( getConfigListEntry(_("Auto check for plugin update"), config.plugins.iptvplayer.autoCheckForUpdate) )
        list.append( getConfigListEntry(_("Update"), config.plugins.iptvplayer.fakeUpdate) )
        list.append( getConfigListEntry(_("Platform"), config.plugins.iptvplayer.plarform) )
        list.append( getConfigListEntry(_("Services configuration"), config.plugins.iptvplayer.fakeHostsList) )
        list.append( getConfigListEntry(_("Remove disabled services"), config.plugins.iptvplayer.remove_diabled_hosts) )
        list.append( getConfigListEntry(_("Disable live at plugin start"), config.plugins.iptvplayer.disable_live))
        list.append( getConfigListEntry(_("Pin protection for plugin"), config.plugins.iptvplayer.pluginProtectedByPin))
        list.append( getConfigListEntry(_("Pin protection for configuration"), config.plugins.iptvplayer.configProtectedByPin) )
        if config.plugins.iptvplayer.pluginProtectedByPin.value or config.plugins.iptvplayer.configProtectedByPin.value:
            list.append( getConfigListEntry(_("Set pin code"), config.plugins.iptvplayer.fakePin) )
        
        list.append(getConfigListEntry(_("Skin"), config.plugins.iptvplayer.skin))
        list.append(getConfigListEntry(_("Display thumbnails"), config.plugins.iptvplayer.showcover))
        if config.plugins.iptvplayer.showcover.value:
            list.append(getConfigListEntry(_("    Allowed formats of thumbnails"), config.plugins.iptvplayer.allowedcoverformats))
            list.append(getConfigListEntry(_("    Remove thumbnails"), config.plugins.iptvplayer.deleteIcons))
        #list.append(getConfigListEntry("Sortować listy?", config.plugins.iptvplayer.sortuj))            
        list.append(getConfigListEntry(_("Graphic services selector"), config.plugins.iptvplayer.ListaGraficzna))
        if config.plugins.iptvplayer.ListaGraficzna.value == True:
            list.append(getConfigListEntry(_("    Service icon size"), config.plugins.iptvplayer.IconsSize))
            list.append(getConfigListEntry(_("    Number of rows"), config.plugins.iptvplayer.numOfRow))
            list.append(getConfigListEntry(_("    Number of columns"), config.plugins.iptvplayer.numOfCol))
        
        list.append(getConfigListEntry(_("https - validate SSL certificates"), config.plugins.iptvplayer.httpssslcertvalidation))
        list.append(getConfigListEntry(_("Polish proxy server url"), config.plugins.iptvplayer.proxyurl))
        list.append(getConfigListEntry(_("German proxy server url"), config.plugins.iptvplayer.german_proxyurl))
        list.append(getConfigListEntry(_("Russian proxy server url"), config.plugins.iptvplayer.russian_proxyurl))
        
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
            list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.iptvplayer.defaultSH4MoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultSH4MoviePlayer0)
            list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.iptvplayer.alternativeSH4MoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeSH4MoviePlayer0)
        
            list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.iptvplayer.defaultSH4MoviePlayer))
            players.append(config.plugins.iptvplayer.defaultSH4MoviePlayer)
            list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.iptvplayer.alternativeSH4MoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeSH4MoviePlayer)
            
        elif 'mipsel' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.iptvplayer.defaultMIPSELMoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultMIPSELMoviePlayer0)
            list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0)
            
            list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.iptvplayer.defaultMIPSELMoviePlayer))
            players.append(config.plugins.iptvplayer.defaultMIPSELMoviePlayer)
            list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.iptvplayer.alternativeMIPSELMoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeMIPSELMoviePlayer)
            
        elif 'i686' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.iptvplayer.defaultI686MoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultI686MoviePlayer0)
            list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.iptvplayer.alternativeI686MoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeI686MoviePlayer0)
            
            list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.iptvplayer.defaultI686MoviePlayer))
            players.append(config.plugins.iptvplayer.defaultI686MoviePlayer)
            list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.iptvplayer.alternativeI686MoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeI686MoviePlayer)

        elif 'armv7' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.iptvplayer.defaultARMV7MoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultARMV7MoviePlayer0)
            list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.iptvplayer.alternativeARMV7MoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeARMV7MoviePlayer0)
            
            list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.iptvplayer.defaultARMV7MoviePlayer))
            players.append(config.plugins.iptvplayer.defaultARMV7MoviePlayer)
            list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.iptvplayer.alternativeARMV7MoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeARMV7MoviePlayer)
            
        elif 'arm' == config.plugins.iptvplayer.plarform.value:
            list.append(getConfigListEntry(_("First move player without buffering mode"), config.plugins.iptvplayer.defaultARMMoviePlayer0))
            players.append(config.plugins.iptvplayer.defaultARMMoviePlayer0)
            list.append(getConfigListEntry(_("Second move player without buffering mode"), config.plugins.iptvplayer.alternativeARMMoviePlayer0))
            players.append(config.plugins.iptvplayer.alternativeARMMoviePlayer0)
            
            list.append(getConfigListEntry(_("First move player in buffering mode"), config.plugins.iptvplayer.defaultARMMoviePlayer))
            players.append(config.plugins.iptvplayer.defaultARMMoviePlayer)
            list.append(getConfigListEntry(_("Second move player in buffering mode"), config.plugins.iptvplayer.alternativeARMMoviePlayer))
            players.append(config.plugins.iptvplayer.alternativeARMMoviePlayer)
            
        else: 
            list.append(getConfigListEntry(_("Movie player"), config.plugins.iptvplayer.NaszPlayer))
        
        playersValues = [player.value for player in players]
        if 'exteplayer' in playersValues or 'extgstplayer' in playersValues or 'auto' in playersValues:
            list.append(getConfigListEntry(_("External movie player config"), config.plugins.iptvplayer.fakExtMoviePlayerList))
        
        list.append(getConfigListEntry(_("Autoplay start delay"), config.plugins.iptvplayer.autoplay_start_delay))
        list.append(getConfigListEntry(_("The number of items in the search history"), config.plugins.iptvplayer.search_history_size))
        list.append(getConfigListEntry(_("Block wmv files"), config.plugins.iptvplayer.ZablokujWMV))
        list.append(getConfigListEntry(_("Show IPTVPlayer in extension list"), config.plugins.iptvplayer.showinextensions))
        list.append(getConfigListEntry(_("Show IPTVPlayer in main menu"), config.plugins.iptvplayer.showinMainMenu))
        list.append(getConfigListEntry(_("Show update icon in service selection menu"), config.plugins.iptvplayer.AktualizacjaWmenu))
        list.append(getConfigListEntry(_("Debug logs"), config.plugins.iptvplayer.debugprint))
        list.append(getConfigListEntry(_("Allow downgrade"), config.plugins.iptvplayer.downgradePossible))
        list.append(getConfigListEntry(_("Update packet type"), config.plugins.iptvplayer.possibleUpdateType))
        if 'j00zekFork' in globals():
            RemoveDuplicatesFromList(list)

    def runSetup(self):
        self.list = []
        ConfigMenu.fillConfigList(self.list, self.isHiddenOptionsUnlocked())
        ConfigBaseWidget.runSetup(self)
        
    def onSelectionChanged(self):
        currItem = self["config"].getCurrent()[1]
        if currItem in [config.plugins.iptvplayer.fakePin, config.plugins.iptvplayer.fakeUpdate, config.plugins.iptvplayer.fakeHostsList, config.plugins.iptvplayer.fakExtMoviePlayerList]:
            self.isOkEnabled  = True
            self.isSelectable = False 
            self.setOKLabel()
        else:
            ConfigBaseWidget.onSelectionChanged(self)

    def keyUpdate(self):
        printDBG("ConfigMenu.keyUpdate")
        if self.isChanged():
            self.askForSave(self.doUpdate, self.doUpdate)
        else:
            self.doUpdate()

    def doUpdate(self, forced=False):
        if 'j00zekFork' in globals():
            from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import j00zekIPTVPlayerConsole, j00zekRunUpdateList
            self.session.open(j00zekIPTVPlayerConsole, title = _("Updating plugin"), cmdlist = j00zekRunUpdateList)
            return
        printDBG("ConfigMenu.doUpdate")
        if not forced:
            self.session.open(IPTVUpdateWindow, UpdateMainAppImpl(self.session))
        else:
            self.session.openWithCallback(self.closeAfterUpdate, IPTVUpdateWindow, UpdateMainAppImpl(self.session, allowTheSameVersion=True))
        
    def closeAfterUpdate(self, arg1=None, arg2=None):
        self.close()
    
    def save(self):
        ConfigBaseWidget.save(self)
        if self.showcoverOld != config.plugins.iptvplayer.showcover.value or \
           self.SciezkaCacheOld != config.plugins.iptvplayer.SciezkaCache.value:
           pass
           # plugin must be restarted if we wont to this options take effect
        if self.platformOld != config.plugins.iptvplayer.plarform.value:
            IPTVPlayerNeedInit(True)
            
    def getMessageBeforeClose(self, afterSave):
        needPluginUpdate = False
        if afterSave and config.plugins.iptvplayer.ListaGraficzna.value and 0 == GetAvailableIconSize(False):
            needPluginUpdate = True
        else:
            enabledHostsList = GetEnabledHostsList()
            hostsFromFolder  = GetHostsList(fromList=False, fromHostFolder=True)
            if self.remove_diabled_hostsOld != config.plugins.iptvplayer.remove_diabled_hosts.value:
                if config.plugins.iptvplayer.remove_diabled_hosts.value:
                    for folderItem in hostsFromFolder:
                        if folderItem in enabledHostsList:
                            continue
                        else:
                            # there is host file which is not enabled, 
                            # so we need perform update to remove it
                            needPluginUpdate = True
                            break
                else:
                    hostsFromList = GetHostsList(fromList=True, fromHostFolder=False)
                    if not set(hostsFromList).issubset(set(hostsFromFolder)):
                        # there is missing hosts files, we need updated does not matter 
                        # if these hosts are enabled or disabled
                        needPluginUpdate = True
                
            elif config.plugins.iptvplayer.remove_diabled_hosts.value and enabledHostsList != self.enabledHostsListOld:
                hostsFromList = GetHostsList(fromList=True, fromHostFolder=False)
                diffDisabledHostsList = set(self.enabledHostsListOld).difference(set(enabledHostsList))
                diffList = set(enabledHostsList).symmetric_difference(set(self.enabledHostsListOld))
                for hostItem in diffList:
                    if hostItem in hostsFromList:
                        if hostItem in diffDisabledHostsList:
                            if hostItem in hostsFromFolder:
                                # standard host has been disabled but it is still in folder
                                needPluginUpdate = True
                                break
                        else:
                            if hostItem not in hostsFromFolder:
                                # standard host has been enabled but it is not in folder
                                needPluginUpdate = True
                                break
            
        if needPluginUpdate:
            return _('Some changes will be applied only after plugin update.\nDo you want to perform update now?')
        else:
            return ''
            
    def performCloseWithMessage(self, afterSave=True):
        message = self.getMessageBeforeClose(afterSave)
        if message == '':
            self.close()
        else:
            self.session.openWithCallback(self.closeAfterMessage, MessageBox, text = message, type = MessageBox.TYPE_YESNO)
            
    def closeAfterMessage(self, arg=None):
        if arg:
            self.doUpdate(True)
        else:
            self.close()

    def keyOK(self):
        curIndex = self["config"].getCurrentIndex()
        currItem = self["config"].list[curIndex][1]
        if isinstance(currItem, ConfigDirectory):
            def SetDirPathCallBack(curIndex, newPath):
                if None != newPath: self["config"].list[curIndex][1].value = newPath
            self.session.openWithCallback(boundFunction(SetDirPathCallBack, curIndex), IPTVDirectorySelectorWidget, currDir=currItem.value, title="Wybierz katalog")
        elif config.plugins.iptvplayer.fakePin == currItem:
            self.changePin(start = True)
        elif config.plugins.iptvplayer.fakeUpdate == currItem:
            self.keyUpdate()
        elif config.plugins.iptvplayer.fakeHostsList == currItem:
            self.hostsList()
        elif config.plugins.iptvplayer.fakExtMoviePlayerList == currItem:
            self.extMoviePlayerList()
        else:
            ConfigBaseWidget.keyOK(self)

    def getSubOptionsList(self):
        tab = [config.plugins.iptvplayer.buforowanie,
              config.plugins.iptvplayer.buforowanie_m3u8,
              config.plugins.iptvplayer.buforowanie_rtmp,
              config.plugins.iptvplayer.showcover,
              config.plugins.iptvplayer.ListaGraficzna,
              config.plugins.iptvplayer.pluginProtectedByPin,
              config.plugins.iptvplayer.configProtectedByPin,
              config.plugins.iptvplayer.plarform
              ]
        players = []
        if 'sh4' == config.plugins.iptvplayer.plarform.value:
            players.append(config.plugins.iptvplayer.defaultSH4MoviePlayer0)
            players.append(config.plugins.iptvplayer.alternativeSH4MoviePlayer0)
            players.append(config.plugins.iptvplayer.defaultSH4MoviePlayer)
            players.append(config.plugins.iptvplayer.alternativeSH4MoviePlayer)
        elif 'mipsel' == config.plugins.iptvplayer.plarform.value:
            players.append(config.plugins.iptvplayer.defaultMIPSELMoviePlayer0)
            players.append(config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0)
            players.append(config.plugins.iptvplayer.defaultMIPSELMoviePlayer)
            players.append(config.plugins.iptvplayer.alternativeMIPSELMoviePlayer)
        elif 'armv7' == config.plugins.iptvplayer.plarform.value:
            players.append(config.plugins.iptvplayer.defaultARMV7MoviePlayer0)
            players.append(config.plugins.iptvplayer.alternativeARMV7MoviePlayer0)
            players.append(config.plugins.iptvplayer.defaultARMV7MoviePlayer)
            players.append(config.plugins.iptvplayer.alternativeARMV7MoviePlayer)
        elif 'i686' == config.plugins.iptvplayer.plarform.value:
            players.append(config.plugins.iptvplayer.defaultI686MoviePlayer0)
            players.append(config.plugins.iptvplayer.alternativeI686MoviePlayer0)
            players.append(config.plugins.iptvplayer.defaultI686MoviePlayer)
            players.append(config.plugins.iptvplayer.alternativeI686MoviePlayer)
        else:
            players.append(config.plugins.iptvplayer.NaszPlayer)
        tab.extend(players)
        return tab
        


    def changePin(self, pin = None, start = False):
        # 'PUT_OLD_PIN', 'PUT_NEW_PIN', 'CONFIRM_NEW_PIN'
        if True == start:
            self.changingPinState = 'PUT_OLD_PIN'
            self.session.openWithCallback(self.changePin, IPTVPinWidget, title=_("Enter old pin"))
        else:
            if pin == None: return
            if 'PUT_OLD_PIN' == self.changingPinState:
                if pin == config.plugins.iptvplayer.pin.value:
                    self.changingPinState = 'PUT_NEW_PIN'
                    self.session.openWithCallback(self.changePin, IPTVPinWidget, title=_("Enter new pin"))
                else:
                    self.session.open(MessageBox, _("Pin incorrect!"), type=MessageBox.TYPE_INFO, timeout=5)
            elif 'PUT_NEW_PIN' == self.changingPinState:
                self.newPin = pin
                self.changingPinState = 'CONFIRM_NEW_PIN'
                self.session.openWithCallback(self.changePin, IPTVPinWidget, title=_("Confirm new pin"))
            elif 'CONFIRM_NEW_PIN' == self.changingPinState:
                if self.newPin == pin:
                    config.plugins.iptvplayer.pin.value = pin
                    config.plugins.iptvplayer.pin.save()
                    configfile.save()
                    self.session.open(MessageBox, _("Pin has been changed."), type=MessageBox.TYPE_INFO, timeout=5)
                else:
                    self.session.open(MessageBox, _("Confirmation error."), type=MessageBox.TYPE_INFO, timeout=5)
                    
    def hostsList(self):
        global gListOfHostsNames
        self.session.open(ConfigHostsMenu, gListOfHostsNames)
        
    def extMoviePlayerList(self):
        self.session.open(ConfigExtMoviePlayer)

def GetMoviePlayer(buffering=False, useAlternativePlayer=False):
    printDBG("GetMoviePlayer buffering[%r], useAlternativePlayer[%r]" % (buffering, useAlternativePlayer))
    # select movie player
    
    availablePlayers = []
    if config.plugins.iptvplayer.plarform.value in ['sh4', 'mipsel'] and IsExecutable(config.plugins.iptvplayer.exteplayer3path.value):
        availablePlayers.append('exteplayer')
    if IsExecutable(config.plugins.iptvplayer.gstplayerpath.value): #config.plugins.iptvplayer.plarform.value in ['sh4', 'mipsel', 'i686'] and 
        availablePlayers.append('extgstplayer')
    availablePlayers.append('mini')
    availablePlayers.append('standard')
        
    player = None
    alternativePlayer = None

    if 'sh4' == config.plugins.iptvplayer.plarform.value:
        if buffering:
            player = config.plugins.iptvplayer.defaultSH4MoviePlayer
            alternativePlayer = config.plugins.iptvplayer.alternativeSH4MoviePlayer
        else:
            player = config.plugins.iptvplayer.defaultSH4MoviePlayer0
            alternativePlayer = config.plugins.iptvplayer.alternativeSH4MoviePlayer0
            
    elif 'mipsel' == config.plugins.iptvplayer.plarform.value:
        if buffering:
            player = config.plugins.iptvplayer.defaultMIPSELMoviePlayer
            alternativePlayer = config.plugins.iptvplayer.alternativeMIPSELMoviePlayer
        else:
            player = config.plugins.iptvplayer.defaultMIPSELMoviePlayer0
            alternativePlayer = config.plugins.iptvplayer.alternativeMIPSELMoviePlayer0

    elif 'armv7' == config.plugins.iptvplayer.plarform.value:
        if buffering:
            player = config.plugins.iptvplayer.defaultARMV7MoviePlayer
            alternativePlayer = config.plugins.iptvplayer.alternativeARMV7MoviePlayer
        else:
            player = config.plugins.iptvplayer.defaultARMV7MoviePlayer0
            alternativePlayer = config.plugins.iptvplayer.alternativeARMV7MoviePlayer0

    elif 'i686' == config.plugins.iptvplayer.plarform.value:
        if buffering:
            player = config.plugins.iptvplayer.defaultI686MoviePlayer
            alternativePlayer = config.plugins.iptvplayer.alternativeI686MoviePlayer
        else:
            player = config.plugins.iptvplayer.defaultI686MoviePlayer0
            alternativePlayer = config.plugins.iptvplayer.alternativeI686MoviePlayer0
    else:
        player = config.plugins.iptvplayer.NaszPlayer
        alternativePlayer = config.plugins.iptvplayer.NaszPlayer
        
    if player.value == 'auto': player = CFakeMoviePlayerOption(availablePlayers[0], GetMoviePlayerName(availablePlayers[0]))
    try: availablePlayers.remove(player.value)
    except: printExc()
    
    if alternativePlayer.value == 'auto': alternativePlayer = CFakeMoviePlayerOption(availablePlayers[0], GetMoviePlayerName(availablePlayers[0]))
    try: availablePlayers.remove(alternativePlayer.value)
    except: printExc()
    
    if useAlternativePlayer:
        return alternativePlayer
    
    return player