"""
the Flask application object creation has to be in the __init__.py file.
That way each module can import it safely and the __name__ variable will
resolve to the correct package.

** all the view functions (the ones with a route() decorator on top)
have to be imported in the __init__.py file.
Not the object itself, but the module it is in.
Import the view module after the application object is created.
"""
# Import flask and template operators
from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# ----------------------------------------------------------------------------#
#  App Config.
# ----------------------------------------------------------------------------#

# Define the WSGI application object
app = Flask(__name__, instance_relative_config=True)
# load the default configuration in config/default.py
app.config.from_object('config.default')
# loads configuration from instance/config.py
app.config.from_pyfile('config.py')
# APP_CONFIG_FILE should be the absolute path to env specific configuration
app.config.from_envvar('APP_CONFIG_FILE')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# initialize flask_migrate
migrate = Migrate(app, db)

# Flask Moment for datetime formatting
moment = Moment(app)

# circular import generally a bad idea; ok here since these not actually used
import postmates.views
