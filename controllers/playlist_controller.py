from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required, checkFirstTime, checkPlexConnection

from sockets import APP

class Playlist(MethodView):

    @login_required
    @checkFirstTime
    @checkPlexConnection
    def get(self, playlistID):

        playlists = APP.plex.getPlaylists()

        return render_template('playlist.html', 
                                    title="Playlist", episodes=APP.plex.getPlaylistShows(playlistID), playlists=playlists, playlistName= playlists[str(playlistID)]['title'], token=APP.yaml.token())

