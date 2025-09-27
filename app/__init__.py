# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # Import routes only inside the factory to avoid circulars
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app
