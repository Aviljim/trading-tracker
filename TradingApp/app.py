"""
TradeLog — Professional Trading Journal
Single-file Streamlit app with full dark-mode UI, option_menu navigation,
accurate PnL parsing, trailing drawdown, calendar, and journal.

Requirements (requirements.txt):
    streamlit==1.41.1
    plotly==5.24.1
    pandas==2.2.3
    numpy==1.26.4
    rich==13.9.4
    streamlit-option-menu==0.3.13
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import io
import calendar
from datetime import date, timedelta

# streamlit-option-menu — graceful fallback if not installed
try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ImportError:
    HAS_OPTION_MENU = False

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeLog — Professional Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Palette ─────────────────────────────────────────────────────────────── */
:root {
    --bg:          #0d0d14;
    --bg-surface:  #12121c;
    --bg-card:     #181824;
    --bg-card2:    #1e1e2e;
    --bg-input:    #1a1a28;
    --border:      #252538;
    --border-hi:   #32324a;
    --text:        #e8e8f0;
    --text-2:      #7878a0;
    --text-3:      #45455e;
    --blue:        #4f8ef7;
    --teal:        #2dd4bf;
    --green:       #22c55e;
    --red:         #f43f5e;
    --amber:       #f59e0b;
    --gold:        #fbbf24;
    --purple:      #a78bfa;
}

/* ── Global reset ─────────────────────────────────────────────────────────── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] .stNumberInput input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}
[data-testid="stFileUploader"] {
    background: var(--bg-input) !important;
    border: 1px dashed var(--border-hi) !important;
    border-radius: 10px !important;
}

/* ── Remove chrome ────────────────────────────────────────────────────────── */
header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
.block-container { padding: 1.4rem 2.2rem 3rem !important; max-width: 100% !important; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ── Metric cards ─────────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1rem 1.3rem !important;
    transition: border-color 0.2s, background 0.2s;
}
div[data-testid="metric-container"]:hover {
    background: var(--bg-card2) !important;
    border-color: var(--border-hi) !important;
}
div[data-testid="metric-container"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: var(--text-2) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Dataframe ────────────────────────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
iframe[title="st_aggrid"] { border-radius: 12px !important; }

/* ── Section headers ─────────────────────────────────────────────────────── */
.sec-hdr {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-2);
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sec-hdr::after { content:''; flex:1; height:1px; background: var(--border); }

/* ── Page title ──────────────────────────────────────────────────────────── */
.pg-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.pg-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-2);
    margin-top: 0.25rem;
}

/* ── Badges ──────────────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}
.bg  { background: rgba(79,142,247,0.12); color: #4f8ef7;  border: 1px solid rgba(79,142,247,0.25); }
.gg  { background: rgba(34,197,94,0.10);  color: #22c55e;  border: 1px solid rgba(34,197,94,0.25); }
.rr  { background: rgba(244,63,94,0.10);  color: #f43f5e;  border: 1px solid rgba(244,63,94,0.25); }
.aa  { background: rgba(251,191,36,0.10); color: #fbbf24;  border: 1px solid rgba(251,191,36,0.25); }

/* ── Stat pills ──────────────────────────────────────────────────────────── */
.pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    color: var(--text-2);
    text-align: center;
    line-height: 1.85;
}
.pill strong { color: var(--text); font-size: 0.88rem; font-family: 'Inter', sans-serif; font-weight: 700; }

/* ── Calendar grid ───────────────────────────────────────────────────────── */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 0.5rem;
}
.cal-day-hdr {
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--text-3);
    padding: 4px 0;
    text-transform: uppercase;
}
.cal-day {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 4px;
    min-height: 60px;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    position: relative;
}
.cal-day.empty { background: transparent; border-color: transparent; }
.cal-day.pos   { border-color: rgba(34,197,94,0.35);  background: rgba(34,197,94,0.06); }
.cal-day.neg   { border-color: rgba(244,63,94,0.35);  background: rgba(244,63,94,0.06); }
.cal-day .dn   { color: var(--text-3); font-size: 0.62rem; }
.cal-day .pv   { font-weight: 700; font-size: 0.72rem; margin-top: 4px; }
.cal-day.pos .pv { color: var(--green); }
.cal-day.neg .pv { color: var(--red); }

/* ── Journal ─────────────────────────────────────────────────────────────── */
.jnl-date-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

/* ── Drawdown callout ────────────────────────────────────────────────────── */
.dd-bar {
    background: rgba(244,63,94,0.05);
    border: 1px solid rgba(244,63,94,0.2);
    border-radius: 10px;
    padding: 0.65rem 1.1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
}

/* ── Upload hint ─────────────────────────────────────────────────────────── */
.upload-hint {
    font-family: 'Inter', sans-serif;
    font-size: 0.73rem;
    color: var(--text-3);
    text-align: center;
    margin-top: 0.4rem;
    line-height: 1.6;
}

/* ── Option menu overrides ───────────────────────────────────────────────── */
.nav-link { font-family: 'Inter', sans-serif !important; font-size: 0.85rem !important; }
.nav-link-selected { background: rgba(79,142,247,0.15) !important; }

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 3px; }

/* ── Streamlit textarea ──────────────────────────────────────────────────── */
textarea {
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY DARK THEME HELPERS
#  RULE: PLOT has NO xaxis/yaxis/margin — pass those explicitly to avoid
#  "got multiple values for keyword argument" errors.
# ─────────────────────────────────────────────────────────────────────────────
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#7878a0", size=12),
    hoverlabel=dict(
        bgcolor="#1e1e2e", bordercolor="#32324a",
        font=dict(family="JetBrains Mono, monospace", size=12, color="#e8e8f0"),
    ),
)

def _ax(prefix="", fmt=",", zeroline=False, zc="rgba(255,255,255,0.10)"):
    return dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.05)",
        tickfont=dict(size=11, color="#45455e"),
        zeroline=zeroline,
        zerolinecolor=zc,
        zerolinewidth=1,
        tickprefix=prefix,
        tickformat=fmt,
    )

_M  = dict(l=10, r=10, t=30, b=10)
_ML = dict(l=10, r=10, t=45, b=10)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_pnl(raw) -> float:
    """
    Strictly parse broker PnL strings:
      '$1,234.56'   →  1234.56
      '$(1,234.56)' → -1234.56
      '(234.00)'    → -234.0
      '-234'        → -234.0
      1234.56       →  1234.56
    """
    if pd.isna(raw):
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    # Parentheses = negative
    negative = "(" in s
    # Strip everything except digits and dot
    cleaned = re.sub(r"[^\d\.]", "", s)
    if not cleaned:
        return 0.0
    try:
        val = float(cleaned)
        return -val if negative else val
    except ValueError:
        return 0.0


def calc_fee(symbol: str, qty) -> float:
    """MNQ → $1.14/contract, NQ (not MNQ) → $4.14/contract, else $0."""
    sym = str(symbol).upper().strip()
    try:
        q = int(float(str(qty)))
    except (ValueError, TypeError):
        q = 1
    if "MNQ" in sym:
        return round(1.14 * q, 2)
    if "NQ" in sym:
        return round(4.14 * q, 2)
    return 0.0


def trailing_dd_limit(cum_net: pd.Series, buffer: float) -> pd.Series:
    """
    Trailing drawdown line:
      limit_i = min(0, HWM_i - buffer)
    Starts at -buffer, trails up with HWM, locks at $0 once HWM >= buffer.
    """
    hwm = cum_net.cummax()
    return (hwm - buffer).clip(upper=0.0)


def streak_calc(pnl: pd.Series):
    """Return (max_win_streak, max_loss_streak)."""
    mw = ml = cw = cl = 0
    for v in pnl:
        if v > 0:
            cw += 1; cl = 0; mw = max(mw, cw)
        elif v < 0:
            cl += 1; cw = 0; ml = max(ml, cl)
        else:
            cw = cl = 0
    return mw, ml


def max_dd(cum: pd.Series) -> float:
    """Largest peak-to-trough drawdown (positive dollar amount)."""
    peak = cum.cummax()
    return float(abs((cum - peak).min()))


def dist_from_peak(cum: pd.Series) -> float:
    """How far current value is below the all-time high."""
    hwm = float(cum.max())
    cur = float(cum.iloc[-1])
    return hwm - cur


def fmt_usd(v: float, sign=False) -> str:
    p = "+" if (sign and v > 0) else ""
    return f"{p}${abs(v) / 1e6:.2f}M" if abs(v) >= 1e6 else f"{p}${v:,.2f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO DATA  (NQ / MNQ heavy so fee logic is exercised)
# ─────────────────────────────────────────────────────────────────────────────

def _demo() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    syms = ["NQ","MNQ","MNQ","NQ","ES","MNQ","NQ","MNQ","NQ","MNQ"]
    wts  = [0.20,0.25,0.10,0.15,0.05,0.08,0.07,0.05,0.03,0.02]
    base = pd.Timestamp("2025-11-03 09:35:00")
    rows = []
    for i in range(80):
        sym   = rng.choice(syms, p=wts)
        qty   = int(rng.choice([1,2,3,5,10]))
        win   = rng.random() < 0.575
        pnl   = round(float(abs(rng.normal(340,260))) if win
                      else -float(abs(rng.normal(185,130))), 2)
        bp    = round(float(rng.uniform(18000,22000)), 2)
        sp    = round(bp + pnl / qty, 2)
        bought= base + pd.Timedelta(days=int(i//4),
                                    hours=int(rng.integers(0,6)),
                                    minutes=int(rng.integers(0,55)))
        mins  = int(rng.integers(1,90))
        sold  = bought + pd.Timedelta(minutes=mins)
        pstr  = f"${pnl:.2f}" if pnl >= 0 else f"$({abs(pnl):.2f})"
        rows.append({
            "symbol":f"{sym}", "_priceFormat":"0.00",
            "_priceFormatType":"DECIMAL","_tickSize":0.25,
            "buyFillId":f"B{i}","sellFillId":f"S{i}",
            "qty":qty,"buyPrice":bp,"sellPrice":sp,"pnl":pstr,
            "boughtTimestamp":bought.strftime("%Y-%m-%dT%H:%M:%S"),
            "soldTimestamp":sold.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration":f"{mins}m",
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA PROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def process(raw: pd.DataFrame, starting: float, dd_buf: float = 2000.0,
            profit_target: float = 3000.0) -> pd.DataFrame:
    df = raw.copy()

    # ── Parse timestamps ──────────────────────────────────────────────────────
    df["soldTimestamp"]   = pd.to_datetime(df["soldTimestamp"],   errors="coerce")
    df["boughtTimestamp"] = pd.to_datetime(df["boughtTimestamp"], errors="coerce")
    df = (df.dropna(subset=["soldTimestamp"])
            .sort_values("soldTimestamp")
            .reset_index(drop=True))

    # ── Gross PnL (strict parser) ─────────────────────────────────────────────
    df["gross_pnl"] = df["pnl"].apply(parse_pnl)

    # ── Fees ─────────────────────────────────────────────────────────────────
    df["fees"] = df.apply(lambda r: calc_fee(r["symbol"], r.get("qty", 1)), axis=1)

    # ── Net PnL = Gross - Fees ────────────────────────────────────────────────
    df["net_pnl"] = df["gross_pnl"] - df["fees"]

    # ── Cumulative series (both start at $0) ──────────────────────────────────
    df["cum_gross"]  = df["gross_pnl"].cumsum()
    df["cum_net"]    = df["net_pnl"].cumsum()

    # ── Absolute equity = Starting Balance + Cumulative Net PnL ──────────────
    df["equity"] = starting + df["cum_net"]

    # ── Trailing drawdown ─────────────────────────────────────────────────────
    df["dd_limit"] = trailing_dd_limit(df["cum_net"], buffer=dd_buf)

    # ── Direction: Long if boughtTimestamp < soldTimestamp, else Short ────────
    df["direction"] = np.where(
        df["boughtTimestamp"] < df["soldTimestamp"], "Long", "Short"
    )

    # ── Calendar/grouping fields ──────────────────────────────────────────────
    df["trade_date"]  = df["soldTimestamp"].dt.date
    df["day_of_week"] = df["soldTimestamp"].dt.day_name()
    df["month_label"] = df["soldTimestamp"].dt.strftime("%b '%y")
    df["trade_num"]   = range(1, len(df) + 1)

    return df


@st.cache_data(show_spinner=False)
def load_csv(data: bytes, starting: float, dd_buf: float,
             profit_target: float) -> pd.DataFrame:
    raw = pd.read_csv(io.BytesIO(data))
    return process(raw, starting, dd_buf=dd_buf, profit_target=profit_target)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.3rem 0 1rem">
      <div style="font-family:'Inter',sans-serif;font-size:1.25rem;font-weight:700;
                  color:#e8e8f0;letter-spacing:-0.02em;">TradeLog</div>
      <div style="font-family:'Inter',sans-serif;font-size:0.73rem;
                  color:#45455e;margin-top:2px;">Professional Trading Journal</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Option menu navigation ────────────────────────────────────────────────
    if HAS_OPTION_MENU:
        active_tab = option_menu(
            menu_title=None,
            options=["Dashboard", "Calendar", "Journal"],
            icons=["bar-chart-line-fill", "calendar3", "journal-text"],
            default_index=0,
            styles={
                "container":    {"padding":"4px 0","background":"transparent"},
                "icon":         {"color":"#7878a0","font-size":"14px"},
                "nav-link":     {"font-family":"Inter,sans-serif","font-size":"0.83rem",
                                 "color":"#7878a0","border-radius":"8px",
                                 "--hover-color":"#1e1e2e"},
                "nav-link-selected":{"background":"rgba(79,142,247,0.15)",
                                     "color":"#4f8ef7","font-weight":"600"},
            },
        )
    else:
        active_tab = st.radio("Navigation", ["Dashboard","Calendar","Journal"],
                              label_visibility="collapsed")

    st.markdown("---")

    # ── Account setup ─────────────────────────────────────────────────────────
    st.markdown("""<div style="font-size:0.66rem;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:#45455e;margin-bottom:0.5rem;">
                Account Setup</div>""", unsafe_allow_html=True)

    starting_balance = st.number_input(
        "Starting Balance ($)", min_value=0.0, value=50_000.0,
        step=1_000.0, format="%.2f",
        help="Account balance before first trade in this dataset.",
    )
    drawdown_buffer = st.number_input(
        "Trailing Drawdown Buffer ($)", min_value=100.0, value=2_000.0,
        step=100.0, format="%.0f",
        help="e.g. $2,000 funded-account trailing stop.",
    )
    profit_target = st.number_input(
        "Profit Target ($)", min_value=0.0, value=3_000.0,
        step=100.0, format="%.0f",
        help="Gold dashed line on the equity curve.",
    )

    st.markdown("---")

    # ── File upload ───────────────────────────────────────────────────────────
    st.markdown("""<div style="font-size:0.66rem;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:#45455e;margin-bottom:0.5rem;">
                Import Trades</div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
    st.markdown("""<div class="upload-hint">
      Required: <code style="color:#4f8ef7;font-size:0.68rem;">
      symbol · pnl · qty · buyPrice · sellPrice<br>
      boughtTimestamp · soldTimestamp · duration</code>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    use_demo = st.checkbox("Load demo data", value=(uploaded is None))


# ─────────────────────────────────────────────────────────────────────────────
#  RESOLVE DATA
# ─────────────────────────────────────────────────────────────────────────────
if uploaded is not None:
    df = load_csv(uploaded.read(), starting_balance, drawdown_buffer, profit_target)
    data_source = "live"
elif use_demo:
    df = process(_demo(), starting_balance, dd_buf=drawdown_buffer,
                 profit_target=profit_target)
    data_source = "demo"
else:
    df = None
    data_source = "none"


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
with h1:
    tab_titles = {
        "Dashboard": ("Performance Dashboard", "Account metrics, equity curve & trade analytics"),
        "Calendar":  ("Trading Calendar",       "Daily P&L heatmap"),
        "Journal":   ("Trade Journal",          "Daily notes & reflection"),
    }
    title, sub = tab_titles.get(active_tab, ("Dashboard",""))
    st.markdown(f'<div class="pg-title">{title}</div>'
                f'<div class="pg-sub">{sub}</div>', unsafe_allow_html=True)
with h2:
    badge_cls = "gg" if data_source == "live" else ("bg" if data_source == "demo" else "rr")
    badge_lbl = "LIVE" if data_source == "live" else ("DEMO" if data_source == "demo" else "NO DATA")
    st.markdown(f'<div style="text-align:right;margin-top:0.9rem;">'
                f'<span class="badge {badge_cls}">{badge_lbl}</span></div>',
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
if df is None or len(df) == 0:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:52vh;text-align:center;">
      <div style="font-size:2.5rem;margin-bottom:1rem;">📂</div>
      <div style="font-family:'Inter',sans-serif;font-size:1.3rem;font-weight:700;
                  color:#e8e8f0;margin-bottom:0.4rem;">No data loaded</div>
      <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#45455e;
                  max-width:360px;line-height:1.7;">
        Upload a CSV or enable <strong style="color:#7878a0;">demo data</strong>
        from the sidebar to get started.
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  COMPUTE CORE METRICS (shared across all tabs)
# ─────────────────────────────────────────────────────────────────────────────
n_trades    = len(df)
wins        = df[df["net_pnl"] > 0]
losses      = df[df["net_pnl"] < 0]
total_gross = float(df["gross_pnl"].sum())
total_fees  = float(df["fees"].sum())
total_net   = float(df["net_pnl"].sum())
gross_wins  = float(wins["gross_pnl"].sum())  if len(wins)   else 0.0
gross_loss  = float(df[df["gross_pnl"] < 0]["gross_pnl"].sum()) if len(losses) else 0.0
curr_equity = starting_balance + total_net
win_rate    = len(wins) / n_trades * 100 if n_trades else 0.0
pf          = (gross_wins / abs(gross_loss)) if gross_loss else float("inf")
avg_win     = float(wins["net_pnl"].mean())   if len(wins)   else 0.0
avg_loss    = float(losses["net_pnl"].mean()) if len(losses) else 0.0
rr          = (avg_win / abs(avg_loss))        if avg_loss    else float("inf")
max_dd_val  = max_dd(df["cum_net"])
dfp_val     = dist_from_peak(df["cum_net"])
total_ret   = (total_net / starting_balance * 100) if starting_balance else 0.0
win_st, loss_st = streak_calc(df["net_pnl"])
expectancy  = total_net / n_trades if n_trades else 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if active_tab == "Dashboard":

    # ── KPI ROW 1 ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Account Overview</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Current Equity",
              f"${curr_equity:,.2f}",
              f"{fmt_usd(total_net, sign=True)} ({fmt_pct(total_ret)})")
    k2.metric("Gross P&L",
              fmt_usd(total_gross, sign=True),
              f"fees: −${total_fees:,.2f}", delta_color="off")
    k3.metric("Net P&L",
              fmt_usd(total_net, sign=True),
              f"{len(wins)}W / {len(losses)}L", delta_color="off")
    pf_s = f"{pf:.2f}×" if pf != float("inf") else "∞"
    k4.metric("Profit Factor", pf_s,
              "strong" if pf > 1.5 else ("neutral" if pf > 0.9 else "review"),
              delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI ROW 2 ─────────────────────────────────────────────────────────────
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Win Rate", fmt_pct(win_rate), f"{n_trades} trades", delta_color="off")
    rr_s = f"{rr:.2f}R" if rr != float("inf") else "∞"
    k6.metric("Risk / Reward", rr_s, "avg win ÷ |avg loss|", delta_color="off")
    k7.metric("Max All-Time Drawdown",
              fmt_usd(-max_dd_val),
              f"−{max_dd_val/starting_balance*100:.1f}% of balance",
              delta_color="inverse")
    k8.metric("Distance from Peak",
              fmt_usd(-dfp_val) if dfp_val > 0 else "+$0.00",
              "profit given back from ATH",
              delta_color="inverse" if dfp_val > 0 else "off")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI ROW 3 ─────────────────────────────────────────────────────────────
    k9, k10, k11, k12 = st.columns(4)
    k9.metric("Avg Win",  fmt_usd(avg_win),  f"{len(wins)} trades",  delta_color="off")
    k10.metric("Avg Loss", fmt_usd(avg_loss), f"{len(losses)} trades", delta_color="off")
    k11.metric("Largest Win Streak",  f"{win_st} trades",  "consecutive",  delta_color="off")
    k12.metric("Largest Loss Streak", f"{loss_st} trades", "consecutive",  delta_color="off")

    # ── EQUITY CURVE ─────────────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Equity Curve — Cumulative Net P&L</div>',
                unsafe_allow_html=True)

    # Origin row ($0 at time just before first trade)
    origin = pd.DataFrame({
        "soldTimestamp": [df["soldTimestamp"].iloc[0] - pd.Timedelta(minutes=5)],
        "cum_net":       [0.0],
        "dd_limit":      [-float(drawdown_buffer)],
        "trade_num":     [0],
        "net_pnl":       [0.0],
        "fees":          [0.0],
    })
    eq = pd.concat(
        [origin, df[["soldTimestamp","cum_net","dd_limit","trade_num","net_pnl","fees"]]],
        ignore_index=True,
    )

    fig = go.Figure()

    # ① Green equity line + fill
    fig.add_trace(go.Scatter(
        x=eq["soldTimestamp"], y=eq["cum_net"],
        mode="lines",
        line=dict(color="#22c55e", width=2.2, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(34,197,94,0.07)",
        name="Net P&L",
        hovertemplate=(
            "<b>Trade #%{customdata[0]}</b><br>"
            "%{x|%b %d %H:%M}<br>"
            "Cum. Net P&L: <b>$%{y:,.2f}</b><br>"
            "This trade: $%{customdata[1]:,.2f} | Fees: $%{customdata[2]:,.2f}"
            "<extra></extra>"
        ),
        customdata=np.column_stack([
            eq["trade_num"].to_numpy(),
            eq["net_pnl"].to_numpy(),
            eq["fees"].to_numpy(),
        ]),
    ))

    # ② Red dashed trailing drawdown limit
    fig.add_trace(go.Scatter(
        x=eq["soldTimestamp"], y=eq["dd_limit"],
        mode="lines",
        line=dict(color="#f43f5e", width=1.6, dash="dash"),
        name=f"Drawdown Limit (−${drawdown_buffer:,.0f})",
        hovertemplate="%{x|%b %d %H:%M}<br>DD Limit: <b>$%{y:,.2f}</b><extra></extra>",
    ))

    # ③ Gold dashed profit target
    pt_y = [float(profit_target)] * len(eq)
    fig.add_trace(go.Scatter(
        x=eq["soldTimestamp"], y=pt_y,
        mode="lines",
        line=dict(color="#fbbf24", width=1.4, dash="dash"),
        name=f"Profit Target (${profit_target:,.0f})",
        hovertemplate=f"Profit Target: <b>${profit_target:,.0f}</b><extra></extra>",
    ))

    # $0 baseline
    fig.add_hline(
        y=0,
        line=dict(color="rgba(255,255,255,0.12)", width=1, dash="dot"),
        annotation_text="  $0 baseline",
        annotation_font=dict(color="#45455e", size=10,
                             family="JetBrains Mono, monospace"),
    )

    # Peak marker
    pk_idx = int(eq["cum_net"].idxmax())
    pk_val = float(eq.loc[pk_idx, "cum_net"])
    if pk_val > 0:
        fig.add_trace(go.Scatter(
            x=[eq.loc[pk_idx, "soldTimestamp"]], y=[pk_val],
            mode="markers+text",
            marker=dict(color="#22c55e", size=9, line=dict(color="#0d0d14", width=2)),
            text=[f"  Peak +${pk_val:,.0f}"],
            textposition="top right",
            textfont=dict(size=10, color="#22c55e",
                         family="JetBrains Mono, monospace"),
            name="Peak", showlegend=False,
            hovertemplate="Peak: +$%{y:,.2f}<extra></extra>",
        ))

    fig.update_layout(
        **PLOT,
        margin=_ML,
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11, family="Inter, sans-serif", color="#7878a0")),
        xaxis=_ax(),
        yaxis=_ax(prefix="$", fmt=",", zeroline=True, zc="rgba(255,255,255,0.10)"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Drawdown status bar
    cur_dd  = float(df["dd_limit"].iloc[-1])
    cur_pnl = float(df["cum_net"].iloc[-1])
    headroom = cur_pnl - cur_dd
    locked   = cur_dd >= 0

    if locked:
        dd_c = "#22c55e"; dd_note = "🔒 Locked at $0 — buffer secured"
    elif headroom > drawdown_buffer * 0.5:
        dd_c = "#22c55e"; dd_note = f"✅ ${headroom:,.2f} headroom"
    elif headroom > drawdown_buffer * 0.2:
        dd_c = "#f59e0b"; dd_note = f"⚠️ Only ${headroom:,.2f} — approaching limit"
    else:
        dd_c = "#f43f5e"; dd_note = f"🚨 DANGER — ${headroom:,.2f} before breach!"

    st.markdown(
        f'<div class="dd-bar" style="color:{dd_c};">'
        f'<strong>Drawdown:</strong> &nbsp;Limit <strong>${cur_dd:,.2f}</strong>'
        f' &nbsp;|&nbsp; P&L <strong>${cur_pnl:,.2f}</strong>'
        f' &nbsp;|&nbsp; {dd_note}</div>',
        unsafe_allow_html=True,
    )

    # ── ANALYTICS ROW ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Trade Analytics</div>', unsafe_allow_html=True)
    al, ar = st.columns([3, 2])

    with al:
        st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#7878a0;'
                    'margin-bottom:0.5rem;">Net P&L by Day of Week</div>',
                    unsafe_allow_html=True)
        DOW = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        dow = (df.groupby("day_of_week")["net_pnl"].sum()
                 .reindex(DOW, fill_value=0).reset_index())
        dow.columns = ["day","pnl"]
        fig_d = go.Figure(go.Bar(
            x=dow["day"], y=dow["pnl"],
            marker_color=dow["pnl"].apply(lambda v:"#22c55e" if v>=0 else "#f43f5e"),
            marker_line_width=0,
            text=dow["pnl"].apply(lambda v:f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="JetBrains Mono, monospace", color="#7878a0"),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_d.update_layout(**PLOT, margin=_M, height=280, bargap=0.35,
                            xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","))
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar":False})

    with ar:
        st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#7878a0;'
                    'margin-bottom:0.5rem;">Win / Loss Split</div>',
                    unsafe_allow_html=True)
        fig_p = go.Figure(go.Pie(
            labels=["Wins","Losses"],
            values=[max(len(wins),0), max(len(losses),0)],
            hole=0.62,
            marker=dict(colors=["#22c55e","#f43f5e"],
                        line=dict(color=["#0d0d14","#0d0d14"], width=3)),
            textinfo="percent",
            textfont=dict(family="JetBrains Mono, monospace", size=12),
            hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
        ))
        fig_p.add_annotation(
            text=f"<b>{win_rate:.0f}%</b><br>"
                 f"<span style='font-size:11px'>Win Rate</span>",
            x=0.5, y=0.5,
            font=dict(size=22, family="Inter, sans-serif", color="#e8e8f0"),
            showarrow=False, align="center",
        )
        fig_p.update_layout(
            **PLOT, height=280, showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.12,
                        xanchor="center", x=0.5,
                        font=dict(size=11, family="Inter, sans-serif", color="#7878a0")),
            margin=dict(l=10, r=10, t=10, b=30),
        )
        st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar":False})

    # ── MONTHLY BAR ───────────────────────────────────────────────────────────
    monthly = (df.groupby("month_label")["net_pnl"].sum()
                 .reset_index().rename(columns={"month_label":"month","net_pnl":"pnl"}))
    if len(monthly) > 1:
        st.markdown('<div class="sec-hdr">Monthly Net P&L</div>', unsafe_allow_html=True)
        fig_m = go.Figure(go.Bar(
            x=monthly["month"], y=monthly["pnl"],
            marker_color=monthly["pnl"].apply(lambda v:"#2dd4bf" if v>=0 else "#f43f5e"),
            marker_line_width=0,
            text=monthly["pnl"].apply(lambda v:f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="JetBrains Mono, monospace", color="#7878a0"),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_m.update_layout(**PLOT, margin=_M, height=230, bargap=0.3,
                            xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","))
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})

    # ── TRADE HISTORY TABLE ───────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Trade History</div>', unsafe_allow_html=True)

    tbl = df[[
        "trade_num","soldTimestamp","symbol","direction","qty",
        "buyPrice","sellPrice","gross_pnl","fees","net_pnl","duration",
    ]].copy().rename(columns={
        "trade_num":"#","soldTimestamp":"Date / Time",
        "symbol":"Symbol","direction":"Dir","qty":"Qty",
        "buyPrice":"Entry","sellPrice":"Exit",
        "gross_pnl":"Gross P&L","fees":"Fees","net_pnl":"Net P&L",
        "duration":"Duration",
    })

    tbl["Date / Time"] = tbl["Date / Time"].dt.strftime("%b %d %Y  %H:%M")
    tbl["Entry"] = tbl["Entry"].apply(lambda v: f"${v:,.2f}" if pd.notna(v) and v!=0 else "—")
    tbl["Exit"]  = tbl["Exit"].apply(lambda v: f"${v:,.2f}"  if pd.notna(v) and v!=0 else "—")

    # Keep numeric columns for styling, format display copies
    net_num   = tbl["Net P&L"].copy()
    dir_vals  = tbl["Dir"].copy()

    tbl["Gross P&L"] = tbl["Gross P&L"].apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")
    tbl["Fees"]      = tbl["Fees"].apply(lambda v: f"-${v:,.2f}" if v>0 else "—")
    tbl["Net P&L"]   = net_num.apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")

    tbl = tbl.iloc[::-1].reset_index(drop=True)
    # Reverse the aux series to match
    net_num  = net_num.iloc[::-1].reset_index(drop=True)
    dir_vals = dir_vals.iloc[::-1].reset_index(drop=True)

    def _color_net(v):
        """Style Net P&L column by reading numeric value from aux series."""
        return ""  # handled via color_map below

    def _style_row(row):
        styles = [""] * len(row.columns) if hasattr(row, "columns") else [""] * len(row)
        return styles

    # Build styled dataframe
    styled = tbl.style.apply(
        lambda col: [
            (f"color: #22c55e; font-weight:600; font-family:'JetBrains Mono',monospace"
             if net_num.iloc[i] > 0
             else f"color: #f43f5e; font-weight:600; font-family:'JetBrains Mono',monospace")
            for i in range(len(col))
        ],
        subset=["Net P&L"],
        axis=0,
    ).apply(
        lambda col: [
            (f"color: #22c55e; font-weight:600"
             if dir_vals.iloc[i] == "Long"
             else f"color: #f43f5e; font-weight:600")
            for i in range(len(col))
        ],
        subset=["Dir"],
        axis=0,
    ).set_properties(**{
        "font-family": "JetBrains Mono, monospace",
        "font-size": "0.8rem",
    }).set_table_styles([
        {"selector":"thead th",
         "props":[("background","#1a1a28"),("color","#7878a0"),
                  ("font-family","Inter, sans-serif"),("font-size","0.68rem"),
                  ("letter-spacing","0.08em"),("text-transform","uppercase"),
                  ("padding","10px 12px")]},
        {"selector":"tbody td",
         "props":[("background","#181824"),("padding","8px 12px")]},
        {"selector":"tbody tr:hover td",
         "props":[("background","#1e1e2e")]},
    ])

    st.dataframe(styled, use_container_width=True, hide_index=True,
                 height=min(40 * len(tbl) + 45, 500))

    # ── FOOTER PILLS ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    p1,p2,p3,p4,p5,p6 = st.columns(6)
    def pill(col, lbl, val):
        col.markdown(f'<div class="pill">{lbl}<br><strong>{val}</strong></div>',
                     unsafe_allow_html=True)

    lw = f"${float(wins['net_pnl'].max()):,.2f}"   if len(wins)   else "—"
    ll = f"${float(losses['net_pnl'].min()):,.2f}" if len(losses) else "—"
    pill(p1, "Gross Profit",    f"${float(df['gross_pnl'].clip(lower=0).sum()):,.2f}")
    pill(p2, "Total Fees",      f"-${total_fees:,.2f}")
    pill(p3, "Largest Win",     lw)
    pill(p4, "Largest Loss",    ll)
    pill(p5, "Expectancy",      f"${expectancy:,.2f}/trade")
    pill(p6, "Symbols Traded",  str(df["symbol"].nunique()))


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB: CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Calendar":

    st.markdown('<div class="sec-hdr">Select Month</div>', unsafe_allow_html=True)

    # Month/year selector
    all_dates  = sorted(df["trade_date"].unique())
    all_months = sorted({d.replace(day=1) for d in all_dates})
    month_opts = [d.strftime("%B %Y") for d in all_months]

    sel_month_str = st.selectbox("Month", month_opts,
                                  index=len(month_opts)-1,
                                  label_visibility="collapsed")
    sel_month = pd.to_datetime(sel_month_str, format="%B %Y").date()

    # Daily PnL for selected month
    daily = (df[df["soldTimestamp"].dt.year == sel_month.year]
             [df["soldTimestamp"].dt.month == sel_month.month]
             .groupby("trade_date")["net_pnl"].sum())

    # Summary for month
    m_net   = float(daily.sum()) if len(daily) else 0.0
    m_days  = len(daily)
    m_green = int((daily > 0).sum())
    m_red   = int((daily < 0).sum())

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Month Net P&L",  fmt_usd(m_net, sign=True))
    s2.metric("Trading Days",   str(m_days))
    s3.metric("Green Days",     str(m_green))
    s4.metric("Red Days",       str(m_red))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">Daily P&L Calendar</div>', unsafe_allow_html=True)

    # Build calendar grid HTML
    year, month = sel_month.year, sel_month.month
    cal = calendar.Calendar(firstweekday=0)  # Monday first
    month_days = cal.monthdayscalendar(year, month)
    dow_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    # Header row
    hdr_html = "".join(f'<div class="cal-day-hdr">{d}</div>' for d in dow_labels)

    # Day cells
    cells_html = ""
    for week in month_days:
        for day_n in week:
            if day_n == 0:
                cells_html += '<div class="cal-day empty"></div>'
                continue
            d_obj = date(year, month, day_n)
            pnl_v = daily.get(d_obj, None)
            cls   = ""
            pv_html = ""
            if pnl_v is not None:
                cls     = "pos" if pnl_v >= 0 else "neg"
                sign    = "+" if pnl_v >= 0 else ""
                pv_html = f'<div class="pv">{sign}${pnl_v:,.0f}</div>'
            cells_html += (
                f'<div class="cal-day {cls}">'
                f'<div class="dn">{day_n}</div>'
                f'{pv_html}</div>'
            )

    st.markdown(
        f'<div class="cal-grid">{hdr_html}{cells_html}</div>',
        unsafe_allow_html=True,
    )

    # Monthly bar chart breakdown
    if len(daily) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Daily Breakdown</div>', unsafe_allow_html=True)
        daily_df = daily.reset_index()
        daily_df.columns = ["date","pnl"]
        daily_df["date_str"] = daily_df["date"].apply(lambda d: d.strftime("%b %d"))
        fig_cal = go.Figure(go.Bar(
            x=daily_df["date_str"], y=daily_df["pnl"],
            marker_color=daily_df["pnl"].apply(lambda v:"#22c55e" if v>=0 else "#f43f5e"),
            marker_line_width=0,
            text=daily_df["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, family="JetBrains Mono, monospace", color="#7878a0"),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_cal.update_layout(
            **PLOT, margin=_M, height=260, bargap=0.3,
            xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","),
        )
        st.plotly_chart(fig_cal, use_container_width=True,
                        config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB: JOURNAL
# ═══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Journal":

    st.markdown('<div class="sec-hdr">Daily Trading Journal</div>',
                unsafe_allow_html=True)

    # Date picker
    trade_dates = sorted(df["trade_date"].unique(), reverse=True)
    sel_date    = st.date_input(
        "Select Date",
        value=trade_dates[0] if trade_dates else date.today(),
        min_value=trade_dates[-1] if trade_dates else date.today() - timedelta(days=365),
        max_value=trade_dates[0]  if trade_dates else date.today(),
    )

    # Trades for selected date
    day_trades = df[df["trade_date"] == sel_date].copy()
    day_net    = float(day_trades["net_pnl"].sum()) if len(day_trades) else 0.0
    day_gross  = float(day_trades["gross_pnl"].sum()) if len(day_trades) else 0.0
    day_fees   = float(day_trades["fees"].sum()) if len(day_trades) else 0.0
    day_w      = int((day_trades["net_pnl"] > 0).sum())
    day_l      = int((day_trades["net_pnl"] < 0).sum())

    # Date card header
    pnl_color = "#22c55e" if day_net >= 0 else "#f43f5e"
    pnl_sign  = "+" if day_net >= 0 else ""
    st.markdown(
        f"""<div class="jnl-date-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                          letter-spacing:0.1em;text-transform:uppercase;color:#45455e;">
                {sel_date.strftime("%A")}</div>
              <div style="font-family:'Inter',sans-serif;font-size:1.4rem;font-weight:700;
                          color:#e8e8f0;letter-spacing:-0.02em;margin-top:2px;">
                {sel_date.strftime("%B %d, %Y")}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;
                          font-weight:700;color:{pnl_color};">
                {pnl_sign}${abs(day_net):,.2f}</div>
              <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#45455e;">
                NET P&L &nbsp;·&nbsp; {day_w}W / {day_l}L</div>
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Day metrics
    j1, j2, j3, j4 = st.columns(4)
    j1.metric("Gross P&L",   fmt_usd(day_gross, sign=True), delta_color="off")
    j2.metric("Total Fees",  f"-${day_fees:,.2f}", delta_color="off")
    j3.metric("Net P&L",     fmt_usd(day_net, sign=True))
    j4.metric("Trades",      str(len(day_trades)), delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # Notes area
    jl, jr = st.columns([3, 2])

    with jl:
        st.markdown('<div class="sec-hdr">Daily Notes & Thoughts</div>',
                    unsafe_allow_html=True)
        note_key = f"note_{sel_date}"
        if note_key not in st.session_state:
            st.session_state[note_key] = ""
        note = st.text_area(
            "Your notes",
            value=st.session_state[note_key],
            height=200,
            placeholder="What went well today? What would you do differently? "
                        "Market conditions, emotional state, rule violations...",
            label_visibility="collapsed",
            key=note_key + "_input",
        )
        if st.button("💾  Save Note", type="secondary"):
            st.session_state[note_key] = note
            st.success("Note saved for this session.")

    with jr:
        st.markdown('<div class="sec-hdr">Day\'s Trades</div>',
                    unsafe_allow_html=True)
        if len(day_trades) == 0:
            st.markdown(
                '<div style="font-family:\'Inter\',sans-serif;font-size:0.85rem;'
                'color:#45455e;padding:2rem 0;text-align:center;">No trades on this date.</div>',
                unsafe_allow_html=True,
            )
        else:
            dt = day_trades[["trade_num","symbol","direction","qty",
                              "gross_pnl","fees","net_pnl","duration"]].copy()
            dt.columns = ["#","Symbol","Dir","Qty","Gross","Fees","Net","Dur"]

            # Numeric refs before formatting
            net_ref = dt["Net"].copy()
            dir_ref = dt["Dir"].copy()

            dt["Gross"] = dt["Gross"].apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")
            dt["Fees"]  = dt["Fees"].apply(lambda v: f"-${v:,.2f}"  if v>0 else "—")
            dt["Net"]   = net_ref.apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")

            styled_dt = dt.style.apply(
                lambda col: [
                    ("color:#22c55e;font-weight:600" if net_ref.iloc[i]>0
                     else "color:#f43f5e;font-weight:600")
                    for i in range(len(col))
                ], subset=["Net"], axis=0,
            ).apply(
                lambda col: [
                    ("color:#22c55e;font-weight:600" if dir_ref.iloc[i]=="Long"
                     else "color:#f43f5e;font-weight:600")
                    for i in range(len(col))
                ], subset=["Dir"], axis=0,
            ).set_properties(**{"font-family":"JetBrains Mono,monospace","font-size":"0.78rem"})

            st.dataframe(styled_dt, use_container_width=True, hide_index=True,
                         height=min(40*len(dt)+45, 360))
