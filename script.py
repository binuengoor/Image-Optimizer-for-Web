#!/usr/bin/env python3
"""
WebP Optimizer
A tool to convert images to WebP format with optimized compression settings
Author: Your Name
Version: 1.0
"""

from PIL import Image
import os
import shutil

def convert_to_webp(input_path, output_path, compression_mode):
    """Convert image to WebP with specified compression settings"""
    try:
        image = Image.open(input_path)
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
    """Clear all files from the input directory"""
    try:
        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Input folder cleared successfully.")
    except Exception as e:
        print(f"Error clearing input folder: {str(e)}")

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup input and output directories
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print("WebP Optimizer v1.0")
    print("\nCompression Options:")
    print("1. Balanced (Recommended: 80% quality, good balance)")
    print("2. High Quality (90% quality, larger file size)")
    print("3. Maximum Compression (60% quality, smallest file size)")
    
    try:
        mode = int(input("\nSelect compression mode (1-3): "))
        if mode not in [1, 2, 3]:
            print("Invalid mode selected. Using default mode 1.")
            mode = 1
    except ValueError:
        print("Invalid input. Using default mode 1.")
        mode = 1
    
    supported_formats = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')
    conversion_count = 0
    
    # Check if input directory is empty
    if not os.listdir(input_dir):
        print(f"\nNo files found! Please place images in the 'input' folder: {input_dir}")
        return
    
    # Process all images in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.webp")
            if convert_to_webp(input_path, output_path, mode):
                conversion_count += 1
                print(f"Converted: {filename}")
    
    if conversion_count == 0:
        print("\nNo compatible images found in the input directory.")
    else:
        print(f"\nConversion complete! {conversion_count} images converted.")
        print(f"Converted images saved in: {output_dir}")
        
        # Ask user if they want to clear the input folder
        while True:
            clear_input = input("\nWould you like to clear the input folder? (y/n): ").lower()
            if clear_input in ['y', 'n']:
                break
            print("Please enter 'y' for yes or 'n' for no.")
        
        if clear_input == 'y':
            clear_input_folder(input_dir)

if __name__ == "__main__":
    main()
