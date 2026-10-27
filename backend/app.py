"""
ImageProof - Image Metadata and Digital Evidence Authenticity Analyzer
Backend: Flask REST API

Designed for 2nd-year Cyber Security college project presentations,
demonstrations, and viva examinations.
"""

import os
import uuid
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image

import database
from services.hasher import calculate_sha256
from services.metadata_extractor import extract_metadata
from services.anomaly_detector import analyze_anomalies
from services.pdf_generator import generate_pdf_report

# Initialize Flask App
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for React frontend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration & Forensic Storage Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.environ.get("VERCEL"):
    UPLOADS_DIR = "/tmp/uploads"
    REPORTS_DIR = "/tmp/reports"
else:
    UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Security Constraints
MAX_FILE_SIZE_BYTES = 16 * 1024 * 1024  # 16 MB maximum upload limit
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_BYTES
app.config["UPLOADS_DIR"] = UPLOADS_DIR
app.config["REPORTS_DIR"] = REPORTS_DIR

# Ensure directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Initialize SQLite database on startup
database.init_db()

def _allowed_file(filename: str) -> bool:
    """Checks whether the file has an authorized forensic image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(413)
def request_entity_too_large(error):
    """Gracefully handles uploads exceeding the 16 MB limit."""
    return jsonify({
        "error": "File size exceeds the 16 MB limit. Please select a smaller evidence file."
    }), 413

# -----------------------------------------------------------------------------
# 1. System Health Check Endpoint
# -----------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health-check API to verify backend connectivity, database status,
    and storage directories.
    """
    return jsonify({
        "status": "healthy",
        "service": "ImageProof Digital Forensics Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "storage": {
            "uploads_dir_exists": os.path.exists(UPLOADS_DIR),
            "reports_dir_exists": os.path.exists(REPORTS_DIR),
            "database_initialized": os.path.exists(database.DB_PATH)
        }
    }), 200

# -----------------------------------------------------------------------------
# 2. Forensic Dashboard Statistics Endpoint
# -----------------------------------------------------------------------------
@app.route("/api/stats", methods=["GET"])
def get_dashboard_stats():
    """Returns aggregated case counts and recent analyses for the dashboard."""
    try:
        stats = database.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve stats: {str(e)}"}), 500

# -----------------------------------------------------------------------------
# 3. Evidence Ingest & Analysis Endpoint (Core Function)
# -----------------------------------------------------------------------------
@app.route("/api/analyze", methods=["POST"])
def analyze_image():
    """
    Forensic Ingestion Workflow:
    1. Validates file presence, extension, and binary image header.
    2. Generates a collision-resistant safe server filename (UUID).
    3. Computes SHA-256 bitwise cryptographic hash.
    4. Extracts file, EXIF, camera, timestamp, and GPS metadata.
    5. Evaluates forensic heuristic rules (anomaly detection).
    6. Persists analysis to SQLite database.
    7. Generates a court-admissible-style PDF report.
    8. Returns complete forensic record to React frontend.
    """
    # 1. Validation: File presence
    if "image" not in request.files:
        return jsonify({"error": "No image file provided in upload request."}), 400
        
    file = request.files["image"]
    if not file or file.filename.strip() == "":
        return jsonify({"error": "No file selected. Please choose a JPG, JPEG, or PNG image."}), 400

    original_filename = secure_filename(file.filename)
    if not original_filename:
        original_filename = f"evidence_{int(datetime.now().timestamp())}.jpg"
        
    # 2. Validation: Extension check
    if not _allowed_file(original_filename):
        return jsonify({
            "error": "Unsupported file format. Only JPG, JPEG, and PNG images are supported."
        }), 400

    # Case details
    user_case_id = request.form.get("case_id", "").strip()
    if not user_case_id:
        user_case_id = f"CASE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
    investigator_notes = request.form.get("notes", "").strip()

    # 3. Save file safely with unique server-side filename (prevents overwrite & traversal)
    file_ext = os.path.splitext(original_filename)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}{file_ext}"
    stored_path = os.path.join(UPLOADS_DIR, stored_filename)
    
    file.save(stored_path)

    # 4. Binary Image Header Validation (Defense against disguised executables)
    try:
        with Image.open(stored_path) as img:
            img.verify()  # Validates that file is truly an image stream
    except Exception:
        # Malformed or malicious file disguised as an image
        if os.path.exists(stored_path):
            os.remove(stored_path)
        return jsonify({
            "error": "Invalid or corrupt image file. The uploaded binary does not match standard image format headers."
        }), 400

    try:
        # 5. Compute SHA-256 Cryptographic Checksum
        sha256_hash = calculate_sha256(stored_path)

        # 6. Extract Structured Forensic Metadata
        metadata = extract_metadata(stored_path, original_filename)

        # 7. Evaluate Heuristic Anomaly Rules
        anomalies = analyze_anomalies(metadata, sha256_hash)

        # 8. Record in SQLite Database
        file_size = os.path.getsize(stored_path)
        file_format = metadata.get("file_info", {}).get("format", file_ext.replace(".", "").upper())

        analysis_id = database.save_analysis(
            case_id=user_case_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_size=file_size,
            file_format=file_format,
            sha256_hash=sha256_hash,
            metadata=metadata,
            anomalies=anomalies,
            report_filename=None,
            notes=investigator_notes
        )

        # 9. Generate Official Forensic PDF Report
        record_for_pdf = {
            "id": analysis_id,
            "case_id": user_case_id,
            "original_filename": original_filename,
            "file_size": file_size,
            "file_format": file_format,
            "sha256_hash": sha256_hash,
            "metadata": metadata,
            "anomalies": anomalies,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": investigator_notes
        }
        
        try:
            report_filename = generate_pdf_report(record_for_pdf, REPORTS_DIR)
            database.update_report_filename(analysis_id, report_filename)
        except Exception as pdf_err:
            print(f"[Warning] PDF generation deferred: {pdf_err}")
            report_filename = None

        # 10. Fetch full record and return
        full_record = database.get_analysis_by_id(analysis_id)
        return jsonify(full_record), 201

    except Exception as e:
        # Clean up file on critical processing failure
        if os.path.exists(stored_path):
            os.remove(stored_path)
        return jsonify({"error": f"Analysis failed during processing: {str(e)}"}), 500

