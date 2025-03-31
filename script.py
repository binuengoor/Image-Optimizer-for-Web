#!/usr/bin/env python3
"""
WebP Optimizer
A tool to convert images to WebP format with optimized compression settings
Now supports max dimension resizing while retaining aspect ratio.
Author: Your Name
Version: 1.3
"""

import os
import logging
from PIL import Image
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import io
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('webp_optimizer')

# Define global variables before use
clear_input_folder_on_startup = True  # Set to False if you don't want to clear input on startup

# Configuration class for WebP Optimizer
class WebPConfig:
    """Configuration settings for WebP conversion."""
    COMPRESSION_MODES = {
        1: {"quality": 80, "method": 6, "lossless": False, "description": "Balanced"},
        2: {"quality": 90, "method": 6, "lossless": True, "description": "High Quality"},
        3: {"quality": 60, "method": 6, "lossless": False, "description": "Maximum Compression"}
    }
    
    SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')
    MIN_DIMENSION = 100
    DEFAULT_DIMENSION = 2000
    DEFAULT_MODE = 1
    THUMBNAIL_SIZE = 100  # Size for thumbnails (square)
    PORT = int(os.environ.get('PORT', 3756))
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')


# File handling class to centralize file operations
class FileHandler:
    """Centralized file operations for WebP Optimizer"""
    
    @staticmethod
    def create_thumbnail_b64(file_path):
        """Create a base64 encoded thumbnail for an image"""
        try:
            with Image.open(file_path) as img:
                # Create a thumbnail, preserving aspect ratio
                img.thumbnail((WebPConfig.THUMBNAIL_SIZE, WebPConfig.THUMBNAIL_SIZE))
                
                # Convert to RGB if necessary (for transparent images)
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                    img = background
                
                # Save thumbnail to memory buffer
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=70)
                buffer.seek(0)
                
                # Convert to base64
                img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
        except Exception as e:
            logger.error(f"Error creating thumbnail for {file_path}: {str(e)}")
            return None

    @staticmethod
    def get_files_with_sizes(directory):
        """Get all files in a directory with their sizes and thumbnails."""
        files = []
        try:
            for file in os.listdir(directory):
                # Skip .gitkeep files
                if file == '.gitkeep':
                    continue
                    
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    file_data = {"name": file, "size": file_size}
                    
                    # Generate thumbnail for supported image formats
                    if file.lower().endswith(WebPConfig.SUPPORTED_FORMATS):
                        thumbnail = FileHandler.create_thumbnail_b64(file_path)
                        if thumbnail:
                            file_data["thumbnail"] = thumbnail
                            
                    files.append(file_data)
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            return []

    @staticmethod
    def clear_directory(directory, dir_type="directory"):
        """Clear all files from a directory."""
        try:
            count = 0
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and file != '.gitkeep':
                    os.remove(file_path)
                    count += 1
            if count > 0:
                logger.info(f"✅ {dir_type.capitalize()} cleared successfully. ({count} files removed)")
            return count
        except Exception as e:
            logger.error(f"❌ Error clearing {dir_type}: {str(e)}")
            return 0
            
    @staticmethod
    def validate_file_operation(filename, directory, check_exists=True):
        """Validate a file operation with common checks."""
        if not filename or filename.strip() == '':
            return False, "Invalid filename"
            
        file_path = os.path.join(directory, filename)
        
        if check_exists and not os.path.exists(file_path):
            return False, f"File {filename} not found"
            
        return True, file_path


