# -*- coding: utf-8 -*-
#
#  Konfigurator dla iptv 2013
#  autorzy: j00zek, samsamsam
#

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, GetHostsList, IsHostEnabled, SaveHostsOrderList, SortHostsList, \
                                                          GetE2VideoAspectChoices, GetE2VideoAspect, SetE2VideoAspect, GetE2VideoPolicyChoices, \
                                                          GetE2VideoPolicy, SetE2VideoPolicy, GetE2AudioCodecMixChoices, GetE2AudioCodecMixOption, IsExecutable
from Plugins.Extensions.IPTVPlayer.components.configbase import ConfigBaseWidget, ConfigIPTVFileSelection
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
###################################################

###################################################
# FOREIGN import
###################################################
import skin
from enigma import gRGB, eLabel
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigYesNo, ConfigOnOff, Config, ConfigInteger, ConfigSubList, ConfigText, getConfigListEntry, configfile
###################################################
COLORS_DEFINITONS = [("#000000", _("black")), ("#C0C0C0", _("silver")), ("#808080", _("gray")), ("#FFFFFF", _("white")), ("#800000", _("maroon")), ("#FF0000", _("red")), ("#800080", _("purple")), ("#FF00FF", _("fuchsia")), \
                     ("#008000", _("green")), ("#00FF00", _("lime")), ("#808000", _("olive")), ("#FFFF00", _("yellow")), ("#000080", _("navy")), ("#0000FF", _("blue")), ("#008080", _("teal")), ("#00FFFF", _("aqua"))]

config.plugins.iptvplayer.show_iframe = ConfigYesNo(default = False)
config.plugins.iptvplayer.iframe_file = ConfigIPTVFileSelection(fileMatch = "^.*\.mvi$", default = "/usr/share/enigma2/radio.mvi")
config.plugins.iptvplayer.clear_iframe_file = ConfigIPTVFileSelection(fileMatch = "^.*\.mvi$", default = "/usr/share/enigma2/black.mvi")

config.plugins.iptvplayer.remember_last_position = ConfigYesNo(default = False)
config.plugins.iptvplayer.fakeExtePlayer3 = ConfigSelection(default = "fake", choices = [("fake", " ")])
config.plugins.iptvplayer.aac_software_decode = ConfigYesNo(default = False)
config.plugins.iptvplayer.dts_software_decode = ConfigYesNo(default = False)
config.plugins.iptvplayer.wma_software_decode = ConfigYesNo(default = True)
config.plugins.iptvplayer.stereo_software_decode = ConfigYesNo(default = False)
config.plugins.iptvplayer.software_decode_as = ConfigSelection(default = "pcm", choices = [("pcm", _("PCM")), ("lpcm", _("LPCM"))])
config.plugins.iptvplayer.aac_mix = ConfigSelection(default = None, choices = [(None, _("from E2 settings"))])
config.plugins.iptvplayer.ac3_mix = ConfigSelection(default = None, choices = [(None, _("from E2 settings"))])

config.plugins.iptvplayer.extplayer_infobar_timeout = ConfigSelection(default = "5", choices = [
        ("1", "1 " + _("second")), ("2", "2 " + _("seconds")), ("3", "3 " + _("seconds")),
        ("4", "4 " + _("seconds")), ("5", "5 " + _("seconds")), ("6", "6 " + _("seconds")), ("7", "7 " + _("seconds")),
        ("8", "8 " + _("seconds")), ("9", "9 " + _("seconds")), ("10", "10 " + _("seconds"))])
config.plugins.iptvplayer.extplayer_aspect = ConfigSelection(default = None, choices = [(None, _("from E2 settings"))])
config.plugins.iptvplayer.extplayer_policy = ConfigSelection(default = None, choices = [(None, _("from E2 settings"))])
config.plugins.iptvplayer.extplayer_policy2 = ConfigSelection(default = None, choices = [(None, _("from E2 settings"))])

