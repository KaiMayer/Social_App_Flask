from flask import Blueprint

# create user blueprint
users = Blueprint('users', __name__)

# add routes to blueprint
from . import views