"""
Vues de l'application : CLI et Web.
Application factory Flask.
"""
import logging
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from archilog.data import init_db

csrf = CSRFProtect()


def create_app() -> Flask:
    """Application factory Flask."""
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")

    # Logging : fichier + stdout
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("archilog.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    csrf.init_app(app)
    init_db()

    from archilog.views.web import web_ui
    from archilog.views.api import api

    app.register_blueprint(web_ui, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api")

    # Exclure l'API du CSRF (authentification par token)
    csrf.exempt(api)

    # Injecte la liste des cagnottes dans tous les templates
    from archilog import domain

    @app.context_processor
    def inject_cagnottes():
        try:
            return {"all_cagnottes": domain.lister_cagnottes()}
        except Exception:
            return {"all_cagnottes": []}

    return app
