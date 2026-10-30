"""Reservas booking board — Unit 1 starter.

Change APP_VERSION when you practise Continuous Deployment in Unit 5.
"""

from __future__ import annotations

import os
import time
from functools import wraps
from pathlib import Path

import jwt
import pymysql
from flask import Flask, g, jsonify, render_template_string, request, url_for

APP_VERSION = "0.1.0"

JWT_SECRET = os.environ.get("JWT_SECRET", "")
JWT_ISSUER = os.environ.get("JWT_ISSUER", "")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "reservas-api")
JWT_ALGORITHMS = ["HS256"]
JWT_SKEW_SECONDS = 60

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "reservas")
DB_USER = os.environ.get("DB_USER", "reservas")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

ATTACHMENTS_DIR = Path(os.environ.get("ATTACHMENTS_DIR", "/data/attachments"))

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reservas</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; max-width: 48rem; }
    .version { color: #666; font-size: 0.9rem; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }
    th { background: #f4f4f4; }
    code { background: #f4f4f4; padding: 0.1rem 0.3rem; }
  </style>
</head>
<body>
  <p class="version">Reservas <strong>{{ version }}</strong></p>
  <h1>Booking board</h1>
  <p>Public list. Creating or cancelling a booking needs
     <code>Authorization: Bearer</code> from the issuer.</p>
  <table>
    <thead>
      <tr><th>ID</th><th>Guest</th><th>When</th><th>Notes</th><th>Attachment</th><th>Status</th></tr>
    </thead>
    <tbody>
    {% for b in bookings %}
      <tr>
        <td>{{ b.id }}</td>
        <td>{{ b.guest_name }}</td>
        <td>{{ b.slot_at }}</td>
        <td>{{ b.notes or "" }}</td>
        <td>
          {% if b.attachment %}
            <a href="{{ url_for('attachment', name=b.attachment) }}">{{ b.attachment }}</a>
          {% endif %}
        </td>
        <td>{{ b.status }}</td>
      </tr>
    {% else %}
      <tr><td colspan="6">No bookings yet.</td></tr>
    {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the bookings table if it does not exist."""
    for attempt in range(30):
        try:
            db = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=True,
            )
            with db.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bookings (
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      guest_name VARCHAR(120) NOT NULL,
                      slot_at VARCHAR(64) NOT NULL,
                      notes VARCHAR(255) NULL,
                      attachment VARCHAR(255) NULL,
                      status VARCHAR(32) NOT NULL DEFAULT 'confirmed'
                    )
                    """
                )
            db.close()
            return
        except pymysql.err.OperationalError:
            time.sleep(2)
    raise RuntimeError("database not reachable")


def require_bearer(view):
    """Validate Authorization: Bearer with HS256 (starter). Extend for RS256 in the JWT lab."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="missing_bearer"), 401
        token = header[7:].strip()
        try:
            claims = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=JWT_ALGORITHMS,
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
                leeway=JWT_SKEW_SECONDS,
            )
        except jwt.PyJWTError as exc:
            return jsonify(error="invalid_token", detail=str(exc)), 401
        g.claims = claims
        return view(*args, **kwargs)

    return wrapper


@app.get("/")
def index():
    with get_db().cursor() as cur:
        cur.execute(
            "SELECT id, guest_name, slot_at, notes, attachment, status "
            "FROM bookings ORDER BY id"
        )
        bookings = cur.fetchall()
    return render_template_string(PAGE, version=APP_VERSION, bookings=bookings)


@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION)


@app.post("/bookings")
@require_bearer
def create_booking():
    data = request.get_json(silent=True) or {}
    guest = (data.get("guest_name") or "").strip()
    slot = (data.get("slot_at") or "").strip()
    notes = (data.get("notes") or "").strip() or None
    if not guest or not slot:
        return jsonify(error="guest_name_and_slot_at_required"), 400
    with get_db().cursor() as cur:
        cur.execute(
            "INSERT INTO bookings (guest_name, slot_at, notes) VALUES (%s, %s, %s)",
            (guest, slot, notes),
        )
        booking_id = cur.lastrowid
    return jsonify(id=booking_id, guest_name=guest, slot_at=slot, status="confirmed"), 201


@app.post("/bookings/<int:booking_id>/cancel")
@require_bearer
def cancel_booking(booking_id: int):
    with get_db().cursor() as cur:
        cur.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = %s",
            (booking_id,),
        )
        if cur.rowcount == 0:
            return jsonify(error="not_found"), 404
    return jsonify(id=booking_id, status="cancelled")


@app.get("/attachments/<path:name>")
def attachment(name: str):
    """Serve a file from the attachments directory (filled later via SFTP)."""
    from flask import send_from_directory

    path = (ATTACHMENTS_DIR / name).resolve()
    if not str(path).startswith(str(ATTACHMENTS_DIR.resolve())):
        return jsonify(error="invalid_path"), 400
    if not path.is_file():
        return jsonify(error="not_found"), 404
    return send_from_directory(ATTACHMENTS_DIR, name)


if __name__ == "__main__":
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    app.run(host="0.0.0.0", port=3000)
