# -*- coding: utf-8 -*-
# Based on (root)/trunk/xbmc-addons/src/plugin.video.polishtv.live/hosts/ @ 419 - Wersja 636

###################################################
# LOCAL import
###################################################
from pCommon import common, CParsingHelper
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSelOneLink, GetCookieDir, byteify, formatBytes
from Plugins.Extensions.IPTVPlayer.libs.crypto.hash.md5Hash import MD5

from Plugins.Extensions.IPTVPlayer.libs.gledajfilmDecrypter import gledajfilmDecrypter
from Plugins.Extensions.IPTVPlayer.libs.crypto.cipher.aes  import AES
from Plugins.Extensions.IPTVPlayer.libs.crypto.cipher.base import noPadding
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import unescapeHTML, clean_html, _unquote
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import unpackJSPlayerParams, unpackJS, \
                                                               getParamsTouple, JS_FromCharCode, \
                                                               JS_toString, \
                                                               VIDUPME_decryptPlayerParams,    \
                                                               VIDEOWEED_unpackJSPlayerParams, \
                                                               SAWLIVETV_decryptPlayerParams,  \
                                                               VIDEOMEGA_decryptPlayerParams, \
                                                               OPENLOADIO_decryptPlayerParams, \
                                                               captchaParser, \
                                                               getDirectM3U8Playlist, \
                                                               decorateUrl, \
                                                               getF4MLinksWithMeta, \
                                                               MYOBFUSCATECOM_OIO, \
                                                               MYOBFUSCATECOM_0ll, \
                                                               int2base, drdX_fx, \
                                                               unicode_escape, JS_FromCharCode, pythonUnescape
from Plugins.Extensions.IPTVPlayer.libs.aadecoder import AADecoder
from Plugins.Extensions.IPTVPlayer.iptvdm.iptvdh import DMHelper
from Plugins.Extensions.IPTVPlayer.components.asynccall import iptv_execute
###################################################
# FOREIGN import
###################################################
import re
import time
import urllib
import socket
import string
import base64
import math

from xml.etree import cElementTree
from random import random, randint, randrange
from urlparse import urlparse, parse_qs
from binascii import hexlify, unhexlify, a2b_hex
from hashlib import md5
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import config

try: import json
except: import simplejson as json
    
import codecs
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.extractor.youtube import YoutubeIE
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.extractor.mtv import GametrailersIE
    
