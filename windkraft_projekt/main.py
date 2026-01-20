#!/usr/bin/env python3
"""
Germany 3D - Main Entry Point
=============================

Run this script to start the interactive 3D Germany visualization.

Usage:
    python main.py

Requirements:
    - pygame
    - PyOpenGL
    - Pillow

Controls:
    - Mouse drag: Rotate view
    - Scroll: Zoom in/out
    - R: Reset view
    - S: Save screenshot
    - ESC: Exit
"""

from germany3d import Germany3DViewer


def main():
    """Start the Germany 3D viewer."""
    viewer = Germany3DViewer()
    viewer.run()


if __name__ == "__main__":
    main()
