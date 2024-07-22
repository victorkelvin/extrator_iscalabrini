
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
class DevelopmentConfig():
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://iscalabrini:IScalabrini@localhost:5432/iscalabrini_db'
    CELERY_BROKER_URL = 'amqp://localhost:5672'
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
class ProductionConfig():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://iscalabrini:IScalabrini@localhost:5432/iscalabrini_db'
    CELERY_BROKER_URL = 'amqp://localhost:5672'
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True





