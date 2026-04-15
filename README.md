# ☁️ CloudOptix — Backend API

Enterprise Cloud Management Platform — Python/Flask REST API.
Built to serve the CloudOptix frontend dashboard exactly.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# Server starts at: http://localhost:5000
# DB is auto-created as cloudoptix.db (SQLite) on first run
# Seed data is loaded automatically
```

---

## 📁 Project Structure

```
cloudoptix/
├── app.py              ← Flask app factory, blueprint registration
├── database.py         ← SQLAlchemy models + seed data
├── requirements.txt
├── routes/
│   ├── auth.py         ← /api/auth/*
│   ├── dashboard.py    ← /api/dashboard/*
│   ├── resources.py    ← /api/resources/*
│   ├── cost.py         ← /api/cost/*
│   ├── alerts.py       ← /api/alerts/*
│   └── settings.py     ← /api/settings/*
```

---

## 🗃️ Database Models

| Model          | Purpose                                      |
|----------------|----------------------------------------------|
| User           | Profile shown in sidebar (Piyush Singh)      |
| Resource       | Cloud instances — EC2, RDS, S3, Lambda, etc. |
| ActivityLog    | Recent operations table on Dashboard         |
| CostRecord     | Daily spend data for the line chart          |
| Alert          | Active alerts with severity levels           |
| Recommendation | Cost optimization suggestions                |
| UserSettings   | Thresholds, notification toggles             |

---

## 🔌 API Reference

### Auth
| Method | Endpoint            | Description               |
|--------|---------------------|---------------------------|
| GET    | /api/auth/profile   | Get current user profile  |
| POST   | /api/auth/login     | Login with email/password |
| POST   | /api/auth/logout    | Logout                    |

---

### Dashboard
| Method | Endpoint                     | Description                        |
|--------|------------------------------|------------------------------------|
| GET    | /api/dashboard/summary       | All dashboard data in one call ✅  |
| GET    | /api/dashboard/kpis          | KPI cards (total/active/idle/cost) |
| GET    | /api/dashboard/cost-trend    | 30-day line chart data             |
| GET    | /api/dashboard/distribution  | Donut chart by service type        |
| GET    | /api/dashboard/activity      | Recent activity table              |

**Example — KPIs response:**
```json
{
  "success": true,
  "data": {
    "total_instances": 10,
    "active_instances": 6,
    "idle_instances": 2,
    "stopped_instances": 2,
    "monthly_cost": 85490.0,
    "monthly_cost_display": "₹85,490",
    "budget": 201500,
    "budget_variance_pct": -57.6
  }
}
```

---

### Resources
| Method | Endpoint                          | Description                      |
|--------|-----------------------------------|----------------------------------|
| GET    | /api/resources/                   | List all (search/region/status)  |
| GET    | /api/resources/<id>               | Single resource detail           |
| POST   | /api/resources/                   | Provision new resource           |
| PATCH  | /api/resources/<id>/status        | Start or stop instance           |
| DELETE | /api/resources/<id>               | Terminate resource               |
| GET    | /api/resources/regions            | Available regions list           |

**Query params for GET /api/resources/:**
```
?search=prod          → filter by name / ID / type
?region=ap-south-1   → filter by region
?status=Running       → Running | Idle | Stopped
```

**POST body for provisioning:**
```json
{
  "name": "new-api-server",
  "type": "EC2 t3.medium",
  "region": "ap-south-1",
  "monthly_cost": 6200
}
```

**PATCH body for start/stop:**
```json
{ "action": "start" }
{ "action": "stop" }
```

---

### Cost Analysis
| Method | Endpoint                          | Description                          |
|--------|-----------------------------------|--------------------------------------|
| GET    | /api/cost/summary                 | All cost data in one call ✅         |
| GET    | /api/cost/by-service              | Bar chart data (cost per service)    |
| GET    | /api/cost/by-region               | Cost breakdown by region             |
| GET    | /api/cost/savings                 | Savings panel + recommendations      |
| POST   | /api/cost/savings/<id>/apply      | Apply an optimization recommendation |

---

### Alerts
| Method | Endpoint                          | Description                  |
|--------|-----------------------------------|------------------------------|
| GET    | /api/alerts/                      | List all active alerts       |
| GET    | /api/alerts/count                 | Badge count only             |
| POST   | /api/alerts/                      | Create new alert             |
| PATCH  | /api/alerts/<id>/acknowledge      | Acknowledge (dismiss) alert  |
| DELETE | /api/alerts/<id>                  | Hard delete alert            |

---

### Settings
| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | /api/settings/        | Get current settings               |
| PUT    | /api/settings/        | Save all settings                  |
| PATCH  | /api/settings/        | Partial update                     |
| POST   | /api/settings/reset   | Reset to defaults                  |

**PUT body:**
```json
{
  "cpu_threshold": 80,
  "memory_threshold": 85,
  "daily_cost_limit": 8500,
  "email_alerts": true,
  "slack_integration": true,
  "pagerduty_enabled": false,
  "weekly_digest": true
}
```

---

## 🔗 Connecting Frontend to Backend

In your `cloudoptix-dashboard.html`, replace the static JS data arrays
with fetch calls to these endpoints. Example:

```javascript
// Replace static resources array with:
async function loadResources() {
  const res = await fetch('http://localhost:5000/api/resources/');
  const json = await res.json();
  filteredRes = json.data;
  renderResourceTable();
}

// Replace static alertsData with:
async function loadAlerts() {
  const res = await fetch('http://localhost:5000/api/alerts/');
  const json = await res.json();
  alertsData = json.data;
  buildAlerts();
}

// Acknowledge alert:
async function ackAlert(id) {
  await fetch(`http://localhost:5000/api/alerts/${id}/acknowledge`, { method: 'PATCH' });
  loadAlerts();
}
```

---

## 🌍 Regions Supported
- `ap-south-1` (Mumbai)
- `us-east-1` (N. Virginia)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)

---

## ⚙️ Environment Variables

| Variable      | Default                        | Description              |
|---------------|--------------------------------|--------------------------|
| SECRET_KEY    | cloudoptix-dev-secret-2024     | Flask session secret     |
| DATABASE_URL  | sqlite:///cloudoptix.db        | DB connection string     |

For PostgreSQL in production:
```
DATABASE_URL=postgresql://user:pass@localhost/cloudoptix
```
