from flask import Flask, jsonify, request
import pymysql
import socket
import os

app = Flask(__name__)

DB_HOST     = os.environ.get("DB_HOST", "localhost")
DB_USER     = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME     = os.environ.get("DB_NAME", "threetierdb")

def get_db():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return f"""
    <h1>Flask App - Three Tier Architecture</h1>
    <p><b>Container:</b> {socket.gethostname()}</p>
    <p><b>Version:</b> {os.environ.get('APP_VERSION', '1.0.0')}</p>
    <p><b>Deployed by:</b> GitHub Actions CI/CD ✅</p>
    <p><b>Pipeline:</b> Test → Build → Push ECR → Deploy ECS</p>
    <p><a href='/users'>View Users</a></p>
    <p><a href='/health'>Health Check</a></p>
    """

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "container": socket.gethostname()}), 200

@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
        conn.close()
        return jsonify({"users": users, "count": len(users)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                (data["name"], data["email"])
            )
        conn.commit()
        conn.close()
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)