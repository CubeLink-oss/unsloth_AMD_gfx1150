# Install this checkout of Unsloth Studio for AMD Radeon 890M / gfx1150.

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

. "$PSScriptRoot\amd-gfx1150-env.ps1"

$env:UNSLOTH_AMD_ROCM_WINDOWS = "1"

powershell -ExecutionPolicy Bypass -File ".\install.ps1" --local --amd-rocm
