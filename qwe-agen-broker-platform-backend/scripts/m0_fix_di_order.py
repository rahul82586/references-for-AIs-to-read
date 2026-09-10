"""
Step M0 part 5 - move the register_port_keys() call below its own definition.

Part 2 inserted the port -> container-key mapping immediately before
register_di_providers, near the top of the file. But register_port_keys and
_ContainerView are defined further down, in the block appended before
get_account_repo, so the call ran before the name existed:

    NameError: name 'register_port_keys' is not defined

This relocates the call to the end of the module, where everything it references is
already defined.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
DI = ROOT / "api" / "di_providers.py"
if not DI.is_file():
    raise SystemExit(f"not found: {DI}")

with open(DI, encoding="utf-8", newline="") as fh:
    text = fh.read()

crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

START = "# Port classes resolved through get_di_container()"
END = "def register_di_providers("

start = work.find(START)
if start == -1:
    raise SystemExit("[FAIL] register_port_keys block not found")
end = work.find(END, start)
if end == -1:
    raise SystemExit("[FAIL] register_di_providers anchor not found after the block")

block = work[start:end]
if "register_port_keys(" not in block:
    raise SystemExit("[FAIL] located block does not contain the call")

work = work[:start] + work[end:]
work = work.rstrip("\n") + "\n\n\n" + block.rstrip("\n") + "\n"

with open(DI, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)

print("  ok  api/di_providers.py: moved register_port_keys() below its definition")
