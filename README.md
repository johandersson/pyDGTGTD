# wxGTD - Python 3 Edition

A GTD (Getting Things Done) task management application built with wxPython.

## Overview

wxGTD is a desktop application for managing tasks following the GTD methodology. This version has been modernized for Python 3.8+ with improved packaging and virtual environment support.

## Requirements

- Python 3.8 or higher
- wxPython 4.0+
- SQLAlchemy 1.4+

## Installation

### Quick Setup (Recommended)

The easiest way to set up wxGTD is using the provided setup scripts:

#### Windows
```cmd
setup_venv.bat
```

#### Linux/macOS
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

Or use Python directly:
```bash
python3 setup_venv.py
```

This will:
1. Create a virtual environment in the `venv` directory
2. Install all required dependencies
3. Install wxGTD in development mode

### Manual Setup

If you prefer to set up manually:

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   
   **Windows:**
   ```cmd
   venv\Scripts\activate
   ```
   
   **Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install wxGTD in development mode:
   ```bash
   pip install -e .
   ```

## Running wxGTD

### After activating the virtual environment:

**GUI Mode:**
```bash
python wxgtd.pyw
```

**CLI Mode:**
```bash
python wxgtd_cli.py
```

**Debug Mode:**
```bash
python wxgtd_dbg.py
```

### Using installed entry points:

If installed via pip, you can also use:
```bash
wxgtd          # GUI mode
wxgtd-cli      # CLI mode
```

## Development

### Installing Development Dependencies

```bash
pip install -r requirements-dev.txt
```

This includes:
- pytest (testing)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black wxgtd/
```

### Linting

```bash
flake8 wxgtd/
```

## Project Structure

```
wxgtd/
├── wxgtd/              # Main package
│   ├── gui/            # GUI components
│   ├── lib/            # Utility libraries
│   ├── logic/          # Business logic
│   ├── model/          # Data models
│   └── wxtools/        # wxPython utilities
├── data/               # Application data files
├── locale/             # Translations
├── man/                # Manual pages
└── po/                 # Translation source files
```

## Migration from Python 2

This version has been updated from Python 2 to Python 3 with the following changes:

- Updated all print statements to print() functions
- Replaced `optparse` with `argparse`
- Removed Python 2 specific encoding workarounds
- Updated shebang lines to use `python3`
- Modernized packaging with `pyproject.toml` and `setup.cfg`
- Added virtual environment support
- Removed py2exe dependencies (Windows builds now use modern alternatives)

## Building and Distribution

### Build source distribution:
```bash
python -m build
```

### Install from source:
```bash
pip install .
```

## License

GPL v2+

See the COPYING file for full license text.

## Author

Karol Będkowski <karol.bedkowski@gmail.com>

Copyright (c) Karol Będkowski, 2013-2015, 2025

## Additional Notes

- The database file is stored in your user configuration directory
- Configuration files are stored according to your platform's standards
- Locale files are automatically loaded based on your system language

## Troubleshooting

### wxPython Installation Issues

If wxPython fails to install, you may need to install system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-wxgtk4.0
```

**macOS (using Homebrew):**
```bash
brew install wxpython
```

**Windows:**
Download the appropriate wheel from: https://wxpython.org/pages/downloads/

### Database Issues

If you encounter database errors, try removing the old database file and letting the application create a new one.

## Contributing

Contributions are welcome! Please ensure:
- Code is formatted with black
- Tests pass with pytest
- Code follows PEP 8 guidelines (checked with flake8)
