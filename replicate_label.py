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

        # Extract and add all paths and shapes from the input SVG
        # Pass transformation parameters to apply directly to coordinates
        _add_svg_content(root, label_group, dwg, scale, label_x, label_y)

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


def _transform_path_data(path_data: str, scale: float, offset_x: float, offset_y: float) -> str:
    """Transform SVG path data by applying scale and offset to coordinates.

    Args:
        path_data: SVG path 'd' attribute string
        scale: Scale factor to apply
        offset_x: X offset to add after scaling
        offset_y: Y offset to add after scaling

    Returns:
        Transformed path data string
    """
    import re

    # Pattern to match numbers (including negative and decimals)
    number_pattern = r'-?\d+\.?\d*'

    # Split path into commands and coordinates
    # Commands are letters, coordinates are numbers
    tokens = re.findall(r'[a-zA-Z]|' + number_pattern, path_data)

    result = []
    i = 0
    current_command = None

    while i < len(tokens):
        token = tokens[i]

        # Check if it's a command (letter)
        if token.isalpha():
            current_command = token
            result.append(token)
            i += 1
        else:
            # It's a number - part of coordinates
            # We need to know which command to determine how to handle coordinates
            if current_command is None:
                result.append(token)
                i += 1
                continue

            # For absolute commands (uppercase), transform coordinates
            # For relative commands (lowercase), only scale (no offset)
            is_absolute = current_command.isupper()

            # Commands that take x,y pairs
            if current_command.upper() in ('M', 'L', 'T'):
                # Single x,y pair
                if i + 1 < len(tokens):
                    x = float(tokens[i])
                    y = float(tokens[i + 1])
                    if is_absolute:
                        x = x * scale + offset_x
                        y = y * scale + offset_y
                    else:
                        x = x * scale
                        y = y * scale
                    result.append(f'{x:.6f}')
                    result.append(f'{y:.6f}')
                    i += 2
                else:
                    result.append(token)
                    i += 1

            # Commands that take multiple x,y pairs (cubic bezier)
            elif current_command.upper() == 'C':
                # Three x,y pairs
                if i + 5 < len(tokens):
                    coords = []
                    for j in range(6):
                        coords.append(float(tokens[i + j]))

                    if is_absolute:
                        for j in range(0, 6, 2):
                            coords[j] = coords[j] * scale + offset_x
                            coords[j + 1] = coords[j + 1] * scale + offset_y
                    else:
                        for j in range(6):
                            coords[j] = coords[j] * scale

                    for coord in coords:
                        result.append(f'{coord:.6f}')
                    i += 6
                else:
                    result.append(token)
                    i += 1

            # Horizontal line (only x coordinate)
            elif current_command.upper() == 'H':
                x = float(tokens[i])
                if is_absolute:
                    x = x * scale + offset_x
                else:
                    x = x * scale
                result.append(f'{x:.6f}')
                i += 1

            # Vertical line (only y coordinate)
            elif current_command.upper() == 'V':
                y = float(tokens[i])
                if is_absolute:
                    y = y * scale + offset_y
                else:
                    y = y * scale
                result.append(f'{y:.6f}')
                i += 1

            # Z/z (close path - no coordinates)
            elif current_command.upper() == 'Z':
                i += 1

            # For any other commands, just copy the number
            else:
                result.append(token)
                i += 1

    return ' '.join(result)


def _add_svg_content(element, group, dwg, scale=1.0, offset_x=0.0, offset_y=0.0):
    """Recursively add SVG content from ElementTree to svgwrite group.

    Args:
        element: ElementTree element to extract content from
        group: svgwrite group to add content to
        dwg: svgwrite Drawing object
        scale: Scale factor to apply to coordinates (default 1.0)
        offset_x: X offset to add to coordinates (default 0.0)
        offset_y: Y offset to add to coordinates (default 0.0)
    """
    # Get the tag name without namespace
    tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag

    # Skip SVG root and metadata elements
    if tag in ('svg', 'metadata', 'title', 'desc', 'defs'):
        # But process children of svg and defs
        if tag in ('svg', 'defs'):
            for child in element:
                _add_svg_content(child, group, dwg, scale, offset_x, offset_y)
        return

    # Handle groups
    if tag == 'g':
        # Create a nested group
        sub_group = dwg.g()
        # Copy attributes (filter out empty values and transform)
        for key, value in element.attrib.items():
            attr_name = key.split('}')[-1] if '}' in key else key
            # Skip transforms - we're applying them to coordinates directly
            if attr_name == 'transform':
                continue
            if attr_name not in ('xmlns', 'xmlns:xlink') and not key.startswith('{') and value:
                sub_group[attr_name] = value
        # Process children
        for child in element:
            _add_svg_content(child, sub_group, dwg, scale, offset_x, offset_y)
        group.add(sub_group)
        return

    # Handle paths
    if tag == 'path':
        # Only add paths with valid 'd' attribute
        d_attr = element.get('d', '').strip()
        if d_attr:  # Only add if d attribute has content after stripping
            # Transform the path data
            transformed_d = _transform_path_data(d_attr, scale, offset_x, offset_y)
            # Create path with transformed 'd' attribute
            path_elem = dwg.path(d=transformed_d)
            # Copy other attributes
            for key, value in element.attrib.items():
                attr_name = key.split('}')[-1] if '}' in key else key
                # Skip 'd' (already set), transform, xmlns, and empty values
                if attr_name in ('d', 'transform'):
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
        _add_svg_content(child, group, dwg, scale, offset_x, offset_y)


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
