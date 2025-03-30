# Image-Optimizer-for-Web

A web-based tool that converts images to WebP format with optimized compression settings for web use. WebP offers superior compression while maintaining high image quality, making it ideal for websites and web applications.

## Features

- Converts common image formats (PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP) to Optimized WebP
- Drag-and-drop interface with batch upload capability
- File size information for both input and output files
- Three optimization levels:
  1. Balanced Mode (80% quality) - Recommended for most uses
  2. High Quality (90% quality) - For quality-critical images
  3. Maximum Compression (60% quality) - For smallest file size
- Preserves transparency in PNG images
- Resizable images with customizable maximum dimensions
- Docker support for easy deployment

## Requirements

For local development:
- Python 3.6 or higher
- Pillow library
- Flask

For Docker deployment:
- Docker and Docker Compose

## Installation

### Local Development

1. Clone or download this repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Run the application:
```
python script.py
```
4. Access the web interface at http://localhost:3756

### Docker Deployment

#### Using Docker Compose (Recommended)

1. Clone this repository
2. Run with Docker Compose:
```
docker-compose up -d
```
3. Access the web interface at http://localhost:3756

#### Using Docker directly

1. Pull the image from Docker Hub:
```
docker pull binuengoor/image-optimizer-for-web:latest
```

2. Run the container:
```
docker run -d -p 3756:3756 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --name webp-optimizer \
  binuengoor/image-optimizer-for-web:latest
```

3. Access the web interface at http://localhost:3756

#### Building the Docker image locally

1. Clone this repository
2. Build the Docker image:
```
docker build -t image-optimizer-for-web .
```

3. Run the container:
```
docker run -d -p 3756:3756 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --name webp-optimizer \
  image-optimizer-for-web
```

## Usage

1. Open the web interface at http://localhost:3756
2. Drag and drop images or click "Browse Files" to select images
3. Select compression mode and max dimension
4. Click "Convert" to process the images
5. Download the converted WebP files from the Output Folder section

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
- GIF
- WEBP

## Environment Variables

For Docker deployment, you can customize the application using environment variables:

- `PORT`: The port to run the application (default: 3756)
- `DEBUG`: Enable debug mode, set to True/False (default: False)
- `MAX_UPLOAD_SIZE`: Maximum upload file size in bytes (default: 16MB)

Example:
```
docker run -d -p 8080:8080 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -e PORT=8080 \
  -e DEBUG=True \
  --name webp-optimizer \
  binuengoor/image-optimizer-for-web:latest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.