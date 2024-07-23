from app import flask_app, celery_app
from waitress import serve

if __name__ == "__main__":
    flask_app.run()

