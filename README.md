# IaC Factory GUI

Interactive web-based GUI for [iac-factory](https://github.com/yourusername/iac-factory).

## Features

- 🎨 Visual drag-and-drop interface for designing cloud infrastructure
- 🔄 Real-time validation of architecture patterns
- 📊 Automatic C4 diagram generation
- 🚀 Export to multiple IaC tools (Pulumi, AWS CDK)
- 💾 Save and load designs
- ✅ Built-in validation rules

## Installation

### Prerequisites

- Python 3.8+
- iac-factory package installed

### Install iac-factory

```bash
pip install iac-factory
```

Or install from source:

```bash
git clone https://github.com/yourusername/iac-factory.git
cd iac-factory
pip install -e .
```

### Install GUI

```bash
git clone https://github.com/yourusername/iac-factory-gui.git
cd iac-factory-gui
pip install -e .
```

## Quick Start

### Start the GUI Server

```bash
python run_gui.py
```

Or use the start script:

```bash
./start.sh
```

Then open your browser to: http://localhost:8000

## Usage

### 1. Design Your Infrastructure

- Click "New Design" to start
- Drag components from the palette onto the canvas
- Connect components by clicking and dragging between them
- Configure component properties in the sidebar

### 2. Validate Architecture

- Click "Validate" to check your design against best practices
- Review warnings and errors
- Fix issues as needed

### 3. Generate Code

- Click "Generate Code" to see outputs
- Choose between:
  - Mermaid diagram (for documentation)
  - Pulumi code (for deployment)
  - AWS CDK code (for deployment)
- Copy code to your project

### 4. Save Your Work

- Click "Save Design" to persist your work
- Load previous designs from the design list

## Architecture

```
iac-factory-gui/
├── backend/              # FastAPI backend
│   ├── main.py          # Server entry point
│   ├── api_routes.py    # Design management API
│   ├── code_generation.py # Code generation endpoints
│   ├── enhanced_factory.py # Extended factory with state
│   └── design_manager.py # Design persistence
├── frontend/            # Static web UI
│   ├── index.html      # Main page
│   ├── app.js          # Application logic
│   └── styles.css      # Styling
├── run_gui.py          # Launcher script
└── setup.py            # Package configuration
```

## API Endpoints

### Design Management
- `GET /api/designs` - List all designs
- `POST /api/designs` - Create new design
- `GET /api/designs/{id}` - Get design by ID
- `PUT /api/designs/{id}` - Update design
- `DELETE /api/designs/{id}` - Delete design

### Code Generation
- `POST /api/designs/{id}/generate/mermaid` - Generate Mermaid diagram
- `POST /api/designs/{id}/generate/pulumi` - Generate Pulumi code
- `POST /api/designs/{id}/generate/cdk` - Generate AWS CDK code

## Development

### Install in Development Mode

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest backend/tests/
```

### Project Structure

The GUI is a separate package that depends on `iac-factory`:

- **iac-factory**: Core library for infrastructure definition and code generation
- **iac-factory-gui**: Web-based interface for visual design

## Configuration

### Server Settings

Edit `run_gui.py` to change:
- Host (default: 0.0.0.0)
- Port (default: 8000)
- Reload settings

### Design Storage

Designs are stored in `~/.iac_factory/designs/` by default.

## Troubleshooting

### Import Errors

Make sure `iac-factory` is installed:
```bash
pip install iac-factory
```

### Port Already in Use

Change the port in `run_gui.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### GUI Not Loading

Check that the server is running and accessible:
```bash
curl http://localhost:8000/health
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Related Projects

- [iac-factory](https://github.com/yourusername/iac-factory) - Core library
- [Pulumi](https://www.pulumi.com/) - Infrastructure as Code
- [AWS CDK](https://aws.amazon.com/cdk/) - AWS Cloud Development Kit

## Support

- 📖 [Documentation](https://github.com/yourusername/iac-factory-gui/docs)
- 🐛 [Issue Tracker](https://github.com/yourusername/iac-factory-gui/issues)
- 💬 [Discussions](https://github.com/yourusername/iac-factory-gui/discussions)
