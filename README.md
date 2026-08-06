# AI GRC Control Mapping Assistant

An AI-powered platform that helps security, risk, and compliance teams map cybersecurity
controls across multiple frameworks, identify gaps, score risk, and govern AI systems —
built as a working demonstration of GRC automation for enterprise environments.

**Built by:** Hellen
 | Sr. Compliance Analyst, Banking & Fintech GRC
**Target roles this project is designed to demonstrate readiness for:** AI Governance Analyst,
AI Risk Analyst, GRC Automation Engineer, Cybersecurity Risk Analyst

---

## Business Problem

Enterprise GRC teams spend enormous manual effort cross-walking requirements against
overlapping frameworks (NIST CSF, NIST 800-53, ISO 27001, PCI DSS, SOC 2), and increasingly
now also AI-specific governance frameworks (NIST AI RMF, ISO/IEC 42001). Control mapping,
gap identification, and risk scoring are typically done in spreadsheets, which don't scale,
aren't auditable, and can't be reused across engagements.

## Solution

This application automates the core GRC workflow end-to-end:

1. **Control Repository** — a normalized, cross-framework database spanning 11 frameworks:
   NIST CSF 2.0, NIST SP 800-53 Rev5, ISO/IEC 27001:2022, PCI DSS 4.0, SOC 2 TSC (traditional
   controls), OWASP LLM Top 10, OWASP API Top 10, OWASP Web Top 10, MITRE ATT&CK, MITRE ATLAS
   (threats and attack techniques), and the EU AI Act (legal requirements) — each entry tagged
   with an `entry_type` (control / threat / attack_technique / legal_requirement) so threats and
   attack techniques can be traced to the traditional controls that mitigate them
2. **AI Mapping Engine** — takes free text (a requirement, policy, procedure, or vendor
   questionnaire response) and recommends the controls it satisfies, with a confidence score
   and an explainable rationale
3. **Gap Analysis** — compares current-state implementation to a required control state and
   derives a defensible gap rating
4. **Risk Scoring** — a transparent, weighted-factor model (not a black box) that combines
   control maturity, evidence availability, business impact, data sensitivity, and regulatory
   weight into a Critical/High/Medium/Low rating
5. **Reporting Dashboard** — aggregate risk posture, a risk heat map, and one-click downloadable
   executive summary, control mapping, and risk assessment reports
6. **AI Governance Module** — assesses AI systems against NIST AI RMF and ISO/IEC 42001 risk
   dimensions (privacy, security, bias/fairness, explainability, accountability)

## Why the mapping engine is rule-based by default

GRC findings need to be defensible to auditors and examiners — "the AI said so" is not an
acceptable answer in an audit. The mapping engine's default scoring model is a transparent
keyword/phrase-overlap algorithm (see `engine/mapping_engine.py`), so every recommended
control mapping can be traced back to the exact matched terms. An optional enrichment step
calls the **Anthropic Claude API** (if an `ANTHROPIC_API_KEY` is configured) to add a
plain-language rationale and flag anything the rule-based pass may have missed — but the
tool is fully functional and auditable without any API key at all.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  Home │ Control Repository │ AI Mapping │ Gap Analysis │     │
│                Risk Dashboard │ AI Governance                │
└───────────────────────────┬───────────────────────────────────┘
                            │
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ engine/        │  │ database/        │  │ engine/           │
│ mapping_engine │  │ db.py            │  │ report_generator  │
│ gap_analysis   │  │ schema.sql       │  │                    │
│ risk_scoring   │  │ seed_data.py     │  │                    │
│ ai_governance  │  │ (SQLite)         │  │                    │
└───────┬────────┘  └──────────────────┘  └──────────────────┘
        │
        ▼
