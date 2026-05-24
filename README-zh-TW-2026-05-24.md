# Unsloth Studio AMD Radeon 890M gfx1150 Windows ROCm 改造紀錄

撰寫日期：2026-05-24  
目標系統：Microsoft Windows 11  
目標 GPU：AMD Radeon(TM) 890M Graphics  
GPU 架構：`gfx1150`  
ROCm/HIP SDK：`6.4.50101-9a6572ae7`  
Unsloth upstream commit：`83b20976f747533c0d92a734c102bbe5d5af81cf`

這份 README 仿照 Ollama 的紀錄方式，記錄目前這個 Unsloth Studio checkout 對 Windows AMD ROCm/HIP 的改造點、安裝方式和驗證方式。

## 目標

讓 `unslothai/unsloth` 的 Windows Studio 安裝流程可以識別本機 AMD HIP SDK，不要把 Radeon 890M 誤判成 CPU-only，並固定 `gfx1150` 相關環境，支援：

- AMD Radeon(TM) 890M Graphics
- Windows ROCm/HIP SDK 6.4
- `gfx1150`
- Unsloth Studio local install
- PyTorch ROCm Windows `gfx1150` wheel index
- llama.cpp HIP source build 參數

## 重要路徑

本專案位置：

```text
F:\A_CODEX_Project\unsloth_AMD_gfx1150
```

AMD HIP SDK：

```text
C:\Program Files\AMD\ROCm\6.4
C:\Program Files\AMD\ROCm\6.4\bin\hipconfig.exe
C:\Program Files\AMD\ROCm\6.4\bin\hipInfo.exe
```

Unsloth Studio 預設安裝位置：

```text
%USERPROFILE%\.unsloth\studio
%USERPROFILE%\.unsloth\studio\unsloth_studio
```

## 已確認的本機狀態

HIP SDK：

```text
hipconfig: 6.4.50101-9a6572ae7
hipInfo: AMD Radeon(TM) 890M Graphics
```

目前 Python 狀態：

```text
Python 3.13.13
py launcher: 3.12, 3.13, 3.14
```

注意：AMD 官方 Windows support matrix 的泛用 PyTorch on Windows 清單沒有列 `gfx1150`。因此本專案不使用 generic `repo.radeon.com/rocm/windows/rocm-rel-7.2/` wheel 路徑，而是使用按架構分流的 `https://repo.amd.com/rocm/whl/gfx1150` wheel index。這個 index 目前提供 Python 3.12 / 3.13 Windows wheels；本 installer 預設使用 Python 3.13，Python 3.12 也可解析。

## 本次改造檔案

Windows Studio installer：

```text
install.ps1
```

修改重點：

- 新增 `--amd-rocm` 旗標。
- 支援 `UNSLOTH_AMD_ROCM_WINDOWS=1`。
- 偵測 `hipInfo.exe` / `hipconfig.exe`。
- 偵測 AMD HIP GPU 時，使用 `gfx1150` index 支援的 Python 3.12 / 3.13；本機目前以 Python 3.13 驗證。
- AMD ROCm Windows 路徑使用 `gfx1150` wheel index：

```text
https://repo.amd.com/rocm/whl/gfx1150
torch==2.9.1+rocm7.12.0
torchvision==0.24.0+rocm7.12.0
torchaudio==2.9.0+rocm7.12.0
rocm-sdk-libraries-gfx1150==7.12.0
```

已用 `uv pip install --dry-run --python <Python 3.13> --index-url https://repo.amd.com/rocm/whl/gfx1150 ...` 驗證 dependency resolver 可解析到 `rocm-sdk-libraries-gfx1150==7.12.0`。Python 3.12 dry-run 也可解析。這仍不等於已完成 runtime smoke test；安裝後還要執行 `scripts\verify-amd-gfx1150.ps1` 確認 `torch.version.hip`、`torch.cuda.is_available()` 和 GPU matmul。

Studio setup：

```text
studio\setup.ps1
```

修改重點：

- 沒有 NVIDIA 時會再偵測 AMD HIP GPU。
- AMD HIP GPU 存在時，不再顯示單純 CPU-only 提示。
- 設定：

```text
HIP_PATH
ROCM_PATH
AMDGPU_TARGETS=gfx1150
```

- llama.cpp source build 時加入：

