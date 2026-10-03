#!/usr/bin/env python3
"""Prefix each line read from stdin with the time elapsed since start.

TF-A and UEFI do not print timestamps of their own, so the boot log is
timestamped on the host as it arrives. Typical use:

    qemu-system-aarch64 ... -nographic | ./tools/timestamp_serial.py > boot.log

Output format, one line per serial line:

    <seconds since start, 6 decimals> <original line>
"""
import sys
import time


def main() -> None:
    start = time.monotonic()
    for raw in sys.stdin.buffer:
        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        elapsed = time.monotonic() - start
        sys.stdout.write(f"{elapsed:.6f} {line}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
