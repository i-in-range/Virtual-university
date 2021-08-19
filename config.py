class BaseConfig(object):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pass@localhost:5432/univ_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_RELOADER = False
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pass@localhost:5432/test_db'
