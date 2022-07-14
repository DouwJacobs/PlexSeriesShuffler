from functools import wraps
from flask import g, request, redirect, url_for

from main import plex, yaml

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if yaml.token() is None:
            return redirect(url_for('sign_in', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def checkPlexConnection(f):
    @wraps(f)
    def checkPlexCon(*args, **kwargs):
        if plex.checkConnection() is None:
            return f(*args, **kwargs)
        return f(*args, **kwargs)
    return checkPlexCon