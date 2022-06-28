from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from constants import Constants


class BE_SWAGGER:

    def prepare_swagger_UI_for_BE(self):
        app = Flask(__name__)
        app.config.from_pyfile('config.py')

        print("swagger specific")
        # swagger specific #
        SWAGGER_FILE = '/static/docs.json'
        SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(Constants.SWAGGER_URL, SWAGGER_FILE)
        app.register_blueprint(SWAGGERUI_BLUEPRINT)
        # end swagger specific #
        print("end swagger specific")

        app.run(host="0.0.0.0", ssl_context='adhoc')    # If this line kept we can access 5000/docs 
                                                        # but server.py and be_swagger.py both will run at same time

