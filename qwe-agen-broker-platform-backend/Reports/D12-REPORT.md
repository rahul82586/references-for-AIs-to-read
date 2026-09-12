# D12 — a close must tell the client what it just did

**Date:** 2026-09-12
**Found by:** the new gate 6b in `scripts/local_e2e.sh` (D11's close, driven over real HTTP)
**Status:** fixed, 588 tests green, `make proofs` 13/0/1

---

## 1. The defect

D11 gave the client a real close route. The route then built its response body by
reading the `Position` the handler returns — which by that point has `volume` 0 and,
in the normal *close at market* case, a `price_current` that no tick has set since
the position opened.

A close that genuinely booked an OUT deal, released the margin and moved the balance
answered this:

```json
{ "volume_closed": "0E-8", "close_price": "0", "realized_pnl": "0E-8",
  "deal_id": "31d3330b-…", "fully_closed": true }
```

The trade happened. The client was told nothing about it.

Two independent fallbacks were both empty exactly when the response mattered most:

| Field | Read from | On a full close |
|---|---|---|
| `volume_closed` | `request.volume`, else `position.volume` | request is `None` ("close all"), position volume is `0` |
| `close_price` | `position.price_current`, else `request.price`, else `0` | no tick has repriced it ⇒ `None`; a market close sends no price ⇒ `0` |
| `realized_pnl` | `position.profit` | still the last *floating* estimate, `0` for a position never repriced |

Meanwhile the OUT deal, the `PositionClosed` event payload and the account balance
all carried the true numbers. This is D1/D2 again — *a value computed correctly
somewhere and served stale (here: empty) from somewhere else* — which is the pattern
`PROJECT-STATE.md` §8 says to keep hunting.

## 2. Why it survived D11

The D11 tests asserted what the close **did**: an OUT deal exists, the position is
gone, margin is released, the deal id is non-empty. All true. None of them asserted
what the close **said**, because the body's numbers were not compared against
anything. The defect only became visible when a proof ran the whole path against a
live broker and printed the response.

Lesson: a gate that prints the body is worth more than a gate that only checks the
status code. `local_e2e.sh` prints every response for exactly this reason.

## 3. The fix

**`ClosePositionHandler`** stamps the close onto the position it saves and returns:

- `price_current` = the price actually dealt — on a **partial** close too, because
  that is a fact about the trade just made, not an estimate of the remainder;
- on a **full** close only, `profit` = the realised result. That is what MT5 reports
  for a position in history, and it is what `liquidation_worker` already assumes when
  it reads `position.profit.amount` as the realised figure.

A partial close deliberately leaves `profit` alone: the position is still open and
still floating, so writing a realised number into a floating field would be the same
lie pointing the other way. The next tick reprices the remainder.

**The route** reads the volume *before* calling the handler and reports
`volume_before − volume_remaining`, so a client that omits `volume` is still told
what was closed. The pre-read goes through the same repository the handler is bound
to, and a failure to pre-read degrades to the old fallback rather than failing the
close — the close is the thing that matters.

Nothing was invented. Every field now comes from a number the close actually used.

## 4. Proof

| Gate | Before | After |
|---|---|---|
| `tests/integration/test_d11_client_trade_routes.py` | 10 tests | **12** (2 new fail against the unfixed tree) |
| `scripts/local_e2e.sh` | 15 checks, no close | **22 checks**, gate 6b closes over HTTP |
| full suite | 586 | **588 passed, 25 skipped** |
| `make proofs` | 12/0/2 | **13/0/1** (the one skip is `m4_proof_order_executes`, weekend session) |

Gate 6b output on a live local broker:

```
close: {'volume_closed': '0.10000000', 'volume_remaining': '0E-8',
        'close_price': '1.07961000', 'realized_pnl': '0E-24',
        'deal_id': '2fbad2c6-…', 'fully_closed': True}
margin_before_close: 107.96100000   margin_after_close: 0
foreign_close_status: 404
```

`realized_pnl` is 0 there because the mock feed never repriced the position, so it
closed at its open price — the handler logs that case at WARNING and the number is
honest. The new integration test moves the market first and pins the exact figure:
0.10 lots × 100 000 contract × (1.10050 − 1.10010) = **4.00 USD**, and asserts the
response, the OUT deal and the balance movement all state the same 4.00.

New gate 6b checks: close 200 · `fully_closed` · position gone from
`/account/positions` · OUT deal id present · **margin released (D10)** · closing
someone else's position refused.

### `E2E_FORCE_SESSIONS`

The seeded sessions are Mon–Fri, which is correct MT5 behaviour, but it made the
whole trade half of `local_e2e.sh` unrunnable at a weekend — and the weekend is when
the gate is most likely to be re-run. Step 3b now widens the sessions to 7×24 **in
the disposable local SQLite proof DB only**, never a cloud database. It is a config
value, not a bypass: `CreateOrderHandler` and `PreTradeRiskService` still check the
session, they just find it open. `E2E_FORCE_SESSIONS=0` keeps the weekend refusal
under test instead, and the trade checks skip as before.

## 5. Files

| File | What |
|---|---|
| `application/commands/close_position.py` | stamps `price_current` (always) and `profit` (full close only) |
| `api/routers/trade.py` | `_position_repo_volume()` pre-read; `volume_closed` is the difference |
| `scripts/patch_d12_close_response.py` | idempotent patch script (project convention) |
| `scripts/patch_local_e2e_close_gate.py` | idempotent; adds step 3b + the close sequence + gate 6b |
| `scripts/local_e2e.sh` | 15 → 22 checks |
| `tests/integration/test_d11_client_trade_routes.py` | 10 → 12 tests |

⚠️ Patch-script gotcha worth remembering: both patched files are **CRLF**. Reading
with `Path.read_text()` applies universal newlines and turns every `\r\n` into `\n`,
so a `\r\n` anchor silently fails to match. Open with `newline=""`.

## 6. Still open

The cloud proof of a client close is **not** yet run: the cloud database still reads
**31 IN deals / 0 OUT deals / 31 open positions**, because no close has been issued
against it since the route existed. That needs the restarted server's URL and a
position to close. The MT5 terminal behind the tunnel also reads
`{"status":"disconnected"}`, so the live-tick path is down independently of this.