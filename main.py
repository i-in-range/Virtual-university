from flask import Flask
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint

from api_v1 import api_bp
from models import db
from config import BaseConfig
from generate import create_all_data


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    return app


app = create_app(BaseConfig)
migrate = Migrate(app, db)


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Virtual University API"
    }
)


app.register_blueprint(api_bp, url_prefix='/api/v1')
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# @app.before_first_request
# def db_initialize():
#     with app.app_context():
#         db.create_all()
#         create_all_data()


if __name__ == '__main__':
    app.run()
