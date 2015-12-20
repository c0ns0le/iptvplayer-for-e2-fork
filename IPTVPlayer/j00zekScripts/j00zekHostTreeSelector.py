from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import *
from Plugins.Extensions.IPTVPlayer.__init__ import _
from Plugins.Extensions.IPTVPlayer.version import IPTV_VERSION
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Tools.LoadPixmap import LoadPixmap

from re import compile as re_compile
from os import path as os_path, listdir, system as os_system
from Components.config import config
from Components.MenuList import MenuList
from Components.Harddisk import harddiskmanager #do wywalenia!!!!

from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename, fileExists

from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, \
    eServiceReference, eServiceCenter, gFont

##################################################### main widget #####################################################
class j00zekHostTreeSelector(Screen):

    def __init__(self, session, list):
        self.Hostslist = list
        self.openHost = ''
        self.LastFolderSelected= None
        self.rootPath = PluginPath+"/hosts/"
  
        self.skin  = LoadSkin("j00zekHostTreeSelector")
        
        Screen.__init__(self, session)
        self["info"] = Label()
        self["myPath"] = Label('')
        
        self["key_red"] = StaticText(_("Exit"))
        self["Cover"] = Pixmap()
        
        self["key_green"] = StaticText("")
            
        self["key_yellow"] = StaticText(_("Delete Category"))
        self["key_blue"] = StaticText(_("New Category"))
        self["info"].setText(PluginName + ' mod j00zek v.' + IPTV_VERSION) #title
        self.filelist = FileList(self.rootPath, HostsList = self.Hostslist)
        self["filelist"] = self.filelist
        self["actions"] = ActionMap(["j00zekHostTreeSelector"],
            {
                "selectHost": self.selectHost,
                "ExitHostSelector": self.ExitHostSelector,
                "lineUp": self.lineUp,
                "lineDown": self.lineDown,
                "pageUp": self.pageUp,
                "pageDown": self.pageDown,
                "newCategory": self.newCategory,
                "addHostToCategory": self.addHostToCategory,
                "deleteCategory": self.deleteCategory,
                "showConfig": self.showConfig,
                "showLocalMedia":  self.showLocalMedia,
            },-2)
        self.setTitle(PluginName + ' mod j00zek v.' + IPTV_VERSION)
        self.onShown.append(self.__LayoutFinish)

    def __LayoutFinish(self):
        if os_path.dirname(config.plugins.iptvplayer.j00zekLastSelectedHost.value) != '':
            self["filelist"].changeDir(os_path.dirname(config.plugins.iptvplayer.j00zekLastSelectedHost.value)+'/', os_path.basename(config.plugins.iptvplayer.j00zekLastSelectedHost.value))
            self.LastFolderSelected = self.__getCurrentDir()
            if not self.LastFolderSelected.endswith('/'): self.LastFolderSelected += '/'
            self["myPath"].setText(self.LastFolderSelected.replace(self.rootPath,''))
        
    def showConfig(self):
        self.close( (("config", "config")) )
      
    def showLocalMedia(self):
        self.close( (("localmedia", "localmedia")) )
      
    def addHostToCategory(self):
        selection = self["filelist"].getSelection()
        if selection[1] == False: # host selected
            myHostName=selection[0]
            hostPath=self.filelist.getCurrentDirectory()
            def CB(ret):
                if ret:
                    ManageHostsAndCategories(myHostName, ret[1])
                
            from Screens.ChoiceBox import ChoiceBox
            from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import ManageHostsAndCategories, GetHostsCategories
            self.session.openWithCallback(CB, ChoiceBox, title=_("Assign to/Remove from Category"), list = GetHostsCategories() )

        self["filelist"].refresh()
      
    def newCategory(self):
        selection = self["filelist"].getSelection()
        def catCB(callback = None):
            if callback is not None:
                printDEBUG('mkdir -p %s/%s' %(self.filelist.getCurrentDirectory(),callback) )
                os_system('mkdir -p %s/%s' %(self.filelist.getCurrentDirectory(),callback) )
                self["filelist"].refresh()
                return
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        self.session.openWithCallback(catCB, VirtualKeyBoard, title=_("Enter Category name"), text = _('new Category') )
            
        self["filelist"].refresh()
      
    def deleteCategory(self):
        selection = self["filelist"].getSelection()
        printDEBUG("Deleting %s" % selection[0])
        if selection[1] == True: # isDir
            os_system('rm -rf %s' % selection[0])
        else:
            os_system('rm -rf %s/%s' % (self.filelist.getCurrentDirectory(),selection[0]))
        self["filelist"].refresh()
        self.setInfo()
      
    def pageUp(self):
        if self["filelist"].getSelectedIndex() == 0:
            self["filelist"].moveToIndex(len(self["filelist"].getFileList())-1)
        else:
            self["filelist"].pageUp()
        self.setInfo()

    def pageDown(self):
        if self["filelist"].getSelectedIndex() == (len(self["filelist"].getFileList())-1):
            self["filelist"].moveToIndex(0)
        else:
            self["filelist"].pageDown()
        self.setInfo()

    def lineUp(self):
        if self["filelist"].getSelectedIndex() == 0:
            self["filelist"].moveToIndex(len(self["filelist"].getFileList())-1)
        else:
            self["filelist"].up()
        self.setInfo()

    def lineDown(self):
        if self["filelist"].getSelectedIndex() == (len(self["filelist"].getFileList())-1):
            self["filelist"].moveToIndex(0)
        else:
            self["filelist"].down()
        self.setInfo()

    def setInfo(self):
        selection = self["filelist"].getSelection()
        if selection[1] == True: # isDir
            self["key_green"].setText("")
            self["key_yellow"].setText(_("Delete Category"))
            self["Cover"].hide()
        else:
            self["key_yellow"].setText(_("Delete Host"))
            self["key_green"].setText(_("Assign to category"))
            HostPreview = '%s/icons/previews/%s.jpg' % (PluginPath,self.filelist.getFilename()[:-4])
            print HostPreview
            if os_path.exists(HostPreview):
                self["Cover"].instance.setScale(1)
                self["Cover"].instance.setPixmap(LoadPixmap(HostPreview))
                self["Cover"].show()
            else:
                self["Cover"].hide()
        return
  
    def __getCurrentDir(self):
        d = self.filelist.getCurrentDirectory()
        if d is None:
            d=""
        elif not d.endswith('/'):
            d +='/'
        return d
      
    def selectHost(self):
        selection = self["filelist"].getSelection()
        if selection[1] == True: # isDir
            if selection[0] is not None and self.filelist.getCurrentDirectory() is not None and \
                    len(selection[0]) > len(self.filelist.getCurrentDirectory()) or self.LastFolderSelected == None:
                self.LastFolderSelected = selection[0]
                self["filelist"].changeDir(selection[0], "FakeFolderName")
            else:
                print "Folder Down"
                self["filelist"].changeDir(selection[0], self.LastFolderSelected)
                
            self["myPath"].setText(self.__getCurrentDir().replace(self.rootPath,''))
        else:
            d = self.__getCurrentDir()
            f = self.filelist.getFilename()
            #printDEBUG("self.selectedFile>> " + d + f)
            self.openHost = f[4:].replace('.pyo','').replace('.pyc','')
            printDEBUG("self.selectedHost>> " + self.openHost)
            #self.SetDescriptionAndCover(self.openHost)
            for host in self.Hostslist:
                if self.openHost == host[1]:
                    config.plugins.iptvplayer.j00zekLastSelectedHost.value = d + f
                    self.close(host)
      
    def SetDescriptionAndCover(self, HostName):
        if HostName == '':
            self["Cover"].hide()
            return
        
        temp = HostName
        ### COVER ###
        if os_path.exists(temp + '.jpg'):
            self["Cover"].instance.setScale(1)
            self["Cover"].instance.setPixmap(LoadPixmap(os_path=temp + '.jpg'))
            self["Cover"].show()
        else:
            self["Cover"].hide()
            
    def ConvertChars(self, text):
        CharsTable={ '\xC2\xB1': '\xC4\x85','\xC2\xB6': '\xC5\x9b','\xC4\xBD': '\xC5\xba'}
        for i, j in CharsTable.iteritems():
            text = text.replace(i, j)
        return text

    def ExitHostSelector(self):
        self.close(None)
