# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, RetHost, CUrlItem, ArticleContent
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSearchHistoryHelper, GetDefaultLang, remove_html_markup, GetLogoDir, GetCookieDir, byteify
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common, CParsingHelper
import Plugins.Extensions.IPTVPlayer.libs.urlparser as urlparser
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
###################################################

###################################################
# FOREIGN import
###################################################
from datetime import timedelta
import time
import re
import urllib
import unicodedata
import base64
try:    import json
except: import simplejson as json
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

def GetConfigList():
    optionList = []
    return optionList
###################################################


def gettytul():
    return 'http://filmovizija.studio/'

class FilmovizijaStudio(CBaseHostClass):
    HEADER = {'User-Agent': 'Mozilla/5.0', 'Accept': 'text/html'}
    AJAX_HEADER = dict(HEADER)
    AJAX_HEADER.update( {'X-Requested-With': 'XMLHttpRequest'} )
    
    MAIN_URL       = 'http://filmovizija.studio/'
    MOV_SEARCH_URL = MAIN_URL + 'search1.php?ser=506&subs=&lks=1&rfrom=0&rto=0&gfrom=0&gto=0&gns=&btn=&keywords='
    SER_SEARCH_URL = MAIN_URL + 'search1.php?ser=528&subs=&lks=1&rfrom=0&rto=0&gfrom=0&gto=0&gns=&btn=&keywords='
    
    DEFAULT_ICON  = "http://www.filmovizija.studio/cdn/images/logo6.png"
    EPISODE_URL   = MAIN_URL + 'episode.php?vid='
    
    mc = 'browse-movies-videos-1-date.html'
    my = 'years.php'
    MAIN_CAT_TAB = [{'category':'list_movie_cats', 'title': _('Movies'),        'url':MAIN_URL+mc,   'icon':DEFAULT_ICON, 'filter':'movies'},
                    {'category':'categories',      'title': _('Top Movies'),    'url':MAIN_URL,      'icon':DEFAULT_ICON, 'filter':'top_movies'},
                    {'category':'categories',      'title': _('Series'),        'url':MAIN_URL,      'icon':DEFAULT_ICON, 'filter':'series'},
                    {'category':'categories',      'title': _('New Videos'),    'url':MAIN_URL,      'icon':DEFAULT_ICON, 'filter':'new_videos'},
                    {'category':'categories',      'title': _('New HD Videos'), 'url':MAIN_URL,      'icon':DEFAULT_ICON, 'filter':'new_hd_videos'},
                    {'category':'year',            'title': _('Year'),          'url':MAIN_URL+my,   'icon':DEFAULT_ICON},
                    {'category':'search',          'title': _('Search'), 'search_item':True,         'icon':DEFAULT_ICON},
                    {'category':'search_history',  'title': _('Search history'),                     'icon':DEFAULT_ICON} ]
 
    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'  filmovizija.studio', 'cookie':'filmovizijastudio.cookie'})
        self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
        self.cacheFilters = {'movies':[], 'top_movies':[], 'series':[], 'new_videos':[], 'new_hd_videos':[]}
        self.cacheSeasons = []
        
    def _getFullUrl(self, url):
        if url.startswith('//'):
            url = 'http:' + url
        else:
            if 0 < len(url) and not url.startswith('http'):
                url =  self.MAIN_URL + url
            if not self.MAIN_URL.startswith('https://'):
                url = url.replace('https://', 'http://')
                
        url = self.cleanHtmlStr(url)
        url = self.replacewhitespace(url)

        return url
        
    def cleanHtmlStr(self, data):
        data = data.replace('&nbsp;', ' ')
        data = data.replace('&nbsp', ' ')
        return CBaseHostClass.cleanHtmlStr(data)
        
    def replacewhitespace(self, data):
        data = data.replace(' ', '%20')
        return CBaseHostClass.cleanHtmlStr(data)

    def listsTab(self, tab, cItem, type='dir'):
        printDBG("FilmovizijaStudio.listsTab")
        for item in tab:
            params = dict(cItem)
            params.update(item)
            params['name']  = 'category'
            if type == 'dir':
                self.addDir(params)
            else: self.addVideo(params)
            
    def fillCategories(self):
        printDBG("FilmovizijaStudio.fillCategories")
        self.cacheFilters = {'movies':[], 'top_movies':[], 'series':[], 'new_videos':[], 'new_hd_videos':[]}
        sts, data = self.cm.getPage(self.MAIN_URL)
        if not sts: return
                     #('movies',        '>Movies</a>',        '</ul>'), \
        for cat in  [('top_movies',    '>Top Movies</a>',    '</ul>'), \
                     ('series',        '>Series</a>',        'divider'), \
                     ('new_videos',    '>New Videos</a>',    '</ul>'), \
                     ('new_hd_videos', '>New HD Videos</a>', '</ul>')]:
            self.cacheFilters[cat[0]] = [] 
            tmp = self.cm.ph.getDataBeetwenMarkers(data, cat[1], cat[2], False)[1]
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<a ', '</a>')
            for item in tmp:
                url = self.cm.ph.getSearchGroups(item, '''href=['"](http[^'^"^>]+?)[>'"]''')[0]
                if '' == url: continue
                self.cacheFilters[cat[0]].append({'title':self.cleanHtmlStr(item.split('</i>')[-1]), 'url':url})
        
    def listCategories(self, cItem, nextCategory):
        printDBG("FilmovizijaStudio.listCategories")
        filter = cItem.get('filter', '')
        tab = self.cacheFilters.get(filter, [])
        if 0 == len(tab):
            self.fillCategories()
        tab = self.cacheFilters.get(filter, [])
            
        cItem = dict(cItem)
        cItem['category'] = nextCategory
        self.listsTab(tab, cItem)
        
    def listYears(self, cItem, nextCategory):
        printDBG("FilmovizijaStudio.listYears")
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return
        tab = []
        data = self.cm.ph.getDataBeetwenMarkers(data, 'godine', '<script', False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a ', '</a>')
        for item in data:
            url = self.cm.ph.getSearchGroups(item, '''href=['"](http[^'^"]+?)['"]''')[0]
            if '' == url: continue
            tab.append({'title':self.cleanHtmlStr(item), 'url':url})
        
        cItem = dict(cItem)
        cItem['category'] = nextCategory
        self.listsTab(tab, cItem)
        
    def listMovieCats(self, cItem, nextCategory):
        printDBG("FilmovizijaStudio.listMovieCats")
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return
        tab = []
        data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="wrapper">', '</ul', False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
        for item in data:
            url  = self.cm.ph.getSearchGroups(item, '''href=['"](http[^'^"]+?)['"]''')[0]
            if '' == url: continue
            icon = self.cm.ph.getSearchGroups(item, '''src=['"]*(http[^'^"^>]+?)[>'"]''')[0]
            title = self.cm.ph.getSearchGroups(item, '''title=['"]([^'^"]+?)['"]''')[0] 
            title += ' ' + self.cleanHtmlStr(item)
            tab.append({'title':title, 'url':url, 'icon':icon})
        
        cItem = dict(cItem)
        cItem['category'] = nextCategory
        self.listsTab(tab, cItem)
            
    def listItems(self, cItem, nextCategory='list_seasons'):
        printDBG("FilmovizijaStudio.listItems")
        
        sts, data = self.cm.getPage(cItem['url']) 
        if not sts: return
        
        tmp = self.cm.ph.getDataBeetwenMarkers(data, '"pagination"', '</ul>', False)[1]
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<a ', '</a>')
        nextPageUrl = ''
        for item in tmp:
            if ' &raquo;' not in item: continue
            nextPageUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''')[0]
        tmp = ''
        
        m1 = '<ul class="cbp-rfgrid">'
        if m1 in data:
            data = self.cm.ph.getDataBeetwenMarkers(data, m1, "</ul>", False)[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
        else:
            data = self.cm.ph.getDataBeetwenMarkers(data, "<div class='series-top'>", "<script>", False)[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a ', '</a>')
            
        for item in data:
            url = self._getFullUrl( self.cm.ph.getSearchGroups(item, '''['"]([^"^']*?watch-[^"^']+?)['"]''')[0] )
            if url == '': url = self._getFullUrl( self.cm.ph.getSearchGroups(item, '''['"]([^"^']*?/movie/[^"^']+?)['"]''')[0] )
            title = self.cleanHtmlStr( self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''')[0] )
            if title == '':
                title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<a ', '</a>')[1] )
            icon  = self._getFullUrl( self.cm.ph.getSearchGroups(item, '''<img[^>]+?data-original=['"]([^"^']+?)['"]''')[0] )
            if icon == '': icon = cItem.get('icon', '') 
            dUrl  = self._getFullUrl( self.cm.ph.getSearchGroups(item, '''data-url=['"]([^"^']+?)['"]''')[0] )
            desc  = self.cleanHtmlStr(item)
            
            if not url.startswith('http'): 
                self.addDir({'title':'Error please report'})
                continue
            params = dict(cItem)
            params.update({'title':title, 'url':url, 'icon':icon, 'desc':desc, 'data_url':dUrl})
            if 'tvshow' in url:
                params['category'] = nextCategory
                self.addDir(params)
            else:
                self.addVideo(params)
        if nextPageUrl != '':
            params = dict(cItem)
            params.update({'title':_('Next page'), 'page':cItem.get('page', 1)+1, 'url':self._getFullUrl(nextPageUrl)})
            self.addDir(params)
            
    def listSeasons(self, cItem, nextCategory):
        printDBG("FilmovizijaStudio.listSeasons")
        self.cacheSeasons = []
        
        url = cItem['url']
        if '--tvshow' in url and 'data_url' in cItem:
            sts, data = self.cm.getPage(cItem['data_url'])
            if sts:
                url = self._getFullUrl( self.cm.ph.getSearchGroups(data, '''['"]([^"^']*?watch-[^"^']+?)['"]''')[0] )
            
        sts, data = self.cm.getPage(url) 
        if not sts: return
        
        desc = self.cm.ph.getDataBeetwenMarkers(data, '<div id="epload">', '<script>', False)[1]
        icon = self._getFullUrl( self.cm.ph.getSearchGroups(desc, '''src=['"]*(http[^'^"^>]+?)[>'"]''')[0] )
        desc = self.cleanHtmlStr(desc)
        
        m1 = "<li class='dropdown epilid caret-bootstrap caret-right' style='font-size:13px;'>"
        data = self.cm.ph.getDataBeetwenMarkers(data, m1, '<div id="epload">', False)[1]
        data = data.split(m1)
        for seasonItem in data:
            seasonTitle = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(seasonItem, '<a ', '</a>')[1] )
            episodesData = self.cm.ph.getDataBeetwenMarkers(seasonItem, '<ul ', '</ul>', False)[1]
            episodesData = episodesData.split("<div class='epi'>")
            if len(episodesData): del episodesData[0]
            episodesTab = []
            for episodeItem in episodesData:
                url = self.cm.ph.getSearchGroups(episodeItem, '''<a[^>]+?epiloader[^>]+?class=["']([^'^"]+?)['"]''')[0]
                if url == '': continue
                url = self.EPISODE_URL + url
                title = self.cleanHtmlStr( episodeItem )
                dUrl  = self._getFullUrl( self.cm.ph.getSearchGroups(episodeItem, '''data-url=['"]([^"^']+?)['"]''')[0] )
                seasonNum = self.cm.ph.getSearchGroups(seasonTitle+'|', '[^0-9]([0-9]+?)[^0-9]')[0]
                episodesTab.append({'title':cItem['title'] + ' - s%se%s' % (seasonNum, title), 'url':url, 'data_url':dUrl})
            if 0 == len(episodesTab): continue
            params = dict(cItem)
            params.update({'category':nextCategory, 'title':seasonTitle, 'desc':desc, 'icon':icon, 'season_idx':len(self.cacheSeasons)})
            self.addDir(params)
            self.cacheSeasons.append(episodesTab)
    
    def listEpisodes(self, cItem):
        printDBG("FilmovizijaStudio.listEpisodes")
        seasonIdx = cItem.get('season_idx', -1)
        if seasonIdx < 0 or seasonIdx >= len(self.cacheSeasons): return
        tab = self.cacheSeasons[seasonIdx]
        self.listsTab(tab, cItem, 'video')
        
    def getLinksForVideo(self, cItem):
        printDBG("FilmovizijaStudio.getLinksForVideo [%s]" % cItem)
        urlTab = [] #{'name':'', 'url':cItem['url'], 'need_resolve':1}]
        
        sts, data = self.cm.getPage(cItem['url']) 
        if not sts: return
        
        tmp = self.cm.ph.getDataBeetwenReMarkers(data, re.compile(';[^;]*?id\^\="page"'), re.compile('show\(\)'))[1].split('</script>')[0]
        printDBG("==========================================")
        printDBG(tmp)
        printDBG("==========================================")
        tmp = tmp.replace('\r', '\n').split('\n')
        tmp2 = []
        for item in tmp:
            if item.strip().startswith('//'): continue
            tmp2.append(item)
        tmp = '\n'.join(tmp2)
        printDBG(tmp)
        pageFormat = self.cm.ph.getSearchGroups(tmp, "src='(http[^']+?)'")[0]
        tmp2 = re.compile('"\+([^+]+?)\+"').findall(pageFormat)
        pageAttribs = []
        for item in tmp2:
            name = item.strip()
            attrib = self.cm.ph.getSearchGroups(tmp, '''var %s =[^;]+?attr\(['"]([^'^"]+?)['"]''' % name)[0]
            printDBG(">>>>>>>>>>>>>>>>>>>>> name[%s] attrib[%s]" % (name, attrib))
            pageAttribs.append({'name':name, 'attrib':attrib})
        
        # main links
        mainData = self.cm.ph.getDataBeetwenMarkers(data, '</table>', '<div id="contents">', False)[1]
        mainData = self.cm.ph.getAllItemsBeetwenMarkers(mainData, '<li>', '</li>')
        for item in mainData:
            try:
                tmp = self.cm.ph.getDataBeetwenMarkers(item, '<a ', '>')[1]
                #tmp = re.compile('''\s(\w)=['"]([^'^"]+?)['"]''').findall(tmp)
                tmp = re.compile('''[^a-zA-Z0-9_]([a-zA-Z0-9_]+?)=['"]([^'^"]+?)['"]''').findall(tmp)
                
                attribs = {}
                for a in tmp:
                    attribs[a[0]] = a[1]
                
                urlId    = attribs['id']
                urlClass = attribs['class']
                urlHref  = attribs['href']
                
                urlName  = self.cleanHtmlStr( item )
                printDBG('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ' + item)
                if urlClass == 'direct':
                    if not urlId.startswith('http'): continue
                    urlTab.append({'name':urlName, 'url':urlId, 'need_resolve':1})
                elif urlId.startswith('page') and pageFormat != '':
                    url = pageFormat
                    for a in pageAttribs:
                        url = url.replace('"+%s+"' % a['name'], attribs[a['attrib']])
                    urlTab.append({'name':urlName, 'url':url, 'need_resolve':1})
                elif urlId.startswith('tab'):
                    url = self.cm.ph.getDataBeetwenMarkers(data, '$("#%s").click' % urlId, '}', False)[1]
                    url = self.cm.ph.getSearchGroups(url, '''['"](http[^'^"]+?)['"]''')[0]
                    if not url.startswith('http'): continue
                    urlTab.append({'name':urlName, 'url':url, 'need_resolve':1})
            except:
                printExc()
        
        return urlTab
        
    def getVideoLinks(self, videoUrl):
        printDBG("FilmovizijaStudio.getVideoLinks [%s]" % videoUrl)
        urlTab = []
        if 'filmovizija.studi' in videoUrl:
            sts, data = self.cm.getPage(videoUrl)
            if not sts: return []
            printDBG(data)
            
            sub_tracks = []
            subData = self.cm.ph.getDataBeetwenMarkers(data, 'tracks:', ']', False)[1].split('}')
            for item in subData:
                if 'captions' in item:
                    label   = self.cm.ph.getSearchGroups(item, '''label:[ ]*?["']([^"^']+?)["']''')[0]
                    src     = self.cm.ph.getSearchGroups(item, '''file:[ ]*?["']([^"^']+?)["']''')[0]
                    if not src.startswith('http'): continue
                    sub_tracks.append({'title':label, 'url':src, 'lang':label, 'format':'srt'})
            
            linksTab = self.up.pp._findLinks(data, serverName='')
            for idx in range(len(linksTab)):
                name = linksTab[idx]['url']
                url  = urlparser.decorateUrl(linksTab[idx]['url'], {'external_sub_tracks':sub_tracks})
                urlTab.append({'name':name, 'url':url, 'need_resolve':0})
            
            if 0 == len(urlTab):
                videoUrl = self.cm.ph.getSearchGroups(data, '<iframe[^>]+?src="([^"]+?)"', 1, True)[0]
            
        if videoUrl.startswith('http'):
            urlTab.extend(self.up.getVideoLinkExt(videoUrl))
        return urlTab
        
    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG("FilmovizijaStudio.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]" % (cItem, searchPattern, searchType))
        cItem = dict(cItem)
        
        if 'movie' == searchType:
            baseUrl = self.MOV_SEARCH_URL
        else:
            baseUrl = self.SER_SEARCH_URL

        cItem['url'] = baseUrl + urllib.quote(searchPattern)
        self.listItems(cItem)

    def getArticleContent(self, cItem):
        printDBG("FilmovizijaStudio.getArticleContent [%s]" % cItem)
        retTab = []
        
        if '' == cItem.get('data_url', ''): return []
        
        sts, data = self.cm.getPage(cItem['data_url'])
        if not sts: return retTab
        
        printDBG(data)
        
        icon = cItem.get('icon', '')
        title = self.cm.ph.getDataBeetwenReMarkers(data, re.compile('''<[^>]*?['"]quad_tit["'][^>]*?>'''), re.compile('</'), False)[1]
        desc  = self.cm.ph.getDataBeetwenReMarkers(data, re.compile('''<[^>]*?['"]quad_description["'][^>]*?>'''), re.compile('</'), False)[1]
        
        otherInfo = {}
        tmpTab = [{'m1':'quad_imdb',      'm2':'</',      'key':'rating'},
                  {'m1':'quad_actors',    'm2':'</div>',  'key':'actors'},
                  {'m1':'quad_genres',    'm2':'</div>',  'key':'genre'},
                  {'m1':'fa fa-clock-o',  'm2':'</span>', 'key':'duration'},
                  {'m1':'fa fa-calendar', 'm2':'</span>', 'key':'year'},]
        
        for item in tmpTab:
            val = self.cm.ph.getDataBeetwenReMarkers(data, re.compile('''<[^>]+?\=['"]%s["'][^>]*?>''' % item['m1']), re.compile(item['m2']), False)[1]
            val = self.cleanHtmlStr(val.replace('Actors:', ''))
            if '' != val: otherInfo[item['key']] =  val
        
        return [{'title':self.cleanHtmlStr( title ), 'text': self.cleanHtmlStr( desc ), 'images':[{'title':'', 'url':self._getFullUrl(icon)}], 'other_info':otherInfo}]
        
    def getFavouriteData(self, cItem):
        return cItem['url']
        
    def getLinksForFavourite(self, fav_data):
        return self.getLinksForVideo({'url':fav_data})
    
    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        mode     = self.currItem.get("mode", '')
        
        printDBG( "handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] " % (name, category) )
        self.currList = []
        
    #MAIN MENU
        if name == None:
            self.listsTab(self.MAIN_CAT_TAB, {'name':'category'})
        elif category == 'categories':
            self.listCategories(self.currItem, 'list_items')
        elif category == 'year':
            self.listYears(self.currItem, 'list_items')
        elif category == 'list_movie_cats':
            self.listMovieCats(self.currItem, 'list_items')
        elif category == 'list_items':
                self.listItems(self.currItem)
    #SEASONS
        elif category == 'list_seasons':
            self.listSeasons(self.currItem, 'list_episodes')
        elif category == 'list_episodes':
            self.listEpisodes(self.currItem)
    #SEARCH
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
        # for now we must disable favourites due to problem with links extraction for types other than movie
        CHostBase.__init__(self, FilmovizijaStudio(), True, favouriteTypes=[CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])

    def getLogoPath(self):
        return RetHost(RetHost.OK, value = [GetLogoDir('filmovizijastudiologo.png')])
    
    def getLinksForVideo(self, Index = 0, selItem = None):
        retCode = RetHost.ERROR
        retlist = []
        if not self.isValidIndex(Index): return RetHost(retCode, value=retlist)
        
        urlList = self.host.getLinksForVideo(self.host.currList[Index])
        for item in urlList:
            retlist.append(CUrlItem(item["name"], item["url"], item['need_resolve']))

        return RetHost(RetHost.OK, value = retlist)
    # end getLinksForVideo
    
    def getResolvedURL(self, url):
        # resolve url to get direct url to video file
        retlist = []
        urlList = self.host.getVideoLinks(url)
        for item in urlList:
            need_resolve = 0
            retlist.append(CUrlItem(item["name"], item["url"], need_resolve))

        return RetHost(RetHost.OK, value = retlist)
        
    def getArticleContent(self, Index = 0):
        retCode = RetHost.ERROR
        retlist = []
        if not self.isValidIndex(Index): return RetHost(retCode, value=retlist)
    
        hList = self.host.getArticleContent(self.host.currList[Index])
        for item in hList:
            title      = item.get('title', '')
            text       = item.get('text', '')
            images     = item.get("images", [])
            othersInfo = item.get('other_info', '')
            retlist.append( ArticleContent(title = title, text = text, images =  images, richDescParams = othersInfo) )
        return RetHost(RetHost.OK, value = retlist)
    
    def converItem(self, cItem):
        hostList = []
        searchTypesOptions = [] # ustawione alfabetycznie
        searchTypesOptions.append((_("Movies"),   "movie"))
        searchTypesOptions.append((_("TV Shows"), "tv_shows"))
        
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
