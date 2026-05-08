"""
generate_logs.py

Run this FIRST to create web_server_logs.csv before launching the dashboard.

Usage:
    python generate_logs.py
"""

import pandas as pd
import random
from datetime import datetime, timedelta

# ── Configuration ────────────────────────────────────────────────────────────
NUM_RECORDS  = 1200
START_DATE   = datetime(2024, 1, 1)
END_DATE     = datetime(2024, 6, 30)
RANDOM_SEED  = 42
random.seed(RANDOM_SEED)

# ── Country → IP prefix mapping ──────────────────────────────────────────────
COUNTRIES = {
    "United Kingdom": ["80.169",  "86.188",  "128.1"  ],
    "United States":  ["155.55",  "192.0",   "198.51" ],
    "Germany":        ["157.20",  "77.87",   "91.65"  ],
    "France":         ["90.60",   "176.160", "195.101"],
    "India":          ["103.21",  "106.51",  "117.196"],
    "Australia":      ["1.128",   "27.32",   "58.96"  ],
    "Canada":         ["24.48",   "99.224",  "142.0"  ],
    "Japan":          ["1.72",    "27.80",   "36.2"   ],
    "Brazil":         ["177.0",   "179.0",   "186.192"],
    "South Africa":   ["196.0",   "41.0",    "102.176"],
}

# Bias UK/US as primary markets for AI-Solutions (Sunderland HQ)
COUNTRY_WEIGHTS = [0.25, 0.22, 0.10, 0.08, 0.09, 0.06, 0.07, 0.05, 0.05, 0.03]

# ── Pages & request weights ───────────────────────────────────────────────────
PAGES = {
    "/index.html":                   0.18,
    "/about.html":                   0.04,
    "/solutions.html":               0.07,
    "/pricing.html":                 0.05,
    "/contact.php":                  0.04,
    "/blog.html":                    0.03,
    "/schedule-demo.php":            0.11,   # key KPI
    "/events.php":                   0.09,   # promotional events
    "/ai-assistant.php":             0.13,   # AI virtual assistant
    "/prototype.php":                0.06,
    "/jobs/software-engineer.php":   0.05,
    "/jobs/data-analyst.php":        0.05,
    "/jobs/ai-specialist.php":       0.05,
    "/jobs/project-manager.php":     0.03,
    "/jobs/ux-designer.php":         0.02,
}

# HTTP status codes — weighted heavily towards 200
STATUS_CODES   = [200, 200, 200, 200, 200, 304, 404, 500]
HTTP_METHODS   = ["GET", "GET", "GET", "GET", "POST"]   # mostly GET, some POST

# ── Helper functions ──────────────────────────────────────────────────────────
def generate_ip(country: str) -> str:
    prefix = random.choice(COUNTRIES[country])
    return f"{prefix}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta))

def categorise_page(page: str) -> str:
    if "schedule-demo"  in page: return "Schedule Demo"
    if "events"         in page: return "Promotional Events"
    if "ai-assistant"   in page: return "AI Virtual Assistant"
    if "jobs/"          in page: return "Job Listings"
    if "prototype"      in page: return "Prototype Solutions"
    if "solutions"      in page: return "Solutions"
    if "index"          in page: return "Homepage"
    if "pricing"        in page: return "Pricing"
    if "contact"        in page: return "Contact"
    if "about"          in page: return "About"
    if "blog"           in page: return "Blog"
    return "Other"

def get_job_type(page: str):
    mapping = {
        "software-engineer": "Software Engineer",
        "data-analyst":      "Data Analyst",
        "ai-specialist":     "AI Specialist",
        "project-manager":   "Project Manager",
        "ux-designer":       "UX Designer",
    }
    for key, label in mapping.items():
        if key in page:
            return label
    return None

# ── Generate records ──────────────────────────────────────────────────────────
records = []
page_list    = list(PAGES.keys())
page_weights = list(PAGES.values())
country_list = list(COUNTRIES.keys())

for _ in range(NUM_RECORDS):
    country = random.choices(country_list, weights=COUNTRY_WEIGHTS)[0]
    ip      = generate_ip(country)
    dt      = random_datetime(START_DATE, END_DATE)
    page    = random.choices(page_list, weights=page_weights)[0]
    method  = random.choice(HTTP_METHODS)
    status  = random.choice(STATUS_CODES)

    records.append({
        "date":        dt.strftime("%Y-%m-%d"),
        "time":        dt.strftime("%H:%M:%S"),
        "client_ip":   ip,
        "country":     country,
        "method":      method,
        "page":        page,
        "status_code": status,
        "category":    categorise_page(page),
        "job_type":    get_job_type(page),
    })

df = (pd.DataFrame(records)
        .sort_values(["date", "time"])
        .reset_index(drop=True))

df.to_csv("web_server_logs.csv", index=False)
print(f"✅  Generated {NUM_RECORDS} log records → web_server_logs.csv")
print(df[["date", "time", "client_ip", "country", "method", "page", "status_code"]].head(10).to_string(index=False))
