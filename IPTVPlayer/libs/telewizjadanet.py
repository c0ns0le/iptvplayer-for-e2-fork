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

def GetConfigList():
    optionList = []
    return optionList
    
###################################################

class TelewizjadaNetApi:
    MAIN_URL   = 'http://www.telewizjada.net/'

    def __init__(self):
        self.COOKIE_FILE = GetCookieDir('telewizjadanet.cookie')
        self.cm = common()
        self.up = urlparser()
        self.http_params = {}
        self.http_params.update({'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIE_FILE})
        
    def getFullUrl(self, url):
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return self.MAIN_URL + url[1:]
        return url
        
    def cleanHtmlStr(self, str):
        return CBaseHostClass.cleanHtmlStr(str)
    
    def getChannelsList(self, cItem):
        printDBG("TelewizjadaNetApi.getChannelsList")
        
        url = self.MAIN_URL + 'live.php'
        http_params = dict(self.http_params)
        http_params['load_cookie'] = False
        sts, data = self.cm.getPage(url, http_params)
        if not sts: return []
        
        data = self.cm.ph.getDataBeetwenMarkers(data, '<ul id="channelListMain">', '</ul>', False)[1]
        data = re.compile('fillchannel\(([^\)]+?)\)').findall(data)
        
        channelsTab = []
        for item in data:
            item  = item.split(',')
            icon  = self.getFullUrl(item[1].replace('"', '').replace('_thumb.png', '.png'))
            title = icon.split('/')[-1].replace('.png', '').title()
            cid  = item[0]
            params = dict(cItem)
            params.update({'title':title, 'cid':cid, 'type':'video', 'icon':icon})
            channelsTab.append(params)
        return channelsTab

    def getVideoLink(self, cItem):
        printDBG("TelewizjadaNetApi.getVideoLink")
        
        url = self.MAIN_URL + 'live.php?cid=' + cItem['cid']
        sts, data = self.cm.getPage(url, self.http_params)
        if not sts: return []
        
        http_params = dict(self.http_params)
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0'}
        http_params.update({'header':HTTP_HEADER})
        http_params['header']['Referer'] = url
        
        url = self.MAIN_URL + 'channel_url.php'
        sts, data = self.cm.getPage(url, http_params, {'cid':cItem['cid']})
        if not sts: return []
        
        urlsTab = []
        data = data.strip()
        printDBG("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK [%s]" % data)
        if data.startswith('http://') and 'm3u8' in data:
            sessid = self.cm.getCookieItem(self.COOKIE_FILE, 'sessid')
            msec   = self.cm.getCookieItem(self.COOKIE_FILE, 'msec')
            statid = self.cm.getCookieItem(self.COOKIE_FILE, 'statid')
            url = strwithmeta(data, {'Cookie':'sessid=%s; msec=%s; statid=%s;' % (sessid, msec, statid)})
            urlsTab = getDirectM3U8Playlist(url)
        return urlsTab
