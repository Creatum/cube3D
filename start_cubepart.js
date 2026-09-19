// Upstream CubePart Gradio demo (cubepart/examples/gradio_demo.py) on port 7861
module.exports = {
  requires: {
    bundle: "ai"
  },
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/cubepart",
        env: {
          PYTORCH_ENABLE_MPS_FALLBACK: "1",
          TOKENIZERS_PARALLELISM: "false",
          GRADIO_ANALYTICS_ENABLED: "False",
          HF_HUB_DISABLE_TELEMETRY: "1"
        },
        message: [
          "python examples/gradio_demo.py --device {{gpu === 'nvidia' ? 'cuda' : (platform === 'darwin' ? 'mps' : 'cpu')}} --server-name 127.0.0.1 --server-port 7861 --hf-local-dir weights"
        ],
        on: [{
          event: "/(http:\/\/[0-9.:a-zA-Z]+)/",
          done: true
        }]
      }
    },
    {
      method: "local.set",
      params: {
        url: "{{input.event[0]}}"
      }
    }
  ]
}
