#!/usr/bin/env python3
"""
Replicate a single label SVG into an A3 sheet with 8 labels.

Takes an existing SVG label design and creates 8 copies arranged in a 2×4 grid
on an A3 sheet according to the Daisy label specifications.
"""

import sys
import os
import xml.etree.ElementTree as ET
import svgwrite
from src import config


def replicate_label(input_svg_path: str, output_svg_path: str) -> None:
    """Replicate a single label SVG into 8 labels on an A3 sheet.

    Args:
        input_svg_path: Path to the input SVG file (single label)
        output_svg_path: Path to save the output SVG file (8 labels on A3)
    """
    if not os.path.exists(input_svg_path):
        raise FileNotFoundError(f"Input SVG not found: {input_svg_path}")

    # Parse the input SVG to extract content
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Extract viewBox and dimensions from input
    input_viewbox = root.get('viewBox', '0 0 100 100')
    viewbox_parts = input_viewbox.split()
    if len(viewbox_parts) == 4:
        input_width = float(viewbox_parts[2])
        input_height = float(viewbox_parts[3])
    else:
        # Fallback to width/height attributes
        input_width = float(root.get('width', '100').replace('px', ''))
        input_height = float(root.get('height', '100').replace('px', ''))

    # Create new A3 SVG using svgwrite
    dwg = svgwrite.Drawing(
        output_svg_path,
        size=(f'{config.SHEET_WIDTH_MM}mm', f'{config.SHEET_HEIGHT_MM}mm'),
        viewBox=f'0 0 {config.SHEET_WIDTH_MM} {config.SHEET_HEIGHT_MM}',
        profile='tiny',  # Disable strict validation
        debug=False
    )

    # Get all label positions
    label_positions = [config.get_label_position(i) for i in range(1, 9)]

    # Calculate scale factor to fit label into 155mm x 70mm
    # We want the input SVG to fit within the label dimensions
    scale_x = config.LABEL_WIDTH_MM / input_width
    scale_y = config.LABEL_HEIGHT_MM / input_height
    # Use the smaller scale to ensure it fits
    scale = min(scale_x, scale_y)

    # Create 8 copies of the label
    for label_num, (label_x, label_y) in enumerate(label_positions, start=1):
        # Create a group for this label
        label_group = dwg.g(id=f'label_{label_num}')

        # Apply transform to position and scale the label
        transform = f'translate({label_x}, {label_y}) scale({scale})'
        label_group['transform'] = transform

        # Extract and add all paths and shapes from the input SVG
        _add_svg_content(root, label_group, dwg)

        # Add the group to the drawing
        dwg.add(label_group)

    # Save the SVG
    dwg.save()

    print(f"✓ Created {output_svg_path}")
    print(f"  Sheet: {config.SHEET_WIDTH_MM}mm × {config.SHEET_HEIGHT_MM}mm")
    print(f"  Labels: 8 (2 columns × 4 rows)")
    print(f"  Label size: {config.LABEL_WIDTH_MM}mm × {config.LABEL_HEIGHT_MM}mm")
    print(f"  Input size: {input_width} × {input_height}")
    print(f"  Scale factor: {scale:.4f}")


def _add_svg_content(element, group, dwg):
    """Recursively add SVG content from ElementTree to svgwrite group.

    Args:
        element: ElementTree element to extract content from
        group: svgwrite group to add content to
        dwg: svgwrite Drawing object
    """
    # Get the tag name without namespace
    tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag

    # Skip SVG root and metadata elements
    if tag in ('svg', 'metadata', 'title', 'desc', 'defs'):
        # But process children of svg and defs
        if tag in ('svg', 'defs'):
            for child in element:
                _add_svg_content(child, group, dwg)
        return

    # Handle groups
    if tag == 'g':
        # Create a nested group
        sub_group = dwg.g()
        # Copy attributes (filter out empty values)
        for key, value in element.attrib.items():
            attr_name = key.split('}')[-1] if '}' in key else key
            if attr_name not in ('xmlns', 'xmlns:xlink') and not key.startswith('{') and value:
                sub_group[attr_name] = value
        # Process children
        for child in element:
            _add_svg_content(child, sub_group, dwg)
        group.add(sub_group)
        return

    # Handle paths
    if tag == 'path':
        # Only add paths with valid 'd' attribute
        d_attr = element.get('d', '').strip()
        if d_attr:  # Only add if d attribute has content after stripping
            # Create path with 'd' attribute
            path_elem = dwg.path(d=d_attr)
            # Copy other attributes
            for key, value in element.attrib.items():
                attr_name = key.split('}')[-1] if '}' in key else key
                # Skip 'd' (already set), xmlns, and empty values
                if attr_name == 'd':
                    continue
                value_stripped = value.strip() if isinstance(value, str) else value
                if attr_name not in ('xmlns', 'xmlns:xlink') and not key.startswith('{') and value_stripped:
                    path_elem[attr_name] = value
            group.add(path_elem)
        return

    # Handle other shapes (rect, circle, ellipse, line, polyline, polygon)
    if tag in ('rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text'):
        # Create the appropriate element
        if tag == 'rect':
            elem = dwg.rect(insert=(0, 0), size=(0, 0))
        elif tag == 'circle':
            elem = dwg.circle(center=(0, 0), r=0)
        elif tag == 'ellipse':
            elem = dwg.ellipse(center=(0, 0), r=(0, 0))
        elif tag == 'line':
            elem = dwg.line(start=(0, 0), end=(0, 0))
        elif tag == 'polyline':
            elem = dwg.polyline(points=[])
        elif tag == 'polygon':
            elem = dwg.polygon(points=[])
        elif tag == 'text':
            elem = dwg.text('', insert=(0, 0))
        else:
            return

        # Copy all attributes (filter out empty values)
        for key, value in element.attrib.items():
            attr_name = key.split('}')[-1] if '}' in key else key
            if attr_name not in ('xmlns', 'xmlns:xlink') and not key.startswith('{') and value:
                elem[attr_name] = value

        # For text elements, also copy the text content
        if tag == 'text' and element.text:
            elem.text = element.text

        group.add(elem)
        return

    # For any other elements, recursively process children
    for child in element:
        _add_svg_content(child, group, dwg)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python replicate_label.py <input.svg> [output.svg]")
        print()
        print("Examples:")
        print("  python replicate_label.py beeswax.svg")
        print("  python replicate_label.py beeswax.svg beeswax-sheet.svg")
        sys.exit(1)

    input_svg = sys.argv[1]

    # Generate output filename if not provided
    if len(sys.argv) >= 3:
        output_svg = sys.argv[2]
    else:
        base_name = os.path.splitext(os.path.basename(input_svg))[0]
        output_svg = f"{base_name}-sheet.svg"

    try:
        replicate_label(input_svg, output_svg)
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
