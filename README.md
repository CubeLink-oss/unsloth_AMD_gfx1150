<h1 align="center" style="margin:0;">
  <a href="https://unsloth.ai/docs"><picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/unslothai/unsloth/main/images/unsloth%20logo%20white%20text.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/unslothai/unsloth/main/images/unsloth%20logo%20black%20text.png">
    <img alt="Unsloth logo" src="https://raw.githubusercontent.com/unslothai/unsloth/main/images/unsloth%20logo%20black%20text.png" height="80" style="max-width:100%;">
  </picture></a>
</h1>
<h3 align="center" style="margin: 0; margin-top: 0;">
Unsloth Studio lets you run and train models locally.
</h3>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-install">Quickstart</a> •
  <a href="#-free-notebooks">Notebooks</a> •
  <a href="https://unsloth.ai/docs">Documentation</a>
</p>
<br>
<a href="https://unsloth.ai/docs/new/studio">
<img alt="unsloth studio ui homepage" src="https://github.com/user-attachments/assets/53ae17a9-d975-44ef-9686-efb4ebd0454d" style="max-width: 100%; margin-bottom: 0;"></a>

## Windows AMD Radeon 890M / gfx1150 Notes

[English Version](#windows-amd-radeon-890m--gfx1150-notes) / [中文版本](#windows-amd-radeon-890m--gfx1150-中文說明)

This community branch tracks Windows AMD ROCm/HIP support experiments for Unsloth Studio on AMD Radeon 890M (`gfx1150`) systems, especially Ryzen AI 9 HX 370 / HX PRO 370 laptops, mini PCs, and related devices.

Current local target:

| Item | Value |
| --- | --- |
| GPU | AMD Radeon(TM) 890M Graphics |
| GPU architecture | `gfx1150` |
| ROCm/HIP SDK | `C:\Program Files\AMD\ROCm\6.4` |
| PyTorch wheel index | `https://repo.amd.com/rocm/whl/gfx1150` |
| llama.cpp backend | HIP build with `-DGGML_HIP=ON`, `-DAMDGPU_TARGETS=gfx1150` |

For the full Traditional Chinese setup log, see [README-zh-TW-2026-05-24.md](README-zh-TW-2026-05-24.md).

### Fast GGUF Downloads

This branch adds a Studio-side segmented downloader for large GGUF files. It uses resumable HTTP Range requests instead of relying only on a single `hf_hub_download()` stream.

What it does:

- Downloads large GGUF files in 64 MB parts by default.
- Runs 16 concurrent segment workers by default.
- Stores in-progress chunks as `.part` files under `%USERPROFILE%\.unsloth\studio\cache\hf-segmented`.
- Resumes from existing `.part` files after an interrupted download.
- Merges all parts into the final `.gguf` after every segment completes.
- Shows a live PowerShell dashboard with overall progress, speed, ETA, completed/active/queued segments, and active segment progress bars.
- Falls back to `huggingface_hub` if segmented Range downloads cannot be used.

Useful knobs:

```powershell
$env:UNSLOTH_HF_DOWNLOAD_WORKERS = "32"      # default: 16, max: 32
$env:UNSLOTH_HF_DOWNLOAD_CHUNK_MB = "64"     # default: 64
$env:UNSLOTH_HF_PROGRESS_ROWS = "32"         # active segment rows shown in the terminal
$env:UNSLOTH_HF_LIVE_PROGRESS = "0"          # disable terminal dashboard
$env:UNSLOTH_HF_SEGMENTED_DOWNLOAD = "0"     # disable segmented downloader
```

Observed validation on `unsloth/Qwen3.6-35B-A3B-MTP-GGUF:UD-Q2_K_XL`: the downloader displayed `74/188 done, 16 active, 98 queued` at about `6.1 MB/s`, with per-segment progress bars in Windows Terminal.

### Supported Product Targets

Exact CPU options vary by country, retailer, and release wave. The important compatibility signal for this branch is the integrated Radeon 890M / `gfx1150` path.

#### Laptops

| Brand | Product | CPU / GPU |
| --- | --- | --- |
| Acer | Swift 14 AI | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Vivobook S 14 OLED M5406 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Vivobook S 15 OLED M5506 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Vivobook S 16 OLED M5606 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Zenbook S 16 OLED UM5606 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | ProArt PX13 | Ryzen AI 9 HX 370 / Radeon 890M; some configurations also include RTX 4050/4060/4070 |
| ASUS | ProArt P16 | Ryzen AI 9 HX 370 / Radeon 890M; configurations may include RTX 4060/4070/50-series discrete GPUs |
| ASUS | TUF Gaming A14 | Ryzen AI 9 HX 370 / Radeon 890M; configurations also include NVIDIA discrete GPUs |
| ASUS | ROG Zephyrus G14 | Ryzen AI 9 HX 370 / Radeon 890M; configurations also include NVIDIA discrete GPUs |
| ASUS | ROG Zephyrus G16 | Ryzen AI 9 HX 370 / Radeon 890M; configurations also include NVIDIA discrete GPUs |
| Dell | Pro 13 Plus / 2-in-1 | Ryzen AI 9 HX 370 or Ryzen AI 9 HX PRO 370 / Radeon 890M |
| Dell | Pro 14 Plus / 2-in-1 | Ryzen AI 9 HX 370 or Ryzen AI 9 HX PRO 370 / Radeon 890M |
| Dell | Pro 16 Plus | Ryzen AI 9 HX 370 / Radeon 890M |
| Framework | Framework Laptop 13 | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Duo OLED | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Pocket 4 | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Win 4 | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Win Mini | Ryzen AI 9 HX 370 / Radeon 890M |
| HP | OmniBook Ultra 14 | Ryzen AI 9 HX 375 / Radeon 890M |
| HP | EliteBook X G1a 14 AI | Ryzen AI 9 HX PRO 375 or HX 375 / Radeon 890M |
| Lenovo | ThinkPad P14s Gen 6 AMD | Ryzen AI 9 HX PRO 370 / Radeon 890M |
| Lenovo | ThinkPad P16s Gen 4 AMD | Ryzen AI 9 HX PRO 370 / Radeon 890M |
| MSI | Prestige A16 AI+ | Ryzen AI 9 HX 370 / Radeon 890M |
| MSI | Stealth A16 AI+ | Ryzen AI 9 HX 370 / Radeon 890M; configurations also include NVIDIA discrete GPUs |
| MSI | Creator A16 AI+ | Ryzen AI 9 HX 370 / Radeon 890M; configurations also include NVIDIA discrete GPUs |
| MSI | Pulse A17 AI+ | Ryzen AI 9 HX 370 / Radeon 890M; configurations also include NVIDIA discrete GPUs |
| NIMO | 17.3" AI Laptop | Ryzen AI 9 HX 370 / Radeon 890M |
| TUXEDO | InfinityBook Pro 14 Gen10 AMD | Ryzen AI 9 HX 370 / Radeon 890M |

#### Desktops / Mini PCs

| Brand | Product | CPU / GPU |
| --- | --- | --- |
| ACEMAGIC | F3A | Ryzen AI 9 HX 370 / Radeon 890M |
| ACEMAGIC | F5A | Ryzen AI 9 HX 470 / Radeon 890M |
| ACEMAGIC | Retro X5 | Ryzen AI 9 HX 370 / Radeon 890M |
| AOOSTAR | GEM10 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| AOOSTAR | GT37 | Ryzen AI 9 HX 370 / Radeon 890M |
| AOOSTAR | G-Flip 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| ARCTIC | Senza AI 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| Beelink | SER9 | Ryzen AI 9 HX 370 / Radeon 890M |
| Beelink | SER9 Pro | Ryzen AI 9 HX 370 / Radeon 890M |
| Beelink | SER10 Pro | Ryzen AI 9 HX 470 / Radeon 890M |
| Beelink | SER10 Max | Ryzen AI 9 HX 470 / Radeon 890M |
| BOSGAME | BeyondMax M6 / M6 HX370 AI PC | Ryzen AI 9 HX 370 / Radeon 890M |
| GEEKOM | A9 Max AI Mini PC | Ryzen AI 9 HX 370 or HX 470 / Radeon 890M |
| GMKtec | EVO-X1 AI Mini PC | Ryzen AI 9 HX 370 / Radeon 890M |
| MINISFORUM | EliteMini AI370 | Ryzen AI 9 HX 370 / Radeon 890M |
| MINISFORUM | AI X1 Pro / AI X1 Pro-370 | Ryzen AI 9 HX 370 / Radeon 890M |
| Sapphire | Edge AI 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| Topton | D12 Ultra, top-end version | Ryzen AI 9 HX 370 / Radeon 890M |

#### NAS / NAS-Like Systems

| Brand | Product | CPU / GPU |
| --- | --- | --- |
| MINISFORUM | N5 Pro AI NAS | Ryzen AI 9 HX PRO 370 / Radeon 890M |

## Windows AMD Radeon 890M / gfx1150 中文說明

[English Version](#windows-amd-radeon-890m--gfx1150-notes) / [中文版本](#windows-amd-radeon-890m--gfx1150-中文說明)

這個社群分支記錄 Unsloth Studio 在 Windows AMD ROCm/HIP 環境上的改造，目標是 AMD Radeon 890M (`gfx1150`) 系統，尤其是 Ryzen AI 9 HX 370 / HX PRO 370 筆記本、Mini PC 和相關設備。

目前本機目標：

| 項目 | 值 |
| --- | --- |
| GPU | AMD Radeon(TM) 890M Graphics |
| GPU 架構 | `gfx1150` |
| ROCm/HIP SDK | `C:\Program Files\AMD\ROCm\6.4` |
| PyTorch wheel index | `https://repo.amd.com/rocm/whl/gfx1150` |
| llama.cpp 後端 | HIP build，使用 `-DGGML_HIP=ON`、`-DAMDGPU_TARGETS=gfx1150` |

完整繁中安裝與改造紀錄請看 [README-zh-TW-2026-05-24.md](README-zh-TW-2026-05-24.md)。

### 高速 GGUF 下載

這個分支新增 Studio 端的大型 GGUF 分段下載器，不再只依賴單一路徑的 `hf_hub_download()`。

功能重點：

- 大型 GGUF 預設切成 64 MB 分段下載。
- 預設 16 個 concurrent segment workers。
- 未完成分段會以 `.part` 存在 `%USERPROFILE%\.unsloth\studio\cache\hf-segmented`。
- 中斷後可沿用既有 `.part` 檔續傳。
- 所有分段完成後會合併成最後的 `.gguf`。
- PowerShell 會顯示 live dashboard：總進度、速度、ETA、完成/進行中/排隊 segment 數，以及 active segment 進度條。
- 如果 Range 分段下載不可用，會 fallback 回 `huggingface_hub`。

可調參數：

```powershell
$env:UNSLOTH_HF_DOWNLOAD_WORKERS = "32"      # 預設 16，最高 32
$env:UNSLOTH_HF_DOWNLOAD_CHUNK_MB = "64"     # 預設 64
$env:UNSLOTH_HF_PROGRESS_ROWS = "32"         # 終端顯示的 active segment 行數
$env:UNSLOTH_HF_LIVE_PROGRESS = "0"          # 關閉終端 live dashboard
$env:UNSLOTH_HF_SEGMENTED_DOWNLOAD = "0"     # 關閉分段下載器
```

已用 `unsloth/Qwen3.6-35B-A3B-MTP-GGUF:UD-Q2_K_XL` 驗證：Windows Terminal 顯示 `74/188 done, 16 active, 98 queued`，速度約 `6.1 MB/s`，並能看到 active segment 的個別進度條。

### 適用產品清單

實際 CPU 選項會依國家、零售通路和上市批次不同而變動。對這個分支來說，關鍵相容訊號是內建 Radeon 890M / `gfx1150` 路徑。

#### 筆記本電腦

| 品牌 | 產品名稱 | CPU / GPU |
| --- | --- | --- |
| Acer | Swift 14 AI | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Vivobook S 14 OLED M5406 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Vivobook S 15 OLED M5506 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Vivobook S 16 OLED M5606 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | Zenbook S 16 OLED UM5606 | Ryzen AI 9 HX 370 / Radeon 890M |
| ASUS | ProArt PX13 | Ryzen AI 9 HX 370 / Radeon 890M，部分配置另有 RTX 4050/4060/4070 |
| ASUS | ProArt P16 | Ryzen AI 9 HX 370 / Radeon 890M，另搭 RTX 4060/4070/50 系列等獨顯配置 |
| ASUS | TUF Gaming A14 | Ryzen AI 9 HX 370 / Radeon 890M，另搭 NVIDIA 獨顯 |
| ASUS | ROG Zephyrus G14 | Ryzen AI 9 HX 370 / Radeon 890M，另搭 NVIDIA 獨顯 |
| ASUS | ROG Zephyrus G16 | Ryzen AI 9 HX 370 / Radeon 890M，另搭 NVIDIA 獨顯 |
| Dell | Pro 13 Plus / 2-in-1 | Ryzen AI 9 HX 370 或 Ryzen AI 9 HX PRO 370 / Radeon 890M |
| Dell | Pro 14 Plus / 2-in-1 | Ryzen AI 9 HX 370 或 Ryzen AI 9 HX PRO 370 / Radeon 890M |
| Dell | Pro 16 Plus | Ryzen AI 9 HX 370 / Radeon 890M |
| Framework | Framework Laptop 13 | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Duo OLED | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Pocket 4 | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Win 4 | Ryzen AI 9 HX 370 / Radeon 890M |
| GPD | Win Mini | Ryzen AI 9 HX 370 / Radeon 890M |
| HP | OmniBook Ultra 14 | Ryzen AI 9 HX 375 / Radeon 890M |
| HP | EliteBook X G1a 14 AI | Ryzen AI 9 HX PRO 375 或 HX 375 / Radeon 890M |
| Lenovo | ThinkPad P14s Gen 6 AMD | Ryzen AI 9 HX PRO 370 / Radeon 890M |
| Lenovo | ThinkPad P16s Gen 4 AMD | Ryzen AI 9 HX PRO 370 / Radeon 890M |
| MSI | Prestige A16 AI+ | Ryzen AI 9 HX 370 / Radeon 890M |
| MSI | Stealth A16 AI+ | Ryzen AI 9 HX 370 / Radeon 890M，另搭 NVIDIA 獨顯 |
| MSI | Creator A16 AI+ | Ryzen AI 9 HX 370 / Radeon 890M，另搭 NVIDIA 獨顯 |
| MSI | Pulse A17 AI+ | Ryzen AI 9 HX 370 / Radeon 890M，另搭 NVIDIA 獨顯 |
| NIMO | 17.3" AI Laptop | Ryzen AI 9 HX 370 / Radeon 890M |
| TUXEDO | InfinityBook Pro 14 Gen10 AMD | Ryzen AI 9 HX 370 / Radeon 890M |

#### 台式電腦 / Mini PC

| 品牌 | 產品名稱 | CPU / GPU |
| --- | --- | --- |
| ACEMAGIC | F3A | Ryzen AI 9 HX 370 / Radeon 890M |
| ACEMAGIC | F5A | Ryzen AI 9 HX 470 / Radeon 890M |
| ACEMAGIC | Retro X5 | Ryzen AI 9 HX 370 / Radeon 890M |
| AOOSTAR | GEM10 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| AOOSTAR | GT37 | Ryzen AI 9 HX 370 / Radeon 890M |
| AOOSTAR | G-Flip 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| ARCTIC | Senza AI 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| Beelink | SER9 | Ryzen AI 9 HX 370 / Radeon 890M |
| Beelink | SER9 Pro | Ryzen AI 9 HX 370 / Radeon 890M |
| Beelink | SER10 Pro | Ryzen AI 9 HX 470 / Radeon 890M |
| Beelink | SER10 Max | Ryzen AI 9 HX 470 / Radeon 890M |
| BOSGAME | BeyondMax M6 / M6 HX370 AI PC | Ryzen AI 9 HX 370 / Radeon 890M |
| GEEKOM | A9 Max AI Mini PC | Ryzen AI 9 HX 370 或 HX 470 / Radeon 890M |
| GMKtec | EVO-X1 AI Mini PC | Ryzen AI 9 HX 370 / Radeon 890M |
| MINISFORUM | EliteMini AI370 | Ryzen AI 9 HX 370 / Radeon 890M |
| MINISFORUM | AI X1 Pro / AI X1 Pro-370 | Ryzen AI 9 HX 370 / Radeon 890M |
| Sapphire | Edge AI 370 | Ryzen AI 9 HX 370 / Radeon 890M |
| Topton | D12 Ultra, top-end version | Ryzen AI 9 HX 370 / Radeon 890M |

#### NAS / 類 NAS 系統

| 品牌 | 產品名稱 | CPU / GPU |
| --- | --- | --- |
| MINISFORUM | N5 Pro AI NAS | Ryzen AI 9 HX PRO 370 / Radeon 890M |

## ⚡ Get started

#### macOS, Linux, WSL:
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```
#### Windows:
```powershell
irm https://unsloth.ai/install.ps1 | iex
```
#### Community:

- [Discord](https://discord.gg/unsloth)
- [𝕏 (Twitter)](https://x.com/UnslothAI)
- [Reddit](https://reddit.com/r/unsloth)

## ⭐ Features
Unsloth Studio (Beta) lets you run and train text, [audio](https://unsloth.ai/docs/basics/text-to-speech-tts-fine-tuning), [embedding](https://unsloth.ai/docs/new/embedding-finetuning), [vision](https://unsloth.ai/docs/basics/vision-fine-tuning) models on Windows, Linux and macOS.

### Inference
* **Search + download + run models** including GGUF, LoRA adapters, safetensors
* **Export models**: [Save or export](https://unsloth.ai/docs/new/studio/export) models to GGUF, 16-bit safetensors and other formats.
* **Tool calling**: Support for [self-healing tool calling](https://unsloth.ai/docs/new/studio/chat#auto-healing-tool-calling) and web search
* **[Code execution](https://unsloth.ai/docs/new/studio/chat#code-execution)**: lets LLMs test code in Claude artifacts and sandbox environments
* **[API inference endpoint](https://unsloth.ai/docs/basics/api)**: Deploy and run local LLMs in Claude Code, Codex tools with Unsloth
* [Auto set inference settings](https://unsloth.ai/docs/new/studio/chat#auto-parameter-tuning) and customize chat templates.
* We work directly with teams behind [gpt-oss](https://docs.unsloth.ai/new/gpt-oss-how-to-run-and-fine-tune#unsloth-fixes-for-gpt-oss), [Qwen3](https://www.reddit.com/r/LocalLLaMA/comments/1kaodxu/qwen3_unsloth_dynamic_ggufs_128k_context_bug_fixes/), [Llama 4](https://github.com/ggml-org/llama.cpp/pull/12889), [Mistral](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/discussions/18), [Gemma 1-3](https://news.ycombinator.com/item?id=39671146), and [Phi-4](https://unsloth.ai/blog/phi4), where we’ve fixed bugs that improve model accuracy.
* Chat with images, audio, PDFs, code, DOCX and more. [Connect API providers](https://unsloth.ai/docs/integrations/connections) (OpenAI, Anthropic) or servers (vLLM, Ollama).
### Training
* Train and RL **500+ models** up to **2x faster** with up to **70% less VRAM**, with no accuracy loss.
* Custom Triton and mathematical **kernels**. See some collabs we did with [PyTorch](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/fp8-reinforcement-learning) and [Hugging Face](https://unsloth.ai/docs/new/faster-moe).
* **Data Recipes**: [Auto-create datasets](https://unsloth.ai/docs/new/studio/data-recipe) from **PDF, CSV, DOCX** etc. Edit data in a visual-node workflow.
* **[Reinforcement Learning](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide)** (RL): The most efficient [RL](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide) library, using **80% less VRAM** for GRPO, [FP8](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/fp8-reinforcement-learning) etc.
* Supports full fine-tuning, RL, pretraining, 4-bit, 16-bit and, FP8 training.
* **Observability**: Monitor training live, track loss and GPU usage and customize graphs.
* [Multi-GPU](https://unsloth.ai/docs/basics/multi-gpu-training-with-unsloth) training is supported, with major improvements coming soon.

## 📥 Install
Unsloth can be used in two ways: through **[Unsloth Studio](https://unsloth.ai/docs/new/studio/)**, the web UI, or through **Unsloth Core**, the code-based version. Each has different requirements.

### Unsloth Studio (web UI)
Unsloth Studio (Beta) works on **Windows, Linux, WSL** and **macOS**.

* **CPU:** Supported for Chat and Data Recipes currently
* **NVIDIA:** Training works on RTX 30/40/50, Blackwell, DGX Spark, Station and more
* **macOS:** Training, MLX and GGUF inference are ALL supported.
* **AMD:** Chat + Data works. Train with [Unsloth Core](#unsloth-core-code-based). Studio support is out soon.
* **Multi-GPU:** Available now, with a major upgrade on the way

#### macOS, Linux, WSL:
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```
#### Windows:
```powershell
irm https://unsloth.ai/install.ps1 | iex
```

#### Launch
```bash
unsloth studio -p 8888
```
For cloud or global access, add `-H 0.0.0.0`. By default, Unsloth is accessible only locally.

#### Update
To update, use the same install commands above or use `unsloth studio update`.

#### Docker
Use our [Docker image](https://hub.docker.com/r/unsloth/unsloth) ```unsloth/unsloth``` container. Run:
```bash
docker run -d -e JUPYTER_PASSWORD="mypassword" \
  -p 8888:8888 -p 8000:8000 -p 2222:22 \
  -v $(pwd)/work:/workspace/work \
  --gpus all \
  unsloth/unsloth
  ```

#### Developer, Nightly, Uninstall
To see developer, nightly and uninstallation etc. instructions, see [advanced installation](#-advanced-installation).

### Unsloth Core (code-based)
#### Linux, WSL:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv unsloth_env --python 3.13
source unsloth_env/bin/activate
uv pip install unsloth --torch-backend=auto
```
#### Windows:
```powershell
winget install -e --id Python.Python.3.13
winget install --id=astral-sh.uv  -e
uv venv unsloth_env --python 3.13
.\unsloth_env\Scripts\activate
uv pip install unsloth --torch-backend=auto
```
For Windows, `pip install unsloth` works only if you have PyTorch installed. Read our [Windows Guide](https://unsloth.ai/docs/get-started/install/windows-installation).
You can use the same Docker image as Unsloth Studio.

#### AMD, Intel:
For RTX 50x, B200, 6000 GPUs: `uv pip install unsloth --torch-backend=auto`. Read our guides for: [Blackwell](https://unsloth.ai/docs/blog/fine-tuning-llms-with-blackwell-rtx-50-series-and-unsloth) and [DGX Spark](https://unsloth.ai/docs/blog/fine-tuning-llms-with-nvidia-dgx-spark-and-unsloth). <br>
To install Unsloth on **AMD** and **Intel** GPUs, follow our [AMD Guide](https://unsloth.ai/docs/get-started/install/amd) and [Intel Guide](https://unsloth.ai/docs/get-started/install/intel).

## 📒 Free Notebooks

Train for free with our notebooks. You can use our new [free Unsloth Studio notebook](https://colab.research.google.com/github/unslothai/unsloth/blob/main/studio/Unsloth_Studio_Colab.ipynb) to run and train models for free in a web UI.
Read our [guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide). Add dataset, run, then deploy your trained model.

| Model | Free Notebooks | Performance | Memory use |
|-----------|---------|--------|----------|
| **Gemma 4 (E2B)**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Gemma4_(E2B)-Vision.ipynb)               | 1.5x faster | 50% less |
| **Qwen3.5 (4B)**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_5_(4B)_Vision.ipynb)               | 1.5x faster | 60% less |
| **gpt-oss (20B)**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/gpt-oss-(20B)-Fine-tuning.ipynb)               | 2x faster | 70% less |
| **Qwen3.5 GSPO**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_5_(4B)_Vision_GRPO.ipynb)               | 2x faster | 70% less |
| **gpt-oss (20B): GRPO**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/gpt-oss-(20B)-GRPO.ipynb)               | 2x faster | 80% less |
| **Qwen3: Advanced GRPO**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_(4B)-GRPO.ipynb)               | 2x faster | 70% less |
| **embeddinggemma (300M)**    | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/EmbeddingGemma_(300M).ipynb)               | 2x faster | 20% less |
| **Mistral Ministral 3 (3B)**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Ministral_3_VL_(3B)_Vision.ipynb)               | 1.5x faster | 60% less |
| **Llama 3.1 (8B) Alpaca**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Llama3.1_(8B)-Alpaca.ipynb)               | 2x faster | 70% less |
| **Llama 3.2 Conversational**      | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Llama3.2_(1B_and_3B)-Conversational.ipynb)               | 2x faster | 70% less |
| **Orpheus-TTS (3B)**     | [▶️ Start for free](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Orpheus_(3B)-TTS.ipynb)               | 1.5x faster | 50% less |

- See all our notebooks for: [Kaggle](https://github.com/unslothai/notebooks?tab=readme-ov-file#-kaggle-notebooks), [GRPO](https://unsloth.ai/docs/get-started/unsloth-notebooks#grpo-reasoning-rl-notebooks), [TTS](https://unsloth.ai/docs/get-started/unsloth-notebooks#text-to-speech-tts-notebooks), [embedding](https://unsloth.ai/docs/new/embedding-finetuning) & [Vision](https://unsloth.ai/docs/get-started/unsloth-notebooks#vision-multimodal-notebooks)
- See [all our models](https://unsloth.ai/docs/get-started/unsloth-model-catalog) and [all our notebooks](https://unsloth.ai/docs/get-started/unsloth-notebooks)
- See detailed documentation for Unsloth [here](https://unsloth.ai/docs)

## 🦥 Unsloth News
- **Connections**: Connect any API provider (OpenAI, Anthropic) or server (vLLM, Ollama). [Guide](https://unsloth.ai/docs/integrations/connections)
- **MTP**: Run Qwen3.6 MTP in Unsloth. MTP settings are autoset specific to your hardware. [Guide](https://unsloth.ai/docs/models/qwen3.6#mtp-guide)
- **API inference endpoint**: Deploy and run local LLMs in Claude Code, Codex tools. [Guide](https://unsloth.ai/docs/basics/api)
- **Qwen3.6**: Qwen3.6-35B-A3B can now be trained and run in Unsloth Studio. [Blog](https://unsloth.ai/docs/models/qwen3.6)
- **Gemma 4**: Run and train Google’s new models directly in Unsloth. [Blog](https://unsloth.ai/docs/models/gemma-4)
- **Introducing Unsloth Studio**: our new web UI for running and training LLMs. [Blog](https://unsloth.ai/docs/new/studio)
- **Qwen3.5** - 0.8B, 2B, 4B, 9B, 27B, 35-A3B, 112B-A10B are now supported. [Guide + notebooks](https://unsloth.ai/docs/models/qwen3.5/fine-tune)
- Train **MoE LLMs 12x faster** with 35% less VRAM - DeepSeek, GLM, Qwen and gpt-oss. [Blog](https://unsloth.ai/docs/new/faster-moe)
- **Embedding models**: Unsloth now supports ~1.8-3.3x faster embedding fine-tuning. [Blog](https://unsloth.ai/docs/new/embedding-finetuning) • [Notebooks](https://unsloth.ai/docs/get-started/unsloth-notebooks#embedding-models)
- New **7x longer context RL** vs. all other setups, via our new batching algorithms. [Blog](https://unsloth.ai/docs/new/grpo-long-context)
- New RoPE & MLP **Triton Kernels** & **Padding Free + Packing**: 3x faster training & 30% less VRAM. [Blog](https://unsloth.ai/docs/new/3x-faster-training-packing)
- **500K Context**: Training a 20B model with >500K context is now possible on an 80GB GPU. [Blog](https://unsloth.ai/docs/blog/500k-context-length-fine-tuning)
- **FP8 & Vision RL**: You can now do FP8 & VLM GRPO on consumer GPUs. [FP8 Blog](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/fp8-reinforcement-learning) • [Vision RL](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/vision-reinforcement-learning-vlm-rl)

## 📥 Advanced Installation
The below advanced instructions are for Unsloth Studio. For Unsloth Core advanced installation, [view our docs](https://unsloth.ai/docs/get-started/install/pip-install#advanced-pip-installation).
#### Developer installs: macOS, Linux, WSL:
```bash
git clone https://github.com/unslothai/unsloth
cd unsloth
./install.sh --local
unsloth studio -p 8888
```
Then to update :
```bash
unsloth studio update
```

#### Developer installs: Windows PowerShell:
```powershell
git clone https://github.com/unslothai/unsloth.git
cd unsloth
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1 --local
unsloth studio -p 8888
```
Then to update :
```bash
unsloth studio update
```

#### Nightly: MacOS, Linux, WSL:
```bash
git clone https://github.com/unslothai/unsloth
cd unsloth
git checkout nightly
./install.sh --local
unsloth studio -p 8888
```
Then to launch every time:
```bash
unsloth studio -p 8888
```

#### Nightly: Windows:
Run in Windows Powershell:
```bash
git clone https://github.com/unslothai/unsloth.git
cd unsloth
git checkout nightly
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1 --local
unsloth studio -p 8888
```
Then to launch every time:
```bash
unsloth studio -p 8888
```

#### Uninstall
The recommended way to fully remove Unsloth Studio is the matching uninstall script for your OS. It stops any running servers, removes the install dir, the launcher data dir, the desktop shortcut, and any platform-specific entries (macOS `.app` bundle + Launch Services on Mac; Start Menu, `HKCU\Software\Unsloth` registry key and user `PATH` entries on Windows):

* ​ **MacOS, WSL, Linux:** `curl -fsSL https://raw.githubusercontent.com/unslothai/unsloth/main/scripts/uninstall.sh | sh`
* ​ **Windows (PowerShell):** `irm https://raw.githubusercontent.com/unslothai/unsloth/main/scripts/uninstall.ps1 | iex`

If you only want to drop the install dir and keep the launcher/shortcut for a later reinstall, you can instead run `rm -rf ~/.unsloth/studio` (Mac/Linux/WSL) or `Remove-Item -Recurse -Force "$HOME\.unsloth\studio"` (Windows). The model cache at `~/.cache/huggingface` is not touched by any of these.

For more info, [see our docs](https://unsloth.ai/docs/new/studio/install#uninstall).

#### Deleting model files

You can delete old model files either from the bin icon in model search or by removing the relevant cached model folder from the default Hugging Face cache directory. By default, HF uses:

* ​ **MacOS, Linux, WSL:** `~/.cache/huggingface/hub/`
* ​ **Windows:** `%USERPROFILE%\.cache\huggingface\hub\`

## 💚 Community and Links
| Type                                                                                                                                      | Links                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| <img width="16" src="https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/66e3d80db9971f10a9757c99_Symbol.svg" />  **Discord**                       | [Join Discord server](https://discord.com/invite/unsloth)                          |
| <img width="15" src="https://redditinc.com/hs-fs/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png" />  **r/unsloth Reddit**                       | [Join Reddit community](https://reddit.com/r/unsloth)                          |
| 📚 **Documentation & Wiki**                                                                                                               | [Read Our Docs](https://unsloth.ai/docs)                                       |
| <img width="13" src="https://upload.wikimedia.org/wikipedia/commons/0/09/X_(formerly_Twitter)_logo_late_2025.svg" />  **Twitter (aka X)** | [Follow us on X](https://twitter.com/unslothai)                                |
| 🔮 **Our Models**                                                                                                                         | [Unsloth Catalog](https://unsloth.ai/docs/get-started/unsloth-model-catalog)   |
| ✍️ **Blog**                                                                                                                               | [Read our Blogs](https://unsloth.ai/blog)                                      |

### Citation

You can cite the Unsloth repo as follows:
```bibtex
@software{unsloth,
  author = {Daniel Han, Michael Han and Unsloth team},
  title = {Unsloth},
  url = {https://github.com/unslothai/unsloth},
  year = {2023}
}
```
If you trained a model with 🦥Unsloth, you can use this cool sticker!   <img src="https://raw.githubusercontent.com/unslothai/unsloth/main/images/made with unsloth.png" width="200" align="center" />

### License
Unsloth uses a dual-licensing model of Apache 2.0 and AGPL-3.0. The core Unsloth package remains licensed under **[Apache 2.0](https://github.com/unslothai/unsloth?tab=Apache-2.0-1-ov-file)**, while certain optional components, such as the Unsloth Studio UI are licensed under the open-source license **[AGPL-3.0](https://github.com/unslothai/unsloth?tab=AGPL-3.0-2-ov-file)**.

This structure helps support ongoing Unsloth development while keeping the project open source and enabling the broader ecosystem to continue growing.

### Thank You to
- The [llama.cpp library](https://github.com/ggml-org/llama.cpp) that lets users run and save models with Unsloth
- The Hugging Face team and their libraries: [transformers](https://github.com/huggingface/transformers) and [TRL](https://github.com/huggingface/trl)
- The Pytorch and [Torch AO](https://github.com/unslothai/unsloth/pull/3391) team for their contributions
- NVIDIA for their [NeMo DataDesigner](https://github.com/NVIDIA-NeMo/DataDesigner) library and their contributions
- And of course for every single person who has contributed or has used Unsloth!
