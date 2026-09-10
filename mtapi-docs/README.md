# MT5 Manager REST API — Offline Reference Pack

> Scraped 2026-09-08 from `https://mng5.mtapi.io` (Swagger UI + ReadMe).
> Generated for offline endpoint development.

## Files in this pack

| File | Size | What's in it |
|------|------|--------------|
| **`MT5-Manager-REST-API.md`** | ~240 KB / ~8000 lines | **The full structured reference** — all 124 endpoints grouped by section, all 128 schemas with field types, required flags, descriptions, enums |
| `QUICKSTART.md` | ~3 KB | Quickstart extracted from the original `/ReadMe` page (install, Connect, OrderSend, WebSockets) |
| `swagger.json` | 366 KB | Raw OpenAPI 3.0.1 spec (source of truth, machine-readable) |
| `index.html` | 0.8 KB | Swagger UI shell — point your browser here if you have the rest served locally |
| `doc-index.html` | 40 KB | The `mng5doc.mtapi.io` landing page (Postman-style doc) |
| `build_md.py` | 13 KB | The Python script that generated `MT5-Manager-REST-API.md` from `swagger.json` (re-run if spec changes) |

## How to use

1. Open `MT5-Manager-REST-API.md` in any Markdown viewer (VS Code, Obsidian, GitHub, etc.).
2. Start with `QUICKSTART.md` to understand the auth flow (Connect → get token → use as `id`).
3. For schema/field details, jump to the **Schemas** section near the bottom of the main file.
4. To regenerate the .md from a newer spec, run:
   ```bash
   python3 build_md.py
   ```

## Document structure

```
# Header (title, version, base URL, auth)
## Authentication
## Table of Contents
## Connection         (endpoints)
## WebSockets         (endpoints)
## Reports            (endpoints)
## Trading            (endpoints)
## Service            (endpoints)
## Main               (endpoints)
## Admin              (endpoints)
## Subscriptions      (endpoints)
## Schemas            (all data models)
## Servers
```

Each endpoint block contains:

- HTTP method + path
- Summary / description
- Parameters table (name, in, type, required, description)
- Request body (if any) with content type + schema fields
- Responses table (status, description, schema ref)
- Inlined response schema fields (so you don't have to flip back to the schema section)
- Security / deprecation notes

Each schema block contains:

- Type-level description (if any)
- Field table (name, type, required, description)
- Inline enum values where applicable
- Required fields list

## Base URLs

- Production: `https://mng5.mtapi.io`
- Demo: `https://mt5mng.mtapi.io`
- Spec: `https://mng5.mtapi.io/swagger/v1/swagger.json`

## Auth pattern (summary)

Every request after `Connect` carries the `id` query parameter = the token returned by `Connect`.

```
GET https://mng5.mtapi.io/Account?id=<TOKEN>
GET https://mng5.mtapi.io/OrderSend?id=<TOKEN>&symbol=EURUSD&operation=Buy&volume=0.01
```

For WebSockets:

```
wss://mng5mng.mtapi.io/events?id=<TOKEN>
```

---

Generated from spec version `v2026.08.21-08.02`.
