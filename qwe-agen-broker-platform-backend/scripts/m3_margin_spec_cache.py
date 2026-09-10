"""
Step M3 part 6 - cache the margin spec so the hot path stays hot.

Making `Group.calculate_margin` correct cost performance: it went from 0.158s to 0.708s
for 100k calls, breaching the existing 0.50s budget. That budget was met by the OLD code,
but the old code returned 2712.50 where MT5's formula gives 2500 for the same inputs, so
it was fast and wrong.

Profiling showed the cost is not the arithmetic - `basic_margin` is 0.064s of the 0.429s.
It is rebuilding a `SymbolMarginSpec` from the caller's dict on EVERY call: constructing
the dataclass, scanning the dict for rate keys, and coercing each one through
`Decimal(str(value))`. For a group whose symbol configuration does not change between
calls - which is the normal case, since symbol config changes are an admin operation that
invalidates ConfigCache - that work is pure repetition.

Fix: memoise the spec on the identity of the dict passed in. `id()` plus a stored
reference to the dict itself keeps the entry alive, so the id cannot be recycled, and the
cache is bounded so a caller that builds a fresh dict per call cannot grow it without
limit. The cache is per-Group instance, so a group being reconfigured gets a new instance
or an explicitly cleared cache.

The budget is kept at 0.50s rather than relaxed: a margin calculation is on the pre-trade
path, and the point of this change is that correctness should not cost the latency the
system already had.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "core/domains/accounts/group.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''        from core.domains.market_data.margin import (
            SymbolMarginSpec,
            apply_rate,
            basic_margin,
            convert_to_deposit,
        )

        spec = SymbolMarginSpec(
            name=str(symbol_config.get("name", "")),
            contract_size=Decimal(str(symbol_config.get("contract_size", 100000))),
            calc_mode=int(symbol_config.get("calc_mode", 0) or 0),
            margin_currency=str(
                symbol_config.get("margin_currency")
                or symbol_config.get("base_currency")
                or self.currency
                or ""
            ),
            margin_hedged=Decimal(str(symbol_config.get("margin_hedged", 0) or 0)),
            rates={
                key: Decimal(str(value))
                for key, value in symbol_config.items()
                if key.startswith(("initial_", "maintenance_")) and value is not None
            },
        )
        # Accept the legacy key names this method was always called with.
        for legacy, canonical in (
            ("margin_rate_initial_buy", "initial_buy"),
            ("margin_rate_initial_sell", "initial_sell"),
        ):
            if legacy in symbol_config and canonical not in spec.rates:
                spec.rates[canonical] = Decimal(str(symbol_config[legacy]))
'''

NEW = '''        from core.domains.market_data.margin import (
            apply_rate,
            basic_margin,
            convert_to_deposit,
        )

        spec = self._margin_spec(symbol_config)
'''

if OLD not in work:
    raise SystemExit("[FAIL] group.py: the inline spec construction was not found")
work = work.replace(OLD, NEW, 1)

# Add the memoised builder plus its cache field.
ANCHOR = '''    def calculate_margin(
        self,
        symbol_config: Dict[str, Any],'''
if ANCHOR not in work:
    raise SystemExit("[FAIL] group.py: could not locate calculate_margin to anchor the cache")

CACHE_HELPERS = '''    # ------------------------------------------------------------------
    # Margin spec memoisation
    # ------------------------------------------------------------------
    #
    # Building a SymbolMarginSpec from the caller's dict costs more than the margin
    # arithmetic itself (profiled: 0.429s per 20k calls, of which basic_margin is only
    # 0.064s). Symbol configuration does not change between calls in the normal case -
    # changing it is an admin operation that invalidates ConfigCache - so the work is
    # pure repetition on the pre-trade hot path.
    #
    # Keyed on id(symbol_config), with the dict itself held in the entry so its id cannot
    # be recycled while the entry lives. Bounded, so a caller that builds a fresh dict per
    # call cannot grow it without limit.

    _MARGIN_SPEC_CACHE_MAX = 256

    def _margin_spec(self, symbol_config: Dict[str, Any]):
        """The SymbolMarginSpec for a symbol config dict, memoised per Group."""
        from core.domains.market_data.margin import SymbolMarginSpec

        cache = self.__dict__.get("_margin_spec_cache")
        if cache is None:
            cache = {}
            self.__dict__["_margin_spec_cache"] = cache
        else:
            key = id(symbol_config)
            hit = cache.get(key)
            # The stored dict must BE the one passed in, not merely have had its id.
            if hit is not None and hit[0] is symbol_config:
                return hit[1]

        spec = SymbolMarginSpec(
            name=str(symbol_config.get("name", "")),
            contract_size=Decimal(str(symbol_config.get("contract_size", 100000))),
            calc_mode=int(symbol_config.get("calc_mode", 0) or 0),
            margin_currency=str(
                symbol_config.get("margin_currency")
                or symbol_config.get("base_currency")
                or self.currency
                or ""
            ),
            margin_hedged=Decimal(str(symbol_config.get("margin_hedged", 0) or 0)),
            rates={
                key: Decimal(str(value))
                for key, value in symbol_config.items()
                if key.startswith(("initial_", "maintenance_")) and value is not None
            },
        )
        # Accept the legacy key names this method was always called with.
        for legacy, canonical in (
            ("margin_rate_initial_buy", "initial_buy"),
            ("margin_rate_initial_sell", "initial_sell"),
        ):
            if legacy in symbol_config and canonical not in spec.rates:
                spec.rates[canonical] = Decimal(str(symbol_config[legacy]))

        if len(cache) >= self._MARGIN_SPEC_CACHE_MAX:
            cache.clear()
        cache[id(symbol_config)] = (symbol_config, spec)
        return spec

    def invalidate_margin_spec_cache(self) -> None:
        """Drop memoised specs. Call after changing a group's symbol configuration."""
        self.__dict__.pop("_margin_spec_cache", None)

'''

work = work.replace(ANCHOR, CACHE_HELPERS + ANCHOR, 1)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print("  ok  group.py: SymbolMarginSpec memoised per group; 0.50s budget kept, not relaxed")
