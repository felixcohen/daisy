"""Text rendering and font handling for SVG path generation."""

import os
from typing import List, Tuple, Dict
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from src import config


class TextRenderer:
    """Handles font loading and text-to-SVG-path conversion."""

    def __init__(self, font_path: str, font_size_mm: float = config.DEFAULT_FONT_SIZE_MM):
        """Initialize the text renderer with a font file.

        Args:
            font_path: Path to the OTF/TTF font file
            font_size_mm: Font size in millimeters

        Raises:
            FileNotFoundError: If font file doesn't exist
            Exception: If font file cannot be loaded
        """
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")

        self.font_path = font_path
        self.font_size_mm = font_size_mm

        try:
            self.font = TTFont(font_path)
        except Exception as e:
            raise Exception(f"Failed to load font {font_path}: {e}")

        # Get font metrics
        self.units_per_em = self.font["head"].unitsPerEm
        self.scale = self.font_size_mm / self.units_per_em

        # Get glyph set for rendering
        self.glyph_set = self.font.getGlyphSet()

        # Get font metrics for vertical positioning
        if "OS/2" in self.font:
            self.ascent = self.font["OS/2"].sTypoAscender
            self.descent = self.font["OS/2"].sTypoDescender
        else:
            self.ascent = self.font["hhea"].ascent
            self.descent = self.font["hhea"].descent

    def get_text_width(self, text: str) -> float:
        """Calculate the width of text in millimeters.

        Args:
            text: Text string to measure

        Returns:
            Width in millimeters
        """
        width = 0
        cmap = self.font.getBestCmap()

        for char in text:
            if ord(char) in cmap:
                glyph_name = cmap[ord(char)]
                if glyph_name in self.glyph_set:
                    glyph = self.glyph_set[glyph_name]
                    width += glyph.width

        return width * self.scale

    def get_text_height(self) -> float:
        """Get the height of text in millimeters (ascent + descent).

        Returns:
            Height in millimeters
        """
        return (self.ascent - self.descent) * self.scale

    def text_to_path(self, text: str, x: float, y: float) -> List[Dict[str, str]]:
        """Convert text to SVG path data with transforms.

        Args:
            text: Text string to convert
            x: X position in millimeters
            y: Y position in millimeters (baseline)

        Returns:
            List of dicts with 'd' (path data) and 'transform' keys
        """
        paths = []
        current_x = x
        cmap = self.font.getBestCmap()

        for char in text:
            if ord(char) in cmap:
                glyph_name = cmap[ord(char)]
                if glyph_name in self.glyph_set:
                    glyph = self.glyph_set[glyph_name]

                    # Create SVG path pen
                    pen = SVGPathPen(self.glyph_set)
                    glyph.draw(pen)

                    # Get the path data
                    path_data = pen.getCommands()

                    if path_data:
                        # Create transform: translate to position, scale, and flip Y
                        # Font coordinate system has Y increasing upward
                        # SVG has Y increasing downward
                        transform = f"translate({current_x}, {y}) scale({self.scale}, {-self.scale})"

                        paths.append({
                            'd': path_data,
                            'transform': transform
                        })

                    # Advance x position
                    current_x += glyph.width * self.scale

        return paths

    def render_multiline_text(
        self, lines: List[str], x: float, y: float, line_spacing: float = 1.2
    ) -> List[Tuple[str, float, float]]:
        """Render multiple lines of text.

        Args:
            lines: List of text lines
            x: X position in millimeters
            y: Y position in millimeters (baseline of first line)
            line_spacing: Line spacing multiplier (default 1.2)

        Returns:
            List of tuples (text, x, y) for each line
        """
        result = []
        line_height = self.get_text_height() * line_spacing
        current_y = y

        for line in lines:
            result.append((line, x, current_y))
            current_y += line_height

        return result
