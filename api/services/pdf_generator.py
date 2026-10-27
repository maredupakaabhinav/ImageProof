"""
ImageProof - Digital Evidence Authenticity Analyzer
Service: Forensic PDF Report Generator (ReportLab)

Generates professional, court-admissible-style digital evidence analysis
reports including cryptographic checksums, metadata audit tables,
anomaly findings, and chain-of-custody verification blocks.
"""

import os
import html
from typing import Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def _escape(text: Any) -> str:
    """Escapes HTML/XML entities for ReportLab Paragraph rendering."""
    if text is None:
        return "N/A"
    return html.escape(str(text))

def generate_pdf_report(analysis_record: dict, output_dir: str) -> str:
    """
    Builds a cyber forensics evidence report as a PDF file.
    
    :param analysis_record: Dictionary containing analysis fields:
           case_id, original_filename, file_size, file_format, sha256_hash,
           metadata, anomalies, created_at, notes.
    :param output_dir: Destination folder (e.g. backend/reports)
    :return: Full path to generated PDF report.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    case_id = analysis_record.get("case_id", "CASE-UNKNOWN")
    filename_base = f"Report_{case_id}_{int(datetime.now().timestamp())}.pdf"
    pdf_path = os.path.join(output_dir, filename_base)
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Palette (Cyber Navy & Blue)
    c_primary = colors.HexColor("#0f172a")     # Dark Navy
    c_accent = colors.HexColor("#2563eb")      # Cyber Blue
    c_text = colors.HexColor("#1e293b")        # Dark slate text
    c_light_bg = colors.HexColor("#f8fafc")    # Off-white background
    c_border = colors.HexColor("#cbd5e1")      # Slate border
    c_warning = colors.HexColor("#b45309")     # Amber warning
    c_success = colors.HexColor("#15803d")     # Green verified
    
    # Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_text
    )
    
    mono_style = ParagraphStyle(
        "Mono",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("IMAGEPROOF: DIGITAL FORENSIC EVIDENCE REPORT", title_style))
    story.append(Paragraph(
        "Cryptographic Integrity & Metadata Authenticity Analysis | Enterprise Forensics Edition",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceBefore=0, spaceAfter=12))

    # 2. Case Details Table
    meta = analysis_record.get("metadata", {})
    file_info = meta.get("file_info", {})
    cam_info = meta.get("camera_info", {})
    gps_info = meta.get("gps_info", {})
    anomalies = analysis_record.get("anomalies", {})
    summary = anomalies.get("summary", {})
    
    case_table_data = [
        [
            Paragraph("<b>Case Reference ID:</b>", body_style),
            Paragraph(_escape(case_id), body_style),
            Paragraph("<b>Examination Date:</b>", body_style),
            Paragraph(_escape(analysis_record.get("created_at")), body_style),
        ],
        [
            Paragraph("<b>Evidence Filename:</b>", body_style),
            Paragraph(_escape(analysis_record.get("original_filename")), body_style),
            Paragraph("<b>File Format & Size:</b>", body_style),
            Paragraph(f"{_escape(analysis_record.get('file_format'))} | {_escape(file_info.get('size_formatted'))}", body_style),
        ],
        [
            Paragraph("<b>Dimensions:</b>", body_style),
            Paragraph(f"{file_info.get('width', 'N/A')} x {file_info.get('height', 'N/A')} ({file_info.get('megapixels', 'N/A')})", body_style),
            Paragraph("<b>Forensic Examiner:</b>", body_style),
            Paragraph("Certified Forensic Examiner / Automated Ingest Engine", body_style),
        ]
    ]
    
    t_case = Table(case_table_data, colWidths=[1.4*inch, 2.1*inch, 1.4*inch, 2.1*inch])
    t_case.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_case)
    story.append(Spacer(1, 10))

    # 3. Cryptographic Hash (SHA-256) Box
    story.append(Paragraph("DIGITAL EVIDENCE INTEGRITY VERIFICATION (SHA-256)", h2_style))
    sha_hash = analysis_record.get("sha256_hash", "UNKNOWN")
    hash_data = [
        [
            Paragraph("<b>Cryptographic Algorithm:</b>", body_style),
            Paragraph("SHA-256 (FIPS 180-4 standard, 256-bit bitwise digest)", body_style)
        ],
        [
            Paragraph("<b>Computed Hash:</b>", body_style),
            Paragraph(f"<b>{sha_hash}</b>", mono_style)
        ],
        [
            Paragraph("<b>Forensic Purpose:</b>", body_style),
            Paragraph(
                "Ensures evidence has remained unaltered since acquisition. Any 1-bit alteration "
                "to the file produces a drastically distinct hash (Avalanche Effect).",
                body_style
            )
        ]
    ]
    t_hash = Table(hash_data, colWidths=[1.8*inch, 5.2*inch])
    t_hash.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_hash)
    story.append(Spacer(1, 10))

    # 4. Authenticity Indicators & Forensic Assessment Summary
    story.append(Paragraph("AUTHENTICITY & ANOMALY FINDINGS", h2_style))
    
    findings_list = anomalies.get("findings", [])
    findings_rows = [
        [
            Paragraph("<b>Rule / Indicator</b>", body_style),
            Paragraph("<b>Status</b>", body_style),
            Paragraph("<b>Forensic Finding & Observation</b>", body_style),
            Paragraph("<b>Recommendation</b>", body_style),
        ]
    ]
    
    for item in findings_list:
        status_str = item.get("status", "info").upper()
        if status_str == "WARNING":
            status_p = Paragraph(f"<font color='{c_warning}'><b>[WARNING]</b></font>", body_style)
        elif status_str == "VERIFIED":
            status_p = Paragraph(f"<font color='{c_success}'><b>[VERIFIED]</b></font>", body_style)
        else:
            status_p = Paragraph(f"<font color='{c_accent}'><b>[INFO]</b></font>", body_style)
            
        findings_rows.append([
            Paragraph(f"<b>{_escape(item.get('title'))}</b>", body_style),
            status_p,
            Paragraph(_escape(item.get('finding')), body_style),
            Paragraph(_escape(item.get('recommendation')), body_style),
        ])
        
    t_findings = Table(findings_rows, colWidths=[1.6*inch, 0.9*inch, 2.5*inch, 2.0*inch])
    t_findings.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t_findings)
    story.append(Spacer(1, 10))

    # 5. Core Forensic Metadata Summary Table
    story.append(Paragraph("EXTRACTED FORENSIC METADATA SUMMARY", h2_style))
    meta_summary_data = [
        [
            Paragraph("<b>Camera Make / Model:</b>", body_style),
            Paragraph(f"{_escape(cam_info.get('make'))} {_escape(cam_info.get('model'))}", body_style),
            Paragraph("<b>Original Capture Date:</b>", body_style),
            Paragraph(_escape(meta.get("timestamp_info", {}).get("datetime_original")), body_style),
        ],
        [
            Paragraph("<b>Software Signature:</b>", body_style),
            Paragraph(_escape(cam_info.get("software")), body_style),
            Paragraph("<b>Lens & Optics:</b>", body_style),
            Paragraph(f"{_escape(cam_info.get('lens_model'))} ({_escape(cam_info.get('focal_length'))}, {_escape(cam_info.get('f_number'))})", body_style),
        ],
        [
            Paragraph("<b>GPS Coordinates:</b>", body_style),
            Paragraph(
                f"Lat: {_escape(gps_info.get('latitude'))}, Lng: {_escape(gps_info.get('longitude'))}" if gps_info.get("has_gps") else "Not Recorded (Optional)",
                body_style
            ),
            Paragraph("<b>GPS Altitude:</b>", body_style),
            Paragraph(_escape(gps_info.get("altitude")) if gps_info.get("has_gps") else "N/A", body_style),
        ]
    ]
    t_meta = Table(meta_summary_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 2.0*inch])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # 6. Chain of Custody & Examiner Attestation
    story.append(Paragraph("CHAIN OF CUSTODY & EXAMINER ATTESTATION", h2_style))
    story.append(Paragraph(
        "I hereby certify that the digital evidence described above was processed using standardized "
        "forensic extraction algorithms without alteration of original binary content. The SHA-256 hash "
        "recorded represents the exact byte state at the time of ingest.",
        body_style
    ))
    story.append(Spacer(1, 8))
    
    cert_data = [
        [
            Paragraph("<b>Examiner Name:</b> ___________________________", body_style),
            Paragraph("<b>Signature:</b> ___________________________", body_style),
            Paragraph("<b>Date:</b> ______________", body_style)
        ]
    ]
    t_cert = Table(cert_data, colWidths=[2.5*inch, 2.7*inch, 1.8*inch])
    t_cert.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cert)

    doc.build(story)
    return filename_base
