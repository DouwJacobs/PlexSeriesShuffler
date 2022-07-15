import sys
from plexapi.server import PlexServer
import plexapi

from random import randint
import datetime
import requests

import uuid
from flask import session
import socket   
from time import sleep
import urllib

from flask_socketio import emit

import yaml as yamlMod
import os

if sys.argv[1] == 'docker':
    path = '/config/'
else:
    path = './'


class FirstUse:

    def __init__(self,configPath):

        self.configPath = configPath
        self.createConfig()

    def defaultConfig(self):

        config = { 
            'FirstTime': True
            }

        return config

    def checkConfigExist(self):

        return os.path.exists(self.configPath)

    def createConfig(self):

        if not self.checkConfigExist():
            self.writeConfig(self.defaultConfig())

    def writeConfig(self,data):

        with open(self.configPath, 'w') as f:

            yamlMod.dump(data, f)

    def get_config_name(self,name):

        return self.readConfig()[name]

    def readConfig(self):

        with open(self.configPath) as f:
            data = yamlMod.load(f, Loader=yamlMod.FullLoader)

        return data

    def first(self):

        return self.get_config_name('FirstTime')

    def updateFirst(self):

        data = self.readConfig()
            
        data['FirstTime'] = False

        self.writeConfig(data)



class YamlTools:

    def __init__(self, configPath):

        self.configPath = configPath

        self.createConfig()

    def defaultConfig(self):

        config = { 
            'PLEX' : {
                'PLEX_ACCESS_TOKEN' : None,
                'PMS_URL': '127.0.0.1',
                'PMS_PORT': 32400,
                'PMS_PROTOCOL': 'http'
                },
            'PLEX_LOGIN' : {
                'PLEX_API_URL' : 'https://plex.tv/api/v2',
                'PLEX_LOGIN_TIMEOUT' : 120
            },
            'PLEX_SERIES_SHUFFLER':{
                'PRODUCT_NAME' : 'Series Shuffler',
                'PORT' : 5000
            }
            }

        return config

    def checkValueType(self, base, name, value):

        config = { 
            'PLEX' : {
                'PLEX_ACCESS_TOKEN' : 'str',
                'PMS_URL': 'str',
                'PMS_PORT': 'int',
                'PMS_PROTOCOL': 'str'
                },
            'PLEX_LOGIN' : {
                'PLEX_API_URL' : 'str',
                'PLEX_LOGIN_TIMEOUT' : 'int'
            },
            'PLEX_SERIES_SHUFFLER':{
                'PRODUCT_NAME' : 'str',
                'PORT' : 'int'
            }
            }

        if config[base][name] == 'int':
            try:
                value = int(value)
            except Exception as e:
                pass

        validValue = type(value) == eval(config[base][name])

        print(validValue)

        return(validValue)


    def checkConfigExist(self):

        return os.path.exists(self.configPath)

    def createConfig(self):

        if not self.checkConfigExist():
            self.writeConfig(self.defaultConfig())

    def readConfig(self):

        with open(self.configPath) as f:
            data = yamlMod.load(f, Loader=yamlMod.FullLoader)

        return data


    def writeConfig(self,data):

        with open(self.configPath, 'w') as f:

            yamlMod.dump(data, f)

    def get_config_name(self,base, name):

        return self.readConfig()[base][name]

    def update_config_name(self, base, name, value):

        data = self.readConfig()
            
        data[base][name] = value

        self.writeConfig(data)


    def token(self):

        return self.get_config_name('PLEX','PLEX_ACCESS_TOKEN')

    def baseurl(self):

        data = self.readConfig()['PLEX']

        protocol = data['PMS_PROTOCOL']
        ip_addr = data['PMS_URL']
        port = data['PMS_PORT']

        return f'{protocol}://{ip_addr}:{port}'


