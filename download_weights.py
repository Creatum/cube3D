"""Download Roblox model weights from the Hugging Face Hub.

Run from the app/ folder (Pinokio does this):

    python ../download_weights.py                                  # cube3d-v0.5 -> model_weights/
    python ../download_weights.py --repo Roblox/cubepart \
        --dir cubepart/weights --expect multi_part_dit.safetensors vae.safetensors
"""

import argparse
import os
import sys

DEFAULT_REPO = "Roblox/cube3d-v0.5"
DEFAULT_DIR = "model_weights"
DEFAULT_EXPECT = ["shape_gpt.safetensors", "shape_tokenizer.safetensors"]


def main():
    parser = argparse.ArgumentParser(description="Download Roblox weights from Hugging Face")
    parser.add_argument("--repo", default=os.environ.get("CUBE3D_REPO_ID", DEFAULT_REPO))
    parser.add_argument("--dir", default=DEFAULT_DIR, help="target dir, relative to cwd")
    parser.add_argument("--expect", nargs="*", default=None, help="files that must exist afterwards")
    args = parser.parse_args()

    from huggingface_hub import snapshot_download

    target = os.path.join(os.getcwd(), args.dir)
    expect = args.expect if args.expect is not None else (
        DEFAULT_EXPECT if args.repo == DEFAULT_REPO else []
    )

    os.makedirs(target, exist_ok=True)
    print("Downloading {} -> {}".format(args.repo, target), flush=True)
    snapshot_download(
        repo_id=args.repo,
        local_dir=target,
        allow_patterns=["*.safetensors", "*.json", "*.md"],
        max_workers=4,
    )

    for name in expect:
        path = os.path.join(target, name)
        if not os.path.exists(path):
            print("ERROR: missing " + path, file=sys.stderr)
            return 1
        print("OK {} ({:.2f} GB)".format(name, os.path.getsize(path) / 1e9))
    print("Weights ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
