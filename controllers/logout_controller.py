from flask import render_template, session, request, redirect, url_for
from flask.views import MethodView

from main import yaml

class Logout(MethodView):

    def get(self):

        if yaml.token():
            yaml.logout()
            return redirect(url_for('sign_in'))
        else:
            return redirect(url_for('sign_in'))
