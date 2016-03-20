﻿# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, remove_html_markup, GetCookieDir, byteify
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CBaseHostClass
###################################################

###################################################
# FOREIGN import
###################################################
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
import re
import urllib
import random
import string
try:    import json
except: import simplejson as json
############################################

###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper
from Screens.MessageBox import MessageBox
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.skylinewebcams_lang = ConfigSelection(default = "en", choices = [("en", _("en")), ("it", _("it")), ("es", _("es")), ("de", _("de")), ("fr", _("fr")),
                                                                                           ("el", _("el")), ("hr", _("hr")), ("sl", _("sl")), ("zh", _("zh"))])

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_("Language:"), config.plugins.iptvplayer.skylinewebcams_lang))
    return optionList
    
###################################################

class WkylinewebcamsComApi:
    MAIN_URL = 'https://www.skylinewebcams.com/'

    def __init__(self):
        self.COOKIE_FILE = GetCookieDir('skylinewebcamscom.cookie')
        self.cm = common()
        self.up = urlparser()
        self.http_params = {}
        self.http_params.update({'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIE_FILE})
        self.cacheList = {}
        self.mainMenuCache = {}
        self.lang = config.plugins.iptvplayer.skylinewebcams_lang.value
        
    def getFullUrl(self, url):
        if url == '':
            return ''
        if url.startswith('//'):
            return 'http:' + url
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            url = url[1:]
        return self.MAIN_URL + url
        
    def cleanHtmlStr(self, str):
        return CBaseHostClass.cleanHtmlStr(str)
        
    def getMainMenu(self, cItem):
        printDBG("WkylinewebcamsCom.getMainMenu")
        STATIC_TAB = [{'title':_('NEW'),           'url':self.getFullUrl('/skyline/morewebcams.php?w=new&l='+self.lang), 'cat':'list_cams2'},
                      {'title':_('NEARBY CAMS'),   'url':self.getFullUrl('/skyline/morewebcams.php?w=you&l='+self.lang), 'cat':'list_cams2'},
                      {'title':_('TOP live cams'), 'url':self.getFullUrl(self.lang+'/top-live-cams.html'),               'cat':'list_cams'},
                      ]
        
        list = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return list
        data = self.cm.ph.getDataBeetwenMarkers(data, 'id="main-menu', ' lang')[1]
        data  = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="dropdown">', '</ul>')
        for idx in range(2):
            if idx >= len(data): continue
            catData = data[idx]
            catData = catData.split('<ul ')
            if 2 != len(catData): continue
            catTitle = self.cleanHtmlStr(catData[0])
            catUrl   = self.cm.ph.getSearchGroups(catData[0], '''<a[^>]*?href="([^"]+?)"''', 1, True)[0]
            catData  = self.cm.ph.getAllItemsBeetwenMarkers(catData[1], '<a ', '</a>')
            tab = []
            for item in catData:
                url   = self.cm.ph.getSearchGroups(item, '''href="([^"]+?)"''', 1, True)[0]
                title = self.cleanHtmlStr(item)
                tab.append({'url':self.getFullUrl(url), 'title':title, 'cat':'list_cams'}) #explore_item
            if len(tab):
                tab.insert(0, {'url':self.getFullUrl(catUrl), 'title':_('All'), 'cat':'list_cams'})
                self.mainMenuCache[idx] = tab
                params = dict(cItem)
                params.update({'title':catTitle, 'cat':'list_main_category', 'idx':idx})
                list.append(params)
        
        for item in STATIC_TAB:
                params = dict(cItem)
                params.update(item)
                list.insert(0, params)
        return list
        
    def listCams2(self, cItem):
        printDBG("WkylinewebcamsCom.listCams2")
        list = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return list
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a ', '</a>')
        for item in data:
            url    = self.cm.ph.getSearchGroups(item, '''href="([^"]+?)"''', 1, True)[0]
            icon   = self.cm.ph.getSearchGroups(item, '''src="([^"]+?)"''', 1, True)[0]
            if not url.startswith('http'): continue
            title  = self.cleanHtmlStr(item)
            params = dict(cItem)
            params.update({'title':title, 'url':self.getFullUrl(url), 'icon':self.getFullUrl(icon), 'type':'video'})
            list.append(params)
        return list
        
    def listCams(self, cItem):
        printDBG("WkylinewebcamsCom.listCams")
        list = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return list
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="webcam">', '</li>')
        for item in data:
            url    = self.cm.ph.getSearchGroups(item, '''href="([^"]+?)"''', 1, True)[0]
            icon   = self.cm.ph.getSearchGroups(item, '''"([^"]+?\.jpg)"''', 1, True)[0]
            if '' == url: continue
            title  = self.cleanHtmlStr(self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0])
            desc   = self.cleanHtmlStr(item)
            params = dict(cItem)
            params.update({'title':title, 'url':self.getFullUrl(url), 'icon':self.getFullUrl(icon), 'desc':desc, 'type':'video'})
            list.append(params)
        return list
        
    def exploreItem(self, cItem):
        printDBG("WkylinewebcamsCom.exploreItem")
        list = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return list
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="webcam">', '</li>')
        for item in data:
            url    = self.cm.ph.getSearchGroups(item, '''href="([^"]+?)"''', 1, True)[0]
            icon   = self.cm.ph.getSearchGroups(item, '''"([^"]+?\.jpg)"''', 1, True)[0]
            if '' == url: continue
            title  = self.cleanHtmlStr(self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0])
            desc   = self.cleanHtmlStr(item)
            params = dict(cItem)
            params.update({'title':title, 'url':self.getFullUrl(url), 'icon':self.getFullUrl(icon), 'desc':desc, 'type':'video'})
            list.append(params)
        return list
        
    def getChannelsList(self, cItem):
        printDBG("WkylinewebcamsCom.getChannelsList")
        list = []
        cat = cItem.get('cat', None)
        lang = config.plugins.iptvplayer.skylinewebcams_lang.value
        self.lang = lang
        if None == cat:
            cItem = dict(cItem)
            cItem['url'] = self.MAIN_URL + lang + '.html'
            return self.getMainMenu(cItem)
        elif 'list_main_category' == cat:
            tab = self.mainMenuCache.get(cItem['idx'], [])
            for item in tab:
                params = dict(cItem)
                params.update(item)
                list.append(params)
        elif 'list_cams2' == cat:
            return self.listCams2(cItem)
        elif 'list_cams' == cat:
            return self.listCams(cItem)
        elif 'explore_item' == cat:
            return self.exploreItem(cItem)

        return list
        
    def getVideoLink(self, cItem):
        printDBG("WkylinewebcamsCom.getVideoLink")
        urlsTab = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return urlsTab
        url = self.cm.ph.getSearchGroups(data, '''['"](http[^"^']+?m3u8[^"^']*?)["']''', 1, True)[0]
        if url.startswith('http'):
            urlsTab = getDirectM3U8Playlist(url)
        data = self.cm.ph.getSearchGroups(data, '''href=['"]([^"^']+?/timelapse\.php[^"^']*?)['"][^>]+?title=['"]([^'^"]+?)['"]''', 2, True)
        name = data[1]
        url  = self.getFullUrl(data[0].replace('&amp;', '&'))
        if not url.startswith('http'): return urlsTab
        sts, data = self.cm.getPage(url)
        if not sts: return urlsTab
        url = self.cm.ph.getSearchGroups(data, '''url:['"]([^"^']+?)["']''', 1, True)[0]
        if '://' in url:
            urlsTab.append({'name':name, 'url':url})
        return urlsTab