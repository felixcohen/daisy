# CLAUDE.md - Daisy Project Guide for AI Assistants

## Project Overview

**Daisy** is a command-line Python application designed to generate SVG files for use with an AxiDraw A3 XY pen plotter. The primary use case is adding customized text to pre-printed labels in a label printing business.

### Business Context
- The business produces printed labels
- Labels are printed on A3 sheets in landscape orientation (420mm × 297mm)
- **8 labels per A3 sheet** in a 2×4 grid layout
- The AxiDraw A3 plotter is used to add variable text/data to labels after printing
- SVG files guide the plotter's pen movements

### Technical Specifications
- **Plotter**: AxiDraw A3 (XY pen plotter)
- **Paper Size**: A3 Landscape (420mm width × 297mm height)
- **Label Layout**: 8 labels per sheet (2 columns × 4 rows)
- **Label Dimensions**: 155mm × 70mm each
- **Output Format**: SVG (Scalable Vector Graphics)
- **Implementation**: Python CLI application
- **House Font**: Brandon_reg.otf (Brandon Grotesque Regular)
- **Reference**: See `Manhattans Project Blank Label.pdf` for label design example

---

## Repository Structure

This is a new project. The recommended structure is:

```
daisy/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface entry point
│   ├── svg_generator.py    # Core SVG generation logic
│   ├── label_layout.py     # Label positioning and layout management
│   ├── text_renderer.py    # Text formatting and rendering
│   └── config.py           # Configuration and constants
├── tests/
│   ├── __init__.py
│   ├── test_svg_generator.py
│   ├── test_label_layout.py
│   └── test_text_renderer.py
├── fonts/                  # Font files (or keep in root)
│   └── Brandon_reg.otf     # House font - Brandon Grotesque Regular
├── templates/              # SVG templates (if needed)
├── output/                 # Generated SVG files (gitignored)
├── examples/               # Example configurations and outputs
├── Brandon_reg.otf         # House font (currently in root)
├── Manhattans Project Blank Label.pdf  # Example label design reference
├── requirements.txt        # Python dependencies
├── setup.py               # Package installation configuration
├── pyproject.toml         # Modern Python project configuration
├── README.md              # User-facing documentation
├── CLAUDE.md              # This file - AI assistant guide
└── .gitignore             # Git ignore rules

```

---

## Development Workflows

### Initial Setup
1. **Python Environment**: Use Python 3.9+
2. **Virtual Environment**: Always use a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

### Key Dependencies to Consider
- **svgwrite** or **drawSvg**: SVG generation libraries
- **fontTools** or **freetype-py**: OTF font parsing and text-to-path conversion
- **click** or **argparse**: CLI framework
- **pyyaml**: Configuration file parsing (if using YAML configs)
- **pytest**: Testing framework
- **black**: Code formatting
- **pylint** or **flake8**: Code linting

**Critical for Text Rendering:**
- **fontTools**: For reading OTF font files and converting text to SVG paths
- **svgpathtools**: For path manipulation and optimization

### Testing Workflow
- Write tests for all core functionality
- Use `pytest` for test execution
- Aim for >80% code coverage
- Test SVG output validity

### Code Quality
- Use **Black** for code formatting (line length: 88 or 100)
- Use type hints (Python 3.9+ style)
- Write docstrings for all public functions and classes
- Follow PEP 8 conventions

---

## Key Technical Considerations

### A3 Dimensions and Coordinate System
- **A3 Size (Landscape)**: 420mm width × 297mm height
- **AxiDraw Coordinate System**: Uses millimeters
- **Origin Point**: Top-left corner (0,0)
- **Label Grid**: 2 columns × 4 rows = 8 labels total

### Exact Label Layout Specifications

**CRITICAL: These measurements must be used exactly as specified**

#### Sheet Dimensions
- **Width**: 420mm
- **Height**: 297mm

#### Label Dimensions
- **Width**: 155mm
- **Height**: 70mm
- **Corner Radius**: 0.7mm (rounded corners)

#### Grid Layout
- **Columns (Across)**: 2
- **Rows (Around)**: 4
- **Total Labels**: 8

