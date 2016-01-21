﻿# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, ArticleContent, RetHost, CUrlItem
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import CSelOneLink, printDBG, printExc, CSearchHistoryHelper, GetLogoDir, GetCookieDir
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html
###################################################

###################################################
# FOREIGN import
###################################################
from Components.config import config, ConfigInteger, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
from datetime import datetime, timedelta
from binascii import hexlify
import re
import urllib
import time
import random
try:    import simplejson as json
except: import json
###################################################


###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper
from Screens.MessageBox import MessageBox
###################################################
config.plugins.iptvplayer.tvpvod_premium  = ConfigYesNo(default = False)
config.plugins.iptvplayer.tvpvod_login    = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.tvpvod_password = ConfigText(default = "", fixed_size = False)

config.plugins.iptvplayer.tvpVodProxyEnable = ConfigYesNo(default = False)
config.plugins.iptvplayer.tvpVodDefaultformat = ConfigSelection(default = "590000", choices = [("360000",  "320x180"),
                                                                                               ("590000",  "398x224"),
                                                                                               ("820000",  "480x270"),
                                                                                               ("1250000", "640x360"),
                                                                                               ("1750000", "800x450"),
                                                                                               ("2850000", "960x540"),
                                                                                               ("5420000", "1280x720"),
                                                                                               ("6500000", "1600x900"),
                                                                                               ("9100000", "1920x1080") ])
config.plugins.iptvplayer.tvpVodUseDF    = ConfigYesNo(default = True)
config.plugins.iptvplayer.tvpVodNextPage = ConfigYesNo(default = True)

###################################################
# Config options for HOST
###################################################

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry("Strefa Widza", config.plugins.iptvplayer.tvpvod_premium))
    if config.plugins.iptvplayer.tvpvod_premium.value:
        optionList.append(getConfigListEntry("  email:", config.plugins.iptvplayer.tvpvod_login))
        optionList.append(getConfigListEntry("  hasło:", config.plugins.iptvplayer.tvpvod_password))
    optionList.append(getConfigListEntry("Domyślny format video",           config.plugins.iptvplayer.tvpVodDefaultformat))
    optionList.append(getConfigListEntry("Używaj domyślnego format video:", config.plugins.iptvplayer.tvpVodUseDF))
    optionList.append(getConfigListEntry("Korzystaj z proxy?",              config.plugins.iptvplayer.tvpVodProxyEnable))
    optionList.append(getConfigListEntry("Więcej jako następna strona",     config.plugins.iptvplayer.tvpVodNextPage))
    return optionList
###################################################

def gettytul():
    return 'vod.tvp.pl'

