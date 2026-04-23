import PyInstaller.__main__
import os
import streamlit

# Get the path to the streamlit library
st_path = os.path.dirname(streamlit.__file__)

PyInstaller.__main__.run([
    'run_app.py',
    # '--onefile',  # TẮT ONEFILE để dễ debug
    '--name=XLSXtoMarkdown',
    f'--add-data=app.py;.',
    f'--add-data=utils.py;.',
    f'--add-data=styles.py;.',
    f'--add-data={os.path.join(st_path, "static")};streamlit/static',
    f'--add-data={os.path.join(st_path, "runtime")};streamlit/runtime',
    '--collect-all=streamlit',
    '--copy-metadata=streamlit',
    '--clean',
])
