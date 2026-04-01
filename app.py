"""
Flask Web Application for Transcript Processor
With Jinja2 templates for easy HTML/CSS editing
"""

import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import sys
import io

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.analytics import compute_analytics
    from app.file_checker import check_csv_format
    from app.summarizer import summarize_transcript
except ImportError:
    # Fallback for development
    def compute_analytics(df):
        return {"messages": "Analytics not available"}
    def check_csv_format(df):
        return True, "OK"
    def summarize_transcript(df, **kwargs):
        return "Summary not available"

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store session data
sessions = {}

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files allowed'}), 400
        
        # Load and validate CSV
        df = pd.read_csv(file)
        
        # Check format
        try:
            is_valid, msg = check_csv_format(df)
            if not is_valid:
                return jsonify({'error': f'Validation error: {msg}'}), 400
        except:
            # If check_csv_format not available, do basic validation
            required_cols = {'speaker', 'text'}
            if not required_cols.issubset(set(df.columns)):
                return jsonify({'error': f'Missing columns: {required_cols}'}), 400
        
        # Store in session
        session_id = str(hash(file.filename))[-10:]
        sessions[session_id] = {
            'df': df,
            'filename': file.filename,
            'rows': len(df),
            'columns': list(df.columns)
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': file.filename,
            'rows': len(df),
            'columns': list(df.columns)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process/<session_id>', methods=['POST'])
def process_file(session_id):
    """Process uploaded file and compute analytics."""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json()
        enable_summary = data.get('enable_summary', False)
        max_words = data.get('max_words', 150)
        
        df = sessions[session_id]['df']
        
        # Compute analytics
        analytics = compute_analytics(df)
        
        # Generate summary if requested
        summary = ""
        if enable_summary:
            try:
                summary = summarize_transcript(df, max_words=max_words)
            except Exception as e:
                summary = f"Summary generation failed: {str(e)}"
        
        return jsonify({
            'success': True,
            'analytics': analytics.get('messages', ''),
            'summary': summary,
            'rows_processed': len(df)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<session_id>')
def download_results(session_id):
    """Download analytics as CSV."""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        df = sessions[session_id]['df']
        
        # Return as CSV download
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='analytics.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=7860)
