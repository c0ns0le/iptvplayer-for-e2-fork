# @j00zek 18.11.2015
#This script downloads IPTVPlayer from github and installs all necessary components
#
install_package(){
if `opkg list_installed|grep -q $1`;then
	echo "$1 already installed"
else
	opkg install $1 1>/dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo "$1 installed correctly"
		echo "$1 installed correctly">/tmp/IPTV-opkg.log
	else
                echo "$1 NOT available in opkg and NOT installed properly :("
	fi
fi
}
echo "Installing necessary packages..."
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
install_package librtmp0
install_package gst-plugins-good
install_package gst-plugins-bad-cdxaparse
install_package gst-plugins-bad-vcdsrc 

curl --help 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo
  echo "Required program 'curl' is not available. Please install it manually."
  exit 0
fi

echo "Checking internet connection..."
ping -c 1 github.com 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo "github server unavailable, update impossible!!!"
  exit 0
fi

echo "Downloading latest plugin version..."
curl -kLs https://api.github.com/repos/j00zek/iptvplayer-for-e2-fork/tarball/master -o /tmp/iptvp.tar.gz
if [ $? -gt 0 ]; then
  echo "Archive downloaded improperly"
  exit 0
fi

if [ ! -e /tmp/iptvp.tar.gz ]; then
  echo "No archive downloaded, check your curl version"
  exit 0
fi

echo "Unpacking new version..."
#cd /tmp
tar -zxf /tmp/iptvp.tar.gz -C /tmp
if [ $? -gt 0 ]; then
  echo "Archive unpacked improperly"
  exit 0
fi

if [ ! -e /tmp/j00zek-iptvplayer-for-e2-fork-* ]; then
  echo "Archive downloaded improperly"
  exit 0
fi
rm -rf /tmp/iptvp.tar.gz


if [ -e /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer ];then
 echo "Cleaning existing folder"
 rm -rf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/*
else
 echo "Creating IPTVPlayer folder"
 mkdir -p /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/
fi

echo "Installing new version..."
if [ -e /DuckboxDisk ]; then
  echo
  echo "github is always up-2-date, no sync required"
  exit 0
else
  rm -rf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/j00zek-FreePlayer-* 2>/dev/null
  cp -a /tmp/j00zek-iptvplayer-for-e2-fork-*/IPTVPlayer/* /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/
  rm -rf /tmp/j00zek-iptvplayer-for-e2-fork-* 2>/dev/null
  echo
  echo "Success: Restart GUI manually to use new plugin version"
fi

exit 0
