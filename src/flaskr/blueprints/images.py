from flask import Blueprint, send_file
import flaskr.config as config
from pathlib import Path

image = Blueprint('character_image', __name__)

img_dir = Path(
    '/Users/joel/Library/Mobile Documents/com~apple~CloudDocs/Covenant of Shifting Lights/World Building/images')


@image.route('/images/<image_uri>')
def show(image_uri):
    try:
        return send_file(Path(config.image_dir).joinpath(image_uri),
                         mimetype='image/png')
    except (Exception) as e:
        return ''

