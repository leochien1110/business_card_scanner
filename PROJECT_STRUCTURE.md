# Business Card Scanner - Project Structure

## Overview
The Business Card Scanner has been refactored from a single large file (832 lines) into a clean, modular architecture with separate concerns and improved maintainability.

## File Structure

```
businesscard_scanner/
├── app.py                    # Main entry point (20 lines)
├── config.py                 # Configuration and settings (245 lines)
├── image_utils.py           # Image processing utilities (70 lines)
├── api_client.py            # API communication layer (132 lines)
├── data_processor.py        # Data extraction and processing (245 lines)
├── ui_components.py         # Gradio UI components (224 lines)
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── PROJECT_STRUCTURE.md   # This file
```

## Module Descriptions

### 🚀 `app.py` - Main Entry Point
- **Purpose**: Application launcher
- **Size**: 20 lines (was 832 lines)
- **Responsibilities**:
  - Initialize and launch the Gradio interface
  - Main application entry point

### ⚙️ `config.py` - Configuration Management
- **Purpose**: Centralized configuration and settings
- **Size**: 245 lines
- **Responsibilities**:
  - Image processing settings (resolution, quality, raw/resized options)
  - Server configurations (Local Ollama, Remote servers, Gemini API)
  - Model configurations (Vision models, Post-processing models)
  - AI prompts (extraction and post-processing)
  - CSS styles for the UI
  - Global variables and constants

### 🖼️ `image_utils.py` - Image Processing
- **Purpose**: Image handling and processing utilities
- **Size**: 70 lines
- **Responsibilities**:
  - Image resizing with aspect ratio preservation
  - Format detection (JPEG, PNG)
  - Raw image handling
  - Gallery display functions

### 🌐 `api_client.py` - API Communication
- **Purpose**: External API communication layer
- **Size**: 132 lines
- **Responsibilities**:
  - Ollama API communication
  - OpenAI-compatible API communication (Gemini)
  - Connection testing for vision models
  - Connection testing for post-processing models
  - Universal API routing

### 🧠 `data_processor.py` - Data Processing
- **Purpose**: Core business logic for data extraction and processing
- **Size**: 245 lines
- **Responsibilities**:
  - Main extraction workflow
  - Post-processing with validation and standardization
  - Model configuration updates
  - Processing control (start/stop)
  - Settings display management

### 🎨 `ui_components.py` - User Interface
- **Purpose**: Gradio UI components and layout
- **Size**: 224 lines
- **Responsibilities**:
  - Processing options section (models, settings)
  - File upload section
  - Image preview gallery
  - Results display (dataframe, CSV download)
  - Event handlers and interactions
  - Complete interface assembly

## Key Improvements

### 🧹 **Clean Architecture**
- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Modularity**: Easy to modify individual components without affecting others
- **Maintainability**: Much easier to understand, debug, and extend

### 🎯 **Improved User Experience**
- **Reorganized Layout**: Processing options moved to the top for better workflow
- **Automatic Connection Testing**: Models are tested automatically when selected
- **Cleaner Interface**: Removed redundant status displays
- **Modern Styling**: Enhanced CSS with gradients, hover effects, and responsive design

### 🔧 **Better Configuration Management**
- **Centralized Settings**: All configuration in one place
- **Easy Customization**: Simple to modify image processing settings
- **Model Management**: Clear separation of vision and post-processing models

### 📱 **Responsive Design**
- **Mobile-Friendly**: CSS includes responsive breakpoints
- **Modern Styling**: Professional appearance with improved typography
- **Better Visual Hierarchy**: Clear sections and improved spacing

## Configuration Options

### Image Processing
```python
# Quick resolution presets
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = 2560, 1440  # 1440p - very high quality
# MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = 1920, 1080  # 1080p - high quality
# MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = 1280, 720   # 720p - balanced
# MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = 854, 480    # 480p - fastest

USE_RAW_IMAGES = True          # Use original images (maximum quality)
USE_POST_PROCESSING = True     # Enable intelligent validation
IMAGE_QUALITY = 100           # JPEG quality (1-100)
```

### Server Configurations
- **Local Ollama**: Multiple model options (qwen2.5vl, llava, mistral)
- **Remote Servers**: Network-based Ollama instances
- **Cloud APIs**: Gemini 2.0 Flash support
- **Custom**: Environment variable configuration

## Usage

### Development
```bash
python app.py
```

### Adding New Models
1. Add to `SERVER_CONFIGS` in `config.py`
2. Model will automatically appear in the UI dropdown
3. Connection testing is handled automatically

### Customizing Processing
1. Modify settings in `config.py`
2. Adjust prompts for different extraction behavior
3. Add new post-processing models to the list

## Benefits of Modular Structure

1. **Easier Maintenance**: Each file has a clear purpose
2. **Better Testing**: Individual modules can be tested separately
3. **Improved Collaboration**: Multiple developers can work on different modules
4. **Cleaner Code**: No more 800+ line files
5. **Better Documentation**: Each module is self-documenting
6. **Easier Debugging**: Issues are isolated to specific modules
7. **Future Extensions**: Easy to add new features without breaking existing code

## Migration Notes

The refactoring maintains 100% backward compatibility:
- All existing functionality is preserved
- Configuration options remain the same
- API behavior is unchanged
- UI functionality is enhanced, not removed

The new structure makes the codebase much more professional and maintainable while providing a better user experience. 