from flask import Blueprint

model_training_bp = Blueprint('model_training', __name__, template_folder='templates', static_folder='static')

from . import routes