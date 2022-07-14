from http import client
import requests
import uuid
from flask import session, redirect, url_for
import socket   
from time import sleep
import urllib

from main import yaml, socketio, app

from flask_socketio import emit


class PlexLogin:

    def __init__(self):

        self.hostname = socket.gethostname()
        self.IPAddr = socket.gethostbyname(self.hostname) 
        self.appPort = yaml.get_config_name('PLEX_SERIES_SHUFFLER','PORT')

        self.apiURL = yaml.get_config_name('PLEX_LOGIN','PLEX_API_URL')

    def verifyAccessToken(self,accessToken):

        if not session.get('clientUuid'):
            clientUuid = str(uuid.uuid4())
        else:
            clientUuid = session['clientUuid']

        params = {
            'X-Plex-Product': yaml.get_config_name('PLEX_SERIES_SHUFFLER','PRODUCT_NAME'),
            'X-Plex-Client-Identifier': clientUuid,
            'X-Plex-Token': accessToken

        }

        headers = {'accept': 'application/json'}

        r = requests.get(self.apiURL + '/user', headers=headers, params=params)

        if r.status_code == 200:
            yaml.update_config_name('PLEX','PLEX_ACCESS_TOKEN', accessToken)
            session['clientUuid'] = clientUuid

            return True
        
        elif r.status_code == 401:
            return False


    def generatePin(self):

        if not session.get('clientUuid'):
            clientUuid = str(uuid.uuid4())
        else:
            clientUuid = session['clientUuid']

        params = {
            'X-Plex-Product': yaml.get_config_name('PLEX_SERIES_SHUFFLER','PRODUCT_NAME') ,
            'X-Plex-Client-Identifier': clientUuid,
            'strong': 'true',
            'origin':f"http://{self.IPAddr}:{self.appPort }"

        }

        headers = {'accept': 'application/json'}

        r = requests.post(self.apiURL  + '/pins', headers=headers, params=params)

        if r.status_code == 201:
            session['code'] = r.json()['code']
            session['id'] = r.json()['id']
            session['clientUuid'] = clientUuid
        return r

    def generateAuthUrl(self):

        params = {
        'clientID': session['clientUuid'],
        'code': session['code'],
        'context%5Bdevice%5D%5Bproduct%5D': yaml.get_config_name('PLEX_SERIES_SHUFFLER','PRODUCT_NAME') ,
        'origin':f"http://{self.IPAddr}:{self.appPort }"
        }

        parsedParams = urllib.parse.urlencode(params)

        authUrl = f"https://app.plex.tv/auth#?{parsedParams}"

        return authUrl

    def verifyPinId(self):

        if not session.get('clientUuid'):
            clientUuid = str(uuid.uuid4())
        else:
            clientUuid = session['clientUuid']

        params = {
            'X-Plex-Client-Identifier': clientUuid,
            'accept': 'application/json',
            'code' : session['code'],

        }

        headers = {'accept': 'application/json'}

        r = requests.get(self.apiURL  + f"/pins/{session['id']}", params=params, headers=headers)

        return r

    def waitPinResponse(self):

        verified = False
        count = 0

        while verified == False:
            r = self.verifyPinId()
            sleep(1)
            count += 1

            if count < yaml.get_config_name('PLEX_LOGIN','PLEX_LOGIN_TIMEOUT'):
                if r.json()['authToken']:
                    yaml.update_config_name('PLEX','PLEX_ACCESS_TOKEN', r.json()['authToken'])

                    verified = True
                    emit('userLoggedIn')
                    
            else:
                verified = True
                emit('loginTimedOut')












