"""
CloudOptix — Database Layer
Uses Python's built-in sqlite3 — zero extra dependencies beyond Flask.
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "cloudoptix.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    role            TEXT DEFAULT 'DevOps Admin',
    avatar_initials TEXT DEFAULT 'PS',
    created_at      TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS user_settings (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER UNIQUE REFERENCES users(id),
    cpu_threshold       INTEGER DEFAULT 80,
    memory_threshold    INTEGER DEFAULT 85,
    daily_cost_limit    REAL    DEFAULT 8500.0,
    email_alerts        INTEGER DEFAULT 1,
    slack_integration   INTEGER DEFAULT 1,
    pagerduty_enabled   INTEGER DEFAULT 0,
    weekly_digest       INTEGER DEFAULT 1,
    updated_at          TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS resources (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    type          TEXT NOT NULL,
    status        TEXT DEFAULT 'Running',
    region        TEXT NOT NULL,
    monthly_cost  REAL DEFAULT 0.0,
    last_activity TEXT DEFAULT (datetime('now')),
    created_at    TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS activity_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    action      TEXT NOT NULL,
    resource_id TEXT,
    region      TEXT,
    status      TEXT,
    timestamp   TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS cost_records (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    date    TEXT NOT NULL,
    amount  REAL NOT NULL,
    service TEXT DEFAULT 'all'
);
CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    severity    TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    action_btn  TEXT DEFAULT 'Acknowledge',
    is_active   INTEGER DEFAULT 1,
    created_at  TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS recommendations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    icon          TEXT DEFAULT 'lightbulb',
    text          TEXT NOT NULL,
    saving_amount REAL NOT NULL,
    is_applied    INTEGER DEFAULT 0
);
"""


def relative_time(dt_str):
    if not dt_str:
        return "unknown"
    try:
        dt = datetime.fromisoformat(dt_str.split(".")[0])
    except Exception:
        return dt_str
    diff = datetime.utcnow() - dt
    s = int(diff.total_seconds())
    if s < 60:    return f"{s} sec ago"
    if s < 3600:  return f"{s // 60} min ago"
    if s < 86400: return f"{s // 3600} hrs ago"
    return f"{s // 86400} days ago"


def fmt_inr(amount):
    return "Rs." + f"{int(amount):,}"


def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    _seed()
    print("CloudOptix DB ready.")


