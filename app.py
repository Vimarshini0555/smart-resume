import os
from flask import Flask, request, jsonify, render_template
from parser import analyze_resume

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

@app.route('/')
def index():
    """Renders the main single-page resume analyzer dashboard."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """API Endpoint to parse resume PDF and compare with optional job description."""
    if 'resume' not in request.files:
        return jsonify({
            "success": False,
            "error": "No resume file uploaded. Please upload a PDF resume."
        }), 400
        
    file = request.files['resume']
    jd_text = request.form.get('job_description', '')
    
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "Empty filename. Please select a valid resume PDF."
        }), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({
            "success": False,
            "error": "Invalid file format. Only PDF files are supported."
        }), 400
        
    try:
        # Pass the file directly in-memory to the parser
        result = analyze_resume(file, jd_text)
        if not result.get("success", False):
            return jsonify(result), 400
            
        return jsonify(result)
    except Exception as e:
        print(f"Error in /analyze route: {e}")
        return jsonify({
            "success": False,
            "error": f"An internal server error occurred during processing: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Ensure templates and static folders exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("AI Resume Analyzer Flask server starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)
