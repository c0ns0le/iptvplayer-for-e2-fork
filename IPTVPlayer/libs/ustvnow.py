﻿# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
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
#config.plugins.iptvplayer.ustvnow_streamprotocol = ConfigSelection(default = "2", choices = [("1", "rtmp"),("2", "HLS - m3u8")]) 
#config.plugins.iptvplayer.ustvnow_defquality     = ConfigSelection(default = "1", choices = [("1", "Low"),("2", "Medium"),("3", "High")]) 
#config.plugins.iptvplayer.ustvnow_premium        = ConfigYesNo(default = False)
config.plugins.iptvplayer.ustvnow_login          = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.ustvnow_password       = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.ustvnow_only_available = ConfigYesNo(default = True)
config.plugins.iptvplayer.ustvnow_epg            = ConfigYesNo(default = True)

def GetConfigList():
    optionList = []
    #optionList.append(getConfigListEntry( _("Stream type") + ": ", config.plugins.iptvplayer.ustvnow_streamprotocol))
    #optionList.append(getConfigListEntry( _("Quality") + ": ", config.plugins.iptvplayer.ustvnow_defquality))
    #optionList.append(getConfigListEntry( _("Subscription") + ": ", config.plugins.iptvplayer.ustvnow_premium))
    optionList.append(getConfigListEntry( _("Email") + ": ", config.plugins.iptvplayer.ustvnow_login))
    optionList.append(getConfigListEntry( _("Password") + ": ", config.plugins.iptvplayer.ustvnow_password))
    optionList.append(getConfigListEntry( _("List only channels with subscription") + ": ", config.plugins.iptvplayer.ustvnow_only_available))
    optionList.append(getConfigListEntry( _("Get EPG") + ": ", config.plugins.iptvplayer.ustvnow_epg))
    
    return optionList
    
###################################################

