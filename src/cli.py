"""Command-line interface for Daisy label generator."""

import os
import sys
import click
from src import config
from src.svg_generator import SVGGenerator, LabelData


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_product_name(product_name: str) -> tuple[str, str]:
    """Validate and split product name.

    Args:
        product_name: Product name with pipe separator

    Returns:
        Tuple of (line1, line2)

    Raises:
        ValidationError: If validation fails
    """
    # Check length
    if len(product_name) > config.MAX_PRODUCT_NAME_CHARS:
        raise ValidationError(
            f"Product name exceeds maximum length: "
            f"{len(product_name)} characters (max: {config.MAX_PRODUCT_NAME_CHARS})"
        )

    # Check for pipe separator
    if "|" not in product_name:
        raise ValidationError(
            "Product name must include pipe '|' character to specify line break. "
            'Example: "ESPRESSO|MARTINI"'
        )

    # Split on pipe
    parts = product_name.split("|")
    if len(parts) != 2:
        raise ValidationError(
            f"Product name must have exactly one pipe '|' separator. Found {len(parts) - 1}"
        )

    line1, line2 = parts
    if not line1.strip() or not line2.strip():
        raise ValidationError("Both lines of product name must contain text")

    return (line1.strip(), line2.strip())


def validate_description(description: str) -> str:
    """Validate description text.

    Args:
        description: Product description

    Returns:
        Validated description

    Raises:
        ValidationError: If validation fails
    """
    if len(description) > config.MAX_DESCRIPTION_CHARS:
        raise ValidationError(
            f"Description exceeds maximum length: "
            f"{len(description)} characters (max: {config.MAX_DESCRIPTION_CHARS})"
        )

    return description


def validate_abv_volume(text: str, field_name: str) -> str:
    """Validate ABV or volume text.

    Args:
        text: ABV or volume text
        field_name: Name of the field for error messages

    Returns:
        Validated text

    Raises:
        ValidationError: If validation fails
    """
    length = len(text)
    if length < config.MIN_ABV_VOLUME_CHARS or length > config.MAX_ABV_VOLUME_CHARS:
        raise ValidationError(
            f"{field_name} must be between {config.MIN_ABV_VOLUME_CHARS} "
            f"and {config.MAX_ABV_VOLUME_CHARS} characters. Got {length} characters."
        )

    return text


def generate_output_filename(product_name: str) -> str:
    """Generate output filename from product name.

    Args:
        product_name: Product name (with pipe separator)

    Returns:
        Generated filename (e.g., "espresso-martini.svg")
    """
    # Remove pipe and convert to lowercase
    name = product_name.replace("|", "-")
    # Replace spaces with hyphens
    name = name.replace(" ", "-")
    # Remove any non-alphanumeric characters except hyphens
    name = "".join(c for c in name if c.isalnum() or c == "-")
    # Convert to lowercase
    name = name.lower()
    # Remove multiple consecutive hyphens
    while "--" in name:
        name = name.replace("--", "-")
    # Remove leading/trailing hyphens
    name = name.strip("-")

    return f"{name}.svg"


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Daisy - SVG generator for AxiDraw A3 plotter label printing."""
    pass


@cli.command()
@click.option(
    "--product-name",
    required=True,
    help='Product name with pipe separator for line break (e.g., "ESPRESSO|MARTINI")',
)
@click.option(
    "--description",
    required=True,
    help="Product description text (max 160 characters)",
)
@click.option(
    "--abv",
    required=True,
    help='ABV percentage (4-6 characters, e.g., "12%")',
)
@click.option(
    "--volume",
    required=True,
    help='Volume information (4-6 characters, e.g., "200ml")',
)
@click.option(
    "--output",
    default=None,
    help="Custom output SVG file path (auto-generated if not specified)",
)
@click.option(
    "--font-size",
    default=config.DEFAULT_FONT_SIZE_MM,
    type=float,
    help=f"Font size in millimeters (default: {config.DEFAULT_FONT_SIZE_MM}mm)",
)
@click.option(
    "--preview",
    is_flag=True,
    help="Preview mode: validate inputs without generating file",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Debug mode: add visual guides showing label and section boundaries",
)
def generate(product_name, description, abv, volume, output, font_size, preview, debug):
    """Generate SVG file with 8 identical labels."""

    try:
        # Validate inputs
        click.echo("Validating inputs...")
        line1, line2 = validate_product_name(product_name)
        description = validate_description(description)
        abv = validate_abv_volume(abv, "ABV")
        volume = validate_abv_volume(volume, "Volume")

        click.echo("✓ All inputs valid")

        # Show what will be generated
        click.echo("\nLabel content:")
        click.echo(f"  Product name: {line1}")
        click.echo(f"                {line2}")
        click.echo(f"  Description:  {description}")
        click.echo(f"  ABV:          {abv}")
        click.echo(f"  Volume:       {volume}")
        click.echo(f"  Font size:    {font_size}mm")

        if preview:
            click.echo("\n✓ Preview mode: validation successful")
            click.echo("  No file generated (use without --preview to generate)")
            return

        # Determine output path
        if output is None:
            output = generate_output_filename(product_name)

        click.echo(f"\nGenerating SVG: {output}")

        # Find font file
        font_path = config.FONT_FILE
        if not os.path.exists(font_path):
            # Try in current directory
            if not os.path.exists(font_path):
                raise FileNotFoundError(
                    f"Font file not found: {config.FONT_FILE}. "
                    "Please ensure Brandon_reg.otf is in the current directory."
                )

        # Create label data
        label_data = LabelData(
            product_name_line1=line1,
            product_name_line2=line2,
            description=description,
            abv=abv,
            volume=volume,
        )

        # Generate SVG
        generator = SVGGenerator(font_path, font_size, debug=debug)
        generator.generate_sheet(label_data, output)

        click.echo(f"✓ SVG generated successfully: {output}")
        click.echo(f"  Sheet size: {config.SHEET_WIDTH_MM}mm × {config.SHEET_HEIGHT_MM}mm")
        click.echo(f"  Labels: 8 (all identical)")
        if debug:
            click.echo(f"  Debug mode: Visual guides included")

    except ValidationError as e:
        click.echo(f"\n✗ Validation Error: {e}", err=True)
        click.echo("\nPlease provide updated text and try again.", err=True)
        sys.exit(1)

    except FileNotFoundError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo(f"\n✗ Unexpected error: {e}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
