from flask import Blueprint
from app.main.models import Permission

# register main blue print
main = Blueprint('main', __name__)

from . import views, errors
from app.main.models import Permission


# add Permissions to Context processors to make it available to all templates during rendering
@main.app_context_processor
def insert_permissions():
    return dict(Permission=Permission)
