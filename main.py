from flask_socketio import SocketIO, emit
from flask import Blueprint, session, render_template, redirect
from __init__ import create_app

from flask_session import Session
from requests.exceptions import ConnectionError

########################################################################################
# our main blueprint
main = Blueprint('main', __name__)
app = create_app() # we initialize our flask app using the __init__.py function

Session(app)
socketio = SocketIO(app, manage_session=False)

from utils.yaml import YamlTools
yaml = YamlTools('/config/config.yml')

from utils.plexLogin import PlexLogin
plexLogin = PlexLogin()

from utils.plex_tools import PlexTools
plex = PlexTools(yaml.baseurl(), yaml.token())

########################################################################################

from controllers.index_controller import Index
from controllers.sign_in_controller import SignIn
from controllers.logout_controller import Logout
from controllers.playlist_controller import Playlist
from controllers.playlists_controller import Playlists
from controllers.createShuffledPlaylist_controller import createShuffledPlaylist
from controllers.delete_playlist_controller import DeletePlaylist
from controllers.settings_controller import Settings

app.add_url_rule('/', view_func=Index.as_view('index'))
app.add_url_rule('/sign_in', view_func=SignIn.as_view('sign_in'))
app.add_url_rule('/logout',view_func=Logout.as_view('logout'))
app.add_url_rule('/playlist/<playlistID>',view_func=Playlist.as_view('playlist'))
app.add_url_rule('/playlists',view_func=Playlists.as_view('playlists'))
app.add_url_rule('/create-shuffled-playlist',view_func=createShuffledPlaylist.as_view('createShuffledPlaylist'))
app.add_url_rule('/delete-playlist/<playlistID>',view_func=DeletePlaylist.as_view('delete_playlist'))
app.add_url_rule('/settings',view_func=Settings.as_view('settings'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',title="404"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html',title="500"), 500

@app.errorhandler(ConnectionError)
def connection_error(e):
    print('This is a connection error')
    return render_template('connection_error.html', title='Connection Error', token=yaml.token())

@app.errorhandler(AttributeError)
def attribute_connection_error(e):
    print('This is a connection error')
    return render_template('connection_error.html', title='Connection Error', token=yaml.token())

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('startPlexLogin')
def startPlexLogin():

    r = plexLogin.generatePin()
    authUrl = plexLogin.generateAuthUrl()

    emit('plexLoadingRedirect',authUrl)

@socketio.on('plexLoginPoll')
def plexLoginPoll():
    print('Triggered')
    plexLogin.waitPinResponse()

@socketio.on('getShowData')
def getShowData(show_id):
    emit('showMetadata',plex.getShowMetadata(show_id))

@socketio.on('updateSettingValue')
def updateSettingValue(setting, input, value):
    
    if yaml.update_config_name(value, setting, input):
        emit('settingValueValid')
    else:
        emit('settingValueInvalid')

if __name__ == '__main__':
    
    socketio.run(app, debug=True, host='0.0.0.0', port=yaml.get_config_name('PLEX_SERIES_SHUFFLER','PORT'))