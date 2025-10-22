import json

def fetch_reports_df(query=None):
    import pandas as pd
    with _conn() as c:
        df = pd.read_sql_query(
            "SELECT id, created_at, reporter_json, organisation_json, purpose_json, incident_json, ransomware_json FROM reports ORDER BY id DESC",
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
            "Email": reporter.get('email',''),
            "Organisation": org.get('name',''),
            "Jurisdiction": org.get('jurisdiction',''),
            "Incident Type": inc.get('type',''),
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

from utils.routing import shape_for_destination
def get_destination_json(report_id: int, dest: str) -> str:
    with _conn() as c:
        cur = c.cursor()
        cur.execute("SELECT reporter_json, organisation_json, purpose_json, incident_json, ransomware_json FROM reports WHERE id=?", (report_id,))
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
    return json.dumps(shape_for_destination(dest, payload), indent=2)

def save_report(report, attachments=None) -> int:
    # minimal save that works with our Pydantic Report (dict-like)
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            "INSERT INTO reports (reporter_json, organisation_json, purpose_json, incident_json, ransomware_json) VALUES (?,?,?,?,?)",
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
