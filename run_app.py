import os
import sys

# In log ngay lập tức để xác nhận script đã chạy
print("--- DEBUG LOG START ---")
print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")

try:
    print("Attempting to import streamlit.web.cli...")
    import streamlit.web.cli as stcli
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {str(e)}")
    sys.exit(1)

def resolve_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

if __name__ == "__main__":
    app_path = resolve_path("app.py")
    print(f"Target App Path: {app_path}")
    
    if not os.path.exists(app_path):
        print(f"ERROR: app.py not found at {app_path}")
        sys.exit(1)

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false", # Thêm dòng này để tắt dev mode
        "--server.port=8501",
        "--server.headless=false",
    ]
    
    print("Launching Streamlit...")
    try:
        stcli.main()
    except Exception as e:
        print(f"Streamlit execution failed: {str(e)}")
