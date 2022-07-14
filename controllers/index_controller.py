from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required, checkPlexConnection

from main import plex, yaml

class Index(MethodView):

    @login_required
    def get(self):

        plex.checkConnection()

        playlists = plex.getPlaylists()
        shows = plex.getAllShows()

        return render_template('shows.html', 
                                    title="Home", shows=shows, playlists=playlists, token=yaml.token())

