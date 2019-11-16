# __init__.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import sys
from flask import Flask
from phenome_core.core.database.db import db_session
from phenome_core.core.base.logger import get_logger

# create the Flask application
flask_app = Flask(__name__, instance_relative_config=True)

# create the main logger
logger = get_logger(None, None, flask_app)

# perform local predictions - now always set to True but
# may be turned off once cloud service is complete
local_predictions = True

# create a shutdown hook that will cleanly remove the db_session
@flask_app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# local helper for error logging
def _output_init_error(component, error):
    message = "Error while trying to initialize '{}': {}"
    logger.error(message.format(component, error))


# Main Method use to Initialize the DB
def initialize_database():

    try:

        # this should init the database engine and session
        import phenome_core.core.database.db

        # now create the data handler and open the DB, start reading META
        from phenome_core.core.database.create import CreateDB
        data_handler = CreateDB()
        data_handler.create()

    except RuntimeError as error:
        logger.error("Error while trying to initialize DB {}".format(error))


# load any and all defined apps in the local META configuration
def load_application():

    # initialize APP environment
    from phenome_core.core import registered_apps as app_initializer

    try:
        # register itself
        app_initializer.register_self()

    except RuntimeError as error:
        _output_init_error('self', error)

    try:
        # initialize all configured APPs
        app_initializer.initialize_apps(flask_app)

    except RuntimeError as error:
        _output_init_error('APPs', error)


# load pollers to start collecting IoT Data
def load_pollers():

    try:
        # now try to start any registered pollers
        from phenome_core.core.globals import registered_pollers as poller_initializer
        poller_initializer.initialize_pollers()

    except RuntimeError as error:
        _output_init_error('Pollers', error)


def load_prediction_manager():

    try:

        # create and start the Prediction Model Managers
        from phenome_core.core.learning.model.model_manager import ModelManager
        from phenome_core.core.learning.model.data_manager import DataManager

        model_manager = ModelManager()
        data_manager = DataManager()

        model_manager.start()
        data_manager.start()

    except RuntimeError as error:
        _output_init_error('PredictionModels', error)


# Main method that will init the ENV on startup
def initialize_environment():

    # by default, we will load up the APPS
    load_app_data = True

    # Who is the caller? If it's unit tests or console, we do not want to load APPS

    if hasattr(sys, '_unit_tests_load_app_data'):
        load_app_data = sys._unit_tests_load_app_data

    if len(sys.argv[0]) == 0 or 'pydevconsole.py' in sys.argv[0]:
        # calling from command line or dev interactive shell
        sys._interactive_shell = True
        load_app_data = False

    # Load some core default configuration from phenome_core/core/default.py
    flask_app.config.from_object('phenome_core.core.default')

    # Load app or custom configuration from phenome/config/default.py
    flask_app.config.from_object('phenome.config.default')

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    # In your shell script:  export APP_CONFIG_FILE={path}/my_config_file.py
    try:
        flask_app.config.from_envvar('APP_CONFIG_FILE')
    except:
        pass

    # first INIT the DB
    initialize_database()

    if load_app_data:
        load_application()
        load_pollers()

    if local_predictions:
        load_prediction_manager()