class PlexTools:

    def __init__(self, yaml, firstUse):

        self.yaml = yaml

        self.firstUse = firstUse

        self.getLatestConfig()

    def checkConnection(self, url=None):

        if not url:
            url = self.yaml.baseurl()

        try:
            PlexServer(url, self.yaml.token())
            return True
        except requests.exceptions.ConnectionError as e:
            return False

    def getLatestConfig(self):

        self.baseurl = self.yaml.baseurl()
        self.token = self.yaml.token()

        try:
            self.server = PlexServer(self.baseurl, self.token)
        except:
            pass
        

    def getPlaylists(self):

        self.getLatestConfig()

        playlists = {}
        
        playlistsObj = self.server.playlists()

        for playlist in playlistsObj:
            playlists[str(playlist.ratingKey)] = {'title': playlist.title,
                                                'episodes': playlist.leafCount,
                                                'time': str(datetime.timedelta(milliseconds=playlist.duration)) } 

        return playlists

    def getPlaylistByID(self,playlistID):

        playlists = self.getPlaylists()

        title = playlists[str(playlistID)]['title']

        return self.server.playlist(title)

    def getPlaylistShows(self,playlistID):

        playlist = self.getPlaylistByID(playlistID)

        episodes = {}

        for episode in playlist.items():
            episodes[episode.ratingKey] = {'thumb': f'{self.baseurl}{episode.grandparentArt }?X-Plex-Token={self.token}',
                                        'tv_show':episode.grandparentTitle ,
                                        'title': episode.title,
                                        'episode': episode.seasonEpisode,
                                        'summary': episode.summary,
                                        'guid': episode.guid}

        return episodes

    def getShowSections(self):

        self.getLatestConfig()

        showSections = []

        for section in self.server.library.sections():

            if isinstance(section, plexapi.library.ShowSection):
                showSections.append(section)

        return showSections

    def getAllShows(self):

        showSections = self.getShowSections()

        shows = {}

        for showSection in showSections:
            for show in showSection.all():
                shows[show.ratingKey] = {'thumb': f'{self.baseurl}{show.thumb}?X-Plex-Token={self.token}',
                                        'title':show.title,
                                        'guid': show.guid}

        return shows

    def getShowMetadata(self, showGuid):

        showSections = self.getShowSections()

        showMetadata = {}

        for section in showSections:
            showObj = section.getGuid(showGuid)
            showMetadata['title'] = showObj.title
            showMetadata['year'] = showObj.year
            showMetadata['seasons'] = showObj.childCount 
            showMetadata['summary'] = showObj.summary

        return(showMetadata)

    def getShowEpisodes(self, showGuid):

        showSections = self.getShowSections()

        for section in showSections:
            showObj = section.getGuid(showGuid)
            episodes = showObj.episodes()

        return episodes

    def createPlaylist(self, playlistName, episodes):

        self.getLatestConfig()

        return self.server.createPlaylist(playlistName, items=episodes)

    def randomEpisodes(self, seasonList):

        totalShows = len(seasonList)
        print(totalShows)
        print(seasonList[0])

        episodes = 0

        for showList in  seasonList:
            print(showList)
            print(len(showList))
            episodes += len(showList)

        random_list = []

        while len(random_list) != episodes:
            rand = randint(0,totalShows-1)
            if seasonList[rand] == []:
                pass
            else:
                random_list.append(seasonList[rand][0])
                seasonList[rand] = seasonList[rand][1:]

        return random_list

    def createShuffledPlaylist(self, playlistName, seasonList):

        shuffledEpisodes = self.randomEpisodes(seasonList)

        return self.createPlaylist(playlistName, shuffledEpisodes)

    def deletePlaylist(self, playlistID):

        self.getPlaylistByID(playlistID).delete()




