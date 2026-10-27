"""
ImageProof - End-to-End Test Suite
Tests the complete forensic pipeline across all sample images,
verifying hashing, EXIF parsing, anomaly detection, database records,
and PDF reports.
"""

import os
import sys
import unittest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from app import app
import database

class EndToEndForensicPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.samples_dir = os.path.join(os.path.dirname(__file__), "sample_images")
        
        # Reset database for fresh test
        database.reset_database()

    def test_01_verify_initial_empty_stats(self):
        res = self.client.get("/api/stats")
        data = res.get_json()
        self.assertEqual(data["total_analyzed"], 0)
        self.assertEqual(data["total_cases"], 0)

    def test_02_analyze_authentic_camera_photo(self):
        sample_path = os.path.join(self.samples_dir, "sample_camera_photo.jpg")
        with open(sample_path, "rb") as f:
            res = self.client.post(
                "/api/analyze",
                data={
                    "image": (f, "sample_camera_photo.jpg"),
                    "case_id": "CASE-CAM-001",
                    "notes": "Authentic Nikon Z8 field test capture"
                },
                content_type="multipart/form-data"
            )
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        
        # Verify SHA-256 is 64 hex chars
        self.assertEqual(len(data["sha256_hash"]), 64)
        
        # Verify Camera Metadata
        cam = data["metadata"]["camera_info"]
        self.assertEqual(cam["make"], "Nikon Corporation")
        self.assertEqual(cam["model"], "Nikon Z8")
        
        # Verify GPS Coordinates
        gps = data["metadata"]["gps_info"]
        self.assertTrue(gps["has_gps"])
        self.assertAlmostEqual(gps["latitude"], 28.613889, places=3)
        self.assertAlmostEqual(gps["longitude"], 77.208944, places=3)
        
        # Verify zero tampering warnings
        summary = data["anomalies"]["summary"]
        self.assertEqual(summary["warning_count"], 0)
        self.assertEqual(summary["assessment_class"], "verified")
        
        # Verify PDF report exists
        self.assertIsNotNone(data["report_filename"])
        pdf_res = self.client.get(f"/api/reports/{data['report_filename']}")
        self.assertEqual(pdf_res.status_code, 200)

    def test_03_analyze_photoshop_edited_photo(self):
        sample_path = os.path.join(self.samples_dir, "sample_photoshop_edited.jpg")
        with open(sample_path, "rb") as f:
            res = self.client.post(
                "/api/analyze",
                data={
                    "image": (f, "sample_photoshop_edited.jpg"),
                    "case_id": "CASE-PS-002",
                    "notes": "Suspected Photoshop editing"
                },
                content_type="multipart/form-data"
            )
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        
        # Verify Anomaly Detector caught Photoshop signature
        summary = data["anomalies"]["summary"]
        self.assertGreaterEqual(summary["warning_count"], 1)
        
        findings = data["anomalies"]["findings"]
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("RULE_SOFTWARE_SIGNATURE_DETECTED", rule_ids)
        self.assertIn("RULE_TIMESTAMP_DISCREPANCY", rule_ids)

    def test_04_analyze_stripped_social_media_image(self):
        sample_path = os.path.join(self.samples_dir, "sample_social_media.png")
        with open(sample_path, "rb") as f:
            res = self.client.post(
                "/api/analyze",
                data={
                    "image": (f, "sample_social_media.png"),
                    "case_id": "CASE-WEB-003",
                    "notes": "Downloaded from web messaging app"
                },
                content_type="multipart/form-data"
            )
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        
        # Verify Missing EXIF Rule triggered
        findings = data["anomalies"]["findings"]
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("RULE_EXIF_MISSING", rule_ids)
        self.assertIn("RULE_GPS_ABSENT", rule_ids)
        
        # Verify GPS absence is informational, not false tampering claim
        gps_finding = next(f for f in findings if f["rule_id"] == "RULE_GPS_ABSENT")
        self.assertEqual(gps_finding["status"], "info")

    def test_05_verify_aggregated_stats(self):
        res = self.client.get("/api/stats")
        data = res.get_json()
        self.assertEqual(data["total_analyzed"], 3)
        self.assertEqual(data["total_cases"], 3)
        self.assertEqual(data["warning_cases"], 2)
        self.assertEqual(len(data["recent_analyses"]), 3)

    def test_06_verify_history_search(self):
        # Search for Nikon
        res = self.client.get("/api/history?search=CASE-CAM")
        data = res.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["case_id"], "CASE-CAM-001")

if __name__ == "__main__":
    unittest.main()
