# armlab driver

Out-of-tree Linux character driver (steps 6 to 8).

It creates `/dev/armlab`, which lets a user-space program read the CPU's performance counters (PMU): cycles, instructions retired and cache misses. Developers use this kind of data to find out why code is slow.

Licensed GPL-2.0 (`MODULE_LICENSE("GPL")`), as required for code that runs inside the Linux kernel.
