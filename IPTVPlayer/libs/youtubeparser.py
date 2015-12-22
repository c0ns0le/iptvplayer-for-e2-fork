# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.extractor.youtube import YoutubeIE
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html, unescapeHTML
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, remove_html_markup, byteify
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common, CParsingHelper
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import decorateUrl

from datetime import timedelta
###################################################

###################################################
# FOREIGN import
###################################################
import re
try: import json
except: import simplejson as json
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.ytformat        = ConfigSelection(default = "mp4", choices = [("flv, mp4", "flv, mp4"),("flv", "flv"),("mp4", "mp4")]) 
config.plugins.iptvplayer.ytDefaultformat = ConfigSelection(default = "360", choices = [("0", _("the worst")), ("144", "144p"), ("240", "240p"), ("360", "360p"),("720", "720"), ("9999", _("the best"))])
config.plugins.iptvplayer.ytUseDF         = ConfigYesNo(default = True)
config.plugins.iptvplayer.ytShowDash      = ConfigYesNo(default = False)
config.plugins.iptvplayer.ytSortBy        = ConfigSelection(default = "", choices = [("", _("Relevance")),("video_date_uploaded", _("Upload date")),("video_view_count", _("View count")),("video_avg_rating", _("Rating"))]) 

class YouTubeParser():
    HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
    def __init__(self):
        self.cm = common()
        return

    def getDirectLinks(self, url, formats = 'flv, mp4', dash=True, dashSepareteList = False):
        printDBG('YouTubeParser.getDirectLinks')
        if config.plugins.iptvplayer.ytUseDF.value: # temporary workaround, similar code should be executed after getDirectLinks
            dash = False
        list = []
        try:
            list = YoutubeIE()._real_extract(url)
        except:
            printExc()
            if dashSepareteList:
                return [], []
            else: return []
        
        retList = []
        # filter dash
        dashAudioLists = []
        dashVideoLists = []
        if dash:
            # separete audio and video links
            for item in list:
                if 'mp4a' == item['ext']:
                    dashAudioLists.append(item)
                elif 'mp4v' == item['ext']:
                    dashVideoLists.append(item)
            # sort by quality -> format
            def _key(x):
                if x['format'].startswith('>'):
                     int(x['format'][1:-1])
                else:
                     int(x['format'][:-1])
                    
            dashAudioLists = sorted(dashAudioLists, key=_key, reverse=True)
            dashVideoLists = sorted(dashVideoLists, key=_key, reverse=True)
            
        for item in list:
            printDBG(">>>>>>>>>>>>>>>>>>>>>")
            printDBG( item )
            printDBG("<<<<<<<<<<<<<<<<<<<<<")
            if -1 < formats.find( item['ext'] ):
                if 'yes' == item['m3u8']:
                    format = re.search('([0-9]+?)p$', item['format'])
                    if format != None:
                        item['format'] = format.group(1) + "x"
                        item['ext']  = item['ext'] + "_M3U8"
                        item['url']  = decorateUrl(item['url'], {"iptv_proto":"m3u8"})
                        retList.append(item)
                else:
                    format = re.search('([0-9]+?x[0-9]+?$)', item['format'])
                    if format != None:
                        item['format'] = format.group(1)
                        item['url']  = decorateUrl(item['url'])
                        retList.append(item)
        
        dashList = []
        if len(dashAudioLists):
            # use best audio
            for item in dashVideoLists:
                item = dict(item)
                item["url"] = decorateUrl("merge://audio_url|video_url", {'audio_url':dashAudioLists[0]['url'], 'video_url':item['url'], 'prefered_merger':'MP4box'})
                dashList.append(item)
                
        if dashSepareteList:
            return retList, dashList
        else:
            retList.extend(dashList)
            return retList
        
        
    ########################################################
    # List Base PARSER
    ########################################################
    def parseListBase(self, data, type='video'):
        printDBG("parseListBase----------------")
        urlPatterns = { 'video'    :    ['video'   , 'href="[ ]*?(/watch\?v=[^"]+?)"'            , ''], 
                        'channel'  :    ['category', 'href="(/[^"]+?)"'                     , ''],
                        'playlist' :    ['category', 'list=([^"]+?)"'                       , '/playlist?list='],
                        'movie'    :    ['video'   , 'data-context-item-id="([^"]+?)"'      , '/watch?v='],
                        'live'     :    ['video'   , 'href="(/watch\?v=[^"]+?)"'            , ''],
                        'tray'     :    ['video'   , 'data-video-id="([^"]+?)"'             , '/watch?v='], }
        currList = []
        for i in range(len(data)):
            #printDBG("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            # get requaired params
            url   = urlPatterns[type][2] + self.getAttributes(urlPatterns[type][1], data[i])
            
            # get title
            title = '' #self.getAttributes('title="([^"]+?)"', data[i])
            if '' == title: title = self.getAttributes('data-context-item-title="([^"]+?)"', data[i])
            if '' == title: title = self.getAttributes('data-video-title="([^"]+?)"', data[i])
            if '' == title: sts,title = CParsingHelper.getDataBeetwenMarkers(data[i], '<h3 class="yt-lockup-title">', '</h3>', False) 
            if '' == title: sts,title = CParsingHelper.getDataBeetwenReMarkers(data[i], re.compile('<span [^>]*?class="title[^>]*?>'), re.compile('</span>'), False) 
            if '' == title: sts,title = CParsingHelper.getDataBeetwenReMarkers(data[i], re.compile('class="pl-video-title-link[^>]*?>'), re.compile('<'), False)
            
            if '' == title:
                titleMarker = self.cm.ph.getSearchGroups(data[i], '(<[^">]+?"yt-lockup-title[^"]*?"[^>]*?>)')[0]
                if '' != titleMarker:
                    tidx = titleMarker.find(' ')
                    if tidx > 0:
                        tmarker = titleMarker[1:tidx]
                        title = self.cm.ph.getDataBeetwenMarkers(data[i],  titleMarker, '</%s>' % tmarker)[1]
            
            if '' != title: title = CParsingHelper.removeDoubles(remove_html_markup(title, ' '), ' ')
                
            img   = self.getAttributes('data-thumb="([^"]+?\.jpg)"', data[i])
            if '' == img:  img = self.getAttributes('src="([^"]+?\.jpg)"', data[i])
            time  = self.getAttributes('data-context-item-time="([^"]+?)"', data[i])
            if '' == time: time  = self.getAttributes('class="video-time">([^<]+?)</span>', data[i])
            if '' == time: sts, time = CParsingHelper.getDataBeetwenReMarkers(data[i], re.compile('pl-video-time"[^>]*?>'), re.compile('<'), False)
            if '' == time: sts, time = CParsingHelper.getDataBeetwenReMarkers(data[i], re.compile('timestamp"[^>]*?>'), re.compile('<'), False)
            time = time.strip()
            # desc
            sts,desc  = CParsingHelper.getDataBeetwenReMarkers(data[i], re.compile('class="video-description[^>]+?>'), re.compile('</p>'), False)
            if '' == desc: sts,desc = CParsingHelper.getDataBeetwenReMarkers(data[i], re.compile('class="yt-lockup-description[^>]+?>'), re.compile('</div>'), False)
            desc = CParsingHelper.removeDoubles(remove_html_markup(desc, ' '), ' ')
            
            urlTmp = url.split(';')
            if len(urlTmp) > 0: url = urlTmp[0]
            if type == 'video': url = url.split('&')[0] 
                
            # printDBG('url   [%s] ' % url)
            # printDBG('title [%s] ' % title)
            # printDBG('img   [%s] ' % img)
            # printDBG('time  [%s] ' % time)
            # printDBG('desc  [%s] ' % desc)
            if title != '' and url != '' and img != '':
                correctUrlTab = [url, img]
                for i in range(len(correctUrlTab)):
                    if not correctUrlTab[i].startswith('http:') and not correctUrlTab[i].startswith('https:'):
                        if correctUrlTab[i].startswith("//"):
                            correctUrlTab[i] = 'http:' + correctUrlTab[i]
                        else:
                            correctUrlTab[i] = 'http://www.youtube.com' + correctUrlTab[i]
                    else:
                        if correctUrlTab[i].startswith('https:'):
                            correctUrlTab[i] = "http:" + correctUrlTab[i][6:]

                title = clean_html(title.decode("utf-8")).encode("utf-8")
                desc  = clean_html(desc.decode("utf-8")).encode("utf-8")
                params = {'type': urlPatterns[type][0], 'category': type, 'title': title, 'url': correctUrlTab[0], 'icon': correctUrlTab[1], 'time': time, 'desc': desc}
                currList.append(params)

        return currList
    #end parseListBase
    
    ########################################################
    # Tray List PARSER
    ########################################################
    def getVideosFromTraylist(self, url, category, page, cItem):
        printDBG('YouTubeParser.getVideosFromTraylist')
        return self.getVideosApiPlayList(url, category, page, cItem)

        currList = []
        try:
            sts,data =  self.cm.getPage(url, {'host': self.HOST})
            if sts:
                sts,data = CParsingHelper.getDataBeetwenMarkers(data, 'class="playlist-videos-container', '<div class="watch-sidebar-body">', False)
                data = data.split('class="yt-uix-scroller-scroll-unit')
                del data[0]
                return self.parseListBase(data, 'tray')
        except:
            printExc()
            return []
            
        return currList
    # end getVideosFromPlaylist
       
    ########################################################
    # PLAYLIST PARSER
    ########################################################
    def getVideosFromPlaylist(self, url, category, page, cItem):
        printDBG('YouTubeParser.getVideosFromPlaylist')
        currList = []
        try:
            sts,data =  self.cm.getPage(url, {'host': self.HOST})
            if sts:
                if '1' == page:
                    sts,data = CParsingHelper.getDataBeetwenMarkers(data, 'id="pl-video-list"', 'footer-container', False)
                else:
                    data = unescapeHTML(data.decode('unicode-escape')).encode('utf-8').replace('\/', '/')
                    
                # nextPage
                match = re.search('data-uix-load-more-href="([^"]+?)"', data)
                if not match: 
                    nextPage = ""
                else: 
                    nextPage = match.group(1).replace('&amp;', '&')
                
                itemsTab = data.split('<tr class="pl-video')
                currList = self.parseListBase(itemsTab)
                if '' != nextPage:
                    item = dict(cItem)
                    item.update({'title': 'Następna strona', 'page': str(int(page) + 1), 'url': 'http://www.youtube.com' + nextPage})
                    currList.append(item)
        except:
            printExc()
            
        return currList
    # end getVideosFromPlaylist

    ########################################################
    # CHANNEL LIST PARSER
    ########################################################
    def getAttributes(self, regx, data, num=1):
        match = re.search(regx, data)
        if not match: return ''
        else: return match.group(1)
        
    def getVideosFromChannelList(self, url, category, page, cItem):
        printDBG('YouTubeParser.getVideosFromChannelList page[%s]' % (page) )
        currList = []
        try:
            sts,data =  self.cm.getPage(url, {'host': self.HOST})
            if sts:
                if '1' == page:
                    sts,data = CParsingHelper.getDataBeetwenMarkers(data, 'feed-item-container', 'footer-container', False)
                else:
                    data = unescapeHTML(data.decode('unicode-escape')).encode('utf-8').replace('\/', '/')
                    
                # nextPage
                match = re.search('data-uix-load-more-href="([^"]+?)"', data)
                if not match: nextPage = ""
                else: nextPage = match.group(1).replace('&amp;', '&')
    
                data = data.split('feed-item-container')
                currList = self.parseListBase(data)
                
                if '' != nextPage:
                    item = dict(cItem)
                    item.update({'title': _("Next page"), 'page': str(int(page) + 1), 'url': 'http://www.youtube.com' + nextPage})
                    currList.append(item)
        except:
            printExc()
            return []
        return currList
    # end getVideosFromChannel

    ########################################################
    # SEARCH PARSER
    ########################################################
    #def getVideosFromSearch(self, pattern, page='1'):
    def getSearchResult(self, pattern, searchType, page, nextPageCategory, sortBy=''):
        printDBG('YouTubeParser.getSearchResult pattern[%s], searchType[%s], page[%s]' % (pattern, searchType, page))
        currList = []
        try:
            url = 'http://www.youtube.com/results?search_query=%s&filters=%s&search_sort=%s&page=%s' % (pattern, searchType, sortBy, page) 
            sts,data =  self.cm.getPage(url, {'host': self.HOST})
            if sts:
                if data.find('data-page="%d"' % (int(page) + 1)) > -1: nextPage = True
                else: nextPage = False
        
                sts,data = CParsingHelper.getDataBeetwenMarkers(data, '<li><div class="yt-lockup', '</ol>', False)
                
                data = data.split('<li><div class="yt-lockup')
                #del data[0]
                currList = self.parseListBase(data, searchType)
        
                if nextPage:
                    item = {'name': 'history', 'type': 'category', 'category': nextPageCategory, 'pattern':pattern, 'search_type':searchType, 'title': _("Next page"), 'page': str(int(page) + 1)}
                    currList.append(item)
        except:
            printExc()
            return []
        return currList
    # end getVideosFromSearch
    
    
    ########################################################
    # PLAYLIST API
    ########################################################
    def getVideosApiPlayList(self, url, category, page, cItem):
        printDBG('YouTubeParser.getVideosApiPlayList url[%s]' % url)
        playlistID = self.cm.ph.getSearchGroups(url + '&', 'list=([^&]+?)&')[0]
        baseUrl = 'https://www.youtube.com/list_ajax?style=json&action_get_list=1&list=%s' % playlistID
        

        currList = []
        if baseUrl != '':
            sts, data =  self.cm.getPage(baseUrl, {'host': self.HOST})
            try:
                data = byteify( json.loads(data) )['video']
                for item in data:
                    url   = 'http://www.youtube.com/watch?v=' + item['encrypted_id']
                    title = item['title']
                    img   = item['thumbnail']
                    time  = item['length_seconds']
                    if '' != time: time = str( timedelta( seconds = int(time) ) )
                    if time.startswith("0:"): time = time[2:]
                    desc  = item['description']
                    params = {'type': 'video', 'category': 'video', 'title': title, 'url': url, 'icon': img, 'time': time, 'desc': desc}
                    currList.append(params)
            except:
                printExc()
        return currList    

