This is fork of https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2.gitlab project
All credits goes to its author(s)

Changes:
- The update mechanism has been CHANGED to not interfere with main project.
- lsdir binary is not reuired anymore to browse directories, Plugin will use standard mechanism, if lsdir not existing for specific platform.
- arm platform has been added, main binaries compiled, new resource server for arm initiated

Planned changes:
- make the plugin skinable - Patially finished, all sk
- detect platform based on standard e2 definitions, special binary is not needed
- use standard binaries installable from opkg (e.g. full wget, rtmpdump) 
- change reporting mechanism to not interfere with main project, if needed
- implement transcoding on highend tuners, possibly limit a need for special external players
