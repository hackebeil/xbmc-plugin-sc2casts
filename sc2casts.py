import re
import sys
import urllib
import urllib2
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import time
import sqlite3
import os
from string import split
from twitch import TwitchTV
from bs4 import BeautifulSoup

class SC2Casts:
   
    #--- Constants
    SC2CASTS_URL = 'http://sc2casts.com'
    VIDEO_URL = 'http://www.youtube.com'
    YOUTUBE_PLUGIN_URL = 'plugin://plugin.video.youtube'
    SELF_PLUGIN_URL = 'plugin://plugin.video.sc2casts'
    DB_FILE = 'watched.db'
    
    #--- Members
    addon = xbmcaddon.Addon()
    language = addon.getLocalizedString
    setting = addon.getSetting

    def action(self, params):
        get = params.get
        action = get(NavigationConstants.ACTION)
        #menu functions
        if (action == NavigationConstants.ROOT_TOP):
            self.rootTop()
        if (action == NavigationConstants.ROOT_BROWSE):
            self.rootBrowse()

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
        self.addCategory(self.language(31000),
                         self.getCastsURL('/all'),
                         NavigationConstants.SHOW_TITLES)
        self.addCategory(self.language(31002), '', NavigationConstants.ROOT_BROWSE)
        self.addCategory(self.language(31001), '', NavigationConstants.ROOT_TOP)
        self.addCategory(self.language(31003), '', NavigationConstants.SHOW_TITLES_SEARCH)

    def rootTop(self):
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
        self.addCategory(self.language(31011), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_EVENTS_PROMINENT)
        self.addCategory(self.language(31012), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_EVENTS_ALL)

    def browseCasterType(self, params):
        self.addCategory(self.language(31013), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_CASTERS_PROMINENT)
        self.addCategory(self.language(31014), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_CASTERS_ALL)
    
    def browsePlayerType(self, params):
        self.addCategory(self.language(31016), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_PLAYERS_NOTABLE)
        self.addCategory(self.language(31017), params.get(NavigationConstants.URL),
                         NavigationConstants.BROWSE_PLAYERS_ALL)
    
    #--- Browse functions   
    def browseEvents(self, params, allEvents):
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
        get = params.get
        url = get('url')
        link = self.getRequest(url)
        soup = self.getSoup(link)
        currentRound = soup.find('a', id='selected')
        if currentRound is None:
            self.showTitles(params)
            return  
        self.addCategory(currentRound.text,url,NavigationConstants.SHOW_TITLES)
              
        rgex = re.compile('javascript:toggleRounds8\((\d+),(\d+)\)')
        otherRounds = soup.find_all('a', onclick=rgex)       
        
        for i in range(len(otherRounds)):
            js = otherRounds[i].get('onclick')
            print(str(js))
            addresses = rgex.findall(js)
            print(str(addresses))
            self.addCategory(otherRounds[i].text,self.getCastsURL('/getRound.php?eid=' + addresses[0][0] + '&rid=' + addresses[0][1] + '&settingz=0'), NavigationConstants.SHOW_TITLES)                      

    def browseCasters(self, params, allCasters):
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

    #--- Functions for showing series
    def showTitles(self, params = {}):
        get = params.get
        url = get(NavigationConstants.URL)
          
        # Check if user want to search
        if get(NavigationConstants.ACTION) == NavigationConstants.SHOW_TITLES_SEARCH:
            keyboard = xbmc.Keyboard('')
            keyboard.setHeading('Search for Events, Players, and/or Casters')
            keyboard.doModal()
            url = self.getCastsURL('/?%s' % urllib.urlencode({'q' :keyboard.getText()}))
        link = self.getRequest(url)

        start = time.time()
        # Get settings
        boolColors = self.setting('colors') == 'true'
        boolDates = self.setting('dates') == 'true'
        boolMatchup = self.setting('matchup') == 'true'
        boolNr_games = self.setting('nr_games') == 'true'
        boolEvent = self.setting('event') == 'true'
        boolRound = self.setting('round') == 'true'
        boolCaster = self.setting('caster') == 'true'
        boolTrackWatched = self.setting('track') == 'true'
        
        soup = self.getSoup(link)
        games = soup.find_all('div', class_='latest_series')
        
        size = len(games)
        
        castPattern = re.compile('/cast\d')
        bestOfPattern = re.compile('\((.*?)\)')
        casterPattern = re.compile('/caster')
        eventPattern = re.compile('/event(.*)')
        
        for i in range(len(games)):
            size = self.addDateItem(boolDates, games[i], boolColors, size)
            
            source = self.checkSource(games[i])
            if source == Source.Unsupported:
                continue
           
            matchup = games[i].find('span', style='color:#cccccc')
            cast = games[i].find('a', href=castPattern)
            castUrl = cast.get('href')
            players = cast.find_all('b')
            bestOf = bestOfPattern.findall(players[1].next_sibling)
            event = games[i].find('a', href=eventPattern)
            rounds = games[i].find('span', class_='round_name')
            caster = games[i].find('a', href=casterPattern)
            
            videoLabel = self.printTitle(matchup, cast, castUrl, players, bestOf, event, rounds, caster, 
                                         boolColors, boolMatchup, boolNr_games, boolEvent, boolRound, boolCaster)
            
            ctxList = self.createContextList(event, caster, players, castUrl, boolTrackWatched)
            
            self.addCategory(videoLabel, self.getCastsURL(castUrl), NavigationConstants.SHOW_GAMES, count=size, ctxItems=ctxList)
        
        currentPage = soup.find('a', class_='current')
        if currentPage is not None:
            nextPage = currentPage.find_next('a',class_='paginate',text=re.compile('Next'))
            if nextPage is not None:
                self.addCategory(self.language(31021),self.getCastsURL(nextPage.get('href')),
                         NavigationConstants.SHOW_TITLES, size)
        
        end = time.time()
        print('time: ' + str(end - start))
        
    def createContextList(self, event, caster, players, castUrl, boolTrackWatched):
        ctxList = []
        if event is not None:
            ctxList += [(
                        self.language(31022) % event.text, 
                        'ActivateWindow(video,%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                NavigationConstants.ACTION : NavigationConstants.BROWSE_EVENT_ROUNDS, 
                                NavigationConstants.URL : self.getCastsURL(event.get('href'))
                            }))
                        )]
        if caster is not None:
            ctxList += [(
                        self.language(31023) % caster.text, 
                        'ActivateWindow(video,%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                NavigationConstants.ACTION : NavigationConstants.SHOW_TITLES, 
                                NavigationConstants.URL : self.getCastsURL(caster.get('href'))
                            }))
                        )]
        for j in range(len(players)):
            ctxList += [(
                        self.language(31024) % players[j].text, 
                        'ActivateWindow(video,%s/?%s)' % (self.SELF_PLUGIN_URL, urllib.urlencode({
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
                   boolColors, boolMatchup, boolNr_games, boolEvent, boolRound, boolCaster):
        videoLabel = ''
        if boolMatchup and matchup is not None and matchup.text != '':
            if boolColors:
                videoLabel += '[COLOR skyblue]'
            videoLabel += matchup.text 
            if boolColors:
                videoLabel += '[/COLOR]'
            videoLabel += ' - '
        
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
        get = params.get

        if self.addon.getSetting('track') == 'true':
            self.setWatched(get(NavigationConstants.URL))
        
        link = self.getRequest(get(NavigationConstants.URL))
        soup = self.getSoup(link)
        playersYT = soup.find_all('iframe', id='ytplayer')
        playersTW = soup.find_all('iframe', id='twitchplayer')

        ytRegex = re.compile('https://www.youtube.com/embed/(.*)')
        twitchRegex = re.compile('http://sc2casts\.com/twitch/embed2\?id=(.*)')
        
        count = 0 
        for i in range(len(playersYT)):
            count += 1
            self.addVideo(self.language(31020) % count + self.getSrcString(Source.YouTube), ytRegex.findall(playersYT[i].get('src'))[0], False, play)
            
        for i in range(len(playersTW)):
            count += 1
            self.addVideo(self.language(31020) % count + self.getSrcString(Source.Twitch), twitchRegex.findall(playersTW[i].get('src'))[0], True, play)
        
        if play:
            self.displayNotification(self.language(31028))

    def getSrcString(self, source):
        if source == Source.Twitch:
            return ' [COLOR slateblue]@ Twitch[/COLOR]'
        else:
            return ' [COLOR crimson]@ YouTube[/COLOR]'
    
    #--- Functions for adding list items
    def addCategory(self, title, url, action, count = 0, ctxItems=[]):
        info = { 'Title': title}
        if self.addon.getSetting('track') == 'true' and action == NavigationConstants.SHOW_GAMES:
            if self.checkWatched(url):
                info['playcount'] = 1
                
        url = '%s/?%s' % (self.SELF_PLUGIN_URL, urllib.urlencode({
                                    NavigationConstants.ACTION : action, 
                                    NavigationConstants.URL : url
                                }))
        
        listitem=xbmcgui.ListItem(title, iconImage='DefaultFolder.png',
                                  thumbnailImage='DefaultFolder.png')

        listitem.setInfo(type='Video', infoLabels=info)

        if len(ctxItems) > 0:
            listitem.addContextMenuItems(ctxItems)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                    listitem=listitem, isFolder=True,
                                    totalItems=count)

    def addVideo(self, title, url, twitch, toCurrentPL = False):
        playUrl = self.getPlayUrl(url, twitch)
        liz=xbmcgui.ListItem(title, iconImage='DefaultVideo.png',
                                 thumbnailImage='DefaultVideo.png')
        liz.setInfo(type='Video', infoLabels={ 'Title': title })
        liz.setProperty('IsPlayable','true')
        if twitch and not toCurrentPL:
            liz.addContextMenuItems([(self.language(31029), 'Seek('+str(playUrl[1])+')')])
        if toCurrentPL:
            xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(playUrl[0], listitem=liz)
        else:
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=playUrl[0], listitem=liz)
            
    def getPlayUrl(self, url, twitch):
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
            url = '%s/?%s' %  (self.SELF_PLUGIN_URL, urllib.urlencode({
                                    NavigationConstants.ACTION : NavigationConstants.PLAY_TWITCH, 
                                    NavigationConstants.VIDEO_ID : 'v' + videoId,
                                    NavigationConstants.START : timeInSec
                                }))

        else:
            #special youtube plugin syntax follows, so no constants are used
            url = '%s/?%s' %  (self.YOUTUBE_PLUGIN_URL, urllib.urlencode({
                                    'action' : 'play_video', 
                                    'videoid' : url,
                                }))
        return (url,timeInSec)
    
    #--- Delegating funtions
    def playVideo(self, videoId, start):
        videoQuality = 1
        simplePlaylist = TwitchTV(xbmc.log).getVideoPlaylist(videoId, videoQuality)
        li = xbmcgui.ListItem('', path=simplePlaylist[0][0]) 
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=li)
        
        #hack to jump to the right position
        while not xbmc.Player().isPlaying():
            xbmc.sleep(100)
        xbmc.sleep(4000)
        xbmc.Player().seekTime(float(start))

    def findPlayer(self, url, playerNo):
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
    def getCastsURL(self, path):
        return self.SC2CASTS_URL + path
    
    def getParams(self, paramList):
        params = urlparse.parse_qs(paramList[paramList.find('?') + 1:])
        paramsFinal = {}
        for key in params:
            paramsFinal[key] = params[key][0]
        return paramsFinal

    def getRequest(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0'
                '(Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) '
                'Gecko/20100722 Firefox/3.6.8')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    
    def displayNotification(self, text):
        time = 5000 #in miliseconds
        theAddon = xbmcaddon.Addon()
        addonName = theAddon.getAddonInfo('name')
        icon  = theAddon.getAddonInfo('icon')
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(addonName, text, time, icon))
        
    def getSoup(self, text):
        print('Python version: ' + str(sys.version_info))
        if sys.version_info < (2,7,3):
            print('Using html5lib')
            return BeautifulSoup(text, 'html5lib')
        print('Using python parser')
        return BeautifulSoup(text, 'html.parser')
    
    #--- Database functions
    def resetWatched(self):
        doIt = xbmcgui.Dialog().yesno(self.language(31030),self.language(31031),yeslabel=self.language(31032),nolabel=self.language(31033))
        if doIt:
            conn = self.getDBConn()
            c = conn.cursor()
            c.execute('DELETE FROM watched')
            conn.commit()
            conn.close()
            self.displayNotification('Successfully reset all watched markers.')
    
    def toogleWatched(self, url):
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
        conn = self.getDBConn()
        if conn is not None:
            c = conn.cursor()
            urlList = (url,)
            c.execute('SELECT * FROM watched WHERE url=?', urlList)
            watched =  c.fetchone() 
            conn.close()
        return (watched is not None)
            
    def getDBConn(self):
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
    PLAY_GAMES= 'playGames'
    PLAY_TWITCH = 'playTwitch'
    FIND_PLAYER = 'findPlayer'
    TOGGLE_WATCHED = 'toggleWatched'
    RESET_WATCHED = 'resetWatched'
    
    URL = 'url'  
    ACTION = 'action' 
    VIDEO_ID = 'videoid'
    START = 'start'
    PLAYER_NO = 'playerNo'     