import logging
import os
import shutil
import subprocess
from pathlib import Path

def main():
    """The entrypoint of Helix.
    This method shouldn't be called explicitly. Use the `helix` command in the
    terminal after installing the app.
    """
    try:
        subprocess.run(["streamlit", "run", "ui/main.py"])
    except KeyboardInterrupt:
        logging.info("Shutting down Lettuce...")
