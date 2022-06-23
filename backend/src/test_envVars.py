from flask import Flask

from constants import Constants

class Test_EnvVars:
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    DUMMY_ENV_VAR = app.config['DUMMY_ENV_VAR']
    # print("test_envVars.py DUMMY_ENV_VAR: ", DUMMY_ENV_VAR)

    print("test_envVars.py Constants.EMBEDDED: ", Constants.EMBEDDED)
    