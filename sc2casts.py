import re
import sys
import urllib
import urllib2
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import sqlite3
import os
from string import split
from bs4 import BeautifulSoup

class SC2Casts:
   
    #--- Constants
    SC2CASTS_URL = 'http://sc2casts.com'
    LIQUID_URL = 'http://www.teamliquid.net'
    VIDEO_URL = 'http://www.youtube.com'
    YOUTUBE_PLUGIN_URL = 'plugin://plugin.video.youtube'
    SELF_PLUGIN_URL = 'plugin://plugin.video.sc2casts'
    DB_FILE = 'watched.db'
    
    #--- Members
    addon = xbmcaddon.Addon()
    language = addon.getLocalizedString
    setting = addon.getSetting
    
    def action(self, params):
        '''Checks the action parameter to determine to which method the work needs to be delegated.'''
        get = params.get
        action = get(NavigationConstants.ACTION)
        #menu functions
        if (action == NavigationConstants.ROOT_TOP):
            self.rootTop()
        if (action == NavigationConstants.ROOT_BROWSE):
            self.rootBrowse()
        if (action == NavigationConstants.SHOW_LIVE):
            self.showLive()

        #browse functions
        if (action == NavigationConstants.BROWSE_EVENT_TYPE):
            self.browseEventType(params)
        if (action == NavigationConstants.BROWSE_CASTER_TYPE):
            self.browseCasterType(params)
        if (action == NavigationConstants.BROWSE_PLAYERS_TYPE):
            self.browsePlayerType(params)
        if (action == NavigationConstants.BROWSE_EVENTS_PROMINENT):
            self.browseEvents(params, False)
        if (action == NavigationConstants.BROWSE_EVENTS_ALL):
            self.browseEvents(params, True)
        if (action == NavigationConstants.BROWSE_EVENT_ROUNDS):
            self.browseEventRounds(params)
        if (action == NavigationConstants.BROWSE_CASTERS_PROMINENT):
            self.browseCasters(params, False)
        if (action == NavigationConstants.BROWSE_CASTERS_ALL):
            self.browseCasters(params, True)
        if (action == NavigationConstants.BROWSE_PLAYERS_NOTABLE):
            self.browsePlayers(params, False)
        if (action == NavigationConstants.BROWSE_PLAYERS_ALL):
            self.browsePlayers(params, True)
        if (action == NavigationConstants.BROWSE_MATCHUPS):
            self.browseMatchups()

        #function for showing series/games
        if (action == NavigationConstants.SHOW_TITLES
            or action == NavigationConstants.SHOW_TITLES_SEARCH):
            self.showTitles(params)
        if (action == NavigationConstants.SHOW_GAMES):
            self.showGames(params,False)
        
        #special functions
        if (action == NavigationConstants.PLAY_DUMMY):
            self.playDummy()
        if (action == NavigationConstants.PLAY_GAMES):
            self.showGames(params, True)
        if (action == NavigationConstants.PLAY_TWITCH):
            self.playVideo(get(NavigationConstants.VIDEO_ID), get(NavigationConstants.START))
        if (action == NavigationConstants.FIND_PLAYER):
            self.findPlayer(get(NavigationConstants.URL), get(NavigationConstants.PLAYER_NO))
        if (action == NavigationConstants.TOGGLE_WATCHED):
            self.toogleWatched(get(NavigationConstants.URL))
        if (action == NavigationConstants.RESET_WATCHED):
            self.resetWatched()        

    #--- Main menu functions 
    def root(self):
        '''Lists the root categories.'''
        self.addCategory(self.language(31000),
                         self.getCastsURL('/all'),
                         NavigationConstants.SHOW_TITLES)
        self.addCategory(self.language(31002), '', NavigationConstants.ROOT_BROWSE)
        self.addCategory(self.language(31001), '', NavigationConstants.ROOT_TOP)
        self.addCategory(self.language(31003), '', NavigationConstants.SHOW_TITLES_SEARCH)
        self.addCategory(self.language(31018), '', NavigationConstants.SHOW_LIVE)

    def rootTop(self):
        '''Lists all top video categories.'''
        self.addCategory(self.language(31004),
                         self.getCastsURL('/top/index.php?all'),
                         NavigationConstants.SHOW_TITLES)
        self.addCategory(self.language(31005),
                         self.getCastsURL('/top/index.php?month'),
                         NavigationConstants.SHOW_TITLES)
        self.addCategory(self.language(31006),
                         self.getCastsURL('/top/index.php?week'),
                         NavigationConstants.SHOW_TITLES)
        self.addCategory(self.language(31007),
                         self.getCastsURL('/top/index.php'),
                         NavigationConstants.SHOW_TITLES)

    def rootBrowse(self):
        '''Lists all browse categories.'''
        self.addCategory(self.language(31008),
                         self.getCastsURL('/browse/index.php'),
                         NavigationConstants.BROWSE_EVENT_TYPE)
        self.addCategory(self.language(31009), '', NavigationConstants.BROWSE_MATCHUPS)
        self.addCategory(self.language(31015), self.getCastsURL('/browse/index.php'), NavigationConstants.BROWSE_PLAYERS_TYPE)
        self.addCategory(self.language(31010),
                         self.getCastsURL('/browse/index.php'),
                         NavigationConstants.BROWSE_CASTER_TYPE)
    
    #--- Browse menu functions   
    def browseMatchups(self):
        '''Lists all matchup categories.'''
        self.addCategory('PvZ', self.getCastsURL('/matchups-PvZ'),
                        NavigationConstants.SHOW_TITLES)
        self.addCategory('PvT', self.getCastsURL('/matchups-PvT'),
                        NavigationConstants.SHOW_TITLES)
        self.addCategory('TvZ', self.getCastsURL('/matchups-TvZ'),
                        NavigationConstants.SHOW_TITLES)
        self.addCategory('PvP', self.getCastsURL('/matchups-PvP'),
                         NavigationConstants.SHOW_TITLES)
        self.addCategory('TvT', self.getCastsURL('/matchups-TvT'),
                        NavigationConstants.SHOW_TITLES)
        self.addCategory('ZvZ', self.getCastsURL('/matchups-ZvZ'),
                        NavigationConstants.SHOW_TITLES)   
     
    def browseEventType(self, params):
        '''Allows the user to choose between a long list of all events or only well known ones.'''
        self.addCategory(self.language(31011), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_EVENTS_PROMINENT)
        self.addCategory(self.language(31012), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_EVENTS_ALL)

    def browseCasterType(self, params):
        '''Allows the user to choose between a long list of all casters or only well known ones.'''
        self.addCategory(self.language(31013), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_CASTERS_PROMINENT)
        self.addCategory(self.language(31014), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_CASTERS_ALL)
    
    def browsePlayerType(self, params):
        '''Allows the user to choose between a long list of all players or only well known ones.'''
        self.addCategory(self.language(31016), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_PLAYERS_NOTABLE)
        self.addCategory(self.language(31017), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_PLAYERS_ALL)
    
    #--- Browse functions   
    def browseEvents(self, params, allEvents):
        '''Extracts and displays all/top events from the main "browse" page of the SC2Casts site.'''
        get = params.get
        link = self.getRequest(get(NavigationConstants.URL))
        soup = self.getSoup(link)
        allEventsMarker = soup.find('span', text='All Events')
        rgex = re.compile('/event')
        if allEvents:
            eventList = allEventsMarker.find_all_next('a', href=rgex)
        else:
            eventList = allEventsMarker.find_all_previous('a', href=rgex)
        theRange = range(len(eventList))
        if not allEvents:
            theRange = reversed(theRange)
        for i in theRange:
            self.addCategory(eventList[i].string,
                             self.getCastsURL(eventList[i].get('href')),
                             NavigationConstants.BROWSE_EVENT_ROUNDS, len(eventList))
    
    def browseEventRounds(self, params = {}):
        '''Extracts and displays the event rounds (e.g. Semi Final, Final, etc.) of a particular event.'''
        get = params.get
        url = get('url')
        link = self.getRequest(url)
        soup = self.getSoup(link)
        currentRound = soup.find('a', id='selected')
        if currentRound is None:
            self.showTitles(params)
            return  
        self.addCategory(currentRound.text,url,NavigationConstants.SHOW_TITLES, isEvent = True)
              
        rgex = re.compile('javascript:toggleRounds8\((\d+),(\d+)\)')
        otherRounds = soup.find_all('a', onclick=rgex)       
        
        for i in range(len(otherRounds)):
            js = otherRounds[i].get('onclick')
            addresses = rgex.findall(js)
            self.addCategory(otherRounds[i].text,self.getCastsURL('/getRound.php?eid=' + addresses[0][0] + '&rid=' + addresses[0][1] + '&settingz=0'), NavigationConstants.SHOW_TITLES, isEvent = True)                      

    def browseCasters(self, params, allCasters):
        '''Extracts and displays all/top casters from the main "browse" page of the SC2Casts site.'''
        get = params.get
        link = self.getRequest(get(NavigationConstants.URL))        
        soup = self.getSoup(link)
        allCastersMarker = soup.find('span', text='All Casters')
        
        rgex = re.compile('/caster')
        
        if allCasters:
            casterList = allCastersMarker.find_all_next('a', href=rgex)
        else:
            casterList = allCastersMarker.find_all_previous('a', href=rgex)
        theRange = range(len(casterList))
        if not allCasters:
            theRange = reversed(theRange)
        for i in theRange:
            self.addCategory(casterList[i].string,
                             self.getCastsURL(casterList[i].get('href')),
                             NavigationConstants.SHOW_TITLES, len(casterList))
    
    def browsePlayers(self, params, allPlayers):
        '''Extracts and displays all/top players from the main "browse" page of the SC2Casts site.'''
        get = params.get
        link = self.getRequest(get(NavigationConstants.URL))        
        soup = self.getSoup(link)
        allPlayersMarker = soup.find('a', text='All Players')
        
        rgex = re.compile('/player')
        
        if allPlayers:
            casterList = allPlayersMarker.find_all_next('a', href=rgex)
        else:
            casterList = allPlayersMarker.find_all_previous('a', href=rgex)
        theRange = range(len(casterList))
        if not allPlayers:
            theRange = reversed(theRange)
        for i in theRange:
            self.addCategory(casterList[i].string,
                             self.getCastsURL(casterList[i].get('href')),
                             NavigationConstants.SHOW_TITLES, len(casterList))
            
    def showLive(self, params = {}):
        link = self.getRequest(self.LIQUID_URL)        
        soup = self.getSoup(link)
        # Find the HTML element that contains the live events and iterate them
        eventBox = soup.find(id='live_events_block')
        liveFeeds = eventBox.find_all('div', 'ev-feed')
        for i in xrange(len(liveFeeds)):
            # Check that it is SC2; otherwise ignore
            if '/images/games/1.png)' not in liveFeeds[i].find('div', 'ev-head').find('span', 'ev')['style']:
                continue
            # Get the events name and stage
            eventName = liveFeeds[i].find('div', 'ev-head').find('div', 'ev-ctrl').text
            eventStage = liveFeeds[i].find('div', 'ev-stage').text
            # Get the links to the twitch channels where the event is casted
            eventLinks = liveFeeds[i].find('div', 'ev-body').find('div', 'ev-stream').find_all('a')
            for j in xrange(len(eventLinks)):
                eventHost = eventLinks[j].text
                # Check if it is actually on Twitch
                if eventLinks[j]['title'].startswith('twitch.tv'):
                    title = self.language(31037) % (eventHost, eventName, eventStage)
                    url = 'plugin://plugin.video.twitch/playLive/' + eventHost.lower()
                    self.addVideo(title, url, False, urlDone = True)

    #--- Functions for showing series
    def showTitles(self, params = {}):
        '''
        This method shows a list of series, i.e., each list entry generated by this method 
        represents a series (which can be any number of games) between two SC2 players
        (or more if it is a 2v2 for example).

        This method is the central piece of code in the plugin and is called in many situations.
        For example, when the user searches, the list of matching series is retrieved
        and displayed via this method. When the user has chosen a caster, a player, 
        an event round, or an event that has only one round, this method is also called.
        
        This is because the SC2Casts website uses (as of right now) the same template 
        for displaying a list of series, independent of the way the user searched for it.
        This make parsing very interchangable and easy.
        '''
        get = params.get
        url = get(NavigationConstants.URL)
          
        # Check if user want to search
        if get(NavigationConstants.ACTION) == NavigationConstants.SHOW_TITLES_SEARCH:
            keyboard = xbmc.Keyboard('')
            keyboard.setHeading('Search for Events, Players, and/or Casters')
            keyboard.doModal()
            url = self.getCastsURL('/?%s' % urllib.urlencode({'q' :keyboard.getText()}))
        link = self.getRequest(url)

        # Get settings:
        # Does the user want colors? what information shall be omitted? shall watched series be marked?
        boolColors = self.setting('colors') == 'true'
        boolDates = self.setting('dates') == 'true'
        boolMatchup = self.setting('matchup') == 'true'
        boolNr_games = self.setting('nr_games') == 'true'
        boolEvent = self.setting('event') == 'true'
        boolRound = self.setting('round') == 'true'
        boolCaster = self.setting('caster') == 'true'
        boolTrackWatched = self.setting('track') == 'true'
        boolSpoilerFreeEventsPlayers = self.setting('spoiler_free_player') == 'true'
        boolSpoilerFreeEventsRace = self.setting('spoiler_free_race') == 'true'
        boolSpoilerFreeReveal = self.setting('spoiler_free_reveal') == 'true'
        
        isEvent = get(NavigationConstants.IS_EVENT) == 'true'
                
        soup = self.getSoup(link)
        # Get all series entries in the hmtl document 
        games = soup.find_all('div', class_='latest_series')
        
        size = len(games)
        
        # Precompile some patterns for later
        castPattern = re.compile('/cast\d')
        bestOfPattern = re.compile('\((.*?)\)')
        casterPattern = re.compile('/caster')
        eventPattern = re.compile('/event(.*)')
        
        # Iterate of list of series
        for i in range(len(games)):
            try:
                # If there is a date item right before the currently inspected series item, 
                # we display the date to improve the readability of the final list.
                # (This only happens if the user selected it in the settings.)
                size = self.addDateItem(boolDates, games[i], boolColors, size)
                
                # Extract the source of the videos of the series.
                # Youtube or twitch are ok, anything else will be skipped.
                source = self.checkSource(games[i])
                if source == Source.Unsupported:
                    continue
               
                # If the source is supported, search for all remaining bits of information.
                matchup = games[i].find('span', style='color:#cccccc')
                cast = games[i].find('a', href=castPattern)
                castUrl = cast.get('href')
                players = cast.find_all('b')
                #TODO: Handle problem when instead of players it only says, for example, "Decider Match" (only happens rarely)
                bestOf = bestOfPattern.findall(players[1].next_sibling)
                event = games[i].find('a', href=eventPattern)
                rounds = games[i].find('span', class_='round_name')
                caster = games[i].find('a', href=casterPattern)
                
                # Check if parts of the title need to be despoilered
                watched = self.checkWatched(self.getCastsURL(castUrl))
                despoilerPlayers = isEvent and boolSpoilerFreeEventsPlayers and not (watched and boolSpoilerFreeReveal)
                despoilerRace = isEvent and boolSpoilerFreeEventsRace and not (watched and boolSpoilerFreeReveal)
                             
                # Generate a label (the string actually displayed ind the kodi listing) for the series.
                videoLabel = self.printTitle(matchup, cast, castUrl, players, bestOf, event, rounds, caster, 
                                             boolColors, boolMatchup, boolNr_games, boolEvent, boolRound, boolCaster, despoilerPlayers, despoilerRace)
                
                # Generate a context menu entry for this series, so that users may more easily 
                # jump to, e.g., one of the players features in the series.
                ctxList = self.createContextList(event, caster, players, castUrl, boolTrackWatched)
                
                # Create the actual list entry.
                self.addCategory(videoLabel, self.getCastsURL(castUrl), NavigationConstants.SHOW_GAMES, count=size, ctxItems=ctxList)
            except Exception as e:
                xbmc.log(str(e), level=xbmc.LOGFATAL)
        # If the list of series we are inspecting is a multi-page list, 
        # we extract the next page link and add a navigation entry to the final list.
        currentPage = soup.find('a', class_='current')
        if currentPage is not None:
            nextPage = currentPage.find_next('a',class_='paginate',text=re.compile('Next'))
            if nextPage is not None:
                self.addCategory(self.language(31021),self.getCastsURL(nextPage.get('href')),
                         NavigationConstants.SHOW_TITLES, size)
        
    def createContextList(self, event, caster, players, castUrl, boolTrackWatched):
        '''
        Creates context menu items for a kodi list entry. 
        This allows users to quickly jump to anyone/anything related to the series 
        they are currently watching, e.g., casters, players, or the event of the series,
        thus eliminating some bothersome manual searching.
        '''
        ctxList = []
        if event is not None:
            ctxList += [(
                        self.language(31022) % event.text, 
                        'ActivateWindow(Videos,%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                NavigationConstants.ACTION : NavigationConstants.BROWSE_EVENT_ROUNDS, 
                                NavigationConstants.URL : self.getCastsURL(event.get('href'))
                            }))
                        )]
        if caster is not None:
            ctxList += [(
                        self.language(31023) % caster.text, 
                        'ActivateWindow(Videos,%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                NavigationConstants.ACTION : NavigationConstants.SHOW_TITLES, 
                                NavigationConstants.URL : self.getCastsURL(caster.get('href'))
                            }))
                        )]
        for j in range(len(players)):
            ctxList += [(
                        self.language(31024) % players[j].text, 
                        'ActivateWindow(Videos,%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                NavigationConstants.ACTION : NavigationConstants.FIND_PLAYER, 
                                NavigationConstants.PLAYER_NO : j,
                                NavigationConstants.URL : self.getCastsURL(castUrl)
                            }))
                        )]

        ctxList += [(
                    self.language(31025), 
                    'RunPlugin(%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                            NavigationConstants.ACTION : NavigationConstants.PLAY_GAMES, 
                            NavigationConstants.URL : self.getCastsURL(castUrl)
                        }))
                    )]
                
        if boolTrackWatched:
            ctxList += [(
                        self.language(31026), 
                        'RunPlugin(%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                NavigationConstants.ACTION : NavigationConstants.TOGGLE_WATCHED, 
                                NavigationConstants.URL : self.getCastsURL(castUrl)
                            }))
                        )]
            
        return ctxList
        
    def printTitle(self, matchup, cast, castUrl, players, bestOf, event, rounds, caster, 
                   boolColors, boolMatchup, boolNr_games, boolEvent, boolRound, boolCaster, despoilerPlayers, despoilerRace):
        '''Generates a string represenation of a series (while considering user parameters).'''
        videoLabel = ''
        if boolMatchup and matchup is not None and matchup.text != '' and not despoilerRace:
            if boolColors:
                videoLabel += '[COLOR skyblue]'
            videoLabel += matchup.text 
            if boolColors:
                videoLabel += '[/COLOR]'
            videoLabel += ' - '
            
        if despoilerPlayers:
            videoLabel += '...'
        else:
            videoLabel += players[0].text + ' vs ' + players[1].text
        
        if boolEvent and event is not None:
            videoLabel += ' - '
            if boolColors:
                videoLabel += '[COLOR burlywood]'
            videoLabel += event.text
            if boolColors:
                videoLabel += '[/COLOR]'
        if boolRound and rounds is not None:
            videoLabel += ' - '
            if boolColors:
                videoLabel += '[COLOR thistle]'
            videoLabel += rounds.text
            if boolColors:
                videoLabel += '[/COLOR]'
        if boolNr_games and len(bestOf) == 1:
            videoLabel += ' - '
            if boolColors:
                videoLabel += '[COLOR lightcyan]'
            videoLabel += bestOf[0]
            if boolColors:
                videoLabel += '[/COLOR]'
        if boolCaster and caster is not None:
            if boolColors:
                videoLabel += '[COLOR lightcyan]'
            videoLabel += self.language(31027) + caster.text
            if boolColors:
                videoLabel += '[/COLOR]'
        return videoLabel
    
    def addDateItem(self, boolDates, currentGameElement, boolColors, listSize):
        '''Extracts and reformats a date string from the website for inclusion in the series list.'''
        if boolDates:
            date = currentGameElement.previous_sibling
            if date.name == 'div' and date.get('style') == 'padding-top: 10px;':
                dateText = ''
                if boolColors:
                    dateText += '[COLOR mediumaquamarine]'
                dateText += '--- ' + date.text + ' ---'
                if boolColors:
                    dateText += '[/COLOR]'
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='',
                                listitem=xbmcgui.ListItem(dateText, iconImage='DefaultFolder.png',
                                thumbnailImage='DefaultFolder.png'), isFolder=False, totalItems =listSize)
                return listSize
        return listSize
    
    def checkSource(self, currentGameElement):
        '''Extracts the source of a series of videos.'''
        source = currentGameElement.find('img')
        if source is None:
            return Source.Unsupported
        sourceCode = source.get('title')
        if sourceCode == 'on YouTube':
            return Source.YouTube
        if sourceCode == 'on Twitch.tv':
            return Source.Twitch
        return Source.Unsupported
    
    #--- Functions for showing games
    def showGames(self, params, play):
        '''
        Extracts and displays a number of games from a SC2 series.
        
        (Actually "games" is misleading because often more than one games is 
        included in one of the list items. A more precise description would be "video".)
        '''
        get = params.get

        # By convention, we mark a series as watched if the user looks at the videos within.
        # This seems premature but because we cannot track the acual watch event because it
        # is handled by the youtube plugin, this is the best we can do.
        if self.addon.getSetting('track') == 'true':
            self.setWatched(get(NavigationConstants.URL))
        
        # Search for ebmedded youtube/twitch player links.
        link = self.getRequest(get(NavigationConstants.URL))
        soup = self.getSoup(link)
        playersYT = soup.find_all('iframe', id='yytplayer')
        playersTW = soup.find_all('iframe', id='twitchplayer')

        ytRegex = re.compile('https://www.youtube.com/embed/(.*)')
        twitchRegex = re.compile('http://sc2casts\.com/twitch/embed2\?id=(.*)')
        
        # Iterate over the found sources and generate list entries for each one.
        # If play = true, the item are added to the queue instead of being displayed as a list.
        count = 0 
        for i in range(len(playersYT)):
            count += 1
            self.addVideo(self.language(31020) % count + self.getSrcString(Source.YouTube), ytRegex.findall(playersYT[i].get('src'))[0], False, play)
            
        for i in range(len(playersTW)):
            count += 1
            self.addVideo(self.language(31020) % count + self.getSrcString(Source.Twitch), twitchRegex.findall(playersTW[i].get('src'))[0], True, play)
        
        # If desired, generate more video items to make it 'spoiler free'
        
        if self.setting('spoiler_free') == 'true' and not play:
            # Find the label of the match type
            matchType = soup.find('div', class_='infolabel').find_all('h2')[0].text;
            # If all matches are contained within one video, we do not need to unspoiler them
            if "in 1 video" not in matchType:
                matchedStr = re.match("Best of ([0-9]+)", matchType)
                if matchedStr is not None:
                    # Find out how many matched can be played and how many have been played
                    boX = int(matchedStr.group(1))
                    youtube = len(playersYT) != 0
                    doneSoFar = len(playersYT) if youtube else len(playersTW)
                    for i in range(doneSoFar+1, boX+1):
                        self.addDummyVideo(i, youtube)
        
        # If the user intent was to add the whole series to the queue, we notify them of the success with a notification.
        if play:
            self.displayNotification(self.language(31028))

    def addDummyVideo(self, number, youtube):
        '''
        Generate a dummy video list item, so that the true number of games played between two players 
        cannot be determined at first glance to avoid spoilers.
        '''
        title = self.language(31020) % number + self.getSrcString(Source.YouTube if youtube else Source.Twitch)
        info = {'Title': title}
        url = '%s/?%s' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                    NavigationConstants.ACTION : NavigationConstants.PLAY_DUMMY
                                }))
        
        listitem=xbmcgui.ListItem(title, iconImage='DefaultFolder.png',
                                  thumbnailImage='DefaultFolder.png')
        listitem.setInfo(type='Video', infoLabels=info)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                    listitem=listitem, isFolder=False,
                                    totalItems=0)
                                    
    def addTwitchExplanation(self):                                    
        '''
        Generate a dummy list item that tells the user how to seek to the right place
        in the twitch video. Since as of now StartOffset is not working. 
        See: http://trac.kodi.tv/ticket/17006
        '''
        title = self.language(31036)
        info = {'Title': title}       
        listitem=xbmcgui.ListItem(title, iconImage='DefaultFolder.png',
                                  thumbnailImage='DefaultFolder.png')
        listitem.setInfo(type='Video', infoLabels=info)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='',
                                    listitem=listitem, isFolder=False,
                                    totalItems=0)
                                    
    def getSrcString(self, source):
        '''Generates an (optionally colored) string representing the source of a video.'''
        if source == Source.Twitch:
            return ' [COLOR slateblue]@ Twitch[/COLOR]'
        else:
            return ' [COLOR crimson]@ YouTube[/COLOR]'
    
    #--- Functions for adding list items
    def addCategory(self, title, url, action, count = 0, ctxItems=[], isEvent = False):
        '''
        Generates a list item other than an actual video. 
        This can be a category but also an event, a list of series, etc.
        '''
        info = { 'Title': title}
        if self.addon.getSetting('track') == 'true' and action == NavigationConstants.SHOW_GAMES:
            if self.checkWatched(url):
                info['playcount'] = 1
        
        urlComponents = {
                            NavigationConstants.ACTION : action, 
                            NavigationConstants.URL : url
                        }
        if isEvent:
            urlComponents[NavigationConstants.IS_EVENT] = 'true'
        else:
            urlComponents[NavigationConstants.IS_EVENT] = 'false'
        url = '%s/?%s' % (self.SELF_PLUGIN_URL, urllib.urlencode(urlComponents))
        listitem=xbmcgui.ListItem(title, iconImage='DefaultFolder.png',
                                  thumbnailImage='DefaultFolder.png')
                                

        listitem.setInfo(type='Video', infoLabels=info)

        if len(ctxItems) > 0:
            listitem.addContextMenuItems(ctxItems)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                    listitem=listitem, isFolder=True,
                                    totalItems=count)

    def addVideo(self, title, url, twitch, toCurrentPL = False, urlDone = False):
        '''
        Generates a list entry representing a video.
        
        If toCurrentPL = true, the item is added to the list currently being prepared 
        for display but is rather added to the kodi video queue. 
        
        This is helpful when the user wants to watch all videos of series or multiple 
        series one after another.
        '''
        if not urlDone:
            playUrl = self.getPlayUrl(url, twitch)
        else:
            playUrl = (url,)
        liz=xbmcgui.ListItem(title, iconImage='DefaultVideo.png',
                                 thumbnailImage='DefaultVideo.png')
        info = {'Title': title}              
        liz.setProperty('IsPlayable','true')
        
        if twitch and not toCurrentPL:
            liz.addContextMenuItems([(self.language(31029), 'Seek('+str(playUrl[1])+')')])
            self.addTwitchExplanation()
        liz.setInfo(type='Video', infoLabels=info)
        if toCurrentPL:
            xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(playUrl[0], listitem=liz)
        else:
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=playUrl[0], listitem=liz)
            
    def getPlayUrl(self, url, twitch):
        ''' 
        Extracts, parses, reformats the video url of twitch and youtube videos.
        
        This is especially important for twitch videos, where the playback starting time
        is almost never at the beginning of the video, which makes it imperative to parse
        and delegate it to the player.
        '''
        timeInSec = 0
        if twitch:
            splt = split(url, '&t=') #30554749&amp;t=09h14m12s
            time = splt[1]
            sys.stderr.write(str(re.compile('(\d+?)s').findall(time)))
            timeInSec = int(re.compile('(\d+?)s').findall(time)[0])
            minu = re.compile('(\d+?)m').findall(time)
            if len(minu) == 1:
                timeInSec += int(minu[0])*60
            hrs = re.compile('(\d+?)h').findall(time)
            if len(hrs) == 1:
                timeInSec += int(hrs[0])*60*60
            videoId = splt[0]
            url = 'plugin://plugin.video.twitch/playVideo/v'+videoId+'/'

        else:
            #special youtube plugin syntax follows, so no constants are used
            url = '%s/?%s' %  (self.YOUTUBE_PLUGIN_URL, urllib.urlencode({
                                    'action' : 'play_video', 
                                    'videoid' : url,
                                }))
        return (url,timeInSec)
    
    #--- Delegating funtions
    def findPlayer(self, url, playerNo):
        '''
        Displays a lists of series of a player. 
        The player is identified by the id of the (most probably) currently inspected series 
        and their number (first or second party in the matchup).
        '''
        link = self.getRequest(url)
        soup = self.getSoup(link)
        rgex = re.compile('/player')
        playerUrls = soup.find_all('a', href=rgex)
        params = {
                    NavigationConstants.ACTION : NavigationConstants.SHOW_TITLES, 
                    NavigationConstants.URL : self.getCastsURL(playerUrls[int(playerNo)].get('href'))
                }
        self.showTitles(params)
        
    #--- Utility functions
    def playDummy(self):
        self.displayNotification(self.language(31035))
    
    def getCastsURL(self, path):
        return self.SC2CASTS_URL + path
    
    def getParams(self, paramList):
        ''' Converts the parameters of the url to a dictionary. '''
        params = urlparse.parse_qs(paramList[paramList.find('?') + 1:])
        paramsFinal = {}
        for key in params:
            paramsFinal[key] = params[key][0]
        return paramsFinal

    def getRequest(self, url):
        ''' Performs an HTTP get request. '''
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0'
                '(Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) '
                'Gecko/20100722 Firefox/3.6.8')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    
    def displayNotification(self, text):
        ''' Displays a kodi notification. '''
        time = 5000 #in miliseconds
        theAddon = xbmcaddon.Addon()
        addonName = theAddon.getAddonInfo('name')
        icon  = theAddon.getAddonInfo('icon')
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(addonName, text, time, icon))
        
    def getSoup(self, text):
        ''' 
        Retrieves a beautiful soup instance taking into account 
        the available parser backend depeding on the python version. 
        '''
        print('Python version: ' + str(sys.version_info))
        if sys.version_info < (2,7,3):
            print('Using html5lib')
            return BeautifulSoup(text, 'html5lib')
        print('Using python parser')
        return BeautifulSoup(text, 'html.parser')
    
    #--- Database functions
    def resetWatched(self):
        ''' Resets the watched marker for a series. '''
        doIt = xbmcgui.Dialog().yesno(self.language(31030),self.language(31031),yeslabel=self.language(31032),nolabel=self.language(31033))
        if doIt:
            conn = self.getDBConn()
            c = conn.cursor()
            c.execute('DELETE FROM watched')
            conn.commit()
            conn.close()
            self.displayNotification('Successfully reset all watched markers.')
    
    def toogleWatched(self, url):
        ''' Toggles the watched marker for a series. '''
        watched = self.checkWatched(url)
        conn = self.getDBConn()
        c = conn.cursor()
        urlList = (url,)
        if watched:
            c.execute('DELETE FROM watched WHERE url=?', urlList)
        else:
            c.execute('INSERT INTO watched VALUES (?)', urlList)
        conn.commit()
        conn.close()
        self.displayNotification(self.language(31034))

    def setWatched(self, url):
        ''' Sets the watched marker for a series to TRUE. '''
        if self.checkWatched(url):
            return
        conn = self.getDBConn()
        if conn is not None:
            c = conn.cursor()
            urlList = (url,)
            c.execute('INSERT INTO watched VALUES (?)', urlList)
            conn.commit()
            conn.close()
    
    def checkWatched(self, url):
        ''' Checks if a series had been watched previously. '''
        conn = self.getDBConn()
        if conn is not None:
            c = conn.cursor()
            urlList = (url,)
            c.execute('SELECT * FROM watched WHERE url=?', urlList)
            watched =  c.fetchone() 
            conn.close()
        return (watched is not None)
            
    def getDBConn(self):
        ''' Retrieves a sqlite database instance. '''
        try:
            userdata_folder = xbmc.translatePath('special://userdata')
            addon_data_folder = os.path.join(userdata_folder, 'addon_data', self.addon.getAddonInfo('id'))
            if not os.path.exists(addon_data_folder):
                os.makedirs(addon_data_folder)
            database_file = os.path.join(addon_data_folder, self.DB_FILE)
            db = None
            if not os.path.exists(database_file):
                open(database_file, 'w').close()
                db = sqlite3.connect(database_file) 
                db.execute('CREATE TABLE watched (url text)')
            if db is None:
                db = sqlite3.connect(database_file) 
            return db
        except:
            return None
    
    
