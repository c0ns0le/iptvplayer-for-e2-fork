
myDir=`dirname $0`

if [ ! -d ~/iptvplayer-GitLab-master-version ];then
  echo 'Cloning...'
  git clone https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2.git ~/iptvplayer-GitLab-master-version
else
  echo 'Syncing GitLab...'
  cd ~/iptvplayer-GitLab-master-version
  git pull
fi
if [ ! -d ~/iptvplayerXXX-GitLab-master-version ];then
  echo 'Cloning XXX host...'
  git clone https://gitlab.com/iptv-host-xxx/iptv-host-xxx.git ~/iptvplayerXXX-GitLab-master-version
else
  echo 'Syncing GitLab XXX host...'
  cd ~/iptvplayerXXX-GitLab-master-version
  git pull
fi

echo 'Syncing Github...'
rm -rf $myDir/IPTVPlayer/hosts/*
cp -a ~/iptvplayer-GitLab-master-version/IPTVPlayer $myDir/
cp -a ~/iptvplayer-GitLab-master-version/setup_translate.py $myDir/
cp -a ~/iptvplayer-GitLab-master-version/setup.py $myDir/
rm -rf $myDir/IPTVPlayer/bin/armv7
ln -sf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/bin/arm $myDir/IPTVPlayer/bin/armv7
cd $myDir

#change numbering
sed -i 's/\(IPTV_VERSION="\)/\1j/' ./IPTVPlayer/version.py
cat ./IPTVPlayer/version.py|grep IPTV_VERSION|grep -o "[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]" > ./jVersion.txt

cp -af ~/iptvplayerXXX-GitLab-master-version/IPTVPlayer/* $myDir/IPTVPlayer/
#sed -i "s/\(self.exteplayer3Version = {'sh4': [0-9]*, 'mipsel': [0-9]*\), 'armv7': 11}/\1}/" ./IPTVPlayer/setup/iptvsetupimpl.py
#rm -rf $myDir/IPTVPlayer/iptvupdate/custom/xxx.sh

#>>>>>patching
patch -p1 < ./iptvplayer-fork.patch
msgfmt $myDir/IPTVPlayer/locale/pl/LC_MESSAGES/IPTVPlayer.po -o $myDir/IPTVPlayer/locale/pl/LC_MESSAGES/IPTVPlayer.mo
mv -f $myDir/IPTVPlayer/hosts/hostipla_blocked_due_privacy_policy.py $myDir/IPTVPlayer/hosts/hostipla.py
sed -i "s/return 'Ipla'/return 'Ipla-brak licencji'/" $myDir/IPTVPlayer/hosts/hostipla.py
#dodatkowe hosty
cp -R $myDir/Hosts2Include/* $myDir/IPTVPlayer/
#kategorie
mkdir -p $myDir/IPTVPlayer/hosts/Polskie
lista='hostiplex.py hostonetvod.py hosttvn24.py hosttvnvod.py hostwptv.py '
for host in $lista
do
[ -e $myDir/IPTVPlayer/hosts/$host ] && ln -sf $myDir/IPTVPlayer/hosts/$host $myDir/IPTVPlayer/hosts/Polskie/$host
done
