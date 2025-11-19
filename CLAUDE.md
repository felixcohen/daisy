# CLAUDE.md - Daisy Project Guide for AI Assistants

## Project Overview

**Daisy** is a command-line Python application designed to generate SVG files for use with an AxiDraw A3 XY pen plotter. The primary use case is adding customized text to pre-printed labels in a label printing business.

### Business Context
- The business produces printed labels
- Labels are printed on A3 sheets (297mm × 420mm)
- **8 labels per A3 sheet** in a grid layout
- The AxiDraw A3 plotter is used to add variable text/data to labels after printing
- SVG files guide the plotter's pen movements

### Technical Specifications
- **Plotter**: AxiDraw A3 (XY pen plotter)
- **Paper Size**: A3 (297mm × 420mm / 11.69" × 16.54")
- **Label Layout**: 8 labels per sheet
- **Output Format**: SVG (Scalable Vector Graphics)
- **Implementation**: Python CLI application

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
├── templates/              # SVG templates (if needed)
├── output/                 # Generated SVG files (gitignored)
├── examples/               # Example configurations and outputs
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
- **click** or **argparse**: CLI framework
- **pyyaml**: Configuration file parsing (if using YAML configs)
- **pytest**: Testing framework
- **black**: Code formatting
- **pylint** or **flake8**: Code linting

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
- **A3 Size**: 297mm × 420mm
- **AxiDraw Coordinate System**: Typically uses millimeters or inches
- **Origin Point**: Usually top-left corner (0,0)
- **Label Grid**: Calculate positions for 8 labels (likely 2×4 or 4×2 grid)

### Label Layout Calculations
For 8 labels on A3, possible layouts:
- **4 columns × 2 rows**: Each label ~74mm × 148.5mm
- **2 columns × 4 rows**: Each label ~148.5mm × 74mm
- Include margins/gutters between labels for cutting

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

### Proposed Command Structure

```bash
# Basic usage
daisy generate --text "Hello World" --output sheet.svg

# With label positioning
daisy generate --text "Serial: 12345" --labels 1,3,5 --output sheet.svg

# Batch generation from CSV
daisy batch --input data.csv --output-dir ./output/

# Preview mode (dry run)
daisy generate --text "Test" --preview

# Custom layout
daisy generate --text "Custom" --layout config.yaml --output sheet.svg
```

### Command-Line Arguments
- `--text`: Text to add to labels (string or list)
- `--labels`: Which labels to populate (1-8, comma-separated)
- `--output`: Output SVG file path
- `--input`: Input data file (CSV, JSON, YAML)
- `--layout`: Custom layout configuration file
- `--font`: Font family/file to use
- `--font-size`: Text size in mm
- `--position`: Text position within each label (center, top-left, etc.)
- `--preview`: Show preview without generating file
- `--dry-run`: Validate inputs without writing file

---

## Configuration

### Layout Configuration
Store layout configurations in YAML or JSON:

```yaml
# layout.yaml
a3:
  width_mm: 297
  height_mm: 420

labels:
  count: 8
  columns: 4
  rows: 2
  margin_mm: 5
  gutter_mm: 3

text:
  font_family: "Arial"
  font_size_mm: 4
  alignment: "center"
  position: [0.5, 0.5]  # Relative position within label (0-1)
```

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

## Questions to Ask the User

When implementing features, clarify:
1. **Label dimensions**: Exact size of each label?
2. **Text requirements**: Single line or multiple lines? Max characters?
3. **Font preferences**: System font or custom font file?
4. **Data source**: CSV format? Database connection? Manual input?
5. **Positioning**: Where should text appear on each label?
6. **Margins**: Safety margins around text?
7. **Batch processing**: How many sheets typically in a batch?
8. **Error handling**: What should happen if text is too long?

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
*Project Status: Initial Setup*
