#!/usr/bin/env python3
"""
WebP Optimizer
A tool to convert images to WebP format with optimized compression settings
Now supports max dimension resizing while retaining aspect ratio.
Author: Your Name
Version: 1.1
"""

from PIL import Image
import os
import shutil
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename

# Define global variables before use
clear_input_folder_on_startup = True  # Set to False if you don't want to clear input on startup

app = Flask(__name__)

# Use absolute paths to ensure files are saved in the correct location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'input')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Make sure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def resize_image(image, max_dim):
    """Resize image while maintaining aspect ratio if it exceeds max_dim."""
    width, height = image.size

    if max(width, height) > max_dim:
        scale = max_dim / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        return image.resize(new_size, Image.LANCZOS)
    
    return image  # Return original image if no resizing is needed

def convert_to_webp(input_path, output_path, compression_mode, max_dim):
    """Convert image to WebP with resizing & compression settings."""
    try:
        print(f"Converting {input_path} to {output_path}")
        image = Image.open(input_path)
        image = resize_image(image, max_dim)  # Resize if needed

        if image.mode in ('RGBA', 'LA'):
            # Handle images with transparency
            if compression_mode == 1:
                image.save(output_path, 'WEBP', quality=80, method=6, lossless=False)
            elif compression_mode == 2:
                image.save(output_path, 'WEBP', quality=90, method=6, lossless=True)
            elif compression_mode == 3:
                image.save(output_path, 'WEBP', quality=60, method=6, lossless=False)
        else:
            # Convert to RGB for non-transparent images
            image = image.convert('RGB')
            if compression_mode == 1:
                image.save(output_path, 'WEBP', quality=80, method=6)
            elif compression_mode == 2:
                image.save(output_path, 'WEBP', quality=90, method=6)
            elif compression_mode == 3:
                image.save(output_path, 'WEBP', quality=60, method=6)

        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return False

def clear_input_folder(input_dir):
    """Clear all files from the input directory."""
    try:
        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("✅ Input folder cleared successfully.")
    except Exception as e:
        print(f"❌ Error clearing input folder: {str(e)}")

def clear_output_folder(output_dir):
    """Clear all files from the output directory."""
    try:
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("✅ Output folder cleared successfully.")
    except Exception as e:
        print(f"❌ Error clearing output folder: {str(e)}")

@app.route('/')
def index():
    # Clear input folder on startup if configured
    global clear_input_folder_on_startup
    if clear_input_folder_on_startup:
        clear_input_folder(app.config['UPLOAD_FOLDER'])
        clear_input_folder_on_startup = False
    
    # List any files in the input directory to show what's ready for conversion
    input_files = []
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], file)):
            input_files.append(file)
    
    # List any output files ready for download
    output_files = []
    for file in os.listdir(app.config['OUTPUT_FOLDER']):
        if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], file)):
            output_files.append(file)
    
    return render_template('index.html', input_files=input_files, output_files=output_files)

@app.route('/list_output')
def list_output():
    """Return a list of files in the output directory with their sizes."""
    output_files = []
    try:
        for file in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                output_files.append({"name": file, "size": file_size})
        return jsonify({"success": True, "files": output_files})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "files": []})

@app.route('/list_input')
def list_input():
    """Return a list of files in the input directory with their sizes."""
    input_files = []
    try:
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                input_files.append({"name": file, "size": file_size})
        return jsonify({"success": True, "files": input_files})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "files": []})

@app.route('/clear_output', methods=['POST'])
def clear_output():
    """Clear all files from the output directory."""
    try:
        clear_output_folder(app.config['OUTPUT_FOLDER'])
        return jsonify({"success": True, "message": "Output folder cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error clearing output folder: {str(e)}"})

@app.route('/clear_input', methods=['POST'])
def clear_input():
    """Clear all files from the input directory."""
    try:
        clear_input_folder(app.config['UPLOAD_FOLDER'])
        return jsonify({"success": True, "message": "Input folder cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error clearing input folder: {str(e)}"})

