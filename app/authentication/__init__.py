from flask import Blueprint
# Authentication blueprint creation
authentication = Blueprint('authentication', __name__)

# import and associate routes with Blueprint
from . import views