class ImageProcessor:
    """Image processing operations for WebP conversion"""
    
    @staticmethod
    def resize_image(image, max_dim):
        """Resize image while maintaining aspect ratio if it exceeds max_dim."""
        width, height = image.size

        if max(width, height) > max_dim:
            scale = max_dim / max(width, height)
            new_size = (int(width * scale), int(height * scale))
            return image.resize(new_size, Image.LANCZOS)
        
        return image  # Return original image if no resizing is needed

    @staticmethod
    def convert_to_webp(input_path, output_path, compression_mode, max_dim):
        """Convert image to WebP with resizing & compression settings."""
        try:
            logger.info(f"Converting {input_path} to {output_path}")
            image = Image.open(input_path)
            image = ImageProcessor.resize_image(image, max_dim)  # Resize if needed

            # Get compression settings
            config = WebPConfig.COMPRESSION_MODES.get(compression_mode, WebPConfig.COMPRESSION_MODES[WebPConfig.DEFAULT_MODE])
            quality = config["quality"]
            method = config["method"]
            lossless = config["lossless"]
            
            # Handle based on image mode
            save_params = {"quality": quality, "method": method}
            
            if image.mode in ('RGBA', 'LA'):
                # Handle images with transparency
                save_params["lossless"] = lossless
            else:
                # Convert to RGB for non-transparent images
                image = image.convert('RGB')
                
            image.save(output_path, 'WEBP', **save_params)
            return True
        except Exception as e:
            logger.error(f"Error converting {input_path}: {str(e)}")
            return False

    @staticmethod
    def process_images(input_dir, output_dir, compression_mode, max_dim):
        """Process all images in input directory and convert to WebP."""
        conversion_count = 0

        logger.info(f"Looking for files in: {input_dir}")
        files_in_input = os.listdir(input_dir)
        logger.info(f"Files found: {len(files_in_input)}")

        for filename in files_in_input:
            if filename == '.gitkeep':
                continue
                
            if filename.lower().endswith(WebPConfig.SUPPORTED_FORMATS):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.webp")
                logger.info(f"Processing {filename}...")
                if ImageProcessor.convert_to_webp(input_path, output_path, compression_mode, max_dim):
                    conversion_count += 1
                    logger.info(f"✅ Converted: {filename}")

        return conversion_count


app = Flask(__name__)

# Use absolute paths to ensure files are saved in the correct location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'input')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'output')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16 MB limit

# Make sure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


# Flask routes
@app.route('/')
def index():
    # Clear input folder on startup if configured
    global clear_input_folder_on_startup
    if clear_input_folder_on_startup:
        FileHandler.clear_directory(app.config['UPLOAD_FOLDER'], "input folder")
        clear_input_folder_on_startup = False
    
    return render_template('index.html')


@app.route('/list_output')
def list_output():
    """Return a list of files in the output directory with their sizes."""
    try:
        output_files = FileHandler.get_files_with_sizes(app.config['OUTPUT_FOLDER'])
        return jsonify({"success": True, "files": output_files})
    except Exception as e:
        logger.error(f"Error in list_output: {str(e)}")
        return jsonify({"success": False, "message": str(e), "files": []})


@app.route('/list_input')
def list_input():
    """Return a list of files in the input directory with their sizes."""
    try:
        input_files = FileHandler.get_files_with_sizes(app.config['UPLOAD_FOLDER'])
        return jsonify({"success": True, "files": input_files})
    except Exception as e:
        logger.error(f"Error in list_input: {str(e)}")
        return jsonify({"success": False, "message": str(e), "files": []})


@app.route('/clear_output', methods=['POST'])
def clear_output():
    """Clear all files from the output directory."""
    try:
        count = FileHandler.clear_directory(app.config['OUTPUT_FOLDER'], "output folder")
        return jsonify({"success": True, "message": f"Output folder cleared successfully. {count} files removed."})
    except Exception as e:
        logger.error(f"Error clearing output folder: {str(e)}")
        return jsonify({"success": False, "message": f"Error clearing output folder: {str(e)}"})


