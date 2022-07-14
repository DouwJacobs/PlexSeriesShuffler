from logging import exception
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
import plexapi

from random import randint
import datetime
import requests


class PlexTools:

    def __init__(self, baseurl=None, token=None):

        #self.account = MyPlexAccount(token)
        self.baseurl = baseurl
        self.token = token

        if baseurl and token:
            try:
                self.server = PlexServer(baseurl, token)
            except requests.exceptions.ConnectionError as e:
                self.server = None

    def getPlaylists(self):

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






