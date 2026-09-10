import io

p = "infrastructure/config/seeder.py"
s = io.open(p, encoding="utf-8").read()

# --- 1. the risk account the router actually reads ---------------------------
anchor = '''# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------'''
assert anchor in s
addition = '''async def ensure_coverage_risk_account(
    coverage_repo: Any,
    group_repo: Any,
    report: SeedReport,
    *,
    account_id: str = "DEFAULT_COVERAGE",
) -> None:
    """Create the CoverageAccount that B-Book exposure is booked against.

    This is a different thing from `ensure_coverage_account` above, and the platform
    needs both:

      * ensure_coverage_account creates a trading ACCOUNT (login 900001) in the
        coverage\\\\house group - a normal account row in the accounts table;
      * this creates the CoverageAccount RISK entity in the coverage_accounts table,
        which is what SmartOrderRouter and ExecutionOrchestrator look up by the id
        "DEFAULT_COVERAGE" when they compute the Net Open Position ratio and book the
        broker's side of an internalised fill.

    Nothing created the second one. A freshly seeded server therefore had no coverage
    account, every B-Book fill logged "coverage exposure could not be updated", broker
    exposure stayed at zero forever, and the 70% warning / 85% auto-hedge / 95% block
    thresholds could never fire - the exposure limit was decoration. The orchestrator
    treats it as a post-fill reporting fault rather than a rejection, so the client's
    trade still went through; only the broker's own risk picture was missing.

    The nop_limit default of 100 lots per symbol is a placeholder for a server that has
    not been configured yet. It is deliberately generous: a tight default on an
    unconfigured server would start rejecting real client flow, and the limit is a risk
    decision that belongs to whoever runs the desk.
    """
    if coverage_repo is None:
        report.warnings.append(
            "no coverage_repo passed to seed_all; the DEFAULT_COVERAGE risk account was "
            "not created and B-Book exposure will not be tracked"
        )
        return

    existing = await coverage_repo.find_by_id(account_id)
    if existing is not None:
        report.coverage_risk_accounts = getattr(report, "coverage_risk_accounts", 0) + 1
        return

    from core.domains.execution.models import CoverageAccount

    currency = "USD"
    group = await group_repo.find_by_name("coverage\\\\house")
    if group is not None and getattr(group, "currency", None):
        currency = group.currency

    account = CoverageAccount(
        account_id=account_id,
        name="Default Coverage (B-Book residual)",
        currency=currency,
    )
    await coverage_repo.save(account)
    report.coverage_risk_accounts = getattr(report, "coverage_risk_accounts", 0) + 1
    logger.info(
        "created coverage risk account %s (%s, NOP limit %s lots per symbol)",
        account_id, currency, account.nop_limit,
    )


''' + anchor
s = s.replace(anchor, addition, 1)

# --- 2. SeedReport field ----------------------------------------------------
old = '''    coverage_accounts: int = 0'''
assert old in s
s = s.replace(old, '''    coverage_accounts: int = 0
    #: CoverageAccount risk entities (coverage_accounts table), distinct from the
    #: trading account in the coverage\\house group counted just above.
    coverage_risk_accounts: int = 0''', 1)

old = '''            "coverage_accounts": self.coverage_accounts,'''
assert old in s
s = s.replace(old, '''            "coverage_accounts": self.coverage_accounts,
            "coverage_risk_accounts": self.coverage_risk_accounts,''', 1)

# --- 3. seed_all takes the repo and calls it --------------------------------
old = '''    manager_repo: Any,
    account_repo: Any,
    config_root: Any = "config",'''
assert old in s
s = s.replace(old, '''    manager_repo: Any,
    account_repo: Any,
    coverage_repo: Any = None,
    config_root: Any = "config",''', 1)

old = '''    await ensure_first_admin(manager_repo, report, password_hasher=password_hasher)
    await ensure_coverage_account(account_repo, group_repo, report)'''
assert old in s
s = s.replace(old, '''    await ensure_first_admin(manager_repo, report, password_hasher=password_hasher)
    await ensure_coverage_account(account_repo, group_repo, report)
    await ensure_coverage_risk_account(coverage_repo, group_repo, report)''', 1)

io.open(p, "w", encoding="utf-8").write(s)
print("seeder: DEFAULT_COVERAGE risk account")

# --- 4. the CLI passes it ---------------------------------------------------
p = "cli/main.py"
s = io.open(p, encoding="utf-8").read()
old = '''        manager_repo=providers["manager_repo"],
        account_repo=providers["account_repo"],'''
assert old in s
s = s.replace(old, '''        manager_repo=providers["manager_repo"],
        account_repo=providers["account_repo"],
        coverage_repo=providers.get("coverage_repo"),''', 1)

old = '''    table.add_row("coverage accounts", str(report.coverage_accounts))'''
assert old in s
s = s.replace(old, '''    table.add_row("coverage accounts", str(report.coverage_accounts))
    table.add_row("coverage risk accounts", str(report.coverage_risk_accounts))''', 1)

io.open(p, "w", encoding="utf-8").write(s)
print("cli: seeds and reports the coverage risk account")
