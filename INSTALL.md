# Installation Guide - IaC Factory GUI

## Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python3 --version
   ```

2. **iac-factory package**
   
   The GUI depends on the core iac-factory package. Install it first:
   
   ```bash
   # Option 1: Install from PyPI (when published)
   pip install iac-factory
   
   # Option 2: Install from source
   git clone https://github.com/yourusername/iac-factory.git
   cd iac-factory
   pip install -e .
   cd ..
   ```

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/iac-factory-gui.git
cd iac-factory-gui

# Install in editable mode
pip install -e .
```

### Method 2: Install from PyPI (When Published)

```bash
pip install iac-factory-gui
```

### Method 3: Install with Development Dependencies

```bash
cd iac-factory-gui
pip install -e ".[dev]"
```

## Verify Installation

```bash
# Test imports
python3 -c "from backend.main import app; print('✓ GUI installed successfully')"

# Check dependencies
python3 -c "import fastapi, uvicorn, pydantic; print('✓ All dependencies available')"
```

## Running the GUI

### Quick Start

```bash
cd iac-factory-gui
python3 run_gui.py
```

### Using the Start Script

```bash
cd iac-factory-gui
./start.sh
```

### Access the GUI

Open your browser to: **http://localhost:8000**

## Directory Structure

After installation, your directory should look like:

```
iac-factory-gui/
├── backend/              # FastAPI backend
│   ├── __init__.py
│   ├── main.py          # Server entry point
│   ├── api_routes.py    # Design management
│   ├── code_generation.py # Code generation
│   ├── enhanced_factory.py # Enhanced factory
│   ├── design_manager.py # Design storage
│   └── tests/           # Test suite
├── frontend/            # Web UI
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── run_gui.py          # Launcher script
├── setup.py            # Package setup
├── pyproject.toml      # Modern package config
└── README.md           # Documentation
```

## Configuration

### Change Server Port

Edit `run_gui.py`:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8001,  # Change this
    reload=True
)
```

### Design Storage Location

Designs are stored in: `~/.iac_factory/designs/`

To change this, edit `backend/design_manager.py`:

```python
self.designs_dir = Path.home() / ".iac_factory" / "designs"
```

## Troubleshooting

### "No module named 'iac_factory'"

The core package isn't installed. Install it:

```bash
pip install iac-factory
```

### "No module named 'fastapi'"

GUI dependencies aren't installed:

```bash
cd iac-factory-gui
pip install -e .
```

### Port 8000 Already in Use

Change the port in `run_gui.py` or kill the process:

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### GUI Not Loading in Browser

1. Check server is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check firewall settings

3. Try accessing via 127.0.0.1:
   ```
   http://127.0.0.1:8000
   ```

### Import Errors

Make sure you're in the correct directory:

```bash
cd iac-factory-gui
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 run_gui.py
```

## Development Setup

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest backend/tests/
```

### Enable Hot Reload

The server automatically reloads when you edit backend files. For frontend changes, just refresh your browser.

## Uninstallation

```bash
pip uninstall iac-factory-gui
```

## Next Steps

1. ✅ Install the GUI
2. 🚀 Start the server: `python3 run_gui.py`
3. 🌐 Open browser: http://localhost:8000
4. 🎨 Create your first design
5. �� Read the [User Guide](README.md)

## Support

- 📖 [Documentation](https://github.com/yourusername/iac-factory-gui)
- 🐛 [Report Issues](https://github.com/yourusername/iac-factory-gui/issues)
- 💬 [Discussions](https://github.com/yourusername/iac-factory-gui/discussions)
