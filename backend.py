from flask import Flask, request, jsonify
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)

DB_FILE = "bookings.db"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT,
            slots TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/api/booking", methods=["POST"])
def booking():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        message = data.get("message", "")
        slots = json.dumps(data.get("slots", []), ensure_ascii=False)

        if not (name and email and phone and slots):
            return jsonify({"error": "缺少必要欄位"}), 400

        # 存進 SQLite
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (name, email, phone, message, slots)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, phone, message, slots))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "預約成功！"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 額外：查詢所有預約（管理者用）
@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, message, slots, created_at FROM bookings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "message": row[4],
            "slots": json.loads(row[5]),
            "created_at": row[6]
        })
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
