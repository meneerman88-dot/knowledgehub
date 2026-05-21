import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from config import Config
from models import db, MonitoringMetric

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Zorg dat de logs-map bestaat
if not os.path.exists("logs"):
    os.makedirs("logs")

# Logging configuratie
file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=5)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info("Knowledge Hub API gestart")

# Database aanmaken
with app.app_context():
    db.create_all()


def check_api_key(req):
    """Controleer of de API key geldig is."""
    api_key = req.headers.get("x-api-key")
    return api_key == app.config["API_KEY"]


@app.before_request
def log_request_info():
    app.logger.info(
        f"Request: {request.method} {request.path} from {request.remote_addr}"
    )


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Knowledge Hub Monitoring API is running",
        "endpoints": {
            "health": "/health",
            "metrics": "/api/v1/metrics"
        }
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/v1/metrics", methods=["POST"])
def create_metric():
    if not check_api_key(request):
        app.logger.warning("Ongeldige API key gebruikt")
        return jsonify({"error": "Unauthorized"}), 401

    if not request.is_json:
        app.logger.warning("Request content is geen JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    required_fields = ["hostname", "cpu_usage", "memory_usage", "disk_usage", "status"]

    for field in required_fields:
        if field not in data:
            app.logger.warning(f"Ontbrekend veld: {field}")
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        metric = MonitoringMetric(
            hostname=data["hostname"],
            cpu_usage=float(data["cpu_usage"]),
            memory_usage=float(data["memory_usage"]),
            disk_usage=float(data["disk_usage"]),
            status=str(data["status"])
        )

        db.session.add(metric)
        db.session.commit()

        app.logger.info(f"Metric opgeslagen voor host: {metric.hostname}")

        return jsonify({
            "message": "Metric stored successfully",
            "data": metric.to_dict()
        }), 201

    except ValueError:
        app.logger.error("Validatiefout: invalid numeric value")
        return jsonify({"error": "Invalid numeric value"}), 400

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Serverfout: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/metrics", methods=["GET"])
def get_metrics():
    if not check_api_key(request):
        app.logger.warning("Ongeldige API key gebruikt bij GET")
        return jsonify({"error": "Unauthorized"}), 401

    try:
        metrics = MonitoringMetric.query.order_by(
            MonitoringMetric.timestamp.desc()
        ).all()
        return jsonify([metric.to_dict() for metric in metrics]), 200

    except Exception as e:
        app.logger.error(f"Fout bij ophalen metrics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 fout: {request.path}")
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 fout: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
