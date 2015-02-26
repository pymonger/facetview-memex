class Config(object):
    SECRET_KEY = 'secret key'
    ELASTICSEARCH_URL = 'http://127.0.0.1:9200'

    # for MEMEX app
    MEMEX_ELASTICSEARCH_INDEX = 'mrs2'
    MEMEX_ELASTICSEARCH_SETTINGS = '../config/es_settings.json'
    MEMEX_ELASTICSEARCH_MAPPING = '../config/es_mapping.json'


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

    CACHE_TYPE = 'simple'


class DevConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    SQLALCHEMY_ECHO = True

    CACHE_TYPE = 'null'

    # This allows us to test the forms from WTForm
    WTF_CSRF_ENABLED = False
