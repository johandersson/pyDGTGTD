# wxGTD - Python 3 Desktop GTD Application

A GTD® (Getting Things Done®) task management application for desktop with data sync support for DGT GTD Android app.

**This is a fork of [wxGTD by Karol Będkowski](https://github.com/KarolBedkowski/wxgtd), updated for Python 3 and wxPython 4.x compatibility.**

## About

wxGTD is a desktop application for managing tasks following the GTD® methodology. This Python 3 version includes:
- Full wxPython 4.x compatibility
- JSON import/export for syncing with DGT GTD Android app
- SQLite database with SQLAlchemy ORM
- Context-based task organization
- Goals and projects (folders) support
- Reminders and recurring tasks
- Notebooks for reference material

## Credits & Attribution

**Original Author:**
- Karol Będkowski <karol.bedkowski@gmail.com> - Original wxGTD desktop application

**DGT GTD Android App:**
- [dgtale - Creator of DGT GTD Android app](https://www.dgtale.ch/)

**Python 3 Migration and added features and improved GUI:**
- Johan Andersson - Python 3 migration, wxPython 4.x compatibility, Android sync fixes (2025)

## Requirements

- Python 3.8 or higher
- wxPython 4.0+
- SQLAlchemy 1.4+

## Quick Start

### Installation

**Windows:**
```cmd
setup_venv.bat
```

**Linux/macOS:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

This creates a virtual environment and installs all dependencies.

### Running

**GUI Mode:**
```bash
python wxgtd.pyw
```

**CLI Mode:**
```bash
python wxgtd_cli.py
```

## Android App Sync

wxGTD can import/export JSON data from the DGT GTD Android app:

1. Export from Android app to JSON file
2. In wxGTD: File → Import/Export → Import from JSON
3. Select your exported JSON file

All tasks, contexts, folders, goals, and notebooks will be imported.

## Python 3 Migration Changes

- Fixed wx.PyValidator → wx.Validator deprecation
- Fixed wx.SystemSettings API changes
- Removed obsolete wxversion import
- Fixed empty UUID handling in JSON imports
- Fixed task-context-folder-goal relationship mapping
- Fixed None type comparisons
- Added session.flush() for UUID auto-generation

## License

GPL v2+ - See COPYING file for full license text.

**Copyright:**
- Copyright (C) 2013-2015 Karol Będkowski (original wxGTD)
- Copyright (C) 2025 Johan Andersson (Python 3 migration and Android sync)
- DGT GTD Android app data format by dgtale

## Trademarks

GTD® and Getting Things Done® are registered trademarks of David Allen and the David Allen Company.

This software is not affiliated with, endorsed by, or supported by David Allen or the David Allen Company. 

## Project Links

- **This Repository:** https://github.com/johandersson/gtgGTDdesktop
- **Original wxGTD (forked from):** https://github.com/KarolBedkowski/wxgtd by Karol Będkowski
- **DGT GTD Android:** By dgtale
