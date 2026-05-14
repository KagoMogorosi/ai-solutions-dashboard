"""
dashboard.py  –  AI-Solutions IIS Analytics Dashboard

Run:  python dashboard.py  →  http://127.0.0.1:8050
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table, callback, Output, Input, no_update, ctx
import dash_bootstrap_components as dbc

# ── Credentials ────────────────────────────────────────────────────────────────
USERS = {"admin": "aisolutions2024", "kago": "dashboard123", "client": "review2024"}

# ── Palette ────────────────────────────────────────────────────────────────────
AB  = "#0ea5e9"   # accent blue
TEA = "#14b8a6"   # teal
PUR = "#8b5cf6"   # purple
ORG = "#f97316"   # orange
GRN = "#22c55e"   # green
PAL = [AB, TEA, "#60a5fa", PUR, "#f472b6", ORG, "#34d399", "#fb923c", "#a78bfa", "#38bdf8"]

# ── Data ───────────────────────────────────────────────────────────────────────
import os
if not os.path.exists("web_server_logs.csv"):
    import generate_logs
RAW = pd.read_csv("web_server_logs.csv", parse_dates=["date"])
RAW["month"]   = RAW["date"].dt.to_period("M").astype(str)
RAW["week"]    = RAW["date"].dt.isocalendar().week.astype(int).astype(str).apply(lambda w: f"Wk {w}")
RAW["hour"]    = pd.to_datetime(RAW["time"], format="%H:%M:%S").dt.hour
RAW["day_name"]= RAW["date"].dt.day_name()

# ── Drop-down options ──────────────────────────────────────────────────────────
OPT = lambda col: [{"label": v, "value": v} for v in sorted(RAW[col].dropna().unique())]

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
server     = app.server
server.secret_key = os.environ.get("SECRET_KEY", "ai-solutions-secret-2024")

# ── CSS ────────────────────────────────────────────────────────────────────────
app.index_string = """
<!DOCTYPE html>
<html style="height:100%;overflow:hidden;">
<head>
    {%metas%}<title>{%title%}</title>{%favicon%}{%css%}
    <style>
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        html,body{height:100vh;width:100vw;overflow:hidden !important;
            font-family:'Segoe UI',system-ui,sans-serif;
            background:linear-gradient(135deg,#0b1728 0%,#0f1f3d 35%,#1a2c4f 65%,#1e3a66 100%) fixed;
            color:#e2e8f0;}
        #react-entry-point,._dash-loading,.dash-renderer{height:100%;}

        /* LOGIN */
        .lw{display:flex;align-items:center;justify-content:center;height:100vh;width:100vw;}
        .lc{background:rgba(22,35,63,.97);border:1px solid rgba(103,232,249,.2);border-radius:20px;
            padding:48px 44px 40px;width:420px;box-shadow:0 20px 60px rgba(0,0,0,.5);}
        .ll{text-align:center;margin-bottom:10px;}.ll .bi{font-size:3rem;color:#67e8f9;}
        .lt{text-align:center;font-size:1.4rem;font-weight:700;color:#bae6fd;margin-bottom:4px;}
        .ls{text-align:center;font-size:.8rem;color:#64748b;margin-bottom:32px;}
        .llab{font-size:.78rem;font-weight:600;color:#94a3b8;margin-bottom:6px;text-transform:uppercase;letter-spacing:.6px;}
        .li{width:100%;background:#1e3a5f !important;border:1.5px solid #67e8f9 !important;
            border-radius:10px !important;color:#f1f5f9 !important;padding:12px 14px !important;
            font-size:.95rem !important;margin-bottom:18px;outline:none;
            transition:border-color .2s,box-shadow .2s;display:block;}
        .li:focus{border-color:#38bdf8 !important;box-shadow:0 0 0 4px rgba(103,232,249,.25) !important;background:#1e3a5f !important;}
        .lb{width:100%;background:linear-gradient(135deg,#0ea5e9,#14b8a6) !important;border:none !important;
            border-radius:10px !important;color:#fff !important;font-size:.95rem !important;
            font-weight:700 !important;padding:13px !important;margin-top:6px;cursor:pointer;
            transition:opacity .2s,transform .15s;}
        .lb:hover{opacity:.9;transform:translateY(-1px);}
        .le{background:rgba(220,38,38,.15);border:1px solid rgba(220,38,38,.4);border-radius:8px;
            color:#fca5a5;font-size:.83rem;padding:10px 14px;margin-bottom:16px;text-align:center;}
        .lf{text-align:center;font-size:.72rem;color:#334155;margin-top:28px;}

        /* SHELL */
        .mw{display:flex;flex-direction:column;height:100vh;width:100%;padding:8px 14px 6px;overflow:hidden;}
        .hdr{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;
             padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:6px;}
        .hdr h2{color:#bae6fd;font-size:1.1rem;font-weight:700;margin:0;}
        .hdr p{color:#94a3b8;font-size:.7rem;margin:0;}

        /* KPI STRIP */
        .ks{flex:0 0 auto;display:flex;gap:6px;margin-bottom:6px;}
        .kb{flex:1;background:rgba(22,35,63,.85);border:1px solid rgba(148,163,184,.15);
            border-radius:10px;padding:6px 10px;box-shadow:0 4px 15px rgba(0,0,0,.25);
            display:flex;align-items:center;gap:8px;min-width:0;}
        .ki{font-size:1.3rem;flex-shrink:0;color:#67e8f9;}
        .kv{font-size:.95rem;font-weight:700;color:#f1f5f9;line-height:1.1;}
        .kl{font-size:.6rem;color:#94a3b8;line-height:1.2;}

        /* FILTER BAR */
        .fb{flex:0 0 auto;display:flex;align-items:center;gap:7px;margin-bottom:6px;
            background:rgba(15,23,42,.7);border:1px solid rgba(103,232,249,.12);
            border-radius:10px;padding:5px 10px;}
        .flbl{font-size:.65rem;font-weight:700;color:#67e8f9;text-transform:uppercase;
              letter-spacing:.7px;white-space:nowrap;flex-shrink:0;}
        .fb .Select-control{background:#16233f !important;border:1px solid rgba(103,232,249,.25) !important;
            border-radius:7px !important;min-height:26px !important;}
        .fb .Select-placeholder,.fb .Select-value-label{color:#94a3b8 !important;font-size:.72rem !important;}
        .fb .Select-value{color:#e2e8f0 !important;}
        .fb .Select-menu-outer{background:#16233f !important;border:1px solid rgba(103,232,249,.2) !important;
            border-radius:8px !important;z-index:9999 !important;}
        .fb .Select-option{color:#e2e8f0 !important;font-size:.72rem !important;background:#16233f !important;}
        .fb .Select-option.is-focused{background:#1e3a5f !important;}
        .fb .Select--multi .Select-value{background:rgba(14,165,233,.2) !important;
            border:1px solid rgba(14,165,233,.4) !important;color:#67e8f9 !important;
            border-radius:4px !important;font-size:.67rem !important;}
        .fb .Select--multi .Select-value-icon{color:#67e8f9 !important;}
        .fb .Select-arrow-zone .Select-arrow{border-top-color:#67e8f9 !important;}
        .frc{font-size:.63rem;color:#67e8f9;white-space:nowrap;flex-shrink:0;
             background:rgba(103,232,249,.1);border-radius:6px;padding:2px 7px;}
        .frb{background:rgba(103,232,249,.1) !important;border:1px solid rgba(103,232,249,.25) !important;
             border-radius:7px !important;color:#67e8f9 !important;font-size:.67rem !important;
             padding:3px 9px !important;cursor:pointer;white-space:nowrap;flex-shrink:0;}
        .frb:hover{background:rgba(103,232,249,.2) !important;}

        /* TABS */
        .nav-tabs{flex:0 0 auto;border-bottom:2px solid rgba(103,232,249,.2) !important;gap:4px;}
        .nav-tabs .nav-link{color:#cbd5e1 !important;background:rgba(22,35,63,.6) !important;
            border:1px solid rgba(148,163,184,.2) !important;border-radius:8px 8px 0 0 !important;
            padding:6px 12px !important;font-size:.76rem;font-weight:500;}
        .nav-tabs .nav-link:hover{background:rgba(22,35,63,.9) !important;}
        .nav-tabs .nav-link.active{color:#0f172a !important;background:#67e8f9 !important;
            font-weight:700 !important;border-bottom-color:transparent !important;}
        .nav-tabs .nav-link .bi{margin-right:4px;font-size:.76rem;}

        /* CONTENT */
        .tca{flex:1 1 0;display:flex;flex-direction:column;overflow:hidden !important;
             background:rgba(15,23,42,.6);border-radius:0 12px 12px 12px;padding:8px;gap:7px;}
        .cr{display:flex;flex:1 1 0;gap:7px;min-height:0;overflow:hidden;}
        .cp{flex:1 1 0;background:#16233f;border:1px solid rgba(148,163,184,.12);border-radius:12px;
            box-shadow:0 6px 20px rgba(0,0,0,.3);overflow:hidden;display:flex;flex-direction:column;min-height:0;}
        .cp .ct{font-size:.73rem;font-weight:700;color:#bae6fd;padding:7px 12px 4px;
                border-bottom:1px solid rgba(103,232,249,.12);flex:0 0 auto;display:flex;align-items:center;gap:5px;}
        .ct .bi{color:#67e8f9;font-size:.76rem;}
        .gw{flex:1 1 0;min-height:0;overflow:hidden;position:relative;}
        .gw .dash-graph,.gw .js-plotly-plot,.gw .plot-container{height:100% !important;width:100% !important;}
        .w25{flex:0 0 25% !important;}.w30{flex:0 0 30% !important;}
        .w35{flex:0 0 35% !important;}.w40{flex:0 0 40% !important;}
        .w45{flex:0 0 45% !important;}.w55{flex:0 0 55% !important;}
        .w60{flex:0 0 60% !important;}
        .dw{flex:1;overflow:auto;padding:5px 7px;}
        .dash-table-container{height:100%;}
        .js-plotly-plot .plotly .bg{fill:transparent !important;}
        .badge{font-size:.68rem;padding:3px 8px;border-radius:20px;}
        .logb{background:rgba(220,38,38,.15) !important;border:1px solid rgba(220,38,38,.35) !important;
              border-radius:7px !important;color:#fca5a5 !important;font-size:.7rem !important;
              padding:4px 10px !important;cursor:pointer;transition:background .2s;}
        .logb:hover{background:rgba(220,38,38,.28) !important;}
        .dw::-webkit-scrollbar{width:5px;height:5px;}
        .dw::-webkit-scrollbar-thumb{background:rgba(103,232,249,.3);border-radius:3px;}
    </style>
</head>
<body>{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>
"""

# ── Chart defaults ─────────────────────────────────────────────────────────────
CL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=30, l=38, r=10),
    font=dict(family="Segoe UI,sans-serif", size=10, color="#e2e8f0"),
    xaxis=dict(gridcolor="rgba(148,163,184,.12)", linecolor="rgba(148,163,184,.25)",
               tickfont=dict(size=9, color="#94a3b8")),
    yaxis=dict(gridcolor="rgba(148,163,184,.12)", linecolor="rgba(148,163,184,.25)",
               tickfont=dict(size=9, color="#94a3b8")),
    legend=dict(font=dict(size=9, color="#e2e8f0"), bgcolor="rgba(22,35,63,.75)",
                bordercolor="rgba(103,232,249,.2)", borderwidth=1),
    coloraxis_colorbar=dict(thickness=7, len=.6,
                            tickfont=dict(size=8, color="#94a3b8")),
    autosize=True,
)
def g(fig, **kw):
    fig.update_layout(**{**CL, **kw})
    return fig

def panel(icon, title, figure, cls=""):
    return html.Div(className=f"cp {cls}", children=[
        html.Div(className="ct", children=[html.I(className=f"bi {icon}"), title]),
        html.Div(className="gw", children=[
            dcc.Graph(figure=figure, config={"displayModeBar": False},
                      style={"height":"100%","width":"100%"}, responsive=True)
        ])
    ])

def kbox(icon, val, lbl):
    return html.Div(className="kb", children=[
        html.I(className=f"bi {icon} ki"),
        html.Div([html.Div(val, className="kv"), html.Div(lbl, className="kl")])
    ])

def tbl_style():
    return dict(
        style_header={"backgroundColor":"#0ea5e9","color":"white","fontWeight":"bold",
                      "textAlign":"center","fontSize":"11px","padding":"6px"},
        style_cell={"textAlign":"center","padding":"6px","fontFamily":"Segoe UI,sans-serif",
                    "fontSize":"11px","backgroundColor":"#16233f","color":"#e2e8f0",
                    "border":"1px solid rgba(148,163,184,.1)"},
        style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#1e2f4e"}],
    )

def apply_filters(countries, continents, regions, months, cats, statuses):
    df = RAW.copy()
    if countries:  df = df[df["country"].isin(countries)]
    if continents: df = df[df["continent"].isin(continents)]
    if regions:    df = df[df["region"].isin(regions)]
    if months:     df = df[df["month"].isin(months)]
    if cats:       df = df[df["category"].isin(cats)]
    if statuses:   df = df[df["status_code"].isin(statuses)]
    return df

def calc_kpis(df):
    d = df.groupby("date").size().reset_index(name="r")
    return {
        "total_req":    len(df),
        "unique_vis":   df["client_ip"].nunique(),
        "demos":        (df["category"]=="Schedule Demo").sum(),
        "ai":           (df["category"]=="AI Virtual Assistant").sum(),
        "events":       (df["category"]=="Promotional Events").sum(),
        "jobs":         (df["category"]=="Job Listings").sum(),
        "success":      round((df["status_code"]==200).mean()*100,1),
        "avg_daily":    round(d["r"].mean(),1),
        "std_daily":    round(d["r"].std(),1),
        "daily":        d,
    }

# ── Filter bar builder ────────────────────────────────────────────────────────
def filter_bar():
    dd = lambda id_, opts, ph: dcc.Dropdown(
        id=id_, options=opts, value=None, multi=True,
        placeholder=ph, clearable=True,
        style={"flex":"1","minWidth":"110px","maxWidth":"175px"}
    )
    return html.Div(className="fb", children=[
        html.Span([html.I(className="bi bi-funnel me-1"), "Filters"], className="flbl"),
        dd("f-country",   OPT("country"),   "Country"),
        dd("f-continent", OPT("continent"), "Continent"),
        dd("f-region",    OPT("region"),    "Region"),
        dd("f-month",     OPT("month"),     "Month"),
        dd("f-category",  OPT("category"),  "Category"),
        dd("f-status",
           [{"label": str(s), "value": s} for s in sorted(RAW["status_code"].unique())],
           "Status"),
        html.Span(id="f-count", className="frc", children=f"{len(RAW):,} records"),
        html.Button([html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset"],
                    id="f-reset", className="frb", n_clicks=0),
    ])

# ── Login layout ───────────────────────────────────────────────────────────────
login_layout = html.Div(className="lw", children=[
    html.Div(className="lc", children=[
        html.Div(className="ll", children=[html.I(className="bi bi-cpu-fill")]),
        html.Div("AI-Solutions", className="lt"),
        html.Div("IIS Analytics Dashboard  ·  Sign in to continue", className="ls"),
        html.Div(id="login-error"),
        html.Div("Username", className="llab"),
        dcc.Input(id="login-user", type="text",   className="li", debounce=False),
        html.Div("Password", className="llab"),
        dcc.Input(id="login-pass", type="password", className="li", debounce=False),
        html.Button([html.I(className="bi bi-box-arrow-in-right me-2"), "Sign In"],
                    id="login-btn", className="lb", n_clicks=0),
        html.Div("AI-Solutions · Business Intelligence Platform · © 2024", className="lf"),
    ])
])

# ── Dashboard layout ───────────────────────────────────────────────────────────
dash_layout = html.Div(className="mw", children=[
    html.Div(className="hdr", children=[
        html.Div([
            html.H2([html.I(className="bi bi-cpu me-2", style={"color":"#67e8f9"}),
                     "AI-Solutions  ·  IIS Web Server Analytics"]),
            html.P("Business Intelligence Dashboard  ·  Jan – Jun 2024"),
        ]),
        html.Div([
            dbc.Badge([html.I(className="bi bi-circle-fill me-1",
                              style={"fontSize":".45rem","verticalAlign":"middle"}),
                       "Live"], color="success", className="me-2"),
            dbc.Badge(f"{len(RAW):,} records", color="primary", className="me-3"),
            html.Button([html.I(className="bi bi-box-arrow-right me-1"), "Logout"],
                        id="logout-btn", className="logb", n_clicks=0),
        ], style={"display":"flex","alignItems":"center"})
    ]),

    # KPI strip — dynamic
    html.Div(id="kpi-strip", className="ks"),

    # Filter bar
    filter_bar(),

    # Tabs — 7 tabs covering all FRs
    dbc.Tabs([
        dbc.Tab(children=[html.I(className="bi bi-bar-chart me-1"),    "Overview"],       tab_id="overview"),
        dbc.Tab(children=[html.I(className="bi bi-globe2 me-1"),       "Geographic"],     tab_id="geo"),
        dbc.Tab(children=[html.I(className="bi bi-clock-history me-1"),"Time Analysis"],  tab_id="time"),
        dbc.Tab(children=[html.I(className="bi bi-people me-1"),       "Demographics"],   tab_id="demo"),
        dbc.Tab(children=[html.I(className="bi bi-briefcase me-1"),    "Business KPIs"],  tab_id="biz"),
        dbc.Tab(children=[html.I(className="bi bi-activity me-1"),     "Statistics"],     tab_id="stats"),
        dbc.Tab(children=[html.I(className="bi bi-table me-1"),        "Raw Logs"],       tab_id="rawlogs"),
    ], id="tabs", active_tab="overview"),

    html.Div(id="tab-out", className="tca"),
])

# ── Root ───────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=True),
    dcc.Store(id="auth-store", storage_type="session"),
    html.Div(id="page-content"),
])

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
@callback(Output("page-content","children"), Output("auth-store","data"),
          Input("url","pathname"), Input("auth-store","data"))
def route(_, auth):
    if auth and auth.get("logged_in"):
        return dash_layout, auth
    return login_layout, auth

@callback(
    Output("auth-store","data",   allow_duplicate=True),
    Output("login-error","children"),
    Output("url","pathname",      allow_duplicate=True),
    Input("login-btn","n_clicks"),
    Input("login-pass","n_submit"),
    Input("login-user","n_submit"),
    Input("login-user","value"),
    Input("login-pass","value"),
    prevent_initial_call=True,
)
def do_login(nc, ps, us, user, pwd):
    if ctx.triggered_id not in ("login-btn","login-pass","login-user"):
        return no_update, no_update, no_update
    u, p = (user or "").strip(), (pwd or "").strip()
    if not u or not p:
        return no_update, html.Div("Please enter both fields.", className="le"), no_update
    if USERS.get(u) == p:
        return {"logged_in": True, "username": u}, None, "/"
    return no_update, html.Div([html.I(className="bi bi-exclamation-circle me-2"),
                                "Invalid credentials."], className="le"), no_update

@callback(
    Output("auth-store","data",  allow_duplicate=True),
    Output("url","pathname",     allow_duplicate=True),
    Input("logout-btn","n_clicks"),
    prevent_initial_call=True,
)
def do_logout(n):
    if n: return {"logged_in": False}, "/login"
    return no_update, no_update

# ══════════════════════════════════════════════════════════════════════════════
# FILTER RESET
# ══════════════════════════════════════════════════════════════════════════════
@callback(
    Output("f-country","value"),   Output("f-continent","value"),
    Output("f-region","value"),    Output("f-month","value"),
    Output("f-category","value"),  Output("f-status","value"),
    Input("f-reset","n_clicks"), prevent_initial_call=True,
)
def reset(*_): return None, None, None, None, None, None

# ══════════════════════════════════════════════════════════════════════════════
# KPI STRIP UPDATE
# ══════════════════════════════════════════════════════════════════════════════
@callback(
    Output("kpi-strip","children"), Output("f-count","children"),
    Input("f-country","value"),     Input("f-continent","value"),
    Input("f-region","value"),      Input("f-month","value"),
    Input("f-category","value"),    Input("f-status","value"),
)
def update_kpis(co, cn, rg, mo, ca, st):
    df = apply_filters(co, cn, rg, mo, ca, st)
    k  = calc_kpis(df)
    strip = [
        kbox("bi-arrow-down-circle", f"{k['total_req']:,}",  "Total Requests"),
        kbox("bi-people",            f"{k['unique_vis']:,}", "Unique Visitors"),
        kbox("bi-calendar-check",    f"{k['demos']:,}",      "Demo Requests"),
        kbox("bi-cpu",               f"{k['ai']:,}",         "AI Assistant"),
        kbox("bi-megaphone",         f"{k['events']:,}",     "Event Requests"),
        kbox("bi-briefcase",         f"{k['jobs']:,}",       "Job Listings"),
        kbox("bi-check2-circle",     f"{k['success']}%",     "Success Rate"),
        kbox("bi-graph-up-arrow",    f"{k['avg_daily']}",    "Avg Daily Req."),
    ]
    label = f"{k['total_req']:,} records"
    if k['total_req'] < len(RAW): label += f" of {len(RAW):,}"
    return strip, label

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TAB CALLBACK
# ══════════════════════════════════════════════════════════════════════════════
@callback(
    Output("tab-out","children"),
    Input("tabs","active_tab"),
    Input("f-country","value"),   Input("f-continent","value"),
    Input("f-region","value"),    Input("f-month","value"),
    Input("f-category","value"),  Input("f-status","value"),
)
def render(tab, co, cn, rg, mo, ca, st):
    df = apply_filters(co, cn, rg, mo, ca, st)
    if df.empty:
        return [html.Div("No data matches the selected filters.",
                         style={"color":"#94a3b8","padding":"40px","textAlign":"center"})]
    k = calc_kpis(df)
    daily = k["daily"]

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    if tab == "overview":
        fig_trend = g(px.line(daily, x="date", y="r",
                              color_discrete_sequence=[AB],
                              labels={"date":"","r":"Requests"}))
        fig_trend.update_traces(line_width=2.5)
        fig_trend.add_hline(y=k["avg_daily"], line_dash="dot", line_color=ORG,
                            annotation_text=f"Mean {k['avg_daily']}",
                            annotation_font=dict(size=9,color=ORG))

        monthly = df.groupby("month").size().reset_index(name="n")
        fig_mo = g(px.bar(monthly, x="month", y="n", color="n",
                          color_continuous_scale="Blues", text_auto=True,
                          labels={"month":"","n":"Requests"}))
        fig_mo.update_layout(xaxis_tickangle=-30)

        sc = df["status_code"].value_counts().rename_axis("s").reset_index(name="n")
        sc["s"] = sc["s"].astype(str)
        fig_st = g(px.pie(sc, values="n", names="s",
                          color_discrete_sequence=PAL, hole=0.45),
                   margin=dict(t=10,b=10,l=10,r=10),
                   legend=dict(orientation="h",y=-.08,x=.5,xanchor="center",
                               font=dict(size=9)))
        return [
            html.Div(className="cr", children=[
                panel("bi-graph-up",       "Daily Request Trend",    fig_trend),
                panel("bi-pie-chart",      "HTTP Status Codes",      fig_st,  "w30"),
            ]),
            html.Div(className="cr", children=[
                panel("bi-bar-chart-line", "Monthly Request Totals", fig_mo),
            ]),
        ]

    # ── GEOGRAPHIC ────────────────────────────────────────────────────────────
    elif tab == "geo":
        # Country
        cc = df.groupby("country").size().reset_index(name="n").sort_values("n",ascending=False)
        fig_country = g(px.bar(cc, x="country", y="n", color="n",
                               color_continuous_scale="Blues", text_auto=True,
                               labels={"country":"","n":"Requests"}))
        fig_country.update_layout(xaxis_tickangle=-30)

        # Continent
        cont = df.groupby("continent").size().reset_index(name="n").sort_values("n",ascending=False)
        fig_cont = g(px.pie(cont, values="n", names="continent",
                            color_discrete_sequence=PAL, hole=0.38),
                     margin=dict(t=10,b=10,l=10,r=10),
                     legend=dict(font=dict(size=8)))

        # Region
        reg = df.groupby("region").size().reset_index(name="n").sort_values("n",ascending=False)
        fig_reg = g(px.bar(reg, x="n", y="region", orientation="h",
                           color="n", color_continuous_scale="Teal", text_auto=True,
                           labels={"region":"","n":"Requests"}))
        fig_reg.update_layout(yaxis={"categoryorder":"total ascending"},
                              margin=dict(t=10,b=30,l=140,r=10))

        # Top 5 countries over time
        top5 = cc.head(5)["country"].tolist()
        mc = df[df["country"].isin(top5)].groupby(["month","country"]).size().reset_index(name="n")
        fig_mc = g(px.line(mc, x="month", y="n", color="country", markers=True,
                           color_discrete_sequence=PAL,
                           labels={"month":"","n":"Requests","country":""}))

        return [
            html.Div(className="cr", children=[
                panel("bi-bar-chart-steps", "Requests by Country",    fig_country),
                panel("bi-globe2",          "Traffic by Continent",   fig_cont,  "w30"),
            ]),
            html.Div(className="cr", children=[
                panel("bi-map",             "Requests by Region",     fig_reg),
                panel("bi-graph-up",        "Top 5 Countries Trend",  fig_mc),
            ]),
        ]

    # ── TIME ANALYSIS ─────────────────────────────────────────────────────────
    elif tab == "time":
        # Hourly
        hr = df.groupby("hour").size().reset_index(name="n")
        fig_hr = g(px.bar(hr, x="hour", y="n", color="n",
                          color_continuous_scale="Blues",
                          labels={"hour":"Hour (24h)","n":"Requests"}))

        # Day of week
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("day_name").size().reindex(dow_order).reset_index(name="n")
        fig_dow = g(px.bar(dow, x="day_name", y="n", color="n",
                           color_continuous_scale="Teal",
                           labels={"day_name":"","n":"Requests"}))

        # Weekly
        wk = df.groupby("week").size().reset_index(name="n")
        fig_wk = g(px.bar(wk, x="week", y="n", color="n",
                          color_continuous_scale="Purp", text_auto=True,
                          labels={"week":"","n":"Requests"}))

        # Monthly
        fig_mo = g(px.line(df.groupby("month").size().reset_index(name="n"),
                           x="month", y="n", markers=True,
                           color_discrete_sequence=[AB],
                           labels={"month":"","n":"Requests"}))

        return [
            html.Div(className="cr", children=[
                panel("bi-clock",      "Requests by Hour of Day",   fig_hr),
                panel("bi-calendar3",  "Requests by Day of Week",   fig_dow),
            ]),
            html.Div(className="cr", children=[
                panel("bi-calendar-week",  "Requests by Week",      fig_wk),
                panel("bi-calendar-month", "Requests by Month",     fig_mo),
            ]),
        ]

    # ── DEMOGRAPHICS ──────────────────────────────────────────────────────────
    elif tab == "demo":
        # User type distribution
        ut = df.groupby("user_type").size().reset_index(name="n")
        fig_ut = g(px.pie(ut, values="n", names="user_type",
                          color_discrete_sequence=PAL, hole=0.38),
                   margin=dict(t=10,b=10,l=10,r=10))

        # Device type
        dv = df.groupby("device").size().reset_index(name="n")
        fig_dv = g(px.bar(dv, x="device", y="n", color="device",
                          color_discrete_sequence=PAL, text_auto=True,
                          labels={"device":"","n":"Requests"}))
        fig_dv.update_layout(showlegend=False)

        # Category preference by user type
        cat_ut = df.groupby(["user_type","category"]).size().reset_index(name="n")
        fig_cat_ut = g(px.bar(cat_ut, x="user_type", y="n", color="category",
                              barmode="stack", color_discrete_sequence=PAL,
                              labels={"user_type":"","n":"Requests","category":""}))
        fig_cat_ut.update_layout(xaxis_tickangle=-15)

        # Device × continent
        dv_cont = df.groupby(["device","continent"]).size().reset_index(name="n")
        fig_dv_cont = g(px.bar(dv_cont, x="continent", y="n", color="device",
                               barmode="group", color_discrete_sequence=PAL,
                               labels={"continent":"","n":"Requests","device":""}))
        fig_dv_cont.update_layout(xaxis_tickangle=-20)

        return [
            html.Div(className="cr", children=[
                panel("bi-person-badge",        "Visitor Type Distribution",     fig_ut,       "w35"),
                panel("bi-phone",               "Access by Device",              fig_dv),
            ]),
            html.Div(className="cr", children=[
                panel("bi-person-lines-fill",   "Page Preferences by Visitor Type", fig_cat_ut),
                panel("bi-globe2",              "Device Usage by Continent",      fig_dv_cont),
            ]),
        ]

    # ── BUSINESS KPIs ─────────────────────────────────────────────────────────
    elif tab == "biz":
        biz_cats = ["Schedule Demo","Promotional Events","AI Virtual Assistant","Job Listings"]
        mb = df[df["category"].isin(biz_cats)].groupby(["month","category"]).size().reset_index(name="n")
        fig_biz = g(px.bar(mb, x="month", y="n", color="category",
                           barmode="group", color_discrete_sequence=PAL,
                           labels={"month":"","n":"Requests","category":""}))

        dc = df[df["category"]=="Schedule Demo"].groupby("country").size().reset_index(name="n").sort_values("n",ascending=False)
        fig_demo = g(px.bar(dc, x="country", y="n", color="n",
                            color_continuous_scale="Oranges", text_auto=True,
                            labels={"country":"","n":"Demos"}))
        fig_demo.update_layout(xaxis_tickangle=-30)

        ac = df[df["category"]=="AI Virtual Assistant"].groupby("country").size().reset_index(name="n").sort_values("n",ascending=False)
        fig_ai = g(px.bar(ac, x="country", y="n", color="n",
                          color_continuous_scale="Teal", text_auto=True,
                          labels={"country":"","n":"Requests"}))
        fig_ai.update_layout(xaxis_tickangle=-30)

        pivot = (df[df["category"].isin(["Schedule Demo","AI Virtual Assistant"])]
                   .groupby(["country","category"]).size().unstack(fill_value=0).reset_index())
        if "Schedule Demo" in pivot.columns and "AI Virtual Assistant" in pivot.columns:
            fig_sc = g(px.scatter(pivot, x="Schedule Demo", y="AI Virtual Assistant",
                                  text="country", color_discrete_sequence=[PUR],
                                  labels={"Schedule Demo":"Demo Req.","AI Virtual Assistant":"AI Req."}))
            fig_sc.update_traces(textposition="top center", marker=dict(size=10,opacity=.8))
        else:
            fig_sc = g(go.Figure())

        return [
            html.Div(className="cr", children=[
                panel("bi-bar-chart-line","Monthly Business KPIs", fig_biz),
            ]),
            html.Div(className="cr", children=[
                panel("bi-calendar-event","Demo Requests by Country",        fig_demo),
                panel("bi-cpu",           "AI Assistant by Country",          fig_ai),
                panel("bi-diagram-3",     "Demo vs AI Assistant (Scatter)",   fig_sc),
            ]),
        ]

    # ── STATISTICS ────────────────────────────────────────────────────────────
    elif tab == "stats":
        fig_hist = g(px.histogram(daily, x="r", nbins=22,
                                  color_discrete_sequence=[AB],
                                  labels={"r":"Daily Requests","count":"Frequency"}))
        fig_hist.add_vline(x=k["avg_daily"], line_dash="dash", line_color="#ef4444",
                           annotation_text=f"μ={k['avg_daily']}",
                           annotation_font=dict(size=9,color="#ef4444"))
        fig_hist.add_vline(x=k["avg_daily"]+k["std_daily"], line_dash="dot", line_color=ORG,
                           annotation_text=f"+1σ={k['avg_daily']+k['std_daily']:.1f}",
                           annotation_font=dict(size=9,color=ORG))

        hr2 = df.groupby("hour").size().reset_index(name="n")
        fig_hr2 = g(px.bar(hr2, x="hour", y="n", color="n",
                           color_continuous_scale="Blues",
                           labels={"hour":"Hour (24h)","n":"Requests"}))

        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow2 = df.groupby("day_name").size().reindex(dow_order).reset_index(name="n")
        fig_dow2 = g(px.bar(dow2, x="day_name", y="n", color="n",
                            color_continuous_scale="Teal",
                            labels={"day_name":"","n":"Requests"}))

        cat_d = df.groupby(["date","category"]).size().reset_index(name="c")
        cs = (cat_d.groupby("category")["c"]
                    .agg(["mean","std","sum","max"]).round(2).reset_index())
        cs.columns = ["Category","Daily Mean","Std Dev","Total","Peak"]
        tbl = dash_table.DataTable(data=cs.to_dict("records"),
                                   columns=[{"name":c,"id":c} for c in cs.columns],
                                   page_size=10, **tbl_style())
        tbl_panel = html.Div(className="cp", children=[
            html.Div(className="ct", children=[html.I(className="bi bi-table"), "Per-Category Stats"]),
            html.Div(className="dw", children=[tbl]),
        ])
        return [
            html.Div(className="cr", children=[
                panel("bi-distribute-horizontal","Daily Distribution",    fig_hist),
                panel("bi-clock-history",         "By Hour of Day",       fig_hr2),
                panel("bi-calendar3",             "By Day of Week",       fig_dow2),
            ]),
            html.Div(className="cr", children=[tbl_panel]),
        ]

    # ── RAW LOGS ──────────────────────────────────────────────────────────────
    elif tab == "rawlogs":
        cols = ["date","time","client_ip","country","continent","region",
                "method","page","status_code","category","user_type","device"]
        tbl = dash_table.DataTable(
            data=df[cols].to_dict("records"),
            columns=[{"name":c.replace("_"," ").title(),"id":c} for c in cols],
            page_size=16, filter_action="native", sort_action="native", sort_mode="multi",
            style_header={"backgroundColor":"#0ea5e9","color":"white","fontWeight":"bold",
                          "padding":"6px","fontSize":"10px"},
            style_cell={"textAlign":"left","padding":"5px","fontSize":"10px",
                        "fontFamily":"Segoe UI,sans-serif","backgroundColor":"#16233f",
                        "color":"#e2e8f0","border":"1px solid rgba(148,163,184,.1)",
                        "maxWidth":"180px","overflow":"hidden","textOverflow":"ellipsis"},
            style_data_conditional=[
                {"if":{"filter_query":"{status_code} = 404","column_id":"status_code"},
                 "color":"#f87171","fontWeight":"bold"},
                {"if":{"filter_query":"{status_code} = 500","column_id":"status_code"},
                 "color":"#ef4444","fontWeight":"bold"},
                {"if":{"row_index":"odd"},"backgroundColor":"#1e2f4e"},
            ],
        )
        return [html.Div(className="cp", style={"flex":"1"}, children=[
            html.Div(className="ct", children=[
                html.I(className="bi bi-table"),
                "IIS Web Server Logs  –  filter / sort any column"
            ]),
            html.Div(className="dw", children=[tbl]),
        ])]

    return html.Div("Select a tab.", style={"color":"#94a3b8","padding":"40px","textAlign":"center"})


if __name__ == "__main__":
    app.run(debug=True)
