"""M6 patch: MT5's scaled-integer volume fields, converted in ONE place.

The wire contract (measured on the reference export, 362 symbols x 4 fields,
zero violations): VolumeMin/Max/Step/Limit are integers at 10^4 lots, and their
*Ext siblings are the same value at 10^8. EURUSD carries VolumeMin="100",
VolumeMinExt="1000000" - a 0.01-lot minimum.

Before this patch the codec read them as plain decimals and rendered them at
scale 0:
  * IMPORT: domain volume_min = 100 (LOTS!) - a 10,000x-too-large minimum.
    Invisible to the round-trip proof, which re-exported the same wrong literal
    byte-identically: wire fidelity masked a semantic error.
  * YAML SEED: domain 0.01 rendered "0" into the column (f"{0.01:.0f}") and read
    back as 0 - the M4 debt-3 symptom ("limits not enforced from the database").

Now: record_to_domain divides (preferring Ext when present), domain_to_record
multiplies and derives BOTH the bare and the Ext literal from the domain value,
so an edited volume can never export a stale, contradictory pair.
"""
import ast
import io
import pathlib


def patch(path, pairs):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    for old, new in pairs:
        assert src.count(old) == 1, f"{path}: anchor not found/ambiguous: {old[:70]!r}"
        src = src.replace(old, new)
    ast.parse(src)
    io.open(p, "w", encoding="utf-8", newline="").write(src)
    print(f"{path}: {len(pairs)} patch(es)")


# ---------------------------------------------------------------------------
# codec.py — the single conversion point
# ---------------------------------------------------------------------------
patch(
    "infrastructure/mt5/codec.py",
    [
        # constants next to the SCALE table
        (
            "#: Default scale for a decimal field absent from :data:`SCALE`.\nDEFAULT_SCALE = 8\n",
            """#: Default scale for a decimal field absent from :data:`SCALE`.
DEFAULT_SCALE = 8

#: MT5 writes Volume{Min,Max,Step,Limit} as INTEGERS scaled 10^4 against the lot,
#: with *Ext siblings at 10^8 (measured on the reference export: Ext == bare x
#: 10^4 for all 362 symbols x 4 fields, zero violations). EURUSD carries
#: VolumeMin="100" / VolumeMinExt="1000000" - a 0.01-lot minimum. They are NOT
#: decimals at scale 0; reading them as such made an imported EURUSD enforce a
#: 100-lot minimum, and rendering a YAML-seeded 0.01 at scale 0 wrote "0".
VOLUME_SCALED_FIELDS = frozenset({"VolumeMin", "VolumeMax", "VolumeStep", "VolumeLimit"})
VOLUME_WIRE_EXPONENT = 4
VOLUME_EXT_EXPONENT = 8
""",
        ),
        # import direction: unscale after conversion
        (
            """        try:
            value = _convert_inbound(raw, field)
        except MT5ConversionError:
            # Never let one bad field abort a whole import; surface it verbatim.
            value = raw
""",
            """        try:
            value = _convert_inbound(raw, field)
        except MT5ConversionError:
            # Never let one bad field abort a whole import; surface it verbatim.
            value = raw

        if field.mt5 in VOLUME_SCALED_FIELDS and isinstance(value, Decimal):
            # Scaled-integer wire fields: prefer the 10^8 Ext sibling when present
            # and non-zero (it carries more precision), else the 10^4 bare field.
            ext_value = None
            ext_raw = record.get(field.mt5 + "Ext")
            if ext_raw is not None:
                try:
                    ext_value = Decimal(str(ext_raw))
                except (InvalidOperation, ValueError, TypeError):
                    ext_value = None
            if ext_value is not None and ext_value != 0:
                value = ext_value / Decimal(10) ** VOLUME_EXT_EXPONENT
            else:
                value = value / Decimal(10) ** VOLUME_WIRE_EXPONENT
""",
        ),
        # export direction: scale both literals from the domain value
        (
            """        out[field.mt5] = _render_scalar(
            _lookup(domain, field.domain), field, scales.get(field.mt5)
        )
        rendered.add(field.mt5)
""",
            """        if field.mt5 in VOLUME_SCALED_FIELDS:
            from decimal import ROUND_HALF_UP

            raw_value = _lookup(domain, field.domain)
            dec = None
            if not is_inherited(raw_value):
                try:
                    dec = Decimal(str(raw_value))
                except (InvalidOperation, ValueError, TypeError):
                    dec = None
            if dec is not None:
                bare = (dec * Decimal(10) ** VOLUME_WIRE_EXPONENT).to_integral_value(
                    rounding=ROUND_HALF_UP
                )
                ext = (dec * Decimal(10) ** VOLUME_EXT_EXPONENT).to_integral_value(
                    rounding=ROUND_HALF_UP
                )
                out[field.mt5] = str(int(bare))
                # Derive the Ext sibling from the SAME domain value and mark it
                # rendered, so a quarantined (possibly stale) Ext literal from
                # import can never contradict an edited volume on export.
                ext_key = field.mt5 + "Ext"
                out[ext_key] = str(int(ext))
                rendered.add(ext_key)
                rendered.add(field.mt5)
                continue

        out[field.mt5] = _render_scalar(
            _lookup(domain, field.domain), field, scales.get(field.mt5)
        )
        rendered.add(field.mt5)
""",
        ),
    ],
)

