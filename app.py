from flask import Flask, jsonify, send_from_directory
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'esg-news-standalone.html')

@app.route('/feed.xml')
def feed():
    return send_from_directory('.', 'feed.xml')

@app.route('/run-aggregator', methods=['POST'])
def run_aggregator():
    try:
        # Run the RSS aggregator
        result = subprocess.run(['python', 'rss_aggregator.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'RSS aggregator completed successfully',
                'timestamp': datetime.now().isoformat(),
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': 'RSS aggregator failed',
                'error': result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error running aggregator: {str(e)}'
        }), 500

@app.route('/get-feed-info')
def get_feed_info():
    try:
        # Check if feed.xml exists and get its modification time
        if os.path.exists('feed.xml'):
            mtime = os.path.getmtime('feed.xml')
            return jsonify({
                'exists': True,
                'last_modified': datetime.fromtimestamp(mtime).isoformat(),
                'size': os.path.getsize('feed.xml')
            })
        else:
            return jsonify({
                'exists': False
            })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
