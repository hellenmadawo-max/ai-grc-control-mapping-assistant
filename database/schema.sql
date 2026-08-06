-- AI GRC Control Mapping Assistant
-- Core schema: multi-framework control repository + assessment tracking

CREATE TABLE IF NOT EXISTS controls (
    control_uid         TEXT PRIMARY KEY,      -- e.g. "NIST_CSF_PR.AA-05"
    framework           TEXT NOT NULL,         -- e.g. "NIST CSF 2.0"
    control_id          TEXT NOT NULL,         -- e.g. "PR.AA-05"
    title               TEXT NOT NULL,
    description         TEXT NOT NULL,
    category            TEXT,                  -- function/domain, e.g. "Protect"
    keywords            TEXT,                  -- comma-separated tags used by the mapping engine
    evidence_requirements TEXT,
    testing_procedures  TEXT
);

CREATE TABLE IF NOT EXISTS control_relationships (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    control_uid     TEXT NOT NULL,
    related_uid     TEXT NOT NULL,
    relationship_type TEXT DEFAULT 'maps_to',   -- maps_to, equivalent_to, supports
    FOREIGN KEY (control_uid) REFERENCES controls(control_uid),
    FOREIGN KEY (related_uid) REFERENCES controls(control_uid)
);

CREATE TABLE IF NOT EXISTS assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT DEFAULT (datetime('now')),
    input_text      TEXT NOT NULL,             -- requirement / policy excerpt submitted by user
    source_type     TEXT,                      -- 'requirement', 'policy_upload', 'procedure_upload', 'vendor_questionnaire'
    mapped_controls TEXT,                      -- JSON list of {control_uid, confidence}
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS gap_assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT DEFAULT (datetime('now')),
    control_uid     TEXT NOT NULL,
    requirement     TEXT NOT NULL,
    current_state   TEXT NOT NULL,
    maturity_level  INTEGER,                   -- 0-4 (CMMI-style: 0=none .. 4=optimized)
    has_evidence    INTEGER DEFAULT 0,         -- 0/1
    business_impact TEXT,                      -- Low/Medium/High/Critical
    data_sensitivity TEXT,                     -- Low/Medium/High/Critical
    regulatory_weight TEXT,                    -- Low/Medium/High/Critical
    gap_rating      TEXT,                      -- computed: Low/Medium/High/Critical
    risk_rating     TEXT,                      -- computed: Low/Medium/High/Critical
    risk_score      REAL,
    recommendation  TEXT,
    FOREIGN KEY (control_uid) REFERENCES controls(control_uid)
);

CREATE TABLE IF NOT EXISTS ai_systems (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT DEFAULT (datetime('now')),
    system_name     TEXT NOT NULL,
    description     TEXT,
    privacy_risk    TEXT,
    security_risk   TEXT,
    bias_risk       TEXT,
    explainability_risk TEXT,
    accountability_risk TEXT,
    overall_risk    TEXT,
    recommendations TEXT
);

CREATE INDEX IF NOT EXISTS idx_controls_framework ON controls(framework);
CREATE INDEX IF NOT EXISTS idx_gap_control ON gap_assessments(control_uid);
