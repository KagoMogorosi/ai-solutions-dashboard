"""
generate_logs.py
================
Generates synthetic IIS-format web server logs for AI-Solutions.
Adds: continent, region, user_type, device fields for full FR coverage.

Usage:  python generate_logs.py
"""

import pandas as pd
import random
from datetime import datetime, timedelta

NUM_RECORDS = 1200
START_DATE  = datetime(2024, 1, 1)
END_DATE    = datetime(2024, 6, 30)
random.seed(42)

# ── Country metadata ──────────────────────────────────────────────────────────
COUNTRY_META = {
    "United Kingdom": {"continent": "Europe",       "region": "Northern Europe",  "prefixes": ["80.169","86.188","128.1"],   "weight": 0.25},
    "United States":  {"continent": "North America","region": "North America",    "prefixes": ["155.55","192.0","198.51"],   "weight": 0.22},
    "Germany":        {"continent": "Europe",       "region": "Western Europe",   "prefixes": ["157.20","77.87","91.65"],    "weight": 0.10},
    "France":         {"continent": "Europe",       "region": "Western Europe",   "prefixes": ["90.60","176.160","195.101"],"weight": 0.08},
    "India":          {"continent": "Asia",         "region": "South Asia",       "prefixes": ["103.21","106.51","117.196"],"weight": 0.09},
    "Australia":      {"continent": "Oceania",      "region": "Oceania",          "prefixes": ["1.128","27.32","58.96"],     "weight": 0.06},
    "Canada":         {"continent": "North America","region": "North America",    "prefixes": ["24.48","99.224","142.0"],    "weight": 0.07},
    "Japan":          {"continent": "Asia",         "region": "East Asia",        "prefixes": ["1.72","27.80","36.2"],       "weight": 0.05},
    "Brazil":         {"continent": "South America","region": "South America",    "prefixes": ["177.0","179.0","186.192"],   "weight": 0.05},
    "South Africa":   {"continent": "Africa",       "region": "Sub-Saharan Africa","prefixes": ["196.0","41.0","102.176"],   "weight": 0.03},
}

PAGES = {
    "/index.html":                 0.18,
    "/about.html":                 0.04,
    "/solutions.html":             0.07,
    "/pricing.html":               0.05,
    "/contact.php":                0.04,
    "/blog.html":                  0.03,
    "/schedule-demo.php":          0.11,
    "/events.php":                 0.09,
    "/ai-assistant.php":           0.13,
    "/prototype.php":              0.06,
    "/jobs/software-engineer.php": 0.05,
    "/jobs/data-analyst.php":      0.05,
    "/jobs/ai-specialist.php":     0.05,
    "/jobs/project-manager.php":   0.03,
    "/jobs/ux-designer.php":       0.02,
}

STATUS_CODES  = [200,200,200,200,200,304,404,500]
HTTP_METHODS  = ["GET","GET","GET","GET","POST"]
USER_TYPES    = ["New Visitor","Returning Visitor","Returning Visitor","Lead","Prospect"]
DEVICES       = ["Desktop","Desktop","Desktop","Mobile","Mobile","Tablet"]

def get_category(page):
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

def get_job_type(page):
    for key, label in [("software-engineer","Software Engineer"),
                       ("data-analyst","Data Analyst"),
                       ("ai-specialist","AI Specialist"),
                       ("project-manager","Project Manager"),
                       ("ux-designer","UX Designer")]:
        if key in page: return label
    return None

def rand_dt(start, end):
    # weight towards business hours 8-18 for realism
    delta = int((end - start).total_seconds())
    dt = start + timedelta(seconds=random.randint(0, delta))
    # 60% chance of being in business hours
    if random.random() < 0.60:
        dt = dt.replace(hour=random.randint(8, 18))
    return dt

country_list   = list(COUNTRY_META.keys())
country_weights= [COUNTRY_META[c]["weight"] for c in country_list]
page_list      = list(PAGES.keys())
page_weights   = list(PAGES.values())

records = []
for _ in range(NUM_RECORDS):
    country = random.choices(country_list, weights=country_weights)[0]
    meta    = COUNTRY_META[country]
    prefix  = random.choice(meta["prefixes"])
    ip      = f"{prefix}.{random.randint(0,255)}.{random.randint(0,255)}"
    dt      = rand_dt(START_DATE, END_DATE)
    page    = random.choices(page_list, weights=page_weights)[0]
    method  = random.choice(HTTP_METHODS)
    status  = random.choice(STATUS_CODES)

    records.append({
        "date":        dt.strftime("%Y-%m-%d"),
        "time":        dt.strftime("%H:%M:%S"),
        "client_ip":   ip,
        "country":     country,
        "continent":   meta["continent"],
        "region":      meta["region"],
        "method":      method,
        "page":        page,
        "status_code": status,
        "category":    get_category(page),
        "job_type":    get_job_type(page),
        "user_type":   random.choice(USER_TYPES),
        "device":      random.choice(DEVICES),
    })

df = (pd.DataFrame(records)
        .sort_values(["date","time"])
        .reset_index(drop=True))

df.to_csv("web_server_logs.csv", index=False)
print(f"Generated {NUM_RECORDS} records → web_server_logs.csv")
print(df[["date","time","country","continent","region","category","device"]].head(8).to_string(index=False))
