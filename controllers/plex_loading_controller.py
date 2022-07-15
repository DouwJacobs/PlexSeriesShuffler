from flask import render_template, session, request, redirect
from flask.views import MethodView

from sockets import APP

class PlexLoading(MethodView):

    def get(self):

        from main import app
        from flask_executor import Executor

        executor = Executor(app)

        r = APP.plexLogin.generatePin()
        authUrl = APP.plexLogin.generateAuthUrl()

        executor.submit(APP.plexLogin.waitPinResponse)

        return redirect(authUrl)