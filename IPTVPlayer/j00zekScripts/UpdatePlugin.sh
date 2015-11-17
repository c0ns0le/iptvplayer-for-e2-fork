#
if `grep -q 'config.plugins.iptvplayer.debugprint=' < /etc/enigma2/settings`;then
  UpdateType='dev'
elif `grep -q 'config.plugins.iptvplayer.debugprint=' < /usr/local/e2/etc/enigma2/settings`;then
  UpdateType='dev'
else
  UpdateType='public'
fi
if [ -z "$1" ];then
  CurrentPublic='version-unknown'
else
  CurrentPublic=$1
fi

[ -e /tmp/iptvp.tar.gz ] && rm -rf /tmp/iptvp.tar.gz
rm -rf /tmp/j00zek-iptvplayer-for-e2-fork-* 2>/dev/null
sudo rm -rf /tmp/j00zek-iptvplayer-for-e2-fork-* 2>/dev/null

curl --help 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo "_(Required program 'curl' is not installed. Trying to install it via OPKG.)"
  echo
  opkg install curl 

  curl --help 1>/dev/null 2>%1
  if [ $? -gt 0 ]; then
    echo
    echo "_(Required program 'curl' is not available. Please install it first manually.)"
    exit 0
  fi
fi

echo "_(Checking installation mode...)"
if `opkg list-installed 2>/dev/null | tr '[:upper:]' '[:lower:]'| grep -q 'iptvplayer'`;then
  echo "_(IPTVPlayer controlled by OPKG. Please use it for updates.)"
  exit 0
fi

echo "_(Update type:) $UpdateType"

echo "_(Checking internet connection...)"
ping -c 1 github.com 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo "_(github server unavailable, update impossible!!!)"
  exit 0
fi

if [ "$UpdateType" == "public" ]; then
  echo "_(Checking web version...)"
  GITversion=`curl -kLs https://raw.githubusercontent.com/j00zek/iptvplayer-for-e2-fork/master/IPTVPlayer/version.py|grep IPTV_VERSION|cut -d '"' -f2`
  echo "_(Version installed:) $CurrentPublic"
  echo "_(Version available:) $GITversion"
  if [ -z "$GITversion" ]; then
    echo "_(Error checking web version)"
    exit 0
  elif [ "$GITversion" == "$CurrentPublic" ]; then
    echo "_(Latest version already installed. Press OK to close the window)"
    exit 0
  else
    echo "_(Vew version available on the web)"
  fi
fi

echo "_(Downloading latest plugin version...)"
curl -kLs https://api.github.com/repos/j00zek/iptvplayer-for-e2-fork/tarball/master -o /tmp/iptvp.tar.gz
if [ $? -gt 0 ]; then
  echo "_(Archive downloaded improperly"
  exit 0
fi

if [ ! -e /tmp/iptvp.tar.gz ]; then
  echo "_(No archive downloaded, check your curl version)"
  exit 0
fi

echo "_(Unpacking new version...)"
#cd /tmp
tar -zxf /tmp/iptvp.tar.gz -C /tmp
if [ $? -gt 0 ]; then
  echo "_(Archive unpacked improperly)"
  exit 0
fi

if [ ! -e /tmp/j00zek-iptvplayer-for-e2-fork-* ]; then
  echo "Archive downloaded improperly)"
  exit 0
fi
rm -rf /tmp/iptvp.tar.gz

version=`ls /tmp/ | grep j00zek-iptvplayer-for-e2-fork-`
if [ -f /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/$version ];then
  echo "_(Latest version already installed. Press OK to exit.)"
  exit 0
fi

echo "_(Installing new version...)"
if [ -e /DuckboxDisk ]; then
  echo
  echo "_(github is always up-2-date, no sync required)"
else
  rm -rf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/j00zek-FreePlayer-* 2>/dev/null
  touch /tmp/$version/IPTVPlayer/$version 2>/dev/null
  cp -a /tmp/$version/IPTVPlayer/* /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/
  #rm -rf /tmp/j00zek-iptvplayer-for-e2-fork-* 2>/dev/null
  echo
  echo "_(Success: Restart GUI manually to use new plugin version)"
fi

exit 0
