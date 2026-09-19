# Cube 3D — Pinokio one-click installer

One-click Pinokio launcher for [Roblox/cube](https://github.com/Roblox/cube) (Cube 3D, text → 3D shape),
with a Gradio web UI, automatic CUDA/torch setup and automatic download of the
[Roblox/cube3d-v0.5](https://huggingface.co/Roblox/cube3d-v0.5) weights.

## Difference with the existing Pinokio app

[`pinokiofactory/cube`](https://github.com/pinokiofactory/cube) installs the
[`peanutcocktail/cube`](https://github.com/peanutcocktail/cube) fork with the **v0.1** weights.
This launcher clones the **upstream Roblox repo at its latest commit** and uses the **v0.5** weights,
plus its own web UI and the optional CubePart module.

## Install

1. Push this repo to GitHub (see below).
2. In Pinokio: **Discover → Download from URL** → paste your repo URL (e.g. `https://github.com/<user>/cube3D`).
3. Click **Install**. Everything is automatic:
   - clones `https://github.com/Roblox/cube` into `app/`
   - creates the `env` virtual environment and installs cube + `pymeshlab` (optional, never blocks the install)
   - installs the right torch build for your machine (CUDA 12.8 on NVIDIA, ROCm on Linux/AMD, MPS on Apple Silicon, CPU otherwise)
   - installs `gradio` + `trimesh`
   - downloads the model weights (~5 GB) into `app/model_weights/`
4. Click **Start**, then **Open Web UI**.

## Web UI

- prompt → 3D mesh, previewed in the browser and downloadable as `.obj` and `.glb`
- settings: fast inference (CUDA graphs), resolution base (4–9), top-p sampling, bounding-box constraint, mesh simplification
- every result is saved in `app/outputs/` (also shared with other Pinokio apps through the Pinokio drive)

## CubePart (optional module)

The upstream repo also ships **CubePart** (open-vocabulary, part-controllable generation:
a mesh + a list of part names → one mesh per part). It is *not* installed by default because it
needs ~10 GB of extra weights ([`Roblox/cubepart`](https://huggingface.co/Roblox/cubepart):
`multi_part_dit.safetensors` 8.6 GB + `vae.safetensors` 1.3 GB) and a large GPU.

Menu → **Install CubePart** installs `cube_part` into the same venv (`--no-deps`, so the CUDA torch
build is untouched), downloads the weights into `app/cubepart/weights/`, and adds a **Start CubePart**
entry that runs the upstream demo `cubepart/examples/gradio_demo.py` on port **7861**
(Cube 3D itself uses **7860**, so both can run side by side).

## Hardware

- NVIDIA GPU with ≥16 GB VRAM (24 GB recommended for **fast inference**)
- Apple Silicon M2+ works through MPS (slower, fast inference disabled)
- CPU works but is very slow
- Windows + AMD is not supported by cube (DirectML has no cube backend) — the installer falls back to a CPU torch build

## Files

| File | Role |
| --- | --- |
| `pinokio.js` | Pinokio menu (Install / Start / Open Web UI / Outputs / Update / Reset) |
| `install.js` | full installation pipeline |
| `torch.js` | platform-aware torch install (CUDA / ROCm / MPS / CPU) |
| `start.js` | launches `app.py` and exposes the web UI URL |
| `update.js` | `git pull` on both repos + reinstall deps |
| `reset.js` | deletes `app/` (venv included) |
| `app.py` | Gradio web UI wrapping `cube3d.inference.engine` |
| `install_cubepart.js` / `start_cubepart.js` | optional CubePart module (port 7861) |
| `download_weights.py` | downloads HF weights (`Roblox/cube3d-v0.5`, or `Roblox/cubepart` with `--repo`) |

`app.py` is run from inside the cloned cube repo (`python ../app.py`), so cube is always used at its
latest cloned version — nothing in the upstream repo is patched.

## Publish to GitHub

```bash
git add -A && git commit -m "Pinokio one-click installer for Roblox Cube 3D"
```

Then create the GitHub repo and push:

```bash
git remote add origin https://github.com/<user>/cube3D.git && git branch -M main && git push -u origin main
```

## Notes

- Blender ≥ 4.3 in the PATH is only needed for the upstream `--render-gif` CLI flag; the web UI does not use it.
- `cubepart` (part segmentation) ships in the upstream repo but is not installed here — it needs a separate, much heavier dependency set.
