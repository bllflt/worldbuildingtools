import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

import flaskr.config as config
from flaskr.blueprints.images import image
from flaskr.resources.character import Character, CharacterList


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.database

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
    api.add_resource(CharacterList, '/api/v1/characters')
    api.add_resource(Character, '/api/v1/characters/<cid>')

    app.register_blueprint(image)
    CORS(app)
    return app
