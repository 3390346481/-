import subprocess
import os

os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_PORT'] = '8000'

subprocess.run(['streamlit', 'run', 'app.py'], check=True)
