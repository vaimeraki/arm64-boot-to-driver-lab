# tools

- `timestamp_serial.py`: stamps every line of the QEMU serial output with the time since start, because TF-A and UEFI don't print timestamps themselves.
- `parse_boot_log.py` (step 9): splits a timestamped log into stages (TF-A, UEFI, kernel, driver) and writes `timings.csv`.
- `check_regression.py` (step 11): compares the median timings with a stored baseline and fails if a stage is slower than the allowed threshold.
