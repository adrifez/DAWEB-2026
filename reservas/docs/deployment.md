# Reservas — deployment note

Fill this file as you complete each unit. It is evidence for the documentation criteria in LO1, LO2, LO3, LO4, LO5 and LO6.

**Your zone:** `<STUDENT_ID>.despliegue.internal` (write your real id below).

| Field | Value |
|-------|--------|
| STUDENT_ID | |
| BASE_DOMAIN | `<STUDENT_ID>.despliegue.internal` |
| Server IP | `192.168.56.10` |

## Goal

<!-- What you are publishing and for whom. -->

## Architecture

<!-- Sketch: host, DNS for your zone, containers, ports on 127.0.0.1, who terminates TLS. -->

## DNS

| Name | Type | Value | Purpose |
|------|------|-------|---------|
| | | | |

## JWT parameters

| Parameter | Value |
|-----------|--------|
| Header | `Authorization: Bearer` |
| `iss` | `https://auth.<STUDENT_ID>.despliegue.internal` |
| `aud` | |
| Algorithms allowed | |
| Key / secret source | |
| Skew | |
| Roles required | |

## Steps performed

<!-- Install and configuration steps, in order. -->

## Verification tests

| Test | Command or observation | Result |
|------|------------------------|--------|
| | | |

## Rollback

<!-- How to undo the last change (previous Compose tag, previous zone serial, previous WAR). -->
