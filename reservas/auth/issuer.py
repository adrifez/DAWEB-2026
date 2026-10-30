"""HS256 JWT issuer for the Reservas lab (Unit 1 starter).

RS256 is a student exercise: do not add it here before that lab.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request

app = Flask(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "")
JWT_ISSUER = os.environ.get("JWT_ISSUER", "")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "reservas-api")
TOKEN_TTL_SECONDS = int(os.environ.get("TOKEN_TTL_SECONDS", "3600"))

# Lab users: username → password. Change for classroom demos if you wish.
USERS = {
    "ana": "ana-lab",
    "luis": "luis-lab",
}


@app.get("/health")
def health():
    return jsonify(status="ok", issuer=JWT_ISSUER)


@app.post("/login")
def login():
    """Issue a Bearer access token after a successful password check."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if USERS.get(username) != password:
        return jsonify(error="invalid_credentials"), 401
    if not JWT_SECRET or not JWT_ISSUER:
        return jsonify(error="JWT_SECRET_or_JWT_ISSUER_not_set"), 500

    now = datetime.now(timezone.utc)
    claims = {
        "iss": JWT_ISSUER,
        "sub": username,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(seconds=TOKEN_TTL_SECONDS),
        "roles": ["staff"],
    }
    token = jwt.encode(claims, JWT_SECRET, algorithm="HS256")
    return jsonify(
        access_token=token,
        token_type="Bearer",
        expires_in=TOKEN_TTL_SECONDS,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
