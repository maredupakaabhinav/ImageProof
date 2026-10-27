# ImageProof: Image Metadata & Digital Evidence Authenticity Analyzer

> **B.Tech Cyber Security Capstone Project (2nd Year)**  
> A lightweight, transparent, and beginner-friendly digital forensics web application for image metadata extraction, cryptographic integrity verification, heuristic anomaly detection, and court-admissible-style PDF reporting.

---

## 1. Project Introduction & Objectives

In modern cyber investigations and digital incident response, digital imagery constitutes critical evidence. However, digital images can easily be stripped of context, edited, recompressed, or forged.

**ImageProof** was created to address the two foundational questions of digital evidence examination:
1. **Evidence Integrity (Bitwise Verification):** Has this image file been altered or corrupted in any way since it was seized or ingested into the forensic custody chain?
2. **Evidence Authenticity & Origin (Metadata Forensics):** What camera or software created this file? Was it taken at a specific GPS location? Does the metadata show editing software artifacts (such as Adobe Photoshop or GIMP) or abnormal timestamp discrepancies?

### Core Educational Objectives
- Implement the **ISO/IEC 27037** standard for digital evidence identification, collection, and preservation.
- Demystify cryptographic hashing (**SHA-256**) and explain the **Avalanche Effect** in simple terms.
- Provide explainable, rule-based **Forensic Anomaly Detection** without "black box" claims.
- Generate automated, tamper-evident **Forensic PDF Reports** with chain-of-custody sign-offs.

---

## 2. Technology Stack

Built with simplicity, readability, and zero bloat in mind:

| Layer | Technology | Purpose in Project |
| :--- | :--- | :--- |
| **Frontend** | React 18 + Vite | Fast, responsive Single Page Application (SPA) with component-based UI. |
| **Icons** | Lucide React | Cybersecurity and forensic iconography (shields, hashes, alert badges). |
| **Styling** | Clean Custom CSS | Modern cybersecurity dark navy palette (`#090d16`), responsive layout, no bulky frameworks. |
| **Backend** | Python 3 + Flask | RESTful API server handling validation, processing, and storage. |
| **CORS** | Flask-CORS | Enables seamless local communication between frontend (`:5173`) and backend (`:5000`). |
| **Database** | SQLite 3 | Lightweight, zero-configuration embedded database storing case records and audit trails. |
| **Hashing** | Python `hashlib` | Computes 256-bit SHA-256 cryptographic digests in 64 KB memory-safe chunks. |
| **Image Analysis** | Pillow (`PIL`) | Decodes binary headers, extracts EXIF tags, GPS coordinates, dimensions, and color spaces. |
| **PDF Generation** | ReportLab | Programmatically builds professional forensic audit reports ready for download. |

---

## 3. Folder Structure & File Purpose

```
ImageProof/
│
├── frontend/                     # React Frontend Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Navigation bar & real-time Flask API health monitor
│   │   │   ├── Footer.jsx        # College project footer & demo data reset button
│   │   │   ├── Badge.jsx         # Status pill badge (Verified, Warning, Info)
│   │   │   ├── HashDisplay.jsx   # SHA-256 box with one-click copy & avalanche explanation
│   │   │   ├── MetadataViewer.jsx# 5-tab inspector (File Info, Camera, Dates, GPS, Raw EXIF)
│   │   │   └── AnomaliesViewer.jsx# Rule-by-rule forensic heuristics findings list
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Project intro, cybersecurity primer, and navigation
│   │   │   ├── Dashboard.jsx     # Live case metrics & recent analyses summary table
│   │   │   ├── Upload.jsx        # Drag-and-drop file ingest with live preview & size validation
│   │   │   ├── AnalysisResult.jsx# Comprehensive evidence result, hash view & PDF download
│   │   │   └── History.jsx       # Searchable SQLite case records table with filtering
│   │   ├── services/
│   │   │   └── api.js            # Unified Fetch API client (configured to http://localhost:5000/api)
│   │   ├── App.jsx               # Main React component managing tab navigation & state
│   │   ├── main.jsx              # React DOM entrypoint
│   │   └── index.css             # Cybersecurity dark-navy theme styles
│   ├── package.json              # Frontend npm dependencies and build scripts
│   ├── vite.config.js            # Vite development server configuration
│   └── index.html                # HTML template
│
├── backend/                      # Python Flask Backend
│   ├── app.py                    # Flask REST API endpoints, file validation & routing
│   ├── database.py               # SQLite initialization, CRUD queries & stats aggregator
│   ├── requirements.txt          # Python dependencies (Flask, Flask-Cors, Pillow, reportlab)
│   ├── test_backend.py           # Automated unit test suite verifying all 8 backend endpoints
│   ├── uploads/                  # Secure directory storing uploaded evidence files
│   ├── reports/                  # Generated forensic PDF reports
│   └── services/
│       ├── hasher.py             # SHA-256 chunk-based cryptographic checksum calculator
│       ├── metadata_extractor.py # Pillow EXIF and GPS geolocation coordinate decoder
│       ├── anomaly_detector.py   # Heuristic forensic rule evaluation engine
│       └── pdf_generator.py      # ReportLab court-ready evidence report builder
│
├── sample_images/                # Ready-to-use forensic test images for viva demonstration
│   ├── generate_samples.py       # Script that created the 3 test images below
│   ├── sample_camera_photo.jpg   # Authentic Nikon Z8 camera photo with EXIF & GPS
│   ├── sample_photoshop_edited.jpg# Modified image with Photoshop software tag
│   └── sample_social_media.png   # PNG with stripped metadata (simulating WhatsApp/web)
│
├── test_e2e.py                   # Automated end-to-end integration test across all sample images
└── README.md                     # Comprehensive project documentation & viva guide
```

