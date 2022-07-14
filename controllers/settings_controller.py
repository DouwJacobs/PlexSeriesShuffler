from flask import render_template, redirect, url_for, session
from flask.views import MethodView

from controllers.decorators import login_required

from main import yaml

class Settings(MethodView):

    @login_required
    def get(self):



        return render_template('settings.html', 
                                    title="Settings", token=yaml.token(), settings=yaml.readConfig())

