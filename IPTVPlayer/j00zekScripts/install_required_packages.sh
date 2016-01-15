# @j00zek 14.01.2016
#This script installs required packages, it is run once after upgrade
#
[ -z "$1" ] && silent=0 || silent=1

if `grep -q 'osd.language=pl_PL' </etc/enigma2/settings`; then
  installedCorrectly="zainstalowany poprawnie"
  installingPackages="Instalacja niezbędnych pakietów..."
else
  installedCorrectly="installed correctly"
  installingPackages="Installing necessary packages..."
fi
install_package(){
if ! `opkg list_installed|grep -q "$1 "`;then
  opkg install $1 1>/dev/null 2>&1
  if [ $? -eq 0 ]; then
    [ $silent -eq 0 ] echo "$1 $installedCorrectly"
    echo "$1 installed correctly">>/tmp/IPTV-opkg.log
  else
    echo "$1 NOT available in opkg and NOT installed properly">>/tmp/IPTV-opkg.log
  fi
fi
}
echo "$installingPackages"
echo "$installingPackages">/tmp/IPTV-opkg.log
install_package curl
install_package gst-plugins-bad-rtmp
install_package gst-plugins-good
install_package gst-plugins-bad-cdxaparse
install_package gst-plugins-bad-vcdsrc 
install_package libidn11
install_package librtmp1
install_package librtmp-bin
install_package python-compression
install_package python-html
install_package python-image
install_package python-imaging
install_package python-json
install_package python-mechanize
install_package python-mutagen
install_package python-robotparser
install_package python-shell
install_package python-simplejson
install_package python-textutils

#gos specific
if [ -f /etc/init.d/graterlia_init ]; then
  install_package gst-plugins-bad-gos
  install_package gst-plugins-good-gos
  install_package enigma2-multiframework
fi
rm -f $0
