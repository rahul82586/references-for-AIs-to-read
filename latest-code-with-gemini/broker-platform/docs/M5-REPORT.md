# M5 — Does it start on a machine that isn't yours?

**Status: COMPLETE (with one honest caveat: no Docker daemon in this workspace, so the
image is written and CI-gated but not built here).** Test suite **274 → 297 passed /
0 failed**. New cloud proof: **28/28 green** against **Neon PostgreSQL 18.6 (TLS,
pooled)** and **Upstash Redis (TLS)** — real network, real SQL, real pub/sub, nothing
mocked below the repository layer.

The milestone question was deployment. The answer before M5 was *no* — and, as with M4,
not because a feature was missing. The deployment path existed on paper (`docker-compose`,
`Makefile`, `cli start`, `REDIS_URL` support) and **not one step of it had ever run
against real infrastructure**. Every milestone so far proved against SQLite and the
in-process bus; both stand-ins silently tolerated things real services reject.

---

## 1. The headline findings

**The REDIS_URL path could never run — twice over.** `RedisEventBus(redis_url)` passed
the URL as a bare *hostname* to `redis.Redis(host=...)`, and the class's real
`disconnect()` had been mis-indented into the `_Subscription` helper during M4, leaving
`RedisEventBus` abstract — instantiation raised `TypeError` before the hostname bug could
even matter. Distributed events had never crossed a process boundary in this codebase.

