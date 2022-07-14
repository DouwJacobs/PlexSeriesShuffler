from flask import render_template, request, redirect, url_for
from flask.views import MethodView


from controllers.decorators import login_required

from main import plex, yaml

class createShuffledPlaylist(MethodView):

    @login_required
    def get(self):

        return render_template('createShuffledPlaylist.html', 
                                    title="Create Shuffled Playlist", shows=plex.getAllShows(), playlists=plex.getPlaylists(), token=yaml.token())

    @login_required
    def post(self):

        data = request.form

        playlistName = data['playlistName']

        showsList = []

        for i in data.keys():
            if i != 'playlistName':
                showsList.append(plex.getShowEpisodes(i))

        playlist = plex.createShuffledPlaylist(playlistName, showsList)

        return redirect(url_for('playlist', playlistID = playlist.ratingKey))

