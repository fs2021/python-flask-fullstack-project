from flask import Flask

from config import Config
from flask_mongoengine import MongoEngine
#from werkzeug.uitls import cached_property

from flask_restx import Api

api = Api()

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)

api.init_app(app)
# it is important to import Afer app=Flask()
from application import routes