config.plugins.iptvplayer.extplayer_subtitle_auto_enable = ConfigYesNo(default = True)
config.plugins.iptvplayer.extplayer_subtitle_font = ConfigSelection(default = "Regular", choices = [("Regular", "Regular")])
config.plugins.iptvplayer.extplayer_subtitle_font_size = ConfigInteger(40, (20, 90))
config.plugins.iptvplayer.extplayer_subtitle_font_color = ConfigSelection(default = "#FFFFFF", choices = COLORS_DEFINITONS)
config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled = ConfigYesNo(default = False)
config.plugins.iptvplayer.extplayer_subtitle_line_height = ConfigInteger(40, (20, 999))
config.plugins.iptvplayer.extplayer_subtitle_line_spacing = ConfigInteger(4, (0, 99))
config.plugins.iptvplayer.extplayer_subtitle_background = ConfigSelection(default = "#000000", choices = [('transparent', _('Transparent')), ('#000000', _('Black')), ('#80000000', _('Darkgray')), ('#cc000000', _('Lightgray'))])

config.plugins.iptvplayer.extplayer_subtitle_border_color = ConfigSelection(default = "#000000", choices = COLORS_DEFINITONS)
config.plugins.iptvplayer.extplayer_subtitle_shadow_color = ConfigSelection(default = "#000000", choices = COLORS_DEFINITONS)

config.plugins.iptvplayer.extplayer_subtitle_border_enabled = ConfigYesNo(default = True)
config.plugins.iptvplayer.extplayer_subtitle_shadow_enabled = ConfigYesNo(default = False)

config.plugins.iptvplayer.extplayer_subtitle_border_width = ConfigInteger(3, (1, 6))
config.plugins.iptvplayer.extplayer_subtitle_shadow_xoffset = ConfigInteger(3, (-6, 6))
config.plugins.iptvplayer.extplayer_subtitle_shadow_yoffset = ConfigInteger(3, (-6, 6))
config.plugins.iptvplayer.extplayer_subtitle_pos = ConfigInteger(50, (0, 400))
config.plugins.iptvplayer.extplayer_subtitle_box_valign = ConfigSelection(default = "bottom", choices = [ ("bottom", _("bottom")), ("center", _("center")), ("top", _("top"))])
config.plugins.iptvplayer.extplayer_subtitle_box_height  = ConfigInteger(240, (50, 400))

