#!/usr/bin/env python3
"""
Business Card Scanner - Multi-Language Support
Main application entry point for the Gradio web interface.
"""

from ui_components import create_gradio_interface


def main():
    """Main application entry point"""
    print("🚀 Starting Business Card Scanner...")
    print("📇 Multi-language support: English, 中文, 日本語, 한국어, etc.")
    
    # Create and launch the Gradio interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        pwa=True,
        app_kwargs={
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        }
    )


if __name__ == "__main__":
    main() 