from flask import Blueprint
from flask_restful import Api

from resources.compile import Compile

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routes
api.add_resource(Compile, '/compile')