import gradio as gr
from config import SERVERS, CSS
from image_utils import show_images
from data_processor import extract, update_model, stop_processing


def create_gradio_interface():
    """Create the complete Gradio interface"""
    with gr.Blocks(title="Business Card Scanner", css=CSS) as demo:
        gr.Markdown("# 📇 Business Card Scanner")
        gr.Markdown("Extract contact information from business card images")
        
        with gr.Row():
            # Left column - Upload and settings
            with gr.Column(scale=1):
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=list(SERVERS.keys()),
                    value="Remote Ollama",
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
                gr.Markdown("### 🖼️ Image Preview")
                image_gallery = gr.Gallery(
                    label="Uploaded Images",
                    columns=3,
                    rows=2,
                    height="400px",
                    object_fit="cover"
                )
        
        # Results section
        gr.Markdown("### 📊 Results")
        
        processing_time = gr.Markdown(visible=False)
        
        results_df = gr.Dataframe(
            headers=["name", "company", "title", "phone", "email", "address", "handwriting_notes", "other"],
            interactive=True,
            wrap=True,
            label="Extracted Data",
            column_widths=["15%", "15%", "12%", "12%", "15%", "10%", "12%", "9%"]
        )
        
        download_file = gr.File(label="💾 Download CSV")
        
        # Event handlers
        uploader.upload(show_images, uploader, image_gallery)
        
        model_dropdown.change(
            update_model,
            inputs=[model_dropdown],
            outputs=[connection_status]
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
        
        # Initialize connection status
        def initialize_connection():
            return update_model("Remote Ollama")
        
        demo.load(
            initialize_connection,
            outputs=[connection_status]
        )
    
    return demo 