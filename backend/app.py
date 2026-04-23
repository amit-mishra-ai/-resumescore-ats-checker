"""
ATS Resume Checker - Backend API
Flask application that analyzes resumes and provides ATS scoring.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import tempfile
from resume_parser import extract_text_from_file
from ats_analyzer import analyze_resume

app = Flask(__name__)

# ── CORS FIX: Allow ALL origins, methods, and headers ──────────────────
# This fixes "Failed to fetch" when frontend is on a different port
CORS(app,
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=False)

# ── Also manually handle OPTIONS preflight for all routes ───────────────
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Max upload size: 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "ATS Checker API is running"})


@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """
    Main endpoint: accepts a resume file, extracts text, and returns ATS analysis.
    Expects: multipart/form-data with 'resume' file + optional 'job_description' text
    Returns: JSON with score, sections, keywords, suggestions
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    # 1. Validate file was uploaded
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    file = request.files['resume']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are supported"}), 400

    # 2. Get optional job description
    job_description = request.form.get('job_description', '').strip()

    # 3. Save file temporarily and extract text
    try:
        suffix = '.' + file.filename.rsplit('.', 1)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Extract plain text from the resume
        resume_text = extract_text_from_file(tmp_path)
        os.unlink(tmp_path)  # Clean up temp file

        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({"error": "Could not extract meaningful text from the resume. Please check your file."}), 400

        # 4. Run full ATS analysis
        result = analyze_resume(resume_text, job_description)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # debug=True shows errors in terminal — helpful for development
    app.run(host='0.0.0.0', port=port, debug=True)
