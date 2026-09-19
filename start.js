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
        path: "app",
        env: {
          PYTORCH_ENABLE_MPS_FALLBACK: "1",
          TOKENIZERS_PARALLELISM: "false",
          GRADIO_ANALYTICS_ENABLED: "False",
          HF_HUB_DISABLE_TELEMETRY: "1"
        },
        message: [
          "python ../app.py"
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
