# wxGTD - Quick Start Guide

## Installation (3 Simple Steps)

### Step 1: Clone or Download the Project
```bash
cd "c:\Users\Johan\Desktop\dgt gtd desktop\wxgtd"
```

### Step 2: Run the Setup Script

**On Windows:**
```cmd
setup_venv.bat
```

**On Linux/macOS:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

This will automatically:
- Create a virtual environment
- Install all dependencies
- Set up wxGTD for development

### Step 3: Activate and Run

**Activate the virtual environment:**

Windows:
```cmd
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

**Run wxGTD:**
```bash
python wxgtd.pyw
```

## That's It!

You're now running wxGTD on Python 3! 🎉

## Additional Commands

### CLI Mode
```bash
python wxgtd_cli.py
```

### Debug Mode
```bash
python wxgtd_dbg.py
```

### View Help
```bash
python wxgtd.pyw --help
```

## Troubleshooting

### "wxPython installation failed"
On some systems, wxPython requires system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-wxgtk4.0
```

**Fedora:**
```bash
sudo dnf install python3-wxpython4
```

**macOS:**
```bash
brew install wxpython
```

### "Module not found"
Make sure your virtual environment is activated (you should see `(venv)` in your prompt).

### "Python version error"
wxGTD requires Python 3.8 or higher. Check your version:
```bash
python --version
```

## More Information

- See `README.md` for detailed documentation
- See `MIGRATION.md` for information about Python 2 to 3 conversion