class ConfigExtMoviePlayerBase():
    
    def __init__(self):
        
        # fill aac_mix option
        options = [(None, _("From E2 settings"))]
        tmp = GetE2AudioCodecMixChoices('aac')
        for item in tmp:
            options.append((item,_(item)))
        if config.plugins.iptvplayer.aac_mix.value not in tmp:
            config.plugins.iptvplayer.aac_mix.value = None
        if len(tmp):
            self.aac_mix_avaliable = True
        else: self.aac_mix_avaliable = False
        config.plugins.iptvplayer.aac_mix = ConfigSelection(default = None, choices = options)
        
        # fill ac3_mix option
        options = [(None, _("From E2 settings"))]
        tmp = GetE2AudioCodecMixChoices('ac3')
        for item in tmp:
            options.append((item,_(item)))
        if config.plugins.iptvplayer.ac3_mix.value not in tmp:
            config.plugins.iptvplayer.ac3_mix.value = None
        if len(tmp):
            self.ac3_mix_avaliable = True
        else: self.ac3_mix_avaliable = False
        config.plugins.iptvplayer.ac3_mix = ConfigSelection(default = None, choices = options)
        
        # fill aspect option
        options = [(None, _("From E2 settings"))]
        tmp = GetE2VideoAspectChoices()
        for item in tmp:
            options.append((item,_(item)))
        if config.plugins.iptvplayer.extplayer_aspect.value not in tmp:
            config.plugins.iptvplayer.extplayer_aspect.value = None
        if len(tmp):
            self.aspect_avaliable = True
        else: self.aspect_avaliable = False
        config.plugins.iptvplayer.extplayer_aspect = ConfigSelection(default = None, choices = options)

        # fill policy option 
        options = [(None, _("From E2 settings"))]
        tmp = GetE2VideoPolicyChoices()
        for item in tmp:
            options.append((item,_(item)))
        if config.plugins.iptvplayer.extplayer_policy.value not in tmp:
            config.plugins.iptvplayer.extplayer_policy.value = None
        if len(tmp):
            self.policy_avaliable = True
        else: self.policy_avaliable = False
        config.plugins.iptvplayer.extplayer_policy = ConfigSelection(default = None, choices = options)
        
        # fill policy 2 option 
        options = [(None, _("From E2 settings"))]
        if None != GetE2VideoPolicy('2'):
            tmp = GetE2VideoPolicyChoices()
            for item in tmp:
                options.append((item,_(item)))
        else: tmp = []
        if config.plugins.iptvplayer.extplayer_policy2.value not in tmp:
            config.plugins.iptvplayer.extplayer_policy2.value = None
        if len(tmp):
            self.policy2_avaliable = True
        else: self.policy2_avaliable = False
        config.plugins.iptvplayer.extplayer_policy2 = ConfigSelection(default = None, choices = options)
        
        # fill fonts option
        options = [("Regular", "Regular")]
        fonts = ["Regular"]
        try:
            for key in skin.fonts:
                font = skin.fonts[key][0]
                if font not in fonts:
                    fonts.append(font)
                    options.append((font, font))
        except: printExc()
        config.plugins.iptvplayer.extplayer_subtitle_font = ConfigSelection(default = "Regular", choices = options)
        
        # check if border is avaliable
        self.subtitle_border_avaliable = False
        try:
            tmp = dir(eLabel)
            if 'setBorderColor' in tmp:
                self.subtitle_border_avaliable = True
        except: printExc()
        if not self.subtitle_border_avaliable:
            config.plugins.iptvplayer.extplayer_subtitle_border_enabled.value = False
    
    def getSubtitleFontSettings(self):
        settings = {}
        settings['auto_enable'] = config.plugins.iptvplayer.extplayer_subtitle_auto_enable.value
        settings['wrapping_enabled'] = config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled.value
        settings['font'] = config.plugins.iptvplayer.extplayer_subtitle_font.value
        settings['font_size'] = config.plugins.iptvplayer.extplayer_subtitle_font_size.value
        settings['font_color'] = config.plugins.iptvplayer.extplayer_subtitle_font_color.value
        settings['background'] = config.plugins.iptvplayer.extplayer_subtitle_background.value
        settings['line_height'] = config.plugins.iptvplayer.extplayer_subtitle_line_height.value
        settings['line_spacing'] = config.plugins.iptvplayer.extplayer_subtitle_line_spacing.value

        if self.subtitle_border_avaliable and config.plugins.iptvplayer.extplayer_subtitle_border_enabled.value:
            settings['border'] = {} 
            settings['border']['color'] = config.plugins.iptvplayer.extplayer_subtitle_border_color.value
            settings['border']['width'] = config.plugins.iptvplayer.extplayer_subtitle_border_width.value
    
        if config.plugins.iptvplayer.extplayer_subtitle_shadow_enabled.value:
            settings['shadow'] = {}
            settings['shadow']['color'] = config.plugins.iptvplayer.extplayer_subtitle_shadow_color.value
            settings['shadow']['xoffset'] = config.plugins.iptvplayer.extplayer_subtitle_shadow_xoffset.value
            settings['shadow']['yoffset'] = config.plugins.iptvplayer.extplayer_subtitle_shadow_yoffset.value
        settings['pos'] = config.plugins.iptvplayer.extplayer_subtitle_pos.value
        settings['box_valign'] = config.plugins.iptvplayer.extplayer_subtitle_box_valign.value        
        settings['box_height'] = config.plugins.iptvplayer.extplayer_subtitle_box_height.value
        return settings
        
    def getDefaultPlayerVideoOptions(self):
        defVideoOptions  = {'aspect':  config.plugins.iptvplayer.extplayer_aspect.value, 
                            'policy':  config.plugins.iptvplayer.extplayer_policy.value, 
                            'policy2': config.plugins.iptvplayer.extplayer_policy2.value 
                           }
        printDBG(">>>>>>>>>>>>>>>>>>>>> getE2VideoOptions[%s]" % defVideoOptions)
        return defVideoOptions
        
    def getDefaultAudioOptions(self):
        defAudioOptions  = {'aac':  config.plugins.iptvplayer.aac_mix.value, 
                            'ac3':  config.plugins.iptvplayer.ac3_mix.value, 
                           }
        printDBG(">>>>>>>>>>>>>>>>>>>>> getDefaultAudioOptions[%s]" % defAudioOptions)
        return defAudioOptions
        
    def getInfoBarTimeout(self):
        return config.plugins.iptvplayer.extplayer_infobar_timeout.value
        
