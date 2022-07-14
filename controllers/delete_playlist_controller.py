from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required

from main import plex, yaml

class DeletePlaylist(MethodView):

    @login_required
    def get(self, playlistID):

        plex.deletePlaylist(playlistID)

        playlists = plex.getPlaylists()

        return render_template('playlists.html', 
                                    title="Playlists", playlists=playlists, token=yaml.token())

