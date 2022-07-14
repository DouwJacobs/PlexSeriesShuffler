from flask import render_template, session, request, redirect, url_for
from flask.views import MethodView

from main import yaml

class SignIn(MethodView):

    def get(self):

        if yaml.token():
            return redirect(url_for('index'))
        else:
            return render_template('sign_in.html', 
                                    title="Sign In", token=yaml.token())

    def post(self):

        return redirect(url_for('plex_loading'))