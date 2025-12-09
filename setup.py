"""
Setup script for IaC Factory GUI
"""
from setuptools import setup, find_packages

setup(
    name="iac-factory-gui",
    version="0.1.0",
    description="Interactive GUI for IaC Factory",
    author="Manus AI",
    packages=find_packages(),
    install_requires=[
        "iac-factory",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "hypothesis>=6.92.1",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "iac-gui=backend.main:main",
        ],
    },
)
