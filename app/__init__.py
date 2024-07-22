from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from variaveis import DevelopmentConfig
# from config import celery_init_app, create_app
from celery import Celery, Task

class FlaskTask(Task):
    def __call__(self, *args: object, **kwargs: object) -> object:
        with flask_app.app_context():
            return self.run(*args, **kwargs)

flask_app = Flask(__name__)
flask_app.config.from_mapping(
    CELERY=dict(
        broker_url="amqp://localhost:5672",
        # result_backend="redis://localhost",
        task_ignore_result=True,
    )
)

celery_app = Celery(flask_app.name)
celery_app.config_from_object(flask_app.config["CELERY"])
celery_app.Task = FlaskTask

flask_app.config.from_object(DevelopmentConfig)


db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)
migrate.init_app(flask_app, db, compare_type=True )

from app.models import models
from app.controllers import routes, extratores

with flask_app.app_context():
    migrate.init_app(flask_app, db, compare_type=True )
    db.create_all()
    db.session.commit()
