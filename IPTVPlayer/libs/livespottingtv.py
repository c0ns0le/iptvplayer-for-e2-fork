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

class LivespottingTvApi:
    MAIN_URL = 'http://livespotting.tv/'

    def __init__(self):
        self.COOKIE_FILE = GetCookieDir('livespottingtv.cookie')
        self.cm = common()
        self.up = urlparser()
        self.http_params = {}
        self.http_params.update({'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIE_FILE})
        self.cache = {}
        
    def cleanHtmlStr(self, str):
        return CBaseHostClass.cleanHtmlStr(str)
        
    def getChannelsList(self, cItem):
        printDBG("WkylinewebcamsCom.getChannelsList")
        list = []
        sts, data = self.cm.getPage('http://livespotting.tv/api/api.json')
        if not sts: return list
        try:
            data = byteify(json.loads(data))
            for item in data['streams']:
                if 'stream' not in item: continue
                try:
                    item = item['stream']['data']
                    title = item['content']['title']
                    icon  = item['images'].get('snapshot-343x192', '')
                    desc  = self.cleanHtmlStr(item['content'].get('longtext', ''))
                    camId = item['camID']['camid']
                    if camId.startswith('LS_'): camId = camId[3:]
                    url   =  'rtmp://stream.livespotting.tv/windit-edge/%s.stream live=1' % camId
                    list.append({'title':title, 'url':url, 'icon':icon, 'desc':desc})
                except: printExc()
        except:
            printExc()

        return list