class TvpVod(CBaseHostClass):
    DEFAULT_ICON = 'http://sd-xbmc.org/repository/xbmc-addons/tvpvod.png'
    PAGE_SIZE = 12
    ALL_FORMATS = [{"video/mp4":"mp4"}, {"application/x-mpegurl":"m3u8"}, {"video/x-ms-wmv":"wmv"}] 
    REAL_FORMATS = {'m3u8':'ts', 'mp4':'mp4', 'wmv':'wmv'}
    MAIN_VOD_URL = "http://vod.tvp.pl/"
    LOGIN_URL = "https://www.tvp.pl/sess/ssologin.php"
    SEARCH_VOD_URL = MAIN_VOD_URL + 'szukaj?query=%s'
    HTTP_HEADERS = {}
    
    VOD_CAT_TAB  = [{'icon':DEFAULT_ICON, 'category':'vods_list_items1',    'title':'Polecamy',                  'url':MAIN_VOD_URL},
                    {'icon':DEFAULT_ICON, 'category':'vods_sub_categories', 'title':'Polecane',                  'marker':'Polecane'},
                    {'icon':DEFAULT_ICON, 'category':'vods_sub_categories', 'title':'VOD',                       'marker':'VOD'},
                    {'icon':DEFAULT_ICON, 'category':'vods_sub_categories', 'title':'Programy',                  'marker':'Programy'},
                    {'icon':DEFAULT_ICON, 'category':'vods_sub_categories', 'title':'Informacje i publicystyka', 'marker':'Informacje i publicystyka'},
                    #{'icon':DEFAULT_ICON, 'category':'vods_sub_categories', 'title':'Serwisy Informacyjne',     'marker':'Serwisy Informacyjne'},
                    #{'icon':DEFAULT_ICON, 'category':'vods_sub_categories', 'title':'Publicystyka',             'marker':'<li><h2>Publicystyka</h2></li>'},
                    {'icon':DEFAULT_ICON, 'category':'search',          'title':_('Search'), 'search_item':True},
                    {'icon':DEFAULT_ICON, 'category':'search_history',  'title':_('Search history')} ]
    
    def __init__(self):
        printDBG("TvpVod.__init__")
        CBaseHostClass.__init__(self, {'history':'TvpVod', 'cookie':'tvpvod.cookie', 'cookie_type':'MozillaCookieJar', 'proxyURL': config.plugins.iptvplayer.proxyurl.value, 'useProxy': config.plugins.iptvplayer.tvpVodProxyEnable.value})
        self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE, 'header':TvpVod.HTTP_HEADERS}
        self.loggedIn = None
        
    def _getPage(self, url, addParams = {}, post_data = None):
        
        try:
            import httplib
            def patch_http_response_read(func):
                def inner(*args):
                    try:
                        return func(*args)
                    except httplib.IncompleteRead, e:
                        return e.partial
                return inner
            prev_read = httplib.HTTPResponse.read
            httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)
        except: printExc()
        sts, data = self.cm.getPage(url, addParams, post_data)
        try: httplib.HTTPResponse.read = prev_read
        except: printExc()
        return sts, data
    
    def _cleanHtmlStr(self, str):
        str = str.replace('<', ' <').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return self.cm.ph.removeDoubles(clean_html(str), ' ').strip()
        
    def _getStr(self, v, default=''):
        return clean_html(self._encodeStr(v, default))
        
    def _encodeStr(self, v, default=''):
        if type(v) == type(u''): return v.encode('utf-8')
        elif type(v) == type(''): return v
        else: return default
        
    def _getNum(self, v, default=0):
        try: return int(v)
        except:
            try: return float(v)
            except: return default
            
    def _getFullUrl(self, url, baseUrl=None):
        if None == baseUrl: baseUrl = TvpVod.MAIN_VOD_URL
        if 0 < len(url) and not url.startswith('http'):
            if not baseUrl.endswith('/'):
                baseUrl += '/'
            if url.startswith('/'):
                url = url[1:]
            url =  baseUrl + url
        return url
        
    def getFormatFromBitrate(self, bitrate):
        tab = [ ("360000",  "320x180"), ("590000",  "398x224"), ("820000",  "480x270"), ("1250000", "640x360"),
                ("1750000", "800x450"), ("2850000", "960x540"), ("5420000", "1280x720"), ("6500000", "1600x900"), ("9100000", "1920x1080") ]
        ret = ''
        for item in tab:
            if int(bitrate) == int(item[0]):
                ret = item[1]
        if '' == ret: ret = 'Bitrate[%s]' % bitrate
        return ret
            
    def tryTologin(self):
        email = config.plugins.iptvplayer.tvpvod_login.value
        password = config.plugins.iptvplayer.tvpvod_password.value
        msg = 'Wystąpił problem z zalogowaniem użytkownika "%s"!' % email
        params = dict(self.defaultParams)
        params.update({'load_cookie': False})
        sts, data = self._getPage(TvpVod.LOGIN_URL, params)
        if sts:
            data = self.cm.ph.getDataBeetwenMarkers(data, '<fieldset>', '</fieldset>', False)[1]
            ref = self.cm.ph.getSearchGroups(data, 'name="ref".+?value="([^"]+?)"')[0]
            login = self.cm.ph.getSearchGroups(data, 'name="login".+?value="([^"]+?)"')[0]
            post_data = {'ref':ref, 'email':email, 'password':password, 'login':login, 'action':'login'}
            sts, data = self._getPage(TvpVod.LOGIN_URL, self.defaultParams, post_data)
            if sts and '"/sess/passwordreset.php"' not in data:
                if "Strefa Widza nieaktywna" in data:
                    msg = "Strefa Widza nieaktywna."
                    sts = False
                else:
                    msg = 'Użytkownik "%s" zalogowany poprawnie!' % email
            else: sts = False
        return sts, msg
       
    def listsTab(self, tab, cItem):
        printDBG("TvpVod.listsMainMenu")
        for item in tab:
            params = dict(cItem)
            params.update(item)
            params['name']  = 'category'
            self.addDir(params)
            
    def _addNavCategories(self, data, cItem, category):
        data = re.findall('href="([^"]+?)"[^>]*?>([^<]+?)<', data)
        for item in data:
            params = dict(cItem)
            params.update({'category':category, 'title':item[1], 'url':item[0]})
            self.addDir(params)
            
    def _getAjaxUrl(self, parent_id, location):
        if location == 'directory_series':
            order='';
            type='website'
            template ='listing_series.html'
            direct='&direct=false'
        elif location == 'directory_stats':
            order=''
            type='video'
            template ='listing_stats.html'
            direct='&filter=%7B%22playable%22%3Atrue%7D&direct=false'
        elif location == 'directory_video':
            order='&order=release_date_long,-1'
            type='video'
            template ='listing.html'
            direct='&filter=%7B%22playable%22%3Atrue%7D&direct=false'
        elif location == 'website':
            order='&order=release_date_long,-1'
            type='video'
            template ='listing.html'
            direct='&filter=%7B%22playable%22%3Atrue%7D&direct=false'
        else:
            order='&order=release_date_long,-1'
            type='video'
            template ='listing.html'
            direct='&filter=%7B%22playable%22%3Atrue%7D&direct=true'
            
        url = '/shared/listing.php?parent_id=' + parent_id + '&type=' + type + order + direct + '&template=directory/' + template + '&count=' + str(TvpVod.PAGE_SIZE) 
                    
        return self._getFullUrl(url)
            
    def listVodsSubCategories(self, cItem, category):
        printDBG("TvpVod.listVodsSubCategories")
        sts, data = self._getPage(TvpVod.MAIN_VOD_URL, self.defaultParams)
        if sts:
            data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="genNav">', '<div id="search">', False)[1]
            data = self.cm.ph.getDataBeetwenMarkers(data, cItem['marker'], '</ul>', False)[1]
            self._addNavCategories(data, cItem, category)
                
    def listListVodCategory1(self, cItem):
        if not cItem.get('list_items', False): # and 1 == cItem['url'].count('/'):
            baseItem = dict(cItem)
            baseItem.update({'list_items':True})
            self.listsMenuGroups(baseItem, cItem['category'])
            if len(self.currList):
                found = False
                for item in self.currList:
                    if baseItem['url'] == item['url']:
                        found = True
                        break
                if not found:
                    baseItem['title'] = _('--Wszystkie--')
                    self.currList.insert(0, baseItem)
        if 0 == len(self.currList):
            self.listItems1(cItem, 'vod_episodes')
        
        
    def listsMenuGroups(self, cItem, category):
        printDBG("TvpVod.listsGroupsType1")
        url = self._getFullUrl(cItem['url'])
        sts, data = self._getPage(url, self.defaultParams)
        if sts:
            # check if 
            data = self.cm.ph.getDataBeetwenMarkers(data, '<section id="menu"', '</section>', False)[1]
            self._addNavCategories(data, cItem, category)
        
    def listItems1(self, cItem, category):
        printDBG("TvpVod.listItems1")

        ajaxUrl = ''
        page = cItem.get('page', 1)
        url = self._getFullUrl(cItem['url'])
        
        if '/shared/' in url:
            url += '&page=%d' %(page)
            ajaxUrl = url
        
        sts, data = self._getPage(url, self.defaultParams)
        if not sts: return
        
        if '<section id="emisje">' in data:
            return self.listItems2(cItem, category, data)
        
        if 'popular' == category:
            itemMarker = '<li class="series">'
            sectionMarker = itemMarker
        else:
            itemMarker = '<div class="item">'
            sectionMarker = itemMarker
        
        if '' == ajaxUrl:
            tmp = self.cm.ph.getSearchGroups(data, "vod\.loadItems\.init\('([0-9]+?)'\,'([^']+?)'", 2)
            if tmp[0] != '' and tmp[1] != '': 
                ajaxUrl = self._getAjaxUrl(tmp[0], tmp[1])
        
        if '/shared/' not in url:
            data = self.cm.ph.getDataBeetwenMarkers(data, sectionMarker, '</section>', True)[1]
        
        printDBG("TvpVod.listItems1 start parse")
        if sts:
            data = data.split(itemMarker)
            if len(data): del data[0]
            for item in data:
                icon = self.cm.ph.getSearchGroups(item, 'src="([^"]+?)"')[0]
                desc = self.cm.ph.getDataBeetwenMarkers(item, '<p>', '</div>', False)[1]
                tmp  = self.cm.ph.getDataBeetwenMarkers(item, '<strong class="fullTitle">', '</strong>', False)[1]
                if '' == tmp: tmp = self.cm.ph.getDataBeetwenMarkers(tmp, '<strong class="shortTitle">', '</strong>', False)[1]
                tmp = self.cm.ph.getSearchGroups(tmp, 'href="([^"]+?)"[^>]+?>([^<]+?)<', 2)
                url = tmp[0]
                title = tmp[1]
                if 'class="new"' in item: title += _(', nowość')
                if 'class="pay"' in item: title += _(', materiał płatny')
                duration = self.cm.ph.getSearchGroups(item, 'class="duration[^>]+?>([^<]+?)</li>')[0]
                if '' != duration: title += ', ' + duration
                params = dict(cItem)
                params.update({'category':category, 'title':title, 'url':url, 'icon':icon, 'desc':desc, 'page':1})
                if '' ==  duration:
                    self.addDir(params)
                else:
                    self.addVideo(params)
        # add next page if needed
        if len(self.currList):
            if '' != ajaxUrl:
                url = ajaxUrl + '&page=%d' %(page+1)
                sts, data = self._getPage(url, self.defaultParams)
                if sts and itemMarker in data: 
                    params = dict(cItem)
                    params.update({'page':page+1, 'url':ajaxUrl})
                    if config.plugins.iptvplayer.tvpVodNextPage.value:
                        params['title'] = _("Następna strona")
                        self.addDir(params)
                    else:
                        params['title'] = _('More')
                        self.addMore(params)
                
    def listItems2(self, cItem, category, data):
        printDBG("TvpVod.listItems2")
        itemMarker = '<div class="'
        sectionMarker = '<section id="emisje">'

        tmp = self.cm.ph.getDataBeetwenMarkers(data, 'class="siteNewscast">', '</section>', False)[1]
        icon = self.cm.ph.getSearchGroups(tmp, 'src="([^"]+?)"')[0]
        desc = self.cm.ph.getDataBeetwenMarkers(tmp, '<p>', '</div>', False)[1]
        data = self.cm.ph.getDataBeetwenMarkers(data, sectionMarker, '</section>', True)[1]
        
        printDBG("TvpVod.listItems2 start parse")
        data = data.split(itemMarker)
        if len(data): del data[0]
        for item in data:
            url = self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0]
            title = self._cleanHtmlStr('<' + item)
            params = dict(cItem)
            params.update({'category':category, 'title':title, 'url':url, 'icon':icon, 'desc':desc, 'page':0})
            self.addVideo(params)
    
    def listEpisodes(self, cItem):
        printDBG("TvpVod.listEpisodes")
        if not cItem.get('list_episodes', False):
            baseItem = dict(cItem)
            baseItem.update({'list_episodes':True})
            self.listsMenuGroups(baseItem, cItem['category'])
        if 0 == len(self.currList):
            self.listItems1(cItem, 'vod_series')

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG("TvpVod.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]" % (cItem, searchPattern, searchType))
        searchPattern = urllib.quote_plus(searchPattern)
        url = TvpVod.SEARCH_VOD_URL % urllib.quote(searchPattern)
        page = cItem.get('page', 1)
        if page > 1:
            url += '&order=desc&page=%s' % page
        
        sts, data = self._getPage(url, self.defaultParams)
        if not sts: return
        
        if ('&page=%s"' % (page+1)) in data:
            nextPage = True
        else:
            nextPage = False
        
        data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="content search_content">', '</section>', False)[1]
        data = data.split('<div class="item">')
        if len(data): del data[0]
        for item in data:
            url  = self._getFullUrl( self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0] )
            icon = self._getFullUrl( self.cm.ph.getSearchGroups(item, 'src="([^"]+?)"')[0] )
            desc = self.cm.ph.getDataBeetwenMarkers(item, '<p>', '</div>', False)[1]
            title  = self.cm.ph.getDataBeetwenMarkers(item, '<strong class="fullTitle">', '</strong>', False)[1]
            if '' == title: title = self.cm.ph.getDataBeetwenMarkers(tmp, '<strong class="shortTitle">', '</strong>', False)[1]
            title = self._cleanHtmlStr(title)
            if 'class="new"' in item: title += _(', nowość')
            if 'class="pay"' in item: title += _(', materiał płatny')
            duration = self.cm.ph.getSearchGroups(item, 'class="duration[^>]+?>([^<]+?)</li>')[0]
            if '' != duration: title += ', ' + duration
            
            object_id = self.cm.ph.getSearchGroups(url, '/([0-9]+?)/')[0]
            #object_id = self.getObjectID(url)
            params = dict(cItem)
            #if '' == object_id:
            if '' == object_id or not self.isVideoData(object_id):
                params.update({'category':'vod_episodes', 'title':title, 'url':url, 'icon':icon, 'desc':desc, 'page':1})
                self.addDir(params)
            else:
                params.update({'title':title, 'url': url, 'icon':icon, 'desc':desc})
                self.addVideo(params)
        
        if nextPage:    
            params = dict(cItem)
            params.update({'page':page+1})
            if config.plugins.iptvplayer.tvpVodNextPage.value:
                params['title'] = _("Następna strona")
                self.addDir(params)
            else:
                params['title'] = _('More')
                self.addMore(params)
            
    def getObjectID(self, url):
        sts, data = self.cm.getPage(url, self.defaultParams)
        if not sts: return ''
        asset_id = self.cm.ph.getSearchGroups(data, 'object_id=([0-9]+?)[^0-9]')[0]
        return asset_id
                
    def getLinksForVideo(self, cItem):
        asset_id = str(cItem.get('object_id', ''))
        url = self._getFullUrl(cItem.get('url', ''))
        if '' == asset_id:
            asset_id = self.getObjectID(url)

        return self.getVideoLink(asset_id)
        
    def isVideoData(self, asset_id):
        sts, data = self.cm.getPage( 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?mime_type=video%2Fmp4&object_id=' + asset_id, self.defaultParams)
        return not 'NOT_FOUND' in data
        
    def getVideoLink(self, asset_id):
        printDBG("getVideoLink asset_id [%s]" % asset_id)
        sts, data = self.cm.getPage( 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?mime_type=video%2Fmp4&object_id=' + asset_id, self.defaultParams)
        if False == sts:
            printDBG("getVideoLink problem")
        
        videoTab = []
        try:
            data = json.loads( data )
            
            def _getVideoLink(data, FORMATS):
                videoTab = []
                for item in data['formats']:
                    if item['mimeType'] in FORMATS.keys():
                        formatType = FORMATS[item['mimeType']].encode('utf-8')
                        format = self.REAL_FORMATS.get(formatType, '')
                        name = self.getFormatFromBitrate( str(item['totalBitrate']) ) + '\t ' + formatType
                        url = item['url'].encode('utf-8')
                        if 'm3u8' == formatType:
                            videoTab.extend( getDirectM3U8Playlist(url) )
                        else:
                            meta = {'iptv_format':format}
                            if config.plugins.iptvplayer.tvpVodProxyEnable.value:
                                meta['http_proxy'] = config.plugins.iptvplayer.proxyurl.value
                            videoTab.append( {'name' : name, 'bitrate': str(item['totalBitrate']), 'url' : self.up.decorateUrl(url, meta) })
                if 1 < len(videoTab):
                    max_bitrate = int(config.plugins.iptvplayer.tvpVodDefaultformat.value)
                    def __getLinkQuality( itemLink ):
                        return int(itemLink['bitrate'])
                    oneLink = CSelOneLink(videoTab, __getLinkQuality, max_bitrate)
                    if config.plugins.iptvplayer.tvpVodUseDF.value:
                        videoTab = oneLink.getOneLink()
                    else:
                        videoTab = oneLink.getSortedLinks()
                return videoTab
            
            for item in TvpVod.ALL_FORMATS:
                videoTab = _getVideoLink(data, item )
                if len(videoTab):
                    break
        except:
            printExc("getVideoLink exception") 
        return videoTab
        
    def getFavouriteData(self, cItem):
        return str(cItem['url'])
        
    def getLinksForFavourite(self, fav_data):
        if None == self.loggedIn:
            premium = config.plugins.iptvplayer.tvpvod_premium.value
            if premium: self.loggedIn, msg = self.tryTologin()
            
        try:
            ok = int(fav_data)
            if ok: return self.getVideoLink(fav_data)
        except: pass
        return getLinksForVideo(self, {'url':fav_data})
    
    def handleService(self, index, refresh=0, searchPattern='', searchType=''):
        printDBG('TvpVod.handleService start')
        if None == self.loggedIn:
            premium = config.plugins.iptvplayer.tvpvod_premium.value
            if premium:
                self.loggedIn, msg = self.tryTologin()
                self.sessionEx.open(MessageBox, msg, type = MessageBox.TYPE_INFO, timeout = 10 )

        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name     = self.currItem.get("name", None)
        category = self.currItem.get("category", '')
        printDBG( "TvpVod.handleService: ---------> name[%s], category[%s] " % (name, category) )
        searchPattern = self.currItem.get("search_pattern", searchPattern)
        self.currList = [] 

        if None == name:
            self.listsTab(TvpVod.VOD_CAT_TAB, {'name':'category'})
    # POPULAR
        elif category == 'vods_list_items1':
            self.listItems1(self.currItem, 'popular')
    # VOD CATEGORIES
        elif category == 'vods_sub_categories':
            self.listVodsSubCategories(self.currItem, 'vod_category_1')
    # LIST VOD CATEGORY 1
        elif category == 'vod_category_1':
            self.listListVodCategory1(self.currItem)
    # LIST EPISODES
        elif category == 'vod_episodes':
            self.listEpisodes(self.currItem)
    #WYSZUKAJ
        elif category == "search":
            cItem = dict(self.currItem)
            cItem.update({'category':'list_search', 'searchPattern':searchPattern, 'searchType':searchType, 'search_item':False})            
            self.listSearchResult(cItem, searchPattern, searchType)
        elif category == "list_search":
            cItem = dict(self.currItem)
            searchPattern = cItem.get('searchPattern', '')
            searchType    = cItem.get('searchType', '')
            self.listSearchResult(cItem, searchPattern, searchType)
    #HISTORIA WYSZUKIWANIA
        elif category == "search_history":
            self.listsHistory({'name':'history', 'category': 'search'}, 'desc', _("Type: "))
        else:
            printExc()
        CBaseHostClass.endHandleService(self, index, refresh)

class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, TvpVod(), True, [CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])
    
    def getLogoPath(self):
        return RetHost(RetHost.OK, value = [GetLogoDir('tvpvodlogo.png')])

    def getLinksForVideo(self, Index = 0, selItem = None):
        retCode = RetHost.ERROR
        retlist = []
        if not self.isValidIndex(Index): return RetHost(retCode, value=retlist)

        urlList = self.host.getLinksForVideo(self.host.currList[Index])
        for item in urlList:
            need_resolve = 0
            name = self.host._getStr( item["name"] )
            url  = item["url"]
            retlist.append(CUrlItem(name, url, need_resolve))

        return RetHost(RetHost.OK, value = retlist)
    # end getLinksForVideo
    
    def converItem(self, cItem):
        hostList = []
        searchTypesOptions = []
        hostLinks = []
        type = CDisplayListItem.TYPE_UNKNOWN
        possibleTypesOfSearch = None

        if 'category' == cItem['type']:
            if cItem.get('search_item', False):
                type = CDisplayListItem.TYPE_SEARCH
                possibleTypesOfSearch = searchTypesOptions
            else:
                type = CDisplayListItem.TYPE_CATEGORY
        elif cItem['type'] == 'video':
            type = CDisplayListItem.TYPE_VIDEO
        elif 'more' == cItem['type']:
            type = CDisplayListItem.TYPE_MORE
        elif 'audio' == cItem['type']:
            type = CDisplayListItem.TYPE_AUDIO
            
        if type in [CDisplayListItem.TYPE_AUDIO, CDisplayListItem.TYPE_VIDEO]:
            url = cItem.get('url', '')
            if '' != url:
                hostLinks.append(CUrlItem("Link", url, 1))
            
        title       =  self.host._getStr( cItem.get('title', '') )
        description =  self.host._getStr( cItem.get('desc', '') ).strip()
        icon        =  self.host._getStr( cItem.get('icon', '') )
        if '' == icon: icon = TvpVod.DEFAULT_ICON
        
        return CDisplayListItem(name = title,
                                description = description,
                                type = type,
                                urlItems = hostLinks,
                                urlSeparateRequest = 1,
                                iconimage = icon,
                                possibleTypesOfSearch = possibleTypesOfSearch)

    def getSearchItemInx(self):
        try:
            list = self.host.getCurrList()
            for i in range( len(list) ):
                if list[i]['category'] == 'search':
                    return i
        except:
            printDBG('getSearchItemInx EXCEPTION')
            return -1

    def setSearchPattern(self):
        try:
            list = self.host.getCurrList()
            if 'history' == list[self.currIndex]['name']:
                pattern = list[self.currIndex]['title']
                search_type = list[self.currIndex]['search_type']
                self.host.history.addHistoryItem( pattern, search_type)
                self.searchPattern = pattern
                self.searchType = search_type
        except:
            printDBG('setSearchPattern EXCEPTION')
            self.searchPattern = ''
            self.searchType = ''
        return
