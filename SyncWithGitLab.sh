
myDir=`dirname $0`

if [ ! -d ~/iptvplayer-GitLab-master-version ];then
  echo 'Cloning...'
  git clone https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2.git ~/iptvplayer-GitLab-master-version
else
  echo 'Syncing GitLab...'
  cd ~/iptvplayer-GitLab-master-version
  git pull
fi
echo 'Syncing Github...'
cp -a ~/iptvplayer-GitLab-master-version/IPTVPlayer $myDir/
cp -a ~/iptvplayer-GitLab-master-version/setup_translate.py $myDir/
cp -a ~/iptvplayer-GitLab-master-version/setup.py $myDir/
cd $myDir
patch -p1 < ./iptvplayer-fork.patch
