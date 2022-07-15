from flask import render_template, session, request, redirect, url_for
from flask.views import MethodView

from controllers.decorators import login_required

from sockets import APP

class Setup(MethodView):

    @login_required
    def get(self):

        return render_template('setup.html', 
                                    title="Setup", url=APP.yaml.baseurl())
