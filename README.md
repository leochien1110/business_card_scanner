# Business Card Scanner

A simple and clean business card scanner that extracts contact information from images using AI vision models.

## Features

- Extract contact information from business card images
- **NEW**: Handwriting notes detection and extraction
- **NEW**: Post-processing with Gemini 2.5 Flash Preview for data standardization
- Support for multiple languages (English, Chinese, Japanese, Korean, etc.)
- Multiple AI model support (Local Ollama, Remote Ollama, Gemini)
- Phone number formatting standardization
- Email format validation and cleaning
- Simple web interface with Gradio
- CSV export functionality

## Installation

1. Clone the repository
1. (Optional) Create and enter the virtual environment:
   ```bash
   python -m venv venv
   source .venv/bin/activate
   ```
   This is highly recommended to avoid conflicts with other Python packages.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

1. Set up your AI models:
   - For local Ollama: Install Ollama and pull `qwen2.5vl:7b` model
   - For remote Ollama: Configure the remote server URL
   - For Gemini: Set your API key in `.env` file

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Open your browser to `http://localhost:7860`

3. Select your preferred AI model

4. Upload business card images

5. Click "Start Processing" to extract information

6. Download the results as CSV

## Data Fields Extracted

The application extracts the following information:
- **Name**: Person's full name
- **Company**: Company/organization name
- **Title**: Job title/position
- **Phone**: Phone number (automatically formatted)
- **Email**: Email address (automatically validated)
- **Address**: Physical address
- **Handwriting Notes**: Any handwritten annotations or notes
- **Other**: Additional information (websites, social media, etc.)

## Post-Processing

After all business cards are extracted, the entire batch undergoes automatic post-processing using Gemini 2.5 Flash Preview 05-20 to:
- Standardize phone number formats across all cards
- Validate and clean email addresses
- Ensure proper capitalization of names and titles
- Apply consistent address formatting
- Preserve handwriting notes as extracted
- Maintain data consistency across the entire batch

## Configuration

Edit `config.py` to:
- Add more AI models
- Adjust image processing settings
- Modify the extraction prompt

## File Structure

- `app.py` - Main application entry point
- `config.py` - Configuration settings
- `api_client.py` - AI API communication
- `data_processor.py` - Data extraction logic
- `image_utils.py` - Image processing utilities
- `ui_components.py` - User interface components

## Requirements

- Python 3.7+
- Gradio 4.25+
- PIL (Pillow)
- Pandas
- Requests

## License

MIT License 