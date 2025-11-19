"""Text rendering and font handling for SVG path generation."""

import os
from typing import List, Tuple
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

    def text_to_path(self, text: str, x: float, y: float) -> List[str]:
        """Convert text to SVG path data.

        Args:
            text: Text string to convert
            x: X position in millimeters
            y: Y position in millimeters (baseline)

        Returns:
            List of SVG path strings
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
                        # Transform the path: scale and translate
                        # SVG coordinate system: y increases downward
                        # Font coordinate system: y increases upward
                        transformed_path = self._transform_path(path_data, current_x, y)
                        paths.append(transformed_path)

                    # Advance x position
                    current_x += glyph.width * self.scale

        return paths

    def _transform_path(self, path_data: str, x: float, y: float) -> str:
        """Transform font path to SVG coordinates.

        Args:
            path_data: SVG path commands from font
            x: X translation in mm
            y: Y translation in mm (baseline)

        Returns:
            Transformed SVG path string
        """
        # Parse and transform path commands
        # The font coordinates need to be scaled and translated
        # Font Y coordinates are flipped relative to SVG

        if not path_data:
            return ""

        # Create transform string
        # Scale, flip Y, then translate
        transform = f"translate({x}, {y}) scale({self.scale}, {-self.scale})"

        return path_data  # Will apply transform in SVG

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
