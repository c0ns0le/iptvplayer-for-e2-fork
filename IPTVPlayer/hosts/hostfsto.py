﻿# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, RetHost, CUrlItem, ArticleContent
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSearchHistoryHelper, remove_html_markup, GetLogoDir, GetCookieDir, byteify
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common, CParsingHelper
import Plugins.Extensions.IPTVPlayer.libs.urlparser as urlparser
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.moonwalkcc import MoonwalkParser
from Plugins.Extensions.IPTVPlayer.libs.youtubeparser import YouTubeParser
###################################################

###################################################
# FOREIGN import
###################################################
import copy
import re
import urllib
import base64
import random
import time
try:    import json
except: import simplejson as json
from datetime import datetime
from urlparse import urlparse
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
###################################################


###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper
from Screens.MessageBox import MessageBox
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.fsto_proxy_enable = ConfigYesNo(default = False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_('Use ru proxy server to get file lists'), config.plugins.iptvplayer.fsto_proxy_enable))
    return optionList
###################################################


def gettytul():
    return 'http://fs.to/'

class FsTo(CBaseHostClass):
    DEFAULT_ICON_URL = 'http://inext.ua/wp-content/uploads/2014/04/fsto_Icon-570x380.jpg'
    MAIN_URL = 'http://fs.to/'
    MAIN_CAT_TAB = [
                    {'category':'search',                   'title':_('Search'), 'search_item':True},
                    {'category':'search_history',           'title':_('Search history')} ]
    
    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'FsTo', 'cookie':'FsTo.cookie'})
        self.searchTypesOptions = []
        self.filtesCache = []
        self.sortKeyCache = []
        self.searchCache = {}
    
    def _getFullUrl(self, url, baseUrl=None):
        if baseUrl == None:
            baseUrl = self.MAIN_URL
        if url.startswith('//'):
            url = 'http:' + url
        elif 0 < len(url) and not url.startswith('http'):
            if url.startswith('/'):
                url = url[1:]
            url =  baseUrl + url
        if baseUrl.startswith('https://'):
            url = url.replace('https://', 'http://')
        return url
        
    def listsTab(self, tab, cItem, type='dir'):
        printDBG("FsTo.listsTab")
        for item in tab:
            params = dict(cItem)
            params.update(item)
            params['name']  = 'category'
            if type == 'dir':
                self.addDir(params)
            else: self.addVideo(params)
            
    def getSearchTypesOptions(self):
        return self.searchTypesOptions
    
    def listMainMenu(self):
        printDBG("FsTo.listMainMenu")
        
        # get main url
        params = {'return_data':False}
        try:
            sts, response = self.cm.getPage(self.MAIN_URL, params)
            url = response.geturl()
            response.close()
            parsed_uri = urlparse( url )
            self.MAIN_URL = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        except:
            printExc()
            return []
        
        printDBG("MAIN_URL[%s]" % self.MAIN_URL)
        
        self.searchTypesOptions = []
        categoryTab = []
        sts, data = self.cm.getPage(self.MAIN_URL)
        if not sts: return
        data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="b-header__menu">', '</td>', False)[1]
        data = re.compile('<a[^<]+?href="([^"]+?)"[^<]*?__menu-section-link[^<]*?>([^<]+?)</a>').findall(data)
        for item in data:
            url   = self._getFullUrl(item[0])
            title = self.cleanHtmlStr(item[1])
            if len(item[0]) > 3:
                self.searchTypesOptions.append((title, item[0][1:-1]))
                params = {'category':'list_cats', 'title': title, 'url':url, 'icon':self.DEFAULT_ICON_URL }
                categoryTab.append( params )
        if len(categoryTab):
            categoryTab.extend(self.MAIN_CAT_TAB)
        
        self.listsTab(categoryTab, {'name':'category'})
        
    def listCategories(self, cItem, category):
        printDBG("FsTo.listCategories")
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return
        data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="b-subsection-menu__items">', '</div>', False)[1]
        data = re.compile('<a[^<]+?href="([^"]+?)"[^<]*?>([^<]+?)</a>').findall(data)
        for item in data:
            params = dict(cItem)
            params.update({'title':item[1], 'url':self._getFullUrl(item[0]), 'category':category})
            self.addDir(params)
            
    def listFilters(self, cItem, category):
        printDBG("FsTo.listFilters")
        self.filtesCache = []
        self.sortKeyCache = []
    
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return
        
        fData = self.cm.ph.getDataBeetwenMarkers(data, '<table>', '</table>', False)[1]
        fData = self.cm.ph.getAllItemsBeetwenMarkers(fData, '<td>', '</td>', False)
        for fItem in fData:
            gFilterTitle = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(fItem, '<li>', '</li>', False)[1] )
            self.filtesCache.append({'title':gFilterTitle, 'items':[]})

            fIdx = len(self.filtesCache) - 1
            if fIdx < 0: continue
            vData = re.compile('<a[^<]+?href="([^"]+?)"[^<]*?>(.+?)</a>').findall(fItem)
            for vItem in vData:
                if len(vItem[0]) > 1:
                    self.filtesCache[fIdx]['items'].append({'ftype':'normal', 'title':self.cleanHtmlStr(vItem[1]), 'url':self._getFullUrl(vItem[0])})
                
            # add more item
            mData = self.cm.ph.getDataBeetwenMarkers(fItem, 'class="more-custom"', '>', False)[1]
            if mData != '':
                try:
                    count = int( self.cm.ph.getSearchGroups(mData, 'count="([0-9]+?)"')[0] )
                    total_count = int( self.cm.ph.getSearchGroups(mData, 'total_count="([0-9]+?)"')[0] )
                    rel = self.cm.ph.getSearchGroups(mData, 'rel="([^"]+?)"')[0]
                    rel = rel.replace('item_type:', "'item_type':")
                    rel = rel.replace('attr:', "'attr':")
                    rel = rel.replace('filter:', "'filter':")
                    rel = rel.replace("'", '"')
                    rel = byteify(json.loads(rel))
                    self.filtesCache[fIdx]['items'].append({'ftype':'more', 'title':_("Next page"), 'rel':rel, 'count':count, 'total_count':total_count})
                except:
                    printExc()
        
        printDBG(self.filtesCache)
        sData = self.cm.ph.getDataBeetwenMarkers(data, '__sort">', '</div>', False)[1]
        sData = re.compile('data-sort="([^"]+?)"[^>]*?>([^<]+?)<').findall(sData)
        for item in sData:
            self.sortKeyCache.append({'title':item[1], 'sort_key':item[0]}) 
        
        params = dict(cItem)
        params.update({'title':_('--All--'), 'category':'list_sort_keys'})
        self.addDir(params)
            
        for idx in range(len(self.filtesCache)):
            item = self.filtesCache[idx]
            params = dict(cItem)
            params.update({'title':item['title'], 'filter_idx':idx, 'category':category})
            self.addDir(params)
            
    def listFilter(self, cItem, category):
        printDBG("FsTo.listFilter")
        
        if cItem.get('ftype', '') == 'more':
            rel = cItem['rel']
            total_count = cItem['total_count']
            count = cItem['count']
            params = ""
            for key, val in rel.items():
                params += "%s=%s&" %(key,val)
            printDBG(total_count)
            url = self.MAIN_URL + 'ajax.aspx?f=more_custom&' + params + '&count={0}'.format(count)
            sts, data = self.cm.getPage(url)
            if not sts: return
            try:
                data = byteify(json.loads(data))
                for item in data['items']:
                    params = dict(cItem)
                    params.update({'title':self.cleanHtmlStr(item['title']), 'url':self._getFullUrl(item['link'])})
                    params['category'] = category
                    self.addDir(params)
                if  data['count'] < total_count:
                    params = dict(cItem)
                    params['count'] = data['count']
                    self.addDir(params)
            except:
                printExc()
        else:
            tab = self.filtesCache[cItem['filter_idx']]['items']
            for item in tab:
                params = dict(cItem)
                params.update(item)
                if item['ftype'] == 'normal':
                    params['category'] = category
                self.addDir(params)
            
    def listSortKeys(self, cItem, category):
        printDBG("FsTo.listSortKeys")
        for item in self.sortKeyCache:
            params = dict(cItem)
            params.update(item)
            params['category'] = category
            self.addDir(params)
            
    def listItems(self, cItem, category):
        printDBG("FsTo.listItems url[%s]" % cItem['url'])
        page = cItem.get('page', 0)
        url = cItem['url']
        params = ''
        if 'sort_key' in cItem:
            params += 'sort=%s&' % (cItem['sort_key'])
        if page > 0:
            params += 'page=%s&' % (page)
        if '?' not in url:
            url += '?'
        else: url += '&'
        url += params + 'view=detailed'
        
        sts, data = self.cm.getPage(url)
        if not sts: return
        
        nextPage = False
        if ('page=%d"' % (page+1)) in data:
            nextPage = True
        
        data = self.cm.ph.getDataBeetwenMarkers(data, '"b-section-list', '<script type="text/javascript">', False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<td>', '</td>', False)
        for item in data:
            url   = self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0]
            icon  = self.cm.ph.getSearchGroups(item, '<img[^>]+?src="([^"]+?)"')[0]
            title = self.cm.ph.getSearchGroups(item, '__title-full"[^>]*?>([^<]+?)<')[0]
            if title == '': title = self.cm.ph.getSearchGroups(item, '__title-short"[^>]*?>([^<]+?)<')[0]
            if title == '': title = self.cm.ph.getSearchGroups(item, '__title"[^>]*?>([^<]+?)<')[0]
            if title == '': title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''')[0]
            desc  = item.split('-info-items">')[-1]
            params = {'category':category, 'title':self.cleanHtmlStr(title), 'icon':self._getFullUrl(icon), 'desc':self.cleanHtmlStr(desc), 'url':self._getFullUrl(url)}
            self.addDir(params)
            
        if nextPage:
            params = dict(cItem)
            params.update({'title':_('Next page'), 'page':page+1})
            self.addDir(params)
            
    def listFiles(self, cItem, category):
        printDBG("listFiles")
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return
        
        materialId = self.cm.ph.getSearchGroups(data, "materialId: '([^']+?)'")[0]
        url = self.MAIN_URL + 'jsitem/i%s/status.js?hr=%s&rf=' % (materialId, urllib.quote(cItem['url']))
        
        sts, data = self.cm.getPage(url)
        if not sts: return
        
        randomNumber = str(random.randint(10000000, 99999999))
        timestamp = str(time.time()).split('.')[0]
        frameHash = self.cm.ph.getSearchGroups(data, "'frame_hash': '([^']+?)'")[0]
        baseUrl = cItem['url'] + '?ajax&r=0.%s&id=%s&download=1&view=1&view_embed=1&blocked=1&frame_hash=%s&folder_quality=null&folder_lang=null&folder_translate=null&folder={0}&_=%s' % (randomNumber, materialId, frameHash, timestamp)
        
        cItem = dict(cItem)
        cItem.update({'url': baseUrl, 'category':category})
        self.listFolder(cItem)
        
    def listFolder(self, cItem):
        printDBG('listFolder')
        
        params = {}
        if config.plugins.iptvplayer.fsto_proxy_enable.value:
            params = {'http_proxy': config.plugins.iptvplayer.russian_proxyurl.value}
            
        url = cItem['url'].format(cItem.get('folder_id', '0'))
        sts, data = self.cm.getPage(url, params)
        if not sts: return
        
        m1 = '<li class='
        items = self.cm.ph.getAllItemsBeetwenMarkers(data, m1, '</li>')
        for item in items:
            if m1 in item:
                item = m1 + item.split(m1)[-1]
            parentId = self.cm.ph.getSearchGroups(item, "parent_id:[^0-9]+?([0-9]+?)[^0-9]")[0]
            url = self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0]
            if parentId != '' and parentId != cItem.get('folder_id', '0') and url == '#':
                tmp = item.split('</a>')
                params = dict(cItem)
                params.update({'folder_id':parentId, 'title':self.cleanHtmlStr(tmp[0]), 'desc':self.cleanHtmlStr(tmp[1])})
                self.addDir(params)
            elif '/get/dl/' in item:
                viewUrl = '' #self.cm.ph.getSearchGroups(item, 'href="([^"]*?/view/[^"]*?)"')[0]
                dlUrl = self.cm.ph.getSearchGroups(item, 'href="([^"]*?/get/dl/[^"]*?)"')[0]
                if viewUrl != '':
                    params = {'title':self.cleanHtmlStr(item) + '[%s]' % _('view'), 'url':self._getFullUrl(viewUrl)}
                    self.addVideo(params)
                if dlUrl != '':
                    params = {'title':self.cleanHtmlStr(item), 'url':self._getFullUrl(dlUrl)}
                    self.addVideo(params)
            else:
                printDBG("-----------------Wrong item-----------------")
                printDBG(item)
                printDBG("--------------------------------------------")
        
        
    def getLinksForVideo(self, cItem):
        printDBG("FsTo.getLinksForVideo [%s]" % cItem)
        urlTab = []
        
        url = cItem['url']
        if config.plugins.iptvplayer.fsto_proxy_enable.value:
            params = {'http_proxy': config.plugins.iptvplayer.russian_proxyurl.value, 'return_data':False}
            try:
                sts, response = self.cm.getPage(url, params)
                url = response.geturl()
                response.close()
            except:
                printExc()
                return []
            
        return [{'name':self.up.getHostName(url), 'url':url, 'need_resolve':0}]
        
    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG("FsTo.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]" % (cItem, searchPattern, searchType))
        SRCH_URL = self.MAIN_URL + '{0}/search.aspx?search='
        url = SRCH_URL.format(searchType) + urllib.quote_plus(searchPattern)
        
        sts, data = self.cm.getPage(url)
        if not sts: return
        
        # get serach sections 
        self.searchCache = {}
        secData = self.cm.ph.getDataBeetwenMarkers(data, '<div class="b-search-page__left">', '</div>', False)[1]
        secData = self.cm.ph.getAllItemsBeetwenMarkers(secData, '<a ', '</a>')
        for item in secData:
            subsection = self.cm.ph.getSearchGroups(item, 'data-subsection="([^"]+?)"')[0]
            self.searchCache[subsection] = []
            self.addDir({'title':self.cleanHtmlStr(item), 'subsection':subsection, 'category':'list_search_section'})
            
        data = self.cm.ph.getDataBeetwenMarkers(data, '__results">', 'class="l-footer', False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a ', '</a>')
        for item in data:
            subsection = self.cm.ph.getSearchGroups(item, 'data-subsection="([^"]+?)"')[0]
            if subsection in self.searchCache:
                url   = self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0]
                icon  = self.cm.ph.getSearchGroups(item, '<img[^>]+?src="([^"]+?)"')[0]
                title = self.cm.ph.getSearchGroups(item, '__title"[^>]*?>([^<]+?)<')[0]
                if title == '': title = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''')[0]
                desc  = item.split('-item-tags">')[-1]
                params = {'title':self.cleanHtmlStr(title), 'icon':self._getFullUrl(icon), 'desc':self.cleanHtmlStr(desc), 'url':self._getFullUrl(url)}
                self.searchCache[subsection].append(params)
            else:
                printDBG('WRONG SECTIO DETECTED IN RESULTS subsection[%s] !!!!' % subsection)
        
    def listSearchSection(self, cItem, category):
        printDBG('listSearchSection')
        subsection = cItem['subsection']
        for item in self.searchCache[subsection]:
            params = dict(item)
            params['category'] = category
            self.addDir(params)
    
    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        printDBG( "handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] " % (name, category) )
        self.currList = []
        
    #MAIN MENU
        if name == None:
            self.listMainMenu()
        elif category == 'list_cats':
            self.listCategories(self.currItem, 'list_filters')
        elif category == 'list_filters':
            self.listFilters(self.currItem, 'list_filter')
        elif category == 'list_filter':
            self.listFilter(self.currItem, 'list_sort_keys')
        elif category == 'list_sort_keys':
            self.listSortKeys(self.currItem, 'list_items')
        elif category == 'list_items':
            self.listItems(self.currItem, 'list_files')
        elif category == 'list_files':
            self.listFiles(self.currItem, 'list_folder')
        elif category == 'list_folder':
            self.listFolder(self.currItem)
    #SEARCH
        elif category == 'list_search_section':
            self.listSearchSection(self.currItem, 'list_files')
        elif category in ["search", "search_next_page"]:
            cItem = dict(self.currItem)
            cItem.update({'search_item':False, 'name':'category'}) 
            self.listSearchResult(cItem, searchPattern, searchType)
    #HISTORIA SEARCH
        elif category == "search_history":
            self.listsHistory({'name':'history', 'category': 'search'}, 'desc', _("Type: "))
        else:
            printExc()
        
        CBaseHostClass.endHandleService(self, index, refresh)
