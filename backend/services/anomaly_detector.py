"""
ImageProof - Digital Evidence Authenticity Analyzer
Service: Anomaly Detector & Heuristic Forensics Rules

Cyber Forensics Principles Implemented:
1. Absence of Evidence is Not Evidence of Tampering: Missing metadata often happens
   routinely due to messaging apps (WhatsApp, Telegram) or web services optimizing images.
2. Hash Integrity Scope: SHA-256 confirms bitwise integrity against an authentic 
   baseline; it does not independently prove an image was never manipulated before capture.
3. Software Signatures: Presence of editing software in EXIF flags manual handling or 
   post-processing, requiring examiner scrutiny.
"""

from typing import Dict, Any, List

KNOWN_EDITORS = [
    "photoshop", "gimp", "lightroom", "canva", "picsart", "snapseed", 
    "coreldraw", "paint.net", "affinity", "pixelmator", "vsco", "fotor"
]

def analyze_anomalies(metadata: Dict[str, Any], sha256_hash: str) -> Dict[str, Any]:
    """
    Evaluates extracted metadata against forensic heuristics.
    
    :param metadata: Output dictionary from extract_metadata()
    :param sha256_hash: The computed SHA-256 checksum
    :return: Dictionary containing findings list, summary counts, and forensic assessment.
    """
    findings: List[Dict[str, Any]] = []
    
    file_info = metadata.get("file_info", {})
    camera_info = metadata.get("camera_info", {})
    timestamp_info = metadata.get("timestamp_info", {})
    gps_info = metadata.get("gps_info", {})
    has_exif = metadata.get("has_exif", False)
    software = (camera_info.get("software") or "").lower()
    
    warning_count = 0
    info_count = 0
    verified_count = 0
    
    # -------------------------------------------------------------------------
    # RULE 1: EXIF Metadata Block Presence
    # -------------------------------------------------------------------------
    if not has_exif:
        warning_count += 1
        findings.append({
            "rule_id": "RULE_EXIF_MISSING",
            "title": "EXIF Metadata Block Absent",
            "status": "warning",
            "severity": "medium",
            "finding": "No exchangeable image file format (EXIF) header was found in this file.",
            "forensic_explanation": (
                "Original camera photos typically contain EXIF headers. However, popular messaging "
                "platforms (WhatsApp, Signal, Instagram) and web compressors routinely strip EXIF "
                "to protect user privacy and reduce bandwidth. Alternatively, metadata scrubbing "
                "tools may have been used intentionally."
            ),
            "recommendation": (
                "Do not label the image as fraudulent on this basis alone. Verify if the image was "
                "transmitted through social media, or request the raw camera original."
            )
        })
    else:
        verified_count += 1
        findings.append({
            "rule_id": "RULE_EXIF_PRESENT",
            "title": "EXIF Metadata Block Identified",
            "status": "verified",
            "severity": "neutral",
            "finding": f"Detected valid EXIF headers containing {len(metadata.get('raw_exif', {}))} parameters.",
            "forensic_explanation": (
                "Standard EXIF data structure is present, allowing investigation of device, optics, "
                "and capture parameters."
            ),
            "recommendation": "Review individual EXIF tags for consistency with claimed evidence context."
        })

    # -------------------------------------------------------------------------
    # RULE 2: Camera Hardware Identifiers
    # -------------------------------------------------------------------------
    make = camera_info.get("make")
    model = camera_info.get("model")
    
    if has_exif:
        if not make and not model:
            warning_count += 1
            findings.append({
                "rule_id": "RULE_CAMERA_HARDWARE_ABSENT",
                "title": "Camera Hardware Information Unavailable",
                "status": "warning",
                "severity": "medium",
                "finding": "EXIF metadata is present, but camera manufacturer (Make) and Model are missing.",
                "forensic_explanation": (
                    "Physical camera sensors typically embed camera hardware identifiers. The absence "
                    "of Make and Model while other tags exist often occurs when images are created via "
                    "graphic design software, screenshots, or partial metadata editors."
                ),
                "recommendation": "Corroborate whether the evidence source was a physical camera or digital rendering."
            })
        else:
            verified_count += 1
            findings.append({
                "rule_id": "RULE_CAMERA_HARDWARE_FOUND",
                "title": "Camera Hardware Metadata Verified",
                "status": "verified",
                "severity": "neutral",
                "finding": f"Device identified as {make or 'Unknown Make'} - {model or 'Unknown Model'}.",
                "forensic_explanation": (
                    "Camera identification matches typical direct-from-sensor photo structures."
                ),
                "recommendation": "Compare the identified camera model with the reported equipment in case logs."
            })

    # -------------------------------------------------------------------------
    # RULE 3: Software Signatures & Image Editing Artifacts
    # -------------------------------------------------------------------------
    detected_editor = None
    for editor in KNOWN_EDITORS:
        if editor in software:
            detected_editor = editor.title()
            break
            
    if detected_editor:
        warning_count += 1
        findings.append({
            "rule_id": "RULE_SOFTWARE_SIGNATURE_DETECTED",
            "title": f"Image Editing Software Signature ({detected_editor})",
            "status": "warning",
            "severity": "high",
            "finding": f"Metadata 'Software' tag explicitly references: '{camera_info.get('software')}'.",
            "forensic_explanation": (
                f"The image metadata documents processing by {detected_editor}. While this could indicate "
                "benign resizing, cropping, or color balancing, it also establishes that the file is not "
                "an untouched raw camera capture."
            ),
            "recommendation": (
                "Treat the image as modified. Perform Error Level Analysis (ELA) or request raw sensor "
                "files (CR2, NEF, DNG) for evidentiary validation."
            )
        })
    elif camera_info.get("software"):
        info_count += 1
        findings.append({
            "rule_id": "RULE_SOFTWARE_INFO",
            "title": "Software/Firmware Tag Identified",
            "status": "info",
            "severity": "low",
            "finding": f"Software tag recorded as: '{camera_info.get('software')}'.",
            "forensic_explanation": (
                "Recorded software appears to be camera firmware or mobile OS camera pipeline (e.g. iOS / Android)."
            ),
            "recommendation": "Document firmware version in forensic custody paperwork."
        })

    # -------------------------------------------------------------------------
    # RULE 4: Timestamp Analysis & Inconsistency
    # -------------------------------------------------------------------------
    dt_orig = timestamp_info.get("datetime_original")
    dt_mod = timestamp_info.get("datetime_modified")
    
    if not dt_orig and not dt_mod:
        info_count += 1
        findings.append({
            "rule_id": "RULE_TIMESTAMPS_ABSENT",
            "title": "Capture Timestamps Absent",
            "status": "info",
            "severity": "low",
            "finding": "No DateTimeOriginal or DateTime tags are recorded in the image file.",
            "forensic_explanation": (
                "Timestamps were either omitted at creation or stripped during transmission. "
                "Operating system file modification times only reflect when the file was saved on the local drive."
            ),
            "recommendation": "Rely on external chain-of-custody logs for chronological ordering."
        })
    elif dt_orig and dt_mod and dt_orig != dt_mod:
        info_count += 1
        findings.append({
            "rule_id": "RULE_TIMESTAMP_DISCREPANCY",
            "title": "Capture vs Modification Timestamp Divergence",
            "status": "info",
            "severity": "low",
            "finding": f"Original capture ({dt_orig}) differs from file modification date ({dt_mod}).",
            "forensic_explanation": (
                "A difference between original capture time and last modification time indicates the file "
                "was saved, edited, or re-exported at a later date. This is common when images are organized "
                "in photo management libraries."
            ),
            "recommendation": "Review the timeline between capture and modification for evidentiary relevance."
        })
    elif dt_orig:
        verified_count += 1
        findings.append({
            "rule_id": "RULE_TIMESTAMP_RECORDED",
            "title": "Original Capture Timestamp Intact",
            "status": "verified",
            "severity": "neutral",
            "finding": f"Capture recorded at {dt_orig}.",
            "forensic_explanation": "Device internal clock embedded timestamp at the moment of shutter release.",
            "recommendation": "Verify whether device clock was synchronized to UTC/network time."
        })

    # -------------------------------------------------------------------------
    # RULE 5: GPS Geolocation Assessment
    # -------------------------------------------------------------------------
    if gps_info.get("has_gps"):
        verified_count += 1
        findings.append({
            "rule_id": "RULE_GPS_PRESENT",
            "title": "GPS Geolocation Coordinates Found",
            "status": "verified",
            "severity": "neutral",
            "finding": f"Latitude {gps_info.get('latitude')}, Longitude {gps_info.get('longitude')}.",
            "forensic_explanation": (
                "Satellite geolocation metadata is embedded. This provides valuable geographic context "
                "regarding where the physical camera was situated during capture."
            ),
            "recommendation": "Cross-reference coordinates with Google Maps / GIS to corroborate witness statements."
        })
    else:
        info_count += 1
        findings.append({
            "rule_id": "RULE_GPS_ABSENT",
            "title": "GPS Geolocation Not Present (Optional)",
            "status": "info",
            "severity": "low",
            "finding": "No GPS latitude/longitude coordinates are embedded in this image.",
            "forensic_explanation": (
                "GPS metadata is completely optional. Most dedicated DSLRs lack GPS modules, and "
                "smartphones often disable location tagging by default or prompt users for location privacy. "
                "The lack of GPS coordinates is entirely normal and does NOT indicate evidence tampering."
            ),
            "recommendation": "No corrective action required. Note lack of geolocation in case notes."
        })

    # -------------------------------------------------------------------------
    # RULE 6: Cryptographic Integrity Status (SHA-256)
    # -------------------------------------------------------------------------
    verified_count += 1
    findings.append({
        "rule_id": "RULE_SHA256_FINGERPRINT",
        "title": "Cryptographic Integrity Checksum Generated",
        "status": "verified",
        "severity": "neutral",
        "finding": f"SHA-256 Digest: {sha256_hash[:16]}...{sha256_hash[-8:]}",
        "forensic_explanation": (
            "A 256-bit cryptographic digest was generated. In accordance with forensic standard ISO/IEC 27037, "
            "this hash serves as a verifiable benchmark. If the image is presented in court, recalculating "
            "this hash proves the digital evidence has not suffered bit-level degradation or post-seizure alteration."
        ),
        "recommendation": "Log this SHA-256 checksum into the official chain-of-custody ledger."
    })

    # Overall forensic assessment summary
    if warning_count >= 2:
        assessment_category = "Altered or Re-Saved"
        assessment_label = "Notable Discrepancies / Editing Signatures Detected"
        assessment_class = "warning"
    elif warning_count == 1:
        assessment_category = "Potential Processing / Partial Metadata"
        assessment_label = "Minor Anomalies Requiring Contextual Verification"
        assessment_class = "attention"
    elif not has_exif:
        assessment_category = "Stripped / Social Media Asset"
        assessment_label = "Metadata Stripped (Common in Transmitted Media)"
        assessment_class = "neutral"
    else:
        assessment_category = "Consistent Standard Evidence"
        assessment_label = "EXIF Metadata & Hardware Details Consistent"
        assessment_class = "verified"

    return {
        "summary": {
            "total_checks": len(findings),
            "warning_count": warning_count,
            "info_count": info_count,
            "verified_count": verified_count,
            "assessment_category": assessment_category,
            "assessment_label": assessment_label,
            "assessment_class": assessment_class
        },
        "findings": findings
    }
