from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import *

class j00zekTreeHostSelector(Screen):

    def __init__(self, session):
        self.sortDate = False
        self.openmovie = ''
        self.opensubtitle = ''
        self.URLlinkName = ''
        self.movietxt = _('Movie: ')
        self.subtitletxt = _('Subtitle: ')
        self.rootID = myConfig.MultiFramework.value
        self.LastPlayedService = None
        self.LastFolderSelected= None
  
        self.skin  = LoadSkin("j00zekTreeHostSelector")
        
        Screen.__init__(self, session)
        self["info"] = Label()
        self["myPath"] = Label(myConfig.FileListLastFolder.value)
        
        self["filemovie"] = Label(self.movietxt)
        self["filesubtitle"] = Label(self.subtitletxt)
        self["key_red"] = StaticText(_("Play"))
        self["Description"] = Label(KeyMapInfo)
        self["Cover"] = Pixmap()
        
        if path.exists(ExtPluginsPath + '/DMnapi/DMnapi.pyo') or path.exists(ExtPluginsPath +'/DMnapi/DMnapi.pyc') or path.exists(ExtPluginsPath +'/DMnapi/DMnapi.py'):
            self.DmnapiInstalled = True
            self["key_green"] = StaticText(_("DMnapi"))
        else:
            self.DmnapiInstalled = False
            self["key_green"] = StaticText(_("Install DMnapi"))
            
        self["key_yellow"] = StaticText(_("Config"))
        self["key_blue"] = StaticText(_("Sort by name"))
        self["info"].setText(PluginName + ' ' + PluginInfo)
        self.filelist = FileList(myConfig.FileListLastFolder.value, matchingPattern = "(?i)^.*\.(avi|txt|srt|mpg|vob|divx|m4v|mkv|mp4|dat|mov|ts|url)(?!\.(cuts|ap$|meta$|sc$))",sortDate=False)
        self["filelist"] = self.filelist
        self["actions"] = ActionMap(["AdvancedFreePlayerSelector"],
            {
                "selectFile": self.selectFile,
                "ExitPlayer": self.ExitPlayer,
                "lineUp": self.lineUp,
                "lineDown": self.lineDown,
                "pageUp": self.pageUp,
                "pageDown": self.pageDown,
                "PlayMovie": self.PlayMovie,
                "runDMnapi": self.runDMnapi,
                "runConfig": self.runConfig,
                "setSort": self.setSort
            },-2)
        self.setTitle(PluginName + ' ' + PluginInfo)
        if myConfig.StopService.value == True:
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()

    def pageUp(self):
        self["filelist"].pageUp()

    def pageDown(self):
        self["filelist"].pageDown()

    def lineUp(self):
        self["filelist"].up()

    def lineDown(self):
        self["filelist"].down()

    def PlayMovie(self):
        if not self.openmovie == "":
            myConfig.FileListLastFolder.value =  self["myPath"].getText()
            myConfig.FileListLastFolder.save()
            print self["myPath"].getText()
            if not path.exists(self.openmovie + '.cuts'):
                self.SelectFramework()
            elif path.getsize(self.openmovie + '.cuts') == 0:
                self.SelectFramework()
            else:
                self.session.openWithCallback(self.ClearCuts, MessageBox, _("Do you want to resume this playback?"), timeout=10, default=True)

    def ClearCuts(self, ret):
        if ret == False:
            resetMoviePlayState(self.openmovie + '.cuts')
        self.SelectFramework()

    def SelectFramework(self):
        if myConfig.MultiFramework.value == "select":
            from Screens.ChoiceBox import ChoiceBox
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = [("gstreamer (root 4097)","4097"),("ffmpeg (root 4099)","4099"),("Hardware (root 1)","1"),])
        else:
            if self.openmovie.endswith('.ts'):
                self.rootID = '1'
            else:
                self.rootID = myConfig.MultiFramework.value
            self.StartPlayer()

    def SelectedFramework(self, ret):
        if ret:
            self.rootID = ret[1]
            printDEBUG("Selected framework: " + ret[1])
        self.StartPlayer()
      
    def StartPlayer(self):
        lastOPLIsetting = None
        
        def EndPlayer():
            if lastOPLIsetting is not None:
                config.subtitles.pango_autoturnon.valu = lastOPLIsetting
            self["filelist"].refresh()

        if not path.exists(self.opensubtitle) and not self.opensubtitle.startswith("http://"):
            self.opensubtitle = ""
        if path.exists(self.openmovie) or self.openmovie.startswith("http://"):
            if myConfig.SRTplayer.value =="system":
                try: 
                    lastOPLIsetting = config.subtitles.pango_autoturnon.value
                    config.subtitles.pango_autoturnon.value = True
                except:
                    pass
                self.session.openWithCallback(EndPlayer,AdvancedFreePlayer,self.openmovie,'',self.rootID,self.LastPlayedService,self.URLlinkName)
                return
            else:
                try: 
                    lastOPLIsetting = config.subtitles.pango_autoturnon.value
                    config.subtitles.pango_autoturnon.value = False
                    printDEBUG("OpenPLI subtitles disabled")
                except:
                    printDEBUG("pango_autoturnon non existent, is it VTI?")
                self.session.openWithCallback(EndPlayer,AdvancedFreePlayer,self.openmovie,self.opensubtitle,self.rootID,self.LastPlayedService,self.URLlinkName)
                return
        else:
            printDEBUG("StartPlayer>>> File %s does not exist :(" % self.openmovie)

    def runConfig(self):
        from AdvancedFreePlayerConfig import AdvancedFreePlayerConfig
        self.session.open(AdvancedFreePlayerConfig)
        return

    def setSort(self):
        if self.sortDate:
            #print "sortDate=False"
            self["filelist"].sortDateDisable()
            self.sortDate=False
            self["key_blue"].setText(_("Sort by name"))
        else:
            #print "sortDate=True"
            self["filelist"].sortDateEnable()
            self.sortDate=True
            self["key_blue"].setText(_("Sort by date"))
        self["filelist"].refresh()

    def selectFile(self):
        selection = self["filelist"].getSelection()
        if selection[1] == True: # isDir
            if selection[0] is not None and self.filelist.getCurrentDirectory() is not None and \
                    len(selection[0]) > len(self.filelist.getCurrentDirectory()) or self.LastFolderSelected == None:
                self.LastFolderSelected = selection[0]
                self["filelist"].changeDir(selection[0], "FakeFolderName")
            else:
                print "Folder Down"
                self["filelist"].changeDir(selection[0], self.LastFolderSelected)
            
            d = self.filelist.getCurrentDirectory()
            if d is None:
                d=""
            elif not d.endswith('/'):
                d +='/'
            #self.title = d
            self["myPath"].setText(d)
        else:
            d = self.filelist.getCurrentDirectory()
            if d is None:
                d=""
            elif not d.endswith('/'):
                d +='/'
            f = self.filelist.getFilename()
            printDEBUG("self.selectFile>> " + d + f)
            temp = self.getExtension(f)
            #print temp
            if temp == ".url":
                self.opensubtitle = ''
                self.openmovie = ''
                with open(d + f,'r') as UrlContent:
                    for data in UrlContent:
                        print data
                        if data.find('movieURL=') > -1: #find instead of startswith to avoid BOM issues ;)
                            self.openmovie = data.split('=')[1].strip()
                            self.URLlinkName = d + f
                        elif data.find('srtURL=') > -1:
                            self.opensubtitle = data.split('=')[1].strip()
                if self["filemovie"].getText() != (self.movietxt + self.openmovie):
                    self["filemovie"].setText(self.movietxt + self.openmovie)
                    self["filesubtitle"].setText(self.subtitletxt + self.opensubtitle)
                elif myConfig.KeyOK.value == 'play':
                    self.PlayMovie()
                    return
                else:
                    self.openmovie = ''
                    self["filemovie"].setText(self.movietxt)
                    self.opensubtitle = ''
                    self["filesubtitle"].setText(self.subtitletxt + self.opensubtitle)
            elif temp == ".srt" or temp == ".txt":
                #if self.DmnapiInstalled == True:
                if self.opensubtitle == (d + f): #clear subtitles selection
                    self["filesubtitle"].setText(self.subtitletxt)
                    self.opensubtitle = ''
                else:
                    self["filesubtitle"].setText(self.subtitletxt + f)
                    self.opensubtitle = d + f
            else:
                if self.openmovie == (d + f):
                    if myConfig.KeyOK.value == 'play':
                        self.PlayMovie()
                        return
                    else:
                        self.openmovie = ''
                        self["filemovie"].setText(self.movietxt)
                else:
                    self.openmovie = d + f
                    self["filemovie"].setText(self.movietxt + f)
                    self.URLlinkName = ''
                
                self.SetDescriptionAndCover(self.openmovie)
                
                #if self.DmnapiInstalled == True:
                temp = f[:-4]
                if path.exists( d + temp + ".srt"):
                    self["filesubtitle"].setText(self.subtitletxt + temp + ".srt")
                    self.opensubtitle = d + temp + ".srt"
                elif path.exists( d + temp + ".txt"):
                    self["filesubtitle"].setText(self.subtitletxt + temp + ".txt")
                    self.opensubtitle = d + temp + ".txt"
                else:
                    self["filesubtitle"].setText(self.subtitletxt)
                    self.opensubtitle = ''
                #else:
                #    self.opensubtitle = ''
      
    def getExtension(self, MovieNameWithExtension):
        return path.splitext( path.basename(MovieNameWithExtension) )[1]
      
    def SetDescriptionAndCover(self, MovieNameWithPath):
        if MovieNameWithPath == '':
            self["Cover"].hide()
            self["Description"].setText('')
            return
        
        temp = getNameWithoutExtension(MovieNameWithPath)
        ### COVER ###
        if path.exists(temp + '.jpg'):
            self["Cover"].instance.setScale(1)
            self["Cover"].instance.setPixmap(LoadPixmap(path=temp + '.jpg'))
            self["Cover"].show()
        else:
            self["Cover"].hide()
            
        ### DESCRIPTION from EIT ###
        if path.exists(temp + '.eit'):
            def parseMJD(MJD):
                # Parse 16 bit unsigned int containing Modified Julian Date,
                # as per DVB-SI spec
                # returning year,month,day
                YY = int( (MJD - 15078.2) / 365.25 )
                MM = int( (MJD - 14956.1 - int(YY*365.25) ) / 30.6001 )
                D  = MJD - 14956 - int(YY*365.25) - int(MM * 30.6001)
                K=0
                if MM == 14 or MM == 15: K=1
                return "%02d/%02d/%02d" % ( (1900 + YY+K), (MM-1-K*12), D)

            def unBCD(byte):
                return (byte>>4)*10 + (byte & 0xf)

            import struct

            with open(temp + '.eit','r') as descrTXT:
                data = descrTXT.read() #[19:].replace('\00','\n')
                ### Below is based on EMC handlers, thanks to author!!!
                e = struct.unpack(">HHBBBBBBH", data[0:12])
                myDescr = _('Recorded: %s %02d:%02d:%02d\n') % (parseMJD(e[1]), unBCD(e[2]), unBCD(e[3]), unBCD(e[4]) )
                myDescr += _('Lenght: %02d:%02d:%02d\n\n') % (unBCD(e[5]), unBCD(e[6]), unBCD(e[7]) )
                extended_event_descriptor = []
                EETtxt = ''
                pos = 12
                while pos < len(data):
                    rec = ord(data[pos])
                    length = ord(data[pos+1]) + 2
                    if rec == 0x4E:
                    #special way to handle CR/LF charater
                        for i in range (pos+8,pos+length):
                            if str(ord(data[i]))=="138":
                                extended_event_descriptor.append("\n")
                            else:
                                if data[i]== '\x10' or data[i]== '\x00' or  data[i]== '\x02':
                                    pass
                                else:
                                    extended_event_descriptor.append(data[i])
                    pos += length

                    # Very bad but there can be both encodings
                    # User files can be in cp1252
                    # Is there no other way?
                EETtxt = "".join(extended_event_descriptor)
                if EETtxt:
                    try:
                        EETtxt.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            EETtxt = EETtxt.decode("cp1250").encode("utf-8")
                        except UnicodeDecodeError:
                            # do nothing, otherwise cyrillic wont properly displayed
                            #extended_event_descriptor = extended_event_descriptor.decode("iso-8859-1").encode("utf-8")
                            pass
                
                self["Description"].setText(myDescr + self.ConvertChars(EETtxt) )
        ### DESCRIPTION from TXT ###
        elif path.exists(temp + '.txt'):
            with open(temp + '.txt','r') as descrTXT:
                myDescr = descrTXT.read()
                if myDescr[0] == "{" or myDescr[0] =="[" or myDescr[1] == ":" or myDescr[2] == ":":
                    self["Description"].setText('')
                else:
                    self["Description"].setText(myDescr)
        else:
            self["Description"].setText('')
    
    def ConvertChars(self, text):
        CharsTable={ '\xC2\xB1': '\xC4\x85','\xC2\xB6': '\xC5\x9b','\xC4\xBD': '\xC5\xba'}
        for i, j in CharsTable.iteritems():
            text = text.replace(i, j)
        return text

    def ExitPlayer(self):
        myConfig.PlayerOn.value = False
        configfile.save()
        self.close()

