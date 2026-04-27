from flask import Flask, jsonify, request
import pymysql
import socket
import os
import logging
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Security: disable debug mode
app.config['DEBUG'] = False

# Security: configure proper logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

metrics = PrometheusMetrics(app)
metrics.info('flask_app_info', 'Flask app info',
    version=os.environ.get('APP_VERSION', '1.0.0'))

# Security: get credentials from environment only
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")

# Security: validate required env vars
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    logger.warning("Database environment variables not fully configured")

def get_db():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

@app.route("/")
def home():
    return jsonify({
        "app": "Flask Three-Tier",
        "container": socket.gethostname(),
        "version": os.environ.get('APP_VERSION', '1.0.0'),
        "endpoints": ["/health", "/metrics", "/users"]
    }), 200

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "container": socket.gethostname()
    }), 200

@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            # Security: use parameterized query
            cursor.execute("SELECT id, name, email, created_at FROM users")
            users = cursor.fetchall()
        conn.close()
        logger.info(f"GET /users returned {len(users)} users")
        return jsonify({"users": users, "count": len(users)}), 200
    except Exception as e:
        logger.error(f"GET /users error: {type(e).__name__}")
        return jsonify({"error": "Database error"}), 500

@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({"error": "name and email required"}), 400

        # Security: validate input length
        if len(data['name']) > 100 or len(data['email']) > 100:
            return jsonify({"error": "Input too long"}), 400

        conn = get_db()
        with conn.cursor() as cursor:
            # Security: parameterized query prevents SQL injection
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                (data["name"], data["email"])
            )
        conn.commit()
        conn.close()
        logger.info(f"POST /users created user")
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        logger.error(f"POST /users error: {type(e).__name__}")
        return jsonify({"error": "Database error"}), 500

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE id = %s", (user_id,)
            )
        conn.commit()
        conn.close()
        logger.info(f"DELETE /users/{user_id}")
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        logger.error(f"DELETE /users error: {type(e).__name__}")
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False    # Security: never True in production
    )  