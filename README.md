# Whatsapp-chat-analyzer-project-python
WhatsApp Chat Analyzer — Python

Project Title: WhatsApp Chat Analyzer — Python
Submitted by: Anish Choudhary
Internship Role: Virtual Intern — Hack Culprit
Project Duration: 1st October 2025 — 31st October 2025
Repository: https://github.com/knight384/Whatsapp-chat-analyzer-project-python.git

1. Executive Summary

This project parses an exported WhatsApp chat (text file), extracts conversation metadata and statistics, and produces human-friendly outputs (CSV summary, HTML report). It includes both a CLI and a small web interface, plus optional OCR support for image-to-text conversions of chat screenshots. The repository contains the core scripts, templates, sample data, and a short OCR setup guide. 
GitHub
+1

2. Problem Statement

Users frequently want quick insights from long WhatsApp chats (e.g., top participants, message counts, active hours, most-used words). Manually scanning chats is tedious and error-prone. This project automates extraction, parsing, and summarization of chat data so users can quickly understand conversation dynamics and export results for reporting or analysis.

3. Project Objectives

Build a repeatable pipeline that converts exported WhatsApp chat text into structured data.

Provide both CLI and lightweight web UI for different user preferences.

Include OCR support to extract text from screenshots (useful when chat export is an image).

Produce documented, modular code suitable for extension (forecasting, visualizations, etc.).

4. Development Approach

Requirement Analysis & Planning — Decided on text parsing + optional OCR path, identified outputs (CSV, HTML report).

Development — Implemented parsing/analysis scripts (main.py, app.py, parsing modules), HTML reporting (report.html), and simple templates. 
GitHub

Testing & Debugging — Added a test file for the parser (test_parser.py) and sample chat (sample_chat.txt) to validate parsing logic. 
GitHub

Documentation & Packaging — Wrote setup docs including OCR setup (SETUP_OCR.md) and this README. 
GitHub

5. Tools & Technologies
Category	Tools / Technologies
Language	Python
Web	Flask (small web UI via app.py)
Testing	pytest / test scripts (test_parser.py)
Extras	OCR support (instructions in SETUP_OCR.md)
Utilities	Git, VS Code, templates/static assets for report generation. 
GitHub
+1
6. Installation & Setup

Prerequisites: Python 3.8+ and pip.

Clone the repo and change directory:

git clone <your-repo-clone-url>
cd Whatsapp-chat-analyzer-project-python


Install dependencies:

pip install -r requirements.txt


(Optional) OCR setup: follow SETUP_OCR.md to install Tesseract or other OCR dependencies if you plan to analyze screenshots. 
GitHub

(Optional) Check project quick fixes or notes: see QUICK_FIX.md. 
GitHub

Replace <your-repo-clone-url> with your repository clone URL when you commit the README.

7. How to Run
Command-line (primary)

A CLI script (main.py) parses an exported WhatsApp chat file and writes summary outputs:

python main.py --input sample_chat.txt --out summary.csv --report report.html


Options may include input path, output CSV path, and whether to generate an HTML report. (See main.py for the exact CLI flags and usage.) 
GitHub
+1

Web interface (optional)

Run the small Flask app to use a browser UI:

python app.py


Then open the local address shown in the console (typically http://127.0.0.1:5000) and upload or paste a chat file. The app generates an interactive report (report.html) in reports/ or shows results in-browser. 
GitHub



Then feed extracted_chat.txt to main.py. See SETUP_OCR.md for platform-specific instructions. 
GitHub
+1

8. Key Features

Robust WhatsApp chat parsing (timestamps, sender, message body).

Output formats: CSV (summary.csv) and an easy-to-read HTML report (report.html).

CLI + minimal web UI.

OCR path for screenshots (setup documented).

Unit test example for parser (test_parser.py) and a sample_chat.txt for quick demos. 
GitHub

9. Project Structure (snapshot)
Whatsapp-chat-analyzer-project-python/
├── app.py                 # small Flask app (web UI)
├── main.py                # CLI parser/runner
├── check_ocr.py           # OCR helper (image -> text)
├── diagnose_file.py       # helper for file diagnostics
├── templates/             # HTML templates (report, index)
├── static/                # CSS / JS assets
├── reports/               # generated HTML reports (output)
├── sample_chat.txt        # example exported chat file
├── summary.csv            # example output
├── report.html            # example report
├── test_parser.py         # parser tests
├── SETUP_OCR.md           # OCR installation notes
├── requirements.txt
└── README.md


(Structure confirmed from repository file listing.) 
GitHub

10. Demonstration

Use sample_chat.txt to run a quick demo locally.

Generated artifacts: summary.csv (tabular summary) and report.html (readable report).

For documentation of OCR setup and troubleshooting, consult SETUP_OCR.md. 
GitHub
+1

11. Challenges Encountered

Handling inconsistent exported chat timestamp formats and different locale date formats.

OCR noise when converting screenshots (requires pre-processing and manual tuning).

Edge-cases in parsing multi-line messages and media-notes (“<Media omitted>”) in chat exports.

12. Scope for Future Enhancements

Add data visualizations (message heatmaps, activity timelines, wordclouds).

Support group vs. individual chat comparisons and trend detection.

Add language detection and stopword sets for multi-lingual chats.

Add CI tests and packaging for pip installation.

Add export to Excel and interactive dashboards.

13. Conclusion

This project provides a practical, extendable tool for extracting useful insights from WhatsApp conversations. It demonstrates parsing logic, optional OCR pipeline, simple reporting, and a mix of CLI and web interfaces to fit different user workflows. 
GitHub

14. Acknowledgements

Thanks to the Hack Culprit team for mentorship and the open-source tools used for OCR and web serving. Also thanks to contributors and testers who helped refine the parser.

15. License

This project is distributed under the MIT License. Add a LICENSE file with the standard MIT text before final release.
