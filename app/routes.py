"""
Routes for the Flask application.
"""
from flask import Blueprint, jsonify, request
import math

bp = Blueprint('routes', __name__)


@bp.route('/healthz')
def healthz():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


@bp.route('/api/log', methods=['POST'])
def api_log():
    """Calculate logarithm endpoint."""
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({"error": "Missing 'value' in request"}), 400

    try:
        value = float(data['value'])
        result = math.log(value)
        return jsonify({"result": result})
    except ValueError:
        return jsonify({"error": "Invalid value"}), 400


@bp.route('/api/sqrt', methods=['POST'])
def api_sqrt():
    """Calculate square root endpoint."""
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({"error": "Missing 'value' in request"}), 400

    try:
        value = float(data['value'])
        if value < 0:
            return jsonify({
                "error": "Cannot calculate square root of negative number"
            }), 400
        result = math.sqrt(value)
        return jsonify({"result": result})
    except ValueError:
        return jsonify({"error": "Invalid value"}), 400


@bp.route('/')
def index():
    """Root endpoint."""
    return jsonify({"message": "Math API is running"})