from flask import Flask, request, jsonify
from flask_cors import CORS
from file_handler import scan_project
from ai_service import analyze_codebase
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    data = request.json
    path = data.get('path')
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
        
    print(f"Analyzing path: {path}")
    
    # 1. Scan files
    files_result = scan_project(path)
    
    if isinstance(files_result, dict) and "error" in files_result:
        return jsonify(files_result), 400
        
    # 2. Process with AI Service
    try:
        result = analyze_codebase(files_result)
        return jsonify(result), 200
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
