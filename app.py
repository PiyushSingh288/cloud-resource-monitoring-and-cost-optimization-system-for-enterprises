"""
CloudOptix - Enterprise Cloud Management Platform
Flask Backend - Zero external dependencies (only Flask, built-in sqlite3)
Run: python app.py
"""

from flask import Flask
from flask import jsonify, render_template
import os
from database import init_db

from routes.auth      import auth_bp
from routes.dashboard import dashboard_bp
from routes.resources import resources_bp
from routes.cost      import cost_bp
from routes.alerts    import alerts_bp
from routes.settings  import settings_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cloudoptix-dev-2024")
    app.config["JSON_SORT_KEYS"] = False

    # Allow CORS manually (no flask-cors needed)
    @app.after_request
    def add_cors(response):
        response.headers["Access-Control-Allow-Origin"]  = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        return response

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "CloudOptix API", "version": "1.0.0"})

    # ── Serve HTML pages ──
    @app.route("/")
    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("webpage.html")

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(resources_bp, url_prefix="/api/resources")
    app.register_blueprint(cost_bp,      url_prefix="/api/cost")
    app.register_blueprint(alerts_bp,    url_prefix="/api/alerts")
    app.register_blueprint(settings_bp,  url_prefix="/api/settings")

    init_db()
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
