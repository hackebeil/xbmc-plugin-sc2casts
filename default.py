import sys, xbmcplugin, xbmcaddon, sc2casts  

__version__ = "0.6"
__plugin__ = "SC2Casts-" + __version__
__author__ = "hackebeil"
__settings__ = xbmcaddon.Addon(id='plugin.video.sc2casts')
__language__ = __settings__.getLocalizedString

           
SC2Casts = sc2casts.SC2Casts()

if (not sys.argv[2]):
    SC2Casts.root()
else:
    print __plugin__

    params = SC2Casts.getParams(sys.argv[2])
    get = params.get
    if get("action"):
        SC2Casts.action(params)
        
action = SC2Casts.getParams(sys.argv[2])
if action != 'playTwitch' and action != 'playGames' and action != 'toggleWatched':
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