┌────────────────────────┐
│ Anthropic Claude API    │  (optional enrichment — LLM rationale)
│ (ANTHROPIC_API_KEY)     │
└────────────────────────┘
```

**Design decisions:**
- **SQLite** for the initial data layer — zero-config, portable, and the schema
  (`database/schema.sql`) is written so swapping in Postgres later only requires changing
  the connection string in `database/db.py`.
- **Modular engine layer** — mapping, gap analysis, risk scoring, and AI governance are
  independent, unit-tested Python modules with no Streamlit dependency, so they could be
  lifted into an API service (FastAPI, etc.) without rewriting logic.
- **Cross-framework relationships are theme-derived** — every control in the seed dataset
  carries a `theme` tag (e.g. `access_control_mfa`, `encryption_data_protection`); controls
  sharing a theme are automatically cross-referenced as "related controls" at load time,
  modeling the common-controls/crosswalk matrix GRC teams maintain by hand today.

## Technologies Used

- **Frontend:** Streamlit (multipage app)
- **Backend:** Python 3
- **Database:** SQLite
- **AI:** Anthropic Claude API (optional enrichment layer)
- **Libraries:** pandas, pytest

## Project Structure

```
ai-grc-control-mapping-assistant/
├── app.py                          # Streamlit entry point / home page
├── pages/
│   ├── 1_Control_Repository.py
│   ├── 2_AI_Mapping_Engine.py
│   ├── 3_Gap_Analysis.py
│   ├── 4_Risk_Dashboard.py
│   └── 5_AI_Governance.py
├── engine/
│   ├── mapping_engine.py           # Phase 3: AI control mapping
│   ├── gap_analysis.py             # Phase 3: gap rating logic
│   ├── risk_scoring.py             # Phase 4: weighted risk model
│   ├── ai_governance.py            # Phase 6: NIST AI RMF / ISO 42001 assessment
│   └── report_generator.py         # Phase 5: downloadable reports
├── database/
│   ├── schema.sql                  # Phase 1: data model
│   ├── seed_data.py                # Phase 2: 55 controls across 5 frameworks
│   └── db.py                       # connection + query layer
├── data/
│   ├── controls.db                 # generated on first run
│   └── sample_policies/            # sample text files for testing the mapping engine
├── tests/
│   └── test_mapping_engine.py      # pytest suite covering all engine modules
└── requirements.txt
```

## Installation

```bash
git clone <this-repo>
cd ai-grc-control-mapping-assistant
pip install -r requirements.txt

# Optional: enable LLM rationale enrichment in the AI Mapping Engine page
export ANTHROPIC_API_KEY="sk-ant-..."

streamlit run app.py
```

The SQLite database and 55 seed controls are created automatically on first run.

### Running tests

```bash
pytest tests/ -v
```

## Example Use Cases

- **GRC Analyst:** paste a new internal policy requirement and instantly see which controls
  across NIST CSF, NIST 800-53, ISO 27001, PCI DSS, and SOC 2 it maps to — instead of manually
  cross-walking five spreadsheets.
- **Third-Party Risk Analyst:** paste a vendor's security questionnaire response and get an
  instant control mapping plus flags for topics the vendor didn't address.
- **Internal Audit:** use the Gap Analysis module to document current-state vs. required-state
  findings with a defensible, weighted risk score instead of a subjective "High/Medium/Low" guess.
- **AI Governance Analyst:** assess a new AI system (e.g. an LLM-powered chatbot) against
  privacy, security, bias, explainability, and accountability risk dimensions, with
  recommendations traceable to specific NIST AI RMF functions and ISO/IEC 42001 clauses.

## Framework Coverage (Sample Dataset)

The seed dataset includes 92 representative entries (not an exhaustive reproduction of any
standard):

**Traditional controls (55)** across 10 common control domains, each expressed in all five
core frameworks (NIST CSF 2.0, NIST 800-53 Rev5, ISO 27001:2022, PCI DSS 4.0, SOC 2 TSC):
Access Control/MFA · Account Lifecycle Management · Encryption/Data Protection ·
Logging & Monitoring · Vulnerability/Patch Management · Incident Response ·
Third-Party/Vendor Risk · Data Classification & Handling · Security Awareness Training ·
Business Continuity/DR

**Threats (20)** from OWASP LLM Top 10, OWASP API Top 10, and OWASP Web Top 10 — tagged so
they cross-reference the traditional control(s) that mitigate them (e.g. OWASP Web "Broken
Access Control" links to the same `access_control_mfa` theme as NIST 800-53 AC-2).

**Attack techniques (11)** from MITRE ATT&CK (enterprise) and MITRE ATLAS (AI/ML-specific),
representing how adversaries actually operate against the controls above.

**Legal requirements (6)** from the EU AI Act (Articles 6, 9, 10, 13, 14, 15), each mapped
in the AI Governance module to its corresponding NIST AI RMF function and ISO/IEC 42001
clause.

## Roadmap / Suggested Improvements

- Replace the keyword-overlap scoring model with embedding-based semantic similarity
  (e.g. `sentence-transformers` or the Claude API alone) for looser-phrased inputs
- Add PDF/DOCX ingestion (policy documents are rarely plain text)
- Add role-based access control and an audit trail of who ran which assessment
- Expand the control repository beyond the 55-control sample toward full framework coverage
- Add a proper time-series remediation tracker (currently illustrative in the dashboard)
- Migrate SQLite → PostgreSQL for multi-user deployment
