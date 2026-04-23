#!/usr/bin/env python3
"""
Metrics API Server
Serves JSON metrics from running engines to dashboards
"""

from flask import Flask, jsonify
from pathlib import Path
import json
import time
from datetime import datetime

app = Flask(__name__)

LOGS_DIR = Path('/logs')

def read_json_file(path):
    """Safely read JSON file"""
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except:
        pass
    return {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Return all engine metrics"""
    
    e01 = read_json_file(LOGS_DIR / 'e01' / 'metrics.json')
    e02 = read_json_file(LOGS_DIR / 'e02' / 'ultimate_sovereign_metrics.json')
    e03 = read_json_file(LOGS_DIR / 'e03' / 'metrics.json')
    
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "engines": {
            "E01_engine_365_days": e01,
            "E02_ultimate_engine": e02,
            "E03_tenetaiagency_101": e03
        },
        "status": "operational"
    })

@app.route('/api/metrics/e01', methods=['GET'])
def get_e01():
    """Engine 365-Days metrics"""
    return jsonify(read_json_file(LOGS_DIR / 'e01' / 'metrics.json'))

@app.route('/api/metrics/e02', methods=['GET'])
def get_e02():
    """Ultimate Engine metrics"""
    return jsonify(read_json_file(LOGS_DIR / 'e02' / 'ultimate_sovereign_metrics.json'))

@app.route('/api/metrics/e03', methods=['GET'])
def get_e03():
    """TENET Agency 101 metrics"""
    return jsonify(read_json_file(LOGS_DIR / 'e03' / 'metrics.json'))

@app.route('/api/system', methods=['GET'])
def get_system():
    """System-wide metrics"""
    e01 = read_json_file(LOGS_DIR / 'e01' / 'metrics.json')
    e02 = read_json_file(LOGS_DIR / 'e02' / 'ultimate_sovereign_metrics.json')
    e03 = read_json_file(LOGS_DIR / 'e03' / 'metrics.json')
    
    e01_cycles = e01.get('cycles_completed', 0)
    e02_cycles = e02.get('cycles', 0)
    e03_ticks = e03.get('ticks', 0)
    
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "total_cycles": e01_cycles + e02_cycles,
            "total_ticks": e03_ticks,
            "engines_active": 3,
            "status": "operational",
            "uptime": "continuous"
        },
        "consensus": {
            "k_value": 1.0,
            "quorum": "10/14",
            "status": "EXECUTE"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001, debug=False)
