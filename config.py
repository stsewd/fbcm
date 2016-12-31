from os import path

here = path.abspath(path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'some_secret_key'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
