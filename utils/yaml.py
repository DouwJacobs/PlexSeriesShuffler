import yaml
import os

from utils.plex_tools import PlexTools


class YamlTools:

    def __init__(self, configPath):

        self.configPath = configPath

        self.createConfig()

    def defaultConfig(self):

        config = { 
            'PLEX' : {
                'PLEX_ACCESS_TOKEN' : None,
                'PMS_URL': '127.0.0.1',
                'PMS_PORT': 32400,
                'PMS_PROTOCOL': 'http'
                },
            'PLEX_LOGIN' : {
                'PLEX_API_URL' : 'https://plex.tv/api/v2',
                'PLEX_LOGIN_TIMEOUT' : 120
            },
            'PLEX_SERIES_SHUFFLER':{
                'PRODUCT_NAME' : 'Series Shuffler',
                'PORT' : 5000
            }
            }

        return config

    def checkValueType(self, base, name, value):

        config = { 
            'PLEX' : {
                'PLEX_ACCESS_TOKEN' : 'str',
                'PMS_URL': 'str',
                'PMS_PORT': 'int',
                'PMS_PROTOCOL': 'str'
                },
            'PLEX_LOGIN' : {
                'PLEX_API_URL' : 'str',
                'PLEX_LOGIN_TIMEOUT' : 'int'
            },
            'PLEX_SERIES_SHUFFLER':{
                'PRODUCT_NAME' : 'str',
                'PORT' : 'int'
            }
            }

        if config[base][name] == 'int':
            try:
                value = int(value)
            except Exception as e:
                pass

        validValue = type(value) == eval(config[base][name])

        print(validValue)

        return(validValue)


    def checkConfigExist(self):

        return os.path.exists(self.configPath)

    def createConfig(self):

        if not self.checkConfigExist():
            self.writeConfig(self.defaultConfig())

    def readConfig(self):

        with open(self.configPath) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        return data


    def writeConfig(self,data):

        with open(self.configPath, 'w') as f:

            yaml.dump(data, f)

    def get_config_name(self,base, name):

        return self.readConfig()[base][name]

    def update_config_name(self, base, name, value):

        if self.checkValueType(base, name, value):

            data = self.readConfig()
            
            data[base][name] = value

            self.writeConfig(data)

            if base in ['PLEX']:
                global plex
                plex = PlexTools(self.baseurl(), self.token())

            return True
        else:
            return False

    def token(self):

        return self.get_config_name('PLEX','PLEX_ACCESS_TOKEN')

    def logout(self):

        self.update_config_name('PLEX','PLEX_ACCESS_TOKEN',None)

    def baseurl(self):

        data = self.readConfig()['PLEX']

        protocol = data['PMS_PROTOCOL']
        ip_addr = data['PMS_URL']
        port = data['PMS_PORT']

        return f'{protocol}://{ip_addr}:{port}'