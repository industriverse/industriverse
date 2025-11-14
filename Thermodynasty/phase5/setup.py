"""
Setup script for Industriverse Diffusion Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text()
else:
    long_description = "Industriverse Diffusion Framework - Energy-based diffusion models for thermodynamic optimization"

setup(
    name="industriverse",
    version="0.5.0-alpha",
    description="Energy-based diffusion framework for thermodynamic optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Industriverse Team",
    author_email="contact@industriverse.io",
    url="https://github.com/industriverse/industriverse",
    packages=find_packages(exclude=["tests*", "docs*"]),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "prometheus-client>=0.17.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "jupyterlab>=4.0.0",
        ],
        "viz": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "idf=phase5.cli.idf:cli",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    include_package_data=True,
    zip_safe=False,
)