class PlexLogin:

    def __init__(self, yaml):

        self.hostname = socket.gethostname()
        self.IPAddr = socket.gethostbyname(self.hostname) 
        self.appPort = yaml.get_config_name('PLEX_SERIES_SHUFFLER','PORT')

        self.apiURL = yaml.get_config_name('PLEX_LOGIN','PLEX_API_URL')

        self.yaml = yaml

    def verifyAccessToken(self,accessToken):

        if not session.get('clientUuid'):
            clientUuid = str(uuid.uuid4())
        else:
            clientUuid = session['clientUuid']

        params = {
            'X-Plex-Product': self.yaml.get_config_name('PLEX_SERIES_SHUFFLER','PRODUCT_NAME'),
            'X-Plex-Client-Identifier': clientUuid,
            'X-Plex-Token': accessToken

        }

        headers = {'accept': 'application/json'}

        r = requests.get(self.apiURL + '/user', headers=headers, params=params)

        if r.status_code == 200:
            self.yaml.update_config_name('PLEX','PLEX_ACCESS_TOKEN', accessToken)
            session['clientUuid'] = clientUuid

            return True
        
        elif r.status_code == 401:
            return False


    def generatePin(self):

        if not session.get('clientUuid'):
            clientUuid = str(uuid.uuid4())
        else:
            clientUuid = session['clientUuid']

        params = {
            'X-Plex-Product': self.yaml.get_config_name('PLEX_SERIES_SHUFFLER','PRODUCT_NAME') ,
            'X-Plex-Client-Identifier': clientUuid,
            'strong': 'true',
            'origin':f"http://{self.IPAddr}:{self.appPort }"

        }

        headers = {'accept': 'application/json'}

        r = requests.post(self.apiURL  + '/pins', headers=headers, params=params)

        if r.status_code == 201:
            session['code'] = r.json()['code']
            session['id'] = r.json()['id']
            session['clientUuid'] = clientUuid
        return r

    def generateAuthUrl(self):

        params = {
        'clientID': session['clientUuid'],
        'code': session['code'],
        'context%5Bdevice%5D%5Bproduct%5D': self.yaml.get_config_name('PLEX_SERIES_SHUFFLER','PRODUCT_NAME') ,
        'origin':f"http://{self.IPAddr}:{self.appPort }"
        }

        parsedParams = urllib.parse.urlencode(params)

        authUrl = f"https://app.plex.tv/auth#?{parsedParams}"

        return authUrl

    def verifyPinId(self):

        if not session.get('clientUuid'):
            clientUuid = str(uuid.uuid4())
        else:
            clientUuid = session['clientUuid']

        params = {
            'X-Plex-Client-Identifier': clientUuid,
            'accept': 'application/json',
            'code' : session['code'],

        }

        headers = {'accept': 'application/json'}

        r = requests.get(self.apiURL  + f"/pins/{session['id']}", params=params, headers=headers)

        return r

    def waitPinResponse(self):

        verified = False
        count = 0

        while verified == False:
            r = self.verifyPinId()
            sleep(1)
            count += 1

            if count < self.yaml.get_config_name('PLEX_LOGIN','PLEX_LOGIN_TIMEOUT'):
                if r.json()['authToken']:
                    self.yaml.update_config_name('PLEX','PLEX_ACCESS_TOKEN', r.json()['authToken'])

                    verified = True
                    emit('userLoggedIn')
                    
            else:
                verified = True
                emit('loginTimedOut')


class Main:

    def __init__(self):

        if sys.argv[1] == 'docker':
            path = '/config/'
        else:
            path = './'

        self.yaml = YamlTools(path + 'config.yml')

        self.firstUse = FirstUse(path + 'do_not_touch.yml')

        self.plexLogin = PlexLogin(self.yaml)

        self.plex = PlexTools(self.yaml, self.firstUse)

        

    def logout(self):

        logged_out = self.yaml.update_config_name('PLEX','PLEX_ACCESS_TOKEN',None)

        if logged_out:
            self.plex = None

    def reloadApp(self):

        from main import reloadApp
        reloadApp()

    def updateSettings(self, base, name, value):

        print(f"INFO: Updating Settings - {base} {name} to {value}")

        if self.yaml.checkValueType(base, name, value):
            self.yaml.update_config_name(base, name, value)
            updated = True
        else:
            updated = False

        if updated and base == 'PLEX':
            print(f"INFO: Updating Plex Before - Baseurl {self.plex.baseurl}")
            self.reloadApp()
            print(f"INFO: Updating Plex Instance - Baseurl {self.yaml.baseurl()}")
            print(f"INFO: Updating Plex After - Baseurl {self.plex.baseurl}")

        if updated:
            print(f"INFO: Updating Settings - Updated {base} {name} to {value}")

        return updated