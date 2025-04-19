# ASCII Art Generator

A cross-platform GUI application that converts images to ASCII art.

## Features

- Load images (PNG, JPG, JPEG, BMP, GIF)
- Preview the loaded image
- Convert images to ASCII art with customizable settings
- Adjust output width with a slider
- Choose from different ASCII character sets:
  - Standard: Basic 11-character set 
  - Detailed: Extended 70-character set for more detailed output
  - Simple: Minimal 5-character set
- Color customization:
  - Choose text color
  - Choose background color
  - Apply colors to the ASCII output
- Option to invert colors (dark becomes light, light becomes dark)
- Export options:
  - Copy to clipboard
  - Save as plain text file
  - Save as HTML file with styling
- Modern and intuitive user interface
- Works on Windows 11 and Fedora 41

## Requirements

- Python 3.6+
- Pillow library (for image processing)
- PyQt5 (for the GUI)

## Installation

### Easy Installation (Recommended)

Run the installation script which will check for dependencies and set up the application:

```bash
python install.py
```

The script will:
1. Check if you have the correct Python version
2. Install required packages automatically
3. Optionally create a desktop shortcut

### Manual Installation

1. Clone or download this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python ascii_art_app.py
```

### Using the Application

1. Click "Select Image" to choose an image file
2. Adjust the settings:
   - Width: Controls the number of characters per line
   - Character Set: Choose between different ASCII character sets
   - Text/Background Color: Customize the appearance
   - Invert Colors: Invert the brightness values
3. Click "Convert to ASCII" to generate the ASCII art
4. Export your creation:
   - Click "Copy to Clipboard" to copy the ASCII art
   - Click "Save as Text" to save as a plain text file
   - Click "Save as HTML" to save as an HTML file with styling

## Screenshots

(Add screenshots here after running the application)

## License

MIT License