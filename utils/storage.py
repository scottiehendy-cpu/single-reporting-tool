import os
import json
import sqlite3
from typing import List, Optional

from utils.config import DB_PATH
from utils.routing import shape_for_destination

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    reporter_json TEXT NOT NULL,
    organisation_json TEXT NOT NULL,
    purpose_json TEXT NOT NULL,
    incident_json TEXT NOT NULL,
    ransomware_json TEXT
);

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    filename TEXT,
    content BLOB,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);
"""

def _conn():
    # Ensure the data/ directory exists and open a SQLite connection
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as c:
        c.executescript(SCHEMA)

def save_report(report, attachments: Optional[List] = None) -> int:
    """Persist a report (and any uploaded files) and return the new row id."""
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            "INSERT INTO reports (reporter_json, organisation_json, purpose_json, incident_json, ransomware_json) "
            "VALUES (?,?,?,?,?)",
            (
                json.dumps(report.reporter),
                json.dumps(report.organisation),
                json.dumps(report.purpose),
                json.dumps(report.incident),
                json.dumps(report.ransomware) if report.ransomware else None,
            ),
        )
        rid = cur.lastrowid
        if attachments:
            for f in attachments:
                cur.execute(
                    "INSERT INTO attachments (report_id, filename, content) VALUES (?,?,?)",
                    (rid, getattr(f, "name", "file"), f.getvalue()),
                )
        c.commit()
        return rid

def fetch_reports_df(query: Optional[str] = None):
    """Return a flattened pandas DataFrame of saved reports for the dashboard."""
    import pandas as pd
    with _conn() as c:
        df = pd.read_sql_query(
            "SELECT id, created_at, reporter_json, organisation_json, purpose_json, incident_json, ransomware_json "
            "FROM reports ORDER BY id DESC",
            c,
        )

    rows = []
    for _, r in df.iterrows():
        reporter = json.loads(r["reporter_json"]) if r["reporter_json"] else {}
        org = json.loads(r["organisation_json"]) if r["organisation_json"] else {}
        inc = json.loads(r["incident_json"]) if r["incident_json"] else {}
        summary = f"{inc.get('type','')} — {inc.get('narrative','')[:80]}"
        rows.append({
            "ID": r["id"],
            "Created": r["created_at"],
            "Reporter": f"{reporter.get('first_name','')} {reporter.get('surname','')}",
            "Email": reporter.get("email",""),
            "Organisation": org.get("name",""),
            "Jurisdiction": org.get("jurisdiction",""),
            "Incident Type": inc.get("type",""),
            "Summary": summary,
        })

    out = pd.DataFrame(rows)
    if query:
        q = query.lower()
        mask = out.apply(lambda s: s.astype(str).str.lower().str.contains(q, na=False))
        out = out[mask.any(axis=1)]
    return out

def purge_all():
    with _conn() as c:
        c.execute("DELETE FROM attachments")
        c.execute("DELETE FROM reports")
        c.commit()

def get_destination_json(report_id: int, dest: str) -> str:
    """Load a saved report and return destination-shaped JSON."""
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            "SELECT reporter_json, organisation_json, purpose_json, incident_json, ransomware_json "
            "FROM reports WHERE id=?",
            (report_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Report {report_id} not found")

        payload = {
            "reporter": json.loads(row[0]),
            "organisation": json.loads(row[1]),
            "purpose": json.loads(row[2]),
            "incident": json.loads(row[3]),
            "ransomware": json.loads(row[4]) if row[4] else None,
        }

    shaped = shape_for_destination(dest, payload)
    return json.dumps(shaped, indent=2)