try:    from urlparse import urlsplit, urlunsplit
except: printExc()
###################################################
class urlparser:
    def __init__(self):
        self.cm = common()
        self.pp = pageParser()
        self.setHostsMap()
    
    @staticmethod
    def decorateUrl(url, metaParams={}):
        return decorateUrl(url, metaParams)
        
    @staticmethod
    def decorateParamsFromUrl(baseUrl, overwrite=False):
        printDBG("urlparser.decorateParamsFromUrl >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + baseUrl)
        tmp        = baseUrl.split('|')
        baseUrl    = urlparser.decorateUrl(tmp[0].strip(), strwithmeta(baseUrl).meta)
        KEYS_TAB = list(DMHelper.HANDLED_HTTP_HEADER_PARAMS)
        KEYS_TAB.extend(["iptv_audio_url", "Host", "Accept"])
        if 2 == len(tmp):
            baseParams = tmp[1].strip()
            try:
                params  = parse_qs(baseParams)
                for key in params.keys():
                    if key not in KEYS_TAB: continue
                    if not overwrite and key in baseUrl.meta: continue
                    try: baseUrl.meta[key] = params[key][0]
                    except: printExc()
            except: printExc()
        return baseUrl

    def preparHostForSelect(self, v, resolveLink = False):
        valTab = []
        i = 0
        if len(v) > 0:
            for url in (v.values() if type(v) is dict else v):
                if 1 == self.checkHostSupport(url):
                    hostName = self.getHostName(url, True)
                    i=i+1
                    if resolveLink:
                        url = self.getVideoLink( url )
                    if isinstance(url, basestring) and url.startswith('http'):
                        valTab.append({'name': (str(i) + '. ' + hostName), 'url': url})
        return valTab

    def getItemTitles(self, table):
        out = []
        for i in range(len(table)):
            value = table[i]
            out.append(value[0])
        return out

#anyfiles, bestreams, cda, cloudyvideos, flashx, neodrive, novamov, nowvideo, openload, played, realvid, streamin, streamplay, thevideo, video, videomega, videowood, vidgg, vidspot, 
#vidto, vidup, vidzer, vodlocker, vshare, vshareio, yourvideohost, youtube, youwatch
#    neodrive
    def setHostsMap(self):
        self.hostMap = {
                       'putlocker.com':        self.pp.parserFIREDRIVE     , 
                       'firedrive.com':        self.pp.parserFIREDRIVE     , 
                       'sockshare.com':        self.pp.parserSOCKSHARE     ,
                       'megustavid.com':       self.pp.parserMEGUSTAVID    ,
                       #'hd3d.cc':              self.pp.parserHD3D          ,
                       'sprocked.com':         self.pp.parserSPROCKED      ,
                       'wgrane.pl':            self.pp.parserWGRANE        ,
                       'cda.pl':               self.pp.parserCDA           ,
                       'ebd.cda.pl':           self.pp.parserCDA           ,
                       'video.anyfiles.pl':    self.pp.parserANYFILES      ,
                       'videoweed.es':         self.pp.parserVIDEOWEED     ,
                       'videoweed.com':        self.pp.parserVIDEOWEED     ,
                       'novamov.com':          self.pp.parserNOVAMOV       ,
                       'nowvideo.eu':          self.pp.parserNOWVIDEO      ,
                       'nowvideo.sx':          self.pp.parserNOWVIDEO      ,
                       'rapidvideo.com':       self.pp.parserRAPIDVIDEO    ,
                       'videoslasher.com':     self.pp.parserVIDEOSLASHER  ,
                       'dailymotion.com':      self.pp.parserDAILYMOTION   ,
                       'video.sibnet.ru':      self.pp.parserSIBNET        ,
                       'vk.com':               self.pp.parserVK            ,
                       'anime-shinden.info':   self.pp.parserANIMESHINDEN  ,
                       'content.peteava.ro':   self.pp.parserPETEAVA       ,
                       'i.vplay.ro':           self.pp.parserVPLAY         ,
                       'nonlimit.pl':          self.pp.parserIITV          ,
                       'streamo.tv':           self.pp.parserIITV          ,
                       'divxstage.eu':         self.pp.parserDIVXSTAGE     ,
                       'divxstage.to':         self.pp.parserDIVXSTAGE     ,
                       'movshare.net':         self.pp.parserWHOLECLOUD     ,
                       'wholecloud.net':       self.pp.parserWHOLECLOUD    ,
                       'tubecloud.net':        self.pp.parserTUBECLOUD     ,
                       'bestreams.net':        self.pp.parserBESTREAMS     ,
                       'freedisc.pl':          self.pp.parserFREEDISC      ,
                       'dwn.so':               self.pp.parserDWN           ,
                       'st.dwn.so':            self.pp.parserDWN           ,
                       'ginbig.com':           self.pp.parserGINBIG        ,
                       'qfer.net':             self.pp.parserQFER          ,
                       'streamcloud.eu':       self.pp.parserSTREAMCLOUD   ,
                       'limevideo.net':        self.pp.parserLIMEVIDEO     ,
                       'donevideo.com':        self.pp.parserLIMEVIDEO     ,
                       'scs.pl':               self.pp.parserSCS           ,
                       'youwatch.org':         self.pp.parserYOUWATCH      ,
                       'played.to':            self.pp.parserPLAYEDTO      ,
                       'videomega.tv':         self.pp.parserVIDEOMEGA     ,
                       'vidto.me':             self.pp.parserVIDTO         ,
                       'vidstream.in':         self.pp.parserVIDSTREAM     ,
                       'faststream.in':        self.pp.parserVIDSTREAM     ,
                       'video.rutube.ru':      self.pp.parserRUTUBE        ,
                       'rutube.ru':            self.pp.parserRUTUBE        ,
                       'youtube.com':          self.pp.parserYOUTUBE       ,
                       'youtu.be':             self.pp.parserYOUTUBE       ,
                       'google.com':           self.pp.parserGOOGLE        ,
                       'tinymov.net':          self.pp.parserTINYMOV       ,
                       'topupload.tv':         self.pp.parserTOPUPLOAD     ,
                       'maxupload.tv':         self.pp.parserTOPUPLOAD     ,
                       'video.yandex.ru':      self.pp.parserYANDEX        ,
                       'seositer.com':         self.pp.parserYANDEX        ,
                       'liveleak.com':         self.pp.parserLIVELEAK      ,
                       'vidup.me':             self.pp.parserVIDUPME       ,
                       'embed.trilulilu.ro':   self.pp.parserTRILULILU     ,
                       'videa.hu':             self.pp.parserVIDEA         ,
                       'emb.aliez.tv':         self.pp.parserALIEZ         ,
                       'my.mail.ru':           self.pp.parserVIDEOMAIL     ,
                       'api.video.mail.ru':    self.pp.parserVIDEOMAIL     ,
                       'videoapi.my.mail.ru':  self.pp.parserVIDEOMAIL     ,
                       'wrzuta.pl':            self.pp.parserWRZUTA        ,
                       'goldvod.tv':           self.pp.parserGOLDVODTV     ,
                       'vidzer.net':           self.pp.parserVIDZER        ,
                       'nowvideo.ch':          self.pp.parserNOWVIDEOCH    ,
                       'streamin.to':          self.pp.parserSTREAMINTO    ,
                       'vidsso.com':           self.pp.parserVIDSSO        ,
                       'wat.tv':               self.pp.parseWATTV          ,
                       'tune.pk':              self.pp.parseTUNEPK         ,
                       'netu.tv':              self.pp.parseNETUTV         ,
                       'hqq.tv':               self.pp.parseNETUTV         ,
                       'waaw.tv':              self.pp.parseNETUTV         ,
                       'vshare.io':            self.pp.parseVSHAREIO       ,
                       'vidspot.net':          self.pp.parserVIDSPOT       ,
                       'video.tt':             self.pp.parserVIDEOTT       ,
                       'vodlocker.com':        self.pp.parserVODLOCKER     ,
                       'vshare.eu':            self.pp.parserVSHAREEU      ,
                       'vidbull.com':          self.pp.parserVIDBULL       ,
                       'divxpress.com':        self.pp.parserDIVEXPRESS    ,
                       'promptfile.com':       self.pp.parserPROMPTFILE    ,
                       'playreplay.net':       self.pp.parserPLAYEREPLAY   ,
                       'moevideo.net':         self.pp.parserPLAYEREPLAY   ,
                       'videowood.tv':         self.pp.parserVIDEOWOODTV   ,
                       'movreel.com':          self.pp.parserMOVRELLCOM    ,
                       'vidfile.net':          self.pp.parserVIDFILENET    ,
                       'mp4upload.com':        self.pp.parserMP4UPLOAD     ,
                       'yukons.net':           self.pp.parserYUKONS        ,
                       'ustream.tv':           self.pp.parserUSTREAMTV     ,
                       'privatestream.tv':     self.pp.parserPRIVATESTREAM ,
                       'abcast.biz':           self.pp.parserABCASTBIZ     ,
                       'abcast.net':           self.pp.parserABCASTBIZ     ,
                       'goodcast.co':          self.pp.parserGOODCASTCO    ,
                       'myvi.ru':              self.pp.parserMYVIRU        ,
                       'myvi.tv':              self.pp.parserMYVIRU        ,
                       'archive.org':          self.pp.parserARCHIVEORG    ,
                       'sawlive.tv':           self.pp.parserSAWLIVETV     ,
                       'shidurlive.com':       self.pp.parserSHIDURLIVECOM ,
                       'castalba.tv':          self.pp.parserCASTALBATV    ,
                       'fxstream.biz':         self.pp.parserFXSTREAMBIZ   ,
                       'webcamera.pl':         self.pp.parserWEBCAMERAPL   ,
                       'flashx.tv':            self.pp.parserFLASHXTV      ,
                       'myvideo.de':           self.pp.parserMYVIDEODE     ,
                       'vidzi.tv':             self.pp.parserVIDZITV       ,
                       'tvp.pl':               self.pp.parserTVP           ,
                       'junkyvideo.com':       self.pp.parserJUNKYVIDEO    ,
                       'live.bvbtotal.de':     self.pp.parserLIVEBVBTOTALDE,
                       'partners.nettvplus.com': self.pp.parserNETTVPLUSCOM,
                       '7cast.net':            self.pp.parser7CASTNET      ,
                       'facebook.com':         self.pp.parserFACEBOOK      ,
                       'cloudyvideos.com':     self.pp.parserCLOUDYVIDEOS  ,
                       'thevideo.me':          self.pp.parserTHEVIDEOME    ,
                       'xage.pl':              self.pp.parserXAGEPL        ,
                       'castamp.com':          self.pp.parserCASTAMPCOM    ,
                       'crichd.tv':            self.pp.parserCRICHDTV      ,
                       'castto.me':            self.pp.parserCASTTOME      ,
                       'deltatv.pw':           self.pp.parserDELTATVPW     ,
                       'pxstream.tv':          self.pp.parserPXSTREAMTV    ,
                       'coolcast.eu':          self.pp.parserCOOLCASTEU    ,
                       'filenuke.com':         self.pp.parserFILENUKE      ,
                       'sharesix.com':         self.pp.parserFILENUKE      ,
                       'thefile.me':           self.pp.parserTHEFILEME     ,
                       'cloudtime.to':         self.pp.parserCLOUDTIME     ,
                       'nosvideo.com':         self.pp.parserNOSVIDEO      ,
                       'letwatch.us':          self.pp.parserLETWATCHUS    ,
                       'uploadc.com':          self.pp.parserUPLOADCCOM    ,
                       'mightyupload.com':     self.pp.parserMIGHTYUPLOAD  ,
                       'zalaa.com':            self.pp.parserZALAACOM      ,
                       'allmyvideos.net':      self.pp.parserALLMYVIDEOS   ,
                       'streamplay.cc':        self.pp.parserSTREAMPLAYCC  ,
                       'yourvideohost.com':    self.pp.parserYOURVIDEOHOST ,
                       'vidgg.to':             self.pp.parserVIDGGTO       ,
                       'vid.gg':               self.pp.parserVIDGGTO       ,
                       'tiny.cc':              self.pp.parserTINYCC        ,
                       'picasaweb.google.com': self.pp.parserPICASAWEB     ,
                       'stream4k.to':          self.pp.parserSTREAM4KTO    ,
                       'onet.pl':              self.pp.parserONETTV        ,
                       'onet.tv':              self.pp.parserONETTV        ,
                       'swirownia.com.usrfiles.com': self.pp.parserSWIROWNIA,
                       'byetv.org':            self.pp.paserBYETVORG       ,
                       'putlive.in':           self.pp.paserPUTLIVEIN      ,
                       'liveall.tv':           self.pp.paserLIVEALLTV      ,
                       'p2pcast.tv':           self.pp.paserP2PCASTTV      ,
                       'streamlive.to':        self.pp.paserSTREAMLIVETO   ,
                       'megom.tv':             self.pp.paserMEGOMTV        ,
                       'openload.io':          self.pp.parserOPENLOADIO    ,
                       'openload.co':          self.pp.parserOPENLOADIO    ,
                       'gametrailers.com':     self.pp.parserGAMETRAILERS  , 
                       'vevo.com':             self.pp.parserVEVO          ,
                       'shared.sx':            self.pp.parserSHAREDSX      ,
                       'gorillavid.in':        self.pp.parserFASTVIDEOIN   , 
                       'daclips.in':           self.pp.parserFASTVIDEOIN   ,
                       'movpod.in':            self.pp.parserFASTVIDEOIN   ,
                       'fastvideo.in':         self.pp.parserFASTVIDEOIN   ,
                       'realvid.net':          self.pp.parserFASTVIDEOIN   ,
                       'rapidvideo.ws':        self.pp.parserRAPIDVIDEOWS  ,
                       'hdvid.tv':             self.pp.parserHDVIDTV       ,
                       'exashare.com':         self.pp.parserEXASHARECOM   ,
                       'openload.info':        self.pp.parserEXASHARECOM   ,
                       'allvid.ch':            self.pp.parserALLVIDCH      ,
                       'posiedze.pl':          self.pp.parserPOSIEDZEPL    ,
                       'neodrive.co':          self.pp.parserNEODRIVECO    ,
                       'cloudy.ec':            self.pp.parserCLOUDYEC      ,
                       'ideoraj.ch':           self.pp.parserCLOUDYEC      ,
                       'miplayer.net':         self.pp.parserMIPLAYERNET   ,
                       'yocast.tv':            self.pp.parserYOCASTTV      ,
                       'liveonlinetv247.info': self.pp.parserLIVEONLINE247 ,
                       'liveonlinetv247.net':  self.pp.parserLIVEONLINE247 ,
                       'filepup.net':          self.pp.parserFILEPUPNET    ,
                       'superfilm.pl':         self.pp.parserSUPERFILMPL   ,
                       'sendvid.com':          self.pp.parserSENDVIDCOM    ,
                       'filehoot.com':         self.pp.parserFILEHOOT      ,
                       'ssh101.com':           self.pp.parserSSH101COM     ,
                       'twitch.tv':            self.pp.parserTWITCHTV      ,
                       'sostart.org':          self.pp.parserSOSTARTORG    ,
                       'theactionlive.com':    self.pp.parserTHEACTIONLIVE ,
                       'biggestplayer.me':     self.pp.parserBIGGESTPLAYER ,
                       'goodrtmp.com':         self.pp.parserGOODRTMP      ,
                       'life-rtmp.com':        self.pp.parserLIFERTMP      ,
                       'openlive.org':         self.pp.parserOPENLIVEORG   ,
                       #'billionuploads.com':   self.pp.parserBILLIONUPLOADS ,
                    }
        return
        
    def getHostName(self, url, nameOnly = False):
        hostName = ''
        match = re.search('https?://(?:www.)?(.+?)/', url)
        if match:
            hostName = match.group(1)
            if (nameOnly):
                n = hostName.split('.')
                hostName = n[-2]
        printDBG("_________________getHostName: [%s] -> [%s]" % (url, hostName))
        return hostName
        
        
    def getParser(self, url):
        host = self.getHostName(url)
        parser = self.hostMap.get(host, None)
        if None == parser:
            host2 = host[host.find('.')+1:]
            printDBG('urlparser.getParser II try host[%s]->host2[%s]' % (host, host2))
            parser = self.hostMap.get(host2, None)
        return parser
    
    def checkHostSupport(self, url):
        # -1 - not supported
        #  0 - unknown
        #  1 - supported
        ret = 0
        parser = self.getParser(url)
        if None != parser:
            return 1
        return ret

    def getVideoLinkExt(self, url):
        videoTab = []
        try:
            ret = self.getVideoLink(url, True)
            
            if isinstance(ret, basestring):
                if 0 < len(ret):
                    host = self.getHostName(url)
                    videoTab.append({'name': host, 'url': ret})
            elif isinstance(ret, list) or isinstance(ret, tuple):
                return ret
        except:
            printExc()
            
        return videoTab
        
    def getVideoLink(self, url, acceptsList = False):
        try:
            url = self.decorateParamsFromUrl(url)
            nUrl=''
            parser = self.getParser(url)
            if None != parser:
                nUrl = parser(url)
    
            if isinstance(nUrl, list) or isinstance(nUrl, tuple):
                if True == acceptsList:
                    return nUrl
                else:
                    if len(nUrl) > 0:
                        return nUrl[0]['url']
                    else:
                        return False
            return nUrl
        except:
            printExc()
        return False
        
    def getAutoDetectedStreamLink(self, baseUrl, data=None):
        printDBG("urlparser.getAutoDetectedStreamLink baseUrl[%s]" % baseUrl)
        url = baseUrl
        num = 0
        while True:
            num += 1
            if None == data:
                url = strwithmeta(url)
                HTTP_HEADER = dict(pageParser.HTTP_HEADER) 
                HTTP_HEADER['Referer'] = url.meta.get('Referer', url)
                sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER})
                if not sts: return []
            data = re.sub("<!--[\s\S]*?-->", "", data)
            if 1 == num  and 'http://up4free.com/' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([^'^"]+?)['"];""")[0]
                tmpUrl = url
                url = 'http://embed.up4free.com/stream.php?id=' + id + '&amp;width=700&amp;height=450&amp;stretching='
                url = strwithmeta(url, {'Referer':tmpUrl})
                data = None
                continue
            elif 'liveonlinetv247' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"](http://[^'^"]*?liveonlinetv247[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'ssh101.com/secure/' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"]([^'^"]*?ssh101.com/secure/[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'twitch.tv' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"]([^'^"]*?twitch.tv[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'goodrtmp.com' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"]([^'^"]*?goodrtmp.com[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'life-rtmp.com' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"]([^'^"]*?life-rtmp.com[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'sostart.org' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([^'"]+?)['"]""")[0]
                videoUrl = 'http://sostart.org/streamk.php?id={0}&width=640&height=390'.format(id)
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'theactionlive.com' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([^'"]+?)['"]""")[0]
                videoUrl = 'http://theactionlive.com/livegamecr2.php?id={0}&width=640&height=460&stretching='.format(id)
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'biggestplayer.me' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([^'"]+?)['"]""")[0]
                videoUrl = 'http://biggestplayer.me/streamcrjeje.php?id={0}&width=640&height=460'.format(id)
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'yocast.tv' in data:
                fid = self.cm.ph.getSearchGroups(data, """fid=['"]([^'"]+?)['"]""")[0]
                videoUrl = 'http://www.yocast.tv/embed.php?live={0}&vw=620&vh=490'.format(fid)
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'miplayer.net' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"](http://miplayer.net[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':strwithmeta(baseUrl).meta.get('Referer', baseUrl)})
                return self.getVideoLinkExt(videoUrl)
            elif 'p2pcast' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([0-9]+?)['"]""")[0]
                videoUrl = 'http://p2pcast.tv/stream.php?id={0}&live=0&p2p=0&stretching=uniform'.format(id)
                videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                return self.getVideoLinkExt(videoUrl)
            elif 'liveall.tv' in data: 
                videoUrl = self.cm.ph.getSearchGroups(data, 'SRC="([^"]+?liveall.tv[^"]+?)"', 1, True)[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                return self.getVideoLinkExt(videoUrl)
            elif 'putlive.in' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, '="([^"]*?putlive.in/[^"]+?)"')[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'streamlive.to' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, '="([^"]*?streamlive.to/[^"]+?)"')[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                return self.getVideoLinkExt(videoUrl)
            elif 'megom.tv' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, '="([^"]*?megom.tv/[^"]+?)"')[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                return self.getVideoLinkExt(videoUrl)
            elif 'byetv.org' in data:
                file = self.cm.ph.getSearchGroups(data, "file=([0-9]+?)[^0-9]")[0]
                if '' == file: file = self.cm.ph.getSearchGroups(data, "a=([0-9]+?)[^0-9]")[0]
                videoUrl = "http://www.byetv.org/embed.php?a={0}&id=&width=710&height=460&autostart=true&strech=".format(file)
                videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                return self.getVideoLinkExt(videoUrl)
            elif 'castto.me' in data:
                fid = self.cm.ph.getSearchGroups(data, """fid=['"]([0-9]+?)['"]""")[0]
                videoUrl = 'http://static.castto.me/embed.php?channel={0}&vw=710&vh=460'.format(fid)
                videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                return self.getVideoLinkExt(videoUrl)
            elif 'deltatv.pw' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([0-9]+?)['"];""")[0]
                videoUrl = 'http://deltatv.pw/stream.php?id=' + id
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'pxstream.tv' in data:
                id = self.cm.ph.getSearchGroups(data, """file=['"]([^'^"]+?)['"];""")[0]
                videoUrl = 'http://pxstream.tv/embed.php?file=' + id
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'coolcast.eu' in data:
                id = self.cm.ph.getSearchGroups(data, """file=['"]([^'^"]+?)['"];""")[0]
                videoUrl = 'http://coolcast.eu/?name=' + id
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'goodcast.co' in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([0-9]+?)['"];""")[0]
                videoUrl = 'http://goodcast.co/stream.php?id=' + id
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif '7cast.net' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"](http[^'^"]+?7cast.net[^'^"]+?)['"]""")[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'partners.nettvplus.com' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """['"](http://partners.nettvplus.com[^'^"]+?)['"]""")[0]
                return self.getVideoLinkExt(videoUrl)
            elif "yukons.net" in data:
                channel = self.cm.ph.getDataBeetwenMarkers(data, 'channel="', '"', False)[1]
                videoUrl = strwithmeta('http://yukons.net/watch/'+channel, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif "castamp.com" in data:
                channel = self.cm.ph.getDataBeetwenMarkers(data, 'channel="', '"', False)[1]
                videoUrl = strwithmeta('http://www.castamp.com/embed.php?c='+channel, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif "crichd.tv" in data:
                if baseUrl.startswith('http://crichd.tv'):
                    videoUrl = strwithmeta(baseUrl, {'Referer':baseUrl})
                else:
                    videoUrl = self.cm.ph.getSearchGroups(data, 'src="(http://crichd.tv[^"]+?)"')[0]
                    videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif "privatestream.tv" in data:
                videoUrl = self.cm.ph.getSearchGroups(data, '"(http://privatestream.tv/[^"]+?)"')[0]
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif "ustream.tv" in data:
                videoUrl = self.cm.ph.getSearchGroups(data, 'src="([^"]+?ustream.tv[^"]+?)"')[0]
                if videoUrl.startswith('//'):
                    videoUrl = 'http:' + videoUrl
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'rtmp://' in data:
                tmp = self.cm.ph.getSearchGroups(data, """(rtmp://[^'^"]+?)['"]""")[0]
                tmp = tmp.split('&amp;')
                r = tmp[0]
                if 1 < len(tmp)and tmp[1].startswith('c='):
                    playpath = tmp[1][2:]
                else:
                    playpath = self.cm.ph.getSearchGroups(data, """['"]*url['"]*[ ]*?:[ ]*?['"]([^'^"]+?)['"]""")[0]
                if '' != playpath:
                    r += ' playpath=%s' % playpath.strip()
                swfUrl = self.cm.ph.getSearchGroups(data, """['"](http[^'^"]+?swf)['"]""")[0]
                r += ' swfUrl=%s pageUrl=%s' % (swfUrl, url)
                return [{'name':'team-cast', 'url':r}]
            elif 'abcast.biz' in data or 'abcast.net' in data :
                file = self.cm.ph.getSearchGroups(data, "file='([^']+?)'")[0]
                if '' != file:
                    if 'abcast.net' in data:
                        videoUrl = 'http://abcast.net/embed.php?file='
                    else:
                        videoUrl = 'http://abcast.biz/embed.php?file='
                    videoUrl += file+'&width=640&height=480'
                    videoUrl = strwithmeta(videoUrl, {'Referer':url})
                    return self.getVideoLinkExt(videoUrl)
            elif 'openlive.org' in data:
                file = self.cm.ph.getSearchGroups(data, """file=['"]([^'^"]+?)['"];""")[0]
                videoUrl = 'http://openlive.org/embed.php?file={0}&width=710&height=460'.format(file)
                videoUrl = strwithmeta(videoUrl, {'Referer':url})
                return self.getVideoLinkExt(videoUrl)
            elif 'shidurlive.com' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """src=['"](http[^'^"]+?shidurlive.com[^'^"]+?)['"]""")[0]
                if '' != videoUrl:
                    videoUrl = strwithmeta(videoUrl, {'Referer':url})
                    return self.getVideoLinkExt(videoUrl)
            elif 'sawlive.tv' in data:
                videoUrl = self.cm.ph.getSearchGroups(data, """src=['"](http[^'^"]+?sawlive.tv[^'^"]+?)['"]""")[0]
                if '' != videoUrl:
                    videoUrl = strwithmeta(videoUrl, {'Referer':baseUrl})
                    return self.getVideoLinkExt(videoUrl)
            elif "castalba.tv" in data:
                id = self.cm.ph.getSearchGroups(data, """id=['"]([0-9]+?)['"];""")[0]
                if '' != id:
                    videoUrl = 'http://castalba.tv/embed.php?cid='+id+'&wh=640&ht=400&r=team-cast.pl.cp-21.webhostbox.net'
                    videoUrl = strwithmeta(videoUrl, {'Referer':url})
                    return self.getVideoLinkExt(videoUrl)
            elif "fxstream.biz" in data:
                file = self.cm.ph.getSearchGroups(data, """file=['"]([^'^"]+?)['"];""")[0]
                if '' != file:
                    videoUrl = 'http://fxstream.biz/embed.php?file='+file+'&width=640&height=400'
                    videoUrl = strwithmeta(videoUrl, {'Referer':url})
                    return self.getVideoLinkExt(videoUrl)
            else:
                file = self.cm.ph.getSearchGroups(data, """['"]*(http[^'^"]+?\.m3u8[^'^"]*?)['"]""")[0]
                if '' != file: 
                    file = file.split('&#038;')[0]
                    return getDirectM3U8Playlist(urllib.unquote(clean_html(file)), checkExt=False)
                if 'x-vlc-plugin' in data:
                    vlcUrl = self.cm.ph.getSearchGroups(data, """target=['"](http[^'^"]+?)['"]""")[0]
                    if '' != vlcUrl: return [{'name':'vlc', 'url':vlcUrl}]
                printDBG("=======================================================================")
                printDBG(data)
                printDBG("=======================================================================")
            return []

class pageParser:
    HTTP_HEADER= {  'User-Agent'  : 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
                    'Accept'      :  'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Content-type': 'application/x-www-form-urlencoded' }
    def __init__(self):
        self.cm = common()
        self.captcha = captchaParser()
        self.ytParser = None
        self.vevoIE = None
        
        #config
        self.COOKIE_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/cache/')
        #self.hd3d_login = config.plugins.iptvplayer.hd3d_login.value
        #self.hd3d_password = config.plugins.iptvplayer.hd3d_password.value
    
    def getYTParser(self):
        if self.ytParser == None:
            try:
                from youtubeparser import YouTubeParser
                self.ytParser = YouTubeParser()
            except:
                printExc()
                self.ytParser = None
        return self.ytParser
        
    def getVevoIE(self):
        if self.vevoIE == None:
            try:
                from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.extractor.vevo import VevoIE
                self.vevoIE = VevoIE()
            except:
                self.vevoIE = None
                printExc()
        return self.vevoIE
        
    def _findLinks(self, data, serverName='', linkMarker=r'''['"]?file['"]?[ ]*:[ ]*['"](http[^"^']+)['"][,}]''', m1='sources', m2=']'):
        linksTab = []
        srcData = self.cm.ph.getDataBeetwenMarkers(data, m1, m2, False)[1].split('},')
        for item in srcData:
            item += '},'
            link = self.cm.ph.getSearchGroups(item, linkMarker)[0].replace('\/', '/')
            label = self.cm.ph.getSearchGroups(item, r'''['"]?label['"]?[ ]*:[ ]*['"]([^"^']+)['"]''')[0]
            if '' != link:
                linksTab.append({'name': '%s %s' % (serverName, label), 'url':link})
                printDBG('_findLinks A')
        
        if 0 == len(linksTab):
            printDBG('_findLinks B')
            link = self.cm.ph.getSearchGroups(data, linkMarker)[0].replace('\/', '/')
            if '' != link:
                linksTab.append({'name':serverName, 'url':link})
        return linksTab
        
    def _findLinks2(self, data, baseUrl):
        videoUrl = self.cm.ph.getSearchGroups(data, 'type="video/divx"src="(http[^"]+?)"')[0]
        if '' != videoUrl: return strwithmeta(videoUrl, {'Referer':baseUrl})
        videoUrl = self.cm.ph.getSearchGroups(data, r'''['"]?file['"]?[ ]*[:,][ ]*['"](http[^"^']+)['"][,}\)]''')[0]
        if '' != videoUrl: return strwithmeta(videoUrl, {'Referer':baseUrl})
        return False
        
    def _parserUNIVERSAL_A(self, baseUrl, embedUrl, _findLinks, _preProcessing=None):
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        if 'embed' not in baseUrl:
            video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9]{12})[/.]')[0]
            url = embedUrl.format(video_id)
        else:
            url = baseUrl
        post_data = None
        sts, data = self.cm.getPage(url, {'header':HTTP_HEADER}, post_data)
        if not sts: return False
        
        if _preProcessing != None:
            data = _preProcessing(data)
        #printDBG(data)
        
        # get JS player script code from confirmation page
        sts, tmpData = CParsingHelper.getDataBeetwenMarkers(data, ">eval(", '</script>', False)
        if sts:
            data = tmpData
            tmpData = None
            # unpack and decode params from JS player script code
            data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams)
            #printDBG(data)
        return _findLinks(data)
        
    def _parserUNIVERSAL_B(self, url):
        printDBG("_parserUNIVERSAL_B url[%s]" % url)
        
        post_data = None
        
        if '/embed' not in url: 
            sts, data = self.cm.getPage( url, {'header':{'User-Agent': 'Mozilla/5.0'}} )
            if not sts: return False
            try:
                tmp = self.cm.ph.getDataBeetwenMarkers(data, '<form method="post" action="">', '</form>', False, False)[1]
                post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', tmp))
            except:
                printExc()
            try:
                tmp = dict(re.findall(r'<button[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', tmp))
                post_data.update(tmp)
            except:
                printExc()
        videoUrl = False
        params = {'header':{ 'User-Agent': 'Mozilla/5.0', 'Content-Type':'application/x-www-form-urlencoded','Referer':url} }
        try:
            sts, data = self.cm.getPage(url, params, post_data)
            printDBG(data)
            filekey = re.search('flashvars.filekey="([^"]+?)";', data)
            if None == filekey: 
                filekey = re.search("flashvars.filekey=([^;]+?);", data)
                filekey = re.search('var {0}="([^"]+?)";'.format(filekey.group(1)), data)
            filekey = filekey.group(1)
            file    = re.search('flashvars.file="([^"]+?)";', data).group(1)
            domain  = re.search('flashvars.domain="(http[^"]+?)"', data).group(1)
            
            url = domain + '/api/player.api.php?cid2=undefined&cid3=undefined&cid=undefined&user=undefined&pass=undefined&numOfErrors=0'
            url = url + '&key=' + urllib.quote_plus(filekey) + '&file=' + urllib.quote_plus(file)
            sts, data = self.cm.getPage(url)
            videoUrl = re.search("url=([^&]+?)&", data).group(1)
            
            errUrl = domain + '/api/player.api.php?errorCode=404&cid=1&file=%s&cid2=undefined&cid3=undefined&key=%s&numOfErrors=1&user=undefined&errorUrl=%s&pass=undefined' % (urllib.quote_plus(file), urllib.quote_plus(filekey), urllib.quote_plus(videoUrl))
            sts, data = self.cm.getPage(errUrl)
            errUrl = re.search("url=([^&]+?)&", data).group(1)
            if '' != errUrl: url = errUrl
            if '' != url:
                videoUrl = url
        except:
            printExc()
        return videoUrl
        
    def __parseJWPLAYER_A(self, baseUrl, serverName='', customLinksFinder=None):
        printDBG("pageParser.__parseJWPLAYER_A serverName[%s], baseUrl[%r]" % (serverName, baseUrl))
        
        linkList = []
        tries = 2
        while tries > 0:
            tries -= 1
            HTTP_HEADER = dict(self.HTTP_HEADER) 
            HTTP_HEADER['Referer'] = baseUrl
            sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER})

            if sts:
                HTTP_HEADER = dict(self.HTTP_HEADER) 
                HTTP_HEADER['Referer'] = baseUrl
                url = self.cm.ph.getSearchGroups(data, 'iframe[ ]+src="(http://embed.[^"]+?)"')[0]
                if serverName in url: sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER}) 
                else: url = baseUrl
            
            if sts and '' != data:
                try:
                    sts, data2 = self.cm.ph.getDataBeetwenMarkers(data, 'method="POST"', '</Form>', False, False)
                    if sts:
                        post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data2))
                        if tries == 0:
                            try:
                                sleep_time = self.cm.ph.getSearchGroups(data2, '>([0-9]+?)</span> seconds<')[0]
                                if '' != sleep_time: time.sleep(int(sleep_time))
                            except:
                                printExc()
                        HTTP_HEADER['Referer'] = url
                        sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER}, post_data)
                    if None != customLinksFinder: linkList = customLinksFinder(data)
                    if 0 == len(linkList): linkList = self._findLinks(data, serverName)
                except:
                    printExc()
            if len(linkList) > 0:
                break
        return linkList
            
    def parserFIREDRIVE(self,url):
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
        COOKIEFILE = self.COOKIE_PATH + "firedrive.cookie"
        url = url.replace('putlocker', 'firedrive').replace('file', 'embed')
        HTTP_HEADER['Referer'] = url
        
        sts, data = self.cm.getPage( url, {'header':HTTP_HEADER, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE} )
        if not sts: return False
        if not 'Continue to ' in data: return False
        data = re.search('name="confirm" value="([^"]+?)"', data)
        if not data: return False
        data = {'confirm' : data.group(1)}
        sts, data = self.cm.getPage( url, {'header':HTTP_HEADER, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': COOKIEFILE}, data)
        if not sts: return False
        sts, link_data = CParsingHelper.getDataBeetwenMarkers(data, "function getVideoUrl(){", 'return', False)
        if sts:       match = re.search("post\('(http[^']+?)'", link_data)
        else:         match = re.search("file: '(http[^']+?)'", data)
        if not match: match = re.search("file: loadURL\('(http[^']+?)'", data)

        if not match: return False
        url = match.group(1)
        printDBG('parserFIREDRIVE url[%s]' % url)
        return url


    def parserMEGUSTAVID(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('value="config=(.+?)">').findall(link)
        if len(match) > 0:
            p = match[0].split('=')
            url = "http://megustavid.com/media/nuevo/player/playlist.php?id=" + p[1]
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('<file>(.+?)</file>').findall(link)
            if len(match) > 0:
                return match[0]
            else:
                return False
        else:
            return False

    #def parserHD3D(self,url):
    #    if not 'html' in url:
    #        url = url + '.html?i'
    #    else:
    #        url = url
    #    username = self.hd3d_login
    #    password = self.hd3d_password
    #    urlL = 'http://hd3d.cc/login.html'
    #    self.COOKIEFILE = self.COOKIE_PATH + "hd3d.cookie"
    #    query_dataL = { 'url': urlL, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
    #    postdata = {'user_login': username, 'user_password': password}
    #    data = self.cm.getURLRequestData(query_dataL, postdata)
    #    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
    #    link = self.cm.getURLRequestData(query_data)
    #    match = re.compile("""url: ["'](.+?)["'],.+?provider:""").findall(link)
    #    if len(match) > 0:
    #        ret = match[0]
    #    else:
    #     ret = False
    #    return ret

    def parserSPROCKED(self,url):
        url = url.replace('embed', 'show')
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.search("""url: ['"](.+?)['"],.*\nprovider""",link)
        if match: return match.group(1)
        else: return False

    def parserWGRANE(self,url):
        # extract video hash from given url
        sts, data = self.cm.getPage(url)
        if not sts: return False
        agree = ''
        if 'controversial_content_agree' in data: agree = 'controversial_content_agree'
        elif 'adult_content_agree' in data: agree = 'adult_content_agree'
        if '' != agree:
            vidHash = re.search("([0-9a-fA-F]{32})$", url)
            if not vidHash: return False
            params = {'use_cookie': True, 'load_cookie':False, 'save_cookie':False} 
            url = "http://www.wgrane.pl/index.html?%s=%s" % (agree, vidHash.group(1))
            sts, data = self.cm.getPage(url, params)
            if not sts: return False

        tmp = re.search('''["'](http[^"^']+?/video/[^"^']+?\.mp4[^"^']*?)["']''', data)
        if tmp: return tmp.group(1)
        data = re.search("<meta itemprop='contentURL' content='([^']+?)'", data)
        if not data: return False
        url = clean_html(data.group(1))
        return url
        
    def parserCDA(self, inUrl):
    
        def _decorateUrl(inUrl, host, referer):
            # prepare extended link
            retUrl = strwithmeta( inUrl )
            retUrl.meta['Host']              = host
            retUrl.meta['Referer']           = referer
            retUrl.meta['Cookie']            = "PHPSESSID=1"
            retUrl.meta['iptv_proto']        = 'http'
            retUrl.meta['iptv_urlwithlimit'] = False
            retUrl.meta['iptv_livestream']   = False
            retUrl.meta['iptv_buffering']    = "required" #"required" # required to handle Cookie
            return retUrl
            
        vidMarker = '/video/'
        videoUrls = []
        tmpUrls = []
        if vidMarker not in inUrl:
            sts, data = self.cm.getPage(inUrl)
            if sts:
                sts,match = CParsingHelper.getDataBeetwenMarkers(data, "Link do tego video:", '</a>', False)
                if sts: match = self.cm.ph.getSearchGroups(match, 'href="([^"]+?)"')[0] 
                else: match = self.cm.ph.getSearchGroups(data, "link[ ]*?:[ ]*?'([^']+?/video/[^']+?)'")[0]
                if match.startswith('http'): inUrl = match
        if vidMarker in inUrl: 
            vid = inUrl.split('/video/')[1]
            inUrl = 'http://www.cda.pl/video/' + vid
        else: tmpUrls.append(inUrl)
        
        # extract qualities
        sts, data = self.cm.getPage(inUrl)
        if sts:
            sts, data = CParsingHelper.getDataBeetwenMarkers(data, 'Jakość:', '</div>', False)
            if sts:
                data = re.findall('<a[^>]+?href="([^"]+?)"[^>]*?>([^<]+?)</a>', data)
                for urlItem in data:
                    tmpUrls.append({'name':'cda.pl ' + urlItem[1], 'url':urlItem[0]})
        if 0 == len(tmpUrls):
            tmpUrls.append({'name':'cda.pl', 'url':inUrl})
        for urlItem in tmpUrls:
            if urlItem['url'].startswith('/'): inUrl = 'http://www.cda.pl/' + urlItem['url']
            else: inUrl = urlItem['url']
            sts, pageData = self.cm.getPage(inUrl)
            if sts:
                data = CParsingHelper.getDataBeetwenMarkers(pageData, "modes:", ']', False)[1]
                data = re.compile("""file: ['"]([^'^"]+?)['"]""").findall(data)
                if 0 < len(data) and data[0].startswith('http'): videoUrls.append( {'name': urlItem['name'] + ' flv', 'url':_decorateUrl(data[0], 'cda.pl', urlItem['url']) } )
                if 1 < len(data) and data[1].startswith('http'): videoUrls.append( {'name': urlItem['name'] + ' mp4', 'url':_decorateUrl(data[1], 'cda.pl', urlItem['url']) } )
                if 0 == len(data):
                    data = CParsingHelper.getDataBeetwenMarkers(pageData, 'video: {', '}', False)[1]
                    data = self.cm.ph.getSearchGroups(data, "'(http[^']+?\.mp4[^']*?)'")[0] 
                    if '' != data:
                        videoUrls.append( {'name': urlItem['name'] + ' mp4', 'url':_decorateUrl(data, 'cda.pl', urlItem['url']) } )
        
        #if len(videoUrls):
        #    videoUrls = [videoUrls[0]]
        return videoUrls

    def parserDWN(self,url):
        if "play4.swf" in url:
            match = re.search("play4.swf([^']+?)',", url+"',")
        else:
            sts, url = self.cm.getPage(url)
            if not sts: return False
            match = re.search('src="([^"]+?)" width=', url)
            if match:
                sts, url = self.cm.getPage( match.group(1) )
                if not sts: return False
            match = re.search("play4.swf([^']+?)',", url)

        if match:
            url = 'http://st.dwn.so/xml/videolink.php' + match.group(1)
            sts, data = self.cm.getPage(url)
            if not sts: return False
            match = re.search('un="([^"]+?),0"', data)
            if match:
                linkvideo = 'http://' + match.group(1)
                printDBG("parserDWN directURL [%s]" % linkvideo)
                return linkvideo
        return False

    def parserANYFILES(self, url):
        from anyfilesapi import AnyFilesVideoUrlExtractor
        self.anyfiles = AnyFilesVideoUrlExtractor()
        
        id = self.cm.ph.getSearchGroups(url+'|', 'id=([0-9]+?)[^0-9]')[0]
        if id != '':
            url = 'http://video.anyfiles.pl/videos.jsp?id=' + id
        retVal = self.anyfiles.getVideoUrl(url)
        return retVal

    def parserWOOTLY(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        c = re.search("""c.value="(.+?)";""",link)
        if c:
            cval = c.group(1)
        else:
            return False
        match = re.compile("""<input type=['"]hidden['"] value=['"](.+?)['"].+?name=['"](.+?)['"]""").findall(link)
        if len(match) > 0:
            postdata = {};
            for i in range(len(match)):
                if (len(match[i][0])) > len(cval):
                    postdata[cval] = match[i][1]
                else:
                    postdata[match[i][0]] = match[i][1]
            self.COOKIEFILE = self.COOKIE_PATH + "wootly.cookie"
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.search("""<video.*\n.*src=['"](.+?)['"]""",link)
            if match:
                return match.group(1)
            else:
                return False
        else:
            return False

    def parserVIDEOWEED(self, url):
        return self._parserUNIVERSAL_B(url)

    def parserNOVAMOV(self, url):
        return self._parserUNIVERSAL_B(url)

    def parserNOWVIDEO(self, url):
        urlTab = []
        if '/mobile/video.php?id' in url:
            sts, data = self.cm.getPage(url)
            if sts:
                data = re.compile('<source ([^>]*?)>').findall(data)
                for item in data:
                    type = self.cm.ph.getSearchGroups(item, 'type="([^"]+?)"')[0]
                    if 'video' not in type: continue 
                    url  = self.cm.ph.getSearchGroups(item, 'src="([^"]+?)"')[0]
                    name = url.split('?')[0].split('.')[-1]
                    urlTab.append({'name':type, 'url':url})
                if len(urlTab): return urlTab
        
        tmp = self._parserUNIVERSAL_B(url)
        if isinstance(tmp, basestring) and 0 < len(tmp):
            tmp += '?client=FLASH'
        return tmp
        
    def parserSOCKSHARE(self,url):
        query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        r = re.search('value="(.+?)" name="fuck_you"', link)
        if r:
            self.COOKIEFILE = self.COOKIE_PATH + "sockshare.cookie"
            postdata = {'fuck_you' : r.group(1), 'confirm' : 'Close Ad and Watch as Free User'}
            query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile("playlist: '(.+?)'").findall(link)
            if len(match) > 0:
                url = "http://www.sockshare.com" + match[0]
                query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
                link = self.cm.getURLRequestData(query_data)
                match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
                if len(match) > 0:
                    url = match[0].replace('&amp;','&')
                    return url
                else:
                    return False
            else:
                return False
        else:
            return False

    def parserRAPIDVIDEO(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #"jw_set('http://176.9.7.56:8080/v/bc71afa327b1351b2d9abe5827aa97dc/240/130219976TEBYU50H0NN.flv','240p','176.9.7.56');"
        match = re.compile("jw_set\('(.+?)','(.+?)','.+?'\);").findall(link)
        if len(match) > 0:
            return match[0][0]
        else:
            return False

    def parserVIDEOSLASHER(self, url):
        self.COOKIEFILE = self.COOKIE_PATH + "videoslasher.cookie"
        query_data = { 'url': url.replace('embed', 'video'), 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
        postdata = {'confirm': 'Close Ad and Watch as Free User', 'foo': 'bar'}
        data = self.cm.getURLRequestData(query_data, postdata)

        match = re.compile("playlist: '/playlist/(.+?)'").findall(data)
        if len(match)>0:
            query_data = { 'url': 'http://www.videoslasher.com//playlist/' + match[0], 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE,  'use_post': True, 'return_data': True }
            data = self.cm.getURLRequestData(query_data)
            match = re.compile('<title>Video</title>.*?<media:content url="(.+?)"').findall(data)
            if len(match)>0:
                sid = self.cm.getCookieItem(self.COOKIEFILE,'authsid')
                if sid != '':
                    streamUrl = urlparser.decorateUrl(match[0], {'Cookie':"authsid=%s" % sid, 'iptv_buffering':'required'})
                    return streamUrl
                else:
                    return False
            else:
                return False
        else:
            return False

    def parserDAILYMOTION(self, baseUrl):
        # https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/dailymotion.py
        COOKIEFILE = self.COOKIE_PATH + "dailymotion.cookie"
        _VALID_URL = r'(?i)(?:https?://)?(?:(www|touch)\.)?dailymotion\.[a-z]{2,3}/(?:(embed|#)/)?video/(?P<id>[^/?_]+)'
        mobj = re.match(_VALID_URL, baseUrl)
        video_id = mobj.group('id')
        
        
        url = 'http://www.dailymotion.com/embed/video/' + video_id
        familyUrl = 'http://www.dailymotion.com/family_filter?enable=false&urlback=' + urllib.quote_plus('/embed/video/' + video_id)
        sts, data = self.cm.getPage(url, {'use_cookie': True, 'save_cookie': False, 'load_cookie': False, 'cookiefile': COOKIEFILE})
        if not sts or "player" not in data: 
            sts, data = self.cm.getPage(familyUrl, {'use_cookie': True, 'save_cookie': False, 'load_cookie': False, 'cookiefile': COOKIEFILE})
            if not sts: return []
        
        vidTab = []
        player_v5 = self.cm.ph.getSearchGroups(data, r'playerV5\s*=\s*dmp\.create\([^,]+?,\s*({.+?})\);')[0]
        if '' != player_v5:
            player_v5 = byteify(json.loads(player_v5))
            printDBG(player_v5)
            player_v5 = player_v5['metadata']['qualities']
            for quality, media_list in player_v5.items():
                for media in media_list:
                    media_url = media.get('url')
                    if not media_url:
                        continue
                    type_ = media.get('type')
                    if type_ == 'application/vnd.lumberjack.manifest':
                        continue
                    if type_ == 'application/x-mpegURL' or media_url.split('?')[-1].endswith('m3u8'):
                        continue
                        tmpTab = getDirectM3U8Playlist(media_url, False)
                        for tmp in tmpTab:
                            vidTab.append({'name':'dailymotion.com: %s hls' % (tmp.get('bitrate', '0')), 'url':tmp['url']})
                    else:
                        vidTab.append({'name':'dailymotion.com: %s' % quality, 'url':media_url})
            
        if 0 == len(vidTab):
            data = CParsingHelper.getDataBeetwenMarkers(data, 'id="player"', '</script>', False)[1].replace('\/', '/')
            match = re.compile('"stream_h264.+?url":"(http[^"]+?H264-)([^/]+?)(/[^"]+?)"').findall(data)
            for i in range(len(match)):
                url = match[i][0] + match[i][1] + match[i][2]
                name = match[i][1]
                vidTab.append({'name': 'dailymotion.com: ' + name, 'url':url})

        return vidTab[::-1]

    def parserSIBNET(self, baseUrl):
        printDBG("parserSIBNET url[%s]" % baseUrl)
        videoUrls = []
        
        videoid = self.cm.ph.getSearchGroups(baseUrl+'|', """videoid=([0-9]+?)[^0-9]""")[0]
        #baseUrl.split('?')[0].endswith('.swf') and
        if '' != videoid: configUrl = "http://video.sibnet.ru/shell_config_xml.php?videoid=%s&partner=null&playlist_position=null&playlist_size=0&related_albid=0&related_tagid=0&related_ids=null&repeat=null&nocache" % (videoid)
        else: configUrl = baseUrl
        # get video for android
        HTTP_HEADER = dict(self.HTTP_HEADER)
        HTTP_HEADER['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
        sts, data = self.cm.getPage(configUrl, {'header':HTTP_HEADER})
        if sts:
            url = self.cm.ph.getSearchGroups(data, """<file>(http[^<]+?\.mp4)</file>""")[0]
            if '' == url: url = self.cm.ph.getSearchGroups(data, """(http[^"']+?\.mp4)""")[0]
            if '' != url: videoUrls.append({'name':'video.sibnet.ru: mp4', 'url':url})
        # get video for PC
        sts, data = self.cm.getPage(configUrl)
        if sts:
            url = self.cm.ph.getSearchGroups(data, """<file>(http[^<]+?)</file>""")[0]
            if '' == url: url = self.cm.ph.getSearchGroups(data, """['"]file['"][ ]*?:[ ]*?['"]([^"^']+?)['"]""")[0]
            if url.split('?')[0].endswith('.m3u8'):
                retTab = getDirectM3U8Playlist(url)
                for item in retTab:
                    videoUrls.append({'name':'video.sibnet.ru: ' + item['name'], 'url':item['url']})
            elif '' != url: videoUrls.append({'name':'video.sibnet.ru: ' + url.split('.')[-1], 'url':url})
        return videoUrls
        '''
        # Old code not used
        mid = re.search('videoid=(.+?)$',url)
        ourl = 'http://video.sibnet.ru'
        movie = 'http://video.sibnet.ru/v/qwerty/'+mid.group(1)+'.mp4?start=0'
        query_data = { 'url': ourl+'/video'+mid.group(1), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.search("'file':'(.+?)'",link)
        if match:
            sUrl = match.group(1)
            if not sUrl.startswith('http'):
                sUrl = ourl + sUrl
            return sUrl
        else:
            return False
        '''

    def parserVK(self, url):
        sts, data = self.cm.getPage(url)
        if not sts: return False
        movieUrls = []
        item = self.cm.ph.getSearchGroups(data, 'cache([0-9]+?)=(http[^"]+?\.mp4[^;]*)', 2)
        if '' != item[1]:
            cacheItem = { 'name': 'vk.com: ' + item[0] + 'p (cache)', 'url':item[1].encode('UTF-8') }
        else: cacheItem = None
        
        tmpTab = re.findall('url([0-9]+?)=(http[^"]+?\.mp4[^;]*)', data)
        ##prepare urls list without duplicates
        for item in tmpTab:
            item = list(item)
            if item[1].endswith('&amp'): item[1] = item[1][:-4]
            found = False
            for urlItem in movieUrls:
                if item[1] == urlItem['url']:
                    found = True
                    break
            if not found:        
                movieUrls.append({ 'name': 'vk.com: ' + item[0] + 'p', 'url':item[1].encode('UTF-8') })
        ##move default format to first position in urls list
        ##default format should be a configurable
        DEFAULT_FORMAT = 'vk.com: 360p'
        defaultItem = None
        for idx in range(len(movieUrls)):
            if DEFAULT_FORMAT == movieUrls[idx]['name']:
                defaultItem = movieUrls[idx]
                del movieUrls[idx]
                break
        if None != defaultItem:
            movieUrls.insert(0, defaultItem)
        if None != cacheItem:
            movieUrls.insert(0, cacheItem)
        return movieUrls

    def parserPETEAVA(self, url):
        mid = re.search("hd_file=(.+?_high.mp4)&", url)
        movie = "http://content.peteava.ro/video/"+mid.group(1)+"?token=PETEAVARO"
        return movie

    def parserVPLAY(self, url):
        vid = re.search("key=(.+?)$", url)
        query_data = { 'url': 'http://www.vplay.ro/play/dinosaur.do', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        postdata = {'key':vid.group(1)}
        link = self.cm.getURLRequestData(query_data, postdata)
        movie = re.search("nqURL=(.+?)&", link)
        if movie:
            return movie.group(1)
        else:
            return False

    def parserIITV(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        query_data_non = { 'url': url + '.html?i&e&m=iitv', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        if 'streamo' in url:
            match = re.compile("url: '(.+?)',").findall(self.cm.getURLRequestData(query_data))
        if 'nonlimit' in url:
            match = re.compile('url: "(.+?)",     provider:').findall(self.cm.getURLRequestData(query_data_non))
        if len(match) > 0:
            linkVideo = match[0]
            print ('linkVideo ' + linkVideo)
            return linkVideo
        else:
            print ('Przepraszamy','Obecnie zbyt dużo osób ogląda film za pomocą', 'darmowego playera premium.', 'Sproboj ponownie za jakis czas')
        return False

    def parserDIVXSTAGE(self,url):
        return self._parserUNIVERSAL_B(url)
            
    def parserBESTREAMS(self, baseUrl):
        printDBG("parserBESTREAMS baseUrl[%s]" % baseUrl)
        USER_AGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
        video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '[/-]([A-Za-z0-9]{12})[/-]')[0]
        
        url = 'http://bestreams.net/{0}'.format(video_id)
        
        HTTP_HEADER = dict(self.HTTP_HEADER)
        HTTP_HEADER['User-Agent'] = USER_AGENT
        HTTP_HEADER['Referer'] = baseUrl
        sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER})
        
        tries = 0
        while tries < 3:
            tries += 1

            try:
                sleep_time = self.cm.ph.getSearchGroups(data, '>([0-9])</span> seconds<')[0]
                sleep_time = int(sleep_time)
                if sleep_time < 12: time.sleep(sleep_time)
            except:
                printExc()
            
            sts, data = self.cm.ph.getDataBeetwenMarkers(data, 'method="POST"', '</Form>', False, False)
            if not sts: continue
            post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
            HTTP_HEADER['Referer'] = url
            sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER}, post_data)
            if not sts: continue
            #printDBG(data)
            
            try:
                tmp = self.cm.ph.getDataBeetwenMarkers(data, 'id="file_title"', '</a>', False)[1]
                videoUrl = self.cm.ph.getSearchGroups(tmp, 'href="(http[^"]+?)"')[0]
                if '' == videoUrl: continue
                return urlparser.decorateUrl(videoUrl, {'User-Agent':USER_AGENT})
            except:
                printExc()
            
        return False

    def parserTUBECLOUD(self, url):
        self.COOKIEFILE = self.COOKIE_PATH + "tubecloud.cookie"
        query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        ID = re.search('name="id" value="(.+?)">', link)
        FNAME = re.search('name="fname" value="(.+?)">', link)
        HASH = re.search('name="hash" value="(.+?)">', link)
        if ID and FNAME and HASH > 0:
            time.sleep(105)
            postdata = {'fname' : FNAME.group(1), 'hash' : HASH.group(1), 'id' : ID.group(1), 'imhuman' : 'Proceed to video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile('file: "(.+?)"').findall(link)
            if len(match) > 0:
                linkvideo = match[0]
                return linkvideo
            else:
                return self.parserPLAYEDTO(url)
        else:
            return self.parserPLAYEDTO(url)
            
    def parserPLAYEDTO(self, url):
        sts, data = self.cm.getPage(url)
        url = re.search('file: "(http[^"]+?)"', data)
        if url:
            return url.group(1)
        return False
        
    def parserFREEDISC(self, url):
        linksTab = []
        baseUrl = 'http://freedisc.pl/'
        userAgent = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
        sts, data = self.cm.getPage(url)
        if not sts: return linksTab
        data = re.findall('data-duration="([^"]+?)"[ ]*?data-video-url="([^"]+?)"', data)
        for item in data:
            if len(item[1]):
                if item[1].startswith('http'): url = item[1] + '?start=0'
                else: url = baseUrl + item[1] + '?start=0'
                linksTab.append({'name':'freedisc.pl ' + item[0], 'url': urlparser.decorateUrl(url, {'User-Agent':userAgent})})
        return linksTab

    def parserGINBIG(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        ID = re.search('name="id" value="(.+?)">', link)
        FNAME = re.search('name="fname" value="(.+?)">', link)
        if ID and FNAME > 0:
            postdata = { 'op': 'download1', 'id': ID.group(1), 'fname': FNAME.group(1), 'referer': url, 'method_free': 'Free Download', 'usr_login': '' }
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            data = link.replace('|', '<>')
            PL = re.search('<>player<>(.+?)<>flvplayer<>', data)
            HS = re.search('video<>(.+?)<>(.+?)<>file<>', data)
            if PL and HS > 0:
                linkVideo = 'http://' + PL.group(1) + '.ginbig.com:' + HS.group(2) + '/d/' + HS.group(1) + '/video.mp4?start=0'
                print ('linkVideo ' + linkVideo)
                return linkVideo
            else:
                return False
        else:
            return False

    def parserQFER(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        match = re.compile('"PSST",url: "(.+?)"').findall(self.cm.getURLRequestData(query_data))
        if len(match) > 0:
            linkVideo = match[0]
            print ('linkVideo ' + linkVideo)
            return linkVideo
        else:
            return False

    def parserSTREAMCLOUD(self, baseUrl):
        printDBG("parserSTREAMCLOUD [%s]" % baseUrl)
        # code from https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/streamcloud.py
    
        _VALID_URL = r'https?://streamcloud\.eu/(?P<id>[a-zA-Z0-9_-]+)(?:/(?P<fname>[^#?]*)\.html)?'
        mobj = re.match(_VALID_URL, baseUrl)
        video_id = mobj.group('id')
        url = 'http://streamcloud.eu/%s' % video_id
        
        sts, data = self.cm.getPage(url)
        if not sts: return False
        
        fields = re.findall(r'''(?x)<input\s+
            type="(?:hidden|submit)"\s+
            name="([^"]+)"\s+
            (?:id="[^"]+"\s+)?
            value="([^"]*)"
            ''', data)
            
        time.sleep(12)
        
        sts, data = self.cm.getPage(url, {}, fields)
        if not sts: return False
        
        file = self.cm.ph.getSearchGroups(data, r'''['"]?file['"]?[ ]*:[ ]*['"]([^"^']+)['"],''')[0]        
        if file.startswith('http'): return file

        return False

    def parserLIMEVIDEO(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        ID = re.search('name="id" value="(.+?)">', link)
        FNAME = re.search('name="fname" value="(.+?)">', link)
        if ID and FNAME > 0:
            time.sleep(205)
            postdata = {'fname' : FNAME.group(1), 'id' : ID.group(1), 'method_free' : 'Continue to Video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            ID = re.search('name="id" value="(.+?)">', link)
            RAND = re.search('name="rand" value="(.+?)">', link)
            table = self.captcha.textCaptcha(link)
            value = table[0][0] + table [1][0] + table [2][0] + table [3][0]
            code = self.cm.html_entity_decode(value)
            print ('captcha-code :' + code)
            if ID and RAND > 0:
                postdata = {'rand' : RAND.group(1), 'id' : ID.group(1), 'method_free' : 'Continue to Video', 'op' : 'download2', 'referer' : url, 'down_direct' : '1', 'code' : code, 'method_premium' : '' }
                query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
                link = self.cm.getURLRequestData(query_data, postdata)
                data = link.replace('|', '<>')
                PL = re.search('<>player<>video<>(.+?)<>(.+?)<>(.+?)<><>(.+?)<>flvplayer<>', data)
                HS = re.search('image<>(.+?)<>(.+?)<>(.+?)<>file<>', data)
                if PL and HS > 0:
                    linkVideo = 'http://' + PL.group(4) + '.' + PL.group(3) + '.' + PL.group(2) + '.' + PL.group(1) + ':' + HS.group(3) + '/d/' + HS.group(2) + '/video.' + HS.group(1)
                    print ('linkVideo :' + linkVideo)
                    return linkVideo
                else:
                    return False
            else:
                return False
        else:
            return False

    def parserSCS(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        ID = re.search('"(.+?)"; ccc', link)
        if ID > 0:
            postdata = {'f' : ID.group(1) }
            query_data = { 'url': 'http://scs.pl/getVideo.html', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile("url: '(.+?)',").findall(link)
            if len(match) > 0:
                linkVideo = match[0]
                print ('linkVideo ' + linkVideo)
                return linkVideo
            else:
                print ('Przepraszamy','Obecnie zbyt dużo osób ogląda film za pomocą', 'darmowego playera premium.', 'Sproboj ponownie za jakis czas')
                return False
        else:
            return False
        
    def parserYOUWATCH(self, baseUrl):
        if 'embed' in baseUrl:
            url = baseUrl
        else:
            url = baseUrl.replace('org/', 'org/embed-').replace('to/', 'to/embed-') + '.html'
        COOKIE_FILE = GetCookieDir('youwatchorg.cookie')
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0'}
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True, 'load_cookie':True}
        
        tries = 0
        while tries < 3:
            tries += 1
            sts, data = self.cm.getPage(url, params)
            if not sts: return False
            if 'sources:' in data:
                break
            else:
                params['header']['Referer'] = url
                url = self.cm.ph.getSearchGroups(data, '<iframe[^>]*?src="(http[^"]+?)"', 1, True)[0].replace('\n', '')
        #printDBG(data)
        return self._findLinks(data)

    def parserPLAYEDTO(self, baseUrl):
        if 'embed' in baseUrl:
            url = baseUrl
        else:
            url = baseUrl.replace('org/', 'org/embed-').replace('to/', 'to/embed-') + '-640x360.html'

        sts, data = self.cm.getPage(url)
        if not sts: return False
        
        if iframe:
            url = self.cm.ph.getSearchGroups(data, '<iframe[^>]*?src="(http[^"]+?)"', 1, True)[0]
            if url != '':
                sts, data = self.cm.getPage(url, {'header':{'Referer':url, 'User-Agent':'Mozilla/5.0'}})
                if not sts: return False
        
        # get JS player script code from confirmation page
        sts, tmpData = CParsingHelper.getDataBeetwenMarkers(data, ">eval(", '</script>', False)
        if sts:
            data = tmpData
            tmpData = None
            # unpack and decode params from JS player script code
            data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams, 0) #YOUWATCH_decryptPlayerParams == VIDUPME_decryptPlayerParams

        # get direct link to file from params
        data = re.search('file:[ ]*?"([^"]+?)"', data)
        if data:
            linkVideo = data.group(1)
            printDBG('parserPLAYEDTO direct link: ' + linkVideo)
            return linkVideo
        return False
    '''
    def parserALLMYVIDEOS(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        ID = re.search('name="id" value="(.+?)">', link)
        FNAME = re.search('name="fname" value="(.+?)">', link)
        if ID and FNAME > 0:
            time.sleep(105)
            postdata = {'fname' : FNAME.group(1), 'method_free' : '1', 'id' : ID.group(1), 'x' : '82', 'y' : '13', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile('"file" : "(.+?)",').findall(link)
            if len(match) > 0:
                linkVideo = match[0]
                print ('linkVideo ' + linkVideo)
                return linkVideo
            else:
                return False
        else:
            return False
    '''
            
    def parserVIDEOMEGA(self,baseUrl):
        video_id  = self.cm.ph.getSearchGroups(baseUrl, 'https?://(?:www\.)?videomega\.tv/(?:iframe\.php|cdn\.php|view\.php)?\?ref=([A-Za-z0-9]+)')[0]
        COOKIE_FILE = GetCookieDir('videomegatv.cookie')
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0'} # (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10' }
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        
        #if 'iframe' in baseUrl:
        #    iframe_url = 'http://videomega.tv/iframe.php?ref=%s' % (video_id)
        #    url = 'http://videomega.tv/iframe.php?ref=%s' % (video_id)
        #else:
        if True:
            iframe_url = 'http://videomega.tv/?ref=%s' % (video_id)
            url = 'http://videomega.tv/cdn.php?ref=%s' % (video_id)
        HTTP_HEADER['Referer'] = iframe_url
        sts, data = self.cm.getPage(url, params)
        if not sts: 
            return False
        if 'dmca ' in data:
            DMCA = True
            SetIPTVPlayerLastHostError("'Digital Millennium Copyright Act' detected.")
            return False
        else: DMCA = False
        
        adUrl =self.cm.ph.getSearchGroups(data, '"([^"]+?/ad\.php[^"]+?)"')[0]
        if adUrl.startswith("/"): 
            adUrl = 'http://videomega.tv' + adUrl
        
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'load_cookie':True, 'save_cookie':False} 
        HTTP_HEADER['Referer'] = url
        sts, tmp = self.cm.getPage(adUrl, params)
        
        #linkVideo  = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"[^>]+?type="video')[0]
       
        #data = data[data.rfind('}(')+2:-2]
        #data = unpackJS(data, SAWLIVETV_decryptPlayerParams)
        
        # get JS player script code from confirmation page
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, "eval(", '</script>')
        if not sts: return False
        # unpack and decode params from JS player script code
        data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams, 0)
        
        linkVideo  = self.cm.ph.getSearchGroups(data, '"(http[^"]+?\.mp4\?[^"]+?)"')[0]
        
        #printDBG('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        #printDBG("DMCA [%r]" % DMCA)
        #printDBG('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        #printDBG(data)
        #printDBG('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        if linkVideo.startswith('http'):
            linkVideo = urlparser.decorateUrl(linkVideo, {"Orgin": "http://videomega.tv/", 'Referer': url, 'User-Agent':HTTP_HEADER['User-Agent'], 'iptv_buffering':'required'})
        else: linkVideo = False #"Cookie": "__cfduid=1", "Range": "bytes=0-",
        return linkVideo

    def parserVIDTO(self, baseUrl):
        printDBG('parserVIDTO baseUrl[%s]' % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        if 'embed' not in baseUrl:
            video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9]{12})[\./]')[0]
            url = 'http://vidto.me/embed-{0}-640x360.html'.format(video_id)
        else:
            url = baseUrl 
        params = {'header' : HTTP_HEADER}
        sts, data = self.cm.getPage(url, params)
        
        # get JS player script code from confirmation page
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, ">eval(", '</script>')
        if not sts: return False
        # unpack and decode params from JS player script code
        data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams)
        return self._findLinks(data, 'vidto.me', m1='hd', m2=']')
        # get direct link to file from params
        data = re.search('file:"([^"]+?)"', data)
        if data:
            directURL = data.group(1) + "?start=0"
            printDBG("VIDTO.ME DIRECT URL: [%s]" % directURL )
            return directURL
        return False

    def parserVIDSTREAM(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        ID = re.search('name="id" value="(.+?)">', link)
        FNAME = re.search('name="fname" value="(.+?)">', link)
        HASH = re.search('name="hash" value="(.+?)">', link)
        if ID and FNAME and HASH > 0:
            time.sleep(55)
            postdata = {'fname' : FNAME.group(1), 'id' : ID.group(1), 'hash' : HASH.group(1), 'imhuman' : 'Proceed to video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile('file: "(.+?)",').findall(link)
            if len(match) > 0:
                linkVideo = match[0]
                printDBG ('linkVideo :' + linkVideo)
                return linkVideo
            else:
                return False
        else:
            return False
        
    def parserYANDEX(self, url):
        #http://www.kreskoweczki.pl/kreskowka/71428/nawiedzeni_4-haunted-kids/
        #http://seositer.com/player10-loader.swf?login=eriica&storage_directory=xeacxjweav.5822/&is-hq=false
        #player10-loader.swf?login=eriica&storage_directory=xeacxjweav.5822/&is-hq=true
        DEFAULT_FORMAT = 'mpeg4_low'
        # authorization
        authData = ''
        urlElems = urlparse(url)
        urlParams = parse_qs(urlElems.query)
        if 0 < len(urlParams.get('file', [])):
            return urlParams['file'][0]
        elif 0 < len(urlParams.get('login', [])) and 0 < len(urlParams.get('storage_directory', [])):
            authData = urlParams['login'][0] + '/' + urlParams['storage_directory'][0]
        elif 'vkid=' in url:
            sts, data = self.cm.getPage(url)
            if not sts: return False
            data = self.cm.ph.getSearchGroups(data, '<iframe[^>]+?src="([^"]+?)"')[0]
            return urlparser().getVideoLink(data, True)
        else:
            # last chance
            r = re.compile('iframe/(.+?)\?|$').findall(url)
            if 0 <= len(r): return False
            authData = r[0]
        # consts
        playerUrlPrefix    = "http://flv.video.yandex.ru/"
        tokenUrlPrefix     = "http://static.video.yandex.ru/get-token/"
        serviceHostUrl     = "http://video.yandex.ru/"
        storageHostUrl     = "http://static.video.yandex.ru/"
        clipStorageHostUrl = "http://streaming.video.yandex.ru/"
        nameSpace          = "get"
        FORMATS_MAP = {}
        FORMATS_MAP["flv_low"]          = "0.flv"
        FORMATS_MAP["mpeg4_low"]        = "m450x334.mp4"
        FORMATS_MAP["mpeg4_med"]        = "medium.mp4"
        FORMATS_MAP["mpeg4_hd_720p"]    = "m1280x720.mp4"
        FORMATS_MAP["flv_h264_low"]     = "m450x334.flv"
        FORMATS_MAP["flv_h264_med"]     = "medium.flv"
        FORMATS_MAP["flv_h264_hd_720p"] = "m1FLV_SAME_QUALITY280x720.flv"
        FORMATS_MAP["flv_same_quality"] = "sq-medium.flv"
        
        # get all video formats info
        # http://static.video.yandex.ru/get/eriica/xeacxjweav.5822//0h.xml?nc=0.9776535825803876
        url = storageHostUrl + nameSpace + "/" + authData + "/0h.xml?nc=" + str(random())
        sts, data = self.cm.getPage(url)
        if not sts: return False
        try:
            formatsTab = []
            defaultItem = None
            for videoFormat in cElementTree.fromstring(data).find("formats_available").getiterator():
                fileName = FORMATS_MAP.get(videoFormat.tag, '')
                if '' != fileName:
                    bitrate  = int(videoFormat.get('bitrate', 0))
                    formatItem = { 'bitrate': bitrate, 'file':fileName, 'ext':fileName[-3:] }
                    if DEFAULT_FORMAT == videoFormat.tag:
                        defaultItem = formatItem
                    else:
                        formatsTab.append(formatItem)
            if None != defaultItem: formatsTab.insert(0, defaultItem)
            if 0 == len(formatsTab): return False
            # get token
            token = tokenUrlPrefix + authData + "?nc=" + str(random())
            sts, token = self.cm.getPage(token)
            sts, token = CParsingHelper.getDataBeetwenMarkers(token, "<token>", '</token>', False)
            if not sts:
                printDBG("parserYANDEX - get token problem")
                return False
            movieUrls = []
            for item in formatsTab:
                # get location
                location = clipStorageHostUrl + 'get-location/' + authData + '/' + item['file'] + '?token=' + token + '&ref=video.yandex.ru'
                sts, location = self.cm.getPage(location)
                sts, location = CParsingHelper.getDataBeetwenMarkers(location, "<video-location>", '</video-location>', False)
                if sts: movieUrls.append({ 'name': 'yandex.ru: ' + item['ext'] + ' bitrate: ' + str(item['bitrate']), 'url':location.replace('&amp;', '&') })
                else: printDBG("parserYANDEX - get location problem")
            return movieUrls
        except:
            printDBG("parserYANDEX - formats xml problem")
            printExc()
            return False
        
    def parserANIMESHINDEN(self, url):
        query_data = { 'url': url, 'return_data': False }       
        response = self.cm.getURLRequestData(query_data)
        redirectUrl = response.geturl() 
        response.close()
        redirectUrl = redirectUrl.replace('https', 'http')
        return redirectUrl

    def parserRUTUBE(self, url):
        if '//rutube.ru/video/embed' in url or '//rutube.ru/play/embed/' in url:
            sts, data = self.cm.getPage(url)
            if not sts: return False
            data = re.search('href="([^"]+?)"', data)
            if not data: return False
            url = data.group(1)
        videoID = ''
        url += '/'

        # get videoID/hash
        match = re.search('video\.rutube\.ru/(\w+?)/', url)
        if match:
            videoID = match.group(1)
        else:
            match = re.search('/video/(\w+?)/', url)
            if match:
                videoID = match.group(1)
            else:
                match = re.search('hash=([^/]+?)/', url)
                if match:
                    videoID = match.group(1)
        if '' != videoID:
            printDBG('parserRUTUBE:                 videoID[%s]' % videoID)
            # get videoInfo:
            #vidInfoUrl = 'http://rutube.ru/api/play/trackinfo/%s/?format=json' % videoID
            vidInfoUrl = 'http://rutube.ru/api/play/options/%s/?format=json&referer=&no_404=true&sqr4374_compat=1' % videoID
            query_data = { 'url': vidInfoUrl, 'return_data': True }
            try:
                videoInfo = self.cm.getURLRequestData(query_data)
            except:
                printDBG('parserRUTUBE problem with getting video info page')
                return []
            printDBG('---------------------------------------------------------')
            printDBG(videoInfo)
            printDBG('---------------------------------------------------------')
            # "m3u8": "http://bl.rutube.ru/ae8621ff85153a30c398746ed8d6cc03.m3u8"
            # "f4m": "http://bl.rutube.ru/ae8621ff85153a30c398746ed8d6cc03.f4m"
            videoUrls = []
            match = re.search('"m3u8":[ ]*?"(http://bl\.rutube\.ru/.+?)"', videoInfo)
            if match:
                printDBG('parserRUTUBE m3u8 link[%s]' % match.group(1))
                retTab = getDirectM3U8Playlist(match.group(1))
                videoUrls.extend(retTab)
            else:
                printDBG('parserRUTUBE there is no m3u8 link in videoInfo:')
                printDBG('---------------------------------------------------------')
                printDBG(videoInfo)
                printDBG('---------------------------------------------------------')
               
            match = re.search('"default":[ ]*?"(http://[^"]+?f4m[^"]*?)"', videoInfo)
            if match:
                printDBG('parserRUTUBE f4m link[%s]' % match.group(1))
                retTab = getF4MLinksWithMeta(match.group(1))
                videoUrls.extend(retTab)
            return videoUrls
        else:
            printDBG('parserRUTUBE ERROR cannot find videoID in link[%s]' % url)
            return []
    
    def parserYOUTUBE(self, url):
        if None != self.getYTParser():
            try:
                formats = config.plugins.iptvplayer.ytformat.value
                bitrate = config.plugins.iptvplayer.ytDefaultformat.value
                dash    = config.plugins.iptvplayer.ytShowDash.value
            except:
                printDBG("parserYOUTUBE default ytformat or ytDefaultformat not available here")
                formats = "mp4"
                bitrate = "360"
                dash    = False
            
            tmpTab, dashTab = self.getYTParser().getDirectLinks(url, formats, dash, dashSepareteList = True)
            # move default URL to the TOP of list
            if 1 < len(tmpTab):
                def __getLinkQuality( itemLink ):
                    tab = itemLink['format'].split('x')
                    return int(tab[0])

                # get default item
                defItem = CSelOneLink(tmpTab, __getLinkQuality, int(bitrate)).getOneLink()[0]
                # remove default item
                tmpTab[:] = [x for x in tmpTab if x['url'] != defItem['url']]
                # add default item at top
                tmpTab.insert(0, defItem)
                    
            videoUrls = []
            for item in tmpTab:
                videoUrls.append({ 'name': 'YouTube: ' + item['format'] + '\t' + item['ext'] , 'url':item['url'].encode('UTF-8') })
            for item in dashTab:
                videoUrls.append({'name': _("[For download only] ") + item['format'] + ' | dash', 'url':item['url']})
            return videoUrls

        return False
        
    def parserTINYMOV(self, url):
        printDBG('parserTINYMOV url[%s]' % url)
        sts, data = self.cm.getPage(url)
        if sts:
            match = re.search("url: '([^']+?.mp4|[^']+?.flv)',", data)
            if match:
                linkVideo = match.group(1)
                printDBG ('parserTINYMOV linkVideo :' + linkVideo)
                return linkVideo
            
        return False
     
    def parserTOPUPLOAD(self, url):
        url = url.replace('topupload.tv', 'maxupload.tv')
        HTTP_HEADER = {'Referer':url}
        post_data = {'ok':'yes', 'confirm':'Close+Ad+and+Watch+as+Free+User', 'submited':'true'}        
        sts, data = self.cm.getPage(url=url, addParams={'header':HTTP_HEADER}, post_data = post_data)
        if sts:
            posibility = ["'file': '([^']+?)'", "file: '([^']+?)'", "'url': '(http[^']+?)'", "url: '(http[^']+?)'"]
            for posibe in posibility:
                match = re.search(posibe, data)  
                if match:
                    try:
                        header = {'Referer':'http://www.maxupload.tv/media/swf/player/player.swf'}
                        query_data = { 'url': match.group(1), 'return_data': False, 'header':header }
                        response = self.cm.getURLRequestData(query_data)
                        redirectUrl = response.geturl() 
                        response.close()
                        return redirectUrl
                    except:
                        printExc()
            else:
                printDBG('parserTOPUPLOAD direct link not found in return data')
        else:
            printDBG('parserTOPUPLOAD error when getting page')
        return False
        
    def parserLIVELEAK(self, baseUrl):
        printDBG('parserLIVELEAK baseUrl[%s]' % baseUrl)
        urlTab = []
        sts, data = self.cm.getPage(baseUrl)
        if sts:
            file_url    = urllib.unquote(self.cm.ph.getSearchGroups(data, 'file_url=(http[^&]+?)&')[0])
            hd_file_url = urllib.unquote(self.cm.ph.getSearchGroups(data, 'hd_file_url=(http[^&]+?)&')[0])
            if '' != file_url:
                urlTab.append({'name':'liveleak.com SD', 'url':file_url})
            if '' != hd_file_url:
                urlTab.append({'name':'liveleak.com HD', 'url':hd_file_url})
                
            printDBG(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> [%s]" % urlTab)
            if 0 == len(urlTab):
                url = self.cm.ph.getSearchGroups(data, '<iframe[^>]+?src="(http[^"]+?youtube[^"]+?)"')[0]
                if '' != url:
                    urlTab = self.parserYOUTUBE(url)
        return urlTab
            
    def parserVIDUPME(self, url):
        COOKIE_FILE = GetCookieDir('vidupme.cookie')
        HTTP_HEADER= { 'Host':'vidup.me',
                       'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        # get embedded video page and save returned cookie
        sts, data = self.cm.getPage(url, params)
        if not sts: return False
        
        # get confirmation "Watch as Free User" url 
        data = re.search('<form method="get" action="([^"]+?)">', data)
        if not data: return False

        HTTP_HEADER['Referer'] = url
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'load_cookie':True, 'save_cookie':False} 
        # send confirmation 
        sts, data = self.cm.getPage('http://vidup.me' + data.group(1) + "?play=1&confirm=Close+Ad+and+Watch+as+Free+User", params)
        if not sts: return False
        # get JS player script code from confirmation page
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, ">eval(", '</script>')
        if not sts: return False
        # unpack and decode params from JS player script code
        data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams)
        # get direct link to file from params
        data = re.search('file:"([^"]+?)"', data)
        if data:
            directURL = data.group(1) + "?start=0"
            printDBG("VIDUPME DIRECT URL: [%s]" % directURL )
            return directURL
        return False
        
    def parserTRILULILU(self, baseUrl):
        def getTrack(userid, hash):
            hashLen = len(hash) / 2
            mixedStr = (hash[0:hashLen] + userid) + hash[hashLen:len(hash)]
            md5Obj = MD5()
            hashTab = md5Obj(mixedStr)
            return hexlify(hashTab)
        
        match = re.search("embed\.trilulilu\.ro/video/([^/]+?)/([^.]+?)\.swf", baseUrl)
        data = None
        if not match:
            sts, data = self.cm.getPage(baseUrl)
            if not sts: return False
            match = re.search('userid=([^"^<^>^&]+?)&hash=([^"^<^>^&]+?)&', data)
        if match:          
            userid = match.group(1)
            hash = match.group(2)
            refererUrl = "http://static.trilulilu.ro/flash/player/videoplayer2011.swf?userid=%s&hash=%s&referer=" % (userid, hash)
            fileUrl = "http://embed.trilulilu.ro/flv/" + userid + "/" + hash + "?t=" + getTrack(userid, hash) + "&referer=" + urllib.quote_plus( base64.b64encode(refererUrl) ) + "&format=mp4-360p"
            return fileUrl
        # new way to get video
        if sts:
            url = self.cm.ph.getSearchGroups(data, 'id="link" href="(http[^"]+?)"')[0]
            if '' != url:
                HTTP_HEADER = dict(self.HTTP_HEADER) 
                HTTP_HEADER['Referer'] = baseUrl
                sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER})
                data = self.cm.ph.getSearchGroups(data, """["']*video["']*:[ ]*["']([^"']+?)["']""")[0]
                if '' != data:
                    if data.startswith('//'):
                        data = 'http:' + data
                    return data
        return False
        
    def parserVIDEA(self, url):
        sts, data = self.cm.getPage(url)
        if not sts: return False
        r = re.compile('v=(.+?)&eventHandler').findall(data)
        sts, data = self.cm.getPage('http://videa.hu/flvplayer_get_video_xml.php?v='+r[0])
        if not sts: return False
        r2 = re.compile('video_url="(.+?)"').findall(data)
        return r2[0]

    def parserALIEZ(self, url):
        sts, data = self.cm.getPage(url)
        if not sts: return False
        r = re.compile("file:.+?'(.+?)'").findall(data)
        return r[0]
        
    def parserVIDEOMAIL(self, url):
        printDBG("parserVIDEOMAIL baseUrl[%s]" % url)
        #http://api.video.mail.ru/videos/embed/mail/etaszto/_myvideo/852.html
        #http://my.mail.ru/video/mail/etaszto/_myvideo/852.html#video=/mail/etaszto/_myvideo/852
        COOKIEFILE = self.COOKIE_PATH + "video.mail.ru.cookie"
        movieUrls = []
        try:
            sts, data = self.cm.getPage(url, {'cookiefile': COOKIEFILE, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False})
            if 'This video is only available on Mail.Ru' in data:
                tmpUrl = self.cm.ph.getSearchGroups(data, 'href="([^"]+?)"')[0]
                sts, data = self.cm.getPage(tmpUrl)
            metadataUrl =  self.cm.ph.getSearchGroups(data, """["']*metadataUrl["']*[ ]*:[ ]*["'](http[^"']+?\.json[^"']*?)["']""")[0]
            if '' == metadataUrl:
                tmp = self.cm.ph.getSearchGroups(data, '<link[^>]*?rel="image_src"[^>]*?href="([^"]+?)"')[0]
                if '' == tmp: tmp = self.cm.ph.getSearchGroups(data, '<link[^>]*?href="([^"]+?)"[^>]*?rel="image_src"[^>]*?')[0]
                tmp = self.cm.ph.getSearchGroups(urllib.unquote(tmp), '[^0-9]([0-9]{19})[^0-9]')[0]
                metadataUrl = 'http://videoapi.my.mail.ru/videos/{0}.json?ver=0.2.102'.format(tmp)
            sts, data = self.cm.getPage(metadataUrl, {'cookiefile': COOKIEFILE, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True})
            video_key = self.cm.getCookieItem(COOKIEFILE,'video_key')
            if '' != video_key:
                data = json.loads(data)['videos']
                for item in data:
                    videoUrl = strwithmeta(item['url'].encode('utf-8'), {'Cookie':"video_key=%s" % video_key, 'iptv_buffering':'required'})
                    videoName = 'mail.ru: %s' % item['key'].encode('utf-8')
                    movieUrls.append({ 'name': videoName, 'url': videoUrl}) 
        except:
            printExc()
        # Try old code extractor
        if 0 == len(movieUrls):
            idx = url.find(".html")
            if 1 > idx: return False
            authData = url[:idx].split('/')
            url = 'http://api.video.mail.ru/videos/' + authData[-4] + '/' + authData[-3] + '/' + authData[-2] + '/' + authData[-1] + '.json'
            sts, data = self.cm.getPage(url, {'cookiefile': COOKIEFILE, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False})
            if not sts: return False
            video_key = self.cm.getCookieItem(COOKIEFILE,'video_key')
            if '' == video_key: return False
            data = re.search('"videos":{([^}]+?)}', data)
            if not data: return False
            formats = ['sd', 'hd']
            for item in formats:
                url = re.search('"%s":"([^"]+?)"' % item, data.group(1))
                if url:
                    movieUrls.append({ 'name': 'mail.ru: %s' % item, 'url':url.group(1) + '|Cookie="video_key=' + video_key + '"' })
        return movieUrls
        
        
    def parserWRZUTA(self, url):
        movieUrls = []
        
        # start algo from https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/wrzuta.py
        _VALID_URL = r'https?://(?P<uploader>[0-9a-zA-Z]+)\.wrzuta\.pl/(?P<typ>film|audio)/(?P<id>[0-9a-zA-Z]+)'
        try:
            while True:
                mobj = re.match(_VALID_URL, url)
                video_id = mobj.group('id')
                typ = mobj.group('typ')
                uploader = mobj.group('uploader')
                
                #sts, data = self.cm.getPage(url)
                #if not sts: break
                quality = {'SD':240, 'MQ':360, 'HQ':480, 'HD':720}
                audio_table = {'flv': 'mp3', 'webm': 'ogg', '???': 'mp3'}
                sts, data = self.cm.getPage('http://www.wrzuta.pl/npp/embed/%s/%s' % (uploader, video_id))
                if not sts: break
                
                data = byteify( json.loads(data) )
                for media in data['url']:
                    fmt = media['type'].split('@')[0]
                    if typ == 'audio':
                        ext = audio_table.get(fmt, fmt)
                    else:
                        ext = fmt
                    if fmt in ['webm']: continue
                    movieUrls.append({'name': 'wrzuta.pl: ' + str(quality.get(media['quality'], 0)) + 'p', 'url':media['url']})                
                break;
        
        except: 
            printExc()
        # end algo
        
        if len(movieUrls): return movieUrls
    
        def getShardUserFromKey(key):
            tab = ["w24", "w101", "w70", "w60", "w2", "w14", "w131", "w121", "w50", "w40", "w44", "w450", "w90", "w80", "w30", "w20", "w25", "w100", "w71", "w61", "w1", "w15", "w130", "w120", "w51", "w41", "w45", "w451", "w91", "w81", "w31", "w21"]
            abc = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            usr_idx = 0
            for i in range(11):
                tmp = key[i]
                usr_idx = (usr_idx * len(abc))
                usr_idx = (usr_idx + abc.find(tmp))
                usr_idx = (usr_idx & 0xFFFF)
            return tab[usr_idx]
            
        def getFileData(login, key, flagaXml, host, site, pltype): 
            url = "http://" + login + "." + host + "/xml/" + flagaXml + "/" + key + "/" + site + "/" + pltype + "/" + str(int(random() * 1000000 + 1))
            sts, data = self.cm.getPage(url)
            return data
        
        urlElems = urlparse(url)
        urlParams = parse_qs(urlElems.query)
        site     = urlParams.get('site', ["wrzuta.pl"])[0]
        host     = urlParams.get('host', ["wrzuta.pl"])[0]
        key      = urlParams.get('key', [None])[0]
        login    = urlParams.get('login', [None])[0]
        language = urlParams.get('login', ["pl"])[0]
        boolTab  = ["yes", "true", "t", "1"]
        embeded  = urlParams.get('embeded', ["false"])[0].lower() in boolTab
        inskin   = urlParams.get('inskin', ["false"])[0].lower() in boolTab
        
        if None == key: return False
        if None == login: login = getShardUserFromKey(key)
        if embeded: pltype = "eb"
        elif inskin: pltype = "is"
        else: pltype = "sa"

        data = getFileData(login, key, "kontent", host, site, pltype)
        formatsTab = [{'bitrate':360, 'file':'fileMQId_h5'},\
                      {'bitrate':480, 'file':'fileHQId_h5'},\
                      {'bitrate':720, 'file':'fileHDId_h5'},\
                      {'bitrate':240, 'file':'fileId_h5'}]
        
        for item in formatsTab:
            sts, url = CParsingHelper.getDataBeetwenMarkers(data, "<%s>" % item['file'], '</%s>' % item['file'], False)
            url = url.replace('<![CDATA[', '').replace(']]>', '')
            if sts: movieUrls.append({'name': 'wrzuta.pl: ' + str(item['bitrate']) + 'p', 'url':url.strip() + '/0'})
        return movieUrls
        
    def parserGOLDVODTV(self, url):
        COOKIE_FILE = GetCookieDir('goldvodtv.cookie')
        HTTP_HEADER = { 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3' }
        SWF_URL = 'http://p.jwpcdn.com/6/9/jwplayer.flash.swf'
        
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        sts, data = self.cm.getPage( url, params)
        
        # get connector link
        data = self.cm.ph.getSearchGroups(data, "'(http://goldvod.tv/tv-connector/[^']+?\.smil[^']*?)'")[0]
        params['load_cookie'] = True
        params['header']['Referer'] = SWF_URL
        
        # get stream link
        sts, data = self.cm.getPage(data, params)
        if sts:
            base = self.cm.ph.getSearchGroups(data, 'base="([^"]+?)"')[0]
            src = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
            if ':' in src:
                src = src.split(':')[1]
                
            if base.startswith('rtmp'):
                return base + '/' + src + ' swfUrl=%s live=1 pageUrl=%s' % (SWF_URL, url)
        return False
        
    def parserVIDZER(self, baseUrl):
        printDBG("parserVIDZER baseUrl[%s]" % baseUrl)
        try:
            sts, data = self.cm.getPage(baseUrl)
            if not sts: return False
            url = self.cm.ph.getSearchGroups(data, '<iframe src="(http[^"]+?)"')[0]
            if url != '':        
                sts, data = self.cm.getPage(url)
                if not sts: return False
            data = CParsingHelper.getDataBeetwenMarkers(data, '<div id="playerVidzer">', '</a>', False)[1]
            match = re.search('href="(http[^"]+?)"', data)
            if match:
                url = urllib.unquote( match.group(1) )
                return url
            
            r = re.search('value="(.+?)" name="fuck_you"', data)
            r2 = re.search('name="confirm" type="submit" value="(.+?)"', data)
            r3 = re.search('<a href="/file/([^"]+?)" target', data)
            if r:
                printDBG("r_1[%s]" % r.group(1))
                printDBG("r_2[%s]" % r2.group(1))
                data = 'http://www.vidzer.net/e/'+r3.group(1)+'?w=631&h=425'
                postdata = {'confirm' : r2.group(1), 'fuck_you' : r.group(1)}
                sts, data = self.cm.getPage(data, {}, postdata)
                match = re.search("url: '([^']+?)'", data)
                if match:
                    url = match.group(1) #+ '|Referer=http://www.vidzer.net/media/flowplayer/flowplayer.commercial-3.2.18.swf'
                    return url
                else:
                    return False
            else:
                return False
        except:
            printExc()
            return False
            
    def parserNOWVIDEOCH(self, url):
        printDBG("parserNOWVIDEOCH url[%s]" % url)
        return self._parserUNIVERSAL_B(url)
    
    def parserSTREAMINTO(self, baseUrl):
        printDBG("parserSTREAMINTO baseUrl[%s]" % baseUrl)
        # example video: http://streamin.to/okppigvwdk8w
        #                http://streamin.to/embed-rme4hyg6oiou-640x500.html
        #tmp =  self.__parseJWPLAYER_A(baseUrl, 'streamin.to')
        
        def getPageUrl(data):
            #printDBG("=======================================")
            #printDBG(data)
            #printDBG("=======================================")
            vidTab = []
            streamer = self.cm.ph.getSearchGroups(data, 'streamer: "(rtmp[^"]+?)"')[0]
            printDBG(streamer)
            data     = re.compile('file:[ ]*?"([^"]+?)"').findall(data)
            
            for item in data:
                if item.startswith('http://'):
                    vidTab.insert(0, {'name': 'http://streamin.to/ ', 'url':item})
                elif item.startswith('rtmp://') or '' != streamer:
                    try:
                        if item.startswith('rtmp://'):
                            item     = item.split('flv:')
                            r        = item[0]
                            playpath = item[1]
                        else:
                            r        = streamer
                            playpath = item 
                        swfUrl  = "http://streamin.to/player6/jwplayer.flash.swf"
                        rtmpUrl = r + ' playpath=%s' % playpath + ' swfUrl=%s' % swfUrl + ' pageUrl=%s' % baseUrl
                        vidTab.append({'name': 'rtmp://streamin.to/ ', 'url':urlparser.decorateUrl(rtmpUrl, {'iptv_livestream':False})})
                    except:
                        printExc()
            return vidTab
        vidTab = []
        if 'embed' not in baseUrl:
            baseUrl = 'http://streamin.to/embed-%s-640x500.html' % baseUrl.split('/')[-1]
        
        HTTP_HEADER = {"User-Agent":"Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"}
        sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER})
        if sts:
            errMarker = 'File was deleted'
            if errMarker in data:
                SetIPTVPlayerLastHostError(errMarker)
            vidTab = getPageUrl(data)
            if 0 == len(vidTab):
                cookies_data = ''
                cookies = re.findall("cookie\('([^']*)', '([^']*)'", data)
                for item in cookies:
                    cookies_data += '%s=%s;' % (item[0], item[1])
                
                sts, data = self.cm.ph.getDataBeetwenMarkers(data, 'method="POST"', '</Form>', False)
                post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
                HTTP_HEADER['Referer'] = baseUrl
                # get cookie for streamin.to
                if len(cookies_data):
                    HTTP_HEADER['Cookie'] = cookies_data[:-1]
                try:
                    sleep_time = int(self.cm.ph.getSearchGroups(data, '<span id="cxc">([0-9])</span>')[0])
                    time.sleep(sleep_time)
                except:
                    printExc()
                    
                sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER}, post_data)
                if sts:
                    vidTab = getPageUrl(data)
        return vidTab
        
    def parseVSHAREIO(self, baseUrl):
        printDBG("parseVSHAREIO baseUrl[%s]" % baseUrl)
        # example video: 
        # http://vshare.io/v/72f9061/width-470/height-305/
        # http://vshare.io/v/72f9061/width-470/height-305/
        # http://vshare.io/d/72f9061/1
        video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/[dv]/([A-Za-z0-9]{7})/')[0]
        url = 'http://vshare.io/v/{0}/width-470/height-305/'.format(video_id)
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0', 'Referer':baseUrl}
        
        vidTab = []
        sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER})
        if not sts: return
        
        stream   = self.cm.ph.getSearchGroups(data, '''['"](http://[^"^']+?/stream\,[^"^']+?)['"]''')[0]
        if '' == stream: stream   = self.cm.ph.getSearchGroups(data, '''['"](http://[^"^']+?\.flv)['"]''')[0]
        if '' != stream:
            vidTab.append({'name': 'http://vshare.io/stream ', 'url':stream})
            
        if 0 == len(vidTab):
            data = self.cm.ph.getDataBeetwenMarkers(data, 'clip:', '}', False)[1]
            url = self.cm.ph.getSearchGroups(data, '''['"](http[^"^']+?)['"]''')[0]
            vidTab.append({'name': 'http://vshare.io/ ', 'url':url})
        return vidTab
            
    def parserVIDSSO(self, url):
        printDBG("parserVIDSSO url[%s]" % url)
        # example video: http://www.vidsso.com/video/hhbwr85FMGX
        try:
            sts, data = self.cm.getPage(url)
            try:
                confirm  = re.search('<input name="([^"]+?)" [^>]+?value="([^"]+?)"', data)
                vs       = re.search('<input type="hidden" value="([^"]+?)" name="([^"]+?)">', data)
                post = {confirm.group(1):confirm.group(2), vs.group(2):vs.group(1)}
                sts, data = self.cm.getPage(url, {'Referer':url}, post)
            except:
                printExc()
            
            url = re.search("'file': '(http[^']+?)'", data).group(1)
            return url
        except:
            printExc()
        return False
            
    def parseWATTV(self, url="http://www.wat.tv/images/v70/PlayerLite.swf?videoId=6owmd"):
        printDBG("parseWATTV url[%s]\n" % url)
        # example video: http://www.wat.tv/video/orages-en-dordogne-festival-6xxsn_2exyh_.html
        def getTS():
            #ts = math.floor( float(ts) / 1000 )
            url = "http://www.wat.tv/servertime?%d" % int(random() * 0x3D0900)
            sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER})
            ts = int(data.split('|')[0])
            return int2base(int(ts), 36)

        def computeToken(urlSuffixe, ts):
            tHex = int2base(int(ts, 36), 16)
            while len(tHex) < 8:
                tHex = "0" + tHex
            constToken = "9b673b13fa4682ed14c3cfa5af5310274b514c4133e9b3a81e6e3aba009l2564"
            hashAlg = MD5() 
            return hexlify( hashAlg(constToken + urlSuffixe + tHex) ) + "/" + tHex

        movieUrls = []
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
        HTTP_HEADER['Referer'] = url
        match = re.search("videoId=([^']+?)'", url + "'")

        sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER})
        if sts:
            real_id = re.search(r'xtpage = ".*-(.*?)";', data)
            if real_id:
                real_id = real_id.group(1)
                movieUrls.append({'name': 'wat.tv: Mobile', 'url':'http://wat.tv/get/android5/%s.mp4' % real_id})    
            if not match:
                match = re.search('videoId=([^"]+?)"', data)
        
        for item in ["webhd", "web"]:
            try:
                vidId = int(match.group(1), 36)
                url_0 = "/%s/%d" % (item, vidId)
                url_1 = computeToken(url_0, getTS())
                url_2 =  url_0 + "?token=" + url_1 + "&"
                url   = "http://www.wat.tv/get" + url_2 + "domain=www.wat.tv&refererURL=www.wat.tv&revision=04.00.388%0A&synd=0&helios=1&context=playerWat&pub=5&country=FR&sitepage=WAT%2Ftv%2Fu%2Fvideo&lieu=wat&playerContext=CONTEXT_WAT&getURL=1&version=WIN%2012,0,0,44"
                printDBG("====================================================: [%s]\n" % url)
                
                sts, url = self.cm.getPage(url, {'header' : HTTP_HEADER})
                if sts:
                    if url.split('?')[0].endswith('.f4m'):
                        url = urlparser.decorateUrl(url, HTTP_HEADER)
                        retTab = getF4MLinksWithMeta(url)
                        movieUrls.extend(retTab)
                    elif 'ism' not in url:
                        movieUrls.append({'name': 'wat.tv: ' + item, 'url':url})
            except:
                printExc()
        movieUrls.reverse()
        return movieUrls
        
        
    def parseTUNEPK(self, url):
        printDBG("parseTUNEPK url[%s]\n" % url)
        # example video: http://tune.pk/video/4203444/top-10-infamous-mass-shootings-in-the-u
        for item in ['vid=', '/video/', '/play/']:
            vid = self.cm.ph.getSearchGroups(url+'&', item+'([0-9]+)[^0-9]')[0]
            if '' != vid: break
        if '' == vid: return []
        url = 'http://embed.tune.pk/play/%s?autoplay=no&ssl=no' % vid
        return self.__parseJWPLAYER_A(url, 'tune.pk')
    
    def parserVIDEOTT(self, url):
        printDBG("parserVIDEOTT url[%r]" % url)
        # based on https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/videott.py
        # example video: http://www.video.tt/video/HRKwm3EhI
        linkList = []
        try:
            mobj = re.match(r'http://(?:www\.)?video\.tt/(?:video/|watch_video\.php\?v=|embed/)(?P<id>[\da-zA-Z]{9})', url)
            video_id = mobj.group('id')
        except:
            printExc()
            return linkList
        url = 'http://www.video.tt/player_control/settings.php?v=%s' % video_id
        sts, data = self.cm.getPage(url)
        if sts:
            try:
                data = json.loads(data)['settings']
                linkList = [
                    {
                        'url': base64.b64decode(res['u'].encode('utf-8')),
                        'name': res['l'].encode('utf-8'),
                    } for res in data['res'] if res['u']
                ]
            except:
                printExc()
        return linkList
        
    def parserEXASHARECOM(self, url):
        printDBG("parserVODLOCKER url[%r]" % url)
        # example video: http://www.exashare.com/s4o73bc1kd8a
        url =  url.replace('exashare.com', 'openload.info')
        def _findLinks(data):
            return self._findLinks(data, 'exashare.com', m1='setup(', m2=')')
        return self.__parseJWPLAYER_A(url, 'exashare.com', _findLinks)
        
    def parserALLVIDCH(self, url):
        printDBG("parserALLVIDCH url[%r]" % url)
        # example video: http://allvid.ch/embed-fhpd7sk5ac2o-830x500.html
        def _findLinks(data):
            return self._findLinks(data, 'allvid.ch', m1='setup(', m2='image:')
        return self.__parseJWPLAYER_A(url, 'allvid.ch', _findLinks)
        
    def parserVODLOCKER(self, url):
        printDBG("parserVODLOCKER url[%r]" % url)
        # example video: http://vodlocker.com/txemekqfbopy
        return self.__parseJWPLAYER_A(url, 'vodlocker.com')
        
    def parserVSHAREEU(self, url):
        printDBG("parserVSHAREEU url[%r]" % url)
        # example video: http://vshare.eu/mvqdaea0m4z0.htm
        return self.__parseJWPLAYER_A(url, 'vshare.eu')
        
    def parserVIDSPOT(self, url):
        printDBG("parserVIDSPOT url[%r]" % url)
        # example video: http://vidspot.net/2oeqp21cdsee
        return self.__parseJWPLAYER_A(url, 'vidspot.net')
            
    def parserVIDBULL(self, baseUrl):
        printDBG("parserVIDBULL baseUrl[%s]" % baseUrl)
        # example video: http://vidbull.com/zsi9kwq0eqm4.html
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = baseUrl
        
        # we will try three times if they tell us that we wait to short
        tries = 0
        while tries < 3:
            # get embedded video page and save returned cookie
            sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER})
            if not sts: return False
            
            sts, data = self.cm.ph.getDataBeetwenMarkers(data, '<input type="hidden" name="op" value="download2">', '</Form>', True)
            post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
            
            try:
                sleep_time = int(self.cm.ph.getSearchGroups(data, '>([0-9])</span> seconds<')[0]) 
                time.sleep(sleep_time)
            except:
                printExc()
            if {} == post_data:
                post_data = None
            sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER}, post_data)
            if not sts: return False
            if 'Skipped countdown' in data:
                tries += tries
                continue # we will try three times if they tell us that we wait to short
            # get JS player script code from confirmation page
            sts, tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div id="player_code"', '</div>', True)
            sts, tmp = self.cm.ph.getDataBeetwenMarkers(tmp, ">eval(", '</script>')
            if sts:
                # unpack and decode params from JS player script code
                data = unpackJSPlayerParams(tmp, VIDUPME_decryptPlayerParams)
                printDBG(data)
                # get direct link to file from params
                src = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
                if src.startswith('http'):
                    return src
            # get direct link to file from params
            file = self.cm.ph.getSearchGroups(data, r'''['"]?file['"]?[ ]*:[ ]*['"]([^"^']+)['"],''')[0]
            if '' != file:
                if file.startswith('http'): return src
                else:
                    key = 'YTk0OTM3NmUzN2IzNjlmMTdiYzdkM2M3YTA0YzU3MjE='
                    bkey, knownCipherText = a2b_hex(base64.b64decode(key)), a2b_hex(file)
                    kSize = len(bkey)
                    alg = AES(bkey, keySize=kSize, padding=noPadding())
                    file = alg.decrypt(knownCipherText).split('\x00')[0]
                    if file.startswith('http'):
                        return file
            break
        return False
        
    def parserDIVEXPRESS(self, baseUrl):
        printDBG("parserDIVEXPRESS baseUrl[%s]" % baseUrl)
        # example video: http://divxpress.com/h87ygyutusp6/The.Last.Ship.S01E04.HDTV.x264-LOL_Napisy_PL.AVI.html
        return self.parserVIDBULL(baseUrl)
        
    def parserPROMPTFILE(self, baseUrl):
        printDBG("parserPROMPTFILE baseUrl[%s]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if sts:
            COOKIE_FILE = GetCookieDir('promptfile.cookie')
            HTTP_HEADER = dict(self.HTTP_HEADER) 
            HTTP_HEADER['Referer'] = baseUrl
            if 'Continue to File' in data:
                sts, data = self.cm.ph.getDataBeetwenMarkers(data, '<form method="post" action="">', '</form>', False, False)
                post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
                params = {'header' : HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True, 'load_cookie':False}
                sts, data = self.cm.getPage(baseUrl, params, post_data)
                if not sts:
                    return False
            data = self.cm.ph.getSearchGroups(data, """url: ["'](http[^"']+?)["'],""")[0]
            if '' != data:
                return data
        return False
        
    def parserPLAYEREPLAY(self, baseUrl):
        printDBG("parserPLAYEREPLAY baseUrl[%s]" % baseUrl)
        videoIDmarker = "((?:[0-9]){5}\.(?:[A-Za-z0-9]){28})"
        data = self.cm.ph.getSearchGroups(baseUrl, videoIDmarker)[0]
        if '' == data: 
            sts, data = self.cm.getPage(baseUrl)
            if sts:
                data = self.cm.ph.getSearchGroups(data, videoIDmarker)[0]
            else:
                data = ''
        if '' != data: 
            HTTP_HEADER = dict(self.HTTP_HEADER) 
            HTTP_HEADER['Referer'] = baseUrl
            post_data = {'r':'["tVL0gjqo5",["preview/flv_image",{"uid":"%s"}],["preview/flv_link",{"uid":"%s"}]]' % (data, data)}
            params = {'header' : HTTP_HEADER}
            sts, data = self.cm.getPage('http://api.letitbit.net', params, post_data)
            if sts:
                data = self.cm.ph.getSearchGroups(data, '"link":[ ]*"(http[^"]+?)"')[0].replace('\/', '/')
                if '' != data:
                    return strwithmeta(data, {'Range':'0', 'iptv_buffering':'required'})
        return False
        
    def parserVIDEOWOODTV(self, baseUrl):
        printDBG("parserVIDEOWOODTV baseUrl[%s]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        if 'embed' not in baseUrl:
            video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9]{4})/')[0]
            url = 'http://videowood.tv/embed/{0}'.format(video_id)
        else:
            url = baseUrl 
        params = {'header' : HTTP_HEADER}
        sts, data = self.cm.getPage(url, params)
        if sts:
            data = self.cm.ph.getSearchGroups(data, """["']*file["']*:[ ]*["'](http[^"']+?)["']""")[0]
            if '' != data:
                return data
        return False
        
    def parserMOVRELLCOM(self, baseUrl):
        printDBG("parserMOVRELLCOM baseUrl[%s]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if sts:
            HTTP_HEADER = dict(self.HTTP_HEADER) 
            HTTP_HEADER['Referer'] = baseUrl
            if 'Watch as Free User' in data:
                sts, data = self.cm.ph.getDataBeetwenMarkers(data, '<form', '</form>', False, False)
                post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
                params = {'header' : HTTP_HEADER}
                sts, data = self.cm.getPage(baseUrl, params, post_data)
                if not sts:
                    return False
            # get JS player script code from confirmation page
            sts, tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div id="player_code"', '</div>', True)
            sts, tmp = self.cm.ph.getDataBeetwenMarkers(tmp, ">eval(", '</script>')
            if sts:
                # unpack and decode params from JS player script code
                data = unpackJSPlayerParams(tmp, VIDUPME_decryptPlayerParams)
                printDBG(data)
                # get direct link to file from params
                src = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
                if src.startswith('http'):
                    return src
        return False
        
    def parserVIDFILENET(self, baseUrl):
        printDBG("parserVIDFILENET baseUrl[%s]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        params = {'header' : HTTP_HEADER}
        sts, data = self.cm.getPage(baseUrl, params)
        if sts:
            data = self.cm.ph.getSearchGroups(data, """["']*file["']*:[ ]*["'](http[^"']+?)["']""")[0]
            if '' != data:
                return data
        return False
        
    def parserMP4UPLOAD(self, baseUrl):
        printDBG("parserMP4UPLOAD baseUrl[%s]" % baseUrl)
        videoUrls = []
        sts, data = self.cm.getPage(baseUrl)
        #printDBG(data)
        if sts:
            data = CParsingHelper.getDataBeetwenMarkers(data, "'modes':", ']', False)[1]
            data = re.compile("""['"]file['"]: ['"]([^'^"]+?)['"]""").findall(data)
            if 1 < len(data) and data[1].startswith('http'): videoUrls.append( {'name': 'mp4upload.com: html5',    'url':data[1] } )
            if 0 < len(data) and data[0].startswith('http'): videoUrls.append( {'name': 'mp4upload.com: download', 'url':data[0] } )
        return videoUrls
        
    def parserYUKONS(self, baseUrl):
        printDBG("parserYUKONS url[%s]" % baseUrl)
        #http://yukons.net/watch/willstream002?Referer=wp.pl
        def _resolveChannelID(channel):
            def _decToHex(a):
                b = hex(a)[2:]
                if 1 == len(b):
                    return '0'+b
                else:
                    return b
            
            def _resolve(a):
                b = ''
                for i in range(len(a)):
                    b += _decToHex(ord(a[i]))
                return b
                
            return _resolve( _resolve(channel) )
        
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        shortChannelId = baseUrl.split('?')[0].split('/')[-1]
        Referer = baseUrl.meta.get('Referer', '')
        
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Referer' : Referer}
        COOKIE_FILE = GetCookieDir('yukonsnet.cookie')
        params = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}

        longChannelId = _resolveChannelID(shortChannelId)
        url1 = 'http://yukons.net/yaem/' + longChannelId
        sts, data = self.cm.getPage(url1, params)
        if sts:
            kunja = re.search("'([^']+?)';", data).group(1)
            url2 = 'http://yukons.net/embed/' + longChannelId + '/' + kunja + '/680/400'
            params.update({'save_cookie' : False, 'load_cookie' : True}) 
            sts, data = self.cm.getPage(url2, params)
            if sts:
                data = CParsingHelper.getDataBeetwenMarkers(data, "eval(", '</script>', False)[1]
                data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams, 0)
                printDBG(data)
                id = CParsingHelper.getDataBeetwenMarkers(data, "id=", '&', False)[1]
                pid = CParsingHelper.getDataBeetwenMarkers(data, "pid=", '&', False)[1]
                data = CParsingHelper.getDataBeetwenMarkers(data, "eval(", '</script>', False)[1]
                sts, data = self.cm.getPage("http://yukons.net/srvload/"+id, params)
                printDBG(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> [%s]" % data)
                if sts:
                    ip = data[4:].strip()
                    url = 'rtmp://%s:443/kuyo playpath=%s?id=%s&pid=%s  swfVfy=http://yukons.net/yplay2.swf pageUrl=%s conn=S:OK live=1' % (ip, shortChannelId, id, pid, url2)
                    return url
        return False
        
    def parserUSTREAMTV(self, linkUrl):
        printDBG("parserUSTREAMTV linkUrl[%s]" % linkUrl)
        #http://www.ustream.tv/channel/nasa-educational
        linksTab = []
        live = True
        # get PC streams
        while True:
            channelID = self.cm.ph.getSearchGroups(linkUrl+'|', "cid=([0-9]+?)[^0-9]")[0]
            if '' == channelID:            
                sts, data = self.cm.getPage(linkUrl)
                if not sts: break
                channelID = self.cm.ph.getSearchGroups(data, 'data-content-id="([0-9]+?)"')[0]
                if '' == channelID: channelID = self.cm.ph.getSearchGroups(data, 'ustream.vars.cId=([0-9]+?)[^0-9]')[0]

            if '' == channelID: break
            #in linkUrl and 'ustream.vars.isLive=true' not in data and '/live/' not in linkUrl
            if '/recorded/' in linkUrl:
                videoUrl = 'https://www.ustream.tv/recorded/' + channelID
                live = False
            else:
                videoUrl = 'https://www.ustream.tv/embed/' + channelID
                live = True
            
            baseWgetCmd = DMHelper.getBaseWgetCmd({})
            cmd = DMHelper.GET_F4M_PATH() + (" '%s'" % baseWgetCmd) + (' "%s"' % videoUrl) + ' 2>&1 > /dev/null'
            
            printDBG("parserUSTREAMTV cmd[%s" % cmd)
            data = iptv_execute()( cmd )
            printDBG(data)
            if not data['sts'] or 0 != data['code']:
                break
            try:
                data = json.loads(data['data'])
                for item in data['stream_info_list']:
                    if not live and item['chunk_name'].startswith('http'):
                        url = urlparser.decorateUrl(item['chunk_name'].encode('utf-8'))
                        linksTab.append({'name':'ustream.tv recorded', 'url': url})
                    else:
                        name     = 'ustream.tv ' + item['stream_name'].encode('utf-8')
                        chankUrl = (item['prov_url'] + item['chunk_name']).encode('utf-8')
                        url      = urlparser.decorateUrl(videoUrl, {'iptv_livestream': True, 'iptv_proto':'f4m', 'iptv_chank_url':chankUrl})
                        linksTab.append({'name':name, 'url':url})
            except:
                printExc()
            break
        return linksTab
        # get mobile streams
        if live:
            playlist_url = "http://iphone-streaming.ustream.tv/uhls/%s/streams/live/iphone/playlist.m3u8" % channelID
            if 0 == len(linksTab): attempts = 5
            else:  attempts = 1                
            while attempts:
                try:
                    retTab = getDirectM3U8Playlist(playlist_url)
                    if len(retTab):
                        for item in retTab:
                            name = ('ustream.tv %s' % item.get('heigth', 0)) + '_mobile'
                            url = urlparser.decorateUrl(item['url'], {'iptv_livestream': True})
                            linksTab.append({'name':name, 'url':url})
                        break
                except:
                    printExc()
                attempts -= 1
                time.sleep(3)
        return linksTab
        
    def parserPRIVATESTREAM(self, linkUrl):
        printDBG("parserPRIVATESTREAM linkUrl[%s]" % linkUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        videoUrl = strwithmeta(linkUrl)
        if 'Referer' in videoUrl.meta:
            HTTP_HEADER['Referer'] = videoUrl.meta['Referer']

        if videoUrl.split('?')[0].endswith('.js'):
            sts, data = self.cm.getPage(videoUrl, {'header': HTTP_HEADER})
            if not sts: return False
            printDBG(data)
            tr = 0
            while tr < 3:
                tr += 1
                videoUrl = self.cm.ph.getSearchGroups(data, '"(http://privatestream.tv/player?[^"]+?)"')[0]
                if "" != videoUrl: break
                time.sleep(1)
        sts, data = self.cm.getPage(videoUrl, {'header': HTTP_HEADER})
        printDBG(data)
        if sts:
            try:
                a = int(self.cm.ph.getSearchGroups(data, 'var a = ([0-9]+?);')[0])
                b = int(self.cm.ph.getSearchGroups(data, 'var b = ([0-9]+?);')[0])
                c = int(self.cm.ph.getSearchGroups(data, 'var c = ([0-9]+?);')[0])
                d = int(self.cm.ph.getSearchGroups(data, 'var d = ([0-9]+?);')[0])
                f = int(self.cm.ph.getSearchGroups(data, 'var f = ([0-9]+?);')[0])
                v_part = self.cm.ph.getSearchGroups(data, "var v_part = '([^']+?)'")[0]
                
                url = ('rtmp://%d.%d.%d.%d' % (a/f, b/f, c/f, d/f) ) + v_part
                url += ' swfUrl=http://privatestream.tv/js/jwplayer.flash.swf pageUrl=%s' % (videoUrl)
                return url
            except:
                printExc()
        return False
        
    def parserABCASTBIZ(self, linkUrl):
        printDBG("parserABCASTBIZ linkUrl[%s]" % linkUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        videoUrl = strwithmeta(linkUrl)
        if 'Referer' in videoUrl.meta:
            HTTP_HEADER['Referer'] = videoUrl.meta['Referer']
        sts, data = self.cm.getPage(linkUrl, {'header': HTTP_HEADER})
        if not sts: return False
            
        file     = self.cm.ph.getSearchGroups(data, 'file=([^&]+?)&')[0]
        if file.endswith(".flv"): file = file[0:-4]
        streamer = self.cm.ph.getSearchGroups(data, 'streamer=([^&]+?)&')[0]
        if '' != file:
            url    = "rtmpe://live.abcast.biz/redirect"
            player = "http://abcast.biz/ab.swf"
            url = streamer
            player = "http://abcast.net/player.swf"
            url += ' playpath=%s swfUrl=%s pageUrl=%s' % (file, player, linkUrl)
            printDBG(url)
            return url
        return False
        
    def parserOPENLIVEORG(self, linkUrl):
        printDBG("parserOPENLIVEORG linkUrl[%s]" % linkUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        videoUrl = strwithmeta(linkUrl)
        if 'Referer' in videoUrl.meta:
            HTTP_HEADER['Referer'] = videoUrl.meta['Referer']
        sts, data = self.cm.getPage(linkUrl, {'header': HTTP_HEADER})
        if not sts: return False
            
        file     = self.cm.ph.getSearchGroups(data, 'file=([^&]+?)&')[0]
        if file.endswith(".flv"): file = file[0:-4]
        streamer = self.cm.ph.getSearchGroups(data, 'streamer=([^&]+?)&')[0]
        if '' != file:
            url = streamer
            player = "http://openlive.org/player.swf"
            url += ' playpath=%s swfUrl=%s pageUrl=%s' % (file, player, linkUrl)
            printDBG(url)
            return url
        return False
        
    def parserGOODCASTCO(self, linkUrl):
        printDBG("parserGOODCASTCO linkUrl[%s]" % linkUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        videoUrl = strwithmeta(linkUrl)
        HTTP_HEADER['Referer'] = videoUrl.meta.get('Referer', videoUrl)
        sts, data = self.cm.getPage(videoUrl, {'header': HTTP_HEADER})
        if not sts: return False
        url  = self.cm.ph.getSearchGroups(data, 'streamer=([^&]+?)&')[0]
        file = self.cm.ph.getSearchGroups(data, 'file=([0-9]+?)&')[0]
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=http://abcast.biz/ab.swf pageUrl=%s token=Fo5_n0w?U.rA6l3-70w47ch' % (file, linkUrl)
            return url
        return False
        
    def paserLIVEALLTV(self, linkUrl):
        printDBG("paserLIVEALLTV linkUrl[%s]" % linkUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        videoUrl = strwithmeta(linkUrl)
        HTTP_HEADER['Referer'] = videoUrl.meta.get('Referer', videoUrl)
        sts, data = self.cm.getPage(videoUrl, {'header': HTTP_HEADER})
        if not sts: return False
        
        a = int(self.cm.ph.getSearchGroups(data, 'var a = ([0-9]+?);')[0])
        b = int(self.cm.ph.getSearchGroups(data, 'var b = ([0-9]+?);')[0])
        c = int(self.cm.ph.getSearchGroups(data, 'var c = ([0-9]+?);')[0])
        d = int(self.cm.ph.getSearchGroups(data, 'var d = ([0-9]+?);')[0])
        f = int(self.cm.ph.getSearchGroups(data, 'var f = ([0-9]+?);')[0])
        v_part = self.cm.ph.getSearchGroups(data, "var v_part = '([^']+?)'")[0]
        
        url = ('rtmp://%d.%d.%d.%d' % (a/f, b/f, c/f, d/f) ) + v_part
        url += ' swfUrl=http://wds.liveall.tv/jwplayer.flash.swf pageUrl=%s' % (linkUrl)
        return url
        
    def paserP2PCASTTV(self, linkUrl):
        printDBG("paserP2PCASTTV linkUrl[%s]" % linkUrl)
        HTTP_HEADER = {}
        videoUrl = strwithmeta(linkUrl)
        HTTP_HEADER['Referer'] = videoUrl.meta.get('Referer', videoUrl)
        HTTP_HEADER['User-Agent'] = "Mozilla/5.0"
        sts, data = self.cm.getPage(videoUrl, {'header': HTTP_HEADER})
        if not sts: return False
        url = self.cm.ph.getSearchGroups(data, 'curl[^"]*?=[^"]*?"([^"]+?)"')[0]
        url = base64.b64decode(url)
        return urlparser.decorateUrl(url, {'Referer':'http://cdn.p2pcast.tv/jwplayer.flash.swf', "User-Agent": HTTP_HEADER['User-Agent']})
    
    def parserGOOGLE(self, linkUrl):
        printDBG("parserGOOGLE linkUrl[%s]" % linkUrl)
        
        videoTab = []
        sts, data = self.cm.getPage(linkUrl)
        if sts: 
            data = self.cm.ph.getSearchGroups(data, '"fmt_stream_map"[:,]"([^"]+?)"')[0]
            data = data.split(',')
            for item in data:
                item = item.split('|')
                if item[0] in YoutubeIE._video_formats_map['mp4']:
                    videoTab.append({'name':'google.com: %s' % YoutubeIE._video_dimensions[item[0]].split('x')[0] + 'p', 'url':unicode_escape(item[1])})
        return videoTab[::-1]
        
    def parserPICASAWEB(self, baseUrl):
        printDBG("parserPICASAWEB baseUrl[%s]" % baseUrl)
        videoTab = []
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return videoTab
        data = re.compile('(\{"url"[^}]+?\})').findall(data)
        printDBG(data)
        for item in data:
            try:
                item = byteify(json.loads(item))
                if 'video' in item.get('type', ''):
                    videoTab.append({'name':'%sx%s' % (item.get('width', ''), item.get('height', '')), 'url':item['url']})
            except:
                printExc()
        return videoTab
        
    def parserMYVIRU(self, linkUrl):
        printDBG("parserMYVIRU linkUrl[%s]" % linkUrl)
        COOKIE_FILE = GetCookieDir('myviru.cookie')
        params  = {'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        videoTab = []
        if '/player/flash/' in linkUrl:
            videoId = linkUrl.split('/')[-1]
            sts, response = self.cm.getPage(linkUrl, {'return_data':False})
            if not sts: return videoTab
            preloaderUrl = response.geturl()
            response.close()
            flashApiUrl = "http://myvi.ru/player/api/video/getFlash/%s?ap=1&referer&sig&url=%s" % (videoId, urllib.quote(preloaderUrl))
            sts, data = self.cm.getPage(flashApiUrl)
            if not sts: return videoTab
            data = data.replace('\\', '')
            data = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
            if not data.startswith("//"): return videoTab
            linkUrl = "http:" + data
        if '/embed/html/' in linkUrl: 
            sts, data = self.cm.getPage(linkUrl)
            if not sts: return videoTab
            data = self.cm.ph.getSearchGroups(data, """dataUrl[^'^"]*?:[^'^"]*?['"]([^'^"]+?)['"]""")[0]
            if data.startswith("//"): linkUrl = "http:" + data
            elif data.startswith("/"): linkUrl = "http://myvi.ru" + data
            elif data.startswith("http"): linkUrl = data
            else: return videoTab 
            sts, data = self.cm.getPage(linkUrl, params)
            if not sts: return videoTab
            try:
                # get cookie data
                universalUserID = self.cm.getCookieItem(COOKIE_FILE,'UniversalUserID')
                data = json.loads(data)
                for item in data['sprutoData']['playlist']:
                    url = item['video'][0]['url'].encode('utf-8')
                    if url.startswith('http'):
                        videoTab.append({'name': 'myvi.ru: %s' % item['duration'], 'url':strwithmeta(url, {'Cookie':'UniversalUserID=%s; vp=0.33' % universalUserID})})
            except: 
                printExc()
        return videoTab
        
    def parserARCHIVEORG(self, linkUrl):
        printDBG("parserARCHIVEORG linkUrl[%s]" % linkUrl)
        videoTab = []
        sts, data = self.cm.getPage(linkUrl)
        if sts: 
            data = self.cm.ph.getSearchGroups(data, '"sources":\[([^]]+?)]')[0]
            data = '[%s]' % data
            try:
                data = json.loads(data)
                for item in data:
                    if 'mp4' == item['type']:
                        videoTab.append({'name':'archive.org: ' + item['label'].encode('utf-8'), 'url':'https://archive.org' + item['file'].encode('utf-8')})
            except:
                printExc()
        return videoTab
        
    def parserSAWLIVETV(self, baseUrl):
        printDBG("parserSAWLIVETV linkUrl[%s]" % baseUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', baseUrl)
        #HTTP_HEADER['Referer'] = Referer
        
        COOKIE_FILE = GetCookieDir('sawlive.tv')
        params = {'header' : HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True, 'load_cookie':True}
        
        stdWay = False
        if 1:
            sts, data = self.cm.getPage(baseUrl, {'header': HTTP_HEADER})
            if not sts: return False
            
            if 'eval' in data:
                data  = data.strip()
                data = data[data.rfind('}(')+2:-2]
                
                data = unpackJS(data, SAWLIVETV_decryptPlayerParams)
                printDBG(">>>>>>>>>>>>>>>>>>>" + data)
                
                def jal(a):
                    b = ''
                    for c in a:
                        b += JS_toString(ord(c), 16)
                    return b
                
                linkUrl = self.cm.ph.getSearchGroups(data, '''src="([^"']+?)["']''')[0] + '/' + jal(urlparser().getHostName(Referer))
            else:
                stdWay = True
        if stdWay:
            params['header']['Referer'] = Referer
            sts, data = self.cm.getPage(baseUrl, params)
            if not sts: return False
            
            vars = dict( re.compile("var ([^=]+?)='([^']+?)';").findall(data) )
            data = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
            
            def fakeJSExec(dat):
                dat = dat.group(1)
                if dat.startswith('unescape'):
                    dat = self.cm.ph.getSearchGroups(dat, '\(([^)]+?)\)')[0]
                    if "'" == dat[0]:
                        dat = dat[1:-1]
                    else:
                        dat = vars[dat]
                    printDBG('dat: ' + dat)
                    return dat.replace('%', '\\u00').decode('unicode-escape').encode("utf-8")
                else:
                    return vars[dat]
            linkUrl = re.sub("'\+([^+]+?)\+'", fakeJSExec, data)
        
        sts, data = self.cm.getPage(linkUrl, params)
        if not sts: return False
        swfUrl = self.cm.ph.getSearchGroups(data, "'(http[^']+?swf)'")[0]
        url    = self.cm.ph.getSearchGroups(data, "streamer'[^']+?'(rtmp[^']+?)'")[0]
        file   = self.cm.ph.getSearchGroups(data, "file'[^']+?'([^']+?)'")[0]
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s pageUrl=%s ' % (file, swfUrl, linkUrl)
            #printDBG(url)
            return url
        return False
        
    def parserSHIDURLIVECOM(self, baseUrl):
        printDBG("parserSHIDURLIVECOM linkUrl[%s]" % baseUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', baseUrl)
        HTTP_HEADER['Referer'] = Referer
        
        sts, data = self.cm.getPage(baseUrl, {'header': HTTP_HEADER})
        if not sts: return False
        linkUrl = self.cm.ph.getSearchGroups(data, 'src="(http[^"]+?)"')[0].strip()
        sts, data = self.cm.getPage(linkUrl, {'header': HTTP_HEADER})
        if not sts: return False
        data = self.cm.ph.getDataBeetwenMarkers(data, 'new SWFObject', '</script>', True)[1]
        printDBG(data)
        dataTab = data.split(';')
        data = ''
        for line in dataTab: 
            if not line.strip().startswith('//'): 
                data += line+';'
        swfUrl = self.cm.ph.getSearchGroups(data, "'(http[^']+?swf)'")[0]
        url    = self.cm.ph.getSearchGroups(data, "streamer'[^']+?'(rtmp[^']+?)'")[0]#.replace('rtmp://', 'rtmpe://')
        file   = urllib.unquote( self.cm.ph.getSearchGroups(data, "file'[^']+?'([^']+?)'")[0] )
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s pageUrl=%s live=1 ' % (file, swfUrl, linkUrl)
            printDBG(url)
            return url
        return False
        
    def parserCASTALBATV(self, baseUrl):
        printDBG("parserCASTALBATV baseUrl[%s]" % baseUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', baseUrl)
        HTTP_HEADER['Referer'] = Referer
        
        sts, data = self.cm.getPage(baseUrl, {'header': HTTP_HEADER})
        if not sts: return False
        def _getParam(name):
            return self.cm.ph.getDataBeetwenMarkers(data, "'%s':" % name, ',', False)[1].strip() + ", '{0}'".format(name)
            #self.cm.ph.getSearchGroups(data, """['"]%s['"][^'^"]+?['"]([^'^"]+?)['"]""" % name)[0] 
        def _getParamVal(value, name):
            return value
            
        data = self.cm.ph.getDataBeetwenMarkers(data, '<script type="text/javascript">', '</script>', False)[1]
        vars = dict( re.compile('''var ([^=]+?)=[^']*?'([^']+?)['];''').findall(data) )
        printDBG("===================================")
        printDBG(vars)
        printDBG("===================================")
        addCode = ''
        for item in vars:
            addCode += '%s="%s"\n' % (item, vars[item])
            
        swfUrl = unpackJS(_getParam('flashplayer'), _getParamVal, addCode)
        url    = unpackJS(_getParam('streamer'), _getParamVal, addCode)
        file   = unpackJS(_getParam('file'), _getParamVal, addCode)
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s pageUrl=%s live=1 ' % (file, swfUrl, baseUrl)
            printDBG(url)
            return url
        return False
        
    def parserFXSTREAMBIZ(self, baseUrl):
        printDBG("parserFXSTREAMBIZ baseUrl[%s]" % baseUrl)
        HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER['Referer'] = Referer
        sts, data = self.cm.getPage(baseUrl, {'header': HTTP_HEADER})
        if not sts: return False
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """['"]*%s['"]*[^'^"]+?['"]([^'^"]+?)['"]""" % name)[0]
        file   = _getParam('file')
        printDBG(data)
        return False
        
    def parserWEBCAMERAPL(self, baseUrl):
        printDBG("parserWEBCAMERAPL baseUrl[%s]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if sts:
            data = self.cm.ph.getSearchGroups(data, """<meta itemprop="embedURL" content=['"]([^'^"]+?)['"]""")[0]
            data = data.split('&')
            if 2 < len(data) and data[0].startswith('http') and data[1].startswith('streamer=') and data[2].startswith('file='):
                swfUrl = data[0]
                url    = urllib.unquote(data[1][len('streamer='):])
                file   = urllib.unquote(data[2][len('file='):])
                if '' != file and '' != url:
                    url += ' playpath=%s swfUrl=%s pageUrl=%s live=1 ' % (file, swfUrl, baseUrl)
                    return url
        else:
            return False
        
    def parserFLASHXTV(self, baseUrl):
        printDBG("parserFLASHXTV baseUrl[%s]" % baseUrl)
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = baseUrl
        SWF_URL = 'http://static.flashx.tv/player6/jwplayer.flash.swf'
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        
        def _first_of_each(*sequences):
            return (next((x for x in sequence if x), '') for sequence in sequences)
        
        def _url_path_join(*parts):
            """Normalize url parts and join them with a slash."""
            schemes, netlocs, paths, queries, fragments = zip(*(urlsplit(part) for part in parts))
            scheme, netloc, query, fragment = _first_of_each(schemes, netlocs, queries, fragments)
            path = '/'.join(x.strip('/') for x in paths if x)
            return urlunsplit((scheme, netloc, path, query, fragment))
        
        url = baseUrl
        post_data = None
        if 'Proceed to video' in data:
            sts, data = self.cm.ph.getDataBeetwenMarkers(data, '<Form method="POST"', '</Form>', True)
            action = self.cm.ph.getSearchGroups(data, "action='([^']+?)'")[0]
            post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
            
            try:
                sleep_time = int(self.cm.ph.getSearchGroups(data, '>([0-9])</span> seconds<')[0]) 
                time.sleep(sleep_time)
            except:
                printExc()
            if {} == post_data:
                post_data = None
            if action.startswith('/'):
                url = _url_path_join(url[:url.rfind('/')+1], action[1:])
            else: url = action
            sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER}, post_data)
            if not sts: return False
        
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, ">eval(", '</script>')
        if not sts: return False
        data = unpackJSPlayerParams(data, VIDUPME_decryptPlayerParams)
        data = self.cm.ph.getSearchGroups(data, """["']*file["']*[ ]*?:[ ]*?["']([^"^']+?)['"]""")[0]
        if data.startswith('http'):
            if data.split('?')[0].endswith('.smil'):
                # get stream link
                sts, data = self.cm.getPage(data)
                if sts:
                    base = self.cm.ph.getSearchGroups(data, 'base="([^"]+?)"')[0]
                    src = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
                    #if ':' in src:
                    #    src = src.split(':')[1]   
                    if base.startswith('rtmp'):
                        return base + '/' + src + ' swfUrl=%s live=1 pageUrl=%s' % (SWF_URL, baseUrl)
            else:
                return data
        return False
        
    def parserMYVIDEODE(self, baseUrl):
        printDBG("parserMYVIDEODE baseUrl[%s]" % baseUrl)
        HTTP_HEADER = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0",
                       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Language': 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4',
                       'Referer': baseUrl}
        baseUrl = strwithmeta(baseUrl)
        ################################################################################
        # Implementation based on:
        # https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/myvideo.py
        ################################################################################
        swfUrl = 'http://is5.myvideo.de/de/player/mingR14b/ming.swf'
        GK = b'WXpnME1EZGhNRGhpTTJNM01XVmhOREU0WldNNVpHTTJOakptTW1FMU5tVTBNR05pWkRaa05XRXhNVFJoWVRVd1ptSXhaVEV3TnpsbA0KTVRkbU1tSTRNdz09'
        requestParams = {'http_proxy':baseUrl.meta.get('http_proxy', '')}
        requestParams['header'] = HTTP_HEADER
        baseUrl = strwithmeta(baseUrl+'/')
        
        videoTab = []
        
        # Original Code from: https://github.com/dersphere/plugin.video.myvideo_de.git
        # Released into the Public Domain by Tristan Fischer on 2013-05-19
        # https://github.com/rg3/youtube-dl/pull/842
        def __rc4crypt(data, key):
            x = 0
            box = list(range(256))
            for i in list(range(256)):
                x = (x + box[i] + ord(key[i % len(key)])) % 256
                box[i], box[x] = box[x], box[i]
            x = 0
            y = 0
            out = ''
            for char in data:
                x = (x + 1) % 256
                y = (y + box[x]) % 256
                box[x], box[y] = box[y], box[x]
                out += chr(ord(char) ^ box[(box[x] + box[y]) % 256])
            return out
        def __md5(s):
            return md5(s).hexdigest().encode()
            
        def _getRtmpLink(r, tcUrl, playpath, swfUrl, page):
            if '?token=' in r:
                tmp = r.split('?token=')
                r = tmp[0]
                token = tmp[1]
            else:
                token = ''
            if '' != tcUrl:    r += ' tcUrl='    + tcUrl
            if '' != playpath: r += ' playpath=' + playpath
            if '' != swfUrl:   r += ' swfUrl='   + swfUrl
            if '' != page:     r += ' pageUrl='  + page
            if '' != token:     r += ' token='    + token
            return urlparser.decorateUrl(r, {'iptv_livestream':False})
        # Get video ID
        video_id = baseUrl
        if '-m-' in video_id:
            video_id = self.cm.ph.getSearchGroups(video_id, """-m-([0-9]+?)[^0-9]""")[0]
        else:
            video_id = self.cm.ph.getSearchGroups(video_id, """/(?:[^/]+/)?watch/([0-9]+)/""")[0]
        if '' != video_id:
            try:
                xmldata_url = "http://www.myvideo.de/dynamic/get_player_video_xml.php?ID=%s&flash_playertype=D&autorun=yes" % video_id
                sts, enc_data = self.cm.getPage(xmldata_url, requestParams)
                enc_data = enc_data.split('=')[1]
                enc_data_b = unhexlify(enc_data)
                sk = __md5(base64.b64decode(base64.b64decode(GK)) + __md5(str(video_id).encode('utf-8')))
                dec_data = __rc4crypt(enc_data_b, sk)
                #printDBG("============================================================================")
                #printDBG(dec_data)
                #printDBG("============================================================================")

                # extracting infos
                connectionurl = urllib.unquote( self.cm.ph.getSearchGroups(dec_data, "connectionurl='([^']*?)'")[0] )
                source        = urllib.unquote( self.cm.ph.getSearchGroups(dec_data, "source='([^']*?)'")[0] )
                path          = urllib.unquote( self.cm.ph.getSearchGroups(dec_data, "path='([^']*?)'")[0] )
                
                if connectionurl.startswith('rtmp'):
                    connectionurl = connectionurl.replace('rtmpe://', 'rtmp://')
                
                    rtmpUrl = urlparser.decorateUrl(connectionurl)
                    if rtmpUrl.meta.get('iptv_proto', '') == 'rtmp':
                        if not source.endswith('f4m') :
                            playpath = source.split('.')
                            playpath = '%s:%s' % (playpath[1], playpath[0]) 
                        videoUrl = _getRtmpLink(rtmpUrl, rtmpUrl, playpath, swfUrl, baseUrl)
                        videoTab.append({'name':'myvideo.de: RTMP', 'url':videoUrl})
                else:
                    videoTab.append({'name':'myvideo.de: HTTP', 'url':path+source})
            except:
                printExc()
                
        return videoTab
        
    def parserVIDZITV(self, baseUrl):
        printDBG("parserVIDZITV baseUrl[%s]" % baseUrl)
        videoTab = []
        if 'embed' not in baseUrl:
            vid = CParsingHelper.getDataBeetwenMarkers(baseUrl, '.tv/', '.html', False)[1]
            baseUrl = 'http://vidzi.tv/embed-%s-682x500.html' % vid
        sts, data = self.cm.getPage(baseUrl)
        if sts:
            data = CParsingHelper.getDataBeetwenMarkers(data, 'sources: [', ']', False)[1]
            data = re.findall('file: "([^"]+?)"', data)
            for item in data:
                if item.split('?')[0].endswith('m3u8'):
                    tmp = getDirectM3U8Playlist(item)
                    videoTab.extend(tmp)
                else:
                    videoTab.insert(0, {'name':'vidzi.tv mp4', 'url':item})
        return videoTab
        
    def parserTVP(self, baseUrl):
        printDBG("parserTVP baseUrl[%s]" % baseUrl)
        vidTab = []
        try:
            sts, data = self.cm.getPage(baseUrl)
            if sts:
                
                object_id = self.cm.ph.getSearchGroups(data, 'data-video-id="([0-9]+?)"')[0]
                if '' == object_id:
                    object_id = self.cm.ph.getSearchGroups(data, "object_id:'([0-9]+?)'")[0]
                if '' == object_id:
                    object_id = self.cm.ph.getSearchGroups(data, 'object_id=([0-9]+?)[^0-9]')[0]
                if '' != object_id:
                    from Plugins.Extensions.IPTVPlayer.hosts.hosttvpvod import TvpVod
                    vidTab = TvpVod().getVideoLink(object_id)
        except:
            printExc()
        return vidTab
        
    def parserJUNKYVIDEO(self, baseUrl):
        printDBG("parserJUNKYVIDEO baseUrl[%s]" % baseUrl)
        sts,data = self.cm.getPage(baseUrl)
        if not sts: return []
        url = self.cm.ph.getSearchGroups(data, r'''['"]?file['"]?[ ]*:[ ]*['"]([^"^']+)['"],''')[0]
        if url.startswith('http'):
            return [{'name':'junkyvideo.com', 'url':url}]
        return []
        
    def parserLIVEBVBTOTALDE(self, baseUrl):
        printDBG("parserJUNKYVIDEO baseUrl[%s]" % baseUrl)
        HTTP_HEADER = dict(self.HTTP_HEADER)
        HTTP_HEADER['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
        HTTP_HEADER['Referer'] = baseUrl
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return []
        data = self.cm.ph.getSearchGroups(data, r'<iframe[^>]+?src="([^"]+)"')[0]
        sts, data = self.cm.getPage(data, {'header':HTTP_HEADER})
        if not sts: return []
        data = self.cm.ph.getSearchGroups(data, r'<iframe[^>]+?src="([^"]+)"')[0]
        sts, data = self.cm.getPage(data, {'header':HTTP_HEADER})
        if not sts: return []
        data = self.cm.ph.getSearchGroups(data, r'url: "([^"]+)"')[0]
        sts, data = self.cm.getPage(data, {'header':HTTP_HEADER})
        if not sts: return []
        printDBG(data)
        if 'statustext="success"' not in data: return []
        url   = self.cm.ph.getSearchGroups(data, r'url="([^"]+)"')[0]
        autch = self.cm.ph.getSearchGroups(data, r'auth="([^"]+)"')[0]
        url += '?' + autch
        linksTab = []
        retTab = getDirectM3U8Playlist(url)
        return retTab
        for item in retTab:
            name = ('live.bvbtotal.de %s' % item.get('heigth', 0))
            url = urlparser.decorateUrl(item['url'], {'iptv_livestream': True})
            linksTab.append({'name':name, 'url':url})
        return linksTab
        
    def parserNETTVPLUSCOM(self, baseUrl):
        printDBG("parserNETTVPLUSCOM baseUrl[%s]" % baseUrl)
        HTTP_HEADER = dict(self.HTTP_HEADER)
        HTTP_HEADER['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
        HTTP_HEADER['Referer'] = baseUrl
        if baseUrl.endswith('/source.js'): url = baseUrl
        else: url = baseUrl[:baseUrl.rfind('/')] + '/source.js'
        sts, data = self.cm.getPage(url, {'header':HTTP_HEADER})
        if not sts: return []
        url = self.cm.ph.getSearchGroups(data, '''["'](http[^'^"]+?m3u8[^'^"]*?)["']''')[0]
        if '' != url: return getDirectM3U8Playlist(url, False)
        return []
        
    def parser7CASTNET(self, baseUrl):
        printDBG("parser7CASTNET baseUrl[%s]" % baseUrl)
        baseUrl = urlparser.decorateUrl(baseUrl)
        referer = baseUrl.meta.get('Referer', baseUrl)
        HTTP_HEADER = dict(self.HTTP_HEADER)
        HTTP_HEADER['User-Agent'] = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
        HTTP_HEADER['Referer'] = referer

        url = baseUrl
        if '/embed/' in url:
            sts, data = self.cm.getPage(url, {'header':HTTP_HEADER})
            if not sts: return []
            url = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=["'](http[^'^"]+?)["']''')[0]
        sts, data = self.cm.getPage(url, {'header': HTTP_HEADER})
        if not sts: return False
        data = data[data.rfind('}(')+2:].split('{}))')[0] + '{}'
        data = unpackJS(data, SAWLIVETV_decryptPlayerParams)
        names  = []
        values = {}
        data = re.compile(";([^;]+?)\.push\('(.)'\)").findall(data)
        for item in data:
            if item[0] not in names:
                names.append(item[0])
                values[item[0]] = item[1]
            else: values[item[0]] += item[1]
        if urllib.unquote(values[names[1]]).startswith('rtmp'): names = names[::-1]
        r = urllib.unquote(values[names[0]]) + '/' + urllib.unquote(values[names[1]])
        printDBG("...............................[%s]" % r)
        if r.startswith('rtmp'):
            swfUrl  = "http://7cast.net/jplayer.swf"
            rtmpUrl = r + ' swfUrl=%s pageUrl=%s live=1 ' % (swfUrl, baseUrl)
            return [{'name': 'rtmp://7cast.com/ ', 'url':urlparser.decorateUrl(rtmpUrl, {'iptv_livestream':True})}]
        return []
        
    def parserFACEBOOK(self, baseUrl):
        printDBG("parserFACEBOOK baseUrl[%s]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return []
        
        
        # FROM: https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/facebook.py
        
        BEFORE = '{swf.addParam(param[0], param[1]);});\n'
        AFTER = '.forEach(function(variable) {swf.addVariable(variable[0], variable[1]);});'
        m = self.cm.ph.getDataBeetwenMarkers(data, BEFORE, AFTER, False)[1]
        data = dict(json.loads(m))
        params_raw = urllib.unquote(data['params'])
        params = byteify( json.loads(params_raw) )

        urlsTab = []
        for format_id, f in params['video_data'].items():
            if not f or not isinstance(f, list):
                continue
            for quality in ('sd', 'hd'):
                for src_type in ('src', 'src_no_ratelimit'):
                    src = f[0].get('%s_%s' % (quality, src_type))
                    if src:
                        urlsTab.append({'name':'facebook %s_%s_%s' % (format_id, quality, src_type), 'url':src})
        return urlsTab
        
    def parserCLOUDYVIDEOS(self, baseUrl):
        printDBG("parserCLOUDYVIDEOS baseUrl[%s]" % baseUrl)
        video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '[/-]([A-Za-z0-9]{12})[/-]')[0]
        url = 'http://cloudyvideos.com/{0}'.format(video_id)
        
        linkList = []
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = baseUrl
        sts, data = self.cm.getPage(baseUrl, {'header' : HTTP_HEADER})

        try:
            sleep_time = self.cm.ph.getSearchGroups(data, '>([0-9])</span> seconds<')[0]
            if '' != sleep_time: time.sleep(int(sleep_time))
        except:
            printExc()
        try:
            sts, data = self.cm.ph.getDataBeetwenMarkers(data, 'method="POST"', '</Form>', False, False)
            if not sts: return False
            post_data = dict(re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', data))
            HTTP_HEADER['Referer'] = url
            sts, data = self.cm.getPage(url, {'header' : HTTP_HEADER}, post_data)
            if not sts: return False
            #printDBG(data)
            linkList = self._findLinks(data, serverName='cloudyvideos.com', m1='setup({', m2='</script>')
            for item in linkList:
                item['url'] = urlparser.decorateUrl(item['url']+'?start=0', {'User-Agent':'Mozilla/5.0', 'Referer':'http://cloudyvideos.com/player510/player.swf'})
        except:
            printExc()
        return linkList
        
    def parserFASTVIDEOIN(self, baseUrl):
        printDBG("parserFASTVIDEOIN baseUrl[%s]" % baseUrl)
        #http://fastvideo.in/nr4kzevlbuws
        hostName = urlparser().getHostName(baseUrl)
        return self.__parseJWPLAYER_A(baseUrl, hostName) #'fastvideo.in')
        
    def parserTHEVIDEOME(self, baseUrl):
        printDBG("parserFASTVIDEOIN baseUrl[%s]" % baseUrl)
        #http://thevideo.me/embed-l03p7if0va9a-682x500.html
        if 'embed' in baseUrl: url = baseUrl
        else: url = baseUrl.replace('.me/', '.me/embed-') + '-640x360.html'

        sts, pageData = self.cm.getPage(url)
        if not sts: return False
        
        videoLinks = self._findLinks(pageData, 'thevideo.me', r'''['"]?file['"]?[ ]*:[ ]*['"](http[^"^']+)['"][,} ]''')
        if len(videoLinks): return videoLinks
        
        # get JS player script code from confirmation page
        sts, data = CParsingHelper.getDataBeetwenMarkers(pageData, ">eval(", '</script>', False)
        if sts:
            mark1 = "}("
            idx1 = data.find(mark1)
            if -1 == idx1: return False
            idx1 += len(mark1)
            # unpack and decode params from JS player script code
            pageData = unpackJS(data[idx1:-3], VIDUPME_decryptPlayerParams)
            return self._findLinks(pageData, 'thevideo.me')
        else:
            pageData = CParsingHelper.getDataBeetwenMarkers(pageData, 'setup(', '</script', False)[1]
            videoUrl = self.cm.ph.getSearchGroups(pageData, r"""['"]?file['"]?[ ]*?\:[ ]*?['"]([^"^']+?)['"]""")[0]
            if videoUrl.startswith('http'): return urlparser.decorateUrl(videoUrl)
        return False
            
    def parserXAGEPL(self, baseUrl):
        printDBG("parserXAGEPL baseUrl[%s]" % baseUrl)
        
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        url = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"')[0]
        return urlparser().getVideoLinkExt(url)
        
    def parserCASTAMPCOM(self, baseUrl):
        printDBG("parserCASTAMPCOM baseUrl[%s]" % baseUrl)
        channel = self.cm.ph.getSearchGroups(baseUrl + '&', 'c=([^&]+?)&')[0]

        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = Referer
        
        def _getDomainsa():
            chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz"
            string_length = 8
            randomstring = ''
            for i in range(string_length):
                rnum = randint(0, len(chars)-1)
                randomstring += chars[rnum]
            return randomstring 
        
        linkUrl = 'http://www.castamp.com/embed.php?c={0}&tk={1}&vwidth=710&vheight=460'.format(channel, _getDomainsa())
        
        sts, data = self.cm.getPage(linkUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, '<div id="player">', '</script>', False)
        if not sts: return False
        
        data = re.sub("<!--[\s\S]*?-->", "", data)
        data = re.sub("/\*[\s\S]*?\*/", "", data)
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """['"]%s['"][^'^"]+?['"]([^'^"]+?)['"]""" % name)[0] 
        swfUrl = _getParam('flashplayer')
        url    = _getParam('streamer')
        file   = _getParam('file')
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s pageUrl=%s live=1 ' % (file, swfUrl, baseUrl)
            printDBG(url)
            return url
        return False
        
    def parserCRICHDTV(self, baseUrl):
        printDBG("parserCRICHDTV baseUrl[%s]" % baseUrl)
        
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = Referer
        
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        links = urlparser().getAutoDetectedStreamLink(Referer, data)
        printDBG(data)
        return links
        
        
        channelId = self.cm.ph.getSearchGroups(data, "id='([0-9]+?)'")[0]
        linkUrl = 'http://popeoftheplayers.eu/crichd.php?id={0}&width=710&height=460'.format(channelId)
        HTTP_HEADER['Referer'] = baseUrl
        
        sts, data = self.cm.getPage(linkUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        data = re.sub("<!--[\s\S]*?-->", "", data)
        data = re.sub("/\*[\s\S]*?\*/", "", data)
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """['"]%s['"][^'^"]+?['"]([^'^"]+?)['"]""" % name)[0] 
        swfUrl = "http://popeoftheplayers.eu/atdedead.swf"#_getParam('flashplayer')
        url    = _getParam('streamer') #rtmp://89.248.172.159:443/liverepeater
        file   = _getParam('file')
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s token=%s pageUrl=%s live=1 ' % (file, swfUrl, '#atd%#$ZH', linkUrl)
            printDBG(url)
            return url
        return False
        
        
    def parserCASTTOME(self, baseUrl):
        printDBG("parserCASTTOME baseUrl[%s]" % baseUrl)
        
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = Referer
        
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        data = re.sub("<!--[\s\S]*?-->", "", data)
        data = re.sub("/\*[\s\S]*?\*/", "", data)
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """['"]%s['"][^'^"]+?['"]([^'^"]+?)['"]""" % name)[0] 
        swfUrl = "http://www.castto.me/_.swf"
        url    = _getParam('streamer')
        file   = _getParam('file')
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s token=%s pageUrl=%s live=1 ' % (file, swfUrl, '#ed%h0#w@1', baseUrl)
            printDBG(url)
            return url
        return False
        
    def parserDELTATVPW(self, baseUrl):
        printDBG("parserDELTATVPW baseUrl[%s]" % baseUrl)
        
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = Referer
        
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        data = re.sub("<!--[\s\S]*?-->", "", data)
        data = re.sub("/\*[\s\S]*?\*/", "", data)
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, "%s=([^&]+?)&" % name)[0] 
        swfUrl = "http://cdn.deltatv.pw/players.swf"
        url    = _getParam('streamer')
        file   = _getParam('file')
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s token=%s pageUrl=%s live=1 ' % (file, swfUrl, 'Fo5_n0w?U.rA6l3-70w47ch', baseUrl)
            printDBG(url)
            return url
        return False
        
    def parserPXSTREAMTV(self, baseUrl):
        printDBG("parserPXSTREAMTV baseUrl[%s]" % baseUrl)
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = Referer
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        data = re.sub("<!--[\s\S]*?-->", "", data)
        data = re.sub("/\*[\s\S]*?\*/", "", data)
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """%s:[^'^"]*?['"]([^'^"]+?)['"]""" % name)[0] 
        swfUrl = "http://pxstream.tv/player510.swf"
        url    = _getParam('streamer')
        file   = _getParam('file')
        if '' != file and '' != url:
            url += ' playpath=%s swfUrl=%s pageUrl=%s live=1 ' % (file, swfUrl, baseUrl)
            printDBG(url)
            return url
        return False
    
    def parserCOOLCASTEU(self, baseUrl):
        printDBG("parserCOOLCASTEU baseUrl[%s]" % baseUrl)
        baseUrl = urlparser.decorateParamsFromUrl(baseUrl)
        Referer = baseUrl.meta.get('Referer', '')
        HTTP_HEADER = dict(self.HTTP_HEADER) 
        HTTP_HEADER['Referer'] = Referer
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        data = re.sub("<!--[\s\S]*?-->", "", data)
        data = re.sub("/\*[\s\S]*?\*/", "", data)
        printDBG(data)
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """['"]%s['"]:[^'^"]*?['"]([^'^"]+?)['"]""" % name)[0] 
        swfUrl = "http://coolcast.eu/file/1444766476/player.swf"
        url    = _getParam('streamer')
        file   = _getParam('file')
        if '' != file and '' != url:
            url += ' playpath=%s swfVfy=%s pageUrl=%s live=1 ' % (file, swfUrl, baseUrl)
            printDBG(url)
            return url
        return False
    
    def parserFILENUKE(self, baseUrl):
        printDBG("parserFILENUKE baseUrl[%s]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0' }
        
        COOKIE_FILE = GetCookieDir('filenuke.com')
        params_s  = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        params_l  = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'load_cookie':True} 
        
        sts, data = self.cm.getPage(baseUrl, params_s)
        if not sts: return False
        
        if 'method_free' in data:
            sts, data = self.cm.getPage(baseUrl, params_l, {'method_free':'Free'})
            if not sts: return False
            
        videoMarker = self.cm.ph.getSearchGroups(data, r"""['"]?file['"]?[ ]*?:[ ]*?([^ ^,]+?),""")[0]
        videoUrl    = self.cm.ph.getSearchGroups(data, r"""['"]?%s['"]?[ ]*?\=[ ]*?['"](http[^'^"]+?)["']""" % videoMarker)[0]
        
        printDBG("parserFILENUKE videoMarker[%s] videoUrl[%s]" % (videoMarker, videoUrl))
        if '' == videoUrl: return False
        videoUrl = urlparser.decorateUrl(videoUrl, {'User-Agent':'Mozilla/5.0', 'Referer':'http://filenuke.com/a/jwplayer/jwplayer.flash.swf'})
        return videoUrl
        
    def parserTHEFILEME(self, baseUrl):
        printDBG("parserTHEFILEME baseUrl[%s]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30" }
        
        COOKIE_FILE = GetCookieDir('thefile.me')
        params_s  = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        params_l  = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'load_cookie':True} 
        
        sts, data = self.cm.getPage(baseUrl, params_s)
        if not sts: return False
        
        data = CParsingHelper.getDataBeetwenMarkers(data, '<div class="main-wrap">', '</script>', False)[1]
        videoUrl = self.cm.ph.getSearchGroups(data, r"""['"]?%s['"]?[ ]*?\=[ ]*?['"](http[^'^"]+?)["']""" % 'href')[0]
        seconds = self.cm.ph.getSearchGroups(data, r"""seconds[ ]*?\=[ ]*?([^;^ ]+?);""")[0]
        printDBG("parserFILENUKE seconds[%s] videoUrl[%s]" % (seconds, videoUrl))
        seconds = int(seconds)
        
        time.sleep(seconds+1) 
        
        params_l['header']['Referer'] = videoUrl
        sts, data = self.cm.getPage(videoUrl, params_l)
        if not sts: return False
        
        data = CParsingHelper.getDataBeetwenMarkers(data, 'setup({', '}', False)[1]
        videoUrl = self.cm.ph.getSearchGroups(data, r"""['"]?file['"]?[ ]*?\:[ ]*?['"]([^"^']+?)['"]""")[0]
        if videoUrl.startswith('http'): return urlparser.decorateUrl(videoUrl)
        return False
        
    def parserCLOUDTIME(self, baseUrl):
        printDBG("parserCLOUDTIME baseUrl[%s]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0" }
        
        COOKIE_FILE = GetCookieDir('cloudtime.to')
        params_s  = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        params_l  = {'header':HTTP_HEADER, 'cookiefile':COOKIE_FILE, 'use_cookie': True, 'load_cookie':True} 
        
        if 'embed.' not in baseUrl:
            baseUrl = 'http://embed.cloudtime.to/embed.php?v=' + self.cm.ph.getSearchGroups(baseUrl + '/', '/video/([^/]+?)/')[0]
        
        sts, data = self.cm.getPage(baseUrl, params_s)
        if not sts: return False
        
        params = {}
        params['filekey'] = self.cm.ph.getSearchGroups(data, 'flashvars.filekey=([^;]+?);')[0]
        params['file'] = self.cm.ph.getSearchGroups(data, 'flashvars.file=([^;]+?);')[0]
        for key in params:
            ok = False
            for m in ['"', "'"]:
                if params[key].startswith(m) and params[key].endswith(m):
                    params[key] = params[key][1:-1]
                    ok = True
                    break
            if not ok:
                params[key] = self.cm.ph.getSearchGroups(data, r'''var %s=['"]([^'^"]+?)['"]''' % params[key])[0]
        
        videoUrl = "http://www.cloudtime.to/api/player.api.php?pass=undefined&key={0}&file={1}&user=undefined&cid3=undefined&cid=undefined&numOfErrors=0&cid2=undefined".format(urllib.quote(params['filekey']), urllib.quote(params['file'])) 
        sts, data = self.cm.getPage(videoUrl, params_l)
        if not sts: return False
        videoUrl = CParsingHelper.getDataBeetwenMarkers(data, 'url=', '&', False)[1]
        if videoUrl.startswith('http'): return urlparser.decorateUrl(videoUrl+'?client=FLASH')
        return False
        
    def parserNOSVIDEO(self, baseUrl):
        printDBG("parserNOSVIDEO baseUrl[%s]" % baseUrl)
        # code from https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/nosvideo.py
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        _VALID_URL = r'https?://(?:www\.)?nosvideo\.com/' + \
                 '(?:embed/|\?v=)(?P<id>[A-Za-z0-9]{12})/?'
        _PLAYLIST_URL = 'http://nosvideo.com/xml/{0}.xml'
        mobj = re.match(_VALID_URL, baseUrl)
        video_id = mobj.group('id')
        
        post_data = {
            'id': video_id,
            'op': 'download1',
            'method_free': 'Continue to Video',
        }
        
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER}, post_data)
        if not sts: return False
        
        id = self.cm.ph.getSearchGroups(data, 'php\|([^\|]+)\|')[0]
        url = _PLAYLIST_URL.format(id)
        
        sts, data = self.cm.getPage(url, {'header':HTTP_HEADER})
        if not sts: return False
        
        videoUrl = CParsingHelper.getDataBeetwenMarkers(data, '<file>', '</file>', False)[1]
        if videoUrl.startswith('http'): return urlparser.decorateUrl(videoUrl)
        return False
        
    def parserLETWATCHUS(self, baseUrl):
        printDBG("parserLETWATCHUS baseUrl[%s]" % baseUrl)
        def _findLinks(data):
            return self._findLinks(data, 'letwatch.us')
        return self._parserUNIVERSAL_A(baseUrl, 'http://letwatch.us/embed-{0}-640x360.html', _findLinks)
        
    def parserUPLOADCCOM(self, baseUrl):
        printDBG("parserUPLOADCCOM baseUrl[%s]" % baseUrl)
        def _findLinks(data):
            return self._findLinks2(data, baseUrl)
        return self._parserUNIVERSAL_A(baseUrl, 'http://www.uploadc.com/embed-{0}.html', _findLinks)
        
    def parserMIGHTYUPLOAD(self, baseUrl):
        printDBG("parserMIGHTYUPLOAD baseUrl[%s]" % baseUrl)
        def _preProcessing(data):
            return CParsingHelper.getDataBeetwenMarkers(data, '<div id="player_code">', '</div>', False)[1]
        def _findLinks(data):
            return self._findLinks2(data, baseUrl)
        return self._parserUNIVERSAL_A(baseUrl, 'http://www.mightyupload.com/embed-{0}-645x353.html', _findLinks, _preProcessing)
        
    def parserZALAACOM(self, baseUrl):
        printDBG("parserZALAACOM baseUrl[%s]" % baseUrl)
        def _findLinks(data):
            return self._findLinks2(data, baseUrl)
        return self._parserUNIVERSAL_A(baseUrl, 'http://www.zalaa.com/embed-{0}.html', _findLinks)
    
    def parserALLMYVIDEOS(self, baseUrl):
        printDBG("parserALLMYVIDEOS baseUrl[%s]" % baseUrl)
        def _findLinks(data):
            return self._findLinks(data, 'allmyvideos.net')
        return self._parserUNIVERSAL_A(baseUrl, 'http://allmyvideos.net/embed-{0}.html', _findLinks)
        
    def parserRAPIDVIDEOWS(self, baseUrl):
        printDBG("parserRAPIDVIDEOWS baseUrl[%s]" % baseUrl)
        def _findLinks(data):
            return self._findLinks2(data, baseUrl)
        return self._parserUNIVERSAL_A(baseUrl, 'http://rapidvideo.ws/embed-{0}-720x420.html', _findLinks)
        
    def parserHDVIDTV(self, baseUrl):
        printDBG("parserHDVIDTV baseUrl[%s]" % baseUrl)
        def _findLinks(data):
            return self._findLinks2(data, baseUrl)
        return self._parserUNIVERSAL_A(baseUrl, 'http://hdvid.tv/embed-{0}-950x480.html', _findLinks)
        
    def parserSTREAMPLAYCC(self, baseUrl):
        printDBG("parserSTREAMPLAYCC baseUrl[%s]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        if '/embed/' not in baseUrl:
            video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9]{16})/')[0]
            url = 'http://www.streamplay.cc/embed/{0}'.format(video_id)
        else:
            url = baseUrl
        post_data = None
        sts, data = self.cm.getPage(url, {'header':HTTP_HEADER}, post_data)
        if not sts: return False
        data = CParsingHelper.getDataBeetwenMarkers(data, 'id="playerStream"', '</a>', False)[1]
        videoUrl = self.cm.ph.getSearchGroups(data, 'href="(http[^"]+?)"')[0]
        if '' != videoUrl: return videoUrl
        return False
        
    def parserYOURVIDEOHOST(self, baseUrl):
        printDBG("parserSTREAMPLAYCC baseUrl[%s]" % baseUrl)
        video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9]{12})/')[0]
        url = 'http://yourvideohost.com/{0}'.format(video_id)
        return self.__parseJWPLAYER_A(url, 'yourvideohost.com')
        
    def parserVIDGGTO(self, baseUrl):
        printDBG("parserVIDGGTO baseUrl[%s]" % baseUrl)
        return self._parserUNIVERSAL_B(baseUrl)
        
    def parserTINYCC(self, baseUrl):
        printDBG("parserTINYCC baseUrl[%s]" % baseUrl)
        query_data = { 'url': baseUrl, 'return_data': False }       
        response = self.cm.getURLRequestData(query_data)
        redirectUrl = response.geturl() 
        response.close()
        if baseUrl != redirectUrl:
            return urlparser().getVideoLinkExt(redirectUrl)
        return False
    
    def parserWHOLECLOUD(self, baseUrl):
        printDBG("parserWHOLECLOUD baseUrl[%s]" % baseUrl)
        url = baseUrl.replace('movshare.net', 'wholecloud.net')
        try:
            mobj = re.search(r'/(?:file|video)/(?P<id>[a-z\d]{13})', url)
            video_id = mobj.group('id')
            url = 'http://www.wholecloud.net/embed/?v=' + video_id
        except:
            printExc()
        return self._parserUNIVERSAL_B(url)
        
    def parserSTREAM4KTO(self, baseUrl):
        printDBG("parserSTREAM4KTO baseUrl[%s]" % baseUrl)
        
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        
        data = self.cm.ph.getSearchGroups(data, "drdX_fx\('([^']+?)'\)")[0]
        data = drdX_fx( data )
        data = self.cm.ph.getSearchGroups(data, 'proxy.link=linkcdn%2A([^"]+?)"')[0]
        printDBG(data)
        x = gledajfilmDecrypter(198,128)
        Key = "VERTR05uak80NEpDajY1ejJjSjY="
        data = x.decrypt(data, Key.decode('base64', 'strict'), "ECB")
        if '' != data:
            return urlparser().getVideoLinkExt(data)
        return False
        
    def parserONETTV(self, baseUrl):
        printDBG("parserONETTV baseUrl[%r]" % baseUrl )
        
        videoUrls = []
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return videoUrls
        ckmId = self.cm.ph.getSearchGroups(data, 'data-params-mvp="([^"]+?)"')[0]
        if '' == ckmId: ckmId = self.cm.ph.getSearchGroups(data, 'id="mvp:([^"]+?)"')[0]
        if '' == ckmId: return videoUrls
        
        tm = str(int(time.time() * 1000))
        jQ = str(randrange(562674473039806,962674473039806))
        authKey = 'FDF9406DE81BE0B573142F380CFA6043'
        hostName = urlparser().getHostName(baseUrl)
        contentUrl = 'http://qi.ckm.onetapi.pl/?callback=jQuery183040'+ jQ + '_' + tm + '&body%5Bid%5D=' + authKey + '&body%5Bjsonrpc%5D=2.0&body%5Bmethod%5D=get_asset_detail&body%5Bparams%5D%5BID_Publikacji%5D=' + ckmId + '&body%5Bparams%5D%5BService%5D={0}&content-type=application%2Fjsonp&x-onet-app=player.front.onetapi.pl&_='.format(hostName) + tm
        sts, data = self.cm.getPage(contentUrl)
        if sts:
            try:
                printDBG(data)
                data = byteify( json.loads(data[data.find("(")+1:-2]) )
                data = data['result']['0']['formats']['wideo']
                for type in data:
                    for vidItem in data[type]:
                        if None != vidItem.get('drm_key', None): continue
                        vidUrl = vidItem.get('url', '')
                        if '' == vidUrl: continue
                        if 'hls' == type:
                            tmpTab = getDirectM3U8Playlist(vidUrl)
                            for tmp in tmpTab:
                                videoUrls.append({'name':'ONET type:%s :%s' % (type, tmp.get('bitrate', '0')), 'url':tmp['url']})
                        elif None != vidItem.get('video_bitrate', None):
                            videoUrls.append({'name':'ONET type:%s :%s' % (type, vidItem.get('video_bitrate', '0')), 'url':vidUrl})
                        elif None != vidItem.get('audio_bitrate', None):
                            videoUrls.append({'name':'ONET type:%s :%s' % (type, vidItem.get('audio_bitrate', '0')), 'url':vidUrl})
            except:
                printExc()
        return videoUrls
        
    def paserBYETVORG(self, baseUrl):
        printDBG("paserBYETVORG baseUrl[%r]" % baseUrl )
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl.meta.get('Referer', baseUrl) }
        file = self.cm.ph.getSearchGroups(baseUrl, "file=([0-9]+?)[^0-9]")[0]
        if '' == file: file = self.cm.ph.getSearchGroups(baseUrl, "a=([0-9]+?)[^0-9]")[0]
        linkUrl = "http://www.byetv.org/embed.php?a={0}&id=&width=710&height=460&autostart=true&strech=".format(file)
        sts, data = self.cm.getPage(linkUrl, {'header':HTTP_HEADER})
        if not sts: return False 
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, '"jwplayer1"', '</script>', False)
        if not sts: return False 
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, "'%s',[ ]*?'([^']+?)'" % name)[0] 
        
        swfUrl  = "http://p.jwpcdn.com/6/8/jwplayer.flash.swf"
        streamer = _getParam('streamer')
        file     = _getParam('file')
        token    = _getParam('token')
        provider = _getParam('provider')
        rtmpUrl  = provider + streamer[streamer.find(':'):]
        if '' != file and '' != rtmpUrl:
            rtmpUrl += ' playpath=file:%s swfUrl=%s token=%s pageUrl=%s live=1 ' % (file, swfUrl, token, linkUrl)
            printDBG(rtmpUrl)
            return rtmpUrl
        return False
        
    def paserPUTLIVEIN(self, baseUrl):
        printDBG("paserPUTLIVEIN baseUrl[%r]" % baseUrl )
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl.meta.get('Referer', baseUrl) }
        file = self.cm.ph.getSearchGroups(baseUrl, "file=([0-9]+?)[^0-9]")[0]
        if '' == file: file = self.cm.ph.getSearchGroups(baseUrl+'/', "/e/([^/]+?)/")[0]
        
        linkUrl = "http://www.putlive.in/e/{0}".format(file)
        sts, data = self.cm.getPage(linkUrl, {'header':HTTP_HEADER})
        if not sts: return False 
        #printDBG("=======================================================")
        #printDBG(data)
        #printDBG("=======================================================")
        token =  self.cm.ph.getSearchGroups(data, "'key' : '([^']+?)'")[0]
        if token != "": token = ' token=%s ' % token
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, 'unescape("', '")', False)
        if not sts: return False 
        data = urllib.unquote(data)
        #printDBG(data)
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, "%s=([^&]+?)&" % name)[0] 
        
        swfUrl  = "http://putlive.in/player59.swf"
        streamer = _getParam('streamer')
        file     = _getParam('file')
        provider = _getParam('provider')
        rtmpUrl  = provider + streamer[streamer.find(':'):]
        if '' != file and '' != rtmpUrl:
            rtmpUrl += ' playpath=%s swfUrl=%s %s pageUrl=%s live=1 ' % (file, swfUrl, token, linkUrl)
            printDBG(rtmpUrl)
            return rtmpUrl
        return False
        
    def paserSTREAMLIVETO(self, baseUrl):
        printDBG("paserSTREAMLIVETO baseUrl[%r]" % baseUrl )
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl.meta.get('Referer', baseUrl) }
        
        _url_re = re.compile("http(s)?://(\w+\.)?(ilive.to|streamlive.to)/.*/(?P<channel>\d+)")
        channel = _url_re.match(baseUrl).group("channel")
        
        linkUrl = "http://www.streamlive.to/embedplayer_new.php?width=640&height=480&channel={0}&autoplay=true".format(channel)
        sts, data = self.cm.getPage(linkUrl, {'header':HTTP_HEADER})
        if not sts: return False 
        
        # get token
        token = CParsingHelper.getDataBeetwenMarkers(data, 'var token="";', '});', False)[1]
        token = self.cm.ph.getSearchGroups(token, '"([^"]+?/server.php[^"]+?)"')[0]
        if token.startswith('//'): token = 'http:' + token
        sts, token = self.cm.getPage(token, {'header':HTTP_HEADER})
        if not sts: return False 
        token = byteify(json.loads(token))['token']
        if token != "": token = ' token=%s ' % token

        # get others params
        data = CParsingHelper.getDataBeetwenMarkers(data, '.setup(', '</script>', False)[1]
        
        def _getParam(name):
            return self.cm.ph.getSearchGroups(data, """['"]*%s['"]*[^'^"]+?['"]([^'^"]+?)['"]""" % name)[0].replace('\\/', '/')
        
        swfUrl  = "http://www.streamlive.to/ads/embed/player_ilive_embed.swf"
        streamer = _getParam('streamer')
        file     = _getParam('file').replace('.flv', '')
        app      = 'edge/' + streamer.split('/edge/')[-1]
        provider = _getParam('provider')
        rtmpUrl  = provider + streamer[streamer.find(':'):]
        if rtmpUrl.startswith('video://'):
            return rtmpUrl.replace('video://', 'http://')
        elif '' != file and '' != rtmpUrl:
            rtmpUrl += ' playpath=%s swfUrl=%s %s pageUrl=%s app=%s live=1 ' % (file, swfUrl, token, linkUrl, app)
            printDBG(rtmpUrl)
            return rtmpUrl
        return False
        
    def paserMEGOMTV(self, baseUrl):
        printDBG("paserMEGOMTV baseUrl[%r]" % baseUrl )
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl.meta.get('Referer', baseUrl) }
        
        id = self.cm.ph.getSearchGroups(baseUrl, "id=([^&]+?)&")[0]
        linkUrl = "http://distro.megom.tv/player-inside.php?id={0}&width=100%&height=450".format(id)
        
        sts, data = self.cm.getPage(linkUrl, {'header':HTTP_HEADER})
        if not sts: return False 
        
        sts, data = CParsingHelper.getDataBeetwenMarkers(data, '<head>', 'var ad_data;', False)
        if not sts: return False 
        swfUrl = 'http://lds.megom.tv/jwplayer.flash.swf'
        a = int(self.cm.ph.getSearchGroups(data, 'var a = ([0-9]+?);')[0])
        b = int(self.cm.ph.getSearchGroups(data, 'var b = ([0-9]+?);')[0])
        c = int(self.cm.ph.getSearchGroups(data, 'var c = ([0-9]+?);')[0])
        d = int(self.cm.ph.getSearchGroups(data, 'var d = ([0-9]+?);')[0])
        f = int(self.cm.ph.getSearchGroups(data, 'var f = ([0-9]+?);')[0])
        v_part = self.cm.ph.getSearchGroups(data, "var v_part = '([^']+?)'")[0]
        
        rtmpUrl = ('rtmp://%d.%d.%d.%d' % (a/f, b/f, c/f, d/f) ) + v_part
        rtmpUrl += ' swfUrl=%s pageUrl=%s live=1 ' % (swfUrl, linkUrl)
        printDBG(rtmpUrl)
        return rtmpUrl
        
    def parserOPENLOADIO(self, baseUrl):
        printDBG("parserOPENLOADIO baseUrl[%r]" % baseUrl )
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        if '/embed/' not in baseUrl:
            video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9_-]{11})[/~]')[0]
            if 'openload.co' in baseUrl:
                url = 'http://openload.co/embed/' + video_id
            else:
                url = 'http://openload.io/embed/' + video_id
        else:
            url = baseUrl
        
        sts, data = self.cm.getPage(url, {'header':HTTP_HEADER})
        if not sts:
            cmd = DMHelper.getBaseWgetCmd(HTTP_HEADER) + url + ' -O - 2> /dev/null'
            data = iptv_execute()( cmd )
            printDBG(data)
            if not data['sts'] or 0 != data['code']: return False
            data = data['data']
        
        # start https://github.com/whitecream01/WhiteCream-V0.0.1/blob/master/plugin.video.uwc/plugin.video.uwc-1.0.51.zip?raw=true
        def decodeOpenLoad(html):

            aastring = re.search(r"<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)</script", html, re.DOTALL | re.IGNORECASE).group(1)
            aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
            aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))","8")
            aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))","7")
            aastring = aastring.replace("((o^_^o) +(o^_^o))","6")
            aastring = aastring.replace("((ﾟｰﾟ) + (ﾟΘﾟ))","5")
            aastring = aastring.replace("(ﾟｰﾟ)","4")
            aastring = aastring.replace("((o^_^o) - (ﾟΘﾟ))","2")
            aastring = aastring.replace("(o^_^o)","3")
            aastring = aastring.replace("(ﾟΘﾟ)","1")
            aastring = aastring.replace("(c^_^o)","0")
            aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]","\\")
            aastring = aastring.replace("(3 +3 +0)","6")
            aastring = aastring.replace("(3 - 1 +0)","2")
            aastring = aastring.replace("(1 -0)","1")
            aastring = aastring.replace("(4 -0)","4")
            
            #printDBG(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n %s <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n" % aastring)

            decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
            decodestring = "\\+"+ decodestring
            decodestring = decodestring.replace("+","")
            decodestring = decodestring.replace(" ","")
            
            decodestring = decode(decodestring)
            decodestring = decodestring.replace("\\/","/")
            
            #printDBG(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n %s <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n" % decodestring)
            
            videourl = self.cm.ph.getSearchGroups(decodestring, '''src=['"](http[^"^']+?)['"]''', 1, True)[0]
            if '' == videourl: videourl = self.cm.ph.getSearchGroups(decodestring, '''['"](http[^"^']*?openload[^"^']+?)['"]''', 1, True)[0]
            if '' == videourl: videourl = self.cm.ph.getSearchGroups(decodestring, '''['"](http[^"^']+?)['"]''', 1, True)[0]
            return videourl

        def decode(encoded):
            for octc in (c for c in re.findall(r'\\(\d{2,3})', encoded)):
                encoded = encoded.replace(r'\%s' % octc, chr(int(octc, 8)))
            return encoded.decode('utf8')
        # end https://github.com/whitecream01/WhiteCream-V0.0.1/blob/master/plugin.video.uwc/plugin.video.uwc-1.0.51.zip?raw=true

        try:
            videoUrl = decodeOpenLoad(data)
        except:
            printExc()
            SetIPTVPlayerLastHostError( self.cm.ph.getDataBeetwenMarkers(data, '<p class="lead">', '</p>', False)[1] )
            return False
        if videoUrl.startswith('http'): return videoUrl.replace('https://', 'http://').replace('\\/', '/')
        return False
        
    def parserGAMETRAILERS(self, baseUrl):
        printDBG("parserGAMETRAILERS baseUrl[%r]" % baseUrl )
        list = GametrailersIE()._real_extract(baseUrl)[0]['formats']
        
        for idx in range(len(list)):
            width   = int(list[idx].get('width', 0))
            height  = int(list[idx].get('height', 0))
            bitrate = int(list[idx].get('bitrate', 0))
            if 0 != width or 0 != height:
                name = '%sx%s' % (width, height)
            elif 0 != bitrate:
                name = 'bitrate %s' % (bitrate)
            else:
                name = '%s.' % (idx + 1)
            list[idx]['name'] = name
        return list
        
    def parserVEVO(self, baseUrl):
        printDBG("parserVEVO baseUrl[%r]" % baseUrl )
        self.getVevoIE()._real_initialize()
        videoUrls = self.getVevoIE()._real_extract(baseUrl)['formats']
        
        for idx in range(len(videoUrls)):
            width   = int(videoUrls[idx].get('width', 0))
            height  = int(videoUrls[idx].get('height', 0))
            bitrate = int(videoUrls[idx].get('bitrate', 0)) / 8
            name = ''
            if 0 != bitrate:
                name = 'bitrate %s' % (formatBytes(bitrate, 0).replace('.0', '')+'/s')
            if 0 != width or 0 != height:
                name += ' %sx%s' % (width, height)
            if '' == name:
                name = '%s.' % (idx + 1)
            videoUrls[idx]['name'] = name
        if 0 < len(videoUrls):
            max_bitrate = int(config.plugins.iptvplayer.vevo_default_quality.value)
            def __getLinkQuality( itemLink ):
                return int(itemLink['bitrate'])
            videoUrls = CSelOneLink(videoUrls, __getLinkQuality, max_bitrate).getSortedLinks()
            if config.plugins.iptvplayer.vevo_use_default_quality.value:
                videoUrls = [videoUrls[0]]
        return videoUrls
        
    def parserSHAREDSX(self, baseUrl):
        printDBG("parserSHAREDSX baseUrl[%r]" % baseUrl )
        # based on https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/shared.py
        sts, data = self.cm.getPage(baseUrl)

        if '>File does not exist<' in data:
            SetIPTVPlayerLastHostError('Video %s does not exist' % baseUrl)
            return False

        data = self.cm.ph.getDataBeetwenMarkers(data, '<form', '</form>', False)[1]
        data = re.compile('name="([^"]+?)"[^>]*?value="([^"]+?)"').findall(data)
        post_data = dict(data)
        sts, data = self.cm.getPage(baseUrl, {'header':self.HTTP_HEADER}, post_data)
        if not sts: return False        
            
        videoUrl = self.cm.ph.getSearchGroups(data, 'data-url="([^"]+)"')[0]
        if videoUrl.startswith('http'): return videoUrl
        return False
        
    def parserPOSIEDZEPL(self, baseUrl):
        printDBG("parserPOSIEDZEPL baseUrl[%r]" % baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        if '/e.' not in baseUrl:
            video_id = self.cm.ph.getSearchGroups(baseUrl+'/', '/([A-Za-z0-9]{10})[/.?]')[0]
            url = 'http://e.posiedze.pl/' + video_id
        else:
            url = baseUrl
        sts, data = self.cm.getPage(url, {'header':HTTP_HEADER})
        if not sts: return False
        
        videoUrl = self.cm.ph.getSearchGroups(data, """["']*file["']*[ ]*?:[ ]*?["']([^"^']+?)['"]""")[0]
        if videoUrl.startswith('http'): return urlparser.decorateUrl(videoUrl)
        return False
        
    def parserNEODRIVECO(self, baseUrl):
        printDBG("parserNEODRIVECO baseUrl[%r]" % baseUrl)
        #http://neodrive.co/embed/EG0F2UYFNR2CN1CUDNT2I5OPN/
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':baseUrl }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        videoUrl = self.cm.ph.getSearchGroups(data, """["']*vurl["']*[ ]*?=[ ]*?["']([^"^']+?)['"]""")[0]
        if videoUrl.startswith('http'): return urlparser.decorateUrl(videoUrl)
        return False
        
    def parserMIPLAYERNET(self, baseUrl):
        printDBG("parserMIPLAYERNET baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        url2 = self.cm.ph.getSearchGroups(data, '''<iframe[^>]*?src=["'](http://miplayer.net[^"^']+?)["']''', 1, True)[0]
        if url2 != '':
            sts, data = self.cm.getPage(url2, {'header':HTTP_HEADER})
            if not sts: return False
        
        curl = self.cm.ph.getSearchGroups(data, '''curl[ ]*?=[ ]*?["']([^"^']+?)["']''', 1, True)[0]
        curl = base64.b64decode(curl)
        if curl.split('?')[0].endswith('.m3u8'):
            return getDirectM3U8Playlist(curl, checkExt=False)
        elif curl.startswith('rtmp'):
            swfUrl = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            curl += ' swfUrl=%s pageUrl=%s token=OOG17t.x#K9Vh#| ' % (swfUrl, url2)
            #curl += ' token=OOG17t.x#K9Vh#| '
            return curl
        return False
        
    def parserYOCASTTV(self, baseUrl):
        printDBG("parserYOCASTTV baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        swfUrl = self.cm.ph.getSearchGroups(data, '''["'](http[^'^"]+?swf)['"]''')[0]
        url    = self.cm.ph.getSearchGroups(data, '''streamer[^'^"]*?['"](rtmp[^'^"]+?)['"]''')[0]
        file   = self.cm.ph.getSearchGroups(data, '''file[^'^"]*?['"]([^'^"]+?)['"]''')[0].replace('.flv', '')
        if '' != file and '' != url:
            url += ' playpath=%s swfVfy=%s pageUrl=%s ' % (file, swfUrl, baseUrl)
            printDBG(url)
            return url
        return False
        
    def parserSOSTARTORG(self, baseUrl):
        printDBG("parserSOSTARTORG baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        swfUrl = 'http://sostart.org/jw/jwplayer.flash.swf'
        url    = ''
        file   = self.cm.ph.getSearchGroups(data, '''file[^'^"]*?['"]([^'^"]+?)['"]''')[0]
        url += file
        if '' != file and '' != url:
            url += ' swfVfy=%s pageUrl=%s ' % (swfUrl, baseUrl)
            printDBG(url)
            return url
        return False
        
    def parserGOODRTMP(self, baseUrl):
        printDBG("parserGOODRTMP baseUrl[%r]" % baseUrl)
        SetIPTVPlayerLastHostError('Links from "goodrtmp.com" not supported.')
        return False
        
    def parserLIFERTMP(self, baseUrl):
        printDBG("parserGOODRTMP baseUrl[%r]" % baseUrl)
        SetIPTVPlayerLastHostError('Links from "life-rtmp.com" not supported.')
        return False
    
    def parserTHEACTIONLIVE(self, baseUrl):
        printDBG("parserTHEACTIONLIVE baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        baseUrl = strwithmeta(baseUrl, {'Referer':baseUrl})
        return urlparser().getAutoDetectedStreamLink(baseUrl, data)
        
    def parserBIGGESTPLAYER(self, baseUrl):
        printDBG("parserBIGGESTPLAYER baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        data = self.cm.ph.getDataBeetwenMarkers(data, 'sources:', '}', False)[1]
        url  = self.cm.ph.getSearchGroups(data, '''file[^'^"]*?['"]([^'^"]+?)['"]''')[0]
        return getDirectM3U8Playlist(url)
        
    def parserLIVEONLINE247(self, baseUrl):
        printDBG("parserLIVEONLINE247 baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        
        swfUrl = self.cm.ph.getSearchGroups(data, '''["'](http[^'^"]+?swf)['"]''')[0]
        if swfUrl == '':
            swfUrl = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
        url   = self.cm.ph.getSearchGroups(data, '''file[^'^"]*?['"]([^'^"]+?)['"]''')[0]
        if url.startswith('rtmp'):
            url += ' swfVfy=%s pageUrl=%s ' % (swfUrl, baseUrl)
            printDBG(url)
            return url
        else:
            data = self.cm.ph.getDataBeetwenMarkers(data, 'source:', '}', False)[1]
            url = self.cm.ph.getSearchGroups(data, '''hls[^'^"]*?['"]([^'^"]+?)['"]''')[0]
            return getDirectM3U8Playlist(url)
        return False
        
    def parserFILEPUPNET(self, baseUrl):
        printDBG("parserFILEPUPNET baseUrl[%r]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        data = self.cm.ph.getDataBeetwenMarkers(data, 'window.onload', '</script>', False)[1]
        qualities = self.cm.ph.getSearchGroups(data, 'qualities:[ ]*?\[([^\]]+?)\]')[0]
        qualities = self.cm.ph.getAllItemsBeetwenMarkers(qualities, '"', '"', False)
        defaultQuality = self.cm.ph.getSearchGroups(data, 'defaultQuality:[ ]*?"([^"]+?)"')[0]
        qualities.remove(defaultQuality)
        
        sub_tracks = []
        subData = self.cm.ph.getDataBeetwenMarkers(data, 'subtitles:', ']', False)[1].split('}')
        for item in subData:
            if '"subtitles"' in item:
                label   = self.cm.ph.getSearchGroups(item, 'label:[ ]*?"([^"]+?)"')[0]
                srclang = self.cm.ph.getSearchGroups(item, 'srclang:[ ]*?"([^"]+?)"')[0]
                src     = self.cm.ph.getSearchGroups(item, 'src:[ ]*?"([^"]+?)"')[0]
                if not src.startswith('http'): continue
                sub_tracks.append({'title':label, 'url':src, 'lang':srclang, 'format':'srt'})
        
        printDBG(">>>>>>>>>>>>>>>>> sub_tracks[%s]\n[%s]" % (sub_tracks, subData))
        
        linksTab = []
        data = self.cm.ph.getDataBeetwenMarkers(data, 'sources:', ']', False)[1]
        defaultUrl = self.cm.ph.getSearchGroups(data, '"(http[^"]+?)"')[0]
        linksTab.append({'name':defaultQuality, 'url': strwithmeta(defaultUrl, {'external_sub_tracks':sub_tracks})})
        for item in qualities:
            if '.mp4' in defaultUrl:
                url = defaultUrl.replace('.mp4', '-%s.mp4' % item)
                linksTab.append({'name':item, 'url': strwithmeta(url, {'external_sub_tracks':sub_tracks})})
        return linksTab
        
    def parserSUPERFILMPL(self, baseUrl):
        printDBG("parserSUPERFILMPL baseUrl[%r]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        data = self.cm.ph.getDataBeetwenMarkers(data, '<video ', '</video>', False)[1]
        linkUrl = self.cm.ph.getSearchGroups(data, '<source[^>]+?src="(http[^"]+?)"')[0]
        return linkUrl
        
    def parserSENDVIDCOM(self, baseUrl):
        printDBG("parserSENDVIDCOM baseUrl[%r]" % baseUrl)
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        data = self.cm.ph.getDataBeetwenMarkers(data, '<video ', '</video>', False)[1]
        linkUrl = self.cm.ph.getSearchGroups(data, '<source[^>]+?src="([^"]+?)"')[0]
        if linkUrl.startswith('//'): linkUrl = 'http:' + linkUrl
        return linkUrl
        
    def parserFILEHOOT(self, baseUrl):
        printDBG("parserFILEHOOT baseUrl[%r]" % baseUrl)
        
        if 'embed-' not in baseUrl:
            baseUrl = 'http://filehoot.com/embed-%s-1046x562.html' % baseUrl.split('/')[-1].replace('.html', '')
        
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return False
        data = re.search('file:[ ]*?"([^"]+?)"', data)
        if data:
            linkVideo = data.group(1)
            printDBG('parserFILEHOOT direct link: ' + linkVideo)
            return linkVideo
        return False
        
    def parserSSH101COM(self, baseUrl):
        printDBG("parserFILEHOOT baseUrl[%r]" % baseUrl)
        Referer = strwithmeta(baseUrl).meta.get('Referer', baseUrl)
        HTTP_HEADER= { 'User-Agent':"Mozilla/5.0", 'Referer':Referer }
        sts, data = self.cm.getPage(baseUrl, {'header':HTTP_HEADER})
        if not sts: return False
        data = re.search('file:[ ]*?"([^"]+?)"', data).group(1)
        if data.split('?')[0].endswith('.m3u8'):
            return getDirectM3U8Playlist(data)
        return False
        
    def parserTWITCHTV(self, baseUrl):
        printDBG("parserFILEHOOT baseUrl[%r]" % baseUrl)
        if 'channel'  in baseUrl:
            data = baseUrl + '&'
        else:
            sts, data = self.cm.getPage(baseUrl)
        
        channel = self.cm.ph.getSearchGroups(data, '''channel=([^&^'^"]+?)[&'"]''')[0]
        MAIN_URLS = 'https://api.twitch.tv/'
        CHANNEL_TOKEN_URL = MAIN_URLS + 'api/channels/%s/access_token'
        LIVE_URL = 'http://usher.justin.tv/api/channel/hls/%s.m3u8?token=%s&sig=%s&allow_source=true'
        if '' != channel:
            url = CHANNEL_TOKEN_URL % channel
            sts, data = self.cm.getPage(url)
            urlTab = []
            if sts:
                try:
                    data = byteify( json.loads(data) )
                    url = LIVE_URL % (channel, urllib.quote(data['token']), data['sig'])
                    data = getDirectM3U8Playlist(url, checkExt=False)
                    for item in data:
                        item['url'] = urlparser.decorateUrl(item['url'], {'iptv_proto':'m3u8', 'iptv_livestream':True}) 
                        urlTab.append(item)
                except: printExc()
            return urlTab
        return False
        
    def parserCLOUDYEC(self, baseUrl):
        printDBG("parserCLOUDYEC baseUrl[%r]" % baseUrl)
        #based on https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/cloudy.py
        
        _VALID_URL = r'''(?x)
            https?://(?:www\.)?(?P<host>cloudy\.ec|videoraj\.ch)/
            (?:v/|embed\.php\?id=)
            (?P<id>[A-Za-z0-9]+)
            '''
        _EMBED_URL = 'http://www.%s/embed.php?id=%s'
        _API_URL = 'http://www.%s/api/player.api.php?%s'
        _MAX_TRIES = 2
        
        mobj = re.match(_VALID_URL, baseUrl)
        video_host = mobj.group('host')
        video_id = mobj.group('id')

        url = _EMBED_URL % (video_host, video_id)
        sts, data = self.cm.getPage(url)
        if not sts: return False

        file_key = self.cm.ph.getSearchGroups(data, r'key\s*:\s*"([^"]+)"')[0]
        if '' == file_key:
            file_key = self.cm.ph.getSearchGroups(data, r'filekey\s*=\s*"([^"]+)"')[0]

        def _extract_video(video_host, video_id, file_key, error_url=None, try_num=0):

            if try_num > _MAX_TRIES - 1:
                return False

            form = {'file': video_id, 'key': file_key}
            if error_url:
                form.update({'numOfErrors': try_num, 'errorCode': '404', 'errorUrl': error_url})

            data_url = _API_URL % (video_host, urllib.urlencode(form))
            sts, player_data = self.cm.getPage(data_url)
            if not sts: return sts

            data = parse_qs(player_data)
            try_num += 1
            if 'error' in data:
                return False
            title = data.get('title', [None])[0]
            if title:
                title = title.replace('&asdasdas', '').strip()
            video_url = data.get('url', [None])[0]
            if video_url:
                sts, data = self.cm.getPage(video_url, {'return_data':False})
                data.close()
                if not sts:
                    return self._extract_video(video_host, video_id, file_key, video_url, try_num)
            return [{'id': video_id, 'url': video_url, 'name': title}]
        return _extract_video(video_host, video_id, file_key)
    
    def parserSWIROWNIA(self, baseUrl):
        printDBG("Ekstraklasa.parserSWIROWNIA baseUrl[%r]" % baseUrl)
        def fun1(x):
            o = ""
            l = len(x)
            i = l - 1;
            while i >= 0:
                try:
                    o += x[i]
                except:
                    pass
                i -= 1
            return o
        def fun2(x):
            o = ""
            ol = len(x)
            l = ol
            while ord(x[l/13]) != 48:
                try:
                    x += x
                    l += l
                except:
                    pass
            i = l - 1
            while i >= 0:
                try:
                    o += x[i]
                except:
                    pass
                i -= 1
            return o[:ol]
        def fun3(x, y, a=1):
            o = ""
            i = 0
            l = len(x)
            while i<l:
                if i<y:
                    y += a
                y %= 127
                o += JS_FromCharCode(ord(x[i]) ^ y)
                y += 1
                i += 1
            return o
              
        sts, data = self.cm.getPage(baseUrl)
        if not sts: return []
        data = data[data.find('x="')+2 : data.rfind('"')+1]
        dataTab = data.split('+\n')
        data = ""
        for line in dataTab:
            line = line.strip()
            if '"' != line[0] or '"' != line[-1]:
                raise Exception("parserSWIROWNIA parsing ERROR")
            data += line[1:-1]


        def backslashUnEscaped(data):
            #return pythonUnescape(data)
            #return codecs.decode(data, "unicode_escape").replace('\\,', ',')
            #return re.sub(r'\\(.)', r'\1', data)
            #try:
            #    return data.decode('unicode-escape')
            #except:
            #    printExc()
                #return re.sub(r'\\(.)', r'\1', data)
            tmp = ''
            idx = 0
            while idx < len(data):
                if data[idx] == '\\':
                    tmp += data[idx+1]
                    idx += 2
                else:
                    tmp += data[idx]
                    idx += 1
            return tmp
            
        def printDBG2(data):
            printDBG("================================================================")
            printDBG( data )
            printDBG("================================================================")
        data = backslashUnEscaped(data)
        
        data = data[data.find('f("')+3:data.rfind('"')]
        data = fun1( data )
        printDBG2(data)
        data = backslashUnEscaped(data)
        
        printDBG2(data)
        
        data = data[data.find('f("')+3:data.rfind('"')]
        printDBG2(data)
        data = data.decode('string_escape')
        data = fun3( data, 50, 0)
        data = backslashUnEscaped(data)
        
        printDBG2(data)
        
        return
        
        data = data[data.find('f("')+3:data.rfind('"')]
        data = fun2( data )
        data = data.decode('string-escape')

        data = data[data.find('f("')+3:data.rfind('"')]
        data = fun3( data, 23, 1)
        data = backslashUnEscaped(data)
        
        printDBG(data)
        printDBG("------------------------------------------------------------------------------------")
        return
        #data = data.decode('string_escape')
        #printDBG(data)
        data = fun3( data, 23, 1)
        #data = data.decode('string_escape')
        data = backslashUnEscaped(data)
        
        printDBG("------------------------------------------------------------------------------------")
        printDBG(data)
        printDBG("------------------------------------------------------------------------------------")
        
    def parseNETUTV(self, url):
        printDBG("parserDIVEXPRESS url[%s]" % url)
        # example video: http://netu.tv/watch_video.php?v=WO4OAYA4K758
    
        printDBG("parseNETUTV url[%s]\n" % url)
        #http://netu.tv/watch_video.php?v=ODM4R872W3S9
        match = re.search("=([0-9A-Z]+?)[^0-9^A-Z]", url + '|' )
        vid = match.group(1)
        playerUrl = "http://hqq.tv/player/embed_player.php?vid=%s&autoplay=no" % vid
        
        HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
        #HTTP_HEADER['Referer'] = url
        sts, data = self.cm.getPage(playerUrl, {'header' : HTTP_HEADER})
        data = base64.b64decode(re.search('base64\,([^"]+?)"', data).group(1))
        #printDBG(data)
        l01 = re.search("='([^']+?)'", data).group(1)
        _0x84de = re.search("var _0x84de=\[([^]]+?)\]", data).group(1)
        _0x84de = re.compile('"([^"]*?)"').findall(_0x84de)
        
        data = MYOBFUSCATECOM_OIO( MYOBFUSCATECOM_0ll(l01, _0x84de[1]), _0x84de[0], _0x84de[1])
        data = re.search("='([^']+?)'", data).group(1).replace('%', '\\').decode('unicode-escape').encode('UTF-8')
        
        data = re.compile('<input name="([^"]+?)" [^>]+? value="([^"]+?)">').findall(data)
        post_data = {}
        for idx in range(len(data)):
            post_data[ data[idx][0] ] = data[idx][1]
            
        secPlayerUrl = "http://hqq.tv/sec/player/embed_player.php?vid=%s&at=%s&autoplayed=%s&referer=on&http_referer=%s&pass=" % (vid, post_data.get('at', ''),  post_data.get('autoplayed', ''), urllib.quote(playerUrl))
        HTTP_HEADER['Referer'] = playerUrl
        sts, data = self.cm.getPage(secPlayerUrl, {'header' : HTTP_HEADER}, post_data)
        data = re.sub('document\.write\(unescape\("([^"]+?)"\)', lambda m: urllib.unquote(m.group(1)), data)
        #CParsingHelper.writeToFile('/home/sulge/test.html', data)
        def getUtf8Str(st):
            idx = 0
            st2 = ''
            while idx < len(st):
                st2 += '\\u0' + st[idx:idx + 3]
                idx += 3
            return st2.decode('unicode-escape').encode('UTF-8')
        file_vars = CParsingHelper.getDataBeetwenMarkers(data, 'Uppod(', ')', False)[1]
        file_vars = CParsingHelper.getDataBeetwenMarkers(data, 'file:', ',', False)[1].strip()
        file_vars = file_vars.split('+')
        file_url = ''
        for file_var in file_vars:
            file_var = file_var.strip()
            if 0 < len(file_var):
                match = re.search('''["']([^"]*?)["']''', file_var)
                if match: file_url += match.group(1)
                else: file_url += re.search('''var[ ]+%s[ ]*=[ ]*["']([^"]*?)["']''' % file_var, data).group(1)
        if file_url.startswith('#') and 3 < len(file_url): file_url = getUtf8Str(file_url[1:])
        #printDBG("[[[[[[[[[[[[[[[[[[[[[[%r]" % file_url)
        if file_url.startswith('http'): return urlparser.decorateUrl(file_url, {'iptv_livestream':False, 'Range':'bytes=0-', 'User-Agent':'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'})
        return False     
       
       
    '''
    ###############################################
    # start - other methods from netu.tv player.swf
    ###############################################
    def encodeByteArray(tab):
        ret = ""
        _lg27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        idx = 0;
        _local4 = [64,64,64,64]
        while idx < len(tab):
            tmpTab = []
            while len(tmpTab) < 4 and idx < len(tab):
                tmpTab.append(ord(tab[idx]))
                idx += 1
                
            _local4[0] = ((tmpTab[0] & 252) >> 2);
            _local4[1] = (((tmpTab[0] & 3) << 4) | (tmpTab[1] >> 4));
            _local4[2] = (((tmpTab[1] & 15) << 2) | (tmpTab[2] >> 6));
            _local4[3] = (tmpTab[2] & 63);
            
            for item in _local4:
                ret += _lg27[item]
        return ret
        
        
    def tr(_arg1, _arg2=114, _arg3=65):
        if ord(_arg1[len(_arg1) - 2]) == _arg2 and ord(_arg1[2]) == _arg3:
            _local5 = "";
            _local4 = len(_arg1) - 1;
            while _local4 >= 0:
                _local5 = _local5 + _arg1[_local4];
                _local4-= 1;
        
            _arg1 = _local5;
            _local6 = _arg1[-2:];
            _arg1 = _arg1[2:];
            _arg1 = _arg1[0, -3];
            _local6 = (_local6 / 2);
            if _local6 < len(_arg1):
                _local4 = _local6;
                while _local4 < _arg1.length:
                    _arg1 = _arg1[0:_local4] + _arg1[_local4 + 1:];
                    _local4 = _local4 + _local6;
            _arg1 = _arg1 + "!";
        return _arg1
    ###############################################
    # end - other methods from netu.tv player.swf
    ###############################################
    '''

    '''
    def parserNEXTVIDEO(self,url):
        sts, data = self.getPage(url)
        if False == sts:
            return False
        match = re.search('file:[^"]+?"([^"]+?)"', data)
        if match: 
            return match.group(1)
        else:
            return False
    '''
        
    '''
    def parserDIVXSTAGE(self, url):
        sts, data = self.getPage(url)
        if False == sts:
            return False
        
        match = re.search('flashvars.file="([^"]+?)";', data)
        if match: 
            file = match.group(1)
        else:
            return False
        match = re.search('flashvars.filekey="([^"]+?)";', data)
        if match: 
            filekey = match.group(1).replace('.', '%2E')
        else:
            return False
        match = re.search('flashvars.cid="([^"]+?)";', data)
        if match: 
            cid = match.group(1)
        else:
            return False
        
        urlApi = 'http://www.divxstage.eu/api/player.api.php?user=undefined&cid3=undefined&file=%s&cid=%s&key=%s&numOfErrors=0&pass=undefined&cid2=undefined' %s (file, cid, filekey)
        
        sts, data = self.getPage(url)
        if False == sts:
            return False
            
        match = re.search('url=([^&]+?)&', data)
        if match: 
            return match.group(1)
        else:
            return False
            
            
<input type="hidden" name="op" value="download1">
<input type="hidden" name="usr_login" value="">
<input type="hidden" name="id" value="7wtoiieyqsmv">
<input type="hidden" name="fname" value="The.Secret.Life.of.Walter.Mitty.2013.PLSUBBED.DVDscr.XViD.AC3-OzW.avi">
<input type="hidden" name="referer" value="http://vidto.me/embed-7wtoiieyqsmv-647x500.html">
<input type="hidden" name="hash" value="4upjo7kqazfuwg4ex75zwmruewqrrxbq">

{
    "auto_hd": false,
    "autoplay_reason": "unknown",
    "default_hd": false,
    "disable_native_controls": false,
    "inline_player": false,
    "pixel_ratio": 1,
    "preload": false,
    "start_muted": false,
    "video_data": [{
        "hd_src": "https:\\/\\/fbcdn-video-a-a.akamaihd.net\\/hvideo-ak-xpa1\\/v\\/t43.1792-2\\/1346786_597358996980898_38093_n.mp4?rl=1924&vabr=1283&oh=39547a46c1706d6985a63f451d9804ee&oe=54FB5F56&__gda__=1425759704_938e66c3e93914a0af0978780c5a3a81",
        "is_hds": false,
        "is_hls": false,
        "rotation": 0,
        "sd_src": "https:\\/\\/fbcdn-video-p-a.akamaihd.net\\/hvideo-ak-xpa1\\/v\\/t42.1790-2\\/1188227_592870284096436_64686_n.mp4?rl=563&vabr=313&oh=e891677083036d0b291ed601f85953d8&oe=54FB5B46&__gda__=1425762824_3c005c8845ab035ba6aceae1cc5f63d5",
        "video_id": "201191406597661",
        "sd_tag": "legacy_sd",
        "hd_tag": "legacy_hd",
        "sd_src_no_ratelimit": "https:\\/\\/fbcdn-video-p-a.akamaihd.net\\/hvideo-ak-xpa1\\/v\\/t42.1790-2\\/1188227_592870284096436_64686_n.mp4?oh=e891677083036d0b291ed601f85953d8&oe=54FB5B46&__gda__=1425762824_fe9007c59a8243300d34f90a3f025c71",
        "hd_src_no_ratelimit": "https:\\/\\/fbcdn-video-a-a.akamaihd.net\\/hvideo-ak-xpa1\\/v\\/t43.1792-2\\/1346786_597358996980898_38093_n.mp4?oh=39547a46c1706d6985a63f451d9804ee&oe=54FB5F56&__gda__=1425759704_4d32e5007b137533f795db5c816d6ef2",
        "subtitles_src": null
    }],
    "show_captions_default": false,
    "persistent_volume": true,
    "buffer_length": 0.1
}
    '''
