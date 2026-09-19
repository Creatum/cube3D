module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    {
      method: "shell.run",
      params: {
        message: "git pull"
      }
    },
    {
      method: "shell.run",
      params: {
        path: "app",
        message: "git pull"
      }
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install -e .",
          "uv pip install gradio trimesh \"huggingface_hub[cli]\""
        ]
      }
    },
    {
      when: "{{!exists('app/model_weights/shape_gpt.safetensors')}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "python ../download_weights.py"
      }
    },
    // keep the optional CubePart module in sync when it is installed
    {
      when: "{{exists('app/cubepart/weights/multi_part_dit.safetensors')}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/cubepart",
        message: "uv pip install -e . --no-deps"
      }
    }
  ]
}
