#!/bin/sh
myDir=`dirname $0`
PluginName='IPTVPlayer'
PluginPath="/usr/lib/enigma2/python/Plugins/Extensions/$PluginName"
PluginGITpath="$myDir/$PluginName"
wersja=`cat $myDir/jVersion.txt`

$myDir/../IPKs-storage/build_ipk_package.sh "$PluginName" "$PluginPath" "$PluginGITpath" "$wersja" "enigma2-plugin-extensions"

if ! `grep -q "$myDir/build_ipk.sh" <$myDir/../IPKs-storage/build_ipk_packages.sh`;then
  echo "$myDir/build_ipk.sh">>$myDir/../IPKs-storage/build_ipk_packages.sh
fi
exit 0