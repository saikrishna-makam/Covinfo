from flask import Blueprint
from ..models import Permission

covinfo = Blueprint('covinfo', __name__)

@covinfo.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
    
from . import views, errors
