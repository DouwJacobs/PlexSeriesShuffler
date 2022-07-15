from flask import render_template, session, request, redirect, url_for
from flask.views import MethodView

from sockets import APP

class SignIn(MethodView):

    def get(self):

        if APP.yaml.token():
            return redirect(url_for('index'))
        else:
            return render_template('sign_in.html', 
                                    title="Sign In", token=APP.yaml.token())

    def post(self):

        return redirect(url_for('plex_loading'))