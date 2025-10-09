import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

import flaskr.config as config
from flaskr.blueprints.images import image
from flaskr.resources.character import Character, CharacterList
from flaskr.resources.character_partners import CharacterPartnersResource
from flaskr.resources.partnership import Partnership, PartnershipList
from flaskr.resources.offspring import Offspring, OffspringList
from flaskr.resources.partners import Partners, PartnersList


def create_app(test_config=None):
    # create and configure the app
    load_dotenv()

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
    api.add_resource(CharacterPartnersResource,
                     '/api/v1/characters/<cid>/partners')

    api.add_resource(PartnershipList, '/api/v1/partnerships')
    api.add_resource(Partnership, '/api/v1/partnerships/<id>')

    api.add_resource(PartnersList, '/api/v1/partnerships/<pid>/participants')
    api.add_resource(Partners, '/api/v1/partnerships/<pid>/participants/<cid>')

    api.add_resource(OffspringList,
                     '/api/v1/partnerships/<pid>/offspring')
    api.add_resource(Offspring,
                     '/api/v1/partnerships/<pid>/offspring/<oid>')

    app.register_blueprint(image)
    CORS(app)
    return app
