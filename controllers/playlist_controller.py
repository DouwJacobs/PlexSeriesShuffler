from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required

from main import plex, yaml

class Playlist(MethodView):

    @login_required
    def get(self, playlistID):

        playlists = plex.getPlaylists()

        return render_template('playlist.html', 
                                    title="Playlist", episodes=plex.getPlaylistShows(playlistID), playlists=playlists, playlistName= playlists[str(playlistID)]['title'], token=yaml.token())

