import io
from PIL import Image
from config import MAX_WIDTH, MAX_HEIGHT, IMAGE_QUALITY


def resize_image(image_path, use_raw=False):
    """Resize image to fit within specified dimensions while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_width, original_height = img.size
            
            if not use_raw:
                # Calculate scaling factor
                width_ratio = MAX_WIDTH / original_width
                height_ratio = MAX_HEIGHT / original_height
                scale_factor = min(width_ratio, height_ratio, 1.0)
                
                # Resize if needed
                if scale_factor < 1.0:
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            return img_byte_arr.getvalue()
            
    except Exception:
        # Fallback: read original file
        with open(image_path, 'rb') as file:
            return file.read()


def detect_image_format(file_path):
    """Detect image format from file extension"""
    file_ext = pathlib.Path(file_path).suffix.lower()
    if file_ext in ['.jpg', '.jpeg']:
        return "image/jpeg"
    elif file_ext == '.png':
        return "image/png"
    else:
        return "image/jpeg"  # default fallback


def show_images(files):
    """Display uploaded images as a gallery"""
    return files if files else None 