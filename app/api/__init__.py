from flask import Blueprint

# Створюємо Blueprint 'api'
api = Blueprint('api', __name__, url_prefix='/api')

# Імпортуємо маршрути, щоб вони зареєструвалися
from . import routes