#### Margins
- **Top Margin**: 5.5mm
- **Bottom Margin**: 5.5mm
- **Left Margin**: 27.5mm
- **Right Margin**: 27.5mm

#### Gaps Between Labels
- **Horizontal Gap (between columns)**: 55mm
- **Vertical Gap (between rows)**: 2mm

#### Layout Verification
```
Total width calculation:
  Left margin:     27.5mm
  Label 1:        155.0mm
  Gap:             55.0mm
  Label 2:        155.0mm
  Right margin:    27.5mm
  ─────────────────────────
  Total:          420.0mm ✓

Total height calculation:
  Top margin:       5.5mm
  Label row 1:     70.0mm
  Gap:              2.0mm
  Label row 2:     70.0mm
  Gap:              2.0mm
  Label row 3:     70.0mm
  Gap:              2.0mm
  Label row 4:     70.0mm
  Bottom margin:    5.5mm
  ─────────────────────────
  Total:          297.0mm ✓
```

#### Label Numbering Convention
Labels should be numbered 1-8 in reading order (left to right, top to bottom):
```
┌─────────────────────────────────────────┐
│    [1]           [2]                    │
│    [3]           [4]                    │
│    [5]           [6]                    │
│    [7]           [8]                    │
└─────────────────────────────────────────┘
```

#### Label Position Calculations
For each label, the top-left corner position (x, y) can be calculated as:

**Column 1 (labels 1, 3, 5, 7):**
- x = 27.5mm (left margin)

**Column 2 (labels 2, 4, 6, 8):**
- x = 27.5mm + 155mm + 55mm = 237.5mm

**Row positions (for all columns):**
- Row 1 (labels 1, 2): y = 5.5mm
- Row 2 (labels 3, 4): y = 5.5mm + 70mm + 2mm = 77.5mm
- Row 3 (labels 5, 6): y = 5.5mm + 70mm + 2mm + 70mm + 2mm = 149.5mm
- Row 4 (labels 7, 8): y = 5.5mm + 70mm + 2mm + 70mm + 2mm + 70mm + 2mm = 221.5mm

### Text Sections Within Each Label

Each label contains three distinct text sections that the plotter will add to pre-printed labels. See `Manhattans Project Blank Label.pdf` for visual reference.

**CRITICAL: Text must be positioned in these specific areas to avoid overlapping with pre-printed graphics**

#### Section 1: Product Name
- **Position**: Approximately 33%-50% from left edge of label
- **Format**: Two lines of text
- **Content**: Product/cocktail name (e.g., "ESPRESSO MARTINI")
- **Horizontal range**: ~51mm to 77.5mm from label left edge
- **Font**: Brandon_reg.otf

#### Section 2: Product Description
- **Position**: Approximately 75%-95% from left edge of label
- **Format**: Single or multi-line text
- **Content**: Product description or tasting notes
- **Horizontal range**: ~116mm to 147mm from label left edge
- **Font**: Brandon_reg.otf

#### Section 3: ABV/Volume Information
- **Position**: To the right of the vertical line at far right of label
- **Format**: Typically 2-3 lines
- **Content**:
  - ABV percentage (e.g., "12% ABV")
  - Total volume (e.g., "200ml")
- **Horizontal range**: ~148mm to 155mm from label left edge (rightmost section)
- **Font**: Brandon_reg.otf
- **Note**: This section is after the printed vertical divider line

#### Important Text Positioning Notes
1. The pre-printed label includes the "daisy" logo on the left (~0-33%)
2. Decorative cocktail glass illustrations occupy the center area
3. A vertical line separates the ABV section on the far right
4. Text must avoid these pre-printed areas
5. All text should be converted to paths for accurate plotting
6. Use the Brandon_reg.otf font file included in the repository

#### Coordinate Reference Within Label
For a label with top-left corner at (label_x, label_y):
- **Section 1 (Product Name)**:
  - x range: label_x + 51mm to label_x + 77.5mm
  - Centered vertically or positioned as needed
- **Section 2 (Description)**:
  - x range: label_x + 116mm to label_x + 147mm
  - Centered vertically or positioned as needed
