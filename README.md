# LogoForge

LogoForge is a powerful command-line tool for generating text-based logos with customizable typography. Built with Django and the Pillow library, it allows you to create professional-looking logos with your site name and slogan using a simple JSON configuration.

## Features

- Generate PNG or SVG images with transparent backgrounds
- Customize site name and slogan with different fonts, sizes, colors, and positions
- Support for Google Fonts with automatic font downloading and caching
- Adjustable letter spacing and word spacing for perfect typography
- Automatic image trimming to remove excess transparent space for both PNG and SVG formats
- SVG output with options for font embedding or linking to Google Fonts

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/logo-forge.git
   cd logo-forge
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   This creates an isolated Python environment for the project. The `source venv/bin/activate` command activates the environment, which you'll see indicated by `(venv)` in your command prompt.

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Google Fonts API key in the environment variables or settings.

5. When you're done working with the project, you can deactivate the virtual environment:
   ```
   deactivate
   ```
   
   This returns your terminal to the global Python environment.

## Usage

### Basic Usage

Generate a logo using the default configuration:

```
python manage.py generate_logo
```

This will create an `output.png` or `output.svg` file with your logo, depending on your configuration.

### Custom Configuration

Create your own JSON configuration file and specify it when running the command:

```
python manage.py generate_logo path/to/your/config.json
```

### Trimming the Output

To remove excess transparent space around your logo, you have several options:

#### 1. Automatic trimming with the command-line flag

```
python manage.py generate_logo --trim
```

This will generate both the original logo and a trimmed version with the suffix "_trimmed".

#### 2. Automatic trimming via configuration

Add the `auto_trim` option to your configuration file:

```json
{
  "output": "png",
  "auto_trim": true,
  ...
}
```

#### 3. Manual trimming with ImageMagick (for PNG files)

```
convert output.png -trim output_trimmed.png
```

#### 4. Manual trimming with the built-in Python utility (supports both PNG and SVG)

```
python -m logo_force.trim_logo
```

The trimming functionality works for both PNG and SVG output formats. For SVG files, it calculates the bounding box of all text elements and adjusts the SVG's viewBox accordingly.

## SVG Output Options

LogoForge supports SVG output with two font handling options:

### 1. Linking to Google Fonts (Default)

```json
{
  "output": "svg",
  "svg_options": {
    "embed_fonts": false
  }
}
```

This generates an SVG that links to Google Fonts CDN:

```xml
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style type="text/css">
      @import url('https://fonts.googleapis.com/css2?family=Roboto&family=Open+Sans&display=swap');
    </style>
  </defs>
  <!-- SVG content -->
</svg>
```

### 2. Embedding Fonts

```json
{
  "output": "svg",
  "svg_options": {
    "embed_fonts": true
  }
}
```

This embeds the font data directly in the SVG for offline use:

```xml
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style type="text/css">
      @font-face {
        font-family: 'Roboto';
        src: url('data:font/truetype;base64,AAEAAAASAQAABAAgR0RFRgBKAA...') format('truetype');
        font-weight: normal;
        font-style: normal;
      }
      /* Additional embedded fonts */
    </style>
  </defs>
  <!-- SVG content -->
</svg>
```

## Configuration

The JSON configuration file allows you to customize every aspect of your logo. Here's an example:

```json
{
  "output": "png",
  "auto_trim": false,
  "svg_options": {
    "embed_fonts": false
  },
  "image": {
    "width": 800,
    "height": 600,
    "background": "transparent"
  },
  "site_name": {
    "text": "Your Site Name",
    "font_family": "Roboto",
    "font_weight": 700,
    "font_style": "normal",
    "font_size": 72,
    "color": "#000000",
    "position": {"x": 200, "y": 250},
    "letter_spacing": 10,
    "word_spacing": 30
  },
  "slogan": {
    "text": "Your catchy slogan goes here",
    "font_family": "Open Sans",
    "font_weight": 400,
    "font_style": "italic",
    "font_size": 24,
    "color": "#555555",
    "position": {"x": 200, "y": 350},
    "letter_spacing": 2,
    "word_spacing": 5
  }
}
```

### Configuration Options

- **output**: Output format, either "png" or "svg" (default: "png")
- **auto_trim**: Whether to automatically trim excess transparent space (default: false)
- **svg_options**: Options specific to SVG output:
  - `embed_fonts`: Whether to embed fonts in the SVG file (default: false)
- **image**: Define the canvas dimensions and background
- **site_name** and **slogan**: Configure text elements with:
  - `text`: The content to display
  - `font_family`: Any Google Font family name
  - `font_weight`: Font weight (e.g., 400, 700)
  - `font_style`: Font style ("normal" or "italic")
  - `font_size`: Size in pixels
  - `color`: Hex color code
  - `position`: X and Y coordinates
  - `letter_spacing`: Extra space between letters in pixels
  - `word_spacing`: Extra space between words in pixels

## How It Works

1. The tool reads your JSON configuration
2. It downloads and caches any required Google Fonts
3. A transparent canvas is created with the specified dimensions
4. Text elements are rendered with the configured typography settings
5. The image is saved in the specified format (PNG or SVG)
6. Optionally, the image can be trimmed to remove excess transparent space

### SVG Generation Process

For SVG output, the tool:
1. Creates an SVG document with the specified dimensions
2. Adds Google Fonts import or embeds fonts directly as data URIs
3. Renders text elements with proper positioning and styling
4. Applies letter and word spacing by positioning each character individually
5. Optionally trims the SVG by calculating the bounding box of all text elements and adjusting the viewBox

### PNG Generation Process

For PNG output, the tool:
1. Creates a transparent image with the specified dimensions
2. Downloads and loads the specified Google Fonts
3. Renders text elements with proper positioning and styling
4. Applies letter and word spacing by positioning each character individually
5. Optionally trims the image by removing transparent borders

## Code Examples

### Generating a Logo Programmatically

```python
from logo_generator.services.logo_service import generate_logo

# Generate a logo using the default configuration
output_path = generate_logo()
print(f"Logo created at: {output_path}")

# Generate a logo with a custom configuration
output_path = generate_logo("path/to/config.json")
print(f"Logo created at: {output_path}")
```

### Trimming a Logo Programmatically

```python
from logo_force.trim_logo import trim_image

# Trim a PNG image
trim_image("output.png", "output_trimmed.png")

# Trim an SVG image
trim_image("output.svg", "output_trimmed.svg")
```

## Development

### Code Quality

Maintain code quality by running these commands before submitting changes:

```bash
black .
isort .
ruff check --fix .
```

These tools help ensure consistent code formatting and quality:
- `black`: Formats Python code according to a consistent style
- `isort`: Sorts and organizes your imports
- `ruff`: Fast Python linter that identifies and fixes common issues

## License

This project is licensed under the terms of the included LICENSE file.
