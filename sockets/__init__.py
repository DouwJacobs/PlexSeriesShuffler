import utils
from __init__ import create_app
from flask_session import Session
from requests.exceptions import ConnectionError


from flask import render_template
from flask_socketio import SocketIO, emit

from django.apps import AppConfig
AppConfig.default = False
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

APP = utils.Main()

from controllers.index_controller import Index
from controllers.sign_in_controller import SignIn
from controllers.logout_controller import Logout
from controllers.playlist_controller import Playlist
from controllers.playlists_controller import Playlists
from controllers.createShuffledPlaylist_controller import createShuffledPlaylist
from controllers.delete_playlist_controller import DeletePlaylist
from controllers.settings_controller import Settings
from controllers.setup_controller import Setup

def initialise():

    app = create_app() # we initialize our flask app using the __init__.py function

    Session(app)
    socketio = SocketIO(app, manage_session=False)

    app.add_url_rule('/', view_func=Index.as_view('index'))
    app.add_url_rule('/sign_in', view_func=SignIn.as_view('sign_in'))
    app.add_url_rule('/logout',view_func=Logout.as_view('logout'))
    app.add_url_rule('/playlist/<playlistID>',view_func=Playlist.as_view('playlist'))
    app.add_url_rule('/playlists',view_func=Playlists.as_view('playlists'))
    app.add_url_rule('/create-shuffled-playlist',view_func=createShuffledPlaylist.as_view('createShuffledPlaylist'))
    app.add_url_rule('/delete-playlist/<playlistID>',view_func=DeletePlaylist.as_view('delete_playlist'))
    app.add_url_rule('/settings',view_func=Settings.as_view('settings'))
    app.add_url_rule('/setup',view_func=Setup.as_view('setup'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html',title="404"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html',title="500"), 500

    @app.errorhandler(ConnectionError)
    def connection_error(e):
        print('This is a connection error')
        return render_template('connection_error.html', title='Connection Error', token=APP.yaml.token())

    # @app.errorhandler(AttributeError)
    # def attribute_connection_error(e):
    #     print('This is a connection error')
    #     return render_template('connection_error.html', title='Connection Error', token=APP.yaml.token())

    @socketio.on('message')
    def handle_message(data):
        print('received message: ' + data)

    @socketio.on('startPlexLogin')
    def startPlexLogin():

        r = APP.plexLogin.generatePin()
        authUrl = APP.plexLogin.generateAuthUrl()

        emit('plexLoadingRedirect',authUrl)

    @socketio.on('plexLoginPoll')
    def plexLoginPoll():
        APP.plexLogin.waitPinResponse()

    @socketio.on('getShowData')
    def getShowData(show_id):
        emit('showMetadata',APP.plex.getShowMetadata(show_id))

    @socketio.on('updateSettingValue')
    def updateSettingValue(setting, input, value):
        
        if APP.updateSettings(value, setting, input):
            emit('settingValueValid')
        else:
            emit('settingValueInvalid')

    @socketio.on('checkPlexUrl')
    def checkPlexUrl(url):
        

        if len(url) == 0:
            print(f'This is my URL: {url} with length {len(url)}')
            emit('plexURLMissing')
        
        val = URLValidator()
        try:
            val(url)
            emit('plexValidURL', url)
        except ValidationError as e:
            print(f'My Error: {e}')
            emit('plexInvalidURL')

    @socketio.on('checkPlexConnection')
    def checkPlexConnection(url):
        urlSplit = url.split(':')
        
        if APP.plex.checkConnection(url):
            APP.yaml.update_config_name('PLEX','PMS_PROTOCOL',urlSplit[0])
            APP.yaml.update_config_name('PLEX','PMS_URL',urlSplit[1][2:])
            APP.yaml.update_config_name('PLEX','PMS_PORT',int(urlSplit[2]))
            APP.firstUse.updateFirst()
            emit('plexConnectionSuccesful')
        else:
            emit('plexConnectionUnsuccesful')

    return app, socketio