# Reservas — starter template

Module 0614 (Web Application Deployment). On the lab appliance this tree lives at `~/reservas` on `despliegue` (`192.168.56.10`).

Each student owns the zone **`<STUDENT_ID>.despliegue.internal`**. Set `STUDENT_ID`, `BASE_DOMAIN`, and `JWT_ISSUER` in `.env` before starting Compose.

This template runs the booking board only. It does **not** configure BIND, TLS, Apache as a reverse proxy, FTP, or Continuous Deployment. Those are later labs on `despliegue`.

## What is included

| Path | Role |
|------|------|
| `app/` | Flask app: HTML list, `POST /bookings`, cancel, attachments directory |
| `auth/` | HS256 issuer at `/login` |
| `compose.yaml` | `app`, `auth`, `db` (MariaDB) |
| `.env.example` | `STUDENT_ID`, secrets, `JWT_ISSUER` |
| `docs/deployment.md` | Headings you fill in each unit |
| `docs/openapi.yaml` | Draft API description (complete in Unit 5) |
| `dns/db.<STUDENT_ID>.despliegue.internal.skeleton` | SOA/NS template; replace `<STUDENT_ID>` with your id |

## Configure `.env`

```bash
cd ~/reservas
cp .env.example .env
# STUDENT_ID=yourid
# BASE_DOMAIN=yourid.despliegue.internal
# JWT_ISSUER=https://auth.yourid.despliegue.internal
# DB_PASSWORD, DB_ROOT_PASSWORD, JWT_SECRET — strong values
```

Never commit `.env`.

## Start the stack (on `despliegue`)

```bash
docker compose up -d --build
docker compose ps
curl -s http://127.0.0.1:3000/health
curl -s http://127.0.0.1:4000/health
```

Ports are published on **`127.0.0.1`** only. After Unit 2, reach the app via Apache at `https://reservas.<STUDENT_ID>.despliegue.internal`.

### Login and create a booking (on `despliegue`)

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:4000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"ana","password":"ana-lab"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

curl -s -X POST http://127.0.0.1:3000/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"guest_name":"Marta","slot_at":"2026-10-20 13:00","notes":"window table"}'
```

Change `APP_VERSION` in `app/app.py` in Unit 5 to prove a deploy.

### Lab users (issuer)

| Username | Password |
|----------|----------|
| `ana` | `ana-lab` |
| `luis` | `luis-lab` |

## Stop and roll back

```bash
docker compose down          # keeps volumes
docker compose down -v       # destroys data — only when you mean it
```

## Out of scope for this repository

- Apache virtual hosts and certificates
- Tomcat / `informes.war`
- GitHub Actions workflow (you write it in Unit 5)
- Real secrets in git
