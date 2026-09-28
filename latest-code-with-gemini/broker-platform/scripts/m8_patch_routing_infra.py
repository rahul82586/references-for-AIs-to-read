"""M8 patch A: routing import + persistence layer.

fieldmap gains the routing domain mapping and the Conditions/Dealers nested
tables (the codec already round-trips nested tables for groups); the loader
gains routes_from_mt5; a typed model + repository persists the wire record;
`cli seed --mt5-routing` imports a real Administrator export.
"""
import ast
import io
import pathlib


def read(path):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    return src, nl


def write(path, src, nl):
    ast.parse(src.replace("\r\n", "\n") if nl == "\r\n" else src)
    io.open(path, "w", encoding="utf-8", newline="").write(src)


def apply(path, pairs):
    src, nl = read(path)
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        assert src.count(old) == 1, f"{path}: anchor {src.count(old)}x: {old[:70]!r}"
        src = src.replace(old, new)
    write(path, src, nl)
    print(f"{path}: {len(pairs)} patch(es)")


# --- 1. fieldmap: routing domains + nested tables -----------------------------
apply("infrastructure/mt5/fieldmap.py", [(
    '''ROUTING_FIELDS: Tuple[Field, ...] = (
    Field("Name", "name", STR),
    Field("Mode", "", INT),
    Field("Request", "", FLAGS),  # bitmask over the 24 request types
    Field("Type", "", FLAGS),      # bitmask over the 8 order types
    Field("Flags", "", FLAGS),
    Field("Action", "", INT),      # 1001 = process to dealers, 1005 = auto execution
    Field("ActionValueInt", "", INT),
    Field("ActionValueUInt", "", INT),
    Field("ActionValueFloat", "", DEC),
    Field("ActionValueString", "", STR),
    Field("Conditions", "", NESTED),
    Field("Dealers", "", NESTED),
)
''',
    '''ROUTING_FIELDS: Tuple[Field, ...] = (
    Field("Name", "name", STR),
    Field("Mode", "mode", INT),                     # 0 = disabled, nonzero = enabled
    Field("Request", "request_mask", FLAGS),        # EnRouteFlags bitmask (25 request types)
    Field("Type", "type_mask", FLAGS),              # bitmask over the 8 order types
    Field("Flags", "flags", FLAGS),
    Field("Action", "action", INT),                 # EnRouteAction: 1001 = dealers, 1003 = reject, 1005 = confirm-client...
    Field("ActionValueInt", "action_value_int", INT),
    Field("ActionValueUInt", "action_value_uint", INT),
    Field("ActionValueFloat", "action_value_float", DEC),
    Field("ActionValueString", "action_value_string", STR),
    Field("Conditions", "conditions", NESTED),
    Field("Dealers", "dealers", NESTED),
)

#: Routing rule conditions (IMTConCondition). Rule = EnConditionRule comparison:
#: 0 EQ, 1 NOT_EQ, 2 GREATER, 3 NOT_LESS, 4 LESS, 5 NOT_GREATER.
ROUTING_CONDITION_FIELDS: Tuple[Field, ...] = (
    Field("Condition", "code", INT),
    Field("Rule", "rule", INT),
    Field("ValueInt", "value_int", INT),
    Field("ValueUInt", "value_uint", INT),
    Field("ValueFloat", "value_float", DEC),
    Field("ValueString", "value_string", STR),
)

#: Routing rule dealers: a gateway or a manager with the Dealing right.
ROUTING_DEALER_FIELDS: Tuple[Field, ...] = (
    Field("Login", "login", INT),
    Field("Name", "name", STR),
)
''',
)])

# --- 2. codec: register the nested tables -------------------------------------
apply("infrastructure/mt5/codec.py", [
    (
        "    ROUTING_FIELDS,\n",
        "    ROUTING_CONDITION_FIELDS,\n    ROUTING_DEALER_FIELDS,\n    ROUTING_FIELDS,\n",
    ),
    (
        '''NESTED_TABLES: Dict[str, Tuple[Field, ...]] = {
    "Commissions": COMMISSION_FIELDS,
    "Tiers": COMMISSION_TIER_FIELDS,
    "Symbols": GROUP_SYMBOL_FIELDS,
}
''',
        '''NESTED_TABLES: Dict[str, Tuple[Field, ...]] = {
    "Commissions": COMMISSION_FIELDS,
    "Tiers": COMMISSION_TIER_FIELDS,
    "Symbols": GROUP_SYMBOL_FIELDS,
    "Conditions": ROUTING_CONDITION_FIELDS,
    "Dealers": ROUTING_DEALER_FIELDS,
}
''',
    ),
])

# --- 3. loader: routes_from_mt5 ------------------------------------------------
apply("infrastructure/config/loader.py", [(
    "def parse_symbol(raw: Dict[str, Any], where: str) -> Symbol:\n",
    '''def routes_from_mt5(path: Any):
    """Import the ConfigRouting table from a real MT5 Administrator export.

    Returns ``[(Mt5RouteRule, raw_record), ...]`` in table order. The raw
    record is kept alongside the rule so the repository can store it verbatim:
    the rule drives evaluation, the record drives byte-identical re-export.
    """
    from core.domains.execution.routing_mt5 import Mt5RouteRule

    payload = decode_file(path)
    out = []
    for position, raw in enumerate(records(payload, "ConfigRouting")):
        out.append((Mt5RouteRule.from_wire(raw, position=position), raw))
    return out


def parse_symbol(raw: Dict[str, Any], where: str) -> Symbol:
''',
)])

# --- 4. db_models re-export (metadata registration for alembic) ---------------
apply("infrastructure/persistence/db_models.py", [(
    "from .manager_models import ClientModel, ManagerModel  # noqa: E402,F401\n",
    "from .manager_models import ClientModel, ManagerModel  # noqa: E402,F401\n"
    "from .routing_models import Mt5RoutingRuleModel  # noqa: E402,F401\n",
)])

# --- 5. di_setup: register the repository -------------------------------------
apply("infrastructure/persistence/di_setup.py", [
    (
        "from .repositories.ledger_repository import SqlLedgerRepository\n",
        "from .repositories.ledger_repository import SqlLedgerRepository\n"
        "from .repositories.routing_mt5_repository import SqlRoutingMt5Repository\n",
    ),
    (
        "    ledger_repo = SqlLedgerRepository(session_factory)\n",
        "    ledger_repo = SqlLedgerRepository(session_factory)\n"
        "    mt5_routing_repo = SqlRoutingMt5Repository(session_factory)\n",
    ),
    (
        "        'ledger_repo': ledger_repo,\n",
        "        'ledger_repo': ledger_repo,\n"
        "        'mt5_routing_repo': mt5_routing_repo,\n",
    ),
])

print("patch A applied")
