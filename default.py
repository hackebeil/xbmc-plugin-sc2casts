import sys, xbmcplugin 
from sc2casts import SC2Casts, NavigationConstants

SC2Casts = SC2Casts()

if (not sys.argv[2]):
    #We are being called for the first time today.
    #Go to main menu.
    SC2Casts.root()
else:
    #Extract call parameters and do something based upon them.
    params = SC2Casts.getParams(sys.argv[2])
    get = params.get
    if get(NavigationConstants.ACTION):
        SC2Casts.action(params)

#Determine if endOfDirectory command shall be called. 
#For some context menu functions this is not the case.
action = SC2Casts.getParams(sys.argv[2])
if action != NavigationConstants.PLAY_TWITCH and action != NavigationConstants.PLAY_GAMES and action != NavigationConstants.TOGGLE_WATCHED:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
