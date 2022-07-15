########################################################################
#################        Importing packages      #######################
########################################################################
from flask import Flask, session
from flask_bootstrap import Bootstrap
import datetime
import os
import jinja2
import sys

def create_app():
    app = Flask(__name__) # creates the Flask instance, __name__ is the name of the current Python module
    app.config['SECRET_KEY'] = 'secret-key-goes-here' # it is used by Flask and extensions to keep data safe
        
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    
    Bootstrap(app)
        
    template_loader = jinja2.ChoiceLoader([app.jinja_loader, jinja2.FileSystemLoader('/static')])
    app.jinja_loader = template_loader
        
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app




    