# ---------------------------------------------------------------------------
# config_mappers.py — the column->wire path must carry Ext too, so a freshly
# YAML-seeded symbol (no mt5_source baseline) still exports a complete,
# self-consistent pair for MT5 Administrator.
# ---------------------------------------------------------------------------
p = pathlib.Path("infrastructure/persistence/config_mappers.py")
src = io.open(p, encoding="utf-8", newline="").read()

helper_anchor = 'def _scaled(value: Any, field_name: str, scales: Dict[str, int], default: str = "0") -> str:\n'
helper = '''def _volume_ext(column_value: Any) -> str:
    """Derive the 10^8 *Ext literal from a volume column holding the 10^4 wire int.

    The columns store what symbol_to_db rendered through the codec, i.e. MT5's
    scaled integers (EURUSD volume_min column = 100 = 0.01 lots x 10^4). A fresh
    YAML-seeded row has no mt5_source baseline, so without this its export would
    carry VolumeMin but no VolumeMinExt and MT5 would read the pair as
    contradictory. For imported rows the computed value equals the baseline
    literal exactly (Ext == bare x 10^4 was verified on all 362 symbols), so
    re-export stays byte-identical.
    """
    from decimal import Decimal as _D, InvalidOperation, ROUND_HALF_UP

    try:
        value = _D(str(column_value if column_value is not None else 0))
    except (InvalidOperation, ValueError, TypeError):
        value = _D(0)
    ext = (value * _D(10) ** 4).to_integral_value(rounding=ROUND_HALF_UP)
    return str(int(ext))


'''
assert src.count(helper_anchor) == 1
src = src.replace(helper_anchor, helper + helper_anchor, 1)

old_owned = '''        "VolumeMin": _scaled(row.volume_min, "VolumeMin", scales, "0"),
        "VolumeMax": _scaled(row.volume_max, "VolumeMax", scales, "0"),
        "VolumeStep": _scaled(row.volume_step, "VolumeStep", scales, "0"),
        "VolumeLimit": _scaled(row.volume_limit, "VolumeLimit", scales, "0"),
'''
new_owned = '''        "VolumeMin": _scaled(row.volume_min, "VolumeMin", scales, "0"),
        "VolumeMax": _scaled(row.volume_max, "VolumeMax", scales, "0"),
        "VolumeStep": _scaled(row.volume_step, "VolumeStep", scales, "0"),
        "VolumeLimit": _scaled(row.volume_limit, "VolumeLimit", scales, "0"),
        "VolumeMinExt": _volume_ext(row.volume_min),
        "VolumeMaxExt": _volume_ext(row.volume_max),
        "VolumeStepExt": _volume_ext(row.volume_step),
        "VolumeLimitExt": _volume_ext(row.volume_limit),
'''
assert src.count(old_owned) == 1
src = src.replace(old_owned, new_owned, 1)

old_keys = '''_SYMBOL_OWNED_WIRE_KEYS = frozenset(
    {
        "Symbol",
'''
new_keys = '''_SYMBOL_OWNED_WIRE_KEYS = frozenset(
    {
        "VolumeMinExt",
        "VolumeMaxExt",
        "VolumeStepExt",
        "VolumeLimitExt",
        "Symbol",
'''
assert src.count(old_keys) == 1
src = src.replace(old_keys, new_keys, 1)
ast.parse(src)
io.open(p, "w", encoding="utf-8", newline="").write(src)
print("config_mappers.py: Ext derivation + owned keys")
