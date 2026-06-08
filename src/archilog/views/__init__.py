
from flask import Flask

from archilog.data import init_db


def create_app() -> Flask:
    """Application factory Flask."""
    app = Flask(__name__, template_folder="../templates")

    init_db()

    from archilog.views.web import web_ui
    from archilog.views.api import api

    app.register_blueprint(web_ui, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api")

    return app
