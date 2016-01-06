# @j00zek 15.12.2015
#This script downloads IPTVPlayer from github and installs all necessary components
#
if `grep -q 'osd.language=pl_PL' </etc/enigma2/settings`; then
  isInstalled="jest już zainstalowany"
  installedCorrectly="zainstalowany poprawnie"
  installingPackages="Instalacja niezbędnych pakietów..."
  curlError="Wymagany program 'curl' jest niezainstalowany. Zainstaluj go ręcznie."
  inetCheck="Sprawdzanie połączenia..."
  githubError="Serwer github jest niedostępny, instalacja niemożliwa!!!"
  download="Pobieranie ostatniej wersji wtyczki..."
  downloadError="Archiwum pobrane niepoprawnie"
  curlIncorrect="Brak archiwum, sprawdź swoją wersję programu curl"
  unpacking="Wypakowywanie archiwum..."
  unpackError="Archiwum wypakowane niepoprawnie"
  archiveIncorrect="Archiwum pobrane niepoprawnie"
  cleaning="Czyszczenie katalogu IPTVPlayer-a"
  creating="Tworzenie katalogu IPTVPlayer"
  installing="Instalacja nowej wersji..."
  success="Sukces: Zrestartuj GUI ręcznie, aby aktywować nową wersję wtyczki"
else
  isInstalled="already installed"
  installedCorrectly="installed correctly"
  installingPackages="Installing necessary packages..."
  curlError="Required program 'curl' is not available. Please install it manually."
  inetCheck="Checking internet connection..."
  githubError="github server unavailable, update impossible!!!"
  download="Downloading latest plugin version..."
  downloadError="Archive downloaded improperly"
  curlIncorrect="No archive downloaded, check your curl version"
  unpacking="Unpacking new version..."
  unpackError="Archive unpacked improperly"
  archiveIncorrect="Archive downloaded improperly"
  cleaning="Cleaning existing folder"
  creating="Creating IPTVPlayer folder"
  installing="Installing new version..."
  success="Success: Restart GUI manually to use new plugin version"
fi
install_package(){
if `opkg list_installed|grep -q "$1 "`;then
  echo "$1 $isInstalled"
else
  opkg install $1 1>/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "$1 $installedCorrectly"
    echo "$1 installed correctly">>/tmp/IPTV-opkg.log
  else
    echo "$1 NOT available in opkg and NOT installed properly">>/tmp/IPTV-opkg.log
  fi
fi
}
echo "$installingPackages"
echo "$installingPackages">/tmp/IPTV-opkg.log
install_package curl
install_package libidn11
install_package python-compression
install_package python-json
install_package python-simplejson
install_package python-html
install_package python-image
install_package python-imaging
install_package python-mechanize
install_package python-mutagen
install_package python-robotparser
install_package python-shell
install_package gst-plugins-bad-rtmp
install_package librtmp1
install_package librtmp-bin 
install_package gst-plugins-good
install_package gst-plugins-bad-cdxaparse
install_package gst-plugins-bad-vcdsrc 
#gos specific
install_package gst-plugins-bad-gos
install_package gst-plugins-good-gos
install_package enigma2-multiframework

curl --help 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo
  echo "$curlError"
  exit 0
fi

echo "$inetCheck"
ping -c 1 github.com 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo "$githubError"
  exit 0
fi

echo "$download"
curl -kLs https://api.github.com/repos/j00zek/iptvplayer-for-e2-fork/tarball/master -o /tmp/iptvp.tar.gz
if [ $? -gt 0 ]; then
  echo "$downloadError"
  exit 0
fi

if [ ! -e /tmp/iptvp.tar.gz ]; then
  echo "$curlIncorrect"
  exit 0
fi

echo "$unpacking"
#cd /tmp
tar -zxf /tmp/iptvp.tar.gz -C /tmp
if [ $? -gt 0 ]; then
  echo "$unpackError"
  exit 0
fi

if [ ! -e /tmp/j00zek-iptvplayer-for-e2-fork-* ]; then
  echo "$archiveIncorrect"
  exit 0
fi
rm -rf /tmp/iptvp.tar.gz


if [ -e /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer ];then
 echo "$cleaning"
 rm -rf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/*
else
 echo "$creating"
 mkdir -p /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/
fi

echo "$installing"
if [ -e /DuckboxDisk ]; then
  echo
  echo "github is always up-2-date, no sync required"
  exit 0
else
  rm -rf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/j00zek-FreePlayer-* 2>/dev/null
  cp -a /tmp/j00zek-iptvplayer-for-e2-fork-*/IPTVPlayer/* /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/
  rm -rf /tmp/j00zek-iptvplayer-for-e2-fork-* 2>/dev/null
  echo
  echo "$success"
fi

exit 0
