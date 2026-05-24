# Windows ROCm/HIP environment for AMD Radeon 890M (gfx1150).

$ErrorActionPreference = "Stop"

$candidateRoots = @(
    "$env:ProgramFiles\AMD\ROCm\6.4",
    "$env:ProgramFiles\AMD\ROCm\6.3",
    "$env:ProgramFiles\AMD\ROCm\6.2"
)

$rocmRoot = $candidateRoots | Where-Object {
    Test-Path -LiteralPath (Join-Path $_ "bin\hipconfig.exe") -PathType Leaf
} | Select-Object -First 1

if (-not $rocmRoot) {
    throw "AMD ROCm/HIP SDK was not found. Expected hipconfig.exe under C:\Program Files\AMD\ROCm\<version>\bin."
}

$rocmBin = Join-Path $rocmRoot "bin"
$env:ROCM_PATH = $rocmRoot
$env:HIP_PATH = $rocmRoot
$env:AMDGPU_TARGETS = "gfx1150"
$env:CMAKE_HIP_ARCHITECTURES = "gfx1150"
$env:ROCR_VISIBLE_DEVICES = if ($env:ROCR_VISIBLE_DEVICES) { $env:ROCR_VISIBLE_DEVICES } else { "0" }
$env:HIP_VISIBLE_DEVICES = if ($env:HIP_VISIBLE_DEVICES) { $env:HIP_VISIBLE_DEVICES } else { "0" }

if ($env:Path -notlike "*$rocmBin*") {
    $env:Path = "$rocmBin;$env:Path"
}

Write-Host "ROCm/HIP SDK: $rocmRoot"
Write-Host "AMDGPU_TARGETS: $env:AMDGPU_TARGETS"
Write-Host "Visible AMD GPU: $env:ROCR_VISIBLE_DEVICES"
