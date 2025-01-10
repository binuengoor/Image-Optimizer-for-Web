# Image Optimizer for Web (WebP)

A Python tool that converts images to WebP format with optimized compression settings for web use. WebP offers superior compression while maintaining high image quality, making it ideal for websites and web applications.

## Features

- Converts common image formats (PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP) to Optimized WebP
- Three optimization levels:
  1. Balanced Mode (80% quality) - Recommended for most uses
  2. High Quality (90% quality) - For quality-critical images
  3. Maximum Compression (60% quality) - For smallest file size
- Preserves transparency in PNG images
- Batch processing of multiple images
- Simple command-line interface

## Requirements

- Python 3.6 or higher
- Pillow library

## Installation

1. Clone or download this repository
2. Install dependencies:
```
pip install -r requirements.txt
```


## Directory Structure
```
Image-Optimizer-for-Web/
├── input/
├── output/
├── script.py
├── requirements.txt
├── Readme.md
└── LICENSE
```


## Usage

1. Place your images in the `input` folder
2. Run the script:
```python webp_optimizer.py```
text
3. Select your desired compression mode (1-3)
4. Find your converted images in the `output` folder

## Compression Modes

| Mode | Quality | Use Case |
|------|---------|----------|
| 1 | 80% | Best balance between quality and file size |
| 2 | 90% | High-quality images where size is less critical |
| 3 | 60% | Maximum compression for significant size reduction |

## Supported Input Formats

- PNG
- JPG/JPEG
- TIFF
- BMP

## License

This project is licensed under the MIT License - see the LICENSE file for details.