def _seed():
    with get_db() as conn:
        if not conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            conn.execute(
                "INSERT INTO users (name,email,role,avatar_initials) VALUES (?,?,?,?)",
                ("Piyush Singh","piyush@cloudoptix.io","DevOps Admin","PS")
            )
            uid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute("INSERT INTO user_settings (user_id) VALUES (?)", (uid,))

        if not conn.execute("SELECT 1 FROM resources LIMIT 1").fetchone():
            now = datetime.utcnow()
            rows = [
                ("i-0a4f9b1c","prod-web-01","EC2 t3.large","Running","ap-south-1",12400,(now-timedelta(minutes=2)).isoformat()),
                ("i-0b7c3e2d","prod-web-02","EC2 t3.large","Running","ap-south-1",12400,(now-timedelta(minutes=2)).isoformat()),
                ("i-0c9d5f4e","staging-api","EC2 t3.medium","Idle","us-east-1",6200,(now-timedelta(hours=3)).isoformat()),
                ("db-0a1b2c3d","prod-mysql-01","RDS db.t3.medium","Running","ap-south-1",18600,(now-timedelta(minutes=1)).isoformat()),
                ("db-0e5f6a7b","staging-postgres","RDS db.t3.micro","Stopped","eu-west-1",0,(now-timedelta(days=2)).isoformat()),
                ("s3-cloudoptix","cloudoptix-assets","S3 Bucket","Running","ap-south-1",3100,(now-timedelta(minutes=5)).isoformat()),
                ("fn-0x1y2z3w","auth-lambda","Lambda Function","Running","us-east-1",890,(now-timedelta(seconds=30)).isoformat()),
                ("i-0r3s4t5u","analytics-worker","EC2 c5.xlarge","Idle","ap-southeast-1",9800,(now-timedelta(hours=1)).isoformat()),
                ("i-0v6w7x8y","ml-training-01","EC2 p3.2xlarge","Stopped","us-east-1",0,(now-timedelta(days=4)).isoformat()),
                ("db-0g8h9i0j","reporting-redshift","Redshift dc2.large","Running","eu-west-1",22100,(now-timedelta(minutes=10)).isoformat()),
            ]
            conn.executemany(
                "INSERT INTO resources (id,name,type,status,region,monthly_cost,last_activity) VALUES (?,?,?,?,?,?,?)",
                rows
            )

        if not conn.execute("SELECT 1 FROM activity_logs LIMIT 1").fetchone():
            now = datetime.utcnow()
            logs = [
                ("Auto-scaling triggered","i-0a4f9b1c","ap-south-1","Success",(now-timedelta(minutes=28)).isoformat()),
                ("Snapshot created","db-0a1b2c3d","ap-south-1","Success",(now-timedelta(minutes=45)).isoformat()),
                ("High CPU alert fired","i-0c9d5f4e","us-east-1","Warning",(now-timedelta(hours=1,minutes=2)).isoformat()),
                ("Deployment completed","fn-0x1y2z3w","us-east-1","Success",(now-timedelta(hours=1,minutes=38)).isoformat()),
                ("Backup failed","db-0e5f6a7b","eu-west-1","Error",(now-timedelta(hours=2,minutes=13)).isoformat()),
                ("Security group updated","i-0b7c3e2d","ap-south-1","Success",(now-timedelta(hours=3,minutes=30)).isoformat()),
                ("Instance stopped","i-0v6w7x8y","us-east-1","Success",(now-timedelta(hours=4,minutes=45)).isoformat()),
            ]
            conn.executemany(
                "INSERT INTO activity_logs (action,resource_id,region,status,timestamp) VALUES (?,?,?,?,?)",
                logs
            )

        if not conn.execute("SELECT 1 FROM cost_records LIMIT 1").fetchone():
            today = datetime.utcnow().date()
            records = []
            for i in range(29,-1,-1):
                day = (today - timedelta(days=i)).isoformat()
                amt = round(4500 + random.uniform(0,3500) + (29-i)*40, 2)
                records.append((day, amt, "all"))
            conn.executemany("INSERT INTO cost_records (date,amount,service) VALUES (?,?,?)", records)

        if not conn.execute("SELECT 1 FROM alerts LIMIT 1").fetchone():
            now = datetime.utcnow()
            alerts = [
                ("critical","High CPU Utilization","Instance i-0c9d5f4e in us-east-1 has been at 94% CPU for over 15 minutes.","Acknowledge",(now-timedelta(minutes=14)).isoformat()),
                ("warning","Idle Resources Detected","9 instances have been idle for more than 48 hours. Estimated monthly waste: Rs.28,400.","View",(now-timedelta(hours=2)).isoformat()),
                ("critical","Backup Failure","Automated backup for db-0e5f6a7b in eu-west-1 failed. Data protection may be at risk.","Acknowledge",(now-timedelta(hours=3)).isoformat()),
                ("info","Reserved Instance Expiring","3 Reserved Instances in ap-south-1 will expire in 7 days.","Renew",(now-timedelta(days=1)).isoformat()),
            ]
            conn.executemany(
                "INSERT INTO alerts (severity,title,description,action_btn,created_at) VALUES (?,?,?,?,?)",
                alerts
            )

        if not conn.execute("SELECT 1 FROM recommendations LIMIT 1").fetchone():
            recs = [
                ("stop","Terminate 9 idle instances",24200),
                ("refresh","Migrate to Reserved Instances (1yr)",11800),
                ("package","Right-size over-provisioned EC2s",2400),
            ]
            conn.executemany(
                "INSERT INTO recommendations (icon,text,saving_amount) VALUES (?,?,?)",
                recs
            )

        conn.commit()
