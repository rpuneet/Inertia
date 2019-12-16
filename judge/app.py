from flask import Blueprint
from flask_restful import Api

from resources.compile import Compile
from resources.execute import Execute
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routes
api.add_resource(Compile, '/compile') 
api.add_resource(Execute , '/execute')