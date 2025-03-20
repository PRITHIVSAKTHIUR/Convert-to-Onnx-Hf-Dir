import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlopen, urlretrieve

import streamlit as st
from huggingface_hub import HfApi, whoami

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration."""

    hf_token: str
    hf_username: str
    transformers_version: str = "3.0.0"
    hf_base_url: str = "https://huggingface.co"
    transformers_base_url: str = (
        "https://github.com/xenova/transformers.js/archive/refs"
    )
    repo_path: Path = Path("./transformers.js")

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables and secrets."""
        system_token = st.secrets.get("HF_TOKEN")
        user_token = st.session_state.get("user_hf_token")
        if user_token:
            hf_username = whoami(token=user_token)["name"]
        else:
            hf_username = (
                os.getenv("SPACE_AUTHOR_NAME") or whoami(token=system_token)["name"]
            )
        hf_token = user_token or system_token

        if not hf_token:
            raise ValueError("HF_TOKEN must be set")

        return cls(hf_token=hf_token, hf_username=hf_username)


class ModelConverter:
    """Handles model conversion and upload operations."""

    def __init__(self, config: Config):
        self.config = config
        self.api = HfApi(token=config.hf_token)

    def _get_ref_type(self) -> str:
        """Determine the reference type for the transformers repository."""
        url = f"{self.config.transformers_base_url}/tags/{self.config.transformers_version}.tar.gz"
        try:
            return "tags" if urlopen(url).getcode() == 200 else "heads"
        except Exception as e:
            logger.warning(f"Failed to check tags, defaulting to heads: {e}")
            return "heads"

    def setup_repository(self) -> None:
        """Download and setup transformers repository if needed."""
        if self.config.repo_path.exists():
            return

        ref_type = self._get_ref_type()
        archive_url = f"{self.config.transformers_base_url}/{ref_type}/{self.config.transformers_version}.tar.gz"
        archive_path = Path(f"./transformers_{self.config.transformers_version}.tar.gz")

        try:
            urlretrieve(archive_url, archive_path)
            self._extract_archive(archive_path)
            logger.info("Repository downloaded and extracted successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to setup repository: {e}")
        finally:
            archive_path.unlink(missing_ok=True)

    def _extract_archive(self, archive_path: Path) -> None:
        """Extract the downloaded archive."""
        import tarfile
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(tmp_dir)

            extracted_folder = next(Path(tmp_dir).iterdir())
            extracted_folder.rename(self.config.repo_path)

    def convert_model(self, input_model_id: str) -> Tuple[bool, Optional[str]]:
        """Convert the model to ONNX format."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "scripts.convert",
                    "--quantize",
                    "--model_id",
                    input_model_id,
                ],
                cwd=self.config.repo_path,
                capture_output=True,
                text=True,
                env={},
            )

            if result.returncode != 0:
                return False, result.stderr

            return True, result.stderr

        except Exception as e:
            return False, str(e)

    def upload_model(self, input_model_id: str) -> Optional[str]:
        """Upload the converted model to the `onnx/` subfolder in the existing model repository."""
        try:
            model_folder_path = self.config.repo_path / "models" / input_model_id
            onnx_folder_path = model_folder_path / "onnx"

            # Create the `onnx` subfolder if it doesn't exist
            onnx_folder_path.mkdir(exist_ok=True)

            # Move the ONNX files to the `onnx` subfolder
            for file in model_folder_path.iterdir():
                if file.is_file() and file.suffix == ".onnx":
                    file.rename(onnx_folder_path / file.name)

            # Upload the `onnx` subfolder to the existing repository
            self.api.upload_folder(
                folder_path=str(onnx_folder_path),
                repo_id=input_model_id,
                path_in_repo="onnx",
            )
            return None
        except Exception as e:
            return str(e)
        finally:
            import shutil

            shutil.rmtree(model_folder_path, ignore_errors=True)


def main():
    """Main application entry point."""
    st.write("## Convert a Hugging Face model to ONNX & Upload Directly to Your Hf Model Repo")

    try:
        config = Config.from_env()
        converter = ModelConverter(config)
        converter.setup_repository()

        input_model_id = st.text_input(
            "Enter the Hugging Face model ID to convert, onnx write to repo.  Example: `prithivMLmods/FastThink-0.5B-Tiny`"
        )

        if not input_model_id:
            return

        st.text_input(
            f"[ 🪪 mandatory ]: Your Hugging Face write token. Fill it if you want to upload the model under your account. `[model_name]/onnx/..`",
            type="password",
            key="user_hf_token",
        )

        output_model_url = f"{config.hf_base_url}/{input_model_id}"

        if not st.button(label="Proceed", type="primary"):
            return

        with st.spinner("Converting model..."):
            success, stderr = converter.convert_model(input_model_id)
            if not success:
                st.error(f"Conversion failed: {stderr}")
                return

            st.success("Conversion successful!")
            st.code(stderr)

        with st.spinner("Uploading model..."):
            error = converter.upload_model(input_model_id)
            if error:
                st.error(f"Upload failed: {error}")
                return

            st.success("Upload successful!")
            st.write("You can now go and view the model on Hugging Face!")
            st.link_button(f"Go to {input_model_id}", output_model_url, type="primary")

    except Exception as e:
        logger.exception("Application error")
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
