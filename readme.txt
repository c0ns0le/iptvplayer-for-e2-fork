This is fork of https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2.gitlab project
All credits goes to its author(s)

Planned changes:
- change the update mechanism to not interfere with main project
- change reporting mechanism to not interfere with main project, if needed
- make plugin platform independent,
  - use standard binaries installable from opkg (e.g. full wget, rtmpdump)
  - detect platform based on standard e2 definitions, special binary is not needed
  - browse directories using standard e2 mechanism, lsdir binary is not needed
- make the plugin skinable
- implement transcoding on highend tuners, possibly limit a need for special external players

NOTE: All original licenses applies to it too.