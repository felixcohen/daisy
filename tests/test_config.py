"""Tests for configuration module."""

import pytest
from src import config


def test_sheet_dimensions():
    """Test A3 sheet dimensions."""
    assert config.SHEET_WIDTH_MM == 420.0
    assert config.SHEET_HEIGHT_MM == 297.0


def test_label_dimensions():
    """Test label dimensions."""
    assert config.LABEL_WIDTH_MM == 155.0
    assert config.LABEL_HEIGHT_MM == 70.0
    assert config.LABEL_CORNER_RADIUS_MM == 0.7


def test_grid_layout():
    """Test grid layout configuration."""
    assert config.LABEL_COLUMNS == 2
    assert config.LABEL_ROWS == 4
    assert config.TOTAL_LABELS == 8


def test_get_label_position():
    """Test label position calculations."""
    # Test label 1 (top-left)
    x, y = config.get_label_position(1)
    assert x == 27.5
    assert y == 5.5

    # Test label 2 (top-right)
    x, y = config.get_label_position(2)
    assert x == 237.5  # 27.5 + 155 + 55
    assert y == 5.5

    # Test label 3 (second row, left)
    x, y = config.get_label_position(3)
    assert x == 27.5
    assert y == 77.5  # 5.5 + 70 + 2

    # Test label 8 (bottom-right)
    x, y = config.get_label_position(8)
    assert x == 237.5
    assert y == 221.5  # 5.5 + 70 + 2 + 70 + 2 + 70 + 2


def test_get_label_position_invalid():
    """Test label position with invalid numbers."""
    with pytest.raises(ValueError):
        config.get_label_position(0)

    with pytest.raises(ValueError):
        config.get_label_position(9)


def test_text_content_limits():
    """Test text content limit constants."""
    assert config.MAX_PRODUCT_NAME_CHARS == 40
    assert config.MAX_DESCRIPTION_CHARS == 160
    assert config.MIN_ABV_VOLUME_CHARS == 4
    assert config.MAX_ABV_VOLUME_CHARS == 6
