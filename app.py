import os
from contextlib import closing

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def run(sql, params=(), fetch=False):
    with closing(psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "app"),
        user=os.environ.get("DB_USER", "app"),
        password=os.environ.get("DB_PASSWORD", ""),
    )) as conn:
        with conn, conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS items "
                        "(id SERIAL PRIMARY KEY, name TEXT NOT NULL)")
            cur.execute(sql, params)
            return cur.fetchall() if fetch else None


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/items")
def list_items():
    rows = run("SELECT id, name FROM items ORDER BY id", fetch=True)
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])


@app.post("/items")
def add_item():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify(error="name is required"), 400
    rows = run("INSERT INTO items (name) VALUES (%s) RETURNING id, name",
               (name,), fetch=True)
    return jsonify(id=rows[0][0], name=rows[0][1]), 201
