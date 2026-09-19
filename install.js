module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    // 1. Clone the latest version of Roblox Cube
    {
      when: "{{!exists('app')}}",
      method: "shell.run",
      params: {
        message: "git clone https://github.com/Roblox/cube app"
      }
    },
    {
      when: "{{exists('app')}}",
      method: "shell.run",
      params: {
        path: "app",
        message: "git pull"
      }
    },

    // 2. Install cube + its dependencies inside the "env" venv
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install -e ."
        ]
      }
    },

    // 3. pymeshlab (mesh simplification) - optional: never fail the install
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "python -c \"import subprocess,sys; subprocess.call([sys.executable,'-m','pip','install','pymeshlab'])\""
        ]
      }
    },

    // 4. Torch (CUDA / ROCm / MPS / CPU depending on the machine)
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app"
        }
      }
    },

    // 5. Web UI dependencies
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install gradio trimesh \"huggingface_hub[cli]\""
        ]
      }
    },

    // 6. Download the model weights (~ 5 GB) into app/model_weights
    {
      when: "{{!exists('app/model_weights/shape_gpt.safetensors')}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "python ../download_weights.py"
        ]
      }
    },

    // 7. Share the outputs folder with other Pinokio apps
    {
      method: "fs.link",
      params: {
        drive: {
          outputs: "app/outputs"
        }
      }
    },

    {
      method: "notify",
      params: {
        html: "<b>Cube 3D is installed.</b> Click <b>Start</b> to launch the web UI."
      }
    }
  ]
}
