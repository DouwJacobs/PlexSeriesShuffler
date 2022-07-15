from flask import Blueprint
import utils

########################################################################################

# our main blueprint
main = Blueprint('main', __name__)

APP = utils.Main()

import sockets

app, socketio = sockets.initialise()

########################################################################################

if __name__ == '__main__':
    
    socketio.run(app, debug=True, host='0.0.0.0', port=APP.yaml.get_config_name('PLEX_SERIES_SHUFFLER','PORT'))