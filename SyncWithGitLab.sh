
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
cp -a ~/iptvplayer-GitLab-master-version/IPTVPlayer $myDir/
cp -a ~/iptvplayer-GitLab-master-version/setup_translate.py $myDir/
cp -a ~/iptvplayer-GitLab-master-version/setup.py $myDir/
rm -rf $myDir/IPTVPlayer/bin/armv7
cd $myDir

#change numbering
sed -i 's/\(IPTV_VERSION="\)/\1j/' ./IPTVPlayer/version.py

mv -f $myDir/IPTVPlayer/hosts/hostipla_blocked_due_privacy_policy.py $myDir/IPTVPlayer/hosts/hostipla.py
cp -af ~/iptvplayerXXX-GitLab-master-version/IPTVPlayer/* $myDir/IPTVPlayer/
rm -rf $myDir//IPTVPlayer/iptvupdate/custom/xxx.sh

patch -p1 < ./iptvplayer-fork.patch