**The migrations had never touched real PostgreSQL.** Against Neon, migration 001 failed
three different ways SQLite tolerates: 55 bare-word column defaults (`DEFAULT USD`,
`DEFAULT real`, `DEFAULT ''` — PostgreSQL: *"cannot use column reference in DEFAULT
expression"*), `accounts` created before the `groups` its FK references, and a 35-char
revision id against `alembic_version`'s `VARCHAR(32)`. And the chain lagged the models by
one column (`symbols.margin_currency`, added in M3, whose proofs ran `create_all` instead
of alembic).

**`GET /api/v1/account/positions` returned `[]` for everyone — including accounts holding
real margined positions.** Three stacked silent failures: the handler was never registered
in the DI container; the route swallowed every exception into `[]`; and the handler itself
still spoke the pre-M3 vocabulary (`pos.side`, `pos.average_price`) with no currency
conversion — a sixth independent PnL formula, on the endpoint clients read money from.

**The server had no price source at all.** `build_market_data_stack`'s docstring promised
`MockTickFeed → TickIngestor → MarketDataEngine`; the code wired only the margin pipeline.
A booted server could not price any order. (M4's proofs installed ticks by hand.)

---

## 2. What was built

| Artifact | What it does |
|---|---|
| `ops/docker/Dockerfile` | Multi-stage, non-root (uid 10001), slim runtime deps — startup chain verified to import none of grpcio/pandas/clickhouse/kafka/locust; interpreter-based HEALTHCHECK against the real `/health` |
| `ops/docker/docker-compose.yml` | `api` service + Caddy TLS terminator (`--profile tls`, `tls internal` for localhost, `SITE_ADDRESS` for public Let's Encrypt). Datastores deliberately external: the same image runs against Neon/Upstash or the dev compose |
| `ops/docker/Caddyfile` | HTTPS → api:8000, WebSocket upgrade, zstd/gzip, JSON access log |
| `ops/docker/docker-compose.dev.yml` | **Kafka + Zookeeper deleted** (nothing referenced them); ClickHouse init-mount path fixed (was relative to the wrong directory) and moved behind the `analytics` profile |
| `.github/workflows/ci.yml` | gate (compileall + ruff `E9,F63,F7,F82` + collect-only) → test (full suite) → image (docker build, GHA cache). The gate that catches every B1–B9 class in seconds |
| `.env.example` + `.gitignore` | Every variable documented; `.env` gitignored; URL-quoting note for `&` in provider DSNs |
| `infrastructure/config/env.py` | dotenv loading, `normalize_database_url` (Neon-style `postgresql://…?sslmode=require&channel_binding=require` → asyncpg-legal), `check_server_secrets` (names each problem + the generate command), `mask_url` for safe logs |
| `MARKET_DATA_SOURCE=mock` | Opt-in price source through the real TickIngestor; every tick self-labelled `source=MOCK`; **default remains no-feed** — a server that cannot price refuses orders rather than inventing numbers (the A-Book stub's rule, applied to feeds) |
| `/health` | Real `SELECT 1` + Redis `PING` with latency; 503 when degraded (was a hardcoded 200 "healthy") |
| `RiskEngine.calculate_position_pnl` | One position → deposit currency, via `margin.position_pnl` — the single source of truth the margin loop and liquidation already use |
| `alembic/script.py.mako` | Restored — autogenerate crashed without it (previous sessions wrote migrations by script) |
| `scripts/m5_proof_cloud.sh` | The 28-check cloud gate, re-runnable |
| Makefile | `test-e2e` now runs `tests/integration` (the M4 suite — the old target pointed at a nonexistent dir); `lint` = the CI gate; `docker-build/up/up-tls/down/health/setup-cloud` |

## 3. Defects fixed (16 code + 4 ops, every one covered by a test or the proof)

1. `RedisEventBus` treated a `rediss://` URL as a hostname — DNS could never resolve it.
2. `RedisEventBus.disconnect` lived inside `_Subscription` → class abstract → `TypeError` on any `REDIS_URL` boot.
3. Migration 001: 55 bare-word `server_default`s (`'USD'`, `'real'`, `''`, `'23:59:59'`…) — legal in SQLite, rejected by PostgreSQL.
4. Migration 001: `accounts` (FK → `groups.name`) created before `groups` — alphabetical autogenerate order; SQLite never enforced the FK.
5. Revision id `002_position_price_current_nullable` = 35 chars > `VARCHAR(32)` — the version stamp could never persist.
6. `symbols.margin_currency` missing from the chain (M3 model drift; only visible against a real DB) → migration 003, autogenerated against live Neon, with `server_default` so it is safe on populated tables.
7. `alembic/script.py.mako` absent — `alembic revision --autogenerate` crashed.
8. `tick_from_event` only understood the in-process event object; Redis delivers a plain dict — **every cross-process tick was dropped silently** by both the margin pipeline and pending-order activation.
9. No feed ever started — a booted server had zero prices (docstring claimed otherwise).
10. `close_position.py` used `OrderReason.CLIENT` without importing it — **every client-initiated close raised NameError**. Untested until now because e2e only closed via the LiquidationWorker. Caught by the new F821 gate.
11. `deal.py` / `position.py` annotation forward-refs unbound (TYPE_CHECKING imports added).
12. `/health` was a hardcoded 200 — a container with a dead database still reported green.
13. Hardcoded JWT `SECRET_KEY` and `ADMIN_API_KEY` default: now fail-hard at boot, and the **old placeholder values are refused by name**; admin auth fails closed (503) when unconfigured.
14. `positions_query_handler` never registered → `[]` for everyone.
15. Positions route `except Exception: pass → []` → now 503 (unwired) / 500 (logged traceback).
16. Positions handler: pre-M3 vocabulary + no currency conversion → rewritten onto `RiskEngine.calculate_position_pnl`; **refuses** to report zero PnL without an engine.
17. Ops: compose ClickHouse mount path unresolvable; Kafka/ZK dead weight; `make test-e2e` pointed at a nonexistent directory; INFO wiring logs invisible under bare uvicorn (operator could not see the in-process-bus fallback warning).
18. Ops: `channel_binding` is not an asyncpg kwarg (DSN-only) — normalised away; asyncpg negotiates SCRAM channel binding automatically over TLS.
19. Ops: unquoted `&` in `.env` URLs breaks shell sourcing (python-dotenv was fine; the proof script was not).
20. Ops: `connect()` now pings — an unreachable Redis fails the boot instead of degrading at first publish.

## 4. What is proven

**`scripts/m5_proof_cloud.sh` — 28/28, against Neon + Upstash:**

```
[1] environment         .env present, gitignored, real 64-char secret, old placeholder refused
[2] migrate             alembic upgrade head on PostgreSQL 18.6 (001→002→003)
[3] seed                idempotent re-run: 7 groups / 5 symbols / coverage / admin updated, 0 dupes
[4] status              "Configuration plane is populated" read back from the cloud DB
[5] boot                trading plane wired · Redis bus connected · mock source announced
[6] /health             200 healthy — database ok 17.8ms, event_bus ok 63.2ms (real probes)
[7] trade over HTTP     account persisted in Neon (int↔String(32) login coercion) →
                        JWT login → BUY 0.10 EURUSD → FILLED at 1.07961 →
                        positions_count=1 → margin_used 107.96100000 USD, equity 9999.00
[8] cross-process       an EXTERNAL subscriber on Upstash received the server's
                        market.tick_received events (5 seen); no in-process fallback
[9] shutdown            TickIngestor stopped · LiquidationWorker stopped · uvicorn clean
```

Margin at step 7 is the M3 maths reached from a cloud deployment: 0.10 × 100,000 / 100
= 100 EUR converted at the ask = **107.961 USD** — the same number the M4 proof produced
on SQLite, now on TLS PostgreSQL 18 two continents away.

**Test suite: 297 passed / 0 failed** (274 before M5): 20 new deployment units
(`tests/unit/infrastructure/test_m5_deployment.py`: wire-dict ticks, bus URL mode,
URL normalisation, secrets gate, migration legality guards) + 3 new e2e/integration
(client close books the realised loss; positions query values in deposit currency;
positions query refuses to fake zeros).

## 5. Known debt — found or left, not hidden

1. **No Docker daemon in this workspace.** Dockerfile/compose/Caddy are written and the
   CI `image` job builds them, but `docker build` has not run here. First action on your
   machine: `make docker-build && make up && make health` (or `up-tls` for HTTPS).
2. **`POST /api/v1/auth/login` does not verify a password.** It issues a JWT for any
   `login_id` that exists and is enabled. Client password hashes are not modelled on the
   trading Account yet (managers have Argon2; clients don't). Until this is fixed the
   client API must not face the internet — it is the largest open hole in the platform.
3. GitHub Actions runs only when `bp` is pushed as a repository root (or the workflow is
   adapted with `working-directory` for a subdirectory — noted in `ci.yml`).
4. The M4 debt queue is untouched and still ordered: `volume_min`/`volume_step` DB
   round-trip (visible in `cli status`: TickSize shows 0), margin reservation, netting
   realised PnL, duplicate margin monitor, swap worker wiring, `on_event` → lifespan.
5. `MockTickFeed` quantises to spread, not `symbol.tick_size` (harmless for a labelled
   mock; must not be copied into a real feed adapter).

## 6. Where this leaves the plan

| Stage | Before M5 | Now |
|---|---|---|
| 1. MT5 install / import | done (M0–M1) | unchanged |
| 2. Admin / manager | done (M2) | secrets fail-hard; admin auth still static-key (debt) |
| 3. Brokerage configuration | done (M2–M3) | now on **real PostgreSQL 18**, migrations legal |
| 4. Routing / A-B book / matching | done for B-Book (M4) | positions API truthful; cross-process events proven |
| 5. **Deployment** | **nothing ran** | runs on managed cloud infra; image/compose/TLS/CI written; docker build pending a daemon |

The original "set up and run" target — `cli migrate && cli seed && cli start` on a clean
machine against real services — is met. **M6** is the debt queue (starting with the codec
round-trip and the login password hole), then **M7 pricing/spread/markup**.