---

## 4. How the System Works

### 1. The Client-Server Architecture
The React frontend and Flask backend run as two independent processes communicating over standard HTTP:
```
[ Browser / React App ]  ----( HTTP / JSON / Multipart )---->  [ Flask Backend (5000) ]
  (localhost:5173)       <---( JSON Responses / PDF Stream )---         │
                                                                         ├──> Pillow (EXIF/GPS)
                                                                         ├──> Hashlib (SHA-256)
                                                                         ├──> Heuristic Rules
                                                                         ├──> SQLite (imageproof.db)
                                                                         └──> ReportLab (.pdf)
```

1. **Ingest:** The user drops an image file (`.jpg` or `.png`) into the React interface.
2. **Transfer:** React sends the binary file to `POST /api/analyze` using `FormData`.
3. **Validation & Protection:**
   - Enforces a 16 MB maximum file size limit.
   - Generates a collision-resistant UUID filename on the server (e.g. `e4f1a2...jpg`) so uploaded files can never overwrite each other or execute path traversal attacks.
   - Validates the binary header via `PIL.Image.open().verify()` to ensure malicious executables disguised with image extensions (polyglot files) are rejected immediately.
4. **Analysis Pipeline:**
   - `services/hasher.py` calculates the SHA-256 hash.
   - `services/metadata_extractor.py` extracts camera properties and converts GPS degrees/minutes/seconds into decimal coordinates.
   - `services/anomaly_detector.py` evaluates 6 forensic rules.
5. **Persistence & Reporting:**
   - Analysis data and findings are stored in SQLite (`imageproof.db`).
   - `services/pdf_generator.py` compiles an official PDF evidence report in `backend/reports/`.
6. **Response:** Flask returns the complete JSON record to React, which updates the state and renders the analysis result page.

---

## 5. Prerequisites & Installation on Windows

### Prerequisites
- **Python 3.10+** (Tested on Python 3.14): Ensure Python is installed and added to your `PATH`.
- **Node.js 18+** (Tested on Node.js v24): Includes `npm`.
- **Operating System:** Windows 10 or 11 (PowerShell or Command Prompt).

---

### Step-by-Step Installation Commands

#### Step A: Open PowerShell or Command Prompt
Navigate to the project root directory:
```powershell
cd C:\Users\ABHINAV\.gemini\antigravity\scratch\ImageProof
```

#### Step B: Install Backend Dependencies
```powershell
cd backend
python -m pip install -r requirements.txt
cd ..
```

#### Step C: Install Frontend Dependencies
```powershell
cd frontend
npm.cmd install
cd ..
```

---

## 6. How to Run the Project (Two Separate Terminals)

To run the full stack, you need to open **two separate terminal windows**.

### Terminal 1: Start the Flask Backend Server
```powershell
cd C:\Users\ABHINAV\.gemini\antigravity\scratch\ImageProof\backend
python app.py
```
*You should see output similar to:*
```
=================================================================
  IMAGEPROOF: Digital Evidence Authenticity Analyzer
  Backend running at: http://127.0.0.1:5000
  API Health check:   http://127.0.0.1:5000/api/health
=================================================================
```

### Terminal 2: Start the React Frontend Dev Server
Open a second terminal window:
```powershell
cd C:\Users\ABHINAV\.gemini\antigravity\scratch\ImageProof\frontend
npm.cmd run dev
```
*You should see output similar to:*
```
  VITE v6.1.0  ready in 250 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

Now open your web browser (Chrome, Edge, or Firefox) and navigate to:
👉 **`http://localhost:5173/`**

