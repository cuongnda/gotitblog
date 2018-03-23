import os


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    GOOGLE_API_CLIENT_ID = "406704713101-d6a8tbbfq6cmmf16vtljh6gj71bn0ro9.apps.googleusercontent.com"
    GOOGLE_API_CLIENT_SECRET = "wvtkTq8IOxtOMHs2bvuN7kiV"
    FACEBOOK_API_CLIENT_ID = "2032137377002819"
    FACEBOOK_API_CLIENT_SECRETE = "f4857526cfa52e0e390e1943dd636225"


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:111111@localhost/test_db'
    DEBUG = True


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
