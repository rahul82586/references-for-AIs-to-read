"""Client pricing: spread transformation per MT5's rules.

The pure domain maths lives here (no I/O, no frameworks). See engine.py for the
authoritative semantics and the documentation references.
"""
from core.domains.pricing.engine import (
    SpreadSettings,
    client_quote,
    resolve_spread_settings,
)

__all__ = ["SpreadSettings", "client_quote", "resolve_spread_settings"]
