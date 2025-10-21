import os, sqlite3
from utils.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT DEFAULT (datetime('now')),
  reporter_json TEXT,
  organisation_json TEXT,
  purpose_json TEXT,
  incident_json TEXT,
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
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as c:
        c.executescript(SCHEMA)
