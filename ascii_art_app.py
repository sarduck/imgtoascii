import sys
import os
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                             QSlider, QSpinBox, QTextEdit, QComboBox, QCheckBox,
                             QMessageBox, QFrame, QSplitter, QGridLayout,
                             QColorDialog, QGroupBox)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QTextCursor
from PyQt5.QtCore import Qt, QSize

# ASCII character sets (from darkest to lightest)
ASCII_SETS = {
    "Standard": ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."],
    "Detailed": ["$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", "\"", "^", "`", "'", ".", " "],
    "Simple": ["#", "+", ":", ".", " "],
    "WhatsApp": ["█", "▓", "▒", "░", "⠀"],  # WhatsApp-friendly characters (block elements and invisible space)
    "iPhone": ["#", "8", "=", ":", "."]  # iPhone-WhatsApp friendly (narrower characters)
}

class AsciiArtConverter:
    @staticmethod
    def resize_image(image, new_width, aspect_correction=0.5):
        width, height = image.size
        # Apply aspect ratio correction factor to compensate for character height/width ratio
        # Most fixed-width fonts have characters that are about 2x taller than wide
        ratio = height / width / aspect_correction
        new_height = int(new_width * ratio)
        resized_image = image.resize((new_width, new_height))
        return resized_image
    
    @staticmethod
    def pixels_to_ascii(image, ascii_chars):
        pixels = image.getdata()
        # Map pixel values to characters based on brightness
        # Adjust the division value based on the number of characters
        divisor = 256 // len(ascii_chars)
        characters = "".join([ascii_chars[min(pixel//divisor, len(ascii_chars)-1)] for pixel in pixels])
        return characters
    
    @staticmethod
    def gray(image, invert=False):
        grayscale_image = image.convert("L")
        # Invert the image if requested
        if invert:
            grayscale_image = Image.eval(grayscale_image, lambda x: 255 - x)
        return grayscale_image
    
    @staticmethod
    def convert_to_ascii(image_path, width=100, ascii_set="Standard", invert=False, aspect_ratio=0.5):
        try:
            image = Image.open(image_path)
            ascii_chars = ASCII_SETS[ascii_set]
            
            # Convert image to ASCII
            new_image_data = AsciiArtConverter.pixels_to_ascii(
                AsciiArtConverter.gray(
                    AsciiArtConverter.resize_image(image, width, aspect_ratio), 
                    invert
                ),
                ascii_chars
            )
            
            # Format
            pixel_count = len(new_image_data)  
            ascii_image = "\n".join([new_image_data[index:(index+width)] for index in range(0, pixel_count, width)])
            
            return ascii_image
        except Exception as e:
            return f"Error: {str(e)}"


class AsciiArtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize attributes before calling initUI
        self.current_image_path = None
        self.text_color = QColor("#000000")  # Default text color
        self.bg_color = QColor("#ffffff")    # Default background color
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("ASCII Art Generator")
        self.setMinimumSize(1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Splitter for image and text areas
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - controls and image preview
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Control panel
        control_panel = QFrame()
        control_panel.setFrameShape(QFrame.StyledPanel)
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        
        # Image selection
        img_button_layout = QHBoxLayout()
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(30)
        self.select_button = QPushButton("Select Image")
        self.select_button.setIcon(QIcon.fromTheme("document-open"))
        self.select_button.clicked.connect(self.select_image)
        img_button_layout.addWidget(self.image_label)
        img_button_layout.addWidget(self.select_button)
        control_layout.addLayout(img_button_layout)
        
        # Image preview
        preview_group = QGroupBox("Image Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        left_layout.addWidget(control_panel)
        left_layout.addWidget(preview_group, 1)
        
        # ASCII Settings
        settings_group = QGroupBox("ASCII Settings")
        settings_layout = QGridLayout()
        
        # Width slider
        settings_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 500)
        self.width_spin.setValue(100)
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(10, 500)
        self.width_slider.setValue(100)
        self.width_slider.valueChanged.connect(self.width_spin.setValue)
        self.width_spin.valueChanged.connect(self.width_slider.setValue)
        settings_layout.addWidget(self.width_spin, 0, 1)
        settings_layout.addWidget(self.width_slider, 0, 2)
        
        # Aspect ratio correction
        settings_layout.addWidget(QLabel("Aspect Ratio:"), 1, 0)
        self.aspect_spin = QSpinBox()
        self.aspect_spin.setRange(1, 100)
        self.aspect_spin.setValue(50)  # Default 0.5 (50%)
        self.aspect_spin.setSuffix("%")
        self.aspect_slider = QSlider(Qt.Horizontal)
        self.aspect_slider.setRange(1, 100)
        self.aspect_slider.setValue(50)
        self.aspect_slider.valueChanged.connect(self.aspect_spin.setValue)
        self.aspect_spin.valueChanged.connect(self.aspect_slider.setValue)
        settings_layout.addWidget(self.aspect_spin, 1, 1)
        settings_layout.addWidget(self.aspect_slider, 1, 2)
        
        # Character set selection
        settings_layout.addWidget(QLabel("Character Set:"), 2, 0)
        self.charset_combo = QComboBox()
        for key in ASCII_SETS.keys():
            self.charset_combo.addItem(key)
        settings_layout.addWidget(self.charset_combo, 2, 1, 1, 2)
        
        # Font size for output
        settings_layout.addWidget(QLabel("Font Size:"), 3, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(4, 20)
        self.font_size_spin.setValue(8)  # Default font size
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        settings_layout.addWidget(self.font_size_spin, 3, 1, 1, 2)
        
        # Invert option
        self.invert_check = QCheckBox("Invert Colors")
        settings_layout.addWidget(self.invert_check, 4, 0, 1, 3)
        
        # Color options
        settings_layout.addWidget(QLabel("Text Color:"), 5, 0)
        self.text_color_button = QPushButton()
        self.text_color_button.setFixedSize(QSize(30, 20))
        self.text_color_button.setStyleSheet(f"background-color: {self.text_color.name()}; border: 1px solid #888;")
        self.text_color_button.clicked.connect(self.choose_text_color)
        settings_layout.addWidget(self.text_color_button, 5, 1)
        
        settings_layout.addWidget(QLabel("Background:"), 6, 0)
        self.bg_color_button = QPushButton()
        self.bg_color_button.setFixedSize(QSize(30, 20))
        self.bg_color_button.setStyleSheet(f"background-color: {self.bg_color.name()}; border: 1px solid #888;")
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        settings_layout.addWidget(self.bg_color_button, 6, 1)
        
        # Apply colors to output
        self.apply_colors_check = QCheckBox("Apply Colors")
        self.apply_colors_check.setChecked(True)
        settings_layout.addWidget(self.apply_colors_check, 7, 0, 1, 3)
        
        # WhatsApp mode
        self.whatsapp_mode_check = QCheckBox("WhatsApp Mode")
        self.whatsapp_mode_check.setToolTip("Optimize for sharing on WhatsApp (especially iPhone)")
        self.whatsapp_mode_check.stateChanged.connect(self.toggle_whatsapp_mode)
        settings_layout.addWidget(self.whatsapp_mode_check, 8, 0, 1, 3)
        
        settings_group.setLayout(settings_layout)
        control_layout.addWidget(settings_group)
        
        # Convert Button
        buttons_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convert to ASCII")
        self.convert_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.convert_button.clicked.connect(self.convert_image)
        self.convert_button.setEnabled(False)
        buttons_layout.addWidget(self.convert_button)
        control_layout.addLayout(buttons_layout)
        
        # Right panel - ASCII output
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # ASCII Output
        output_group = QGroupBox("ASCII Output")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 8))
        output_layout.addWidget(self.output_text)
        
        # Output buttons
        output_buttons = QHBoxLayout()
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        
        self.save_button = QPushButton("Save as Text")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_ascii)
        self.save_button.setEnabled(False)
        
        self.save_html_button = QPushButton("Save as HTML")
        self.save_html_button.setIcon(QIcon.fromTheme("text-html"))
        self.save_html_button.clicked.connect(self.save_as_html)
        self.save_html_button.setEnabled(False)
        
        self.whatsapp_button = QPushButton("Share to WhatsApp")
        self.whatsapp_button.setIcon(QIcon.fromTheme("document-share"))
        self.whatsapp_button.clicked.connect(self.share_to_whatsapp)
        self.whatsapp_button.setEnabled(False)
        self.whatsapp_button.setStyleSheet("background-color: #25D366; color: white;")  # WhatsApp green
        
        output_buttons.addWidget(self.copy_button)
        output_buttons.addWidget(self.save_button)
        output_buttons.addWidget(self.save_html_button)
        output_buttons.addWidget(self.whatsapp_button)
        
        output_layout.addLayout(output_buttons)
        output_group.setLayout(output_layout)
        right_layout.addWidget(output_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set style
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QFrame, QGroupBox {
                border-radius: 5px;
                background-color: white;
                padding: 10px;
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QLabel {
                color: #343a40;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 4px;
            }
        """)
    
    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_name:
            self.current_image_path = file_name
            self.image_label.setText(os.path.basename(file_name))
            self.display_preview()
            self.convert_button.setEnabled(True)
            self.statusBar().showMessage(f"Image loaded: {os.path.basename(file_name)}")
    
    def display_preview(self):
        if self.current_image_path:
            pixmap = QPixmap(self.current_image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(pixmap)
                self.preview_label.setMinimumSize(1, 1)  # Allow the label to resize with the pixmap
            else:
                self.preview_label.setText("Cannot display preview")
    
    def choose_text_color(self):
        color = QColorDialog.getColor(self.text_color, self, "Select Text Color")
        if color.isValid():
            self.text_color = color
            self.text_color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")
            
            # Update the output text color if colored output is enabled
            if self.apply_colors_check.isChecked() and self.output_text.toPlainText():
                self.apply_colors()
    
    def choose_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self, "Select Background Color")
        if color.isValid():
            self.bg_color = color
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")
            
            # Update the output background if colored output is enabled
            if self.apply_colors_check.isChecked() and self.output_text.toPlainText():
                self.apply_colors()
    
    def apply_colors(self):
        # Apply the selected colors to the output text
        if self.apply_colors_check.isChecked():
            self.output_text.setStyleSheet(
                f"background-color: {self.bg_color.name()}; color: {self.text_color.name()};"
            )
        else:
            self.output_text.setStyleSheet("")
    
    def update_font_size(self):
        """Update the font size of the ASCII output text."""
        size = self.font_size_spin.value()
        self.output_text.setFont(QFont("Courier New", size))
    
    def convert_image(self):
        if not self.current_image_path:
            return
        
        try:
            width = self.width_spin.value()
            aspect_ratio = self.aspect_spin.value() / 100  # Convert percentage to decimal
            charset = self.charset_combo.currentText()
            invert = self.invert_check.isChecked()
            
            self.statusBar().showMessage("Converting image to ASCII...")
            
            ascii_result = AsciiArtConverter.convert_to_ascii(
                self.current_image_path, 
                width=width,
                ascii_set=charset,
                invert=invert,
                aspect_ratio=aspect_ratio
            )
            
            self.output_text.setText(ascii_result)
            self.apply_colors()
            
            # Enable buttons
            self.save_button.setEnabled(True)
            self.copy_button.setEnabled(True)
            self.save_html_button.setEnabled(True)
            self.whatsapp_button.setEnabled(True)
            
            self.statusBar().showMessage("Conversion complete")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error converting image: {str(e)}")
            self.statusBar().showMessage("Conversion failed")
    
    def copy_to_clipboard(self):
        if not self.output_text.toPlainText():
            return
            
        clipboard = QApplication.clipboard()
        text = self.output_text.toPlainText()
        
        # For WhatsApp mode, add formatting to help with iPhone display
        if self.whatsapp_mode_check.isChecked():
            # Add zero-width spaces between lines to help preserve format on iPhone
            lines = text.split("\n")
            # Add extra spacing between lines for iPhone
            text = "\n\n".join(lines)
        
        clipboard.setText(text)
        self.statusBar().showMessage("ASCII art copied to clipboard (WhatsApp-optimized)" if self.whatsapp_mode_check.isChecked() else "ASCII art copied to clipboard")
    
    def save_ascii(self):
        if not self.output_text.toPlainText():
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save ASCII Art", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.output_text.toPlainText())
                self.statusBar().showMessage(f"ASCII art saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")
                self.statusBar().showMessage("Save failed")
    
    def save_as_html(self):
        if not self.output_text.toPlainText():
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save as HTML", "", "HTML Files (*.html);;All Files (*)"
        )
        
        if file_name:
            try:
                text = self.output_text.toPlainText()
                
                # Special handling for WhatsApp mode
                if self.whatsapp_mode_check.isChecked():
                    # Add a special note for WhatsApp sharing
                    whatsapp_note = """
<div style="margin-top: 20px; padding: 10px; background-color: #dcf8c6; border-radius: 5px;">
    <p><strong>WhatsApp Sharing Instructions:</strong></p>
    <ol>
        <li>Copy from this HTML file by selecting all (Ctrl+A) and copying (Ctrl+C)</li>
        <li>Paste directly into WhatsApp</li>
        <li>For iPhone users: You may need to paste into Notes app first, then copy again to WhatsApp</li>
    </ol>
</div>
"""
                else:
                    whatsapp_note = ""
                
                # Replace spaces with non-breaking spaces and newlines with <br>
                text = text.replace(" ", "&nbsp;").replace("\n", "<br>")
                
                # Get the current font size
                font_size = self.font_size_spin.value()
                
                # Calculate an appropriate line-height based on aspect ratio
                aspect_ratio = self.aspect_spin.value() / 100
                line_height = aspect_ratio * 1.2  # Adjust this multiplier as needed
                
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ASCII Art</title>
    <style>
        body {{
            background-color: {self.bg_color.name()};
            margin: 20px;
            font-family: monospace;
        }}
        pre {{
            color: {self.text_color.name()};
            font-family: 'Courier New', monospace;
            font-size: {font_size}pt;
            line-height: {line_height};
            white-space: pre;
            letter-spacing: {"-0.1em" if self.whatsapp_mode_check.isChecked() else "0"};
        }}
    </style>
</head>
<body>
    <pre>{text}</pre>
    {whatsapp_note}
</body>
</html>"""
                
                with open(file_name, 'w') as f:
                    f.write(html_content)
                self.statusBar().showMessage(f"ASCII art saved as HTML to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving HTML file: {str(e)}")
                self.statusBar().showMessage("Save failed")
    
    def toggle_whatsapp_mode(self, state):
        """Toggle WhatsApp-friendly mode for better sharing on mobile."""
        if state:
            # Default character set based on device
            charset = "iPhone"  # Use iPhone-optimized characters by default
            
            # Select the appropriate character set
            index = self.charset_combo.findText(charset)
            if index >= 0:
                self.charset_combo.setCurrentIndex(index)
            
            # Adjust width for iPhone screen (narrower than regular WhatsApp)
            self.width_spin.setValue(20)  # Reduced width for iPhone
            
            # Set optimal aspect ratio for WhatsApp
            self.aspect_spin.setValue(90)  # Higher aspect ratio for iPhone
            
            # Set appropriate font size
            self.font_size_spin.setValue(12)
            
            self.statusBar().showMessage("WhatsApp mode enabled (iPhone optimized)")
        else:
            # Reset to default values if turning off
            self.statusBar().showMessage("WhatsApp mode disabled")

    def share_to_whatsapp(self):
        """Prepare and share ASCII art to WhatsApp."""
        if not self.output_text.toPlainText():
            return
        
        # Automatically enable WhatsApp mode if not already enabled
        if not self.whatsapp_mode_check.isChecked():
            self.whatsapp_mode_check.setChecked(True)
            # This will trigger toggle_whatsapp_mode and convert
            self.convert_image()
        
        # Create temporary HTML file for easy copy-paste to WhatsApp
        temp_dir = os.path.join(os.path.expanduser("~"), ".ascii_art_temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, "whatsapp_share.html")
        
        try:
            text = self.output_text.toPlainText()
            
            # Process text for iPhone-WhatsApp compatibility
            lines = text.split("\n")
            # Add double line breaks for iPhone display
            text = "\n\n".join(lines)
            
            # Special handling for WhatsApp
            # Replace spaces with non-breaking spaces and newlines with <br><br> for iPhone
            text = text.replace(" ", "&nbsp;").replace("\n", "<br><br>")
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp ASCII Art for iPhone</title>
    <style>
        body {{
            background-color: #ECE5DD;  /* WhatsApp chat background */
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }}
        .message {{
            background-color: #DCF8C6;  /* WhatsApp message bubble */
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 20px;
            position: relative;
            max-width: 80%;
            float: right;
            clear: both;
        }}
        .message::after {{
            content: "";
            position: absolute;
            right: -10px;
            top: 10px;
            border-width: 10px 0 0 10px;
            border-style: solid;
            border-color: transparent transparent transparent #DCF8C6;
        }}
        pre {{
            font-family: 'Courier New', monospace;
            margin: 0;
            white-space: pre;
            overflow-x: auto;
            color: #000000;
            font-size: 12pt;
            line-height: 1.0;
            letter-spacing: -0.1em;  /* Tight letter spacing for iPhone */
        }}
        .instructions {{
            margin-top: 20px;
            padding: 15px;
            background-color: #FFF9C4;
            border-radius: 8px;
            clear: both;
        }}
        .btn {{
            background-color: #25D366;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            display: inline-block;
            margin-top: 15px;
            text-decoration: none;
        }}
        .clearfix::after {{
            content: "";
            clear: both;
            display: table;
        }}
        .iphone-note {{
            background-color: #ffcdd2;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Your WhatsApp ASCII Art</h2>
        <div class="clearfix">
            <div class="message">
                <pre>{text}</pre>
            </div>
        </div>
        <div class="instructions">
            <h3>How to share on iPhone WhatsApp:</h3>
            <ol>
                <li>Click the <strong>Select ASCII Art</strong> button below</li>
                <li>Press <strong>Ctrl+C</strong> (or Cmd+C on Mac) to copy</li>
                <li>Open <strong>Notes</strong> app on your iPhone first</li>
                <li>Paste the content into Notes</li>
                <li>Then copy from Notes and paste to WhatsApp</li>
            </ol>
            <div class="iphone-note">
                <p>⚠️ For best results on iPhone:</p>
                <ol>
                    <li>After pasting in Notes, make sure the text looks good before copying again</li>
                    <li>Use smaller images for better results</li>
                    <li>The simpler the image, the better it will display</li>
                </ol>
            </div>
            <button class="btn" id="selectBtn">Select ASCII Art</button>
            <a href="https://web.whatsapp.com/" target="_blank" class="btn">Open WhatsApp Web</a>
        </div>
    </div>
    
    <script>
        document.getElementById('selectBtn').addEventListener('click', function() {{
            const range = document.createRange();
            range.selectNode(document.querySelector('.message pre'));
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
        }});
    </script>
</body>
</html>"""
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open the HTML file in the default browser
            import webbrowser
            webbrowser.open('file://' + temp_file)
            self.statusBar().showMessage(f"iPhone-optimized WhatsApp sharing page opened in browser")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error preparing WhatsApp share: {str(e)}")
            self.statusBar().showMessage("WhatsApp sharing failed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look across platforms
    window = AsciiArtApp()
    window.show()
    sys.exit(app.exec_()) 