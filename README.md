# **Convert-to-Onnx-Hf-Dir**
Convert a Hugging Face model to ONNX &amp; Upload Directly to Your Hf Model Repo

https://github.com/user-attachments/assets/346816ac-af39-40f1-8c33-ce7196ce2c30

Convert a Hugging Face model to ONNX format and directly upload the converted files to your Hugging Face model repository. This tool leverages [Streamlit](https://streamlit.io/) for a web-based UI and the [Hugging Face Hub](https://huggingface.co/) API for authentication and file uploads.

## Overview

This application automates the following steps:
- **Repository Setup:** Downloads and extracts the Transformers.js repository from a specific version tag or branch.
- **Model Conversion:** Converts the specified Hugging Face model to ONNX format using a conversion script.
- **Model Upload:** Moves the generated ONNX files to an `onnx/` subfolder and uploads them to your Hugging Face model repository.

## Features

- **Streamlit UI:** Provides an easy-to-use web interface for inputting model details and tokens.
- **Flexible Configuration:** Uses environment variables and Streamlit secrets for configuration.
- **Repository Management:** Automatically handles repository download and extraction.
- **Error Handling:** Detailed logging and error messages for troubleshooting.

## Requirements

- Python 3.7+
- [Streamlit](https://streamlit.io/) 
- [Hugging Face Hub](https://github.com/huggingface/huggingface_hub)
- Other dependencies listed in `requirements.txt`

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/PRITHIVSAKTHIUR/Convert-to-Onnx-Hf-Dir.git
   cd Convert-to-Onnx-Hf-Dir
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The application requires a Hugging Face token for authentication. You can provide this token via environment variables or Streamlit secrets.

- **Environment Variables:**
  - `HF_TOKEN`: Your Hugging Face API token.
  - `SPACE_AUTHOR_NAME` (optional): Your Hugging Face username if not provided via token.
  
- **Streamlit Secrets:**
  - Create a file named `.streamlit/secrets.toml` with the following content:

    ```toml
    HF_TOKEN = "your_hf_api_token_here"
    ```

- **User Token Input:**
  - When running the application, you can also input your Hugging Face write token through the UI.

## Usage

1. **Run the Streamlit app:**

   ```bash
   streamlit run app.py
   ```

2. **Using the UI:**
   - Enter the Hugging Face model ID you wish to convert (e.g., `prithivMLmods/FastThink-0.5B-Tiny`).
   - Optionally provide your Hugging Face write token if you wish to upload the model under your account.
   - Click on the "Proceed" button.
   - The application will:
     - Convert the model to ONNX format.
     - Upload the ONNX files to the `onnx/` folder in your Hugging Face model repository.
   - A link will be provided to view your model on Hugging Face after a successful upload.

## Code Structure

- **`app.py`**: Main application file that sets up the UI and orchestrates the conversion and upload process.
- **`Config` class**: Manages configuration and secrets.
- **`ModelConverter` class**: Contains methods for repository setup, model conversion, and upload.

## Troubleshooting

- **Conversion Errors:** Check the error output provided by the app if conversion fails.
- **Upload Errors:** Ensure your Hugging Face token has write permissions for the target repository.
- **Repository Setup:** The app downloads and extracts the repository only if it does not already exist locally. If you encounter issues, try deleting the local repository folder (`./transformers.js`) and restarting the app.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes and push: `git push origin feature/YourFeature`
4. Open a Pull Request with a clear description of your changes.
