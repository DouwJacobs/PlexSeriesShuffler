from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required, checkFirstTime, checkPlexConnection

from sockets import APP

class Index(MethodView):

    @login_required
    @checkFirstTime
    @checkPlexConnection
    def get(self):

        print(f"INDEX PLEX: {APP.plex.baseurl}")

        playlists = APP.plex.getPlaylists()
        shows = APP.plex.getAllShows()

        return render_template('shows.html', 
                                    title="Home", shows=shows, playlists=playlists, token=APP.yaml.token())

