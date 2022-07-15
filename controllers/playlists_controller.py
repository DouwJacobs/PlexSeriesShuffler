from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required, checkFirstTime, checkPlexConnection

from sockets import APP

class Playlists(MethodView):

    @login_required
    @checkFirstTime
    @checkPlexConnection
    def get(self):

        playlists = APP.plex.getPlaylists()

        return render_template('playlists.html', 
                                    title="Playlists", playlists=playlists, token=APP.yaml.token())

