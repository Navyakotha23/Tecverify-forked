from flask_swagger_ui import get_swaggerui_blueprint

from constants import Constants


class BE_SWAGGER:

    def __init__(self, app) -> None:
        self.app = app

    def prepare_swagger_UI_for_BE(self):
        """
        This method implements Swagger UI for TecVerify backend.
        """
        SWAGGER_FILE = '/static/docs.json'
        SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(Constants.SWAGGER_URL, SWAGGER_FILE)
        self.app.register_blueprint(SWAGGERUI_BLUEPRINT)

        