import gradio as gr
from config import SERVERS, CSS
from image_utils import show_images
from data_processor import extract, update_model, stop_processing
from translations import get_text, get_headers, TRANSLATIONS


def create_gradio_interface():
    """Create the complete Gradio interface with i18n support"""
    
    with gr.Blocks(title="Business Card Scanner", css=CSS) as demo:
        
        # Language state
        current_lang = gr.State("en")
        
        # Language toggle at the top
        with gr.Row():
            with gr.Column(scale=4):
                pass  # Empty space
            with gr.Column(scale=1):
                lang_toggle = gr.Radio(
                    choices=[("English", "en"), ("繁體中文", "zh-tw")],
                    value="en",
                    label="Language / 語言",
                    container=False
                )
        
        # Main title and description
        title_md = gr.Markdown("# 📇 Business Card Scanner")
        desc_md = gr.Markdown("Extract contact information from business card images")
        
        with gr.Row():
            # Left column - Upload and settings
            with gr.Column(scale=1):
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=list(SERVERS.keys()),
                    value="Gemini 2.0 Flash",
                    label="🎯 Vision Model"
                )
                
                connection_status = gr.Markdown("🟡 Testing connection...")
                
                # Upload section
                uploader = gr.File(
                    file_types=["image"],
                    file_count="multiple",
                    label="📁 Upload Business Cards"
                )
                
                # Settings
                use_raw_images = gr.Checkbox(
                    label="📸 Use Raw Images (Higher Quality)",
                    value=False
                )
                
                custom_filename = gr.Textbox(
                    label="📝 Custom Filename (optional)",
                    placeholder="my_contacts.csv"
                )
                
                # Process buttons
                with gr.Row():
                    start_btn = gr.Button(
                        "🚀 Start Processing",
                        elem_classes=["btn-primary"],
                        scale=2
                    )
                    stop_btn = gr.Button(
                        "⏹️ Stop",
                        elem_classes=["btn-danger"],
                        interactive=False,
                        scale=1
                    )
            
            # Right column - Preview
            with gr.Column(scale=1):
                preview_md = gr.Markdown("### 🖼️ Image Preview")
                image_gallery = gr.Gallery(
                    label="Uploaded Images",
                    columns=3,
                    rows=2,
                    height="400px",
                    object_fit="cover"
                )
        
        # Results section
        results_md = gr.Markdown("### 📊 Results")
        
        processing_time = gr.Markdown(visible=False)
        
        results_df = gr.Dataframe(
            headers=["name", "company", "title", "phone", "email", "address", "handwriting_notes", "other"],
            interactive=True,
            wrap=True,
            label="Extracted Data",
            column_widths=["15%", "15%", "12%", "12%", "15%", "10%", "12%", "9%"]
        )
        
        download_file = gr.File(label="💾 Download CSV")
        
        # Language update function
        def update_language(lang):
            """Update all UI elements with new language"""
            return [
                lang,  # current_lang state
                get_text("title", lang),  # title_md
                get_text("description", lang),  # desc_md
                gr.update(label=get_text("vision_model", lang)),  # model_dropdown
                gr.update(label=get_text("upload_label", lang)),  # uploader
                gr.update(label=get_text("use_raw_images", lang)),  # use_raw_images
                gr.update(
                    label=get_text("custom_filename", lang),
                    placeholder=get_text("filename_placeholder", lang)
                ),  # custom_filename
                gr.update(value=get_text("start_processing", lang)),  # start_btn
                gr.update(value=get_text("stop", lang)),  # stop_btn
                get_text("image_preview", lang),  # preview_md
                gr.update(label=get_text("uploaded_images", lang)),  # image_gallery
                get_text("results", lang),  # results_md
                gr.update(
                    label=get_text("extracted_data", lang),
                    headers=get_headers(lang)
                ),  # results_df
                gr.update(label=get_text("download_csv", lang))  # download_file
            ]
        
        # Event handlers
        uploader.upload(show_images, uploader, image_gallery)
        
        model_dropdown.change(
            update_model,
            inputs=[model_dropdown],
            outputs=[connection_status]
        )
        
        # Language toggle change
        lang_toggle.change(
            update_language,
            inputs=[lang_toggle],
            outputs=[
                current_lang, title_md, desc_md, model_dropdown, uploader,
                use_raw_images, custom_filename, start_btn, stop_btn,
                preview_md, image_gallery, results_md, results_df, download_file
            ]
        )
        
        def start_processing_wrapper(files, custom_filename, use_raw_images, vision_model):
            return extract(files, custom_filename, use_raw_images, vision_model)
        
        def enable_stop_disable_start():
            return gr.update(interactive=False), gr.update(interactive=True)
        
        start_btn.click(
            enable_stop_disable_start,
            outputs=[start_btn, stop_btn]
        ).then(
            start_processing_wrapper,
            inputs=[uploader, custom_filename, use_raw_images, model_dropdown],
            outputs=[results_df, download_file, start_btn, stop_btn, processing_time]
        )
        
        stop_btn.click(
            stop_processing,
            outputs=[stop_btn, start_btn]
        )
        
        # Initialize connection status on load
        def initialize_connection():
            return update_model("Gemini 2.0 Flash")
        
        demo.load(
            initialize_connection,
            outputs=[connection_status]
        )
    
    return demo 