"""
ImageProof - Digital Evidence Authenticity Analyzer
Module: Database Management (SQLite)

Provides a lightweight, zero-configuration local database to persist
digital evidence analysis records, hashes, metadata, and anomaly findings.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/imageproof.db"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imageproof.db")

def get_db_connection():
    """Returns a SQLite connection configured with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_format TEXT NOT NULL,
            sha256_hash TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            anomalies_json TEXT NOT NULL,
            report_filename TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(
    case_id: str,
    original_filename: str,
    stored_filename: str,
    file_size: int,
    file_format: str,
    sha256_hash: str,
    metadata: Dict[str, Any],
    anomalies: Dict[str, Any],
    report_filename: Optional[str] = None,
    notes: Optional[str] = None
) -> int:
    """Inserts a new evidence analysis record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO analyses (
            case_id, original_filename, stored_filename, file_size,
            file_format, sha256_hash, metadata_json, anomalies_json,
            report_filename, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        original_filename,
        stored_filename,
        file_size,
        file_format,
        sha256_hash,
        json.dumps(metadata),
        json.dumps(anomalies),
        report_filename,
        notes or "",
        now_str
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def update_report_filename(analysis_id: int, report_filename: str):
    """Associates a generated PDF report filename with an existing record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE analyses SET report_filename = ? WHERE id = ?
    """, (report_filename, analysis_id))
    conn.commit()
    conn.close()

def _format_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Helper to deserialize JSON columns into a clean Python dictionary."""
    data = dict(row)
    try:
        data["metadata"] = json.loads(data["metadata_json"])
    except Exception:
        data["metadata"] = {}
    try:
        data["anomalies"] = json.loads(data["anomalies_json"])
    except Exception:
        data["anomalies"] = {}
        
    del data["metadata_json"]
    del data["anomalies_json"]
    return data

def get_all_analyses(search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieves all analysis records, optionally filtered by keyword."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search:
        query_str = f"%{search}%"
        cursor.execute("""
            SELECT * FROM analyses
            WHERE case_id LIKE ? OR original_filename LIKE ? OR sha256_hash LIKE ?
            ORDER BY id DESC LIMIT ?
        """, (query_str, query_str, query_str, limit))
    else:
        cursor.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,))
        
    rows = cursor.fetchall()
    conn.close()
    return [_format_row(r) for r in rows]

def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single analysis record by its primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return _format_row(row)
    return None

def delete_analysis(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Deletes an analysis record and returns its data for file cleanup."""
    record = get_analysis_by_id(analysis_id)
    if not record:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    conn.commit()
    conn.close()
    return record

def get_stats() -> Dict[str, Any]:
    """Computes summary statistics for the dashboard view."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total_analyzed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT case_id) FROM analyses")
    total_cases = cursor.fetchone()[0]
    
    cursor.execute("SELECT anomalies_json FROM analyses")
    all_anomalies_rows = cursor.fetchall()
    
    warning_cases = 0
    for row in all_anomalies_rows:
        try:
            parsed = json.loads(row[0])
            if parsed.get("summary", {}).get("warning_count", 0) > 0:
                warning_cases += 1
        except Exception:
            pass
            
    # Recent 5 items for dashboard
    cursor.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT 5")
    recent = [_format_row(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        "total_analyzed": total_analyzed,
        "total_cases": total_cases,
        "warning_cases": warning_cases,
        "recent_analyses": recent
    }

def reset_database():
    """Drops and resets the table. Useful for testing and viva demonstration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS analyses")
    conn.commit()
    conn.close()
    init_db()