- **Section 3 (ABV/Volume)**:
  - x range: label_x + 148mm to label_x + 155mm
  - Positioned in top-right area

### SVG Best Practices for AxiDraw
1. **Units**: Use millimeters for consistency with A3 specs
2. **Paths**: Generate `<path>` elements for plotter movements
3. **Text to Paths**: Convert text to paths for accurate plotting
4. **Layer Management**: Use groups `<g>` for organizing elements
5. **Stroke Width**: Keep strokes thin (plotter pen width)
6. **No Fills**: AxiDraw plots outlines only, avoid filled shapes
7. **Pen Lifts**: Minimize pen up/down movements for efficiency

### AxiDraw-Specific Requirements
- **Stroke-based graphics only**: No fills, only strokes
- **Single color**: One pen at a time
- **Optimized path order**: Minimize pen travel time
- **Safe margins**: Keep content within printable area
- **Font considerations**: Use fonts that convert well to paths

---

## CLI Design

### Command Structure

**IMPORTANT**: The tool generates SVG files with all 8 labels populated with the same content. No CSV batch processing - all inputs are provided via command line arguments.

```bash
# Basic usage - generates all 8 labels with same content
daisy generate \
  --product-name "ESPRESSO|MARTINI" \
  --description "Rich coffee with smooth vodka" \
  --abv "12%" \
  --volume "200ml"

# The output file is automatically named based on product name
# Output: espresso-martini.svg

# With custom font size
daisy generate \
  --product-name "NEGRONI|CLASSIC" \
  --description "Bitter, sweet & perfectly balanced" \
  --abv "24%" \
  --volume "200ml" \
  --font-size 3.5

# With custom output location
daisy generate \
  --product-name "MARGARITA|FRESH" \
  --description "Tangy lime with premium tequila" \
  --abv "18%" \
  --volume "200ml" \
  --output /path/to/margarita-fresh.svg

# Preview mode (dry run) - validates without generating file
daisy generate \
  --product-name "TEST|PRODUCT" \
  --description "Test description" \
  --abv "12%" \
  --volume "200ml" \
  --preview
```

**Product Name Line Breaking**: Use pipe character `|` to manually specify where to split the product name across two lines. For example, `"ESPRESSO|MARTINI"` will render as:
```
ESPRESSO
MARTINI
```

### Command-Line Arguments

**Required:**
- `--product-name`: Product name with pipe `|` separator for 2-line split (max 40 chars total)
- `--description`: Product description text (max 160 chars)
- `--abv`: ABV percentage (4-6 chars, e.g., "12%" or "12.5%")
- `--volume`: Volume information (4-6 chars, e.g., "200ml")

**Optional:**
- `--output`: Custom output SVG file path (defaults to auto-generated from product name)
- `--font-size`: Text size in mm (optional override, default: 4mm)
- `--preview`: Show preview/validation without generating file (dry run)

**Not Implemented:**
- No `--labels` argument - always generates all 8 labels with same content
- No batch processing from CSV - use shell scripts to call tool multiple times if needed

### Input Validation & Error Handling

**Text Length Validation:**
- Product name: Maximum 40 characters (including pipe separator)
- Product description: Maximum 160 characters
- ABV: 4-6 characters
- Volume: 4-6 characters

**Error Behavior:**
If any text exceeds its maximum length, the tool must:
1. Display a clear error message indicating which field exceeded the limit
2. Show the actual character count vs. the maximum allowed
3. Request the user to provide updated text
4. Exit with non-zero status code

**Line Breaking:**
- Product names must include a pipe `|` character to manually specify line break
- Example: `"ESPRESSO|MARTINI"` renders as two lines
- The tool should validate that the pipe character is present

**Vertical Alignment:**
- All text sections should be aligned to the bottom of their respective areas

**Output File Naming:**
- Automatically generate filename from product name (e.g., "ESPRESSO|MARTINI" → "espresso-martini.svg")
- Convert to lowercase, replace pipe and spaces with hyphens
- User can override with `--output` argument

**No Product Validation:**
- Accept any text input - no validation against known product list

---

## Configuration

