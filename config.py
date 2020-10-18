import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
   SECRET_KEY = "super secret key"
   SQLALCHEMY_DATABASE_URI = (
           'sqlite:///' + os.path.join(BASE_DIR, 'db/users.db')
   )
   SQLALCHEMY_TRACK_MODIFICATIONS = True

