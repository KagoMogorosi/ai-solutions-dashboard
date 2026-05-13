"""
dashboard.py  –  AI-Solutions IIS Analytics Dashboard (Dark Professional)
=========================================================================
Run:  python dashboard.py
Open: http://127.0.0.1:8050
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table, callback, Output, Input, no_update, ctx, State
from flask import session, redirect
import dash_bootstrap_components as dbc

# ── Credentials ────────────────────────────────────────────────────────────────
USERS = {
    "admin":  "aisolutions2024",
    "kago":   "dashboard123",
    "client": "review2024",
}

# ── Colors ─────────────────────────────────────────────────────────────────────
ACCENT_BLUE = "#0ea5e9"
TEAL        = "#14b8a6"
PURPLE      = "#8b5cf6"
ORANGE      = "#f97316"
PALETTE     = [ACCENT_BLUE, TEAL, "#60a5fa", PURPLE, "#f472b6", ORANGE,
               "#34d399", "#fb923c", "#a78bfa", "#38bdf8"]

# ── Data ───────────────────────────────────────────────────────────────────────
df_master = pd.read_csv("web_server_logs.csv", parse_dates=["date"])
df_master["month"]    = df_master["date"].dt.to_period("M").astype(str)
df_master["hour"]     = pd.to_datetime(df_master["time"], format="%H:%M:%S").dt.hour
df_master["day_name"] = df_master["date"].dt.day_name()

# ── Filter options (computed once from master data) ───────────────────────────
ALL_COUNTRIES  = sorted(df_master["country"].unique().tolist())
ALL_MONTHS     = sorted(df_master["month"].unique().tolist())
ALL_CATEGORIES = sorted(df_master["category"].unique().tolist())
ALL_STATUSES   = sorted(df_master["status_code"].unique().tolist())

def kpi_stats(df):
    daily       = df.groupby("date").size().reset_index(name="requests")
    return {
        "total_req":    len(df),
        "unique_vis":   df["client_ip"].nunique(),
        "total_demos":  (df["category"] == "Schedule Demo").sum(),
        "total_ai":     (df["category"] == "AI Virtual Assistant").sum(),
        "total_events": (df["category"] == "Promotional Events").sum(),
        "total_jobs":   (df["category"] == "Job Listings").sum(),
        "success_rate": round((df["status_code"] == 200).mean() * 100, 1),
        "mean_daily":   round(daily["requests"].mean(), 1),
        "std_daily":    round(daily["requests"].std(), 1),
        "daily":        daily,
    }

# ── App ────────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    ],
    title="AI-Solutions Analytics",
    suppress_callback_exceptions=True,
)

server = app.server
server.secret_key = os.environ.get("SECRET_KEY", "ai-solutions-secret-2024")

app.index_string = """
<!DOCTYPE html>
<html style="height:100%;overflow:hidden;">
<head>
    {%metas%}<title>{%title%}</title>{%favicon%}{%css%}
    <style>
        *, *::before, *::after { box-sizing: border-box; margin:0; padding:0; }

        html, body {
            height: 100vh; width: 100vw;
            overflow: hidden !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg,
                #0b1728 0%, #0f1f3d 35%, #1a2c4f 65%, #1e3a66 100%) fixed;
            color: #e2e8f0;
        }
        #react-entry-point, ._dash-loading, .dash-renderer { height:100%; }

        /* ── LOGIN ── */
        .login-wrap {
            display:flex; align-items:center; justify-content:center;
            height:100vh; width:100vw;
        }
        .login-card {
            background:rgba(22,35,63,0.97);
            border:1px solid rgba(103,232,249,0.2);
            border-radius:20px; padding:48px 44px 40px 44px;
            width:420px; box-shadow:0 20px 60px rgba(0,0,0,0.5);
        }
        .login-logo { text-align:center; margin-bottom:10px; }
        .login-logo .bi { font-size:3rem; color:#67e8f9; }
        .login-title { text-align:center; font-size:1.4rem; font-weight:700; color:#bae6fd; margin-bottom:4px; }
        .login-sub   { text-align:center; font-size:0.8rem; color:#64748b; margin-bottom:32px; }
        .login-label { font-size:0.78rem; font-weight:600; color:#94a3b8; margin-bottom:6px;
                       text-transform:uppercase; letter-spacing:0.6px; }
        .login-input {
            width:100%; background:#1e3a5f !important;
            border:1.5px solid #67e8f9 !important; border-radius:10px !important;
            color:#f1f5f9 !important; padding:12px 14px !important;
            font-size:0.95rem !important; margin-bottom:18px;
            outline:none; transition:border-color 0.2s,box-shadow 0.2s; display:block;
        }
        .login-input:focus {
            border-color:#38bdf8 !important;
            box-shadow:0 0 0 4px rgba(103,232,249,0.25) !important;
            background:#1e3a5f !important;
        }
        .login-btn {
            width:100%; background:linear-gradient(135deg,#0ea5e9,#14b8a6) !important;
            border:none !important; border-radius:10px !important; color:white !important;
            font-size:0.95rem !important; font-weight:700 !important; padding:13px !important;
            margin-top:6px; cursor:pointer; transition:opacity 0.2s,transform 0.15s;
        }
        .login-btn:hover { opacity:0.9; transform:translateY(-1px); }
        .login-error {
            background:rgba(220,38,38,0.15); border:1px solid rgba(220,38,38,0.4);
            border-radius:8px; color:#fca5a5; font-size:0.83rem;
            padding:10px 14px; margin-bottom:16px; text-align:center;
        }
        .login-footer { text-align:center; font-size:0.72rem; color:#334155; margin-top:28px; }

        /* ── DASHBOARD SHELL ── */
        .main-wrap {
            display:flex; flex-direction:column;
            height:100vh; width:100%;
            padding:10px 16px 8px 16px; overflow:hidden;
        }
        .hdr {
            flex:0 0 auto; display:flex; align-items:center;
            justify-content:space-between; padding-bottom:6px;
            border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:6px;
        }
        .hdr h2 { color:#bae6fd; font-size:1.18rem; font-weight:700; margin:0; }
        .hdr p  { color:#94a3b8; font-size:0.72rem; margin:0; }

        /* ── KPI STRIP ── */
        .kpi-strip {
            flex:0 0 auto; display:flex; gap:7px; margin-bottom:7px;
        }
        .kpi-box {
            flex:1; background:rgba(22,35,63,0.85);
            border:1px solid rgba(148,163,184,0.15); border-radius:10px;
            padding:6px 10px; box-shadow:0 4px 15px rgba(0,0,0,0.25);
            display:flex; align-items:center; gap:8px; min-width:0;
        }
        .kpi-icon { font-size:1.3rem; flex-shrink:0; color:#67e8f9; }
        .kpi-val  { font-size:0.95rem; font-weight:700; color:#f1f5f9; line-height:1.1; }
        .kpi-lbl  { font-size:0.6rem; color:#94a3b8; line-height:1.2; }

        /* ── FILTER BAR ── */
        .filter-bar {
            flex:0 0 auto; display:flex; align-items:center;
            gap:8px; margin-bottom:7px;
            background:rgba(15,23,42,0.7);
            border:1px solid rgba(103,232,249,0.12);
            border-radius:10px; padding:6px 12px;
        }
        .filter-label {
            font-size:0.68rem; font-weight:700; color:#67e8f9;
            text-transform:uppercase; letter-spacing:0.7px;
            white-space:nowrap; flex-shrink:0;
        }
        .filter-bar .Select-control {
            background:#16233f !important; border:1px solid rgba(103,232,249,0.25) !important;
            border-radius:7px !important; min-height:28px !important; color:#e2e8f0;
        }
        .filter-bar .Select-placeholder,
        .filter-bar .Select-value-label { color:#94a3b8 !important; font-size:0.75rem !important; }
        .filter-bar .Select-value { color:#e2e8f0 !important; }
        .filter-bar .Select-menu-outer {
            background:#16233f !important; border:1px solid rgba(103,232,249,0.2) !important;
            border-radius:8px !important; z-index:9999 !important;
        }
        .filter-bar .Select-option { color:#e2e8f0 !important; font-size:0.75rem !important;
            background:#16233f !important; }
        .filter-bar .Select-option.is-focused { background:#1e3a5f !important; }
        .filter-bar .Select-option.is-selected { background:rgba(14,165,233,0.3) !important; }
        .filter-bar .Select--multi .Select-value {
            background:rgba(14,165,233,0.2) !important;
            border:1px solid rgba(14,165,233,0.4) !important;
            color:#67e8f9 !important; border-radius:4px !important;
            font-size:0.7rem !important;
        }
        .filter-bar .Select--multi .Select-value-icon { color:#67e8f9 !important; }
        .filter-bar .Select-arrow-zone .Select-arrow { border-top-color:#67e8f9 !important; }
        .filter-bar .Select-clear-zone { color:#94a3b8 !important; }
        .filter-bar .VirtualizedSelectFocusedOption { background:#1e3a5f !important; }
        .filter-active-dot {
            width:7px; height:7px; border-radius:50%;
            background:#67e8f9; flex-shrink:0; display:none;
        }
        .filter-reset-btn {
            background:rgba(103,232,249,0.1) !important;
            border:1px solid rgba(103,232,249,0.25) !important;
            border-radius:7px !important; color:#67e8f9 !important;
            font-size:0.7rem !important; padding:4px 10px !important;
            cursor:pointer; white-space:nowrap; flex-shrink:0;
            transition:background 0.2s;
        }
        .filter-reset-btn:hover { background:rgba(103,232,249,0.2) !important; }
        .filter-count {
            font-size:0.65rem; color:#67e8f9; white-space:nowrap;
            flex-shrink:0; background:rgba(103,232,249,0.1);
            border-radius:6px; padding:2px 8px;
        }

        /* ── TABS ── */
        .nav-tabs {
            flex:0 0 auto;
            border-bottom:2px solid rgba(103,232,249,0.2) !important;
            gap:5px;
        }
        .nav-tabs .nav-link {
            color:#cbd5e1 !important; background:rgba(22,35,63,0.6) !important;
            border:1px solid rgba(148,163,184,0.2) !important;
            border-radius:8px 8px 0 0 !important; padding:6px 13px !important;
            font-size:0.78rem; font-weight:500;
        }
        .nav-tabs .nav-link:hover { background:rgba(22,35,63,0.9) !important; }
        .nav-tabs .nav-link.active {
            color:#0f172a !important; background:#67e8f9 !important;
            font-weight:700 !important; border-bottom-color:transparent !important;
        }
        .nav-tabs .nav-link .bi { margin-right:4px; font-size:0.78rem; }

        /* ── TAB CONTENT ── */
        .tab-content-area {
            flex:1 1 0; display:flex; flex-direction:column;
            overflow:hidden !important; background:rgba(15,23,42,0.6);
            border-radius:0 12px 12px 12px; padding:8px; gap:7px;
        }
        .chart-row { display:flex; flex:1 1 0; gap:7px; min-height:0; overflow:hidden; }
        .chart-panel {
            flex:1 1 0; background:#16233f;
            border:1px solid rgba(148,163,184,0.12); border-radius:12px;
            box-shadow:0 6px 20px rgba(0,0,0,0.3); overflow:hidden;
            display:flex; flex-direction:column; min-height:0;
        }
        .chart-panel .chart-title {
            font-size:0.74rem; font-weight:700; color:#bae6fd;
            padding:7px 12px 4px 12px;
            border-bottom:1px solid rgba(103,232,249,0.12);
            flex:0 0 auto; display:flex; align-items:center; gap:5px;
        }
        .chart-title .bi { color:#67e8f9; font-size:0.78rem; }
        .graph-wrap { flex:1 1 0; min-height:0; overflow:hidden; position:relative; }
        .graph-wrap .dash-graph,
        .graph-wrap .js-plotly-plot,
        .graph-wrap .plot-container { height:100% !important; width:100% !important; }
        .w25{flex:0 0 25% !important;} .w30{flex:0 0 30% !important;}
        .w35{flex:0 0 35% !important;} .w40{flex:0 0 40% !important;}
        .w60{flex:0 0 60% !important;}
        .dt-wrap { flex:1; overflow:auto; padding:5px 7px; }
        .dash-table-container { height:100%; }
        .js-plotly-plot .plotly .bg { fill:transparent !important; }
        .badge { font-size:0.7rem; padding:3px 9px; border-radius:20px; }
        .logout-btn {
            background:rgba(220,38,38,0.15) !important;
            border:1px solid rgba(220,38,38,0.35) !important;
            border-radius:7px !important; color:#fca5a5 !important;
            font-size:0.72rem !important; padding:4px 11px !important;
            cursor:pointer; transition:background 0.2s;
        }
        .logout-btn:hover { background:rgba(220,38,38,0.28) !important; }
        .dt-wrap::-webkit-scrollbar { width:5px; height:5px; }
        .dt-wrap::-webkit-scrollbar-track { background:rgba(255,255,255,0.03); }
        .dt-wrap::-webkit-scrollbar-thumb { background:rgba(103,232,249,0.3); border-radius:3px; }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
"""

# ── Chart layout defaults ──────────────────────────────────────────────────────
CL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=30, l=38, r=10),
    font=dict(family="Segoe UI, sans-serif", size=10, color="#e2e8f0"),
    xaxis=dict(gridcolor="rgba(148,163,184,0.12)", linecolor="rgba(148,163,184,0.25)",
               tickfont=dict(size=9, color="#94a3b8"), title_font=dict(size=10, color="#94a3b8")),
    yaxis=dict(gridcolor="rgba(148,163,184,0.12)", linecolor="rgba(148,163,184,0.25)",
               tickfont=dict(size=9, color="#94a3b8"), title_font=dict(size=10, color="#94a3b8")),
    legend=dict(font=dict(size=9, color="#e2e8f0"), bgcolor="rgba(22,35,63,0.75)",
                bordercolor="rgba(103,232,249,0.2)", borderwidth=1),
    coloraxis_colorbar=dict(thickness=7, len=0.6,
                            tickfont=dict(size=8, color="#94a3b8"),
                            title_font=dict(size=8, color="#94a3b8")),
    autosize=True,
)

def g(fig, **kw):
    fig.update_layout(**{**CL, **kw})
    return fig

def panel(icon_class, title, figure, extra_class=""):
    return html.Div(className=f"chart-panel {extra_class}", children=[
        html.Div(className="chart-title", children=[
            html.I(className=f"bi {icon_class}"), title,
        ]),
        html.Div(className="graph-wrap", children=[
            dcc.Graph(figure=figure, config={"displayModeBar": False},
                      style={"height":"100%","width":"100%"}, responsive=True)
        ])
    ])

def kpi_box(icon_class, value, label):
    return html.Div(className="kpi-box", children=[
        html.I(className=f"bi {icon_class} kpi-icon"),
        html.Div([
            html.Div(value, className="kpi-val"),
            html.Div(label, className="kpi-lbl"),
        ])
    ])

# ── Filter bar (reusable) ──────────────────────────────────────────────────────
def make_filter_bar():
    dd_style = {"flex": "1", "minWidth": "120px", "maxWidth": "200px"}
    return html.Div(className="filter-bar", children=[
        html.Span([html.I(className="bi bi-funnel me-1"), "Filters"],
                  className="filter-label"),

        dcc.Dropdown(
            id="f-country", options=[{"label": c, "value": c} for c in ALL_COUNTRIES],
            value=None, multi=True, placeholder="All Countries",
            style=dd_style, clearable=True,
        ),
        dcc.Dropdown(
            id="f-month", options=[{"label": m, "value": m} for m in ALL_MONTHS],
            value=None, multi=True, placeholder="All Months",
            style=dd_style, clearable=True,
        ),
        dcc.Dropdown(
            id="f-category",
            options=[{"label": c, "value": c} for c in ALL_CATEGORIES],
            value=None, multi=True, placeholder="All Categories",
            style=dd_style, clearable=True,
        ),
        dcc.Dropdown(
            id="f-status",
            options=[{"label": str(s), "value": s} for s in ALL_STATUSES],
            value=None, multi=True, placeholder="All Status Codes",
            style={"flex": "0 0 160px"}, clearable=True,
        ),

        html.Span(id="filter-count", className="filter-count",
                  children=f"{len(df_master):,} records"),

        html.Button([html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset"],
                    id="filter-reset-btn", className="filter-reset-btn", n_clicks=0),
    ])

# ── Login layout ──────────────────────────────────────────────────────────────
login_layout = html.Div(className="login-wrap", children=[
    html.Div(className="login-card", children=[
        html.Div(className="login-logo", children=[html.I(className="bi bi-cpu-fill")]),
        html.Div("AI-Solutions", className="login-title"),
        html.Div("IIS Analytics Dashboard  ·  Sign in to continue", className="login-sub"),
        html.Div(id="login-error"),
        html.Div("Username", className="login-label"),
        dcc.Input(id="login-user", type="text", className="login-input",
                  debounce=False, style={"display":"block"}),
        html.Div("Password", className="login-label"),
        dcc.Input(id="login-pass", type="password", className="login-input",
                  debounce=False, style={"display":"block"}),
        html.Button([html.I(className="bi bi-box-arrow-in-right me-2"), "Sign In"],
                    id="login-btn", className="login-btn", n_clicks=0),
        html.Div("AI-Solutions · Business Intelligence Platform · © 2024",
                 className="login-footer"),
    ])
])

# ── Dashboard layout ───────────────────────────────────────────────────────────
dashboard_layout = html.Div(className="main-wrap", children=[

    # Header
    html.Div(className="hdr", children=[
        html.Div([
            html.H2([html.I(className="bi bi-cpu me-2", style={"color":"#67e8f9"}),
                     "AI-Solutions  ·  IIS Web Server Analytics"]),
            html.P("Business Intelligence Dashboard  ·  Jan – Jun 2024"),
        ]),
        html.Div([
            dbc.Badge([html.I(className="bi bi-circle-fill me-1",
                              style={"fontSize":"0.45rem","verticalAlign":"middle"}),
                       "Live"], color="success", className="me-2"),
            dbc.Badge(f"{len(df_master):,} records", color="primary", className="me-3"),
            html.Button([html.I(className="bi bi-box-arrow-right me-1"), "Logout"],
                        id="logout-btn", className="logout-btn", n_clicks=0),
        ], style={"display":"flex","alignItems":"center"})
    ]),

    # KPI strip (dynamic — updates with filters)
    html.Div(id="kpi-strip", className="kpi-strip"),

    # Filter bar
    make_filter_bar(),

    # Tabs
    dbc.Tabs([
        dbc.Tab(children=[html.I(className="bi bi-bar-chart me-1"), "Overview"],    tab_id="overview"),
        dbc.Tab(children=[html.I(className="bi bi-globe2 me-1"),    "Geographic"],  tab_id="geo"),
        dbc.Tab(children=[html.I(className="bi bi-file-earmark-text me-1"), "Page Analysis"], tab_id="pages"),
        dbc.Tab(children=[html.I(className="bi bi-briefcase me-1"), "Business Insights"], tab_id="business"),
        dbc.Tab(children=[html.I(className="bi bi-activity me-1"), "Statistics"],   tab_id="stats"),
        dbc.Tab(children=[html.I(className="bi bi-table me-1"),    "Raw Logs"],     tab_id="rawlogs"),
    ], id="tabs", active_tab="overview"),

    html.Div(id="tab-out", className="tab-content-area"),
])

# ── Root layout ────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=True),
    dcc.Store(id="auth-store", storage_type="session"),
    html.Div(id="page-content"),
])

# ─────────────────────────────────────────────────────────────────────────────
# AUTH CALLBACKS
# ─────────────────────────────────────────────────────────────────────────────
@callback(Output("page-content","children"), Output("auth-store","data"),
          Input("url","pathname"), Input("auth-store","data"))
def route(pathname, auth_data):
    if auth_data and auth_data.get("logged_in"):
        return dashboard_layout, auth_data
    return login_layout, auth_data

@callback(
    Output("auth-store","data", allow_duplicate=True),
    Output("login-error","children"),
    Output("url","pathname", allow_duplicate=True),
    Input("login-btn","n_clicks"),
    Input("login-pass","n_submit"),
    Input("login-user","n_submit"),
    Input("login-user","value"),
    Input("login-pass","value"),
    prevent_initial_call=True,
)
def handle_login(n_clicks, pass_submit, user_submit, username, password):
    triggered = ctx.triggered_id
    if triggered not in ("login-btn","login-pass","login-user"):
        return no_update, no_update, no_update
    u = (username or "").strip()
    p = (password or "").strip()
    if not u or not p:
        return no_update, html.Div("Please enter both username and password.",
                                   className="login-error"), no_update
    if USERS.get(u) == p:
        return {"logged_in": True, "username": u}, None, "/"
    return no_update, html.Div([html.I(className="bi bi-exclamation-circle me-2"),
                                "Invalid username or password."],
                               className="login-error"), no_update

@callback(
    Output("auth-store","data", allow_duplicate=True),
    Output("url","pathname", allow_duplicate=True),
    Input("logout-btn","n_clicks"),
    prevent_initial_call=True,
)
def handle_logout(n_clicks):
    if n_clicks:
        return {"logged_in": False}, "/login"
    return no_update, no_update

# ─────────────────────────────────────────────────────────────────────────────
# FILTER RESET
# ─────────────────────────────────────────────────────────────────────────────
@callback(
    Output("f-country", "value"),
    Output("f-month",   "value"),
    Output("f-category","value"),
    Output("f-status",  "value"),
    Input("filter-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(n):
    return None, None, None, None

# ─────────────────────────────────────────────────────────────────────────────
# FILTERED DATA HELPER
# ─────────────────────────────────────────────────────────────────────────────
def apply_filters(countries, months, categories, statuses):
    df = df_master.copy()
    if countries:   df = df[df["country"].isin(countries)]
    if months:      df = df[df["month"].isin(months)]
    if categories:  df = df[df["category"].isin(categories)]
    if statuses:    df = df[df["status_code"].isin(statuses)]
    return df

# ─────────────────────────────────────────────────────────────────────────────
# KPI STRIP UPDATE
# ─────────────────────────────────────────────────────────────────────────────
@callback(
    Output("kpi-strip",     "children"),
    Output("filter-count",  "children"),
    Input("f-country",  "value"),
    Input("f-month",    "value"),
    Input("f-category", "value"),
    Input("f-status",   "value"),
)
def update_kpis(countries, months, categories, statuses):
    df = apply_filters(countries, months, categories, statuses)
    k  = kpi_stats(df)
    strip = [
        kpi_box("bi-arrow-down-circle", f"{k['total_req']:,}",   "Total Requests"),
        kpi_box("bi-people",            f"{k['unique_vis']:,}",  "Unique Visitors"),
        kpi_box("bi-calendar-check",    f"{k['total_demos']:,}", "Demo Requests"),
        kpi_box("bi-cpu",               f"{k['total_ai']:,}",    "AI Assistant"),
        kpi_box("bi-megaphone",         f"{k['total_events']:,}","Event Requests"),
        kpi_box("bi-briefcase",         f"{k['total_jobs']:,}",  "Job Listings"),
        kpi_box("bi-check2-circle",     f"{k['success_rate']}%", "Success Rate"),
        kpi_box("bi-graph-up-arrow",    f"{k['mean_daily']}",    "Avg Daily Req."),
    ]
    count_label = f"{k['total_req']:,} records"
    if k['total_req'] < len(df_master):
        count_label += f" of {len(df_master):,}"
    return strip, count_label

# ─────────────────────────────────────────────────────────────────────────────
# TAB CALLBACK
# ─────────────────────────────────────────────────────────────────────────────
@callback(
    Output("tab-out","children"),
    Input("tabs","active_tab"),
    Input("f-country",  "value"),
    Input("f-month",    "value"),
    Input("f-category", "value"),
    Input("f-status",   "value"),
)
def render(tab, countries, months, categories, statuses):
    df   = apply_filters(countries, months, categories, statuses)
    k    = kpi_stats(df)
    daily     = k["daily"]
    mean_daily = k["mean_daily"]
    std_daily  = k["std_daily"]

    if df.empty:
        return [html.Div("No data matches the selected filters.",
                         style={"color":"#94a3b8","padding":"40px","textAlign":"center",
                                "fontSize":"0.9rem"})]

    # ── OVERVIEW ──────────────────────────────────────────────────────────
    if tab == "overview":
        fig_trend = g(px.line(daily, x="date", y="requests",
                              color_discrete_sequence=[ACCENT_BLUE],
                              labels={"date":"","requests":"Requests"}))
        fig_trend.update_traces(line_width=2.5)
        fig_trend.add_hline(y=mean_daily, line_dash="dot", line_color=ORANGE,
                            annotation_text=f"Mean {mean_daily}",
                            annotation_font=dict(size=9, color=ORANGE))

        monthly = df.groupby("month").size().reset_index(name="n")
        fig_monthly = g(px.bar(monthly, x="month", y="n", color="n",
                               color_continuous_scale="Blues", text_auto=True,
                               labels={"month":"","n":"Requests"}))
        fig_monthly.update_layout(xaxis_tickangle=-30)

        sc = df["status_code"].value_counts().rename_axis("s").reset_index(name="n")
        sc["s"] = sc["s"].astype(str)
        fig_status = g(px.pie(sc, values="n", names="s",
                              color_discrete_sequence=PALETTE, hole=0.45),
                       margin=dict(t=10,b=10,l=10,r=10),
                       legend=dict(orientation="h",y=-0.08,x=0.5,xanchor="center",
                                   font=dict(size=9)))
        return [
            html.Div(className="chart-row", children=[
                panel("bi-graph-up",       "Daily Request Trend",    fig_trend),
                panel("bi-pie-chart",      "HTTP Status Code Split", fig_status, "w30"),
            ]),
            html.Div(className="chart-row", children=[
                panel("bi-bar-chart-line", "Monthly Request Totals", fig_monthly),
            ]),
        ]

    # ── GEOGRAPHIC ────────────────────────────────────────────────────────
    elif tab == "geo":
        cc = df.groupby("country").size().reset_index(name="n").sort_values("n", ascending=False)
        fig_bar = g(px.bar(cc, x="country", y="n", color="n",
                           color_continuous_scale="Blues", text_auto=True,
                           labels={"country":"","n":"Requests"}))
        fig_bar.update_layout(xaxis_tickangle=-30)
        fig_pie = g(px.pie(cc, values="n", names="country",
                           color_discrete_sequence=PALETTE, hole=0.35),
                    margin=dict(t=10,b=10,l=10,r=10),
                    legend=dict(font=dict(size=8), orientation="v"))
        top5 = cc.head(5)["country"].tolist()
        mc = (df[df["country"].isin(top5)]
                .groupby(["month","country"]).size().reset_index(name="n"))
        fig_mc = g(px.line(mc, x="month", y="n", color="country",
                           markers=True, color_discrete_sequence=PALETTE,
                           labels={"month":"","n":"Requests","country":""}))
        return [
            html.Div(className="chart-row", children=[
                panel("bi-bar-chart-steps","Requests by Country",       fig_bar),
                panel("bi-pie-chart-fill", "Country Traffic Share",     fig_pie, "w35"),
            ]),
            html.Div(className="chart-row", children=[
                panel("bi-graph-up","Monthly Trend – Top 5 Countries", fig_mc),
            ]),
        ]

    # ── PAGE ANALYSIS ─────────────────────────────────────────────────────
    elif tab == "pages":
        cats = df.groupby("category").size().reset_index(name="n").sort_values("n", ascending=False)
        fig_cat = g(px.bar(cats, x="category", y="n", color="category",
                           color_discrete_sequence=PALETTE, text_auto=True,
                           labels={"category":"","n":"Requests"}))
        fig_cat.update_layout(showlegend=False, xaxis_tickangle=-18)

        pages = (df.groupby("page").size().reset_index(name="n")
                   .sort_values("n", ascending=False).head(10))
        fig_pg = g(px.bar(pages, x="n", y="page", orientation="h",
                          color="n", color_continuous_scale="Blues", text_auto=True,
                          labels={"page":"","n":"Requests"}))
        fig_pg.update_layout(yaxis={"categoryorder":"total ascending"},
                             margin=dict(t=10,b=30,l=150,r=10))

        jdf = df[df["job_type"].notna()]
        fig_jobs = g(px.pie(jdf.groupby("job_type").size().reset_index(name="n"),
                            values="n", names="job_type",
                            color_discrete_sequence=PALETTE, hole=0.38),
                     margin=dict(t=10,b=10,l=10,r=10),
                     legend=dict(font=dict(size=8))) if not jdf.empty else g(go.Figure())

        mc = df.groupby("method").size().reset_index(name="n")
        fig_m = g(px.pie(mc, values="n", names="method",
                         color_discrete_sequence=[ACCENT_BLUE,ORANGE], hole=0.38),
                  margin=dict(t=10,b=10,l=10,r=10), legend=dict(font=dict(size=9)))

        return [
            html.Div(className="chart-row", children=[
                panel("bi-grid-1x2",               "Requests by Category", fig_cat, "w60"),
                panel("bi-arrows-angle-contract",  "HTTP Methods",         fig_m,   "w40"),
            ]),
            html.Div(className="chart-row", children=[
                panel("bi-list-ol",             "Top 10 Pages",      fig_pg),
                panel("bi-person-lines-fill",   "Job Role Requests", fig_jobs),
            ]),
        ]

    # ── BUSINESS INSIGHTS ─────────────────────────────────────────────────
    elif tab == "business":
        biz_cats = ["Schedule Demo","Promotional Events","AI Virtual Assistant","Job Listings"]
        mb = (df[df["category"].isin(biz_cats)]
                .groupby(["month","category"]).size().reset_index(name="n"))
        fig_biz = g(px.bar(mb, x="month", y="n", color="category",
                           barmode="group", color_discrete_sequence=PALETTE,
                           labels={"month":"","n":"Requests","category":""}))

        dc = (df[df["category"]=="Schedule Demo"].groupby("country").size()
                .reset_index(name="n").sort_values("n",ascending=False))
        fig_demo = g(px.bar(dc, x="country", y="n", color="n",
                            color_continuous_scale="Oranges", text_auto=True,
                            labels={"country":"","n":"Demos"}))
        fig_demo.update_layout(xaxis_tickangle=-30)

        ac = (df[df["category"]=="AI Virtual Assistant"].groupby("country").size()
                .reset_index(name="n").sort_values("n",ascending=False))
        fig_ai = g(px.bar(ac, x="country", y="n", color="n",
                          color_continuous_scale="Teal", text_auto=True,
                          labels={"country":"","n":"Requests"}))
        fig_ai.update_layout(xaxis_tickangle=-30)

        pivot = (df[df["category"].isin(["Schedule Demo","AI Virtual Assistant"])]
                   .groupby(["country","category"]).size()
                   .unstack(fill_value=0).reset_index())
        if "Schedule Demo" in pivot.columns and "AI Virtual Assistant" in pivot.columns:
            fig_sc = g(px.scatter(pivot, x="Schedule Demo", y="AI Virtual Assistant",
                                  text="country", color_discrete_sequence=[PURPLE],
                                  labels={"Schedule Demo":"Demo Requests",
                                          "AI Virtual Assistant":"AI Requests"}))
            fig_sc.update_traces(textposition="top center", marker=dict(size=10,opacity=0.8))
        else:
            fig_sc = g(go.Figure())

        return [
            html.Div(className="chart-row", children=[
                panel("bi-bar-chart-line","Monthly Business Activity – Key KPIs", fig_biz),
            ]),
            html.Div(className="chart-row", children=[
                panel("bi-calendar-event", "Demo Requests by Country",        fig_demo),
                panel("bi-cpu",            "AI Assistant Requests by Country", fig_ai),
                panel("bi-diagram-3",      "Demo vs AI Assistant by Country",  fig_sc),
            ]),
        ]

    # ── STATISTICS ────────────────────────────────────────────────────────
    elif tab == "stats":
        fig_hist = g(px.histogram(daily, x="requests", nbins=22,
                                  color_discrete_sequence=[ACCENT_BLUE],
                                  labels={"requests":"Daily Requests","count":"Frequency"}))
        fig_hist.add_vline(x=mean_daily, line_dash="dash", line_color="#ef4444",
                           annotation_text=f"μ={mean_daily}",
                           annotation_font=dict(size=9,color="#ef4444"))
        fig_hist.add_vline(x=mean_daily+std_daily, line_dash="dot", line_color=ORANGE,
                           annotation_text=f"+1σ={mean_daily+std_daily:.1f}",
                           annotation_font=dict(size=9,color=ORANGE))

        hr = df.groupby("hour").size().reset_index(name="n")
        fig_hr = g(px.bar(hr, x="hour", y="n", color="n",
                          color_continuous_scale="Blues",
                          labels={"hour":"Hour (24h)","n":"Requests"}))

        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("day_name").size().reindex(dow_order).reset_index(name="n")
        fig_dow = g(px.bar(dow, x="day_name", y="n", color="n",
                           color_continuous_scale="Teal",
                           labels={"day_name":"","n":"Requests"}))

        cat_d = df.groupby(["date","category"]).size().reset_index(name="c")
        cs = (cat_d.groupby("category")["c"]
                    .agg(["mean","std","sum","max"]).round(2).reset_index())
        cs.columns = ["Category","Daily Mean","Std Dev","Total","Peak"]

        tbl = dash_table.DataTable(
            data=cs.to_dict("records"),
            columns=[{"name":c,"id":c} for c in cs.columns],
            style_header={"backgroundColor":"#0ea5e9","color":"white","fontWeight":"bold",
                          "textAlign":"center","fontSize":"11px","padding":"6px"},
            style_cell={"textAlign":"center","padding":"6px","fontFamily":"Segoe UI,sans-serif",
                        "fontSize":"11px","backgroundColor":"#16233f","color":"#e2e8f0",
                        "border":"1px solid rgba(148,163,184,0.1)"},
            style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#1e2f4e"}],
            page_size=10,
        )
        tbl_panel = html.Div(className="chart-panel", children=[
            html.Div(className="chart-title", children=[
                html.I(className="bi bi-table"), "Per-Category Daily Statistics"]),
            html.Div(className="dt-wrap", children=[tbl]),
        ])

        return [
            html.Div(className="chart-row", children=[
                panel("bi-distribute-horizontal","Daily Request Distribution",fig_hist),
                panel("bi-clock-history",        "Traffic by Hour of Day",   fig_hr),
                panel("bi-calendar3",            "Traffic by Day of Week",   fig_dow),
            ]),
            html.Div(className="chart-row", children=[tbl_panel]),
        ]

    # ── RAW LOGS ──────────────────────────────────────────────────────────
    elif tab == "rawlogs":
        cols = ["date","time","client_ip","country","method","page","status_code","category"]
        tbl = dash_table.DataTable(
            data=df[cols].to_dict("records"),
            columns=[{"name":c.replace("_"," ").title(),"id":c} for c in cols],
            page_size=18, filter_action="native", sort_action="native", sort_mode="multi",
            style_header={"backgroundColor":"#0ea5e9","color":"white","fontWeight":"bold",
                          "padding":"7px","fontSize":"11px"},
            style_cell={"textAlign":"left","padding":"6px","fontSize":"11px",
                        "fontFamily":"Segoe UI,sans-serif","backgroundColor":"#16233f",
                        "color":"#e2e8f0","border":"1px solid rgba(148,163,184,0.1)",
                        "maxWidth":"200px","overflow":"hidden","textOverflow":"ellipsis"},
            style_data_conditional=[
                {"if":{"filter_query":"{status_code} = 404","column_id":"status_code"},
                 "color":"#f87171","fontWeight":"bold"},
                {"if":{"filter_query":"{status_code} = 500","column_id":"status_code"},
                 "color":"#ef4444","fontWeight":"bold"},
                {"if":{"row_index":"odd"},"backgroundColor":"#1e2f4e"},
            ],
        )
        return [html.Div(className="chart-panel", style={"flex":"1"}, children=[
            html.Div(className="chart-title", children=[
                html.I(className="bi bi-table"),
                "IIS Web Server Logs  –  filter / sort any column",
            ]),
            html.Div(className="dt-wrap", children=[tbl]),
        ])]

    return html.Div("Select a tab.", style={"color":"#94a3b8","padding":"40px","textAlign":"center"})


if __name__ == "__main__":
    app.run(debug=True)
