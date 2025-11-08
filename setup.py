# ============================================================================
# FILE 7: setup.py
# ============================================================================

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="airtouchpad",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Control your computer with hand gestures using AI-powered computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AirTouchPad",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "mediapipe>=0.10.0",
        "pyautogui>=0.9.54",
        "pystray>=0.19.5",
        "pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "airtouchpad=launcher:main",
        ],
    },
)

