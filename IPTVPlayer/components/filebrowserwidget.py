# -*- coding: utf-8 -*-
#
#  Directory selector
#
#  $Id$
#
# 
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, mkdir, IsValidFileName
###################################################
 
###################################################
# FOREIGN import
###################################################
from enigma import getDesktop

from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Components.FileList import FileList
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.ActionMap import ActionMap
from Tools.BoundFunction import boundFunction
from os import path as os_path
###################################################
 
class DirectorySelectorWidget(Screen):
    from Plugins.Extensions.IPTVPlayer.j00zekScripts.j00zekToolSet import LoadSkin
    skin=LoadSkin('DirectorySelectorWidget')
    
    def __init__(self, session, currDir, title="Directory browser"):
        printDBG("DirectorySelectorWidget.__init__ -------------------------------")
        Screen.__init__(self, session)
        # for the skin: first try MediaPlayerDirectoryBrowser, then FileBrowser, this allows individual skinning
        #self.skinName = ["MediaPlayerDirectoryBrowser", "FileBrowser" ]
        self["key_red"]    = Label(_("Anuluj"))
        #self["key_yellow"] = Label(_("Odśwież"))
        self["key_blue"]   = Label(_("New folder"))
        self["key_green"]  = Label(_("Apply"))
        self["curr_dir"]   = Label(_(" "))
        self.filelist      = FileList(directory=currDir, matchingPattern="", showFiles=False)
        self["filelist"]   = self.filelist
        self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green" : self.use,
                "red"   : self.exit,
                "yellow": self.refresh,
                "blue"  : self.newDir,
                "ok"    : self.ok,
                "cancel": self.exit
            })
        self.title = title
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.__onClose)

    def __del__(self):
        printDBG("DirectorySelectorWidget.__del__ -------------------------------")

    def __onClose(self):
        printDBG("DirectorySelectorWidget.__onClose -----------------------------")
        self.onClose.remove(self.__onClose)
        self.onLayoutFinish.remove(self.layoutFinished)

    def layoutFinished(self):
        printDBG("DirectorySelectorWidget.layoutFinished -------------------------------")
        self.setTitle(_(self.title))
        self.currDirChanged()

    def currDirChanged(self):
        self["curr_dir"].setText(_(self.getCurrentDirectory()))
        
    def getCurrentDirectory(self):
        currDir = self["filelist"].getCurrentDirectory()
        if currDir and os_path.isdir( currDir ):
            return currDir
        else:
            return "/"

    def use(self):
        self.close( self.getCurrentDirectory() )

    def exit(self):
        self.close(None)

    def ok(self):
        if self.filelist.canDescent():
            self.filelist.descent()
        self.currDirChanged()

    def refresh(self):
        self["filelist"].refresh()

    def newDir(self):
        currDir = self["filelist"].getCurrentDirectory()
        if currDir and os_path.isdir( currDir ):
            self.session.openWithCallback(boundFunction(self.enterPatternCallBack, currDir), VirtualKeyBoard, title = (_("Enter name")), text = "")

    def enterPatternCallBack(self, currDir, newDirName=None):
        if None != currDir and newDirName != None:
            sts = False
            if IsValidFileName(newDirName):
                sts,msg = mkdir(os_path.join(currDir, newDirName))
            else:
                msg = _("Invalid name.")
            if sts:
                self.refresh()
            else:
                self.session.open(MessageBox, msg, type = MessageBox.TYPE_INFO, timeout=5)