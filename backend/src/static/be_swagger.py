from flask_swagger_ui import get_swaggerui_blueprint

from common.constants import Constants


class BE_SWAGGER:

    def __init__(self, app) -> None:
        self.app = app

    def prepare_swagger_UI_for_BE(self):
        """
        This method implements Swagger UI for TecVerify backend.
        """
        SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(Constants.SWAGGER_URL, Constants.SWAGGER_FILE)
        self.app.register_blueprint(SWAGGERUI_BLUEPRINT)

        