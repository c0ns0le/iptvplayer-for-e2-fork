myDir=`dirname $0`
cd $myDir
#[ -e neutrino-mp-next/src/ ] && diff -Naur neutrino-mp-next.org/src/ neutrino-mp-next/src/ -X ../exclude.pats >../jzk/GOS-plugins/GOS-neutrino/patches/neutrino-mp-next.patch
#diff -Naur neutrino-mp-cst-next.org/src/ neutrino-mp-cst-next/src/ -X ../exclude.pats >../jzk/GOS-plugins/GOS-neutrino/patches/neutrino-mp-cst-next.patch
diff -Naur ~/iptvplayer-GitLab-master-version/IPTVPlayer/ ./IPTVPlayer/ -X ./exclude.pats >./iptvplayer-fork.patch
