# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.extractor.youtube import YoutubeIE
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html, unescapeHTML
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, remove_html_markup, CSelOneLink, GetCookieDir, byteify
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common, CParsingHelper
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import decorateUrl, getDirectM3U8Playlist, getF4MLinksWithMeta
###################################################

###################################################
# FOREIGN import
###################################################
import re
import base64
import copy
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
try: import json
except: import simplejson as json
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.moonwalk_format    = ConfigSelection(default = "m3u8", choices = [("hls/m3u8", "m3u8"),("f4m", "f4m/hds")]) 
config.plugins.iptvplayer.moonwalk_df_format = ConfigSelection(default = 360, choices = [(0, _("the worst")), (360, "360p"), (480, "480p"), (720, "720"), (9999, _("the best"))])
config.plugins.iptvplayer.moonwalk_use_df    = ConfigYesNo(default = False)

class MoonwalkParser():
    USER_AGENT = 'Mozilla/5.0'
    def __init__(self):
        self.cm = common()
        self.HTTP_HEADER= {'User-Agent':self.USER_AGENT, 'Referer':''}
        self.COOKIEFILE = GetCookieDir("moonwalkcc.cookie")
        self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE}
        self.baseUrl = ''
        
    def _setBaseUrl(self, url):
        self.baseUrl = 'http://' + self.cm.ph.getDataBeetwenMarkers(url, '://', '/', False)[1]
        
    def _getSecurityData(self, data):
        printDBG('MoonwalkParser._getSecurityData')
        sec_header = {}
        post_data = {}

        contentData = self.cm.ph.getDataBeetwenMarkers(data, 'setRequestHeader|', '|beforeSend', False)[1]
        csrfToken = self.cm.ph.getSearchGroups(data, '<meta name="csrf-token" content="([^"]+?)"')[0] 
        
        cd = self.cm.ph.getSearchGroups(data, 'var condition_detected = ([^;]+?);')[0]
        if 'true' == cd: cd = 1
        else: cd = 0
        data = self.cm.ph.getDataBeetwenMarkers(data, '/sessions/create_session', '.success', False)[1]
        partner = self.cm.ph.getSearchGroups(data, 'partner: ([^,]+?),')[0]
        if 'null' in partner: partner = ''
        d_id = self.cm.ph.getSearchGroups(data, 'd_id: ([^,]+?),')[0]
        video_token = self.cm.ph.getSearchGroups(data, "video_token: '([^,]+?)'")[0]
        content_type = self.cm.ph.getSearchGroups(data, "content_type: '([^']+?)'")[0]
        access_key = self.cm.ph.getSearchGroups(data, "access_key: '([^']+?)'")[0]

        sec_header['Content-Data'] = base64.b64encode(contentData)
        sec_header['X-CSRF-Token'] = csrfToken
        sec_header['X-Requested-With'] = 'XMLHttpRequest'
        post_data = {'partner':partner, 'd_id':d_id, 'video_token':video_token, 'content_type':content_type, 'access_key':access_key, 'cd':cd}

        return sec_header, post_data

    def getDirectLinks(self, url):
        printDBG('MoonwalkParser.getDirectLinks')
        linksTab = []
        try:
            self._setBaseUrl(url)
            params = copy.deepcopy(self.defaultParams)
            params['header']['Referer'] = url
            sts, data = self.cm.getPage( url, params)
            if not sts: return []
            
            sec_header, post_data = self._getSecurityData(data)
            params['header'].update(sec_header)
            
            sts, data = self.cm.getPage( '%s/sessions/create_session' % self.baseUrl, params, post_data)
            if not sts: return []
            
            data = byteify( json.loads(data) )
            if 'm3u8' == config.plugins.iptvplayer.moonwalk_format.value:
                tmpTab = getDirectM3U8Playlist(data["manifest_m3u8"])
                def __getLinkQuality( itemLink ):
                    return itemLink['heigth']
                if config.plugins.iptvplayer.moonwalk_use_df.value:
                    maxRes = config.plugins.iptvplayer.moonwalk_df_format.value
                    tmpTab = CSelOneLink(tmpTab, __getLinkQuality, maxRes).getSortedLinks()
                    tmpTab = [tmpTab[0]]
                for item in tmpTab:
                    linksTab.append({'name':'[hls/m3u8] %sp' % __getLinkQuality(item), 'url':item['url']})
            else:
                tmpTab = getF4MLinksWithMeta(data["manifest_f4m"])
                def __getLinkQuality( itemLink ):
                    printDBG(itemLink)
                    bitrate = int(self.cm.ph.getDataBeetwenMarkers(itemLink['name'], 'bitrate[', ']', False)[1])
                    if bitrate < 400:
                        return 360
                    elif bitrate < 700:
                        return 480
                    elif bitrate < 1200:
                        return 720
                    return 1080
                if config.plugins.iptvplayer.moonwalk_use_df.value:
                    maxRes = config.plugins.iptvplayer.moonwalk_df_format.value
                    tmpTab = CSelOneLink(tmpTab, __getLinkQuality, maxRes).getSortedLinks()
                    tmpTab = [tmpTab[0]]
                for item in tmpTab:
                    linksTab.append({'name':'[f4m/hds] %sp' % __getLinkQuality(item), 'url':item['url']})
        except:
            printExc()
        return linksTab
        
    def getSeasonsList(self, url):
        printDBG('MoonwalkParser.getSeasonsList')
        seasonsTab = []
        try:
            self._setBaseUrl(url)
            params = copy.deepcopy(self.defaultParams)
            params['header']['Referer'] = url
            sts, data = self.cm.getPage( url, params)
            if not sts: return []
            
            seasonData = self.cm.ph.getDataBeetwenMarkers(data, 'id="season"', '</select>', False)[1]
            printDBG(seasonData)
            seasonData = re.compile('<option[^>]+?value="([0-9]+?)">([^<]+?)</option>').findall(seasonData)
            seasonMainUrl = self.cm.ph.getDataBeetwenMarkers(data, "$('#season').val();", '});', False)[1]
            seasonMainUrl = self.cm.ph.getSearchGroups(seasonMainUrl, "var url = '(http[^']+?)'")[0] + '?season='
            if not seasonMainUrl.startswith('http'): 
                return []
            
            for item in seasonData:
                seasonsTab.append({'title':item[1], 'id':int(item[0]), 'url': seasonMainUrl + item[0]})
        except:
            printExc()
        return seasonsTab
        
    def getEpiodesList(self, url, seasonIdx):
        printDBG('MoonwalkParser.getEpiodesList')
        episodesTab = []
        try:
            self._setBaseUrl(url)
            params = copy.deepcopy(self.defaultParams)
            params['header']['Referer'] = url
            sts, data = self.cm.getPage( url, params)
            if not sts: return []
            
            episodeData = self.cm.ph.getDataBeetwenMarkers(data, 'id="episode"', '</select>', False)[1]
            episodeData = re.compile('<option[^>]+?value="([0-9]+?)">([^<]+?)</option>').findall(episodeData)
            episodeMainUrl = self.cm.ph.getDataBeetwenMarkers(data, "$('#episode').val();", '});', False)[1]
            episodeMainUrl = self.cm.ph.getSearchGroups(episodeMainUrl, "var url = '(http[^']+?)'")[0] + '?season=' + str(seasonIdx) + '&episode='
            if not episodeMainUrl.startswith('http'): 
                return []
            
            for item in episodeData:
                episodesTab.append({'title':item[1], 'id':int(item[0]), 'url': episodeMainUrl + item[0]})
        except:
            printExc()
        return episodesTab
