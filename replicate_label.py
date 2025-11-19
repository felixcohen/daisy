#!/usr/bin/env python3
"""
Replicate a single label SVG into an A3 sheet with 8 labels.

Takes an existing SVG label design and creates 8 copies arranged in a 2×4 grid
on an A3 sheet according to the Daisy label specifications.
"""

import sys
import os
import xml.etree.ElementTree as ET
from src import config


def replicate_label(input_svg_path: str, output_svg_path: str) -> None:
    """Replicate a single label SVG into 8 labels on an A3 sheet.

    Args:
        input_svg_path: Path to the input SVG file (single label)
        output_svg_path: Path to save the output SVG file (8 labels on A3)
    """
    if not os.path.exists(input_svg_path):
        raise FileNotFoundError(f"Input SVG not found: {input_svg_path}")

    # Parse the input SVG
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Create new A3 SVG document
    # Register the SVG namespace (this will add xmlns automatically)
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    # Create root SVG element for A3 sheet
    # Don't include xmlns in attributes since register_namespace handles it
    a3_svg = ET.Element(
        '{http://www.w3.org/2000/svg}svg',
        {
            'width': f'{config.SHEET_WIDTH_MM}mm',
            'height': f'{config.SHEET_HEIGHT_MM}mm',
            'viewBox': f'0 0 {config.SHEET_WIDTH_MM} {config.SHEET_HEIGHT_MM}',
        }
    )

    # Get all label positions
    label_positions = [config.get_label_position(i) for i in range(1, 9)]

    # Create a group for each label
    for label_num, (label_x, label_y) in enumerate(label_positions, start=1):
        # Create a group for this label
        label_group = ET.SubElement(
            a3_svg,
            '{http://www.w3.org/2000/svg}g',
            {
                'id': f'label_{label_num}',
                'transform': f'translate({label_x}, {label_y})',
            }
        )

        # Clone all elements from the input SVG into this group
        for child in root:
            # Skip metadata, defs that aren't needed
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag_name in ('metadata', 'sodipodi:namedview', 'defs', 'title', 'desc'):
                continue

            # Clone the element (without SVG root attributes)
            cloned = _clone_element_clean(child)
            if cloned is not None:
                label_group.append(cloned)

    # Write the output SVG
    output_tree = ET.ElementTree(a3_svg)
    output_tree.write(output_svg_path, encoding='utf-8', xml_declaration=True)

    print(f"✓ Created {output_svg_path}")
    print(f"  Sheet: {config.SHEET_WIDTH_MM}mm × {config.SHEET_HEIGHT_MM}mm")
    print(f"  Labels: 8 (2 columns × 4 rows)")
    print(f"  Label size: {config.LABEL_WIDTH_MM}mm × {config.LABEL_HEIGHT_MM}mm")


def _clone_element_clean(element):
    """Recursively clone an XML element and its children, filtering out SVG root attributes.

    Args:
        element: XML element to clone

    Returns:
        Cloned element
    """
    # Create new element with same tag
    # Filter out xmlns and other namespace declarations from attributes
    clean_attribs = {}
    for key, value in element.attrib.items():
        # Skip xmlns attributes and other namespace declarations
        if key.startswith('{') or key == 'xmlns' or key.startswith('xmlns:'):
            continue
        clean_attribs[key] = value

    cloned = ET.Element(element.tag, clean_attribs)

    # Copy text and tail
    cloned.text = element.text
    cloned.tail = element.tail

    # Recursively clone children
    for child in element:
        cloned_child = _clone_element_clean(child)
        if cloned_child is not None:
            cloned.append(cloned_child)

    return cloned


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
