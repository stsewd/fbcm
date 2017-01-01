from os import path

here = path.abspath(path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'some_secret_key'

    # Database configs
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWD = '1234'
    DB_NAME = 'testperson'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
