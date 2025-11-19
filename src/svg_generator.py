"""SVG generation for AxiDraw plotter labels."""

from typing import List, Tuple
import svgwrite
from src import config
from src.label_layout import LabelLayout
from src.text_renderer import TextRenderer


class LabelData:
    """Data for a single label."""

    def __init__(
        self,
        product_name_line1: str,
        product_name_line2: str,
        description: str,
        abv: str,
        volume: str,
    ):
        """Initialize label data.

        Args:
            product_name_line1: First line of product name
            product_name_line2: Second line of product name
            description: Product description
            abv: ABV percentage
            volume: Volume information
        """
        self.product_name_line1 = product_name_line1
        self.product_name_line2 = product_name_line2
        self.description = description
        self.abv = abv
        self.volume = volume


class SVGGenerator:
    """Generates SVG files for AxiDraw plotter."""

    def __init__(self, font_path: str, font_size_mm: float = config.DEFAULT_FONT_SIZE_MM):
        """Initialize the SVG generator.

        Args:
            font_path: Path to the font file
            font_size_mm: Font size in millimeters
        """
        self.font_path = font_path
        self.font_size_mm = font_size_mm
        self.text_renderer = TextRenderer(font_path, font_size_mm)
        self.layout = LabelLayout()

    def generate_sheet(self, label_data: LabelData, output_path: str) -> None:
        """Generate an A3 sheet with 8 identical labels.

        Args:
            label_data: Data for the labels
            output_path: Path to save the SVG file
        """
        # Create SVG drawing
        dwg = svgwrite.Drawing(
            output_path,
            size=(f"{config.SHEET_WIDTH_MM}mm", f"{config.SHEET_HEIGHT_MM}mm"),
            viewBox=f"0 0 {config.SHEET_WIDTH_MM} {config.SHEET_HEIGHT_MM}",
        )

        # Get all label positions
        label_positions = self.layout.get_all_label_positions()

        # Generate each label
        for label_num, (label_x, label_y) in enumerate(label_positions, start=1):
            self._add_label(dwg, label_x, label_y, label_data, label_num)

        # Save the SVG
        dwg.save()

    def _add_label(
        self,
        dwg: svgwrite.Drawing,
        label_x: float,
        label_y: float,
        label_data: LabelData,
        label_num: int,
    ) -> None:
        """Add a single label to the SVG.

        Args:
            dwg: SVG drawing object
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
            label_num: Label number (for grouping)
        """
        # Create a group for this label
        label_group = dwg.g(id=f"label_{label_num}")

        # Add product name (Section 1 - center aligned, 2 lines)
        self._add_product_name(label_group, label_x, label_y, label_data)

        # Add description (Section 2 - left aligned)
        self._add_description(label_group, label_x, label_y, label_data)

        # Add ABV and volume (Section 3 - right aligned, 2 lines)
        self._add_abv_volume(label_group, label_x, label_y, label_data)

        # Add the group to the drawing
        dwg.add(label_group)

    def _add_product_name(
        self,
        group: svgwrite.container.Group,
        label_x: float,
        label_y: float,
        label_data: LabelData,
    ) -> None:
        """Add product name to the label (Section 1).

        Args:
            group: SVG group to add to
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
        """
        # Get section bounds
        x_start, y_start, width, height = self.layout.get_text_section_bounds(
            label_x, label_y, "product_name"
        )

        # Render two lines
        lines = [label_data.product_name_line1, label_data.product_name_line2]

        # Calculate line height and total text block height
        line_height = self.text_renderer.get_text_height() * 1.2
        total_height = line_height * 2

        # Start from bottom (bottom-aligned)
        baseline_y = y_start + height

        # Position each line
        for i, line in enumerate(reversed(lines)):  # Reverse to start from bottom
            line_y = baseline_y - (i * line_height)

            # Get text width for centering
            text_width = self.text_renderer.get_text_width(line)

            # Calculate centered X position
            text_x = x_start + (width - text_width) / 2

            # Add text as path
            self._add_text_as_path(group, line, text_x, line_y)

    def _add_description(
        self,
        group: svgwrite.container.Group,
        label_x: float,
        label_y: float,
        label_data: LabelData,
    ) -> None:
        """Add product description to the label (Section 2).

        Args:
            group: SVG group to add to
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
        """
        # Get section bounds
        x_start, y_start, width, height = self.layout.get_text_section_bounds(
            label_x, label_y, "description"
        )

        # For now, render as single line (can add line wrapping later if needed)
        # Bottom-aligned, left-aligned
        text_y = y_start + height

        # Add text as path
        self._add_text_as_path(group, label_data.description, x_start, text_y)

    def _add_abv_volume(
        self,
        group: svgwrite.container.Group,
        label_x: float,
        label_y: float,
        label_data: LabelData,
    ) -> None:
        """Add ABV and volume to the label (Section 3).

        Args:
            group: SVG group to add to
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
        """
        # Get section bounds
        x_start, y_start, width, height = self.layout.get_text_section_bounds(
            label_x, label_y, "abv_volume"
        )

        # Render two lines (ABV and Volume)
        lines = [label_data.abv, label_data.volume]

        # Calculate line height
        line_height = self.text_renderer.get_text_height() * 1.2

        # Start from bottom (bottom-aligned)
        baseline_y = y_start + height

        # Position each line (right-aligned)
        for i, line in enumerate(reversed(lines)):  # Reverse to start from bottom
            line_y = baseline_y - (i * line_height)

            # Get text width for right alignment
            text_width = self.text_renderer.get_text_width(line)

            # Calculate right-aligned X position
            text_x = x_start + width - text_width

            # Add text as path
            self._add_text_as_path(group, line, text_x, line_y)

    def _add_text_as_path(
        self, group: svgwrite.container.Group, text: str, x: float, y: float
    ) -> None:
        """Add text as SVG path (for accurate plotting).

        Args:
            group: SVG group to add to
            text: Text to render
            x: X position
            y: Y position (baseline)
        """
        # Get SVG path data for the text
        paths = self.text_renderer.text_to_path(text, x, y)

        # Add each glyph path to the group
        for path_data in paths:
            if path_data:
                path_element = group.add(
                    group.path(
                        d=path_data,
                        fill="none",
                        stroke=config.SVG_STROKE_COLOR,
                        stroke_width=config.SVG_STROKE_WIDTH,
                    )
                )
