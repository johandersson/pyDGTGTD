# pyDGTGTD - Python 3 Desktop GTD Application

A GTD® (Getting Things Done®) task management application for desktop with data sync support for DGT GTD Android app.

**This is a fork of [wxGTD by Karol Będkowski](https://github.com/KarolBedkowski/wxgtd), updated for Python 3 and wxPython 4.x compatibility. The original program was called wxGTD, but this fork has been renamed to pyWeeklyReview.**

## About

pyWeeklyReview is a desktop application for managing tasks following the GTD® methodology. This Python 3 version includes:
- Full wxPython 4.x compatibility
- JSON import/export for syncing with DGT GTD Android app
- SQLite database with SQLAlchemy ORM
- Context-based task organization
- Goals and projects (folders) support
- Reminders and recurring tasks
- Notebooks for reference material

## Known Issues

⚠️ **Dropbox Sync is Currently Broken** - The original Dropbox API v1 used for synchronization has been deprecated by Dropbox and no longer works. This feature will hang if attempted. Use JSON import/export as an alternative for syncing data.

## Credits & Attribution

**Original Author:**
- (C) Karol Będkowski <karol.bedkowski@gmail.com> - Original wxGTD desktop application, GPL2 License

**DGT GTD Android App:**
- (C) [dgtale - Creator of DGT GTD Android app](https://www.dgtale.ch/), Unkown license, this project does not use any code from that app, just the JSON file format that it uses to backup and export the tasks and projects.

**Python 3 Migration and added features and improved GUI:**
- (C) Johan Andersson - Python 3 migration, wxPython 4.x compatibility, Android sync fixes (2025), GPL2 License

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

pyWeeklyReview can import/export JSON data from the DGT GTD Android app:

1. Export from Android app to JSON file
2. In pyWeeklyReview: File → Import/Export → Import from JSON
3. Select your exported JSON file

All tasks, contexts, folders, goals, and notebooks will be imported.

## Fork Improvements & Changes

This fork includes:

**Python 3 & wxPython 4.x Migration:**
- Upgraded from Python 2.7 to Python 3.8+
- Updated to wxPython 4.x (Phoenix) from legacy wxPython 2.8
- Fixed wx.PyValidator → wx.Validator deprecation
- Fixed wx.SystemSettings API changes
- Removed obsolete wxversion import

**Bug Fixes & Compatibility:**
- Fixed empty UUID handling in JSON imports
- Fixed task-context-folder-goal relationship mapping
- Fixed None type comparisons
- Added session.flush() for UUID auto-generation
- Improved Android DGT GTD JSON sync reliability

**Performance Improvements:**
- Added task count caching for filter tree
- Optimized database queries with reduced redundant calls
- Improved GUI responsiveness with cached filter counts

**New Features:**
- Dynamic task counts in filter checkboxes (e.g., "@home (5)")
- Context-aware count updates based on active filters
- Enhanced filter tree with real-time count refresh

**Code Quality:**
- Improved code organization following PEP 8 standards
- Added comprehensive test suite with 197 unit tests
- 31% code coverage with pytest and coverage.py

## License

GPL v2+ - See COPYING file for full license text.

**Copyright:**
- Copyright (C) 2013-2015 Karol Będkowski (original wxGTD)
- Copyright (C) 2025 Johan Andersson (Python 3 migration and Android sync, renamed to pyWeeklyReview)
- DGT GTD Android app data format by dgtale

## Trademarks

GTD® and Getting Things Done® are registered trademarks of David Allen and the David Allen Company.

This software is not affiliated with, endorsed by, or supported by David Allen or the David Allen Company. 

## Project Links

- **This Repository:** https://github.com/johandersson/gtgGTDdesktop
- **Original wxGTD (forked from):** https://github.com/KarolBedkowski/wxgtd by Karol Będkowski
- **DGT GTD Android:** By dgtale
