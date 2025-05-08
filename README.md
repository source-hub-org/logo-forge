# LogoForge

LogoForge is a powerful command-line tool for generating text-based logos with customizable typography. Built with Django and the Pillow library, it allows you to create professional-looking logos with your site name and slogan using a simple JSON configuration.

## Features

- Generate PNG images with transparent backgrounds
- Customize site name and slogan with different fonts, sizes, colors, and positions
- Support for Google Fonts with automatic font downloading and caching
- Adjustable letter spacing and word spacing for perfect typography
- Automatic image trimming to remove excess transparent space

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/logo-forge.git
   cd logo-forge
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Google Fonts API key in the environment variables or settings.

## Usage

### Basic Usage

Generate a logo using the default configuration:

```
python manage.py generate_logo
```

This will create an `output.png` file with your logo.

### Custom Configuration

Create your own JSON configuration file and specify it when running the command:

```
python manage.py generate_logo path/to/your/config.json
```

### Trimming the Output

To remove excess transparent space around your logo:

```
convert output.png -trim output_trimmed.png
```

Or use the built-in Python trimming utility:

```
python -m logo_force.trim_logo
```

## Configuration

The JSON configuration file allows you to customize every aspect of your logo. Here's an example:

```json
{
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
5. The image is saved as a PNG file
6. Optionally, the image can be trimmed to remove excess transparent space

## License

This project is licensed under the terms of the included LICENSE file.
