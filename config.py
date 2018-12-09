import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = "[FoodDairyProject]"
    MAIL_DEFAULT_SENDER = "FoodDairy Admin"
    ADMIN = os.environ.get("ADMIN")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get("DEV_DATABASE_URI") or f"sqlite:///{os.path.join(basedir, 'fooddairydb.sqlite3')}"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get("TEST_DATABASE_URI") or f"sqlite:///{os.path.join(basedir, 'fooddairydb.sqlite3')}"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get("DATABASE_URI") or f"sqlite:///{os.path.join(basedir, 'fooddairydb.sqlite3')}"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
