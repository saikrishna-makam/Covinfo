from flask import render_template, current_app as app
from . import covinfo

@covinfo.app_errorhandler(404)
def page_not_found(e):
    app.logger.warning('404: Page Not Found')
    return render_template('404.html'), 404
    

@covinfo.app_errorhandler(500)
def internal_server_error(e):
    app.logger.warning('500: Internal Server Error')
    return render_template('500.html'), 500
    
@covinfo.app_errorhandler(403)
def forbidden_error(e):
    app.logger.warning('403: Forbidden Error')
    return render_template('403.html'), 403
