import re
import sys
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from string import split
from twitch import TwitchTV
from bs4 import BeautifulSoup
import time
import sqlite3
import os

TWITCHTV = TwitchTV(xbmc.log)

class SC2Casts:
   
    SC2CASTS_URL = 'http://sc2casts.com'
    VIDEO_URL = 'http://www.youtube.com'
    VIDEO_PLUGIN_URL = 'plugin://plugin.video.youtube'
    TWITCH_PLUGIN_URL = 'plugin://plugin.video.twitch'
    SELF_PLUGIN_URL = 'plugin://plugin.video.sc2casts'
    USERAGENT = ('Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) '
                 'Gecko/20100722 Firefox/3.6.8')
    DB_FILE = 'watched.db'
    __settings__ = xbmcaddon.Addon(id='plugin.video.sc2casts')
    __language__ = __settings__.getLocalizedString

    def getCastsURL(self, path):
        return self.SC2CASTS_URL + path
    
    def action(self, params):
        get = params.get
        if (get('action') == 'rootTop'):
            self.rootTop()
        if (get('action') == 'rootBrowse'):
            self.rootBrowse()
        if (get('action') == 'browseEventType'):
            self.browseEventType(params)
        if (get('action') == 'browseEventsProminent'):
            self.browseEvents(params, False)
        if (get('action') == 'browseEventsAll'):
            self.browseEvents(params, True)
        if (get('action') == 'browseMatchups'):
            self.browseMatchups()
        if (get('action') == 'browseCastersType'):
            self.browseCastersType(params)
        if (get('action') == 'browseCastersProminent'):
            self.browseCasters(params, False)
        if (get('action') == 'browseCastersAll'):
            self.browseCasters(params, True)
        if (get('action') == 'browsePlayersType'):
            self.browsePlayersType(params)
        if (get('action') == 'browsePlayersNotable'):
            self.browsePlayers(params, False)
        if (get('action') == 'browsePlayersAll'):
            self.browsePlayers(params, True)
        if (get('action') == 'showTitles'
            or get('action') == 'showTitlesTop'
            or get('action') == 'showTitlesSearch'):
            self.showTitles(params)
        if (get('action') == 'showGames'):
            self.showGames(params,False)
        if (get('action') == 'playGames'):
            self.showGames(params, True)
        if (get('action') == 'showEventRounds'):
            self.showEventRounds(params)
        if (get('action') == 'playTwitch'):
            self.playVideo(params.get('id'), params.get('start'))
        if (get('action') == 'findPlayer'):
            self.findPlayer(params.get('url'), params.get('playerNo'))
        if (get('action') == 'toggleWatched'):
            print('TEEEEST')
            self.toogleWatched(params.get('url'))

    # Menu functions #

    # display the root menu
    def root(self):
        self.addCategory(self.__language__(31000),
                         self.getCastsURL('/all'),
                         'showTitles')
        self.addCategory(self.__language__(31002), '', 'rootBrowse')
        self.addCategory(self.__language__(31001), '', 'rootTop')
        self.addCategory(self.__language__(31003), '', 'showTitlesSearch')

    # display the top casts menu
    def rootTop(self):
        self.addCategory(self.__language__(31004),
                         self.getCastsURL('/top/index.php?all'),
                         'showTitlesTop')
        self.addCategory(self.__language__(31005),
                         self.getCastsURL('/top/index.php?month'),
                         'showTitlesTop')
        self.addCategory(self.__language__(31006),
                         self.getCastsURL('/top/index.php?week'),
                         'showTitlesTop')
        self.addCategory(self.__language__(31007),
                         self.getCastsURL('/top/index.php'),
                         'showTitlesTop')

    # display the browse casts menu
    def rootBrowse(self):
        self.addCategory(self.__language__(31008),
                         self.getCastsURL('/browse/index.php'),
                         'browseEventType')
        self.addCategory(self.__language__(31009), '', 'browseMatchups')
        self.addCategory(self.__language__(31015), self.getCastsURL('/browse/index.php'), 'browsePlayersType')
        self.addCategory(self.__language__(31010),
                         self.getCastsURL('/browse/index.php'),
                         'browseCastersType')

    # display the browse events menu
    def browseEvents(self, params, allEvents):
        get = params.get
        link = self.getRequest(get('url'))
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
                             'showEventRounds', len(eventList))
        
    def browseEventType(self, params):
        self.addCategory(self.__language__(31011), params.get('url'),
                         'browseEventsProminent')
        self.addCategory(self.__language__(31012), params.get('url'),
                         'browseEventsAll')

    # display the browse casters menu
    def browseMatchups(self):
        self.addCategory('PvZ', self.getCastsURL('/matchups-PvZ'),
                         'showTitles')
        self.addCategory('PvT', self.getCastsURL('/matchups-PvT'),
                         'showTitles')
        self.addCategory('TvZ', self.getCastsURL('/matchups-TvZ'),
                         'showTitles')
        self.addCategory('PvP', self.getCastsURL('/matchups-PvP'),
                         'showTitles')
        self.addCategory('TvT', self.getCastsURL('/matchups-TvT'),
                         'showTitles')
        self.addCategory('ZvZ', self.getCastsURL('/matchups-ZvZ'),
                         'showTitles')

    # display the browse casters menu
    def browseCasters(self, params, allCasters):
        get = params.get
        link = self.getRequest(get('url'))        
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
                             'showTitles', len(casterList))


    def browseCastersType(self, params):
        self.addCategory(self.__language__(31013), params.get('url'),
                         'browseCastersProminent')
        self.addCategory(self.__language__(31014), params.get('url'),
                         'browseCastersAll')
        
    
    def browsePlayers(self, params, allPlayers):
        get = params.get
        link = self.getRequest(get('url'))        
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
                             'showTitles', len(casterList))

    def browsePlayersType(self, params):
        self.addCategory(self.__language__(31016), params.get('url'),
                         'browsePlayersNotable')
        self.addCategory(self.__language__(31017), params.get('url'),
                         'browsePlayersAll')

        

    # Add functions #
    def addCategory(self, title, url, action, count = 0, ctxItems=[]):
        info = { 'Title': title}
        if self.__settings__.getSetting('track') == 'true' and action == 'showGames':
            if self.checkWatched(url):
                info['playcount'] = 1
        
        url=(sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&title=' +
             urllib.quote_plus(title) + '&action=' + urllib.quote_plus(action))
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
            liz.addContextMenuItems([('Retry seek', 'Seek('+str(playUrl[1])+')')])
        if toCurrentPL:
            xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(playUrl[0], listitem=liz)
        else:
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=playUrl[0], listitem=liz)
    # Show functions #

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
            url = splt[0]
            url = ('%s/?action=playTwitch&id=v%s&start=%i'
                        %(self.SELF_PLUGIN_URL, url, timeInSec))

        else:
            url = ('%s/?action=play_video&videoid=%s'
                        %(self.VIDEO_PLUGIN_URL, url))
        return (url,timeInSec)

    def showTitles(self, params = {}):
        get = params.get
        url = get('url')
        
    
        
        # Check if user want to search
        if get('action') == 'showTitlesSearch':
            keyboard = xbmc.Keyboard('')
            keyboard.doModal()
            url = self.getCastsURL('/?q=' + keyboard.getText())
        link = self.getRequest(url)

        start = time.time()
        # Get settings
        boolColors = self.__settings__.getSetting('colors') == 'true'
        boolDates = self.__settings__.getSetting('dates') == 'true'
        boolMatchup = self.__settings__.getSetting('matchup') == 'true'
        boolNr_games = self.__settings__.getSetting('nr_games') == 'true'
        boolEvent = self.__settings__.getSetting('event') == 'true'
        boolRound = self.__settings__.getSetting('round') == 'true'
        boolCaster = self.__settings__.getSetting('caster') == 'true'
        boolTrackWatched = self.__settings__.getSetting('track') == 'true'
        
        soup = self.getSoup(link)
        games = soup.find_all('div', class_='latest_series')
        
        size = len(games)
        
        castPattern = re.compile('/cast\d')
        bestOfPattern = re.compile('\((.*?)\)')
        casterPattern = re.compile('/caster')
        eventPattern = re.compile('/event(.*)')
        
        for i in range(len(games)):
            if boolDates:
                date = games[i].previous_sibling
                if date.name == 'div' and date.get('style') == 'padding-top: 10px;':
                    dateText = ''
                    if boolColors:
                        dateText += '[COLOR mediumaquamarine]'
                    dateText += '--- ' + date.text + ' ---'
                    if boolColors:
                        dateText += '[/COLOR]'
                    size += 1
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='',
                                    listitem=xbmcgui.ListItem(dateText, iconImage='DefaultFolder.png',
                                    thumbnailImage='DefaultFolder.png'), isFolder=False, totalItems = size)
                    
            
            source = games[i].find('img')
            if source is None:
                continue
            sourceCode = source.get('title')
            if sourceCode != 'on YouTube' and  sourceCode != 'on Twitch.tv':
                continue
            
            
            matchup = games[i].find('span', style='color:#cccccc')
            cast = games[i].find('a', href=castPattern)
            castUrl = cast.get('href')
            players = cast.find_all('b')
            bestOf = bestOfPattern.findall(players[1].next_sibling)
            event = games[i].find('a', href=eventPattern)
            rounds = games[i].find('span', class_='round_name')
            caster = games[i].find('a', href=casterPattern)
            
            videoLabel = self.printTitle(sourceCode, matchup, cast, castUrl, players, bestOf, event, rounds, caster, 
                                         boolColors, boolMatchup, boolNr_games, boolEvent, boolRound, boolCaster)
            
            ctxList = []
            if event is not None:
                ctxUrl = '?action=showEventRounds&url=' + urllib.quote_plus(self.getCastsURL(event.get('href')))
                ctxList += [('Go to event: ' + event.text, 'ActivateWindow(video,plugin://plugin.video.sc2casts/'+ctxUrl+')')]
            if caster is not None:
                ctxUrl = '?action=showTitles&url=' + urllib.quote_plus(self.getCastsURL(caster.get('href')))
                ctxList += [('Go to caster: ' + caster.text, 'ActivateWindow(video,plugin://plugin.video.sc2casts/'+ctxUrl+')')]
            
            for j in range(len(players)):
                ctxUrl = '?action=findPlayer&playerNo='+str(j)+'&url=' + urllib.quote_plus(self.getCastsURL(castUrl))
                ctxList += [('Go to player: ' + players[j].text, 'ActivateWindow(video,plugin://plugin.video.sc2casts/'+ctxUrl+')')]
            
            ctxUrl = '?action=playGames&url=' + urllib.quote_plus(castUrl)
            ctxList += [('Queue all videos', 'RunPlugin(plugin://plugin.video.sc2casts/'+ctxUrl+')')]
            
            if boolTrackWatched:
                ctxUrl = '?action=toggleWatched&url=' + urllib.quote_plus(castUrl)
                ctxList += [('Toggle watched', 'RunPlugin(plugin://plugin.video.sc2casts/'+ctxUrl+')')]
            
            self.addCategory(videoLabel, castUrl,'showGames',count=size,ctxItems=ctxList)
        
        currentPage = soup.find('a', class_='current')
        if currentPage is not None:
            nextPage = currentPage.find_next('a',class_='paginate',text=re.compile('Next'))
            if nextPage is not None:
                self.addCategory('Next page -->',self.getCastsURL(nextPage.get('href')),
                         'showTitles', size)
        
        end = time.time()
        print('time: ' + str(end - start))
            
    def printTitle(self, sourceCode, matchup, cast, castUrl, players, bestOf, event, rounds, caster, boolColors, boolMatchup, boolNr_games, boolEvent, boolRound, boolCaster):
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
            videoLabel += ' - cast by: ' + caster.text
            if boolColors:
                videoLabel += '[/COLOR]'
        return videoLabel
    
    def findPlayer(self, url, playerNo):
        link = self.getRequest(url)
        soup = self.getSoup(link)
        rgex = re.compile('/player')
        playerUrls = soup.find_all('a', href=rgex)
        
        self.showTitles(self.getParams('?action=showTitles&url=' + urllib.quote_plus(self.getCastsURL(playerUrls[int(playerNo)].get('href')))))
        
    def showGames(self, params, play):
        get = params.get

        if self.__settings__.getSetting('track') == 'true':
            self.setWatched(get('url'))
        
        link = self.getRequest(self.getCastsURL(get('url')))
        soup = self.getSoup(link)
        playersYT = soup.find_all('iframe', id='ytplayer')
        playersTW = soup.find_all('iframe', id='twitchplayer')

        ytRegex = re.compile('https://www.youtube.com/embed/(.*)')
        twitchRegex = re.compile('http://sc2casts\.com/twitch/embed2\?id=(.*)')
        
        cnt = 0 
        for i in range(len(playersYT)):
            cnt += 1
            self.addVideo('Game ' + str(cnt) + self.getSrcString(False), ytRegex.findall(playersYT[i].get('src'))[0], False, play)
            
        for i in range(len(playersTW)):
            cnt += 1
            self.addVideo('Game ' + str(cnt) + self.getSrcString(True), twitchRegex.findall(playersTW[i].get('src'))[0], True, play)
        
        if play:
            self.displayNotification('Queued all games from this series.')

    def getSrcString(self, twitch):
        if twitch:
            return ' [COLOR slateblue]@ Twitch[/COLOR]'
        else:
            return ' [COLOR crimson]@ YouTube[/COLOR]'

    def showEventRounds(self, params = {}):
        get = params.get
        url = get('url')
        link = self.getRequest(url)
        soup = self.getSoup(link)
        currentRound = soup.find('a', id='selected')
        if currentRound is None:
            self.showTitles(params)
            return  
        self.addCategory(currentRound.text,url,'showTitles')
              
        rgex = re.compile('javascript:toggleRounds8\((\d+),(\d+)\)')
        otherRounds = soup.find_all('a', onclick=rgex)       
        
        for i in range(len(otherRounds)):
            js = otherRounds[i].get('onclick')
            print(str(js))
            addresses = rgex.findall(js)
            print(str(addresses))
            self.addCategory(otherRounds[i].text,self.getCastsURL('/getRound.php?eid=' + addresses[0][0] + '&rid=' + addresses[0][1] + '&settingz=0 '),'showTitles')                      
    
    
    # Data functions #
    def getParams(self, paramList):
        splitParams = paramList[paramList.find('?') + 1:].split('&')
        paramsFinal = {}
        for value in splitParams:
            splitParams = value.split('=')
            typeT = splitParams[0]
            if len(splitParams)==2:
                content = splitParams[1]
                if typeT == 'url':
                    content = urllib.unquote_plus(content)
                paramsFinal[typeT] = content
        return paramsFinal

    def getRequest(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.USERAGENT)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    
    def playVideo(self, theId, start):
        videoQuality = 1
        simplePlaylist = TWITCHTV.getVideoPlaylist(theId,videoQuality)
        li = xbmcgui.ListItem("", path=simplePlaylist[0][0]) 
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=li)
        
        #hack to jump to the right position
        while not xbmc.Player().isPlaying():
            xbmc.sleep(100)
        xbmc.sleep(4000)
        xbmc.Player().seekTime(float(start))
    
    
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
        self.displayNotification('Watched status updated.')

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
            userdata_folder = xbmc.translatePath("special://userdata")
            addon_data_folder = os.path.join(userdata_folder, "addon_data", xbmcaddon.Addon().getAddonInfo("id"))
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
        
        
            
            