# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, RetHost, CUrlItem, ArticleContent
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSearchHistoryHelper, remove_html_markup, \
                                                          GetLogoDir, GetCookieDir, byteify, ReadTextFile, GetBinDir, \
                                                          formatBytes, GetTmpDir, mkdirs
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist, getF4MLinksWithMeta, MYOBFUSCATECOM_OIO, MYOBFUSCATECOM_0ll, \
                                                               unpackJS, TEAMCASTPL_decryptPlayerParams, SAWLIVETV_decryptPlayerParams
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common, CParsingHelper
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html
from Plugins.Extensions.IPTVPlayer.libs.m3uparser import ParseM3u
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.iptvdm.iptvdh import DMHelper
from Plugins.Extensions.IPTVPlayer.components.iptvchoicebox import IPTVChoiceBoxItem
###################################################

###################################################
# FOREIGN import
###################################################
import re
import urllib
import base64
try:    import json
except: import simplejson as json
from os import path as os_path, chmod as os_chmod, remove as os_remove, rename as os_rename
from Components.config import config, ConfigSelection, ConfigInteger, ConfigYesNo, ConfigText, getConfigListEntry
###################################################


###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper, iptv_execute
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import fileExists
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.local_showfilesize = ConfigYesNo(default = True)
config.plugins.iptvplayer.local_showhiddensdir = ConfigYesNo(default = False)
config.plugins.iptvplayer.local_showhiddensfiles = ConfigYesNo(default = False)
config.plugins.iptvplayer.local_maxitems    = ConfigInteger(1000, (10, 1000000))

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_("Show file size"), config.plugins.iptvplayer.local_showfilesize ))
    optionList.append(getConfigListEntry(_("Show hiddens files"), config.plugins.iptvplayer.local_showhiddensfiles ))
    optionList.append(getConfigListEntry(_("Show hiddens catalogs"), config.plugins.iptvplayer.local_showhiddensdir ))
    optionList.append(getConfigListEntry(_("Max items per page"), config.plugins.iptvplayer.local_maxitems ))
    return optionList
###################################################


def gettytul():
    return (_('LocalMedia'))

