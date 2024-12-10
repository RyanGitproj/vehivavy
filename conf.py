from os import environ as env


class Configuration:
    '''
        Retrieves the value from the environment.
        Takes the default value if not defined.
    '''
    ADAPTER = 'MYSQL'

    DB_FILE = 'ampalibe.db'
    DB_HOST = "34.141.105.101"
    DB_USER = 'root'
    DB_PASSWORD = '07ke6u%56O5x'
    DB_PORT = 3306
    DB_NAME = 'vehivavy'
    SRV_PROTOCOL = ''

    # DB_HOST = "localhost"
    # DB_USER = 'root'
    # DB_PASSWORD = ''
    # DB_PORT = 3306
    # DB_NAME = 'vehivavy'
    # SRV_PROTOCOL = ''

    # REDIS_HOST = "34.141.105.101"  
    # REDIS_PORT = 6379         
    # REDIS_PASSWORD = '07ke6u%56O5x'


    ACCESS_TOKEN = 'EAAWhes9F3lcBO9dlrCTq8V2XHSzZC9ndJg5PRFZCkALz1bC7ag5ZBZBzR89YAbh856ld1ifMJvo3xKvYTSAwVk99eRYR6kJIjlu7AR1mQfeNZBAhkBqKRNur90cC67915Q159pC00UgQpEPhJHWg0Y0iTZBoNlMJAuurpJzwRI5ZAvIJf2SAJV2sLkOpPgzOZBAwZAAZDZD'
    VERIF_TOKEN = 'VEHIVAVYAPP'

    APP_HOST = "0.0.0.0"
    APP_PORT = 4555
    APP_URL = ''