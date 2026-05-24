# Verify the local AMD ROCm/HIP + PyTorch environment used by Unsloth Studio.

$ErrorActionPreference = "Stop"

. "$PSScriptRoot\amd-gfx1150-env.ps1"

$python = $env:UNSLOTH_STUDIO_PYTHON
if (-not $python) {
    $defaultStudioPython = Join-Path $env:USERPROFILE ".unsloth\studio\unsloth_studio\Scripts\python.exe"
    if (Test-Path -LiteralPath $defaultStudioPython -PathType Leaf) {
        $python = $defaultStudioPython
    } else {
        $python = "python"
    }
}

Write-Host ""
Write-Host "HIP device probe:"
hipInfo | Select-String -Pattern "device#|Name:|gcnArchName|totalGlobalMem" | Select-Object -First 12

Write-Host ""
Write-Host "PyTorch probe ($python):"
& $python -c @"
import torch
print("torch:", torch.__version__)
print("torch.version.cuda:", getattr(torch.version, "cuda", None))
print("torch.version.hip:", getattr(torch.version, "hip", None))
print("cuda API available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
    x = torch.ones((256, 256), device="cuda")
    y = x @ x
    torch.cuda.synchronize()
    print("matmul checksum:", float(y[0, 0].detach().cpu()))
"@
