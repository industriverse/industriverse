from setuptools import setup, find_packages

setup(
    name="industriverse-sdk",
    version="1.0.0",
    description="Official Python SDK for Industriverse",
    author="Industriverse",
    author_email="support@industriverse.io",
    url="https://github.com/industriverse/industriverse-python-sdk",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
