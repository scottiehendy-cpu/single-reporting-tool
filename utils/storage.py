import os
import json
import uuid
import sqlite3
from typing import List, Optional

from utils.config import DB_PATH
from utils.routing import shape_for_destination

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    ref TEXT UNIQUE,                 -- short reference for drafts/final
    status TEXT DEFAULT 'submitted', -- 'draft' or 'submitted'
    reporter_json TEXT NOT NULL,
    organisation_json TEXT NOT NULL,
    purpose_json TEXT NOT NULL,
    incident_json TEXT NOT NULL,
    ransomware_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_reports_ref ON reports(ref);

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    filename TEXT,
    content BLOB,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);
"""

def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as c:
        c.executescript(SCHEMA)

# ---------- drafts ----------
def _new_ref() -> str:
    return uuid.uuid4().hex[:8].upper()

def save_draft(payload: dict, ref: str | None = None) -> str:
    ref = (ref or _new_ref()).upper()
    with _conn() as c:
        cur = c.cursor()
        cur.execute("SELECT id FROM reports WHERE ref=?", (ref,))
        row = cur.fetchone()
        vals = (
            json.dumps(payload["reporter"]),
            json.dumps(payload["organisation"]),
            json.dumps(payload["purpose"]),
            json.dumps(payload["incident"]),
            json.dumps(payload.get("ransomware")) if payload.get("ransomware") else None,
            ref,
        )
        if row:
            cur.execute(
                "UPDATE reports SET status='draft', reporter_json=?, organisation_json=?, purpose_json=?, incident_json=?, ransomware_json=? WHERE ref=?",
                vals
            )
        else:
            cur.execute(
                "INSERT INTO reports (status, reporter_json, organisation_json, purpose_json, incident_json, ransomware_json, ref) VALUES ('draft',?,?,?,?,?,?)",
                vals
            )
        c.commit()
    return ref

def load_draft(ref: str) -> dict | None:
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            "SELECT reporter_json, organisation_json, purpose_json, incident_json, ransomware_json FROM reports WHERE ref=? AND status='draft'",
            (ref.upper(),)
        )
        row = cur.fetchone()
        if not row: return None
        return {
            "reporter": json.loads(row[0]),
            "organisation": json.loads(row[1]),
            "purpose": json.loads(row[2]),
            "incident": json.loads(row[3]),
            "ransomware": json.loads(row[4]) if row[4] else None,
        }

def submit_from_ref(ref: str) -> int:
    with _conn() as c:
        cur = c.cursor()
        cur.execute("UPDATE reports SET status='submitted' WHERE ref=?", (ref.upper(),))
        cur.execute("SELECT id FROM reports WHERE ref=?", (ref.upper(),))
        row = cur.fetchone()
        c.commit()
    if not row:
        raise ValueError("Draft not found")
    return int(row[0])

# ---------- final save / fetch ----------
def save_report(report, attachments: Optional[List]=None) -> int:
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            "INSERT INTO reports (reporter_json, organisation_json, purpose_json, incident_json, ransomware_json, status) "
            "VALUES (?,?,?,?,?,'submitted')",
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

def fetch_reports_df(query: Optional[str]=None):
    import pandas as pd
    with _conn() as c:
        df = pd.read_sql_query(
            "SELECT id, created_at, ref, status, reporter_json, organisation_json, purpose_json, incident_json FROM reports ORDER BY id DESC",
            c
        )
    rows = []
    for _, r in df.iterrows():
        reporter = json.loads(r["reporter_json"]) if r["reporter_json"] else {}
        org = json.loads(r["organisation_json"]) if r["organisation_json"] else {}
        inc = json.loads(r["incident_json"]) if r["incident_json"] else {}
        summary = f"{inc.get('type','')} — {inc.get('narrative','')[:80]}"
        rows.append({
            "ID": r["id"],
            "Ref": r["ref"] or "",
            "Status": r["status"],
            "Created": r["created_at"],
            "Reporter": f"{reporter.get('first_name','')} {reporter.get('surname','')}",
            "Email": reporter.get('email',''),
            "Organisation": org.get('name',''),
            "Jurisdiction": org.get('jurisdiction',''),
            "Incident Type": inc.get('type',''),
            "Summary": summary,
        })
    import pandas as pd
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
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            "SELECT reporter_json, organisation_json, purpose_json, incident_json, ransomware_json FROM reports WHERE id=?",
            (report_id,)
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
