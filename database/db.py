"""
Database access layer for the AI GRC Control Mapping Assistant.
Uses SQLite for portability -- swap get_connection() for a Postgres/MySQL
driver later without touching the rest of the app (all queries go through
this module).
"""
import sqlite3
import os
from itertools import combinations
from database.seed_data import CONTROLS

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "controls.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force_reseed: bool = False):
    """Create schema and seed control data if the DB doesn't exist yet."""
    first_run = not os.path.exists(DB_PATH)
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    if first_run or force_reseed:
        if force_reseed:
            conn.execute("DELETE FROM control_relationships")
            conn.execute("DELETE FROM controls")
        _seed_controls(conn)
        _build_relationships(conn)
        conn.commit()
    conn.close()


def _seed_controls(conn):
    for c in CONTROLS:
        conn.execute(
            """INSERT OR REPLACE INTO controls
               (control_uid, framework, control_id, title, description, category,
                keywords, evidence_requirements, testing_procedures)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (c["control_uid"], c["framework"], c["control_id"], c["title"],
             c["description"], c["category"], c["keywords"],
             c["evidence_requirements"], c["testing_procedures"])
        )


def _build_relationships(conn):
    """Any two controls sharing a `theme` are cross-referenced as related_controls.
    This models the real-world practice of maintaining a common-controls / crosswalk
    matrix across frameworks."""
    by_theme = {}
    for c in CONTROLS:
        by_theme.setdefault(c["theme"], []).append(c["control_uid"])

    for theme, uids in by_theme.items():
        for a, b in combinations(uids, 2):
            conn.execute(
                "INSERT INTO control_relationships (control_uid, related_uid, relationship_type) VALUES (?, ?, ?)",
                (a, b, "maps_to")
            )
            conn.execute(
                "INSERT INTO control_relationships (control_uid, related_uid, relationship_type) VALUES (?, ?, ?)",
                (b, a, "maps_to")
            )


def get_all_controls():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM controls ORDER BY framework, control_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_control(control_uid):
    conn = get_connection()
    row = conn.execute("SELECT * FROM controls WHERE control_uid = ?", (control_uid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_related_controls(control_uid):
    conn = get_connection()
    rows = conn.execute(
        """SELECT c.* FROM control_relationships r
           JOIN controls c ON c.control_uid = r.related_uid
           WHERE r.control_uid = ?""",
        (control_uid,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_frameworks():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT framework FROM controls ORDER BY framework").fetchall()
    conn.close()
    return [r["framework"] for r in rows]


def save_assessment(input_text, source_type, mapped_controls_json, notes=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO assessments (input_text, source_type, mapped_controls, notes) VALUES (?, ?, ?, ?)",
        (input_text, source_type, mapped_controls_json, notes)
    )
    conn.commit()
    conn.close()


def save_gap_assessment(record: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO gap_assessments
           (control_uid, requirement, current_state, maturity_level, has_evidence,
            business_impact, data_sensitivity, regulatory_weight, gap_rating,
            risk_rating, risk_score, recommendation)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (record["control_uid"], record["requirement"], record["current_state"],
         record["maturity_level"], record["has_evidence"], record["business_impact"],
         record["data_sensitivity"], record["regulatory_weight"], record["gap_rating"],
         record["risk_rating"], record["risk_score"], record["recommendation"])
    )
    conn.commit()
    conn.close()


def get_gap_assessments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM gap_assessments ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_ai_system_assessment(record: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO ai_systems
           (system_name, description, privacy_risk, security_risk, bias_risk,
            explainability_risk, accountability_risk, overall_risk, recommendations)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (record["system_name"], record["description"], record["privacy_risk"],
         record["security_risk"], record["bias_risk"], record["explainability_risk"],
         record["accountability_risk"], record["overall_risk"], record["recommendations"])
    )
    conn.commit()
    conn.close()


def get_ai_systems():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM ai_systems ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
