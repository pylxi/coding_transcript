from flask import Flask, render_template, request, jsonify
from csv_validator import validate_csv_file

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    is_valid, message, data = validate_csv_file(file)
    
    if not is_valid:
        return jsonify({'success': False, 'error': message}), 400
    
    return jsonify({
        'success': True,
        'message': 'File uploaded successfully',
        'rows': data['rows'],
        'columns': data['columns']
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=7860)