class Source:
    Unsupported = 0
    Twitch = 1
    YouTube = 2

class NavigationConstants:
    ROOT_TOP = 'rootTop'
    ROOT_BROWSE = 'rootBrowse'
    BROWSE_EVENT_TYPE = 'browseEventType'
    BROWSE_CASTER_TYPE = 'browseCasterType'
    BROWSE_PLAYERS_TYPE = 'browsePlayerType'
    BROWSE_EVENTS_PROMINENT = 'browseEventsProminent'
    BROWSE_EVENTS_ALL = 'browseEventsAll'
    BROWSE_EVENT_ROUNDS = 'browseEventRounds'
    BROWSE_CASTERS_PROMINENT = 'browseCastersProminent'
    BROWSE_CASTERS_ALL = 'browseCastersAll'
    BROWSE_PLAYERS_NOTABLE = 'browsePlayersNotable'
    BROWSE_PLAYERS_ALL = 'browsePlayersAll'
    BROWSE_MATCHUPS = 'browseMatchups'
    SHOW_TITLES = 'showTitles'
    SHOW_TITLES_SEARCH = 'showTitlesSearch'
    SHOW_GAMES = 'showGames'
    SHOW_LIVE = 'showLive'
    PLAY_GAMES= 'playGames'
    PLAY_TWITCH = 'playTwitch'
    PLAY_DUMMY = 'playDummy'
    FIND_PLAYER = 'findPlayer'
    TOGGLE_WATCHED = 'toggleWatched'
    RESET_WATCHED = 'resetWatched'
    IS_EVENT = 'isEvent'
    
    URL = 'url'  
    ACTION = 'action' 
    VIDEO_ID = 'videoid'
    START = 'start'
    PLAYER_NO = 'playerNo'     