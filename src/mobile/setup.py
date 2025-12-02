from setuptools import setup, find_packages

setup(
    name="industriverse-mobile-defense",
    version="0.1.0",
    description="Thermodynamic Mobile Surveillance Forensics Suite",
    author="Empeiria Haus",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "cryptography"
    ],
    entry_points={
        'console_scripts': [
            'mobile-defense=src.mobile.agent.core:main',
        ],
    },
)
