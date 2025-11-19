"""Tests for label layout module."""

import pytest
from src.label_layout import LabelLayout


def test_get_all_label_positions():
    """Test getting all label positions."""
    layout = LabelLayout()
    positions = layout.get_all_label_positions()

    assert len(positions) == 8
    assert all(isinstance(pos, tuple) for pos in positions)
    assert all(len(pos) == 2 for pos in positions)


def test_get_text_section_bounds():
    """Test getting text section bounds."""
    layout = LabelLayout()

    label_x, label_y = 27.5, 5.5

    # Product name section
    x, y, w, h = layout.get_text_section_bounds(label_x, label_y, "product_name")
    assert x == label_x + 51.0
    assert w == 26.5  # 77.5 - 51.0

    # Description section
    x, y, w, h = layout.get_text_section_bounds(label_x, label_y, "description")
    assert x == label_x + 116.0
    assert w == 31.0  # 147.0 - 116.0

    # ABV/Volume section
    x, y, w, h = layout.get_text_section_bounds(label_x, label_y, "abv_volume")
    assert x == label_x + 148.0
    assert w == 7.0  # 155.0 - 148.0


def test_get_text_section_bounds_invalid():
    """Test getting text section bounds with invalid section name."""
    layout = LabelLayout()

    with pytest.raises(ValueError):
        layout.get_text_section_bounds(0, 0, "invalid_section")


def test_calculate_text_position_center():
    """Test text position calculation with center alignment."""
    layout = LabelLayout()

    x, y = layout.calculate_text_position(
        x_start=100,
        y_start=50,
        width=50,
        height=20,
        text_width=20,
        text_height=10,
        alignment="center",
    )

    assert x == 115  # 100 + (50 - 20) / 2
    assert y == 70  # 50 + 20 (bottom-aligned)


def test_calculate_text_position_left():
    """Test text position calculation with left alignment."""
    layout = LabelLayout()

    x, y = layout.calculate_text_position(
        x_start=100,
        y_start=50,
        width=50,
        height=20,
        text_width=20,
        text_height=10,
        alignment="left",
    )

    assert x == 100
    assert y == 70


def test_calculate_text_position_right():
    """Test text position calculation with right alignment."""
    layout = LabelLayout()

    x, y = layout.calculate_text_position(
        x_start=100,
        y_start=50,
        width=50,
        height=20,
        text_width=20,
        text_height=10,
        alignment="right",
    )

    assert x == 130  # 100 + 50 - 20
    assert y == 70
