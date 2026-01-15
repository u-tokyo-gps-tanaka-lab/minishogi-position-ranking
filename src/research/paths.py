"""Path utilities for research scripts."""

import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "research")


def data_path(filename: str) -> str:
    """Get path to a file in the data directory."""
    return os.path.join(DATA_DIR, filename)


def output_path(filename: str) -> str:
    """Get path to a file in the research output directory."""
    return os.path.join(OUTPUT_DIR, filename)
