# pyDGTGTD - Python 3 Desktop GTD Application

A GTD® (Getting Things Done®) task management application for desktop with data sync support for DGT GTD Android app.

**This is a fork of [wxGTD by Karol Będkowski](https://github.com/KarolBedkowski/wxgtd), updated for Python 3 and wxPython 4.x compatibility. The original program was called wxGTD, but this fork has been renamed to pyWeeklyReview for .**

## About

pyWeeklyReview is a desktop application for managing tasks following the GTD® methodology. This Python 3 version includes:
- Full wxPython 4.x compatibility
- JSON import/export for syncing with DGT GTD Android app
- **Dropbox sync with upgraded API v2** (fixed from deprecated v1)
- SQLite database with SQLAlchemy ORM
- Context-based task organization
- Goals and projects (folders) support
- Reminders and recurring tasks
- Notebooks for reference material
- **Project List view** for tracking active and empty projects

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

## Sync Options

### Dropbox Sync

pyWeeklyReview now includes updated Dropbox synchronization using API v2:

1. Configure Dropbox in Settings → Preferences → Sync tab
2. Authenticate with your Dropbox account
3. Enable automatic sync on startup/exit (optional)
4. Use File → Synchronize Tasks to manually sync

**Note:** This fork upgraded from the deprecated Dropbox API v1 to v2, restoring full Dropbox sync functionality.

### Android App Sync

pyWeeklyReview can import/export JSON data from the DGT GTD Android app:

1. Export from Android app to JSON file
2. In pyWeeklyReview: File → Import/Export → Import from JSON
3. Select your exported JSON file

All tasks, contexts, folders, goals, and notebooks will be imported.

## Fork Improvements & Changes

This fork includes significant enhancements over the original wxGTD:

### Python 3 & wxPython 4.x Migration
- Upgraded from Python 2.7 to Python 3.8+
- Updated to wxPython 4.x (Phoenix) from legacy wxPython 2.8
- Fixed wx.PyValidator → wx.Validator deprecation
- Fixed wx.SystemSettings API changes
- Removed obsolete wxversion import

### Dropbox Sync Restoration
- **Upgraded from deprecated Dropbox API v1 to v2**
- Restored full Dropbox synchronization functionality
- Fixed authentication and file operations with current Dropbox API

### Bug Fixes & Compatibility
- Fixed empty UUID handling in JSON imports
- Fixed task-context-folder-goal relationship mapping
- Fixed None type comparisons
- Added session.flush() for UUID auto-generation
- Improved Android DGT GTD JSON sync reliability

### Performance Improvements
- Added task count caching for filter tree
- Optimized database queries with reduced redundant calls
- Improved GUI responsiveness with cached filter counts
- Added database indexing for common query patterns

### New Features
- **Project List View** - New tab showing projects categorized as "With Actions" vs "No Tasks"
- Dynamic task counts in filter checkboxes (e.g., "@home (5)")
- Context-aware count updates based on active filters
- Enhanced filter tree with real-time count refresh
- Double-click project list items to edit projects

### Code Quality & Internationalization
- Improved code organization following PEP 8 naming standards
- Renamed all camelCase variables to snake_case for consistency
- Translated all Polish comments to English for international collaboration
- Added comprehensive test suite with 205+ unit tests
- Achieved 31% code coverage with pytest and coverage.py
- Fixed method name typos and standardized naming

## Credits & Attribution

**Original Author:**
- (C) Karol Będkowski <karol.bedkowski@gmail.com> - Original wxGTD desktop application, GPL2 License

**DGT GTD Android App:**
- (C) [dgtale - Creator of DGT GTD Android app](https://www.dgtale.ch/), Unknown license, this project does not use any code from that app, just the JSON file format that it uses to backup and export the tasks and projects.

**Python 3 Migration and Fork Improvements:**
- (C) Johan Andersson - Python 3 migration, wxPython 4.x compatibility, Dropbox API upgrade, Android sync fixes, new features, performance improvements (2025), GPL2 License

## License

GPL v2+ - See COPYING file for full license text.

**Copyright:**
- Copyright (C) 2013-2015 Karol Będkowski (original wxGTD)
- Copyright (C) 2025 Johan Andersson (Python 3 migration, Dropbox API upgrade, Android sync, renamed to pyWeeklyReview)
- DGT GTD Android app data format by dgtale

## Trademarks

GTD® and Getting Things Done® are registered trademarks of David Allen and the David Allen Company.

This software is not affiliated with, endorsed by, or supported by David Allen or the David Allen Company. 

## Project Links

- **This Repository:** https://github.com/johandersson/gtgGTDdesktop
- **Original wxGTD (forked from):** https://github.com/KarolBedkowski/wxgtd by Karol Będkowski
- **DGT GTD Android:** By dgtale
