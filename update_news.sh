#!/bin/bash
# Navigate to the script's directory
cd "$(dirname "$0")"
# Activate the virtual environment
source venv/bin/activate
# Run the python script
/opt/anaconda3/bin/python3 update_news.py