```text
-DGGML_HIP=ON
-DAMDGPU_TARGETS=gfx1150
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

本機已另外用 Visual Studio 2022 Build Tools + HIP SDK 6.4 編譯 `llama-server`，關鍵 CMake 參數：

```text
-DGGML_HIP=ON
-DAMDGPU_TARGETS=gfx1150
-DCMAKE_HIP_ARCHITECTURES=gfx1150
-DCMAKE_CXX_COMPILER=C:\Program Files\AMD\ROCm\6.4\bin\hipcc.exe
-DCMAKE_CXX_FLAGS=--offload-arch=gfx1150
```

已驗證替換到 Studio 使用的位置：

```text
%USERPROFILE%\.unsloth\llama.cpp\build\bin\Release\llama-server.exe
```

`llama-server --list-devices` 預期會看到：

```text
Available devices:
  ROCm0: AMD Radeon(TM) 890M Graphics
```

新增輔助腳本：

```text
scripts\amd-gfx1150-env.ps1
scripts\install-amd-gfx1150-local.ps1
scripts\verify-amd-gfx1150.ps1
```

## 快速安裝

從 repo root 執行：

```powershell
cd F:\A_CODEX_Project\unsloth_AMD_gfx1150
powershell -ExecutionPolicy Bypass -File .\scripts\install-amd-gfx1150-local.ps1
```

等價手動流程：

```powershell
cd F:\A_CODEX_Project\unsloth_AMD_gfx1150
.\scripts\amd-gfx1150-env.ps1
$env:UNSLOTH_AMD_ROCM_WINDOWS = "1"
powershell -ExecutionPolicy Bypass -File .\install.ps1 --local --amd-rocm
```

## 啟動 Studio

```powershell
cd F:\A_CODEX_Project\unsloth_AMD_gfx1150
.\scripts\amd-gfx1150-env.ps1
$env:UNSLOTH_STUDIO_PYTHON = "$env:USERPROFILE\.unsloth\studio\unsloth_studio\Scripts\python.exe"
& "$env:USERPROFILE\.unsloth\studio\unsloth_studio\Scripts\unsloth.exe" studio -p 8888
```

瀏覽器開：

```text
http://127.0.0.1:8888
```

## 驗證

安裝後執行：

```powershell
cd F:\A_CODEX_Project\unsloth_AMD_gfx1150
powershell -ExecutionPolicy Bypass -File .\scripts\verify-amd-gfx1150.ps1
```

預期重點：

```text
hipInfo 顯示 AMD Radeon(TM) 890M Graphics
torch.version.hip 不是 None
torch.cuda.is_available() 是 True
device 顯示 AMD Radeon(TM) 890M Graphics
matmul checksum: 256.0
```

PyTorch 在 ROCm/HIP 上仍使用 `torch.cuda.*` API，這是正常的；判斷是否真的走 ROCm 要看 `torch.version.hip`。

## 重要限制

- Installer 預設使用 Python 3.13；`gfx1150` index 也支援 Python 3.12。
- `gfx1150` index 有 `torchaudio`，目前安裝 `torchaudio==2.9.0+rocm7.12.0`。
- AMD 上 bitsandbytes / 4-bit 訓練仍比 NVIDIA CUDA 路徑敏感，若遇到不穩定，先用非 4-bit 或 GGUF chat 驗證基礎環境。
- llama.cpp HIP source build 需要 Visual Studio Build Tools、CMake、HIP SDK 都能被 CMake 找到。

## 快速接手 Checklist

1. 確認 `F:\A_CODEX_Project\unsloth_AMD_gfx1150` 存在。
2. 確認 `C:\Program Files\AMD\ROCm\6.4\bin\hipconfig.exe` 存在。
3. 執行 `.\scripts\amd-gfx1150-env.ps1`。
4. 執行 `hipconfig`，應顯示 `6.4.50101-9a6572ae7`。
5. 執行 `hipInfo`，應看到 `AMD Radeon(TM) 890M Graphics`。
6. 若尚未安裝 Studio，執行 `.\scripts\install-amd-gfx1150-local.ps1`。
7. 安裝後執行 `.\scripts\verify-amd-gfx1150.ps1`。
8. 啟動 `unsloth studio -p 8888`，用 `http://127.0.0.1:8888` 開啟。
