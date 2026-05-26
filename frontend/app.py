import os
from datetime import datetime

import msal
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session, request
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-change-later")

# Nodig voor Azure Container Apps HTTPS reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/metrics")
API_KEY = os.getenv("API_KEY", "default-dev-key")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORITY = os.getenv("AUTHORITY")
SCOPE = [os.getenv("SCOPE", "User.Read")]


def build_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )


def build_auth_url():
    return build_msal_app().get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=url_for("authorized", _external=True)
    )


def get_token_from_code(auth_code):
    return build_msal_app().acquire_token_by_authorization_code(
        auth_code,
        scopes=SCOPE,
        redirect_uri=url_for("authorized", _external=True)
    )


def fetch_metrics():
    try:
        response = requests.get(
            API_URL,
            headers={"x-api-key": API_KEY},
            timeout=5
        )

        if response.status_code == 200:
            return response.json(), "online"

        return [], "error"

    except requests.exceptions.RequestException:
        return [], "offline"


def calculate_dashboard_data(metrics):
    if not metrics:
        return {
            "total_systems": 0,
            "system_health": 0,
            "avg_cpu": 0,
            "avg_memory": 0,
            "avg_disk": 0,
            "latest_metric": {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "status": "unknown"
            },
            "alerts": [],
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0
        }

    hostnames = {metric.get("hostname", "unknown") for metric in metrics}
    latest_metric = metrics[0]

    avg_cpu = round(sum(float(m.get("cpu_usage", 0)) for m in metrics) / len(metrics), 1)
    avg_memory = round(sum(float(m.get("memory_usage", 0)) for m in metrics) / len(metrics), 1)
    avg_disk = round(sum(float(m.get("disk_usage", 0)) for m in metrics) / len(metrics), 1)

    alerts = [
        metric for metric in metrics
        if float(metric.get("cpu_usage", 0)) >= 80
        or float(metric.get("memory_usage", 0)) >= 80
        or float(metric.get("disk_usage", 0)) >= 80
        or metric.get("status", "").lower() not in ["healthy", "online", "running"]
    ]

    healthy_count = len([
        metric for metric in metrics
        if metric.get("status", "").lower() in ["healthy", "online", "running"]
    ])

    warning_count = len([
        metric for metric in metrics
        if metric.get("status", "").lower() == "warning"
    ])

    critical_count = len(metrics) - healthy_count - warning_count
    system_health = round((healthy_count / len(metrics)) * 100, 1)

    return {
        "total_systems": len(hostnames),
        "system_health": system_health,
        "avg_cpu": avg_cpu,
        "avg_memory": avg_memory,
        "avg_disk": avg_disk,
        "latest_metric": latest_metric,
        "alerts": alerts[:5],
        "healthy_count": healthy_count,
        "warning_count": warning_count,
        "critical_count": critical_count
    }


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    metrics, api_status = fetch_metrics()
    dashboard = calculate_dashboard_data(metrics)

    return render_template(
        "dashboard.html",
        metrics=metrics,
        api_status=api_status,
        dashboard=dashboard,
        current_time=datetime.now().strftime("%d-%m-%Y %H:%M"),
        user=session.get("user")
    )


@app.route("/login")
def login():
    auth_url = build_auth_url()
    return render_template("login.html", auth_url=auth_url)


@app.route("/signin")
def signin():
    return redirect(build_auth_url())


@app.route("/getAToken")
def authorized():
    if "error" in request.args:
        return f"Login error: {request.args.get('error_description')}"

    if "code" not in request.args:
        return redirect(url_for("login"))

    result = get_token_from_code(request.args["code"])

    if "id_token_claims" in result:
        claims = result["id_token_claims"]

        session["user"] = {
            "name": claims.get("name", "Unknown user"),
            "email": claims.get("preferred_username", "unknown"),
            "tenant": claims.get("tid", "unknown")
        }

        return redirect(url_for("index"))

    return f"Could not log in: {result}"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        "?post_logout_redirect_uri=https://"
        + request.host
        + "/login"
    )


@app.route("/health")
def health():
    return {"status": "frontend healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)