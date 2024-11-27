from os import environ as env


class Configuration:
    '''
        Retrieves the value from the environment.
        Takes the default value if not defined.
    '''
    ADAPTER = 'MYSQL'

    DB_FILE = 'ampalibe.db'
    DB_HOST = "DB_HOST"
    DB_USER = 'root'
    DB_PASSWORD = 'PASSWORD'
    DB_PORT = 3306
    DB_NAME = 'vosaryai'
    SRV_PROTOCOL = ''

    ACCESS_TOKEN = 'TOKEN'
    VERIF_TOKEN = 'VEHIVAVYAPP'

    APP_HOST = "0.0.0.0"
    APP_PORT = 4555
    APP_URL = ''