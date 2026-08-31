#!/usr/bin/env python3
"""Fail CI on incomplete packages, wrong variants or unsafe kernel configs."""
import pathlib
import subprocess
import sys
import zipfile


def require(condition, message):
    if not condition:
        raise SystemExit(message)


variant = sys.argv[1]
require(variant in ("aosp", "oneui"), "Unsupported variant")
config = set(pathlib.Path(".config").read_text().splitlines())
for flag in (
    "CONFIG_KSU=y", "CONFIG_KSU_MANUAL_HOOK=y", "CONFIG_KSU_SUSFS=y",
    "CONFIG_KSU_SUSFS_SUS_MEMFD=y", "CONFIG_SECURITY_SELINUX=y",
    "CONFIG_MINT_PLATFORM_VERSION=11",
):
    require(flag in config, f"Required config missing: {flag}")
for flag in ("CONFIG_KSU_DEBUG=y", "CONFIG_KSU_KPROBES_HOOK=y",
             "CONFIG_KSU_SUSFS_ENABLE_LOG=y"):
    require(flag not in config, f"Unexpected config: {flag}")
packages = list(pathlib.Path("out").glob("*.zip"))
require(len(packages) == 1, f"Expected one ZIP, found {len(packages)}")
with zipfile.ZipFile(packages[0]) as package:
    require(package.testzip() is None, "ZIP CRC validation failed")
    for name in ("Image", "dtb.img", "ramdisk-new.cpio", "anykernel.sh",
                 "META-INF/com/google/android/update-binary", "mint.prop"):
        require(package.getinfo(name).file_size > 0, f"Empty payload: {name}")
    require(package.getinfo("Image").file_size > 10_000_000, "Kernel Image too small")
    manifest = dict(line.split("=", 1) for line in package.read("mint.prop").decode().splitlines() if "=" in line)
    expected = {"ro.mint.build.ksu": "true", "ro.mint.build.susfs.version": "v2.2.0",
                "ro.mint.droid.android": "11", "ro.mint.droid.device": "A50",
                "ro.mint.droid.variant": "AOSP" if variant == "aosp" else "OneUI"}
    for key, value in expected.items():
        require(manifest.get(key) == value, f"Manifest mismatch: {key}")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    require(manifest.get("ro.mint.build.source.commit") == source, "Source revision mismatch")
    ramdisk = package.read("ramdisk-new.cpio")
    # The shared archive also carries exynos9611's fstab. Only the A50's
    # exynos9610 fstab determines whether this variant mounts /product.
    fstab = subprocess.run(
        ["cpio", "--quiet", "-i", "--to-stdout", "./fstab.exynos9610"],
        input=ramdisk, capture_output=True, check=True,
    ).stdout
    require(b"/system" in fstab and b"/vendor" in fstab, "Missing A50 fstab")
    require((b"/product" in fstab) == (variant == "oneui"), "Wrong variant ramdisk")
boot = pathlib.Path("out/boot.img").read_bytes()
require(boot[:8] == b"ANDROID!", "Invalid Android boot image")
require(b"androidboot.selinux=enforcing" in boot[:1632], "SELinux must boot enforcing")
require(b"androidboot.selinux=permissive" not in boot[:1632], "Permissive boot image")
print(f"Validated {packages[0]}: Android 11 {variant}, KernelSU Next/SUSFS, enforcing")
