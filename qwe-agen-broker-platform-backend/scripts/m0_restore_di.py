"""
Step M0 part 3 - restore the handler factories that duplicate-removal carried away,
complete the port -> container-key mapping, and normalise this file's line endings.

The original api/di_providers.py defined get_cancel_order_handler twice. Removing the
first copy also removed the `get_account_query_handler` alias that sat between them,
and the second copy was itself deleted, so the name vanished while routers still
import it. This restores exactly one definition plus the alias.

All matching is line-ending agnostic: this file ended up with mixed CRLF/LF after
earlier patches, so we normalise to CRLF (the repo-wide convention) at the end.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
DI = ROOT / "api" / "di_providers.py"
if not DI.is_file():
    raise SystemExit(f"not found: {DI}")

with open(DI, encoding="utf-8", newline="") as fh:
    raw = fh.read()
# Normalise first, so every subsequent match is against plain LF.
text = raw.replace("\r\n", "\n").replace("\r", "\n")


def sub(old: str, new: str, why: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"[FAIL] pattern not found ({why}):\n{old[:200]!r}")
    text = text.replace(old, new, 1)
    print(f"  ok  {why}")


# --- 1. widen the port imports -------------------------------------------
sub(
    "    IHolidayRepository,\n    IPositionRepository,\n)",
    "    IHolidayRepository,\n"
    "    IPositionRepository,\n"
    "    IOrderRepository,\n"
    "    IDealRepository,\n"
    ")",
    "imported IOrderRepository and IDealRepository",
)

# --- 2. complete the resolve() mapping -----------------------------------
sub(
    '        IHolidayRepository: "holiday_repo",\n'
    '        IPositionRepository: "position_repo",',
    '        IHolidayRepository: "holiday_repo",\n'
    '        IPositionRepository: "position_repo",\n'
    '        IOrderRepository: "order_repo",\n'
    '        IDealRepository: "deal_repo",\n'
    "        # Not a port: a concrete application service, resolved by class.\n"
    '        PreTradeRiskService: "risk_service",',
    "mapped IOrderRepository, IDealRepository and PreTradeRiskService for resolve()",
)

# --- 3. restore the alias and the missing handler ------------------------
RESTORED = '''# Backwards-compatible alias: some routers import the shorter name.
get_account_query_handler = get_account_info_query_handler


def get_cancel_order_handler() -> CancelOrderHandler:
    """FastAPI dependency provider for CancelOrderHandler."""
    container = get_di_container()
    return CancelOrderHandler(
        account_repo=container.resolve(IAccountRepository),
        order_repo=container.resolve(IOrderRepository),
        risk_service=container.resolve(PreTradeRiskService),
        event_bus=container.resolve(IEventBus),
    )


'''
sub(
    "def get_modify_order_handler() -> ModifyOrderHandler:",
    RESTORED + "def get_modify_order_handler() -> ModifyOrderHandler:",
    "restored get_cancel_order_handler and the get_account_query_handler alias",
)

# Write back as CRLF to match the rest of the repository.
with open(DI, "w", encoding="utf-8", newline="") as fh:
    fh.write(text.replace("\n", "\r\n"))
print("  ok  normalised api/di_providers.py to CRLF")
