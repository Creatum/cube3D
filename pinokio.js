module.exports = {
  version: "1.0",
  title: "Cube 3D (Roblox)",
  description: "Roblox Cube 3D — text-to-shape generative 3D model (cube3d-v0.5) with a Gradio web UI, plus optional CubePart part decomposition. https://github.com/Roblox/cube",
  icon: "icon.png",
  menu: async (kernel, info) => {
    let installed = info.exists("app/env")
    let cubepart_installed = info.exists("app/cubepart/weights/multi_part_dit.safetensors")
    let running = {
      install: info.running("install.js"),
      start: info.running("start.js"),
      install_cubepart: info.running("install_cubepart.js"),
      start_cubepart: info.running("start_cubepart.js"),
      update: info.running("update.js"),
      reset: info.running("reset.js")
    }

    if (running.install) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Installing",
        href: "install.js"
      }]
    }

    if (!installed) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Install",
        href: "install.js"
      }]
    }

    if (running.install_cubepart) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Installing CubePart",
        href: "install_cubepart.js"
      }]
    }

    // a running Gradio UI takes over the menu
    for (let item of [
      { key: "start", script: "start.js", label: "Cube 3D" },
      { key: "start_cubepart", script: "start_cubepart.js", label: "CubePart" }
    ]) {
      if (running[item.key]) {
        let local = info.local(item.script)
        if (local && local.url) {
          return [{
            default: true,
            icon: "fa-solid fa-rocket",
            text: "Open Web UI (" + item.label + ")",
            href: local.url
          }, {
            icon: "fa-solid fa-terminal",
            text: "Terminal",
            href: item.script
          }]
        }
        return [{
          default: true,
          icon: "fa-solid fa-terminal",
          text: "Terminal",
          href: item.script
        }]
      }
    }

    if (running.update) {
      return [{
        default: true,
        icon: "fa-solid fa-terminal",
        text: "Updating",
        href: "update.js"
      }]
    }

    if (running.reset) {
      return [{
        default: true,
        icon: "fa-solid fa-terminal",
        text: "Resetting",
        href: "reset.js"
      }]
    }

    let cubepart_item = cubepart_installed ? {
      icon: "fa-solid fa-puzzle-piece",
      text: "Start CubePart",
      href: "start_cubepart.js"
    } : {
      icon: "fa-solid fa-puzzle-piece",
      text: "Install CubePart (~10 GB)",
      href: "install_cubepart.js",
      confirm: "CubePart downloads ~10 GB of weights and needs a large GPU (24 GB+ VRAM recommended). Install it now?"
    }

    return [{
      default: true,
      icon: "fa-solid fa-power-off",
      text: "Start",
      href: "start.js"
    }, cubepart_item, {
      icon: "fa-solid fa-folder-open",
      text: "Outputs",
      href: "app/outputs?fs"
    }, {
      icon: "fa-solid fa-rotate",
      text: "Update",
      href: "update.js"
    }, {
      icon: "fa-solid fa-plug",
      text: "Reinstall",
      href: "install.js"
    }, {
      icon: "fa-regular fa-circle-xmark",
      text: "Reset",
      href: "reset.js",
      confirm: "Are you sure you wish to reset the app? (the venv and the app folder will be deleted)"
    }]
  }
}