class LocalMedia(CBaseHostClass):
    ISO_MOUNT_POINT_NAME = '.iptvplayer_iso'
    FILE_SYSTEMS = ['ext2', 'ext3', 'ext4', 'vfat', 'msdos', 'iso9660', 'nfs', 'jffs2', 'autofs', 'fuseblk', 'udf', 'cifs', 'ntfs']
    VIDEO_FILE_EXTENSIONS    = ['avi', 'flv', 'mp4', 'ts', 'mov', 'wmv', 'mpeg', 'mpg', 'mkv', 'vob', 'divx', 'm2ts', 'evo']
    AUDIO_FILES_EXTENSIONS   = ['mp3', 'm4a', 'ogg', 'wma', 'fla', 'wav', 'flac']
    PICTURE_FILES_EXTENSIONS = ['jpg', 'jpeg', 'png']
    M3U_FILES_EXTENSIONS     = ['m3u']
    ISO_FILES_EXTENSIONS     = ['iso']
    
    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'LocalMedia'})
        self.currDir = ''

    def getCurrDir(self):
        return self.currDir
        
    def setCurrDir(self, currDir):
        self.currDir = currDir
        
    def getExtension(self, path):
        ext = ''
        try:
            path, ext = os_path.splitext(path)
            ext = ext[1:]
        except: pass
        return ext.lower()
        
    def prepareCmd(self, path, start, end):
        lsdirPath = GetBinDir("lsdir")
        try: os_chmod(lsdirPath, 0777)
        except: printExc()
        if config.plugins.iptvplayer.local_showhiddensdir.value:
            dWildcards = '[^.]*|.[^.]*|..[^.]*'
        else: dWildcards = '[^.]*'
        
        fWildcards = []
        extensions = self.VIDEO_FILE_EXTENSIONS + self.AUDIO_FILES_EXTENSIONS + self.PICTURE_FILES_EXTENSIONS + self.M3U_FILES_EXTENSIONS + self.ISO_FILES_EXTENSIONS
        for ext in extensions:
            if config.plugins.iptvplayer.local_showhiddensfiles.value:
                wilcard = ''
            else: wilcard = '[^.]*'
            insensitiveExt=''
            for l in ext:
                insensitiveExt += '[%s%s]' % (l.upper(), l.lower())
            wilcard += '.' + insensitiveExt
            fWildcards.append(wilcard)
        cmd = '%s "%s" rdl rd %d %d "%s" "%s"' % (lsdirPath, path, start, end, '|'.join(fWildcards), dWildcards)
        if config.plugins.iptvplayer.local_showfilesize.value:
            cmd += " 1 ";
        return cmd
        
    def listsMainMenu(self, cItem):
        printDBG("LocalMedia.listsMainMenu [%s]" % cItem)
        # list mount points
        predefined = [{'title':_('IPTV Recordings'), 'path':config.plugins.iptvplayer.NaszaSciezka.value}, {'title':_('rootfs'), 'path':'/'}]
        for item in predefined:
            params = dict(cItem)
            params.update( item ) 
            self.addDir(params)
        
        table = self.getMountsTable()
        for item in table:
            if config.plugins.iptvplayer.local_showhiddensdir.value:
                path, name = os_path.split(item['node'])
                if name.startswith('.'): continue
                
            if '/' != item['node'] and item['filesystem'] in self.FILE_SYSTEMS:
                params = dict(cItem)
                params.update( {'title':item['node'], 'path':item['node']} ) 
                self.addDir(params)
        
    def listM3u(self, cItem):
        printDBG("LocalMedia.listM3u [%s]" % cItem)
        path = cItem['path']
        sts, data = ReadTextFile(path)
        if not sts: return
        data = ParseM3u(data)
        for item in data:
            params = dict(cItem)
            need_resolve = 1
            url = item['uri']
            if url.startswith('/'):
                url = 'file://' + url
                need_resolve = 0
            params.update( {'title':item['title'], 'category':'m3u_item', 'url':url, 'need_resolve':need_resolve} )
            self.addVideo(params)
            
    def showErrorMessage(self, message):
        printDBG(message)
        SetIPTVPlayerLastHostError(message)
        self.sessionEx.open(MessageBox, text=message, type=MessageBox.TYPE_ERROR)
        
    def getMountsTable(self, silen=False):
        table = []
        
        cmd = 'mount  2>&1'
        ret = iptv_execute()(cmd)
        if ret['sts']:
            data = ret.get('data', '')
            if 0 == ret['code']:
                data = data.split('\n')
                for line in data:
                    item = self.cm.ph.getSearchGroups(line, '(.+?) on (.+?) type ([^ ]+?) ', 3)
                    if len(item) < 3: continue
                    table.append({'device':item[0], 'node':item[1], 'filesystem':item[2]})
            else:
                message = _('Can not get mount points - cmd mount failed.\nReturn code[%s].\nReturn data[%s].') % (ret['code'], data)
        return table
            
    def getMountPoint(self, device, table=[], silen=False):
        printDBG("LocalMedia.getMountPoint")
        if [] == table:
            table = self.getMountsTable(silen)
        for item in table:
            if device == item['device']:
                return item['node']
        return ''
        
    def isMountPoint(self, path, table=[], silen=False):
        printDBG("LocalMedia.isMountPoint")
        if [] == table:
            table = self.getMountsTable(silen)
        for item in table:
            if path == item['node']:
                return True
        return False
            
    def listIso(self, cItem):
        printDBG("LocalMedia.listIso [%s]" % cItem)
        # check if iso file is mounted
        path  = cItem['path']
        defaultMountPoint = GetTmpDir(self.ISO_MOUNT_POINT_NAME)
        defaultMountPoint = defaultMountPoint.replace('//', '/')
        
        mountPoint = self.getMountPoint(path)
        
        if '' == mountPoint:
            # umount if different image already mounted
            if self.isMountPoint(defaultMountPoint):
                cmd = 'umount "{0}"'.format(defaultMountPoint) + ' 2>&1'
                ret = iptv_execute()(cmd)
                if ret['sts'] and 0 != ret['code']:
                    # normal umount failed, so detach filesystem only
                    cmd = 'umount -l "{0}"'.format(defaultMountPoint) + ' 2>&1'
                    ret = iptv_execute()(cmd)
                    
            # now mount the iso file
            if not mkdirs(defaultMountPoint):
                message = _('Make directory [%s]') % (defaultMountPoint)
                self.showErrorMessage(message)
                return
            else:
                cmd = 'mount -r "{0}" "{1}"'.format(path, defaultMountPoint) + ' 2>&1'
                ret = iptv_execute()(cmd)
                if ret['sts']:
                    if 0 != ret['code']:
                        message = _('Mount ISO file [%s] on [%s] failed.\nReturn code[%s].\nReturn data[%s].') % (path, defaultMountPoint, ret['code'], ret['data'])
                        self.showErrorMessage(message)
                        return
                    else:
                        mountPoint = defaultMountPoint
        
        if '' != mountPoint:
            params = dict(cItem)
            params.update( {'path':mountPoint, 'category':'dir'} )
            self.listDir(params)
        
    def listDir(self, cItem):
        printDBG("LocalMedia.listDir [%s]" % cItem)
        page = cItem.get('page', 0)
        
        start = cItem.get('start', 0)
        end   = start + config.plugins.iptvplayer.local_maxitems.value
        
        cItem = dict(cItem)
        cItem['start'] = 0
        
        path  = cItem['path']
        cmd = self.prepareCmd(path, start, end+1) + ' 2>&1'
        printDBG("cmd [%s]" % cmd) 
        ret = iptv_execute()(cmd)
        printDBG(ret)
        
        if ret['sts'] and 0 == ret['code']:
            self.setCurrDir(path)
            data = ret['data'].split('\n')
            dirTab = []
            m3uTab = []
            isoTab = []
            vidTab = []
            audTab = []
            picTab = []
            for item in data:
                start += 1
                if start > end: break 
                item = item.split('//')
                if config.plugins.iptvplayer.local_showfilesize.value:
                    if 5 != len(item):
                        continue
                elif 4 != len(item): 
                    continue
                
                fileSize = -1
                if 5 == len(item):
                    try: fileSize = int(item[3])
                    except:
                        printExc()
                        continue
                params = {'title':item[0]}
                if 'd' == item[1]:
                    dirTab.append(params)
                elif 'r' == item[1]:
                    params['size'] = fileSize
                    ext = self.getExtension(item[0])
                    if ext in self.M3U_FILES_EXTENSIONS:
                        m3uTab.append(params)
                    elif ext in self.ISO_FILES_EXTENSIONS:
                        isoTab.append(params)
                    elif ext in self.VIDEO_FILE_EXTENSIONS:
                        vidTab.append(params)
                    elif ext in self.AUDIO_FILES_EXTENSIONS:
                        audTab.append(params)
                    elif ext in self.PICTURE_FILES_EXTENSIONS:
                        picTab.append(params)
            self.addFromTab(cItem, dirTab, path, 'dir')
            self.addFromTab(cItem, isoTab, path, 'iso')
            self.addFromTab(cItem, m3uTab, path, 'm3u', 1)
            self.addFromTab(cItem, vidTab, path, 'video')
            self.addFromTab(cItem, audTab, path, 'audio')
            self.addFromTab(cItem, picTab, path, 'picture')
            
            if start > end:
                params = dict(cItem)
                params.update({'category':'more', 'title':_('More'), 'start':end})
                self.addMore(params)

    def addFromTab(self, params, tab, path, category='', need_resolve=0):
        table = []
        if category == 'iso':
            table = self.getMountsTable(True)
            
        tab.sort()
        for item in tab:
            params = dict(params)
            params.update( {'title':item['title'], 'category':category, 'desc':''} )
            if category in ['m3u', 'dir', 'iso']:
                fullPath = os_path.join(path, item['title'])
                params['path']  = fullPath
                if category != 'dir':
                    descTab = []
                    if item.get('size', -1) >= 0:
                        descTab.append( _("Total size: ") + formatBytes(item['size']) )
                        
                    #if len(table):
                    #    params['iso_mount_path']  = self.getMountPoint(fullPath, table)
                    #    if params['iso_mount_path']:
                    #        descTab.append( _('Mounted on %s') % params['iso_mount_path'] )
                    
                    if len(descTab):
                        params['desc'] = '[/br]'.join(descTab)
                self.addDir(params)
            else:
                fullPath = 'file://' + os_path.join(path, item['title'])
                params['url']  = fullPath
                params['type'] = category
                if 'picture' == category:
                    params['icon'] = fullPath
                params['need_resolve'] = need_resolve
                if item.get('size', -1) >= 0:
                    params['desc'] = _("Total size: ") + formatBytes(item['size'])
                self.currList.append(params)
    
    def getArticleContent(self, cItem):
        printDBG("LocalMedia.getArticleContent [%s]" % cItem)
        retTab = []
        
        return []
        
    def _uriIsValid(self, url):
        if '://' in url:
            return True
        return False
        
    def getResolvedURL(self, url):
        printDBG("LocalMedia.getResolvedURL [%s]" % url)
        videoUrls = []
        
        if url.startswith('/') and fileExists(url):
            url = 'file://'+url
        
        uri, params   = DMHelper.getDownloaderParamFromUrl(url)
        printDBG(params)
        uri = urlparser.decorateUrl(uri, params)
        
        if uri.meta.get('iptv_proto', '') in ['http', 'https']:
            urlSupport = self.up.checkHostSupport( uri )
        else:
            urlSupport = 0
        if 1 == urlSupport:
            retTab = self.up.getVideoLinkExt( uri )
            videoUrls.extend(retTab)
        elif 0 == urlSupport and self._uriIsValid(uri):
            if uri.split('?')[0].endswith('.m3u8'):
                retTab = getDirectM3U8Playlist(uri)
                videoUrls.extend(retTab)
            elif uri.split('?')[0].endswith('.f4m'):
                retTab = getF4MLinksWithMeta(uri)
                videoUrls.extend(retTab)
            else:
                videoUrls.append({'name':'direct link', 'url':uri})
        return videoUrls
        
    def getFavouriteData(self, cItem):
        return cItem['url']
        
    def getLinksForFavourite(self, fav_data):
        need_resolve = 0
        if not fav_data.startswith('file://'):
            need_resolve = 1
        return [{'name':'', 'url':fav_data, 'need_resolve':need_resolve}]

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        printDBG( "handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] " % (name, category) )
        self.currList = []
        
    #MAIN MENU
        if name == None:
            self.listsMainMenu({'name':'category'})
        elif category == 'm3u':
            self.listM3u(self.currItem)
        elif category == 'iso':
            self.listIso(self.currItem)
        else:
            self.listDir(self.currItem)
        
        CBaseHostClass.endHandleService(self, index, refresh)