##################################################################### SUBTITLES >>>>>>>>>>
    def runDMnapi(self):
        if self.DmnapiInstalled == True:
            self.DMnapi()
            self["filelist"].refresh()
        else:
            def doNothing():
                pass
            def goUpdate(ret):
                if ret is True:
                    runlist = []
                    runlist.append( ('chmod 755 %sUpdate*.sh' % PluginPath) )
                    runlist.append( ('cp -a %sUpdateDMnapi.sh /tmp/AFPUpdate.sh' % PluginPath) ) #to have clear path of updating this script too ;)
                    runlist.append( ('/tmp/AFPUpdate.sh %s "%s"' % (config.plugins.AdvancedFreePlayer.Version.value,PluginInfo)) )
                    from AdvancedFreePlayerConfig import AdvancedFreePlayerConsole
                    self.session.openWithCallback(doNothing, AdvancedFreePlayerConsole, title = _("Installing DMnapi plugin"), cmdlist = runlist)
                    return
            self.session.openWithCallback(goUpdate, MessageBox,_("Do you want to install DMnapi plugin?"),  type = MessageBox.TYPE_YESNO, timeout = 10, default = False)
        return

    def DMnapi(self):
        if not self["filelist"].canDescent():
            f = self.filelist.getFilename()
            temp = f[-4:]
            if temp != ".srt" and temp != ".txt":
                curSelFile = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
                try:
                    from Plugins.Extensions.DMnapi.DMnapi import DMnapi
                    self.session.openWithCallback(self.dmnapiCallback, DMnapi, curSelFile)
                except:
                    printDEBUG("Exception loading DMnapi!!!")
            else:
                self.session.open(MessageBox,_("Please select movie files !\n\n"),MessageBox.TYPE_INFO)
                return

    def dmnapiCallback(self, answer=False):
        self["filelist"].refresh()
        
    def createSummary(self):
        return AdvancedFreePlayerStartLCD
##################################################################### LCD Screens <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class AdvancedFreePlayerLCD(Screen): 
    skin = LoadSkin('AdvancedFreePlayerLCD')
 
class AdvancedFreePlayerStartLCD(Screen):
    skin = LoadSkin('AdvancedFreePlayerStartLCD')
                
##################################################################### CLASS ENDS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def getNameWithoutExtension(MovieNameWithExtension):
    extLenght = len(path.splitext( path.basename(MovieNameWithExtension) )[1])
    return MovieNameWithExtension[: -extLenght]

import struct
cutsParser = struct.Struct('>QI') # big-endian, 64-bit PTS and 32-bit type
def resetMoviePlayState(cutsFileName):
    printDEBUG('resetMoviePlayState >>>')
    return
    try:
        f = open(cutsFileName, 'rb')
        cutlist = []
        while 1:
            data = f.read(cutsParser.size)
            if len(data) < cutsParser.size:
                break
            cut, cutType = cutsParser.unpack(data)
            if cutType != 32:
                cutlist.append(data)
        f.close()
        f = open(cutsFileName, 'wb')
        #f.write(''.join(cutlist))
        printDEBUG(''.join(cutlist))
        f.close()
    except:
        pass

        