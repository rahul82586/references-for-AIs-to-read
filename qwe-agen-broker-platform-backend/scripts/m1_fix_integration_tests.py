"""
Step M1 part 5 - move the integration tests onto the percent convention.

These two tests encoded the old fraction thresholds (0.8 / 0.5) and asserted a
ratio-scale margin level. They were passing before M1 only because BOTH sides were
fractions; the production code paths that used percent were the ones that were wrong.
Now that everything is percent, the fixtures and assertions move with them.

One behavioural change is worth calling out because it looks like a regression but is
not: test_liquidation_worker_closes_worst_loss_first used margin_level 0.4545 against
stop_out 0.5. On the ratio scale that is "just below stop-out", so closing one position
recovered the account. On the percent scale the same account sits at 45.45% against a
50% threshold, which is genuinely deeper underwater, so the worker correctly keeps
closing until it recovers - and closes both. The fixture now sets the account at 45.45%
against a 30% stop-out (MT5's real real\\real value), which restores the intended
"close the worst one and recover" scenario.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests" / "integration" / "test_margin_loop.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def patch(rel: str, pairs: list[tuple[str, str]]) -> None:
    path = ROOT / rel
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    applied = 0
    for old, new in pairs:
        if old in work:
            work = work.replace(old, new)
            applied += 1
        else:
            print(f"  warn {rel}: not found: {old[:70]!r}")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(work.replace("\n", "\r\n") if crlf else work)
    print(f"  ok  {rel}: {applied}/{len(pairs)} replacements")


# ---------------------------------------------------------------------------
# test_margin_loop.py
# ---------------------------------------------------------------------------

patch(
    "tests/integration/test_margin_loop.py",
    [
        (
            "            margin_call_level=Decimal('0.8'),  # 80%\n"
            "            stop_out_level=Decimal('0.5'),  # 50%",
            "            # PERCENT, matching MT5 (MarginCall / MarginStopOut).\n"
            "            margin_call_level=Decimal('80'),\n"
            "            stop_out_level=Decimal('50'),",
        ),
        (
            "        margin_level=Decimal('1.818'),  # 181.8%",
            "        margin_level=Decimal('181.8'),  # percent: healthy",
        ),
        (
            "    assert updated_account.margin_level == Decimal('0.9090909090909090909090909091'), \\\n"
            '        f"Expected margin level ~0.909, got {updated_account.margin_level}"',
            "    assert updated_account.margin_level == Decimal('90.90909090909090909090909091'), \\\n"
            '        f"Expected margin level ~90.9%, got {updated_account.margin_level}"',
        ),
        (
            "    assert updated_account.margin_level < Decimal('0.8'), \\\n"
            '        f"Expected margin level < 0.8, got {updated_account.margin_level}"',
            "    assert updated_account.margin_level < Decimal('80'), \\\n"
            '        f"Expected margin level below the 80% margin call, got {updated_account.margin_level}"',
        ),
        (
            "    assert updated_account.margin_level < Decimal('0.5'), \\\n"
            '        f"Expected margin level < 0.5, got {updated_account.margin_level}"',
            "    assert updated_account.margin_level < Decimal('50'), \\\n"
            '        f"Expected margin level below the 50% stop-out, got {updated_account.margin_level}"',
        ),
    ],
)

# ---------------------------------------------------------------------------
# test_liquidation_worker.py
# ---------------------------------------------------------------------------

patch(
    "tests/integration/test_liquidation_worker.py",
    [
        (
            "            margin_call_level=Decimal('0.8'),\n"
            "            stop_out_level=Decimal('0.5'),",
            "            # PERCENT. stop_out 30 matches MT5's real\\real group in the live export\n"
            "            # (MarginCall 50.00, MarginStopOut 30.00). At 50 the fixture account,\n"
            "            # which sits at 45.45%, would be liquidated twice over and the test\n"
            "            # would no longer exercise 'close the worst one and recover'.\n"
            "            margin_call_level=Decimal('80'),\n"
            "            stop_out_level=Decimal('30'),",
        ),
        (
            "        margin_level=Decimal('0.4545'),  # 45.45%",
            "        margin_level=Decimal('45.45'),  # percent: below the 80% call, above the 30% stop-out",
        ),
        (
            '            "margin_level": "0.4545",',
            '            "margin_level": "45.45",',
        ),
        (
            '    assert updated_account.margin_level > Decimal(\'0.5\'), "Margin level should be above stop-out"',
            '    assert updated_account.margin_level > Decimal(\'30\'), \\\n'
            '        "Margin level should have recovered above the 30% stop-out"',
        ),
    ],
)

print()
print("  note: the StopOutEntered event payload in the liquidation fixture now carries a")
print("        percent margin_level, which is what the worker compares against the group's")
print("        percent stop_out_level. Both sides agree for the first time.")