@app.route('/clear_input', methods=['POST'])
def clear_input():
    """Clear all files from the input directory."""
    try:
        count = FileHandler.clear_directory(app.config['UPLOAD_FOLDER'], "input folder")
        return jsonify({"success": True, "message": f"Input folder cleared successfully. {count} files removed."})
    except Exception as e:
        logger.error(f"Error clearing input folder: {str(e)}")
        return jsonify({"success": False, "message": f"Error clearing input folder: {str(e)}"})


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads to the input folder."""
    try:
        if 'files[]' not in request.files:
            logger.warning("No files part in the request")
            return jsonify({"success": False, "message": "No files part in the request"})

        files = request.files.getlist('files[]')
        logger.info(f"Received {len(files)} files: {[file.filename for file in files]}")
        
        file_count = 0
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                file_count += 1
                logger.info(f"Saved file: {filename}")

        if file_count > 0:
            input_files = FileHandler.get_files_with_sizes(app.config['UPLOAD_FOLDER'])
            return jsonify({
                "success": True, 
                "message": f"{file_count} files uploaded successfully!",
                "input_files": input_files
            })
        else:
            return jsonify({"success": False, "message": "No valid files uploaded"})
    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}")
        return jsonify({"success": False, "message": f"Upload error: {str(e)}"})


@app.route('/convert', methods=['POST'])
def convert():
    """Convert images in the input folder to WebP format."""
    try:
        # Get parameters from the form
        compression_mode = int(request.form.get('compression_mode', WebPConfig.DEFAULT_MODE))
        max_dim = int(request.form.get('max_dim', WebPConfig.DEFAULT_DIMENSION))
        
        # Validate parameters
        if max_dim < WebPConfig.MIN_DIMENSION:
            max_dim = WebPConfig.MIN_DIMENSION
            
        if compression_mode not in WebPConfig.COMPRESSION_MODES:
            compression_mode = WebPConfig.DEFAULT_MODE

        # Process images
        conversion_count = ImageProcessor.process_images(
            app.config['UPLOAD_FOLDER'],
            app.config['OUTPUT_FOLDER'],
            compression_mode,
            max_dim
        )

        if conversion_count > 0:
            output_files = FileHandler.get_files_with_sizes(app.config['OUTPUT_FOLDER'])
            return jsonify({
                "success": True, 
                "message": f"Conversion complete! {conversion_count} images converted.",
                "output_files": output_files
            })
        else:
            return jsonify({
                "success": False,
                "message": "No files were converted. Please upload images first."
            })
    except Exception as e:
        logger.error(f"Error in convert: {str(e)}")
        return jsonify({"success": False, "message": f"Conversion error: {str(e)}"})


@app.route('/output/<filename>')
def download_file(filename):
    """Serve files from the output directory."""
    try:
        # Use send_from_directory with as_attachment=True to force download
        # But only when the download parameter is present
        as_attachment = 'download' in request.args
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=as_attachment)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({"success": False, "message": f"File not found: {filename}"})


@app.route('/rename_output_file', methods=['POST'])
def rename_output_file():
    """Rename a file in the output directory."""
    try:
        data = request.get_json()
        if not data or 'oldName' not in data or 'newName' not in data:
            return jsonify({"success": False, "message": "Both old and new filenames are required"})
        
        old_name = data['oldName']
        new_name = data['newName']
        
        # Validate old filename
        valid, result = FileHandler.validate_file_operation(old_name, app.config['OUTPUT_FOLDER'])
        if not valid:
            return jsonify({"success": False, "message": result})
            
        old_path = result
        
        # Validate that new filename is secure and ends with .webp
        if not new_name.lower().endswith('.webp'):
            new_name += '.webp'
        
        new_name = secure_filename(new_name)
        
        # Check if new filename is empty after securing
        if not new_name or new_name.strip() == '':
            return jsonify({"success": False, "message": "Invalid new filename"})
        
        new_path = os.path.join(app.config['OUTPUT_FOLDER'], new_name)
            
        # Check if the new filename already exists
        if os.path.exists(new_path) and old_path != new_path:
            return jsonify({"success": False, "message": f"File {new_name} already exists"})
        
        # Rename the file
        os.rename(old_path, new_path)
        
        # Return updated file list
        output_files = FileHandler.get_files_with_sizes(app.config['OUTPUT_FOLDER'])
        return jsonify({
            "success": True, 
            "message": f"File renamed successfully from {old_name} to {new_name}",
            "output_files": output_files
        })
        
    except Exception as e:
        logger.error(f"Error renaming file: {str(e)}")
        return jsonify({"success": False, "message": f"Error renaming file: {str(e)}"})


@app.route('/remove_input_file', methods=['POST'])
def remove_input_file():
    """Remove a file from the input directory."""
    try:
        data = request.get_json()
        if not data or 'fileName' not in data:
            return jsonify({"success": False, "message": "Filename is required"})
        
        file_name = data['fileName']
        
        # Validate filename
        valid, result = FileHandler.validate_file_operation(file_name, app.config['UPLOAD_FOLDER'])
        if not valid:
            return jsonify({"success": False, "message": result})
            
        file_path = result
        
        # Remove the file
        os.remove(file_path)
        
        # Return updated file list
        input_files = FileHandler.get_files_with_sizes(app.config['UPLOAD_FOLDER'])
        return jsonify({
            "success": True, 
            "message": f"File {file_name} removed successfully",
            "input_files": input_files
        })
        
    except Exception as e:
        logger.error(f"Error removing file: {str(e)}")
        return jsonify({"success": False, "message": f"Error removing file: {str(e)}"})


if __name__ == "__main__":
    logger.info(f"Starting WebP Optimizer v1.2 on port {WebPConfig.PORT}")
    app.run(host='0.0.0.0', port=WebPConfig.PORT, debug=WebPConfig.DEBUG)