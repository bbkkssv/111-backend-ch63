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
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      password TEXT NOT NULL DEFAULT ''
    )
    """
    )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      description TEXT NOT NULL,
      amount REAL NOT NULL,
      date TEXT NOT NULL,
      category TEXT NOT NULL,
      user_id INTEGER NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

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
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (user, email, password))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201

@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allow columns to be retrieved by name (e.g. row["name"])
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users")
    rows = cursor.fetchall()
    print(rows)
    conn.close()

    users = []
    for row in rows:
        user = {"id": row["id"], "name": row["name"]}
        users.append(user)

    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200

@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Validate if the user exist
    cursor.execute("SELECT id, name FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    print(row["name"])
    conn.close()

    return jsonify({
        "success": True,
        "message": "User retrieved successfully",
        "data": {"id": row["id"], "name": row["name"]}
    }), 200

@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # validate if user exists
    cursor.execute("SELECT id, name FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200

@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET name=?, email=?, password=? WHERE id=?",
        (name, email, password, user_id),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200

#------------Expenses Endpoints------------#
@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "No data found to create an expense!"
        }), 400
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (title, description, amount, date, category, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (title, description, amount, date, category, user_id),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense created successfully"
    }), 201

@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    expenses = []
    for row in rows:
        expense = {
            "id": row["id"],
            "title": row["title"],
            "category": row["category"],
            "user_id": row["user_id"]
        }
        expenses.append(expense)

    return jsonify({
        "success": True,
        "message": "Expenses retrieved successfully",
        "data": expenses
    }), 200

@app.get("/api/expenses/<int:expense_id>")
def get_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    expense = {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "amount": row["amount"],
        "date": row["date"],
        "category": row["category"],
        "user_id": row["user_id"]
    }
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense retrieved successfully",
        "data": expense
    }), 200

@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM expenses WHERE id=?", (expense_id,))

    if not cursor.fetchone(): #check to see if it exists
        conn.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense deleted successfully"
    }), 200

@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE expenses
            SET title=?, description=?, amount=?, date=?, category=?, user_id=?
            WHERE id=?
        """, (title, description, amount, date, category, user_id, expense_id))
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Expense updated successfully"
        }), 200
    except sqlite3.IntegrityError as e:
        # IntegrityError is most likely when an attribute has any specific options
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 400
    except sqlite3.OperationalError as e:
        # OperationalError wraps SQL syntax errors, missing table/columns
        return jsonify({"error": f"Database operational error: {str(e)}"}), 500
    except sqlite3.DatabaseError as e:
        # DatabaseError is for general databases errors
        return jsonify({"error": f"Database error {str(e.sqlite_errorcode)}: {str(e)}"}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)