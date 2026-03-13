# Aethel Project Structure

## Directory Layout

```
aethel-core/
├── aethel/                    # Main package
│   ├── __init__.py
│   ├── core/                  # Core components
│   │   ├── __init__.py
│   │   ├── parser.py          # Parser (The Eye)
│   │   ├── judge.py           # Judge (The Juiz)
│   │   ├── bridge.py          # Bridge (The Ponte)
│   │   ├── kernel.py          # Kernel (The Cérebro)
│   │   ├── vault.py           # Vault (The Cofre)
│   │   ├── weaver.py          # Weaver (The Tecelão)
│   │   └── grammar.py         # Grammar definition
│   ├── cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py            # CLI implementation
│   ├── examples/              # Example programs
│   │   ├── README.md
│   │   └── finance.ae         # Aethel-Finance (DeFi Core)
│   ├── tests/                 # Test suite
│   └── docs/                  # Documentation
├── bin/                       # Executable scripts
│   └── aethel                 # CLI entry point
├── examples/                  # High-stakes examples
│   ├── README.md
│   ├── DIOTEC360_sat.ae          # Satellite controller
│   └── mission_simulator.py   # Mission simulation
├── output/                    # Generated code output
├── .DIOTEC360_vault/             # Local vault storage
├── docs/                      # Project documentation
│   ├── MANIFESTO.md
│   ├── ROADMAP.md
│   ├── QUICKSTART.md
│   ├── STATUS.md
│   ├── EXECUTIVE_SUMMARY.md
│   └── FINAL_REPORT.md
├── setup.py                   # Package setup
├── requirements.txt           # Dependencies
├── README.md                  # Project README
└── PROJECT_STRUCTURE.md       # This file
```

## Component Overview

### Core Components

1. **Parser** (`aethel/core/parser.py`)
   - Reads Aethel source code
   - Generates Abstract Syntax Tree (AST)
   - Uses Lark parser with EBNF grammar

2. **Judge** (`aethel/core/judge.py`)
   - Formal verification using Z3 Solver
   - Proves pre-conditions (guards)
   - Proves post-conditions (verify)
   - Finds counter-examples

3. **Bridge** (`aethel/core/bridge.py`)
   - Translates AST to AI prompts
   - Manages feedback loop
   - Supports multiple AI providers

4. **Kernel** (`aethel/core/kernel.py`)
   - Orchestrates compilation pipeline
   - Self-correction loop
   - Integrates all components

5. **Vault** (`aethel/core/vault.py`)
   - Content-addressable storage
   - SHA-256 hashing
   - Immutable function storage

6. **Weaver** (`aethel/core/weaver.py`)
   - Hardware-aware compilation
   - Polymorphic execution modes
   - Carbon footprint estimation

### CLI

The `aethel` command provides:
- `build`: Compile Aethel source files
- `verify`: Verify without generating code
- `vault list`: List stored functions
- `vault stats`: Show vault statistics

### Examples

- **Aethel-Sat**: Satellite controller (Epoch 0 proof of concept)
- **Aethel-Finance**: DeFi core (Epoch 1 real-world application)

## Installation

### Development Install
```bash
pip install -e .
```

### Production Install
```bash
pip install aethel
```

## Usage

### Command Line
```bash
# Build a file
aethel build mycode.ae

# Verify without building
Diotec360 verify mycode.ae

# List vault contents
Diotec360 vault list
```

### Python API
```python
from aethel import AethelKernel

kernel = AethelKernel(ai_provider="anthropic")
result = kernel.compile(source_code, max_attempts=3)
```

## Development

### Running Tests
```bash
pytest aethel/tests/
```

### Code Style
```bash
black aethel/
flake8 aethel/
```

## Next Steps (Epoch 1)

1. ✅ Professional project structure
2. ✅ CLI interface
3. ✅ Aethel-Finance example
4. ⏳ Distributed Vault (P2P)
5. ⏳ Web Playground
6. ⏳ Whitepaper

---

**Status**: Epoch 1 - The Great Expansion  
**Version**: 0.6.0  
**Last Updated**: February 1, 2026
