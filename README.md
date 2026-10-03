# arm64-boot-to-driver-lab

> Personal project, not affiliated with Arm.

**Boot-time regressions in firmware stacks often go unnoticed; this lab measures every boot stage on every commit and flags them.**

It builds the Arm64 boot chain (TF-A → UEFI → Linux, with my own PMU driver) on QEMU, boots it automatically, turns the boot log into per-stage timings, and fails the build when a stage gets slower.

## The problem

Cars, phones and IoT devices have strict boot-time targets. A rear-view camera, for example, has to show an image within a few seconds of the ignition. Firmware teams therefore keep asking two questions:

1. **Which stage of the boot is slow?** Secure firmware, UEFI, the kernel, or a driver?
2. **Did this change make boot slower?**

Answering them by hand is slow and error-prone. This lab answers them automatically: every commit rebuilds the full Arm64 boot chain, boots it, turns the boot log into per-stage timings, and fails the build if a stage gets slower than its baseline.

## What it does

```
 commit ──► CI build ──► boot in QEMU ──► boot log ──► parse ──► timings per stage ──► compare to baseline ──► pass / fail + chart
```

The boot chain that runs inside QEMU:

```
┌───────────────────────────────────────────────────────────────┐
│ User space     pmu-read tool  ──►  /dev/armlab (char device)  │  EL0
├───────────────────────────────────────────────────────────────┤
│ Linux kernel   arm64 + armlab.ko (exposes CPU PMU counters)   │  EL1
├───────────────────────────────────────────────────────────────┤
│ UEFI           EDK II ArmVirtQemu → Linux EFI stub            │  EL2 / EL1 (non-secure)
├───────────────────────────────────────────────────────────────┤
│ TF-A           BL1 → BL2 → BL31 (EL3 runtime, PSCI)           │  EL3 (secure)
├───────────────────────────────────────────────────────────────┤
│ QEMU           virt board, Cortex-A57/A72, GICv3              │  emulated hardware
└───────────────────────────────────────────────────────────────┘
```

**Exception Levels (EL)** are Arm's privilege levels: EL3 is secure firmware, EL2 the hypervisor, EL1 the OS kernel, and EL0 user programs. One goal of the lab is to show, in the boot log, exactly when control moves from one level to the next.

### The pieces

| Part | What it is | Licence |
|------|------------|---------|
| [QEMU](https://www.qemu.org/) | Emulates an Arm64 board (`-M virt,secure=on`), so no hardware is needed | GPL-2.0 |
| [Trusted Firmware-A](https://www.trustedfirmware.org/projects/tf-a/) | Arm's reference secure firmware (`PLAT=qemu`) | BSD-3-Clause |
| [EDK II](https://github.com/tianocore/edk2) | Open-source UEFI firmware (`ArmVirtQemu`) | BSD-2-Clause-Patent |
| [Linux](https://www.kernel.org/) | arm64 kernel + BusyBox initramfs | GPL-2.0 |
| `driver/` (mine) | `armlab.ko`: character driver that reads the CPU's performance counters (PMU: cycles, instructions, cache misses) and exposes them to user space | GPL-2.0 |
| `scripts/`, `tools/` (mine) | Build and boot scripts, boot-log parser, regression check | MIT |
| `.github/workflows/` (mine) | CI pipeline on GitHub Actions | MIT |

## How timing works

Measuring boot time in an emulator needs care, so the lab follows three rules:

- **Timestamps come from the host.** Linux prints its own timestamps, but TF-A and UEFI usually don't. `tools/timestamp_serial.py` stamps every line of the serial output as it arrives, which makes it possible to split the boot into stages using marker lines (for example the TF-A `BL31` banner, the UEFI banner and the kernel's `Booting Linux`).
- **One boot is not a measurement.** QEMU on a shared CI runner is noisy, so each commit is booted several times and the **median** is kept.
- **Results are relative.** Emulator times are not real hardware boot times. The lab reports changes between commits ("this commit made the kernel stage 12% slower"), which is what matters for catching regressions. Runs with QEMU's `-icount` option (deterministic guest time) are compared against host-side wall-clock runs to see which one gives more stable results.

## Steps

**Part 1: Build the boot chain**
- [x] 0. Repo set up: goal, architecture, plan, licence, CI skeleton
- [ ] 1. Toolchain: `aarch64-linux-gnu-` cross compiler and QEMU installed, versions recorded
- [ ] 2. Bare kernel: boot an arm64 Linux kernel + BusyBox initramfs directly in QEMU
- [ ] 3. TF-A: build BL1/BL2/BL31 for `PLAT=qemu` and boot through EL3
- [ ] 4. UEFI: build EDK II `ArmVirtQemu` as BL33 and reach the UEFI shell
- [ ] 5. Full chain: TF-A → UEFI → Linux, with a boot log annotated per Exception Level

**Part 2: The driver**
- [ ] 6. Character driver `armlab.ko` (open / read / ioctl) loads and unloads cleanly
- [ ] 7. Driver reads PMU counters (cycles, instructions, cache misses) for a user-space program
- [ ] 8. Device Tree node + platform-driver binding

**Part 3: Measure and automate** (built on top of Parts 1 and 2, which are the core of the project)
- [ ] 9. Host-side timestamping of the serial log + parser that splits it into stages → `timings.csv`
- [ ] 10. CI: GitHub Actions builds the chain and boots it N times on every push (median per stage)
- [ ] 11. Regression check: fail the build if a stage's median is slower than its baseline by more than a threshold; compare stability with and without `-icount`
- [ ] 12. Results: chart of boot time per stage across commits, published in `docs/`

**Part 4: Use it**
- [ ] 13. Optimise: use the measurements to cut boot time (kernel config, firmware options) and document the gain
- [ ] 14. Write-up: what I learned at each stage

## Repository layout

```
.github/workflows/  CI pipeline
docs/               notes and results per step (boot logs, timings, charts)
scripts/            build and boot scripts for each stage
tools/              boot-log parser and regression check
driver/             armlab kernel driver (PMU counters)
```

## Quick start

```bash
./scripts/00-check-tools.sh   # check that the toolchain is installed
```

More commands will be added here as each step is completed.

## References

Arm's public documentation only:

- Arm Architecture Reference Manual for A-profile
- Learn the architecture: *Exception model*, *Boot flow*, *Performance Monitoring Unit*, on developer.arm.com
- Trusted Firmware-A documentation: trustedfirmware-a.readthedocs.io
- EDK II ArmVirtPkg documentation

## Licence

My scripts, tools and docs are under the MIT licence (see `LICENSE`). The kernel driver in `driver/` is GPL-2.0, as required for code that runs inside Linux. Third-party projects keep their own licences. They are downloaded at build time, not copied into this repo.
