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
    print("🌐 Interface languages: English, 繁體中文")
    print("📱 PWA enabled - Install from browser address bar!")
    
    # Create and launch the Gradio interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        # Enhanced PWA configuration
        pwa=True,
        app_kwargs={
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        },
        # Enable internationalization
        show_api=False,
        # Additional launch parameters for better i18n and PWA support
        inbrowser=False,
        share=False,
        quiet=False  # Show startup messages
    )


if __name__ == "__main__":
    main() 