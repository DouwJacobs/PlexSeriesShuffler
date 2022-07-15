from functools import wraps
from flask import g, request, redirect, url_for, render_template
import sys

from sockets import APP

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if APP.yaml.token() is None:
            return redirect(url_for('sign_in', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def checkFirstTime(f):
    @wraps(f)
    def decoreated_function(*args, **kwargs):
        if APP.firstUse.first():
            return redirect(url_for('setup'))
        return f(*args, **kwargs)
    return decoreated_function

def checkPlexConnection(f):
    @wraps(f)
    def decoreated_function(*args, **kwargs):
        if not APP.plex.checkConnection():
            return render_template('connection_error.html', title='Connection Error', token=APP.yaml.token())
        return f(*args, **kwargs)
    return decoreated_function

# def checkPlexConnection(f):
#     @wraps(f)
#     def checkPlexCon(*args, **kwargs):
#         if not APP.plex.checkConnection():
#             return f(*args, **kwargs)
#         return f(*args, **kwargs)
#     return checkPlexCon