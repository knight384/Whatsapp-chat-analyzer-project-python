from flask import Flask, request, redirect, url_for, send_file, abort, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import tempfile
import uuid
import time
from datetime import datetime, timedelta
import json
from main import analyze, export_html, export_csv

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB (for images)

# Directory to store generated reports for download
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# How long to keep generated reports (hours)
REPORT_RETENTION_HOURS = 24


def clean_reports(retention_hours=REPORT_RETENTION_HOURS):
    """Remove files in REPORTS_DIR older than retention_hours."""
    now = time.time()
    cutoff = now - (retention_hours * 3600)
    for name in os.listdir(REPORTS_DIR):
        full = os.path.join(REPORTS_DIR, name)
        try:
            if os.path.isfile(full):
                mtime = os.path.getmtime(full)
                if mtime < cutoff:
                    os.remove(full)
        except Exception:
            # ignore deletion errors
            pass


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return abort(400, 'No file part')
    file = request.files['file']
    if file.filename == '':
        return abort(400, 'No selected file')
    if not allowed_file(file.filename):
        return abort(400, 'Only .txt files and images (png, jpg, jpeg, gif, bmp, webp) are allowed')
    filename = secure_filename(file.filename)
    is_image = is_image_file(filename)
    
    # Check if image upload is attempted but OCR is not available
    if is_image:
        try:
            from main import OCR_AVAILABLE
            if not OCR_AVAILABLE:
                error_msg = (
                    "Image processing requires OCR libraries. "
                    "Please install: pip install Pillow pytesseract\n\n"
                    "Also install Tesseract OCR engine:\n"
                    "• Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "• After installation, add Tesseract to your system PATH\n"
                    "• Or restart your terminal/IDE after installation\n\n"
                    "Note: Text file (.txt) uploads work without OCR!"
                )
                return render_template('error.html', error_message=error_msg), 400
        except ImportError:
            pass
    
    # Save to a temporary file then persist generated reports in REPORTS_DIR
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, filename)
        file.save(path)
        try:
            top_n = int(request.form.get('top', 20))
        except Exception:
            top_n = 20
        try:
            summary = analyze(path, top_n=top_n, is_image=is_image)
        except Exception as e:
            error_msg = str(e)
            # Provide helpful installation instructions for OCR errors
            if 'OCR' in error_msg or 'tesseract' in error_msg.lower():
                error_msg += (
                    "\n\n📥 Installation Instructions:\n"
                    "1. Install Python packages: pip install Pillow pytesseract\n"
                    "2. Download Tesseract OCR for Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "3. Install Tesseract (use default installation path)\n"
                    "4. Restart your terminal/IDE\n"
                    "5. Try uploading again\n\n"
                    "💡 Tip: Text file (.txt) uploads work immediately without OCR!"
                )
            return render_template('error.html', error_message=error_msg), 400
        
        # generate a unique base name for reports
        base = uuid.uuid4().hex
        html_name = f'report_{base}.html'
        csv_name = f'summary_{base}.csv'
        html_path = os.path.join(REPORTS_DIR, html_name)
        csv_path = os.path.join(REPORTS_DIR, csv_name)
        export_html(summary, html_path)
        export_csv(summary, csv_path)
        # run cleanup of old reports (best-effort)
        try:
            clean_reports()
        except Exception:
            pass

        # Prepare per-day series for chart (sorted by date)
        per_day_items = sorted(summary.get('per_day', {}).items())
        per_day_dates = [d for d, c in per_day_items]
        per_day_counts = [c for d, c in per_day_items]
        
        # Prepare per-hour data for chart
        per_hour_items = sorted(summary.get('per_hour', {}).items())
        per_hour_hours = [f"{h:02d}:00" for h, c in per_hour_items]
        per_hour_counts = [c for h, c in per_hour_items]
        
        # Prepare per-weekday data
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        per_weekday_dict = summary.get('per_weekday', {})
        per_weekday_labels = [day for day in weekday_order if day in per_weekday_dict]
        per_weekday_counts = [per_weekday_dict[day] for day in per_weekday_labels]
        
        # Prepare active periods data
        active_periods = summary.get('active_periods', {})
        period_labels = ['Morning', 'Afternoon', 'Evening', 'Night']
        period_counts = [active_periods.get(period, 0) for period in period_labels]

        # render a nicer results page with download links and chart data
        return render_template(
            'report.html',
            summary=summary,
            report_url=url_for('reports', filename=html_name),
            csv_url=url_for('reports', filename=csv_name),
            per_day_dates=per_day_dates,
            per_day_counts=per_day_counts,
            per_hour_hours=per_hour_hours,
            per_hour_counts=per_hour_counts,
            per_weekday_labels=per_weekday_labels,
            per_weekday_counts=per_weekday_counts,
            period_labels=period_labels,
            period_counts=period_counts,
        )


@app.route('/reports/<path:filename>')
def reports(filename):
  # Serve generated report files. HTML will be displayed inline; CSV will download.
  full = os.path.join(REPORTS_DIR, filename)
  if not os.path.exists(full):
    return abort(404)
  if filename.lower().endswith('.csv'):
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)
  return send_from_directory(REPORTS_DIR, filename)


if __name__ == '__main__':
    # Run on 0.0.0.0 so you can open on localhost
    app.run(host='0.0.0.0', port=5000, debug=True)
