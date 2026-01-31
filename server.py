from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "budget_manager.db"  # would normally be in env file

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor() # creates a cursor object to interact with the database

    #Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        pcreated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    conn.commit()
    conn.close()

@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

@app.post("/api/register")
def register():
    data = request.get_json()
    print(data)

    user = data.get("name")
    email = data.get("email")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user, email))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)