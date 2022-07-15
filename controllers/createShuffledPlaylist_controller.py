from flask import render_template, request, redirect, url_for
from flask.views import MethodView


from controllers.decorators import login_required, checkFirstTime, checkPlexConnection

from sockets import APP

class createShuffledPlaylist(MethodView):

    @login_required
    @checkFirstTime
    @checkPlexConnection
    def get(self):

        return render_template('createShuffledPlaylist.html', 
                                    title="Create Shuffled Playlist", shows=APP.plex.getAllShows(), playlists=APP.plex.getPlaylists(), token=APP.yaml.token())

    @login_required
    @checkFirstTime
    def post(self):

        data = request.form

        playlistName = data['playlistName']

        showsList = []

        for i in data.keys():
            if i != 'playlistName':
                showsList.append(APP.plex.getShowEpisodes(i))

        playlist = APP.plex.createShuffledPlaylist(playlistName, showsList)

        return redirect(url_for('playlist', playlistID = playlist.ratingKey))