---

## 7. How to Test the Complete Workflow

We have provided three pre-configured test images located in `sample_images/`:

### Test Case 1: Authentic Camera Photo
1. Click **Upload & Analyze** in the navbar.
2. Select or drag-and-drop `sample_images/sample_camera_photo.jpg`.
3. Enter Case ID: `CASE-NIKON-001` and click **Start Forensic Analysis**.
4. **Observed Results:**
   - SHA-256 hash displayed with one-click copy button.
   - Camera verified: **Nikon Corporation - Nikon Z8** with 50mm f/2.8 lens.
   - Capture date: `2026:10:25 14:32:10`.
   - GPS Location: Latitude `28.613889°`, Longitude `77.208944°` with a direct link to open Google Maps.
   - Anomaly Status: **0 Warnings** (Verified Consistent).
   - Click **Download PDF Forensic Report** to view and download the official generated PDF.

### Test Case 2: Photoshop Manipulated Image
1. Upload `sample_images/sample_photoshop_edited.jpg`.
2. Enter Case ID: `CASE-EDIT-002` and click **Start Forensic Analysis**.
3. **Observed Results:**
   - Anomaly Warning: **Image Editing Software Signature (Photoshop)** detected.
   - Observation: Software tag explicitly records `Adobe Photoshop 2024 (Windows)`.
   - Timestamp divergence flagged: Original capture was September 2026, while modification date was October 2026.
   - Status: Flagged with warning badge for investigator scrutiny.

### Test Case 3: Stripped Social Media Asset (PNG)
1. Upload `sample_images/sample_social_media.png`.
2. **Observed Results:**
   - Anomaly Notice: **EXIF Metadata Block Absent**.
   - Forensic Explanation: Explains that messaging platforms (WhatsApp, Telegram) compress and strip metadata for user privacy and bandwidth reduction.
   - GPS Notice: Labeled as **Informational** (GPS is optional and does not imply tampering).

### Test Case 4: Security Rejection (Invalid Extension)
1. Try uploading any `.txt` or `.exe` file.
2. **Observed Results:**
   - Frontend and backend reject the file with an informative message: *"Unsupported file format. Only JPG, JPEG, and PNG images are supported."*

### Test Case 5: Case History & Deletion
1. Open the **Case History** page.
2. Use the search bar to filter by Case ID (e.g. `CASE-NIKON`).
3. Click **Inspect** to review past cases.
4. Click **PDF** to re-download the generated report.

---

## 8. Automated Test Execution

You can run the built-in automated test suites at any time to verify system health without a browser:

### Run Backend Unit Tests (8 tests)
```powershell
cd C:\Users\ABHINAV\.gemini\antigravity\scratch\ImageProof\backend
python test_backend.py
```
*(Tests health check, stats, PNG hashing, ID lookup, PDF download, extension validation, binary header verification, and history).*

### Run End-to-End Pipeline Tests (6 tests)
```powershell
cd C:\Users\ABHINAV\.gemini\antigravity\scratch\ImageProof
python test_e2e.py
```
*(Tests all 3 sample images, verifies EXIF extraction, anomaly heuristic evaluation, and SQLite aggregation).*

---

## 9. Forensic Technical Details (For Viva Preparation)

### A. How SHA-256 Cryptographic Hashing Works
- **Algorithm:** Secure Hash Algorithm 256-bit (FIPS 180-4 standard).
- **Fixed Output:** Produces a 64-character hexadecimal string regardless of file size.
- **The Avalanche Effect:** If an attacker modifies even a single pixel in an 8-megapixel photo, more than 50% of the bits in the output hash will change unpredictably.
- **Forensic Scope:** Proves that an evidence file in the lab is bit-for-bit identical to the file seized at the crime scene.

### B. How EXIF Metadata Extraction Works
- **EXIF (Exchangeable Image File Format):** Metadata standard embedded in JPEG and TIFF headers (APP1 marker `0xFFE1`).
- **Pillow Implementation:** Pillow opens the image stream, calls `img.getexif()`, and resolves numerical tag IDs using `PIL.ExifTags.TAGS` (for standard EXIF) and `GPSTAGS` (for satellite tags).
- **GPS Coordinates Calculation:** Raw GPS coordinates are stored as rational degree, minute, and second tuples (e.g. `((28, 1), (36, 1), (50, 1))` with ref `N`). ImageProof converts them to standard decimal degrees using:
  $$\text{Decimal Degrees} = \text{Degrees} + \frac{\text{Minutes}}{60} + \frac{\text{Seconds}}{3600}$$
  If the reference is South (`S`) or West (`W`), the value is multiplied by $-1$.

