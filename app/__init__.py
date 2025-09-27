"""
Math Core Application Package
"""
from flask import Flask


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # Import routes only inside the factory to avoid circulars
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app


from .math_core import log, sqrt, add, subtract, multiply, divide

__all__ = [
    'create_app', 
    'log', 
    'sqrt', 
    'add', 
    'subtract', 
    'multiply', 
    'divide'
]