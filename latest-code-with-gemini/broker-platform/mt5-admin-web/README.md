# MT5 Administrator — standalone web workbench

VS Code-style admin panel for the broker platform. Ported from the Theia
extension `mt5-admin-fontend-for-testing` (@ 8781c33) into a **standalone
single application** — no Theia, no IDE runtime, no Node backend. Just
`npm run dev`.

**Design contract (non-negotiable):**

1. **Zero domain logic in the frontend.** Every number the UI shows comes from
   the API. Margin/PnL/spread/routing math lives in the backend.
2. **Everything through one contract.** Features import `services/api` only.
   Two interchangeable transports: `mock` (in-memory fixtures, default) and
   `live` (real bp backend at `/api/v1`). Swappable at runtime from Settings.
3. **Honest gaps.** Endpoints the backend doesn't expose yet throw
   `BackendGapError` and render as a red/amber banner — never fake data. The
   set of these errors is the live work order for the backend session.

## Run

```bash
npm install
npm run dev          # http://localhost:5173  (mock backend by default)
npm run build        # typecheck + production bundle in dist/
```

To talk to the real broker platform:

```bash
# terminal 1: your backend on :8000
# terminal 2:
VITE_PROXY_TARGET=http://localhost:8000 npm run dev
```

then in the app: gear icon → Settings → mode **Live**, base URL `/backend`
(dev proxy, no CORS), paste the backend's `ADMIN_API_KEY`. Anything the M10
backend can't serve shows a gap banner (accounts writes, global
positions/deals/orders, routing HTTP, gateways registry, ticks snapshot,
risk endpoints — see `services/transport/http.ts` for the exact list).

## Architecture

```
src/
├── shell/            workbench chrome — NO business UI
│   ├── workbench/    title/activity/side/status bars, Workbench composition
│   ├── layout/       LayoutHost.tsx — the ONLY file importing dockview
│   ├── tree/         TreeView (ported Theia tree widget, pure React)
│   ├── command-palette/
│   └── registry/     panel-registry.ts (node→panel resolution) + panels.tsx
│                     (lazy feature registrations) — the core mechanism
├── features/         one folder per MT5 Admin section
│   ├── market-watch/ groups/ orders/      ← ported in F0
│   ├── settings/ welcome/ placeholder/
│   └── …             F1 adds the remaining ~20 (one registry line each)
├── services/
│   ├── api/          contract.ts (AdminApi interface) + index.ts (facade)
│   └── transport/    mock.ts (fixtures) · http.ts (real /api/v1 + mappers)
├── store/            zustand: settings (mode/URL/key), persisted
└── theme/            tokens.css (VS Code Dark+ under --theia-* names),
                      adm.css (ported component CSS), workbench.css
```

Import direction (enforced by review, lint rule planned):
`shell → registry → features → services/api → transport`.
Features never import each other; only LayoutHost imports dockview;
only transports import `fetch`.

Keyboard: `Ctrl+Shift+P` palette · `Ctrl+B` sidebar · drag tabs to split/dock
(layout auto-saved to localStorage, restored on reload).

## Status

- **F0 ✅** — shell + registry + transports + 3 proof panels (Market Watch,
  Groups incl. 9-tab settings modal, Orders incl. new-order form), verified in
  a headless browser (render, deep-link filters, palette, live/mock swap,
  layout restore).
- **F1** — bulk-port remaining ~20 pages into `features/`, drop `@ts-nocheck`.
- **F2** — split contract into per-domain endpoint modules; TanStack Query for
  server state; WS client (`/ws/stream`) for Market Watch instead of polling.
- **F3** — field alignment vs real backend; manager-API session flow
  (Connect + JWT) for orders/positions; login screen.
- **F4** — Routing editor rebuilt on the M8 MT5 taxonomy; light theme;
  OpenAPI-generated DTO types.

See `../work/ARCHITECTURE.md` for the full design rationale and
`../work/FRONTEND-REVIEW.md` for the backend API gap matrix.
