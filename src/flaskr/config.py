import os


class Config:
    image_dir = os.environ['IMAGE_DIR']
    database = os.environ['DATABASE_URI']
