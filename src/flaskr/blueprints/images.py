from pathlib import Path

from flask import Blueprint, send_file

from flaskr.config import Config

image = Blueprint('character_image', __name__)


@image.route('/images/<image_uri>')
def show(image_uri):
    try:
        return send_file(Path(Config.image_dir).joinpath(image_uri),
                         mimetype='image/png')
    except (Exception) as e:
        return '', 404