class ConfigExtMoviePlayer(ConfigBaseWidget, ConfigExtMoviePlayerBase):
   
    def __init__(self, session, operatingPlayer=False):
        printDBG("ConfigExtMoviePlayer.__init__ -------------------------------")
        self.list = [ ]
        ConfigBaseWidget.__init__(self, session)
        ConfigExtMoviePlayerBase.__init__(self)
        self.setup_title = _("Configuring an external movie player")
        self.operatingPlayer = operatingPlayer
        self.runtimeOptionsValues = self.getRuntimeOptionsValues()

    def __del__(self):
        printDBG("ConfigExtMoviePlayer.__del__ -------------------------------")
        
    def __onClose(self):
        printDBG("ConfigExtMoviePlayer.__onClose -----------------------------")
        ConfigBaseWidget.__onClose(self)
        
    def saveAndClose(self):
        self.save()
        message = self.getMessageAfterSave()
        if message == '':
            if self.operatingPlayer:
                self.close(True)
            else:
                self.close()
        else:
            self.session.openWithCallback(self.closeAfterMessage, MessageBox, text = message, type = MessageBox.TYPE_INFO)
        
    def closeAfterMessage(self, arg=None):
        if self.operatingPlayer:
            self.close(True)
        else:
            self.close()
            
    def getMessageAfterSave(self):
        if self.operatingPlayer and self.runtimeOptionsValues != self.getRuntimeOptionsValues():
            return _('Some changes will be applied only after movie player restart.')
        else:
            return ''

    def layoutFinished(self):
        ConfigBaseWidget.layoutFinished(self)
        self.setTitle("IPTV Player " + (_("Configuring an external movie player")))
        
    def getRuntimeOptionsValues(self):
        valTab = []
        valTab.append(config.plugins.iptvplayer.aac_software_decode.value)
        valTab.append(config.plugins.iptvplayer.dts_software_decode.value)
        valTab.append(config.plugins.iptvplayer.wma_software_decode.value)
        valTab.append(config.plugins.iptvplayer.software_decode_as.value)
        valTab.append(config.plugins.iptvplayer.stereo_software_decode.value)
        valTab.append(config.plugins.iptvplayer.ac3_mix.value)
        valTab.append(config.plugins.iptvplayer.aac_mix.value)
        valTab.append(config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled.value)
        valTab.append(config.plugins.iptvplayer.show_iframe.value)
        return valTab
        
    def runSetup(self):
        list = []
        list.append(getConfigListEntry(_("show iframe for audio item"), config.plugins.iptvplayer.show_iframe))
        if config.plugins.iptvplayer.show_iframe.value:
            list.append(getConfigListEntry("    " + _("Iframe file"), config.plugins.iptvplayer.iframe_file))
            if 'sh4' != config.plugins.iptvplayer.plarform.value:
                list.append(getConfigListEntry("    " + _("Clear iframe file"), config.plugins.iptvplayer.clear_iframe_file))
        
        list.append(getConfigListEntry(_("Remember last watched position"), config.plugins.iptvplayer.remember_last_position))
        if 1:#IsExecutable(config.plugins.iptvplayer.exteplayer3path.value):
            list.append(getConfigListEntry(_("----------------- External exteplayer3 options -----------------"), config.plugins.iptvplayer.fakeExtePlayer3))
            list.append(getConfigListEntry("    " + _("External player use software decoder for the AAC"), config.plugins.iptvplayer.aac_software_decode))
            if config.plugins.iptvplayer.plarform.value in ['mipsel', 'armv7', 'i686']:
                list.append(getConfigListEntry("    " + _("External player use software decoder for the DTS"), config.plugins.iptvplayer.dts_software_decode))
                list.append(getConfigListEntry("    " + _("External player use software decoder for the WMA"), config.plugins.iptvplayer.wma_software_decode))
                list.append(getConfigListEntry("    " + _("Software decoding as"), config.plugins.iptvplayer.software_decode_as))
                list.append(getConfigListEntry("    " + _("Stereo downmix mode for software decoder"), config.plugins.iptvplayer.stereo_software_decode))
        if self.ac3_mix_avaliable:
            list.append(getConfigListEntry(_("AC3 mix mode"), config.plugins.iptvplayer.ac3_mix))
        if self.aac_mix_avaliable:
            list.append(getConfigListEntry(_("AAC mix mode"), config.plugins.iptvplayer.aac_mix))
            
        list.append(getConfigListEntry(_("External player infobar timeout"), config.plugins.iptvplayer.extplayer_infobar_timeout))
        
        if self.aspect_avaliable:
            list.append(getConfigListEntry(_("Default video aspect ratio"), config.plugins.iptvplayer.extplayer_aspect) )
        if self.policy_avaliable:
            list.append(getConfigListEntry(_("Default video policy"), config.plugins.iptvplayer.extplayer_policy) )
        if self.policy2_avaliable:
            list.append(getConfigListEntry(_("Default second video policy"), config.plugins.iptvplayer.extplayer_policy2) )
        
        list.append(getConfigListEntry(_("Load automatically the subtitle from file with the same name"), config.plugins.iptvplayer.extplayer_subtitle_auto_enable) )
        list.append(getConfigListEntry(_("Subtitle line wrapping"), config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled) )
        list.append(getConfigListEntry(_("Subtitle font"), config.plugins.iptvplayer.extplayer_subtitle_font) )
        list.append(getConfigListEntry(_("Subtitle font size"), config.plugins.iptvplayer.extplayer_subtitle_font_size) )
        if not config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled.value:
            list.append(getConfigListEntry(_("Subtitle line height"), config.plugins.iptvplayer.extplayer_subtitle_line_height) )
            list.append(getConfigListEntry(_("Line Spacing"), config.plugins.iptvplayer.extplayer_subtitle_line_spacing) )
        elif 'transparent' != config.plugins.iptvplayer.extplayer_subtitle_background.value:
            list.append(getConfigListEntry(_("Subtitle line height"), config.plugins.iptvplayer.extplayer_subtitle_line_height) )
        
        list.append(getConfigListEntry(_("Subtitle font color"), config.plugins.iptvplayer.extplayer_subtitle_font_color) )
        list.append(getConfigListEntry(_("Subtitle background"), config.plugins.iptvplayer.extplayer_subtitle_background) )
        
        list.append(getConfigListEntry(_("Subtitle box position"), config.plugins.iptvplayer.extplayer_subtitle_pos) )
        if config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled.value:
            if 'transparent' == config.plugins.iptvplayer.extplayer_subtitle_background.value:
                list.append(getConfigListEntry(_("Subtitle box height"), config.plugins.iptvplayer.extplayer_subtitle_box_height) )
                list.append(getConfigListEntry(_("Subtitle vertical alignment"), config.plugins.iptvplayer.extplayer_subtitle_box_valign) )
        
        if self.subtitle_border_avaliable:
            list.append(getConfigListEntry(_("Subtitle border enabled"), config.plugins.iptvplayer.extplayer_subtitle_border_enabled) )
            if config.plugins.iptvplayer.extplayer_subtitle_border_enabled.value:
                list.append(getConfigListEntry(_("Subtitle border color"), config.plugins.iptvplayer.extplayer_subtitle_border_color) )
                list.append(getConfigListEntry(_("Subtitle border width"), config.plugins.iptvplayer.extplayer_subtitle_border_width) )
                
        list.append(getConfigListEntry(_("Subtitle shadow enabled"), config.plugins.iptvplayer.extplayer_subtitle_shadow_enabled) )
        if config.plugins.iptvplayer.extplayer_subtitle_shadow_enabled.value:
            list.append(getConfigListEntry(_("Subtitle shadow color"), config.plugins.iptvplayer.extplayer_subtitle_shadow_color) )
            list.append(getConfigListEntry(_("Subtitle shadow X offset"), config.plugins.iptvplayer.extplayer_subtitle_shadow_xoffset) )
            list.append(getConfigListEntry(_("Subtitle shadow Y offset"), config.plugins.iptvplayer.extplayer_subtitle_shadow_yoffset) )
        
        self.list = list
        ConfigBaseWidget.runSetup(self)
        
    def getSubOptionsList(self):
        tab = [config.plugins.iptvplayer.extplayer_subtitle_border_enabled,
               config.plugins.iptvplayer.extplayer_subtitle_shadow_enabled,
               config.plugins.iptvplayer.extplayer_subtitle_wrapping_enabled,
               config.plugins.iptvplayer.extplayer_subtitle_background,
               config.plugins.iptvplayer.show_iframe,
              ]

    def changeSubOptions(self):
        self.runSetup()
        