##################################################### treeSelector #####################################################

def FileEntryComponent(name, absolute = None, isDir = False):
    res = [ (absolute, isDir) ]
    #res.append((eListboxPythonMultiContent.TYPE_TEXT, 130, 1, 1020, 50, 0, RT_HALIGN_LEFT, name))
    if isDir:
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 40, 7, 1020, 40, 0, RT_HALIGN_LEFT, name))
        png = LoadPixmap(cached=True, path="%s/icons/folder.png" % PluginPath)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 5, 7, 25, 25, png))
    else:
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 170, 7, 1020, 40, 0, RT_HALIGN_LEFT, name))
        if os_path.exists("%s/icons/logos/%slogo.png" % (PluginPath,absolute[4:-4])):
            #print "%s/icons/logos/%slogo.png" % (PluginPath,absolute[4:-4])
            png = LoadPixmap("%s/icons/logos/%slogo.png" % (PluginPath,absolute[4:-4]))
        else:
            png = None
        if png is not None:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 1, 120, 40, png))
    return res

class FileList(MenuList):
    def __init__(self, directory, enableWrapAround = False, HostsList = []):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.Hostslist = HostsList
        self.mountpoints = []
        self.current_directory = None
        self.current_mountpoint = None
        self.showDirectories = True
        self.rootDirectory = directory
        self.showFiles = True
        # example: matching .nfi and .ts files: "^.*\.(nfi|ts)"
        self.inhibitDirs = []
        self.inhibitMounts = []

        self.refreshMountpoints()
        #if config.plugins.iptvplayer.j00zekLastSelectedHost.value != '':
        #    self.changeDir( os_path.dirname(config.plugins.iptvplayer.j00zekLastSelectedHost.value), os_path.basename(config.plugins.iptvplayer.j00zekLastSelectedHost.value) )
        self.changeDir(directory)
        self.l.setFont(0, gFont("Regular", 26)) #int(config.plugins.AdvancedFreePlayer.FileListFontSize.value)))
        self.l.setItemHeight(42)
        self.serviceHandler = eServiceCenter.getInstance()

    def refreshMountpoints(self):
        self.mountpoints = [os_path.join(p.mountpoint, "") for p in harddiskmanager.getMountedPartitions()]
        self.mountpoints.sort(reverse = True)

    def getMountpoint(self, file):
        file = os_path.join(os_path.realpath(file), "")
        for m in self.mountpoints:
            if file.startswith(m):
                return m
        return False

    def getMountpointLink(self, file):
        if os_path.realpath(file) == file:
            return self.getMountpoint(file)
        else:
            if file[-1] == "/":
                file = file[:-1]
            mp = self.getMountpoint(file)
            last = file
            file = os_path.dirname(file)
            while last != "/" and mp == self.getMountpoint(file):
                last = file
                file = os_path.dirname(file)
            return os_path.join(last, "")

    def getSelection(self):
        if self.l.getCurrentSelection() is None:
            return None
        return self.l.getCurrentSelection()[0]

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        if not l or l[0][1] == True:
            return None
        #else:
        #    return self.serviceHandler.info(l[0][0]).getEvent(l[0][0])

    def getFileList(self):
        return self.list

    def inParentDirs(self, dir, parents):
        dir = os_path.realpath(dir)
        for p in parents:
            if dir.startswith(p):
                return True
        return False

    def changeDir(self, directory, select = None):
        self.list = []

        # if we are just entering from the list of mount points:
        if self.current_directory is None:
            self.current_mountpoint = None
            
        self.current_directory = directory
        directories = []
        files = []

        if directory is None:
            files = [ ]
            directories = [ ]
        else:
            if fileExists(directory):
                try:
                    files = listdir(directory)
                except:
                    files = []
                files.sort(key=lambda s: s.lower())
                #files.sort()
                tmpfiles = files[:]
                for x in tmpfiles:
                    if os_path.isdir(directory + x):
                        directories.append(directory + x + "/")
                        files.remove(x)

        if directory is not None and self.showDirectories:
            if (directory != self.rootDirectory) and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(FileEntryComponent(name = "<" +_("Parent Category") + ">", absolute = '/'.join(directory.split('/')[:-2]) + '/', isDir = True))

        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    self.list.append(FileEntryComponent(name = name, absolute = x, isDir = True))

        if self.showFiles:
            for x in files:
                path = directory + x
                name = x

                if name.startswith('host') and (name.endswith('.pyo') or name.endswith('.pyc')):
                    name = name[4:-4]
                    for host in self.Hostslist:
                        if name == host[1]:
                            name = host[0]
                            self.list.append(FileEntryComponent(name = name, absolute = x , isDir = False))
                            break

        self.l.setList(self.list)

        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                #if isinstance(p, eServiceReference):
                #    p = p.getPath()
                if p == select:
                    self.moveToIndex(i)
                i += 1

    def getCurrentDirectory(self):
        return self.current_directory

    def canDescent(self):
        if self.getSelection() is None:
            return False
        return self.getSelection()[1]

    def descent(self):
        if self.getSelection() is None:
            return
        self.changeDir(self.getSelection()[0], select = self.current_directory)

    def getFilename(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        #if isinstance(x, eServiceReference):
        #    x = x.getPath()
        return x

    def getServiceRef(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        #if isinstance(x, eServiceReference):
        #    return x
        return None

    def execBegin(self):
        harddiskmanager.on_partition_list_change.append(self.partitionListChanged)

    def execEnd(self):
        harddiskmanager.on_partition_list_change.remove(self.partitionListChanged)

    def refresh(self):
        self.changeDir(self.current_directory, self.getFilename())

    def partitionListChanged(self, action, device):
        self.refreshMountpoints()
        if self.current_directory is None:
            self.refresh()
