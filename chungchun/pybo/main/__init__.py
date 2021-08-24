from flask import Blueprint

bp = Blueprint('main', __name__)

from pybo.main import chat, main_views
