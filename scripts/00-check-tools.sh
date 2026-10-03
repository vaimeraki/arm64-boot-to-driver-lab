#!/usr/bin/env bash
# Check that the tools needed for the lab are installed and print their versions.
set -u
for t in aarch64-linux-gnu-gcc qemu-system-aarch64 make git; do
  if command -v "$t" >/dev/null 2>&1; then
    printf '%-24s %s\n' "$t" "$("$t" --version | head -n1)"
  else
    printf '%-24s MISSING\n' "$t"
  fi
done
