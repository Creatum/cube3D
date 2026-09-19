"""Gradio web UI for Roblox Cube 3D (text -> 3D shape).

Launched by Pinokio from the cloned repo folder:  python ../app.py  (cwd = app/)
"""

import argparse
import datetime
import inspect
import os
import sys
import traceback

import gradio as gr
import torch
import trimesh

APP_DIR = os.getcwd()
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from cube3d.inference.engine import Engine, EngineFast  # noqa: E402
from cube3d.inference.utils import select_device  # noqa: E402

try:
    from cube3d.mesh_utils.postprocessing import (
        PYMESHLAB_AVAILABLE,
        create_pymeshset,
        postprocess_mesh,
        save_mesh,
    )
except Exception:  # cube build without the postprocessing module
    PYMESHLAB_AVAILABLE = False

CONFIG_CANDIDATES = [
    "cube3d/configs/open_model_v0.5.yaml",
    "cube3d/configs/open_model.yaml",
]
GPT_CKPT = os.path.join("model_weights", "shape_gpt.safetensors")
SHAPE_CKPT = os.path.join("model_weights", "shape_tokenizer.safetensors")
OUTPUT_DIR = os.path.join(APP_DIR, "outputs")

STATE = {"engine": None, "fast": None}


def supported_kwargs(func, **kwargs):
    """Keep only the kwargs this Gradio version actually accepts.

    Gradio 6 moved `theme` from Blocks() to launch() and dropped `show_api`.
    """
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        return kwargs
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return kwargs
    return {k: v for k, v in kwargs.items() if k in params}


LAUNCH_TAKES_THEME = "theme" in supported_kwargs(gr.Blocks.launch, theme=None)


def config_path():
    for candidate in CONFIG_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No cube3d config found. Expected one of: " + ", ".join(CONFIG_CANDIDATES)
    )


def device_label(device):
    if device.type == "cuda":
        try:
            return "CUDA - " + torch.cuda.get_device_name(0)
        except Exception:
            return "CUDA"
    if device.type == "mps":
        return "Apple MPS"
    return "CPU (slow)"


def get_engine(fast):
    device = select_device()
    fast = bool(fast) and device.type == "cuda"
    if STATE["engine"] is not None and STATE["fast"] == fast:
        return STATE["engine"], device

    for ckpt in (GPT_CKPT, SHAPE_CKPT):
        if not os.path.exists(os.path.join(APP_DIR, ckpt)):
            raise FileNotFoundError(
                "Missing weights: " + ckpt + ". Run the Pinokio install again "
                "(it downloads Roblox/cube3d-v0.5 into model_weights/)."
            )

    STATE["engine"] = None  # free VRAM before loading the other engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    cls = EngineFast if fast else Engine
    print("Loading {} on {}...".format(cls.__name__, device), flush=True)
    engine = cls(config_path(), GPT_CKPT, SHAPE_CKPT, device=device)
    STATE["engine"] = engine
    STATE["fast"] = fast
    return engine, device


def export_mesh(vertices, faces, stem, simplify):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    obj_path = os.path.join(OUTPUT_DIR, stem + ".obj")
    glb_path = os.path.join(OUTPUT_DIR, stem + ".glb")

    if PYMESHLAB_AVAILABLE:
        ms = create_pymeshset(vertices, faces)
        if simplify:
            target_face_num = max(10000, int(faces.shape[0] * 0.1))
            print("Postprocessing mesh to {} faces".format(target_face_num), flush=True)
            postprocess_mesh(ms, target_face_num, obj_path)
        save_mesh(ms, obj_path)
        mesh = trimesh.load(obj_path, force="mesh")
    else:
        mesh = trimesh.Trimesh(vertices, faces)
        mesh.export(obj_path)

    mesh.export(glb_path)
    return obj_path, glb_path, mesh


