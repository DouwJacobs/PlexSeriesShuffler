from flask import render_template, session, request, redirect, url_for
from flask.views import MethodView

from sockets import APP

class Logout(MethodView):

    def get(self):

        if APP.yaml.token():
            APP.logout()
            return redirect(url_for('sign_in'))
        else:
            return redirect(url_for('sign_in'))
