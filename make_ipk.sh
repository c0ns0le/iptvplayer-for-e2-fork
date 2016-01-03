#!/bin/sh
sciezkaIPK='/tmp/ipk'
PluginName='IPTVPlayer'
sciezkaPLUGIN="$sciezkaIPK/usr/lib/enigma2/python/Plugins/Extensions/$PluginName"
myDir=`dirname $0`

wersja=`cat $myDir/jVersion.txt`
[ $? -gt 0 ] && echo 'Błąd' && exit 0
data=`date '+%d-%m-%Y'`

rm -rf $sciezkaIPK 2>/dev/null
#copy source files into structure
mkdir -p $sciezkaPLUGIN
echo $myDir/$PluginName/
cp -rf $myDir/$PluginName/* $sciezkaPLUGIN
[ $? -gt 0 ] && echo 'Błąd' && exit 0
cd $sciezkaPLUGIN
find . -name "*.pyc" -type f -delete
find . -name "*.pyo" -type f -delete
#create control files
mkdir -p $sciezkaIPK
mkdir -p $sciezkaIPK/control
cd $sciezkaIPK/control
echo "">./conffiles
echo "Package: j00zeks-$PluginName">./control
echo "Priority: optional">>./control
echo "Section: utils">>./control
echo "Depends:">>./control
echo "Description: j00zek's $PluginName">>./control
echo "Maintainer: j00zek">>./control
echo "Source: N/A">>./control
echo "Version: $wersja">>./control
echo "Architecture: all">>./control
#
echo "2.0">../debian_binary
##############################################
# create data.tar
#
# exclude control, conffiles, this script (if it exists), 
# and anything else prudent to ignore
#
cd $sciezkaIPK/control
tar -cvf ../control.tar ./*
cd $sciezkaIPK
gzip < ./control.tar > ./control.tar.gz
rm -f ./control.tar
#cd /
tar -cvf $sciezkaIPK/data.tar ./usr/lib/enigma2/python/Plugins/Extensions/$PluginName/*
#cd $sciezkaIPK
gzip < ./data.tar > ./data.tar.gz
rm -f ./data.tar
##############################################
# create PACKAGE.tar
#
tar -cf ./packagetemp.tar ./control.tar.gz ./data.tar.gz ./debian_binary
if [ $? != 0 ] || [ ! -f ./packagetemp.tar ]; then 
	echo " ERROR: creation of packagetemp.tar failed!"
	exit 2	
fi
##############################################
# finally gzip the result to PACKAGE.ipk
#
gzip < ./packagetemp.tar > ./j00zeks-$PluginName.ipk
if [ $? != 0 ] || [ ! -f $1 ]; then 
	echo " ERROR: creation of $1 failed!"
	exit 2	
else
rm -f ./packagetemp.tar
rm -f ./data.tar.gz
rm -f ./control.tar.gz
fi
#create package file
cp -f ./control/control  ./j00zeks-$PluginName-package
echo `stat ./j00zeks-$PluginName.ipk|grep Size:|sed 's/^.*\(Size: [1234567890]*\).*/\1/'` >>./j00zeks-$PluginName-package
echo "MD5Sum: `md5sum /tmp/ipk/j00zeks-$PluginName.ipk|cut -d ' ' -f1`" >>./j00zeks-$PluginName-package
echo " Done. Created: $1"
mv -f ./j00zeks-$PluginName* /DuckboxDisk/j00zek-github/IPKs-storage/opkg-j00zka/
