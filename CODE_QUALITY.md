# Code Quality Setup

## Overview
This project uses a **hybrid approach** for code quality:
- 🚨 **Critical issues BLOCK PRs** (syntax errors, unused imports, etc.)
- 💅 **Style issues show as warnings** (spacing, formatting, etc.)  
- 🎨 **Auto-formatting available** via pre-commit hooks

## What Gets Checked

### 🚨 Critical (Blocking)
- `F401` - Unused imports
- `F811` - Redefined variables  
- `F821` - Undefined names
- `F841` - Unused variables
- `E999` - Syntax errors
- `B007/B008` - Likely bugs

### 💅 Style (Non-blocking warnings)
- Import sorting
- Code formatting  
- Line spacing
- Modern Python upgrades

## Quick Setup

### Install pre-commit (optional but recommended):
```bash
pip install pre-commit
pre-commit install
```

### Manual code formatting:
```bash
cd backend
pip install ruff
ruff format .        # Auto-fix formatting
ruff check . --fix   # Auto-fix what's possible
```

## How it Works
1. **Pre-commit hooks** catch issues locally (if installed)
2. **PR workflow** only checks changed files
3. **Critical issues** will block PR merging
4. **Style warnings** show up but don't block development
5. **Legacy code** is never checked (only new changes)

This keeps code quality high without blocking development velocity! 🚀