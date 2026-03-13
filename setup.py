"""
Aethel Compiler Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="aethel",
    version="1.9.0",
    description="The World's First Formally Verified Language with Autonomous Defense - The Age of Facts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aethel Team",
    author_email="team@aethel-lang.org",
    url="https://github.com/aethel-lang/aethel-core",
    packages=find_packages(),
    install_requires=[
        "lark>=1.1.0",
        "z3-solver>=4.12.0",
        "psutil>=5.9.0",
        "anthropic>=0.18.0",
        "openai>=1.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
        'gpu': [
            'GPUtil>=1.4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'aethel=aethel.cli.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="compiler formal-verification proof-system ai-assisted",
    project_urls={
        "Documentation": "https://docs.aethel-lang.org",
        "Source": "https://github.com/aethel-lang/aethel-core",
        "Tracker": "https://github.com/aethel-lang/aethel-core/issues",
    },
)
