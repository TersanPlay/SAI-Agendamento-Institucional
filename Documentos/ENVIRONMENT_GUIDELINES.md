# Environment Guidelines for EventoSys Project

This document explains how to properly manage the Python virtual environment for the EventoSys project to avoid dependency conflicts.

## 🎯 Objective

Remove environment variables that were installed outside the virtual environment and ensure proper virtual environment activation before working with Django projects.

## 📋 What We've Done

1. **Created a clean virtual environment** at `.venv/`
2. **Installed all dependencies** within this isolated environment
3. **Created helper scripts** to ensure clean environment activation
4. **Updated documentation** with best practices

## 🛠️ Tools Created

### 1. `activate_clean.bat`
A batch script that:
- Clears potentially conflicting environment variables (`PYTHONPATH`, `DJANGO_SETTINGS_MODULE`)
- Activates the virtual environment
- Shows confirmation of proper activation

### 2. `verify_environment.py`
A Python script that:
- Verifies we're working in the correct virtual environment
- Checks that required packages are installed
- Displays relevant environment variables
- Provides a summary of the environment status

### 3. `start_project.ps1`
A PowerShell script that:
- Automatically activates the virtual environment
- Provides useful command reminders
- Ensures a consistent development start

## 🔄 Best Practices Implemented

### Before Starting Work
```bash
# Option 1: Use the clean activation script (recommended)
activate_clean.bat

# Option 2: Use the PowerShell script
.\start_project.ps1

# Option 3: Manual activation
.venv\Scripts\activate
```

### Verification
```bash
# Run the verification script to ensure proper setup
python verify_environment.py
```

## 🚫 Environment Variables to Avoid

These environment variables can cause conflicts and should not be set globally:

- `PYTHONPATH` - Can interfere with virtual environment package resolution
- `DJANGO_SETTINGS_MODULE` - Can cause Django to use wrong settings
- Any globally installed Python package paths

## ✅ Proper Workflow

1. **Always activate the virtual environment** before working on the project
2. **Verify your environment** with `verify_environment.py`
3. **Run Django commands** with `python manage.py` (not `py manage.py`)
4. **Install new packages** only within the virtual environment using `pip install`

## 🔍 Troubleshooting

### Issue: "python is not recognized"
**Solution**: Make sure the virtual environment is activated. The prompt should show `(.venv)`.

### Issue: Wrong package versions
**Solution**: Verify you're in the virtual environment and reinstall packages:
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Django command not found
**Solution**: Check if Django is installed in the virtual environment:
```bash
pip list | findstr Django
```

## 📝 Summary

By following these guidelines and using the provided tools, you can ensure a clean, isolated development environment for the EventoSys project that avoids dependency conflicts and ensures consistent behavior across different development machines.