"""
Deploy the app to Hugging Face Spaces.
Uses the Hugging Face Hub API to create the Space, upload files, and set secrets.
"""
import os
from pathlib import Path

from huggingface_hub import HfApi, create_repo, upload_folder

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HF_TOKEN = os.environ.get("HF_TOKEN", "")
SPACE_NAME = "sunbird-ai-genapp"
REPO_ID = f"sneakypete01/{SPACE_NAME}"
LOCAL_DIR = Path(__file__).parent.resolve()

# Files to exclude from upload
EXCLUDE = [".git", "__pycache__", ".pytest_cache", "venv", ".env", ".gitignore"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _filter_paths(paths):
    return [p for p in paths if not any(part in EXCLUDE for part in Path(p).parts)]


def deploy():
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable is not set.")

    api = HfApi(token=HF_TOKEN)

    # 1. Create or verify the Space
    print(f"Creating / verifying Space: {REPO_ID}")
    try:
        create_repo(
            repo_id=REPO_ID,
            repo_type="space",
            space_sdk="gradio",
            private=False,
            token=HF_TOKEN,
            exist_ok=True,
        )
        print("Space created or already exists.")
    except Exception as exc:
        print(f"Space creation warning: {exc}")

    # 2. Upload files
    print(f"Uploading files from {LOCAL_DIR} ...")
    upload_folder(
        repo_id=REPO_ID,
        repo_type="space",
        folder_path=str(LOCAL_DIR),
        path_in_repo="",
        token=HF_TOKEN,
        ignore_patterns=[
            ".git/*",
            "__pycache__/*",
            ".pytest_cache/*",
            "venv/*",
            ".env",
            ".gitignore",
            "*.pyc",
        ],
    )
    print("Upload complete.")

    # 3. Set secrets
    sunbird_token = os.environ.get("SUNBIRD_API_TOKEN", "")
    if sunbird_token:
        print("Setting SUNBIRD_API_TOKEN secret...")
        api.add_space_secret(
            repo_id=REPO_ID,
            key="SUNBIRD_API_TOKEN",
            value=sunbird_token,
            token=HF_TOKEN,
        )
        print("Secret set.")
    else:
        print("WARNING: SUNBIRD_API_TOKEN not set locally — you must add it manually in Space Settings.")

    print(f"\nDone! Your Space is available at:")
    print(f"https://huggingface.co/spaces/{REPO_ID}")


if __name__ == "__main__":
    deploy()