class UstvnowApi:
    MAIN_URL = 'http://m.ustvnow.com/'
    LOG_URL  = MAIN_URL + 'iphone/1/live/login'
    LIVE_URL = MAIN_URL + 'iphone/1/live/playingnow'
    HTTP_HEADER  = { 'User-Agent': 'Mozilla/5.0', 'Referer': MAIN_URL }

    def __init__(self):
        self.cm = common()
        self.up = urlparser()
        self.sessionEx = MainSessionWrapper()
        self.cookiePath = GetCookieDir('ustvnow.cookie')
        self.token = ''
        
        HTTP_HEADER= dict(self.HTTP_HEADER)
        HTTP_HEADER.update( {'Content-Type':'application/x-www-form-urlencoded'} )
        self.defParams = {'header':HTTP_HEADER, 'cookiefile': self.cookiePath, 'use_cookie': True, 'load_cookie':True, 'save_cookie':True}
        
    def _getFullUrl(self, url):
        if url.startswith('//'):
            return 'http:' + url
        if url.startswith('/'):
            url = url[1:]
        if 0 < len(url) and not url.startswith('http'):
            url =  self.MAIN_URL + url
        if not self.MAIN_URL.startswith('https://'):
            url = url.replace('https://', 'http://')
        return url
        
    def cleanHtmlStr(self, str):
        return CBaseHostClass.cleanHtmlStr(str)
        
    def _getChannelsNames(self):
        printDBG("UstvnowApi._getChannelsNames")
        url = 'http://m.ustvnow.com/gtv/1/live/listchannels?%s' % urllib.urlencode({'token': self.token})
        sts, data = self.cm.getPage(url)
        if not sts: return []
        
        channelList = []
        try:
            data = byteify(json.loads(data))
            for item in data['results']['streamnames']:
                params = {}
                params['sname']         = item['sname']
                params['img']           = item['img']
                params['scode']         = item['scode']
                params['t']             = item['t']
                params['callsign']      = item['callsign']
                params['prgsvcid']      = item['prgsvcid']
                params['data_provider'] = item['data_provider']
                params['lang']          = item['lang']
                params['af']            = item['af']
                channelList.append(params)
                
        except:
            printExc()
        return channelList
    
    def getChannelsList(self, cItem):
        printDBG("UstvnowApi.getChannelsList")
        
        login  = config.plugins.iptvplayer.ustvnow_login.value
        passwd = config.plugins.iptvplayer.ustvnow_password.value

        if '' != login.strip() and '' != passwd.strip():
            self.token = self.doLogin(login, passwd)
            if self.token == '':
                self.sessionEx.open(MessageBox, _('An error occurred when try to sign in the user "%s.\nPlease check your login credentials and try again later..."') % login, type = MessageBox.TYPE_INFO, timeout = 10 )
                return []
        else:
            self.sessionEx.open(MessageBox, _('You need to enter email and password in configuration.'), type = MessageBox.TYPE_INFO, timeout = 10 )
            return []
            
    
        sts, data = self.cm.getPage(self.LIVE_URL, self.defParams)
        if not sts: return []
        
        channelsNames = self._getChannelsNames()
        channelsTab = []
        data = self.cm.ph.getDataBeetwenMarkers(data, '<div data-role="content" data-theme="c">', '</ul>', False)[1]
        data = data.split('</li>')
        prgsvcidMap = {}
        for item in data:
            url  = self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0]
            ui   = url.split('ui-page=')[-1]
            icon = self.cm.ph.getSearchGroups(item, 'src="([^"]+?)"')[0]
            desc = self.cleanHtmlStr(item)
            params = dict(cItem)
            params.pop('url')
            params.update({'priv_url':self._getFullUrl(url), 'ui_page':ui, 'icon':icon, 'desc':desc})
            
            for nameItem in channelsNames:
                if nameItem['img'] in icon:
                    if config.plugins.iptvplayer.ustvnow_only_available.value and 0 == nameItem['t']:
                        break
                    params['title'] = nameItem['sname'] + ' [%s]' % nameItem['t']
                    params['prgsvcid'] = nameItem['prgsvcid']
                    prgsvcidMap[params['prgsvcid']] = len(channelsTab)
                    channelsTab.append(params)
                    break
                    
        if config.plugins.iptvplayer.ustvnow_epg.value:
            sts, data = self.cm.getPage(self.MAIN_URL + 'gtv/1/live/channelguide', self.defParams)
            if sts:
                try:
                    data = byteify(json.loads(data))
                    for item in data['results']:
                        if item['prgsvcid'] in prgsvcidMap:
                            idx = prgsvcidMap[item['prgsvcid']]
                            channelsTab[idx]['desc'] += '[/br][/br] [%s %s][/br]%s[/br]%s[/br]%s[/br]%s' % (item.get('event_date', ''), item.get('event_time', ''), item.get('title', ''), item.get('synopsis', ''), item.get('description', ''), item.get('episode_title', ''))
                except:
                    printExc()
            
        return channelsTab
        
    def doLogin(self, login, password):
        printDBG("UstvnowApi.doLogin")
        token = ''
        post_data = {'username':login, 'password':password, 'device':'iphone'}
        sts, data = self.cm.getPage(self.LOG_URL, self.defParams, post_data)
        if sts:
            token = self.cm.getCookieItem(self.cookiePath, 'token')
        return token
        
    def getVideoLink(self, cItem):
        printDBG("UstvnowApi.getVideoLink")
        
        sts, data = self.cm.getPage(cItem['priv_url'], self.defParams)
        if not sts: return []
        
        url = self.cm.ph.getSearchGroups(data, 'for="popup-%s"[^>]*?href="([^"]+?)"[^>]*?>' % cItem['ui_page'])[0]
        url = self._getFullUrl(url)
        
        sts, data = self.cm.getPage(url, self.defParams)
        if not sts: return []
        
        url = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
        urlsTab = []
        tmp = getDirectM3U8Playlist(strwithmeta(url, {'User-Agent':self.HTTP_HEADER['User-Agent']}), cookieParams = {'cookiefile': self.cookiePath, 'use_cookie': True, 'load_cookie':True, 'save_cookie':True})
        hdntl = self.cm.getCookieItem(self.cookiePath, 'hdntl')
        
        for item in tmp:
            item['url'] = urlparser.decorateUrl(item['url'], {'User-Agent':self.HTTP_HEADER['User-Agent'], 'Cookie':"hdntl=%s" % urllib.unquote(hdntl)})
            urlsTab.append(item)
        
        return urlsTab
