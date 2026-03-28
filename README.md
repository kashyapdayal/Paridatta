# Paridatta (Metascrubber)

Paridatta is a robust Python-based utility designed to extract, analyze, and scrub metadata from various media files. It provides both a Command Line Interface (CLI) and a Graphical User Interface (GUI), making it suitable for both automated batch processing and interactive manual use.

## Features

- **Metadata Extraction:** Identify and extract hidden metadata from media files.
- **Metadata Scrubbing:** Safely remove sensitive information (v.g. EXIF, ID3) to protect privacy.
- **Batch Processing:** Process multiple files or entire directories simultaneously.
- **Reporting:** Generate detailed reports of the metadata found and operations performed.
- **Cross-Platform:** Includes installation scripts for both Windows (`install.ps1`) and Unix/Linux (`install.sh`).
- **User Interface:** Offers an easy-to-use GUI alongside a fully functional CLI.

## Prerequisites

- **Python 3.8+**
- Recommended: A virtual environment

## Installation

You can install Paridatta and its dependencies using the provided installation scripts:

**On Windows:**
```powershell
.%install.ps1
```

**On Linux/macOS:**
```bash
./install.sh
```

Alternatively, you can install the dependencies manually using `pip`:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface (CLI)
Run the main script to use the CLI application. Use the `-h` flag to see available options:
```bash
python paridatta.py -h
```

###y Graphical User Interface (GUI)
To launch the GUI, you can run the GUI module:
```bash
python -m gui.main_gui
```

## Project Structure

- `paridatta.py`: Main CLI entry point.
- `gui/`: Contains the Graphical User Interface components (`main_gui.py`).
- `modules/`: Core business logic modules including:
  - `batch.py`: Batch processing logic.
  - `extractor.py`: Metadata extraction utilities.
  - `media.py`: Media file handling.
  - `reporter.py`: Report generation logic.
  - `scrubber.py`: Metadata removal and scrubbing utilities.
- `tests/`: Automated test suites and sample files.
- `utils/`: Helper functions for file operations and logging.
- `build.py`: Script for building executable binaries.
- `requirements.txt`: Project dependencies.

## Testing

To run the automated test suite, use `pytest` or `unittest` from the root directory:

```bash
pytest tests/
```