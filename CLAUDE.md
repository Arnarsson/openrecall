# OpenRecall - Claude Code Instructions

## Project Overview

OpenRecall is a macOS screenshot recording and OCR search tool (similar to Windows Recall). It continuously captures screenshots, extracts text via OCR, generates embeddings for semantic search, and provides a web dashboard to browse and search your screen history.

## Tech Stack

- **Language**: Python 3.12+
- **Web Framework**: Flask
- **OCR**: DocTR (document text recognition)
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **ML Backend**: PyTorch with MPS (Apple Silicon) support
- **Database**: SQLite
- **Screenshot Capture**: mss library
- **macOS Integration**: pyobjc

## Project Structure

```
openrecall/
├── app.py              # Flask web app and main entry point
├── screenshot.py       # Screenshot capture and recording thread
├── ocr.py              # Text extraction from images (DocTR)
├── nlp.py              # Embedding generation (SentenceTransformers)
├── database.py         # SQLite database operations
├── config.py           # Configuration and paths
├── utils.py            # macOS utilities (active window, idle detection)
└── cli.py              # CLI interface with menu bar support
```

## Key Files

- **screenshot.py**: Main recording loop - captures screens, compares for changes (MSSIM), saves images, runs OCR, stores in DB
- **app.py**: Flask routes for web dashboard, serves screenshots from `~/Library/Application Support/openrecall/screenshots/`
- **database.py**: SQLite operations - `recall.db` stores entries with text, timestamp, embedding, app name, window title

## Data Locations

- **Screenshots**: `~/Library/Application Support/openrecall/screenshots/`
- **Database**: `~/Library/Application Support/openrecall/recall.db`
- **Logs**: `~/Library/Logs/openrecall.log` and `openrecall.error.log`

## Running OpenRecall

### Development
```bash
source venv/bin/activate
python -m openrecall.app
# Web dashboard at http://localhost:8082
```

### Production (LaunchAgent)
```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.openrecall.agent.plist

# Unload service
launchctl unload ~/Library/LaunchAgents/com.openrecall.agent.plist

# Check status
launchctl list | grep openrecall
```

### Desktop App
Open `/Applications/OpenRecall.app` - launches browser to dashboard

## Common Issues & Fixes

### Screenshot thread crashes
- Check `~/Library/Logs/openrecall.error.log` for Python errors
- Common: variable name mismatches, function signature mismatches

### Images not showing in dashboard
- Filename format must be `{timestamp}.webp` (no monitor suffix)
- Files saved in `~/Library/Application Support/openrecall/screenshots/`

### Database table missing
```python
from openrecall.database import create_db
create_db()
```

### Screen Recording Permission
- System Preferences > Privacy & Security > Screen Recording
- Add the Python executable (e.g., `python3.13`)

### Dependency Installation Fails
- Install GEOS: `brew install geos` (required for shapely)
- Use flexible versions in setup.py for torch/torchvision compatibility

## Architecture Notes

1. **Recording Thread**: Runs in background, captures every 3s if screen changed (MSSIM threshold 0.9)
2. **OCR Pipeline**: DocTR extracts text from screenshots
3. **Embeddings**: SentenceTransformers generates vectors for semantic search
4. **Web Dashboard**: Flask serves screenshots and provides search interface
5. **LaunchAgent**: Keeps service running, auto-starts at login

## Development Guidelines

- Test OCR changes by manually running screenshot capture
- Database schema changes require migration or DB recreation
- Image filenames must match timestamp format expected by web app
- Use `wait_or_sleep()` for responsive shutdown in recording thread
