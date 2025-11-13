# Data Privacy and Security

## Database Location

All personal task data is stored in **SQLite database files** located **outside the git repository**:

```
Windows: C:\Users\<username>\.local\share\wxgtd\wxgtd.db
Linux:   ~/.local/share/wxgtd/wxgtd.db
macOS:   ~/Library/Application Support/wxgtd/wxgtd.db
```

## What is Stored in SQLite

The database contains ALL your personal GTD data:
- ✅ Tasks (titles, descriptions, notes)
- ✅ Projects/Folders
- ✅ Contexts
- ✅ Goals
- ✅ Tags
- ✅ Notebooks
- ✅ Reminders/Alarms
- ✅ Completed tasks history
- ✅ Task relationships

## Git Repository Protection

The `.gitignore` file ensures NO personal data is committed:

### Excluded from Git:
- `*.db` - All SQLite database files
- `*.sqlite`, `*.sqlite3` - Alternative database extensions
- `backups/` - Database backup directory
- `*.cfg` - User configuration files
- Any files in `~/.local/share/wxgtd/` (outside repo)

### Safe to Commit:
- ✅ `comprehensive_test_data.json` - Funny fake test data (penguins, wizards, etc.)
- ✅ `funny_test_data.json` - Humorous test tasks
- ✅ `test_import_data.json` - Sample import format

## Important Warnings

⚠️ **NEVER commit files containing real personal data:**
- Your actual Android DGT GTD exports
- Real database backups
- Configuration files with personal paths
- Any JSON files with your actual tasks

⚠️ **Before sharing on GitHub:**
1. Always use test data files (the funny ones already in repo)
2. Never export your real data to the repository directory
3. Keep backups in `~/.local/share/wxgtd/backups/` (excluded from git)

## Export/Import Safety

When syncing with Android DGT GTD:
- Import/Export happens via JSON files
- Store your real export files OUTSIDE the git repository
- Use the "Archive Database" feature which saves to `backups/` (git-ignored)
- The backup folder is automatically excluded from version control

## Verification

You can verify no personal data is tracked by running:

```bash
# Check for database files in git
git ls-files | grep -E "\.(db|sqlite)$"

# Check for backup files in git  
git ls-files | grep backup

# Should return nothing!
```

## Summary

✅ **Your data is safe** - All personal information stays in SQLite databases outside the git repository

✅ **Automatic protection** - `.gitignore` prevents accidental commits of sensitive files

✅ **Test data only** - The repository contains only funny/fake test data for development
