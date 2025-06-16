# AutoPylot

AutoPylot is a tool that automatically installs missing Python libraries in your projects.

## Features

- Scans your Python project for imports
- Detects missing packages
- Automatically installs missing packages using pip
- Uses a comprehensive mapping of import names to package names
- Works as both a CLI tool and an importable module

## Installation

```bash
pip install autopylot
```

Or install from source:

```bash
git clone https://github.com/harshRaj1601/AutoPylot
cd autopylot
pip install -e .
```

## Usage

### Method 1: As an importable module (recommended)

Simply import AutoPylot at the top of your Python file, and it will automatically scan for imports and install missing packages:

```python
import AutoPylot

# Rest of your code with imports
import numpy as np
import pandas as pd
# ...
```

You can also use AutoPylot programmatically:

```python
import AutoPylot

# Scan and install packages for the current directory
AutoPylot.install()

# Scan and install packages for a specific directory
AutoPylot.install('/path/to/your/project')

# Scan and install packages for a specific file
AutoPylot.scan_file('/path/to/your/file.py')
```

### Method 2: Using the CLI

AutoPylot provides two main commands through its CLI: `install` and `list`.

#### Install all missing packages in a project

```bash
autopylot install
```

Or use the short form:

```bash
autopylot i
```

Options:
- `--dir`, `-d`: Specify a different directory to scan (default: current directory)
- `--quiet`, `-q`: Suppress informational output

Example:
```bash
autopylot install --dir /path/to/your/project --quiet
```

#### List all external packages used in a project

```bash
autopylot list
```

Or use the short form:

```bash
autopylot l
```

Options:
- `--dir`, `-d`: Specify a different directory to scan (default: current directory)
- `--quiet`, `-q`: Only output package names without additional info (useful for generating requirements.txt)

Example:
```bash
# List packages with detailed output
autopylot list --dir /path/to/your/project

# Generate requirements.txt
autopylot list --quiet > requirements.txt
```





## How it works

1. AutoPylot scans all Python files in your project
2. It extracts all import statements and identifies unique module names
3. It checks if each module is available in your Python environment
4. For missing modules, it determines the correct package name using a mapping system
5. It installs missing packages using pip

## License

MIT