### Layout Configuration
Store layout configurations in YAML or JSON using the exact specifications:

```yaml
# layout.yaml - Default configuration matching exact specifications
sheet:
  width_mm: 420
  height_mm: 297
  orientation: "landscape"

labels:
  count: 8
  columns: 2
  rows: 4
  width_mm: 155
  height_mm: 70
  corner_radius_mm: 0.7

margins:
  top_mm: 5.5
  bottom_mm: 5.5
  left_mm: 27.5
  right_mm: 27.5

gaps:
  horizontal_mm: 55  # Gap between columns
  vertical_mm: 2     # Gap between rows

text:
  font_file: "Brandon_reg.otf"  # House font - must use this for production
  font_family: "Brandon Grotesque Regular"
  font_size_mm: 4
  alignment: "center"

  # Text sections with their specific positioning
  sections:
    product_name:
      x_range: [51, 77.5]  # mm from label left edge
      lines: 2
      alignment: "center"
    description:
      x_range: [116, 147]  # mm from label left edge
      alignment: "left"
    abv_volume:
      x_range: [148, 155]  # mm from label left edge
      lines: 2-3
      alignment: "right"
```

**IMPORTANT**: The layout configuration above reflects the exact physical label sheet specifications. Do not modify these values unless the physical label sheets change.

---

## Code Conventions

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Type Hints
```python
from typing import List, Tuple, Optional

def generate_label_svg(
    text: str,
    position: Tuple[float, float],
    font_size: float = 12.0
) -> str:
    """Generate SVG markup for a single label."""
    pass
```

### Docstring Style
Use Google-style docstrings:

```python
def calculate_label_positions(
    columns: int,
    rows: int,
    sheet_width: float,
    sheet_height: float
) -> List[Tuple[float, float]]:
    """Calculate the position of each label on the A3 sheet.

    Args:
        columns: Number of label columns
        rows: Number of label rows
        sheet_width: Width of A3 sheet in mm
        sheet_height: Height of A3 sheet in mm

    Returns:
        List of (x, y) tuples representing top-left corner of each label

    Raises:
        ValueError: If columns or rows are less than 1
    """
    pass
```

### Error Handling
- Use specific exceptions
- Provide helpful error messages
- Validate inputs early
- Handle file I/O errors gracefully

```python
class InvalidLabelNumberError(ValueError):
    """Raised when label number is outside valid range (1-8)."""
    pass
```

---

## Testing Strategy

### Unit Tests
- Test SVG generation functions
- Test label position calculations
- Test text rendering logic
- Test configuration parsing

### Integration Tests
- Test complete SVG generation workflow
- Test CLI commands end-to-end
- Validate SVG output structure

### Output Validation
- Verify SVG is valid XML
- Check dimensions match A3 specifications
- Ensure all paths are within bounds
- Validate no fill attributes (stroke only)

---

## Git Workflow

### Branch Strategy
- `main`: Stable, production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `bugfix/*`: Bug fix branches

### Commit Messages
Follow conventional commits:
- `feat: add batch processing from CSV`
- `fix: correct label positioning for 4×2 layout`
- `docs: update README with installation instructions`
- `test: add tests for SVG generator`
- `refactor: extract font handling to separate module`

### Before Committing
1. Run tests: `pytest`
2. Format code: `black .`
3. Lint code: `pylint src/`
4. Update documentation if needed

---

## Dependencies and External Resources

### Python Libraries
- **svgwrite**: Primary SVG generation library
- **click**: CLI framework (modern alternative to argparse)
- **pyyaml**: YAML configuration parsing
- **pytest**: Testing framework
- **black**: Code formatter
- **mypy**: Static type checker

