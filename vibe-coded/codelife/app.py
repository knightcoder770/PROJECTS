from flask import Flask
from routes.setup import setup_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp
from routes.timer import timer_bp
from routes.gitpush import gitpush_bp
from routes.ai import ai_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "codelife-dev-key-change-in-prod"

    app.register_blueprint(setup_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(timer_bp)
    app.register_blueprint(gitpush_bp)
    app.register_blueprint(ai_bp)

    return app
