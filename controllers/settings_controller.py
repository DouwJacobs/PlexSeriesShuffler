from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required, checkFirstTime

from sockets import APP

class Settings(MethodView):

    @login_required
    @checkFirstTime
    def get(self):

        return render_template('settings.html', 
                                    title="Settings", token=APP.yaml.token(), settings=APP.yaml.readConfig())