@app.route('/upload', methods=['POST'])
def upload_files():
    # Save uploaded files
    if 'files[]' not in request.files:
        print("❌ No files part in the request")  # Debugging log
        return jsonify({"success": False, "message": "No files part in the request"})

    files = request.files.getlist('files[]')
    print(f"📂 Received files: {[file.filename for file in files]}")  # Debugging log
    
    file_count = 0
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"💾 Saving file to: {save_path}")  # Debugging log
            file.save(save_path)
            file_count += 1

    if file_count > 0:
        # Get list of all files in the input folder with their sizes
        input_files = []
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                input_files.append({"name": file, "size": file_size})
                
        return jsonify({
            "success": True, 
            "message": f"{file_count} files uploaded successfully!",
            "input_files": input_files
        })
    else:
        return jsonify({"success": False, "message": "No valid files uploaded"})

@app.route('/convert', methods=['POST'])
def convert():
    # Get parameters from the form
    compression_mode = int(request.form.get('compression_mode', 1))
    max_dim = int(request.form.get('max_dim', 2000))

    # Check if there are files in input directory
    input_files = os.listdir(app.config['UPLOAD_FOLDER'])
    print(f"Files in input directory before conversion: {input_files}")  # Debug

    # Call the main conversion logic
    conversion_count = main_gui(compression_mode, max_dim)

    if conversion_count > 0:
        # Get output files with their sizes
        output_files = []
        for file in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                output_files.append({"name": file, "size": file_size})
                
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

@app.route('/output/<filename>')
def download_file(filename):
    # Use send_from_directory with as_attachment=True to force download
    # But only when the download parameter is present
    as_attachment = 'download' in request.args
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=as_attachment)

def main_gui(compression_mode, max_dim):
    input_dir = app.config['UPLOAD_FOLDER']
    output_dir = app.config['OUTPUT_FOLDER']

    supported_formats = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')
    conversion_count = 0

    print(f"Looking for files in: {input_dir}")
    files_in_input = os.listdir(input_dir)
    print(f"Files found: {files_in_input}")

    for filename in files_in_input:
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.webp")
            print(f"Processing {filename}...")
            if convert_to_webp(input_path, output_path, compression_mode, max_dim):
                conversion_count += 1
                print(f"✅ Converted: {filename}")

    return conversion_count

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup input and output directories
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Ask user if they want to clear the output folder
    while True:
        clear_output = input("\nWould you like to clear the output folder before starting? (y/n): ").lower()
        if clear_output in ['y', 'n']:
            break
        print("⚠ Please enter 'y' for yes or 'n' for no.")

    if clear_output == 'y':
        clear_output_folder(output_dir)

    print("🔹 WebP Optimizer v1.1 🔹")
    print("\nCompression Options:")
    print("1. Balanced (Recommended: 80% quality, good balance)")
    print("2. High Quality (90% quality, larger file size)")
    print("3. Maximum Compression (60% quality, smallest file size)")
    
    try:
        mode = int(input("\nSelect compression mode (1-3): "))
        if mode not in [1, 2, 3]:
            print("⚠ Invalid mode selected. Using default mode 1.")
            mode = 1
    except ValueError:
        print("⚠ Invalid input. Using default mode 1.")
        mode = 1

    try:
        max_dim = int(input("\nEnter max dimension in pixels (e.g., 2000): "))
        if max_dim < 100:  # Prevent unreasonably small sizes
            print("⚠ Minimum allowed size is 100px. Using 100px.")
            max_dim = 100
    except ValueError:
        print("⚠ Invalid input. Using default 2000px.")
        max_dim = 2000
    
    supported_formats = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')
    conversion_count = 0
    
    # Check if input directory is empty
    if not os.listdir(input_dir):
        print(f"\n❌ No files found! Please place images in the 'input' folder: {input_dir}")
        return
    
    # Process all images in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.webp")
            if convert_to_webp(input_path, output_path, mode, max_dim):
                conversion_count += 1
                print(f"✅ Converted: {filename}")
    
    if conversion_count == 0:
        print("\n❌ No compatible images found in the input directory.")
    else:
        print(f"\n✅ Conversion complete! {conversion_count} images converted.")
        print(f"📁 Converted images saved in: {output_dir}")
        
        # Ask user if they want to clear the input folder
        while True:
            clear_input = input("\nWould you like to clear the input folder? (y/n): ").lower()
            if clear_input in ['y', 'n']:
                break
            print("⚠ Please enter 'y' for yes or 'n' for no.")
        
        if clear_input == 'y':
            clear_input_folder(input_dir)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3756, debug=True)