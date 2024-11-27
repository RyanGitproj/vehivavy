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

    ACCESS_TOKEN = 'EAAWhes9F3lcBOwxtu73RG1JMIxtKgjBZCqsVsaQJrIZCFwRrOrytBEvAcCnCjNrJHYV2Voh2X5z9FqONNF8o5pkUhOYoNbQCNjLo0Qdg9MzPqFLqDZAqO0uy8viLyx4EtckudBzVRVxiOawOX1OQXNzNZCRfZCYQf1ekTlPact2UZC5e8ynv7AwmUuq4j6TLCiMAZDZD'
    VERIF_TOKEN = 'VEHIVAVYAPP'

    APP_HOST = "0.0.0.0"
    APP_PORT = 4555
    APP_URL = ''