### C. Forensic Anomaly Heuristic Rules
| Rule Identifier | Trigger Condition | Forensic Meaning |
| :--- | :--- | :--- |
| **RULE_EXIF_MISSING** | Image file contains no EXIF block. | Common in web exports and social messaging apps; warrants origin inquiry. |
| **RULE_CAMERA_HARDWARE_ABSENT** | EXIF is present, but Make/Model is blank. | Suggests image originated from a digital illustration tool or screenshot. |
| **RULE_SOFTWARE_SIGNATURE** | Software tag matches Photoshop, GIMP, Canva, etc. | Proves image was processed or re-exported by an editing program. |
| **RULE_TIMESTAMP_DISCREPANCY** | `DateTimeOriginal` differs from `DateTime`. | File was altered or saved at a later date after camera shutter release. |
| **RULE_GPS_ABSENT** | No GPS IFD tags found. | Optional attribute; informational only, does not indicate tampering. |
| **RULE_SHA256_FINGERPRINT** | Checksum computed. | Establishes cryptographic baseline for chain of custody. |

---

## 10. Common Errors & Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **Navbar says "API Offline"** | Flask backend server is not running on port 5000. | Open a terminal, run `cd backend; python app.py`, and check that `http://127.0.0.1:5000/api/health` responds. |
| **`npm : File cannot be loaded because running scripts is disabled`** | Windows PowerShell ExecutionPolicy restriction. | Use `npm.cmd run dev` instead of `npm run dev`. |
| **"File too large. Maximum allowed size is 16MB"** | Uploaded image exceeds 16 MB. | Choose a file smaller than 16 MB or compress the test image. |
| **"Invalid or corrupt image file"** | A `.txt` or `.exe` file was renamed to `.jpg`. | Pillow header validation caught the file. Upload a genuine image. |
| **Port 5000 or 5173 already in use** | A previous instance is still running in the background. | In PowerShell, run `Get-Process python` or `Stop-Process -Name node -Force`. |

---

## 11. Viva Questions & Short Answers

**Q1: What is the difference between image integrity and image authenticity?**  
*Answer:* **Integrity** means the file has not been altered since the moment of acquisition (verified using SHA-256 hash comparison). **Authenticity** means the image genuinely depicts what it claims to depict from the claimed source and device (evaluated through metadata analysis and forensic heuristics).

**Q2: Can we declare an image fake simply because its EXIF metadata is missing?**  
*Answer:* No. Messaging apps like WhatsApp, Telegram, and social platforms automatically strip EXIF metadata to protect user privacy and save network bandwidth. Missing metadata is an anomaly requiring manual context review, not definitive proof of malicious forgery.

**Q3: Why did you use SHA-256 instead of MD5 or SHA-1?**  
*Answer:* MD5 and SHA-1 suffer from known cryptographic collision vulnerabilities where two different inputs can produce identical hashes. SHA-256 remains collision-resistant and complies with modern forensic standards (NIST SP 800-86).

**Q4: How do you prevent malicious executable uploads (e.g. polyglot web shells)?**  
*Answer:* We apply three layers of defense:
1. Strict extension whitelisting (`.jpg`, `.jpeg`, `.png`).
2. Server-side UUID filename generation (prevents path traversal and execution).
3. Binary header verification with `PIL.Image.open().verify()` which checks the actual magic bytes before processing.

**Q5: What is the role of the PDF report in digital forensics?**  
*Answer:* Forensic evidence must be reproducible and court-admissible. The generated PDF report records the case reference, SHA-256 fingerprint, technical parameters, and an examiner attestation sign-off to preserve the legal chain of custody.

---

## 12. Resetting the Local Database & Test Uploads

To restore ImageProof to a fresh state before a project presentation:
1. Open the application in your browser (`http://localhost:5173/`).
2. Scroll to the footer and click the **Reset Demo Data** button.
3. Confirm the dialog. The SQLite database will be cleared, and all uploaded images and generated reports will be cleaned up.

Alternatively, via PowerShell:
```powershell
python -c "import sys; sys.path.insert(0, 'backend'); import database; database.reset_database(); print('Database reset!')"
```

---

## License & Academic Disclaimer
Developed strictly for educational and academic demonstration purposes as part of a 2nd-Year B.Tech Cyber Security curriculum. Complies with beginner-friendly development principles without unnecessary cloud or deployment overhead.
