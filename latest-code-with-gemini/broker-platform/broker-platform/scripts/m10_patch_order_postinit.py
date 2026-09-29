"""M10 patch part 3: Order.__post_init__ must not resurrect the volume of a
filled order.

The 'initialize volume_current to volume_initial' default ran on EVERY Order
construction - including db_to_order(), which rebuilds the entity on every read
from SQL. A fully filled order legitimately carries volume_current == 0, so
every read of one reset it to the initial volume: the HTTP response reported
filled_volume 0 for genuinely filled orders, and any consumer re-reading a
filled order saw phantom remaining volume. The in-memory repositories used by
the harness never reconstruct entities, which is why 417 tests missed it and
the cloud gate caught it.
"""
import io
import sys

OLD = '''    def __post_init__(self):
        """Initialize volume_current to volume_initial for new orders."""
        if self.volume_current.value == Decimal('0') and self.volume_initial.value > 0:
            self.volume_current = Volume(self.volume_initial.value)
'''

NEW = '''    def __post_init__(self):
        """For a NEW order, volume_current defaults to volume_initial.

        Past entry into execution, zero is a REAL value, not a missing one: a
        fully filled order carries volume_current == 0. This default used to run
        on EVERY construction - including db_to_order(), which rebuilds the
        entity on every SQL read - so every read of a filled order resurrected
        the initial volume: the HTTP layer reported filled_volume 0 for genuinely
        filled orders and re-reads saw phantom remaining volume (caught by the
        M10 cloud gate; the in-memory harness never reconstructs entities, which
        is why the unit suite could not see it). Only STARTED orders - which have
        not been priced, approved or filled - get the default.
        """
        if (
            self.state is OrderState.STARTED
            and self.volume_current.value == Decimal('0')
            and self.volume_initial.value > 0
        ):
            self.volume_current = Volume(self.volume_initial.value)
'''


def patch(path, replacements):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    crlf = "\r\n" in text
    for old, new in replacements:
        if crlf:
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        if text.count(old) != 1:
            print(f"FAIL: pattern occurs {text.count(old)}x in {path}")
            sys.exit(1)
        text = text.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched {path} (crlf={crlf})")


patch("core/domains/oms/entities/order.py", [(OLD, NEW)])
print("OK part3")
