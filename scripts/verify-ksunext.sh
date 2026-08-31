#!/usr/bin/env bash
# Validate a clean source checkout without modifying the caller's tree.
set -euo pipefail
cd "$(dirname "$0")/.."
bash -n build.sh
expected_commit="$(sed -n 's/^KSU_NEXT_COMMIT="\([^"]*\)"/\1/p' build.sh)"
test -n "$expected_commit"
test "$(git -C KernelSU rev-parse HEAD)" = "$expected_commit"
test "$(git -C KernelSU rev-parse --is-shallow-repository)" = false
# This branch derives its userspace API version from commit history. A shallow
# submodule silently reports 30201 instead of the tested kernel version 33215.
test "$((30200 + $(git -C KernelSU rev-list --count HEAD)))" -eq 33215
test "$(git config -f .gitmodules --get submodule.KernelSU.branch)" = legacy-susfs-v2
port=kernel/patches/susfs-v2.2.0-exynos9610.patch
compat=kernel/patches/ksunext-v3.2.0-legacy-susfs-v2-exynos9610.patch
git apply --check "$port"
git -C KernelSU apply --ignore-space-change --check "../$compat"
grep -q 'KernelSU Next 3.2 managers use app profile v3' "$compat"
grep -q 'FLAG_KSU_NO_NEW_PRIVS' "$compat"
grep -q 'susfs_is_avc_log_spoofing_enabled' "$port"
grep -q '#define SUSFS_VERSION "v2.2.0"' "$port"
grep -q 'return ksu_handle_sys_reboot(magic1, magic2, cmd, &arg);' kernel/reboot.c
grep -q '^CONFIG_KSU_MANUAL_HOOK=y' kernel/configs/mint_root-kernelsu.config
grep -q '^CONFIG_KSU_SUSFS_SUS_MEMFD=y' kernel/configs/mint_root-kernelsu.config
grep -q '^# CONFIG_KSU_SUSFS_ENABLE_LOG is not set' kernel/configs/mint_root-kernelsu.config
echo "Validated clean-checkout patches: KernelSU Next $expected_commit + SUSFS v2.2.0"
