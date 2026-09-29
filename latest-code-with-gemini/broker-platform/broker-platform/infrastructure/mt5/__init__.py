"""
Infrastructure adapters for MetaTrader 5 interoperability.

``mt5.wire``      the MT5 Administrator JSON wire contract (lossless decode/encode)
``mt5.fieldmap``  MT5 PascalCase field names <-> domain snake_case field names
``mt5.codec``     typed conversion between MT5 records and domain value objects

Design rule: the wire layer never coerces types, so an export can always be
re-produced byte-identically. Typing happens only in the codec, and only inbound, so
a lossy import can never silently corrupt an export.
"""
