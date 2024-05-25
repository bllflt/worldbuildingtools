import os

from flask import Flask

from flaskr.resources.character import CharacterList
from flask_restful import Api

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///green.sqlite"

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr.model import db
    from flaskr.schemas.character import ma   

    db.init_app(app)
    ma.init_app(app)

    api = Api(app)
    api.add_resource(CharacterList, '/api/v1/character')

    return app
