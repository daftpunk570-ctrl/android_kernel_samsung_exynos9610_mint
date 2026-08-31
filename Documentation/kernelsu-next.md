# KernelSU Next legacy + SUSFS on Mint Kernel

The Galaxy A50 Android 11 builds use the community KernelSU Next branch
`legacy-susfs-v2`, pinned to commit
`f110cddc07e27b21ad77c6c31261660efb25dce4`. Git describes this revision as
`v3.2.0-legacy-susfs-v2-29-gf110cddc`: it is the requested v3.2.0 legacy
SUSFS line plus 29 later compatibility fixes from that same branch.

SUSFS is pinned to `v2.2.0` in non-GKI/manual-hook mode. The Exynos9610 port
is stored in `kernel/patches/susfs-v2.2.0-exynos9610.patch`; `build.sh`
applies it once and verifies the version before compiling. The small
KernelSU-side compatibility patch is stored in
`kernel/patches/ksunext-v3.2.0-legacy-susfs-v2-exynos9610.patch`.

The SUSFS port was based on the Samsung 4.14 implementation from
Project Matrixx's Exynos9820 `ksunext-qpr2` branch and adapted to Mint's older
VFS, procfs, IDA and mount APIs. It includes path, mount, kstat, map, memfd,
uname, cmdline and open-redirect hooks.

## Configuration used

- `CONFIG_KSU=y`
- `CONFIG_KSU_MANUAL_HOOK=y`
- `CONFIG_KSU_KPROBES_HOOK` disabled
- KernelSU and SUSFS debug logging disabled
- SUS path, mount, kstat, map and memfd enabled
- try-umount, spoof-uname and spoof-cmdline enabled
- open-redirect and symbol hiding enabled
- SELinux boot command line set to `androidboot.selinux=enforcing`

The package manifest records the exact KernelSU repository revision and SUSFS
version. Rootless builds continue to use `mint_root-none.config` and do not
enable these features.

The selected branch contains the post-3.2 app-profile v4 kernel API, while the
3.2 Manager emits app-profile v3. The Exynos9610 compatibility patch therefore
adds bounded v3 read/write support and migrates granted v3 profiles to v4 with
`FLAG_KSU_NO_NEW_PRIVS`. This keeps the spoofed KernelSU Next 3.2 Manager
compatible without copying a v4 structure past its smaller userspace buffer.

The manual reboot hook returns immediately for KernelSU's `0xDEADBEEF`
supercalls. Continuing through the normal reboot syscall would replace a
successful SUSFS command with `-EINVAL`; clients that validate the syscall
result (including ZeroMount) would then incorrectly report SUSFS as absent.

## Reproducible builds

Run from Linux or WSL with the Mint toolchain dependencies installed:

```sh
./build.sh -d a50 -a 11 -v aosp -k
./build.sh -d a50 -a 11 -v oneui -k
```

Use a Linux filesystem for the checkout (including under WSL), because kernel
source filenames differ only by case and include names reserved on Windows.
Start with `git clone --recurse-submodules` of this repository. The tested Proton
toolchain is pinned to `32074ae4fc8e2269569fdff26a22da037388c3e3` and downloaded
by the build script; an existing toolchain at a different commit is rejected.
The scripts stop on pipeline failures. Build each variant in a clean checkout
when validating release contents.

GitHub Actions builds both variants on Ubuntu 22.04 and publishes ZIPs, configs,
dependency/patch provenance and SHA-256 checksums after both jobs succeed.
Trigger through a push to `main`, an `a50-*` tag, or `workflow_dispatch`.
Only the release job gets `contents: write`; the build jobs have read-only access.
Local diagnostic files, APKs and ADB credentials are not part of the source or
release uploads. Build logs contain CI output only and are retained for 7 days.

The AOSP ramdisk removes the One UI `/product` mount only from its temporary
copy. This prevents an AOSP build from modifying the source ramdisk used by a
later One UI build.

## Manager and hiding recommendations

Use the KernelSU Next Manager compatible with the selected community branch.
After boot:

1. Keep **Umount modules by default** enabled.
2. Grant superuser access only to apps that genuinely require it.
3. Deny root to banking, DRM and integrity-sensitive apps and give each an
   App Profile that unmounts modules.
4. Keep SELinux enforcing and avoid modules that globally modify `/system`,
   Zygote or SELinux policy.
5. Enable/configure SUSFS features through a module or userspace tool that
   explicitly supports SUSFS 2.2.0 and this KernelSU Next legacy branch.
6. Reboot after changing modules, mount rules or app profiles, then verify
   `/sys/fs/selinux/enforce` returns `1`.

These measures reduce ordinary root, mount, procfs and kernel-symbol exposure;
they do not guarantee that every application will accept the device. An
unlocked bootloader, Knox state and hardware-backed attestation remain visible
independently of KernelSU/SUSFS.

References:

- https://github.com/sidex15/KernelSU-Next/tree/legacy-susfs-v2
- https://github.com/Project-Matrixx-New/android_kernel_samsung_exynos9820/tree/ksunext-qpr2
- https://github.com/sidex15/KernelSU-Next/releases
