import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from flaskr.blueprints.images import image
from flaskr.config import Config
from flaskr.resources.character import Character, CharacterList
from flaskr.resources.character_connections import CharacterConnections
from flaskr.resources.offspring import Offspring, OffspringList
from flaskr.resources.partners import Partners, PartnersList
from flaskr.resources.partnership import Partnership, PartnershipList


def create_app():
    # create and configure the app
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.database

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # pylint: disable=import-outside-toplevel
    from flaskr.model import db
    from flaskr.schemas.character import ma

    db.init_app(app)
    ma.init_app(app)

    api = Api(app)
    api.add_resource(CharacterList, '/api/v1/characters')
    api.add_resource(Character, '/api/v1/characters/<cid>')
    
    api.add_resource(CharacterConnections,
                     '/api/v1/characters/<cid>/connections')

    api.add_resource(PartnershipList, '/api/v1/partnerships')
    api.add_resource(Partnership, '/api/v1/partnerships/<id>')

    api.add_resource(PartnersList, '/api/v1/partnerships/<pid>/participants')
    api.add_resource(Partners, '/api/v1/partnerships/<pid>/participants/<cid>')

    api.add_resource(OffspringList,
                     '/api/v1/partnerships/<pid>/offspring')
    api.add_resource(Offspring,
                     '/api/v1/partnerships/<pid>/offspring/<cid>')

    app.register_blueprint(image)
    CORS(app)
    return app
