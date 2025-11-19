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

    def __init__(
        self,
        font_path: str,
        font_size_mm: float = config.DEFAULT_FONT_SIZE_MM,
        debug: bool = False
    ):
        """Initialize the SVG generator.

        Args:
            font_path: Path to the font file
            font_size_mm: Font size in millimeters
            debug: If True, add visual guides for label boundaries
        """
        self.font_path = font_path
        self.font_size_mm = font_size_mm
        self.debug = debug
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

        # Add debug sheet boundary if debug mode
        if self.debug:
            sheet_rect = dwg.rect(
                insert=(0, 0),
                size=(config.SHEET_WIDTH_MM, config.SHEET_HEIGHT_MM),
                fill="none",
                stroke="red",
                stroke_width=0.2,
            )
            dwg.add(sheet_rect)

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

        # Add debug label boundary if debug mode
        if self.debug:
            label_rect = dwg.rect(
                insert=(label_x, label_y),
                size=(config.LABEL_WIDTH_MM, config.LABEL_HEIGHT_MM),
                rx=config.LABEL_CORNER_RADIUS_MM,
                ry=config.LABEL_CORNER_RADIUS_MM,
                fill="none",
                stroke="blue",
                stroke_width=0.2,
            )
            label_group.add(label_rect)

        # Add product name (Section 1 - center aligned, 2 lines)
        self._add_product_name(dwg, label_group, label_x, label_y, label_data)

        # Add description (Section 2 - left aligned)
        self._add_description(dwg, label_group, label_x, label_y, label_data)

        # Add ABV and volume (Section 3 - right aligned, 2 lines)
        self._add_abv_volume(dwg, label_group, label_x, label_y, label_data)

        # Add the group to the drawing
        dwg.add(label_group)

    def _add_product_name(
        self,
        dwg: svgwrite.Drawing,
        group: svgwrite.container.Group,
        label_x: float,
        label_y: float,
        label_data: LabelData,
    ) -> None:
        """Add product name to the label (Section 1).

        Args:
            dwg: SVG drawing object
            group: SVG group to add to
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
        """
        # Get section bounds
        x_start, y_start, width, height = self.layout.get_text_section_bounds(
            label_x, label_y, "product_name"
        )

        # Add debug section boundary
        if self.debug:
            section_rect = dwg.rect(
                insert=(x_start, y_start),
                size=(width, height),
                fill="none",
                stroke="green",
                stroke_width=0.1,
                opacity=0.5,
            )
            group.add(section_rect)

        # Render two lines
        lines = [label_data.product_name_line1, label_data.product_name_line2]

        # Calculate line height and positioning
        line_height = self.text_renderer.get_text_height() * 1.2

        # Start from bottom (bottom-aligned)
        baseline_y = y_start + height

        # Position each line (in reverse to place from bottom)
        for i, line in enumerate(reversed(lines)):
            line_y = baseline_y - (i * line_height)

            # Get text width for centering
            text_width = self.text_renderer.get_text_width(line)

            # Calculate centered X position
            text_x = x_start + (width - text_width) / 2

            # Add text as path
            self._add_text_as_path(dwg, group, line, text_x, line_y)

    def _add_description(
        self,
        dwg: svgwrite.Drawing,
        group: svgwrite.container.Group,
        label_x: float,
        label_y: float,
        label_data: LabelData,
    ) -> None:
        """Add product description to the label (Section 2).

        Args:
            dwg: SVG drawing object
            group: SVG group to add to
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
        """
        # Get section bounds
        x_start, y_start, width, height = self.layout.get_text_section_bounds(
            label_x, label_y, "description"
        )

        # Add debug section boundary
        if self.debug:
            section_rect = dwg.rect(
                insert=(x_start, y_start),
                size=(width, height),
                fill="none",
                stroke="purple",
                stroke_width=0.1,
                opacity=0.5,
            )
            group.add(section_rect)

        # Bottom-aligned, left-aligned
        text_y = y_start + height

        # Add text as path
        self._add_text_as_path(dwg, group, label_data.description, x_start, text_y)

    def _add_abv_volume(
        self,
        dwg: svgwrite.Drawing,
        group: svgwrite.container.Group,
        label_x: float,
        label_y: float,
        label_data: LabelData,
    ) -> None:
        """Add ABV and volume to the label (Section 3).

        Args:
            dwg: SVG drawing object
            group: SVG group to add to
            label_x: Label X position
            label_y: Label Y position
            label_data: Label data
        """
        # Get section bounds
        x_start, y_start, width, height = self.layout.get_text_section_bounds(
            label_x, label_y, "abv_volume"
        )

        # Add debug section boundary
        if self.debug:
            section_rect = dwg.rect(
                insert=(x_start, y_start),
                size=(width, height),
                fill="none",
                stroke="orange",
                stroke_width=0.1,
                opacity=0.5,
            )
            group.add(section_rect)

        # Render two lines (ABV and Volume)
        lines = [label_data.abv, label_data.volume]

        # Calculate line height
        line_height = self.text_renderer.get_text_height() * 1.2

        # Start from bottom (bottom-aligned)
        baseline_y = y_start + height

        # Position each line (right-aligned, from bottom)
        for i, line in enumerate(reversed(lines)):
            line_y = baseline_y - (i * line_height)

            # Get text width for right alignment
            text_width = self.text_renderer.get_text_width(line)

            # Calculate right-aligned X position
            text_x = x_start + width - text_width

            # Add text as path
            self._add_text_as_path(dwg, group, line, text_x, line_y)

    def _add_text_as_path(
        self, dwg: svgwrite.Drawing, group: svgwrite.container.Group, text: str, x: float, y: float
    ) -> None:
        """Add text as SVG path (for accurate plotting).

        Args:
            dwg: SVG drawing object
            group: SVG group to add to
            text: Text to render
            x: X position
            y: Y position (baseline)
        """
        # Get SVG path data for the text
        path_dicts = self.text_renderer.text_to_path(text, x, y)

        # Add each glyph path to the group
        for path_dict in path_dicts:
            if path_dict and path_dict.get('d'):
                path_element = dwg.path(
                    d=path_dict['d'],
                    fill="none",
                    stroke=config.SVG_STROKE_COLOR,
                    stroke_width=config.SVG_STROKE_WIDTH,
                    transform=path_dict.get('transform', '')
                )
                group.add(path_element)