### AxiDraw Resources
- [AxiDraw Documentation](https://axidraw.com/doc/)
- [AxiDraw Software](https://github.com/evil-mad/axidraw)
- SVG files should be compatible with AxiDraw's Inkscape extension

### SVG References
- [SVG Specification](https://www.w3.org/TR/SVG2/)
- [SVGWrite Documentation](https://svgwrite.readthedocs.io/)
- Focus on `<path>`, `<text>`, and `<g>` elements

---

## Common Tasks for AI Assistants

### Adding New Features
1. Discuss requirements with the user
2. Design the API/interface
3. Write tests first (TDD approach)
4. Implement the feature
5. Update documentation
6. Commit with descriptive message

### Debugging Issues
1. Reproduce the issue
2. Write a failing test case
3. Fix the bug
4. Verify test passes
5. Check for similar issues elsewhere
6. Update documentation if behavior changed

### Refactoring
1. Ensure tests exist and pass
2. Make incremental changes
3. Run tests after each change
4. Keep commits small and focused
5. Update docstrings and type hints

### Adding Dependencies
1. Verify the package is actively maintained
2. Check license compatibility
3. Add to `requirements.txt`
4. Document why it's needed
5. Update installation instructions

---

## Important Considerations

### Performance
- SVG generation should be fast (<1 second per sheet)
- Batch processing should handle hundreds of sheets efficiently
- Consider caching layout calculations

### Extensibility
- Design for different label layouts (not just 8 per sheet)
- Support multiple paper sizes (A3, A4, etc.)
- Allow custom label shapes in future
- Support multiple text fields per label

### Maintainability
- Keep functions small and focused
- Avoid deep nesting
- Use meaningful variable names
- Comment complex algorithms
- Keep configuration separate from code

### User Experience
- Provide clear error messages
- Show progress for batch operations
- Validate inputs before processing
- Offer helpful CLI help text
- Include examples in documentation

---

## Troubleshooting

### Common Issues

**SVG doesn't render correctly in AxiDraw**
- Ensure all elements use strokes, not fills
- Check units are in millimeters
- Verify viewBox matches A3 dimensions
- Test SVG in Inkscape first

**Text positioning is off**
- Verify label position calculations
- Check font metrics and baseline
- Account for font bounding box
- Convert text to paths for accuracy

**Performance issues with batch processing**
- Profile code to find bottlenecks
- Consider parallel processing for large batches
- Cache layout calculations
- Optimize SVG generation

---

## Future Enhancements

Consider these features for future development:
- [ ] Web interface for easier configuration
- [ ] QR code generation support
- [ ] Barcode generation support
- [ ] Multiple font support
- [ ] Template system for complex label designs
- [ ] Preview rendering (PNG/PDF output)
- [ ] AxiDraw direct integration (plot without manual import)
- [ ] Support for multiple pens/colors
- [ ] Variable data mail merge from database

---

## Implementation Requirements (User Confirmed)

The following requirements have been confirmed by the user and must be implemented exactly as specified:

**Text Limits:**
- Product name: 40 characters maximum (including pipe separator)
- Product description: 160 characters maximum
- ABV: 4-6 characters
- Volume: 4-6 characters

**Behavior:**
- Line breaking: Manual split using pipe `|` character (e.g., "ESPRESSO|MARTINI")
- Font size: Configurable via `--font-size` argument (default: 4mm)
- Vertical alignment: All text aligned to bottom of sections
- Error handling: Display error and request updated text if limits exceeded
- Input validation: Accept any text input (no product name validation)
- Output naming: Auto-generate from product name (lowercase, hyphens), or use `--output`
- Label population: Always generate all 8 labels with same content (no selective labeling)
- Data input: Command-line arguments only (no CSV batch processing)

**Fixed Elements (Do Not Question):**
- Label dimensions and sheet layout (see Exact Label Layout Specifications)
- Font file: Brandon_reg.otf (Brandon Grotesque Regular)
- Three text section positions: product name (51-77.5mm), description (116-147mm), ABV/volume (148-155mm)
- Pre-printed label design with daisy logo and cocktail graphics

---

## Contact and Support

This project is owned by the user who operates a label printing business with an AxiDraw A3 plotter.

For AI assistants: Always prioritize:
1. **Accuracy**: SVG dimensions must be exact
2. **Reliability**: Code should never generate invalid SVG
3. **Usability**: CLI should be intuitive
4. **Documentation**: Keep this file updated as project evolves

---

*Last Updated: 2025-11-19*
*Project Status: Requirements Finalized - Ready for implementation*
