"""Configuration constants for Daisy label generator.

All measurements are in millimeters to match AxiDraw A3 specifications.
"""

from typing import Tuple

# Sheet dimensions (A3 Landscape)
SHEET_WIDTH_MM: float = 420.0
SHEET_HEIGHT_MM: float = 297.0

# Label dimensions
LABEL_WIDTH_MM: float = 155.0
LABEL_HEIGHT_MM: float = 70.0
LABEL_CORNER_RADIUS_MM: float = 0.7

# Grid layout
LABEL_COLUMNS: int = 2
LABEL_ROWS: int = 4
TOTAL_LABELS: int = 8

# Margins
TOP_MARGIN_MM: float = 5.5
BOTTOM_MARGIN_MM: float = 5.5
LEFT_MARGIN_MM: float = 27.5
RIGHT_MARGIN_MM: float = 27.5

# Gaps between labels
HORIZONTAL_GAP_MM: float = 55.0  # Gap between columns
VERTICAL_GAP_MM: float = 2.0  # Gap between rows

# Font settings
FONT_FILE: str = "Brandon_reg.otf"
FONT_FAMILY: str = "Brandon Grotesque Regular"
DEFAULT_FONT_SIZE_MM: float = 4.0

# Text section positions (relative to label left edge)
# Section 1: Product Name (2 lines, center aligned)
PRODUCT_NAME_X_START_MM: float = 51.0
PRODUCT_NAME_X_END_MM: float = 77.5
PRODUCT_NAME_WIDTH_MM: float = PRODUCT_NAME_X_END_MM - PRODUCT_NAME_X_START_MM

# Section 2: Product Description (multi-line, left aligned)
DESCRIPTION_X_START_MM: float = 116.0
DESCRIPTION_X_END_MM: float = 147.0
DESCRIPTION_WIDTH_MM: float = DESCRIPTION_X_END_MM - DESCRIPTION_X_START_MM

# Section 3: ABV/Volume (2-3 lines, right aligned)
ABV_VOLUME_X_START_MM: float = 148.0
ABV_VOLUME_X_END_MM: float = 155.0
ABV_VOLUME_WIDTH_MM: float = ABV_VOLUME_X_END_MM - ABV_VOLUME_X_START_MM

# Text content limits
MAX_PRODUCT_NAME_CHARS: int = 40
MAX_DESCRIPTION_CHARS: int = 160
MIN_ABV_VOLUME_CHARS: int = 4
MAX_ABV_VOLUME_CHARS: int = 6

# SVG settings
SVG_STROKE_WIDTH: float = 0.5  # Pen width in mm
SVG_STROKE_COLOR: str = "black"


def get_label_position(label_number: int) -> Tuple[float, float]:
    """Calculate the top-left corner position for a given label number (1-8).

    Args:
        label_number: Label number from 1 to 8

    Returns:
        Tuple of (x, y) coordinates in millimeters

    Raises:
        ValueError: If label_number is not between 1 and 8
    """
    if not 1 <= label_number <= TOTAL_LABELS:
        raise ValueError(f"Label number must be between 1 and {TOTAL_LABELS}")

    # Convert to 0-indexed
    index = label_number - 1

    # Calculate column (0 or 1) and row (0-3)
    col = index % LABEL_COLUMNS
    row = index // LABEL_COLUMNS

    # Calculate x position
    if col == 0:
        x = LEFT_MARGIN_MM
    else:
        x = LEFT_MARGIN_MM + LABEL_WIDTH_MM + HORIZONTAL_GAP_MM

    # Calculate y position
    y = TOP_MARGIN_MM + row * (LABEL_HEIGHT_MM + VERTICAL_GAP_MM)

    return (x, y)
