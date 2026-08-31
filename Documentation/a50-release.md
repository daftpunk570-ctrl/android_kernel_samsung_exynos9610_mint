# Mint / Galaxy A50 / Android 11

Two TWRP-flashable kernel ZIPs with KernelSU Next community legacy and SUSFS 2.2.0:

- **AOSP**: Android 11 AOSP-based ROMs.
- **OneUI3**: Samsung One UI 3.x / Android 11 ROMs (not One UI 11).

Choose only the ZIP matching the installed ROM. Do not flash both.
Back up your boot partition in TWRP and keep a known-good kernel available.
These are custom kernels, provided without warranty; CI compilation is not
a substitute for testing a new release on the device.

## Included

- KernelSU Next `legacy-susfs-v2`, pinned to `f110cddc07e27b21ad77c6c31261660efb25dce4`.
- SUSFS `v2.2.0`, non-GKI, manual hooks, SELinux enforcing at boot.
- Manager 3.2 app-profile compatibility fix (grant/revoke root).
- Correct return value for manual reboot supercalls, including SUSFS clients.
- Original Mint/AnyKernel3 installer and variant-specific ramdisk.

The Manager APK and userspace modules are not bundled. Use the Manager compatible
with this legacy branch. Do not assume the newest Manager has a compatible ABI.
SUSFS kernel support alone does not configure userspace modules or guarantee
that games, banking apps or hardware attestation will accept a rooted device.

`SHA256SUMS` covers the ZIPs, kernel configs and build provenance files.
The exact dependency commits and integration patches are included in the source
repository. See `Documentation/kernelsu-next.md` for manual build instructions.