class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, FsTo(), True)#, [CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])

    def getLogoPath(self):
        return RetHost(RetHost.OK, value = [GetLogoDir('fstologo.png')])
    
    def getLinksForVideo(self, Index = 0, selItem = None):
        retCode = RetHost.ERROR
        retlist = []
        if not self.isValidIndex(Index): return RetHost(retCode, value=retlist)
        
        urlList = self.host.getLinksForVideo(self.host.currList[Index])
        for item in urlList:
            retlist.append(CUrlItem(item["name"], item["url"], item['need_resolve']))

        return RetHost(RetHost.OK, value = retlist)
    # end getLinksForVideo
    
    def converItem(self, cItem):
        hostList = []
        searchTypesOptions = self.host.getSearchTypesOptions()
        #searchTypesOptions.append((_("Video"), "video"))
        #searchTypesOptions.append((_("Audio"), "audio"))
        
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
            
        title       =  cItem.get('title', '')
        description =  cItem.get('desc', '')
        icon        =  cItem.get('icon', '')
        
        return CDisplayListItem(name = title,
                                    description = description,
                                    type = type,
                                    urlItems = hostLinks,
                                    urlSeparateRequest = 1,
                                    iconimage = icon,
                                    possibleTypesOfSearch = possibleTypesOfSearch)
    # end converItem

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
