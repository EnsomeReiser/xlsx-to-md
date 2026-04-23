# XLSX to Markdown Converter

A powerful Streamlit-based tool to convert Excel workbooks (.xlsx) to Markdown format with live preview and translation support.

## 🌟 Features
- **Live Preview**: Instantly view Markdown results as you switch sheets or search.
- **Multi-file Support**: Upload and process multiple workbooks simultaneously.
- **Export Options**: 
  - Download individual Markdown files.
  - Download all results as a ZIP archive.
  - Merge all workbooks into a single Markdown file.
- **Translation**: Translate content to a target language using DeepL or Google Translate API.
- **Stand-alone EXE**: Can be bundled into a portable executable (.exe) for Windows.

## 🛠 Installation

This project uses Python and can be managed via `pnpm` or `npm`.

1. **Install Python Dependencies**:
   ```bash
   pnpm run install-deps
   # Or: pip install -r requirements.txt pyinstaller
   ```

## 🚀 Usage

### Run in Development Mode
```bash
pnpm run dev
```
The application will be available at `http://localhost:8502`.

### Build to Executable (.exe)
To create a standalone Windows executable:
```bash
pnpm run build
```
Once completed, the executable will be located in the `dist/XLSXtoMarkdown/` directory.

## 📂 Project Structure
- `app.py`: Main Streamlit application interface.
- `utils.py`: Contains core logic for Excel processing and Markdown generation.
- `styles.py`: Custom CSS and UI styling definitions.
- `run_app.py`: Entry point script for the bundled executable.
- `build_exe.py`: Automation script for PyInstaller bundling.

## 📝 License
This project is developed for personal use. Feel free to use and modify it!
