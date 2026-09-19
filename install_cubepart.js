// Optional module: CubePart (open-vocabulary part-controllable 3D generation)
// Installs into the SAME venv as cube3d, without touching the torch build.
module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    {
      method: "notify",
      params: {
        html: "<b>Installing CubePart</b><br>Downloads ~10 GB of weights (multi_part_dit 8.6 GB + vae 1.3 GB). A 24 GB+ GPU is recommended."
      }
    },

    // 1. cube_part package, without deps so the CUDA torch build stays untouched
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/cubepart",
        message: [
          "uv pip install -e . --no-deps"
        ]
      }
    },

    // 2. the deps cube3d does not already provide (torch/torchvision left alone)
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/cubepart",
        message: [
          "uv pip install \"diffusers>=0.30\" \"transformers>=4.45\" \"accelerate>=0.30\" \"safetensors>=0.4\" \"omegaconf>=2.3\" \"scikit-image>=0.22\" \"trimesh>=4.0\" \"pillow>=10.0\" \"einops>=0.7\" \"warp-lang>=1.4\" \"jaxtyping>=0.2\" \"typeguard>=4.0\" \"fpsample>=0.3\" gradio"
        ]
      }
    },

    // 3. weights -> app/cubepart/weights
    {
      when: "{{!exists('app/cubepart/weights/multi_part_dit.safetensors')}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "python ../download_weights.py --repo Roblox/cubepart --dir cubepart/weights --expect multi_part_dit.safetensors vae.safetensors"
        ]
      }
    },

    {
      method: "notify",
      params: {
        html: "<b>CubePart is installed.</b> Use <b>Start CubePart</b> in the menu."
      }
    }
  ]
}
