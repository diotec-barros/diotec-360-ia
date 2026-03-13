# Installation Guide

## Overview

Aethel is a financial programming language with mathematical proof capabilities. This guide will help you install Aethel on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install aethel
```

### Method 2: Install from Source

1. Clone the repository:
```bash
git clone https://github.com/diotec360/aethel.git
cd aethel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Aethel:
```bash
pip install -e .
```

## Platform-Specific Instructions

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Open Command Prompt or PowerShell
3. Run the installation command:
```cmd
pip install aethel
```

### macOS

1. Install Python using Homebrew:
```bash
brew install python3
```

2. Install Aethel:
```bash
pip3 install aethel
```

### Linux (Ubuntu/Debian)

1. Update package list:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

2. Install Aethel:
```bash
pip3 install aethel
```

### Linux (Fedora/RHEL)

1. Install Python:
```bash
sudo dnf install python3 python3-pip
```

2. Install Aethel:
```bash
pip3 install aethel
```

## Verify Installation

After installation, verify that Aethel is correctly installed:

```bash
aethel --version
```

You should see output similar to:
```
Diotec360 v1.9.0 - Autonomous Sentinel
```

## Optional Dependencies

### Z3 Theorem Prover (for advanced verification)

```bash
pip install z3-solver
```

### Development Tools

For contributing to Aethel:

```bash
pip install pytest hypothesis black mypy
```

## Troubleshooting

### Permission Errors

If you encounter permission errors, try using a virtual environment:

```bash
python -m venv aethel-env
source aethel-env/bin/activate  # On Windows: aethel-env\Scripts\activate
pip install aethel
```

### Python Version Issues

Ensure you're using Python 3.8 or higher:

```bash
python --version
```

If you have multiple Python versions, use `python3` explicitly:

```bash
python3 -m pip install aethel
```

### Import Errors

If you encounter import errors, ensure your Python path is correctly configured:

```bash
python -c "import aethel; print(aethel.__version__)"
```

## Next Steps

- [Quick Start Tutorial](quickstart.md) - Generate your first proof in 5 minutes
- [First Steps Guide](first-steps.md) - Learn the basics of Aethel
- [Language Reference](../language-reference/syntax.md) - Comprehensive language documentation

## Getting Help

- [GitHub Issues](https://github.com/diotec360/diotec360/issues) - Report bugs or request features
- [Community Forum](https://community.aethel.dev) - Ask questions and share knowledge
- [Discord](https://discord.gg/aethel) - Real-time community support

## Commercial Support

For enterprise deployments and professional support, visit [diotec360.com/aethel](https://diotec360.com/aethel).
