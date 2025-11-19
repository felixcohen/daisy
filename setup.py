"""Setup script for Daisy label generator."""

from setuptools import setup, find_packages

setup(
    name="daisy",
    version="0.1.0",
    description="SVG generator for AxiDraw A3 plotter label printing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Daisy Drinks",
    author_email="hello@daisydrinks.com",
    url="https://daisydrinks.com",
    packages=find_packages(),
    install_requires=[
        "svgwrite>=1.4.3",
        "fonttools>=4.47.0",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black>=23.12.0",
            "pylint>=3.0.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "daisy=src.cli:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
