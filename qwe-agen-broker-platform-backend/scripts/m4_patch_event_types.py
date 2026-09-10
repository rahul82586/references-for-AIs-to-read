import io

p = "core/events/domain_events.py"
s = io.open(p, encoding="utf-8").read()

# --- 1. two new EventType members -------------------------------------------
old = '''    MARGIN_CALL_TRIGGERED = "risk.margin_call_triggered"'''
assert old in s
new = '''    MARGIN_CALL_TRIGGERED = "risk.margin_call_triggered"
    MARGIN_CALL_EXITED = "risk.margin_call_exited"'''
s = s.replace(old, new, 1)

old = '''    STOP_OUT_INITIATED = "risk.stop_out_initiated"'''
assert old in s
new = '''    STOP_OUT_INITIATED = "risk.stop_out_initiated"
    STOP_OUT_EXITED = "risk.stop_out_exited"'''
s = s.replace(old, new, 1)

old = '''    HOLIDAY_UPDATED = "config.holiday_updated"'''
assert old in s
new = '''    HOLIDAY_CREATED = "config.holiday_created"
    HOLIDAY_UPDATED = "config.holiday_updated"'''
s = s.replace(old, new, 1)

# --- 2. give the five inheritors their own event_type -----------------------
FIXES = [
    ("MarginCallEntered", "MARGIN_CALL_TRIGGERED"),
    ("MarginCallExited", "MARGIN_CALL_EXITED"),
    ("StopOutEntered", "STOP_OUT_INITIATED"),
    ("StopOutExited", "STOP_OUT_EXITED"),
    ("HolidayCreated", "HOLIDAY_CREATED"),
]

for cls, member in FIXES:
    marker = f"class {cls}(DomainEvent):"
    idx = s.index(marker)
    end = s.index("\n\n", idx)
    block = s[idx:end]
    assert block.rstrip().endswith("pass"), f"{cls} does not look like a bare pass:\n{block}"
    docstring_end = block.index('"""', block.index('"""') + 3) + 3
    replacement = (
        block[:docstring_end]
        + "\n    # Declared explicitly. Without it this class inherited DomainEvent's default of\n"
        + "    # EventType.ORDER_CREATED, so a margin call / stop-out was published on the\n"
        + '    # "order.created" channel. In-process subscribers registered by event CLASS\n'
        + "    # still received it, which is why nothing failed loudly - but the channel is\n"
        + "    # what Redis pub/sub routes on, so across processes a stopped-out account\n"
        + "    # notified every OrderCreated listener and reached no LiquidationWorker.\n"
        + f"    event_type: EventType = field(default=EventType.{member}, init=False)"
    )
    s = s[:idx] + replacement + s[end:]

io.open(p, "w", encoding="utf-8").write(s)
print("domain_events: five event types corrected")
