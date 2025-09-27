from __future__ import annotations

from flask import Flask


def create_app() -> Flask:
    """Flask application factory."""
    app = Flask(__name__)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    return app

app = create_app()