class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, LocalMedia(), False, [CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO, CDisplayListItem.TYPE_PICTURE])
        self.cFilePath = ''
        self.cType = ''
        self.needRefresh = ''
        self.DEFAULT_ICON='http://www.ngonb.ru/files/res_media.png'

    def getLogoPath(self):
        return RetHost(RetHost.OK, value = [GetLogoDir('localmedialogo.png')])
        
    def getPrevList(self, refresh = 0):
        self.host.setCurrDir('')
        if(len(self.listOfprevList) > 0):
            hostList = self.listOfprevList.pop()
            hostCurrItem = self.listOfprevItems.pop()
            self.host.setCurrList(hostList)
            self.host.setCurrItem(hostCurrItem)
            
            convList = None
            if '' != self.needRefresh: 
                path = hostCurrItem.get('path', '')
                if '' != path and os_path.realpath(path) == os_path.realpath(self.needRefresh):
                    self.needRefresh = ''
                    self.host.handleService(self.currIndex, 1, self.searchPattern, self.searchType)
                    convList = self.convertList(self.host.getCurrList())
            if None == convList:
                convList = self.convertList(hostList)
            return RetHost(RetHost.OK, value = convList)
        else:
            return RetHost(RetHost.ERROR, value = [])
        
    def getCustomActions(self, Index = 0):
        retCode = RetHost.ERROR
        retlist = []
        
        def addPasteAction(path):
            if os_path.isdir(path):
                if '' != self.cFilePath:
                    cutPath, cutFileName = os_path.split(self.cFilePath)
                    params = IPTVChoiceBoxItem(_('Paste "%s"') % cutFileName, "", {'action':'paste_file', 'path':path})
                    retlist.append(params)
        
        ok = False
        if not self.isValidIndex(Index):
            path = self.host.getCurrDir()
            addPasteAction(path)
            retCode = RetHost.OK 
            return RetHost(retCode, value=retlist)
        
        if self.host.currList[Index]['type'] in ['video', 'audio', 'picture'] and \
           self.host.currList[Index].get('url', '').startswith('file://'):
            fullPath = self.host.currList[Index]['url'][7:]
            ok = True
        elif self.host.currList[Index].get("category", '') == 'm3u':
            fullPath = self.host.currList[Index]['path']
            ok = True
        elif self.host.currList[Index].get("category", '') == 'dir':
            fullPath = self.host.currList[Index]['path']
            ok = True
        elif self.host.currList[Index].get("category", '') == 'iso':
            fullPath = self.host.currList[Index]['path']
            ok = True
        if ok:
            path, fileName = os_path.split(fullPath)
            name, ext = os_path.splitext(fileName)
            
            if '' != self.host.currList[Index].get("iso_mount_path", ''):
                params = IPTVChoiceBoxItem(_('Umount iso file'), "", {'action':'umount_iso_file', 'file_path':fullPath, 'iso_mount_path':self.host.currList[Index]['iso_mount_path']})
                retlist.append(params)
            
            if os_path.isfile(fullPath):
                params = IPTVChoiceBoxItem(_('Rename'), "", {'action':'rename_file', 'file_path':fullPath})
                retlist.append(params)
                params = IPTVChoiceBoxItem(_('Remove'), "", {'action':'remove_file', 'file_path':fullPath})
                retlist.append(params)
                
                params = IPTVChoiceBoxItem(_('Copy'), "", {'action':'copy_file', 'file_path':fullPath})
                retlist.append(params)
                
                params = IPTVChoiceBoxItem(_('Cut'), "", {'action':'cut_file', 'file_path':fullPath})
                retlist.append(params)
            
            addPasteAction(path)
            retCode = RetHost.OK
        
        return RetHost(retCode, value = retlist)
        
    def performCustomAction(self, privateData):
        retCode = RetHost.ERROR
        retlist = []
        if privateData['action'] == 'remove_file':
            try:
                ret = self.host.sessionEx.waitForFinishOpen(MessageBox, text=_('Are you sure you want to remove file "%s"?') % privateData['file_path'], type=MessageBox.TYPE_YESNO, default=False)
                if ret[0]:
                    os_remove(privateData['file_path'])
                    retlist = ['refresh']
                    retCode = RetHost.OK
            except:
                printExc()
        if privateData['action'] == 'rename_file':
            try:
                path, fileName = os_path.split(privateData['file_path'])
                name, ext = os_path.splitext(fileName)
                ret = self.host.sessionEx.waitForFinishOpen(VirtualKeyBoard, title=_('Set file name'), text=name)
                printDBG('rename_file new name[%s]' % ret)
                if isinstance(ret[0], basestring):
                    newPath = os_path.join(path, ret[0] + ext)
                    printDBG('rename_file new path[%s]' % newPath)
                    if not os_path.isfile(newPath) and not os_path.islink(newPath):
                        os_rename(privateData['file_path'], newPath)
                        retlist = ['refresh']
                        retCode = RetHost.OK
                    else:
                        retlist = [_('File "%s" already exists!') % newPath]
            except:
                printExc()
        elif privateData['action'] == 'cut_file':
            self.cFilePath = privateData['file_path']
            self.cType = 'cut'
            retCode = RetHost.OK
        elif privateData['action'] == 'copy_file':
            self.cFilePath = privateData['file_path']
            self.cType = 'copy'
            retCode = RetHost.OK
        elif privateData['action'] == 'paste_file':
            try:
                ok = True
                cutPath, cutFileName = os_path.split(self.cFilePath)
                newPath = os_path.join(privateData['path'], cutFileName)
                if os_path.isfile(newPath):
                    retlist = [_('File "%s" already exists') % newPath]
                    ok = False
                else:
                    if self.cType == 'cut':
                        os_rename(self.cFilePath, newPath)
                        self.needRefresh = cutPath
                    elif self.cType == 'copy':
                        cmd = 'cp "%s" "%s"' % (self.cFilePath, newPath)
                        ret = iptv_execute()(cmd)
                if ok:
                    self.cType =  ''
                    self.cFilePath =  ''
                    retlist = ['refresh']
                    retCode = RetHost.OK
            except:
                printExc()
        elif privateData['action'] == 'umount_iso_file':
            cmd = 'umount "{0}"'.format(privateData['iso_mount_path']) + ' 2>&1'
            ret = iptv_execute()(cmd)
            if ret['sts'] and 0 != ret['code']:
                # normal umount failed, so detach filesystem only
                cmd = 'umount -l "{0}"'.format(privateData['iso_mount_path']) + ' 2>&1'
                ret = iptv_execute()(cmd)
        
        return RetHost(retCode, value=retlist)
        
    def getResolvedURL(self, url):
        # resolve url to get direct url to video file
        retlist = []
        urlList = self.host.getResolvedURL(url)
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
        elif 'picture' == cItem['type']:
            type = CDisplayListItem.TYPE_PICTURE
            
        if type in [CDisplayListItem.TYPE_AUDIO, CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_PICTURE]:
            url = cItem.get('url', '')
            if '' != url:
                hostLinks.append(CUrlItem("Link", url, cItem.get('need_resolve', 0)))
            
        title       =  cItem.get('title', '')
        description =  cItem.get('desc', '')
        icon        =  cItem.get('icon', '')
        if icon == '': icon = self.DEFAULT_ICON
        
        return CDisplayListItem(name = title,
                                    description = description,
                                    type = type,
                                    urlItems = hostLinks,
                                    urlSeparateRequest = 0,
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
