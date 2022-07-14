from flask import render_template, session, request, redirect
from flask.views import MethodView

from main import plexLogin


class PlexLoading(MethodView):

    def get(self):

        from main import app
        from flask_executor import Executor

        executor = Executor(app)

        r = plexLogin.generatePin()
        authUrl = plexLogin.generateAuthUrl()

        executor.submit(plexLogin.waitPinResponse)

        return redirect(authUrl)