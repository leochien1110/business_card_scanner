import os
from dotenv import load_dotenv

load_dotenv()

# Image processing settings: 3:2 aspect ratio
MAX_WIDTH = 2160
MAX_HEIGHT = 1440
IMAGE_QUALITY = 90

# Server configurations - simplified to just essential ones
SERVERS = {
    "Local Ollama": {
        "url": "http://127.0.0.1:11434/api/generate",
        "model": "qwen2.5vl:7b",
        "type": "ollama"
    },
    "Remote Ollama": {
        "url": "http://192.168.0.243:11434/api/generate",
        "model": "qwen2.5vl:7b",
        "type": "ollama"
    },
    "Gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-2.0-flash",
        "type": "openai",
        "api_key": os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    }
}

# Post-processing configuration
POST_PROCESSING_CONFIG = {
    "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent",
    "model": "gemini-2.5-flash-preview-05-20",
    "type": "gemini",
    "api_key": os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
}

# Current configuration
current_config = SERVERS["Remote Ollama"]

# Global processing control
processing_stopped = False

# AI Prompts
PROMPT = """
Extract information from this business card and return a JSON object with these fields:
{name, company, title, phone, email, address, handwriting_notes, other}

Rules:
- Extract text exactly as printed on the card
- PRESERVE ALL MULTILINGUAL TEXT: If text exists in multiple languages, format as "English / 中文 / 日本語" etc.
- For handwriting_notes: extract any handwritten text, notes, or annotations (separate from printed text)
- Do not translate or create missing information - keep original multilingual format
- Return only valid JSON, no comments or markdown

Example: {"name": "John Smith / 約翰", "company": "ABC Corp", "title": "Manager", "phone": "+1-555-1234", "email": "john@abc.com", "address": "123 Main St", "handwriting_notes": "Call after 2pm", "other": "www.abc.com"}
"""

POST_PROCESSING_PROMPT = """
You are a data quality expert. Please standardize and validate the following business card data to ensure consistency and proper formatting:

Original data: {data}

Please return a JSON object with the same fields but with standardized formatting:

Rules for standardization:
1. Phone numbers: Format as international standard (e.g., +1-555-123-4567) or local standard if country unclear
2. Email: Ensure proper email format (lowercase domain)
3. Address: Clean and standardize address format (but preserve multilingual text like "123 Main St / 主要街道123号")
4. Name: Proper capitalization, remove extra spaces BUT PRESERVE multilingual format (e.g., "John Smith / 約翰・スミス")
5. Company: Proper business name formatting BUT PRESERVE multilingual format (e.g., "ABC Corp / ABC株式会社")
6. Title: Standardize job titles (e.g., "CEO" not "C.E.O.") BUT PRESERVE multilingual format (e.g., "CEO / 最高経営責任者")
7. Keep handwriting_notes as extracted
8. Other: Clean URLs, social media handles, etc. BUT PRESERVE multilingual text

Return only valid JSON with the same field structure, no comments or markdown.
"""

# Simple CSS
CSS = """
.container { max-width: 1200px; margin: 0 auto; }
.btn-primary { background: #007bff !important; color: white !important; }
.btn-danger { background: #dc3545 !important; color: white !important; }
""" 