# Daisy

SVG generator for AxiDraw A3 XY pen plotter label printing. Generates precision-aligned text for pre-printed cocktail labels.

## Overview

Daisy is a Python command-line tool that creates SVG files for adding customized text to pre-printed labels using an AxiDraw A3 plotter. Each SVG file contains 8 identical labels arranged in a 2×4 grid on an A3 sheet.

## Features

- ✨ Generates A3 SVG files with 8 identical labels
- 🎯 Precision positioning to avoid pre-printed graphics
- 🔤 Uses Brandon Grotesque Regular font (Brandon_reg.otf)
- ✅ Input validation with clear error messages
- 📏 Configurable font sizes
- 🎨 Text rendered as paths for accurate plotter output

## Installation

### Requirements

- Python 3.9 or higher
- Brandon_reg.otf font file (included in repository)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd daisy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### Basic Usage

Generate an SVG with all 8 labels:

```bash
daisy generate \
  --product-name "ESPRESSO|MARTINI" \
  --description "Rich coffee with smooth vodka" \
  --abv "12%" \
  --volume "200ml"
```

This creates `espresso-martini.svg` in the current directory.

### Command Options

**Required Arguments:**
- `--product-name`: Product name with `|` separator for line break (max 40 chars)
- `--description`: Product description (max 160 chars)
- `--abv`: ABV percentage (4-6 chars)
- `--volume`: Volume information (4-6 chars)

**Optional Arguments:**
- `--output`: Custom output path (default: auto-generated from product name)
- `--font-size`: Font size in millimeters (default: 4mm)
- `--preview`: Validate inputs without generating file

### Examples

**Custom output path:**
```bash
daisy generate \
  --product-name "NEGRONI|CLASSIC" \
  --description "Bitter, sweet & perfectly balanced" \
  --abv "24%" \
  --volume "200ml" \
  --output my-labels.svg
```

**Custom font size:**
```bash
daisy generate \
  --product-name "MARGARITA|FRESH" \
  --description "Tangy lime with premium tequila" \
  --abv "18%" \
  --volume "200ml" \
  --font-size 3.5
```

**Preview mode (validation only):**
```bash
daisy generate \
  --product-name "TEST|PRODUCT" \
  --description "Test description" \
  --abv "12%" \
  --volume "200ml" \
  --preview
```

## Label Layout

Each A3 sheet (420mm × 297mm landscape) contains:
- **8 labels** in a 2×4 grid
- **Label size**: 155mm × 70mm each
- **Margins**: 27.5mm left/right, 5.5mm top/bottom
- **Gaps**: 55mm horizontal, 2mm vertical

### Text Sections

Each label has three text sections:

1. **Product Name** (51-77.5mm from left edge)
   - Two lines, center-aligned
   - Split using `|` character

2. **Description** (116-147mm from left edge)
   - Multi-line, left-aligned
   - Product description or tasting notes

3. **ABV/Volume** (148-155mm from left edge)
   - Two lines, right-aligned
   - ABV percentage and volume

All text is bottom-aligned within its section.

## AxiDraw Plotting

The generated SVG files are optimized for AxiDraw plotters:

- Text is converted to paths (no font issues)
- Stroke-based rendering (no fills)
- Millimeter units throughout
- 0.5mm stroke width

To plot:
1. Open SVG in Inkscape
2. Use AxiDraw extension to plot
3. Ensure paper is aligned to origin (0,0)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_config.py
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting

```bash
# Run pylint
pylint src/
```

## Project Structure

```
daisy/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── svg_generator.py    # SVG generation logic
│   ├── label_layout.py     # Label positioning
│   ├── text_renderer.py    # Font handling
│   └── config.py           # Constants
├── tests/
│   ├── test_config.py
│   └── test_label_layout.py
├── Brandon_reg.otf         # House font
├── requirements.txt
├── pyproject.toml
├── CLAUDE.md              # AI assistant guide
└── README.md              # This file
```

## Technical Details

### Dependencies

- **svgwrite**: SVG file generation
- **fonttools**: OTF font parsing and text-to-path conversion
- **click**: Command-line interface framework

### Coordinate System

- Origin (0,0) at top-left corner
- X increases rightward
- Y increases downward
- All measurements in millimeters

### Font Rendering

Text is converted to SVG paths using fontTools for maximum accuracy and portability. This ensures the plotter renders exactly what you see in the SVG, regardless of font availability.

## Troubleshooting

### Font not found

Ensure `Brandon_reg.otf` is in the same directory as where you run the `daisy` command.

### Validation errors

All inputs are validated before SVG generation:
- Product name must include `|` separator and be ≤40 chars
- Description must be ≤160 chars
- ABV and volume must be 4-6 chars each

### SVG doesn't plot correctly

- Verify SVG opens correctly in Inkscape
- Check that text appears as paths (not text elements)
- Ensure AxiDraw is calibrated for A3 paper
- Confirm paper alignment at origin (0,0)

## License

Copyright © 2025 Daisy Drinks. All rights reserved.

## Support

For issues or questions, please contact the Daisy team.
