from flask import Flask

from . import math_core  
__all__ = ["create_app", "math_core"]

def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app
