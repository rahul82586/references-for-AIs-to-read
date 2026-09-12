"""Client pricing: MT5's two independent price transforms.

The pure domain maths lives here (no I/O, no frameworks). See engine.py for the
group-spread semantics and translation.py for the gateway markup semantics, each
with its documentation references.

The two layers are on opposite sides of the venue boundary and must not be
conflated:

    venue raw --[translation.py: gateway markup]--> platform price
              --[engine.py: symbol spread, then group SpreadDiff]--> client price

MT5 has no markup field on a group. Markup lives on a gateway/feeder
CONFIGURATION's Translates table, and the configuration's Groups list decides
which clients' flow reaches it - so per-group markup is achieved by cloning a
gateway configuration per group, which is what the live TCTrader export does
(two configs of MetaTrader5Gateway64.exe, one named "... clone", differing only
in Groups).
"""
from core.domains.pricing.a_book import (
    ABookPricing,
    ABookQuoteError,
    client_fill_price,
    venue_price_for_instruction,
)
from core.domains.pricing.engine import (
    SpreadSettings,
    client_quote,
    resolve_spread_settings,
)
from core.domains.pricing.translation import (
    Translation,
    TranslationResult,
    apply_translate,
    mask_matches,
    resolve_translation,
)

__all__ = [
    "ABookPricing",
    "ABookQuoteError",
    "SpreadSettings",
    "client_fill_price",
    "Translation",
    "TranslationResult",
    "apply_translate",
    "client_quote",
    "mask_matches",
    "resolve_spread_settings",
    "resolve_translation",
]