# -----------------------------------------------------------------------------
# 4. History & Single Record Retrieval
# -----------------------------------------------------------------------------
@app.route("/api/history", methods=["GET"])
def get_history():
    """Returns list of past analyses with optional search query."""
    search_query = request.args.get("search", "").strip() or None
    limit = int(request.args.get("limit", 100))
    records = database.get_all_analyses(search=search_query, limit=limit)
    return jsonify(records), 200

@app.route("/api/analysis/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id: int):
    """Returns full details of a specific analysis record."""
    record = database.get_analysis_by_id(analysis_id)
    if not record:
        return jsonify({"error": f"Analysis record #{analysis_id} not found."}), 404
    return jsonify(record), 200

# -----------------------------------------------------------------------------
# 5. PDF Report Generation & Download
# -----------------------------------------------------------------------------
@app.route("/api/reports/<filename>", methods=["GET"])
def download_report_by_name(filename: str):
    """Serves the generated PDF report as a downloadable attachment."""
    safe_name = secure_filename(filename)
    report_path = os.path.join(REPORTS_DIR, safe_name)
    if not os.path.exists(report_path):
        return jsonify({"error": "Report file not found on server."}), 404
    return send_from_directory(REPORTS_DIR, safe_name, as_attachment=True)

@app.route("/api/analysis/<int:analysis_id>/report", methods=["GET"])
def download_report_by_id(analysis_id: int):
    """Retrieves or dynamically regenerates the PDF report for a given analysis."""
    record = database.get_analysis_by_id(analysis_id)
    if not record:
        return jsonify({"error": f"Analysis record #{analysis_id} not found."}), 404
        
    report_filename = record.get("report_filename")
    if not report_filename or not os.path.exists(os.path.join(REPORTS_DIR, report_filename)):
        # Generate new report
        report_filename = generate_pdf_report(record, REPORTS_DIR)
        database.update_report_filename(analysis_id, report_filename)
        
    return send_from_directory(REPORTS_DIR, report_filename, as_attachment=True)

# -----------------------------------------------------------------------------
# 6. Secure Image Preview Endpoint
# -----------------------------------------------------------------------------
@app.route("/api/uploads/<filename>", methods=["GET"])
def get_uploaded_image(filename: str):
    """Serves uploaded images for preview in the React frontend interface."""
    safe_name = secure_filename(filename)
    file_path = os.path.join(UPLOADS_DIR, safe_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "Image file not found."}), 404
    return send_from_directory(UPLOADS_DIR, safe_name)

# -----------------------------------------------------------------------------
# 7. Delete Record & Reset Endpoints (Testing & Maintenance)
# -----------------------------------------------------------------------------
@app.route("/api/analysis/<int:analysis_id>", methods=["DELETE"])
def delete_record(analysis_id: int):
    """Deletes an analysis record and cleans up associated files."""
    record = database.delete_analysis(analysis_id)
    if not record:
        return jsonify({"error": f"Record #{analysis_id} does not exist."}), 404
        
    # Remove stored image
    stored_name = record.get("stored_filename")
    if stored_name:
        img_p = os.path.join(UPLOADS_DIR, stored_name)
        if os.path.exists(img_p):
            try:
                os.remove(img_p)
            except Exception:
                pass
                
    # Remove report
    rep_name = record.get("report_filename")
    if rep_name:
        rep_p = os.path.join(REPORTS_DIR, rep_name)
        if os.path.exists(rep_p):
            try:
                os.remove(rep_p)
            except Exception:
                pass
                
    return jsonify({"message": f"Analysis #{analysis_id} deleted successfully."}), 200

@app.route("/api/reset", methods=["POST"])
def reset_all_data():
    """
    Completely resets the database and deletes all uploaded images and reports.
    Helpful for starting fresh before college project viva demonstrations.
    """
    database.reset_database()
    
    # Clean uploads directory
    for item in os.listdir(UPLOADS_DIR):
        p = os.path.join(UPLOADS_DIR, item)
        if os.path.isfile(p):
            try:
                os.remove(p)
            except Exception:
                pass
                
    # Clean reports directory
    for item in os.listdir(REPORTS_DIR):
        p = os.path.join(REPORTS_DIR, item)
        if os.path.isfile(p):
            try:
                os.remove(p)
            except Exception:
                pass
                
    return jsonify({
        "message": "ImageProof database and forensic storage reset successfully."
    }), 200

# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("  IMAGEPROOF: Digital Evidence Authenticity Analyzer")
    print("  Backend running at: http://127.0.0.1:5000")
    print("  API Health check:   http://127.0.0.1:5000/api/health")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=True)
