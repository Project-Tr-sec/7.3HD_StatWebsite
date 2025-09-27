from flask import Flask

def create_app() -> Flask:
    # __name__ ensures Flask uses app/templates automatically
    app = Flask(__name__)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
