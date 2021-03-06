import os
import click
from flask_migrate import Migrate, upgrade
from flask_ngrok import run_with_ngrok
from app import create_app, db
from app.models import User, Role


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
run_with_ngrok(app)

def start_ngrok():
    from pyngrok import ngrok

    url = ngrok.connect(5000).public_url
    print(' * Tunnel URL:', url)

if app.config['START_NGROK']:
    start_ngrok()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    
@app.cli.command()
def deploy():
    upgrade()
    Role.insert_roles()
