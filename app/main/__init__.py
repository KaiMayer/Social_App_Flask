from flask import Blueprint
from app.main.models import Permission

main = Blueprint('main', __name__)

from . import views, errors


@main.app_context_processor
def insert_permissions():
    return dict(Permission=Permission)
