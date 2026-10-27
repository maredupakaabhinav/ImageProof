"""
ImageProof - Backend Test Suite
Executes automated integration tests against the Flask backend services,
database, metadata extraction, hashing, anomaly rules, and PDF generation.
"""

import os
import io
import json
import hashlib
import unittest
from PIL import Image

from app import app
import database

class ImageProofBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        database.init_db()

    def test_01_health_check(self):
        """Verify health check endpoint returns 200 OK and valid status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["storage"]["database_initialized"])

    def test_02_dashboard_stats_empty_or_populated(self):
        """Verify /api/stats endpoint works cleanly."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_analyzed", data)
        self.assertIn("total_cases", data)
        self.assertIn("warning_cases", data)

    def test_03_analyze_valid_png_image(self):
        """Create a valid PNG image in-memory and send it to /api/analyze."""
        img = Image.new("RGB", (200, 150), color=(30, 60, 120))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Expected hash
        expected_hash = hashlib.sha256(img_bytes.getvalue()).hexdigest()

        response = self.client.post(
            "/api/analyze",
            data={
                "image": (img_bytes, "sample_evidence.png"),
                "case_id": "TEST-CASE-001",
                "notes": "Automated unit test sample"
            },
            content_type="multipart/form-data"
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["case_id"], "TEST-CASE-001")
        self.assertEqual(data["original_filename"], "sample_evidence.png")
        self.assertEqual(data["file_format"], "PNG")
        self.assertEqual(data["sha256_hash"], expected_hash)
        self.assertIn("metadata", data)
        self.assertIn("anomalies", data)
        self.assertIsNotNone(data["report_filename"])

        # Check anomaly findings for PNG without EXIF
        findings = data["anomalies"]["findings"]
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("RULE_EXIF_MISSING", rule_ids)
        self.assertIn("RULE_SHA256_FINGERPRINT", rule_ids)

        # Save analysis ID for subsequent test
        self.__class__.created_id = data["id"]
        self.__class__.report_filename = data["report_filename"]

    def test_04_get_analysis_by_id(self):
        """Verify fetching an existing analysis record by ID."""
        response = self.client.get(f"/api/analysis/{self.created_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], self.created_id)
        self.assertEqual(data["case_id"], "TEST-CASE-001")

    def test_05_download_pdf_report(self):
        """Verify that the generated PDF report exists and can be retrieved."""
        response = self.client.get(f"/api/reports/{self.report_filename}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertTrue(len(response.data) > 1000)

    def test_06_reject_invalid_extension(self):
        """Verify upload rejection of unauthorized extensions (e.g. .txt)."""
        fake_file = io.BytesIO(b"This is not an image file.")
        response = self.client.post(
            "/api/analyze",
            data={
                "image": (fake_file, "malicious_script.txt")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Unsupported file format", data["error"])

    def test_07_reject_fake_image_binary(self):
        """Verify upload rejection of executable/text file renamed to .jpg."""
        fake_binary = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00FakePEHeader")
        response = self.client.post(
            "/api/analyze",
            data={
                "image": (fake_binary, "fake_photo.jpg")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Invalid or corrupt image file", data["error"])

    def test_08_history_retrieval(self):
        """Verify /api/history returns the list of analyses."""
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]["case_id"], "TEST-CASE-001")

if __name__ == "__main__":
    unittest.main()
