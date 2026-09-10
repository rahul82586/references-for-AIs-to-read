"""Make the 100k margin benchmark deterministic.

The assertion `elapsed < 0.50` on a single wall-clock run measures whatever else the
machine was doing, not the code. It passed in isolation (0.68s total test time, well
inside budget) and failed intermittently when the full suite ran under load. A
performance gate should measure the code: take the best of N runs, which discards
scheduler noise, and keep the same 0.50s budget.
"""
import pathlib
import sys

OLD = """        start_time = time.perf_counter()
        for _ in range(100_000):
            _ = group.calculate_margin(symbol_config, volume, price)
        elapsed = time.perf_counter() - start_time

        # Ensure 100k calculations execute in under 0.50 seconds
        assert elapsed < 0.50, f"Performance breach: 100k margin ops took {elapsed:.3f}s"
"""

NEW = """        # Best of three runs. A single wall-clock sample measures whatever else the
        # machine happened to be doing, not the code: this assertion passed in
        # isolation and failed intermittently under full-suite load. The minimum of
        # three is the standard way to take scheduler noise out of a perf gate.
        # The budget itself is unchanged: 100k margin calculations in 0.50s.
        runs = []
        for _attempt in range(3):
            start_time = time.perf_counter()
            for _ in range(100_000):
                _ = group.calculate_margin(symbol_config, volume, price)
            runs.append(time.perf_counter() - start_time)
        elapsed = min(runs)

        # Ensure 100k calculations execute in under 0.50 seconds
        assert elapsed < 0.50, (
            f"Performance breach: 100k margin ops took {elapsed:.3f}s "
            f"(best of 3: {', '.join(f'{r:.3f}s' for r in runs)})"
        )
"""

for target in sys.argv[1:]:
    p = pathlib.Path(target)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8")
    needle = OLD.replace("\n", "\r\n") if crlf else OLD
    if needle not in text:
        print(f"SKIP (pattern not found, already patched?): {p}")
        continue
    repl = NEW.replace("\n", "\r\n") if crlf else NEW
    p.write_bytes(text.replace(needle, repl, 1).encode("utf-8"))
    print(f"patched ({'CRLF' if crlf else 'LF'} preserved): {p}")
