# Business Card Scanner

A simple and clean business card scanner that extracts contact information from images using AI vision models.

## Features

- **🚀 Default Model**: Gemini 2.0 Flash - Fast and accurate extraction
- Extract contact information from business card images
- **NEW**: Handwriting notes detection and extraction
- **NEW**: Post-processing with Gemini 2.5 Flash Preview for data standardization
- Support for multiple languages (English, Chinese, Japanese, Korean, etc.)
- Multiple AI model support (Local Ollama, Remote Ollama, Gemini)
- Phone number formatting standardization
- Email format validation and cleaning
- **🐳 Docker Service**: One-command deployment with auto-startup
- Simple web interface with Gradio
- CSV export functionality

## Installation

### Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd business_card_scanner
   ```

2. Set up your API key:
   ```bash
   cp env.example .env
   nano .env  # Add your GEMINI_API_KEY
   ```

3. Deploy as a system service:
   ```bash
   sudo ./install-service.sh
   sudo systemctl start business-card-scanner
   ```

4. Access the application at `http://localhost:7860`

### Manual Installation

1. Clone the repository
2. (Optional) Create and enter the virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   This is highly recommended to avoid conflicts with other Python packages.

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your AI models:
   - **For Gemini (Default)**: Set your API key in `.env` file: `GEMINI_API_KEY=YOUR_GEMINI_API_KEY`
   - For local Ollama: Install Ollama and pull `qwen2.5vl:7b` model
   - For remote Ollama: Configure the remote server URL

## Usage

### Service Mode (Production)
The application runs automatically as a system service:
- **Access**: http://localhost:7860
- **Manage**: `sudo systemctl start/stop/restart business-card-scanner`
- **Logs**: `sudo journalctl -u business-card-scanner -f`
- **Auto-start**: Enabled at boot time

### Manual Mode (Development)
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

## Docker Deployment

### System Service (Recommended)
Deploy as a Docker-based system service that starts automatically at boot:

```bash
# Build and install the service
sudo ./install-service.sh

# Manage the service
sudo systemctl start business-card-scanner
sudo systemctl stop business-card-scanner
sudo systemctl restart business-card-scanner
sudo systemctl status business-card-scanner

# View logs
sudo journalctl -u business-card-scanner -f
```

### Manual Docker Deployment
For development or one-time deployments:

```bash
# Build and start
./deploy.sh

# View status
docker ps
docker logs business-card-scanner

# Stop
docker compose down
```

## Security & API Keys

**Important**: Your API keys are protected from accidental git commits:

1. **API keys are stored in `.env`** - this file is git-ignored
2. **Use `env.example` as template** - copy and modify with your keys
3. **Never commit `.env` file** - it contains sensitive information

```bash
# Correct way to set up API keys
cp env.example .env
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

## Configuration

Edit `config.py` to:
- Add more AI models
- Adjust image processing settings
- Modify the extraction prompt
- Change default model selection

## File Structure

- `app.py` - Main application entry point
- `config.py` - Configuration settings
- `api_client.py` - AI API communication
- `data_processor.py` - Data extraction logic
- `image_utils.py` - Image processing utilities
- `ui_components.py` - User interface components

## Requirements

### For Docker Deployment (Recommended)
- Docker and Docker Compose
- Linux system with systemd (for service mode)
- Internet connection for image building

### For Manual Installation
- Python 3.7+
- Gradio 4.25+
- PIL (Pillow)
- Pandas
- Requests

### AI Models
- **Gemini API Key** (Default) - Get from Google AI Studio
- Ollama (Optional) - For local/remote inference

### TODO
- [ ] Be able to run with docker compose - currently can be built from docker image but not run with docker compose
- [ ] Add more languages
- [ ] Add more models
- [ ] Add more features
- [ ] Add more tests
- [ ] Add more documentation
- [ ] Add more examples

## License

MIT License 