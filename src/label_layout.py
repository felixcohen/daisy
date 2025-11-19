"""Label layout and positioning calculations."""

from typing import List, Tuple
from src import config


class LabelLayout:
    """Manages label positioning and text section coordinates."""

    @staticmethod
    def get_all_label_positions() -> List[Tuple[float, float]]:
        """Get positions for all 8 labels on the sheet.

        Returns:
            List of (x, y) tuples for each label's top-left corner
        """
        return [config.get_label_position(i) for i in range(1, config.TOTAL_LABELS + 1)]

    @staticmethod
    def get_text_section_bounds(
        label_x: float, label_y: float, section: str
    ) -> Tuple[float, float, float, float]:
        """Get the bounding box for a text section within a label.

        Args:
            label_x: Label's top-left x coordinate
            label_y: Label's top-left y coordinate
            section: Section name ('product_name', 'description', or 'abv_volume')

        Returns:
            Tuple of (x_start, y_start, width, height) in millimeters

        Raises:
            ValueError: If section name is invalid
        """
        if section == "product_name":
            x_start = label_x + config.PRODUCT_NAME_X_START_MM
            width = config.PRODUCT_NAME_WIDTH_MM
        elif section == "description":
            x_start = label_x + config.DESCRIPTION_X_START_MM
            width = config.DESCRIPTION_WIDTH_MM
        elif section == "abv_volume":
            x_start = label_x + config.ABV_VOLUME_X_START_MM
            width = config.ABV_VOLUME_WIDTH_MM
        else:
            raise ValueError(f"Invalid section name: {section}")

        # For now, use full label height for all sections
        # Text will be bottom-aligned within these bounds
        y_start = label_y
        height = config.LABEL_HEIGHT_MM

        return (x_start, y_start, width, height)

    @staticmethod
    def calculate_text_position(
        x_start: float,
        y_start: float,
        width: float,
        height: float,
        text_width: float,
        text_height: float,
        alignment: str = "center",
    ) -> Tuple[float, float]:
        """Calculate the position for text within a bounding box.

        Text is always bottom-aligned vertically as per requirements.

        Args:
            x_start: Bounding box left edge
            y_start: Bounding box top edge
            width: Bounding box width
            height: Bounding box height
            text_width: Actual text width
            text_height: Actual text height
            alignment: Horizontal alignment ('left', 'center', or 'right')

        Returns:
            Tuple of (x, y) coordinates for text baseline start

        Raises:
            ValueError: If alignment is invalid
        """
        # Horizontal alignment
        if alignment == "left":
            x = x_start
        elif alignment == "center":
            x = x_start + (width - text_width) / 2
        elif alignment == "right":
            x = x_start + width - text_width
        else:
            raise ValueError(f"Invalid alignment: {alignment}")

        # Vertical alignment (always bottom)
        # SVG text baseline is at the bottom of the text
        y = y_start + height

        return (x, y)