def generate(prompt, fast, resolution_base, top_p, use_top_p, use_bbox, bx, by, bz, simplify):
    prompt = (prompt or "").strip()
    if not prompt:
        raise gr.Error("Please enter a prompt.")

    try:
        engine, device = get_engine(fast)
    except Exception as exc:
        traceback.print_exc()
        raise gr.Error(str(exc))

    bounding_box_xyz = (float(bx), float(by), float(bz)) if use_bbox else None

    try:
        mesh_v_f = engine.t2s(
            [prompt],
            use_kv_cache=True,
            resolution_base=float(resolution_base),
            top_p=float(top_p) if use_top_p else None,
            bounding_box_xyz=bounding_box_xyz,
        )
    except Exception as exc:
        traceback.print_exc()
        raise gr.Error("Generation failed: {}".format(exc))

    vertices, faces = mesh_v_f[0][0], mesh_v_f[0][1]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = "".join(c if c.isalnum() else "_" for c in prompt.lower())[:40].strip("_")
    obj_path, glb_path, mesh = export_mesh(
        vertices, faces, stamp + "_" + (slug or "shape"), simplify
    )

    info = (
        "**" + prompt + "**\n\n"
        "- device: " + device_label(device)
        + (" - fast inference" if STATE["fast"] else "") + "\n"
        "- vertices: {:,} - faces: {:,}\n".format(len(mesh.vertices), len(mesh.faces))
        + "- saved to `outputs/`"
    )
    return glb_path, [obj_path, glb_path], info


def build_ui():
    device = select_device()
    blocks_kwargs = {"title": "Cube 3D - Roblox"}
    if not LAUNCH_TAKES_THEME:
        blocks_kwargs["theme"] = gr.themes.Soft()
    with gr.Blocks(**blocks_kwargs) as demo:
        gr.Markdown(
            "# Cube 3D - Roblox\n"
            "Text-to-shape generation with [Roblox/cube](https://github.com/Roblox/cube). "
            "Running on **" + device_label(device) + "**."
        )
        with gr.Row():
            with gr.Column(scale=1):
                prompt = gr.Textbox(label="Prompt", placeholder="A tall pagoda", lines=2)
                run_btn = gr.Button("Generate 3D shape", variant="primary")
                with gr.Accordion("Settings", open=False):
                    fast = gr.Checkbox(
                        label="Fast inference (CUDA graphs, needs ~24 GB VRAM)",
                        value=device.type == "cuda",
                        interactive=device.type == "cuda",
                    )
                    resolution_base = gr.Slider(
                        4.0, 9.0, value=8.0, step=0.5,
                        label="Resolution base (higher = finer, slower)",
                    )
                    simplify = gr.Checkbox(
                        label="Simplify mesh (pymeshlab)"
                        + ("" if PYMESHLAB_AVAILABLE else " - unavailable"),
                        value=PYMESHLAB_AVAILABLE,
                        interactive=PYMESHLAB_AVAILABLE,
                    )
                    use_top_p = gr.Checkbox(label="Sample with top-p (adds variety)", value=False)
                    top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="top-p")
                    use_bbox = gr.Checkbox(label="Constrain bounding box (x, y, z)", value=False)
                    with gr.Row():
                        bx = gr.Number(value=1.0, label="x", precision=2)
                        by = gr.Number(value=1.0, label="y", precision=2)
                        bz = gr.Number(value=1.0, label="z", precision=2)
                gr.Examples(
                    examples=[
                        ["A tall pagoda"],
                        ["A pair of headphones"],
                        ["A medieval sword with an ornate hilt"],
                        ["A cartoon bulldozer"],
                        ["A wooden sailing boat"],
                    ],
                    inputs=[prompt],
                )
            with gr.Column(scale=1):
                model_out = gr.Model3D(
                    **supported_kwargs(
                        gr.Model3D.__init__,
                        label="Result",
                        height=460,
                        clear_color=[0.07, 0.07, 0.1, 1.0],
                    )
                )
                files_out = gr.Files(label="Download (.obj / .glb)")
                info_out = gr.Markdown()

        inputs = [prompt, fast, resolution_base, top_p, use_top_p, use_bbox, bx, by, bz, simplify]
        outputs = [model_out, files_out, info_out]
        run_btn.click(generate, inputs=inputs, outputs=outputs)
        prompt.submit(generate, inputs=inputs, outputs=outputs)
    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cube 3D web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    demo = build_ui().queue()
    launch_kwargs = supported_kwargs(
        demo.launch,
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        allowed_paths=[OUTPUT_DIR],
        inbrowser=False,
        show_api=False,
    )
    if LAUNCH_TAKES_THEME:
        launch_kwargs["theme"] = gr.themes.Soft()
    demo.launch(**launch_kwargs)
