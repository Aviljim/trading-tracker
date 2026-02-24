"""
TradeLore Capital — Luxury Trading Journal
===========================================
Single-file Streamlit app.

requirements.txt:
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
import re, io, calendar
from datetime import date, timedelta

try:
    from streamlit_option_menu import option_menu
    _HAS_MENU = True
except ImportError:
    _HAS_MENU = False

# ──────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be the very first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeLore Capital",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
#  PALETTE CONSTANTS  (Python-side for chart colours)
# ──────────────────────────────────────────────────────────────────────────────
GOLD    = "#C5A350"
GOLD_LT = "#D4B86A"
GOLD_DIM= "rgba(197,163,80,0.15)"
OBS     = "#0E1117"          # obsidian background
CARD    = "#161B22"          # card background
CARD2   = "#1C2330"
BORDER  = "#21262D"
BORDER2 = "#30363D"
TEXT    = "#E6EDF3"
TEXT2   = "#8B949E"
TEXT3   = "#484F58"
GREEN   = "#3FB950"
RED     = "#F85149"
GREEN_D = "rgba(63,185,80,0.10)"
RED_D   = "rgba(248,81,73,0.10)"

# ──────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS — Montserrat headings, Inter data, gold accents
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --obs:    {OBS};
    --card:   {CARD};
    --card2:  {CARD2};
    --border: {BORDER};
    --bhi:    {BORDER2};
    --text:   {TEXT};
    --text2:  {TEXT2};
    --text3:  {TEXT3};
    --gold:   {GOLD};
    --goldl:  {GOLD_LT};
    --green:  {GREEN};
    --red:    {RED};
}}

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background-color: var(--obs) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif !important;
}}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: #0B0F15 !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebar"] input {{
    background: #13181F !important;
    border: 1px solid var(--bhi) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}}
[data-testid="stFileUploader"] {{
    background: #13181F !important;
    border: 1px dashed var(--bhi) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stFileUploader label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: var(--text3) !important;
}}

/* ── Chrome removal ──────────────────────────────────────────────────────── */
header[data-testid="stHeader"], #MainMenu, footer {{ display: none !important; }}
.block-container {{ padding: 1.6rem 2.4rem 3rem !important; max-width: 100% !important; }}
hr {{ border-color: var(--border) !important; margin: 1rem 0 !important; }}
[data-testid="stVerticalBlock"] > div {{ gap: 0.6rem; }}

/* ── Metric cards ────────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem 0.9rem !important;
    transition: border-color 0.18s, background 0.18s;
    position: relative;
    overflow: hidden;
}}
div[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {GOLD}, transparent);
    opacity: 0;
    transition: opacity 0.18s;
}}
div[data-testid="metric-container"]:hover {{
    background: var(--card2) !important;
    border-color: var(--bhi) !important;
}}
div[data-testid="metric-container"]:hover::before {{ opacity: 1; }}

div[data-testid="metric-container"] label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.66rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text3) !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
}}

/* ── Tables ──────────────────────────────────────────────────────────────── */
.stDataFrame {{
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Section headers ─────────────────────────────────────────────────────── */
.lx-hdr {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {GOLD};
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.lx-hdr::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, {BORDER2}, transparent);
}}

/* ── Page wordmark ───────────────────────────────────────────────────────── */
.wordmark {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text);
    line-height: 1;
}}
.wordmark span {{ color: {GOLD}; }}
.wordmark-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text3);
    margin-top: 3px;
}}

/* ── Page title area ────────────────────────────────────────────────────── */
.pg-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.03em;
    line-height: 1.15;
}}
.pg-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    color: var(--text2);
    margin-top: 3px;
}}

/* ── Gold badge ─────────────────────────────────────────────────────────── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 11px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.05em;
}}
.live  {{ background: rgba(63,185,80,0.12);   color: {GREEN}; border: 1px solid rgba(63,185,80,0.3); }}
.demo  {{ background: rgba(197,163,80,0.12);  color: {GOLD};  border: 1px solid rgba(197,163,80,0.3); }}
.none  {{ background: rgba(248,81,73,0.12);   color: {RED};   border: 1px solid rgba(248,81,73,0.3); }}

/* ── Stat pills ─────────────────────────────────────────────────────────── */
.pill {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text2);
    text-align: center;
    line-height: 1.9;
}}
.pill strong {{
    display: block;
    color: var(--text);
    font-size: 0.9rem;
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
}}

/* ── Upload hint ─────────────────────────────────────────────────────────── */
.up-hint {{
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text3);
    text-align: center;
    margin-top: 6px;
    line-height: 1.6;
}}

/* ── Drawdown bar ────────────────────────────────────────────────────────── */
.dd-bar {{
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    margin-bottom: 0.5rem;
    border: 1px solid;
}}

/* ── Calendar ────────────────────────────────────────────────────────────── */
.cal-wrap {{ margin-top: 0.5rem; }}

/* ── Journal ─────────────────────────────────────────────────────────────── */
.jnl-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid {GOLD};
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}}
textarea {{
    background: #13181F !important;
    color: var(--text) !important;
    border: 1px solid var(--bhi) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
}}

/* ── Withdrawal callout ──────────────────────────────────────────────────── */
.wd-note {{
    background: rgba(197,163,80,0.06);
    border: 1px solid rgba(197,163,80,0.2);
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    color: {GOLD};
    margin-bottom: 0.6rem;
}}

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: var(--obs); }}
::-webkit-scrollbar-thumb {{ background: var(--bhi); border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
#  PLOTLY HELPERS  — PLOT dict has NO xaxis/yaxis/margin (prevents duplicate-kwarg errors)
# ──────────────────────────────────────────────────────────────────────────────
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TEXT2, size=12),
    hoverlabel=dict(
        bgcolor=CARD2, bordercolor=BORDER2,
        font=dict(family="JetBrains Mono, monospace", size=12, color=TEXT),
    ),
)

def _ax(prefix="", fmt=",", zeroline=False, zc="rgba(255,255,255,0.08)"):
    return dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.05)",
        tickfont=dict(size=11, color=TEXT3, family="JetBrains Mono, monospace"),
        zeroline=zeroline,
        zerolinecolor=zc,
        zerolinewidth=1,
        tickprefix=prefix,
        tickformat=fmt,
    )

_M  = dict(l=8, r=8, t=28, b=8)
_ML = dict(l=8, r=8, t=48, b=8)


# ──────────────────────────────────────────────────────────────────────────────
#  PURE MATH HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def parse_pnl(raw) -> float:
    """
    Strict broker PnL parser:
      '$1,234.56'   →  1234.56
      '$(1,234.56)' → -1234.56   (parentheses = negative)
      '(234)'       → -234.0
      -234          → -234.0
    """
    if pd.isna(raw):
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    negative = "(" in s
    cleaned = re.sub(r"[^\d\.]", "", s)
    if not cleaned:
        return 0.0
    try:
        v = float(cleaned)
        return -v if negative else v
    except ValueError:
        return 0.0


def calc_fee(symbol: str, qty, nq_fee: float, mnq_fee: float) -> float:
    """
    MNQ checked BEFORE NQ to avoid substring collision.
      MNQ → mnq_fee * qty
      NQ  → nq_fee  * qty
      else → 0.0
    """
    sym = str(symbol).upper().strip()
    try:
        q = int(float(str(qty)))
    except (ValueError, TypeError):
        q = 1
    if "MNQ" in sym:
        return round(mnq_fee * q, 2)
    if "NQ" in sym:
        return round(nq_fee * q, 2)
    return 0.0


def is_withdrawal(row) -> bool:
    """True if the row should be excluded (withdrawal, transfer, zero qty)."""
    sym = str(row.get("symbol", "")).upper().strip()
    if any(k in sym for k in ("WITHDRAWAL", "TRANSFER", "DEPOSIT")):
        return True
    try:
        if float(str(row.get("qty", 1))) == 0:
            return True
    except (ValueError, TypeError):
        pass
    return False


def trailing_dd(cum_net: pd.Series, buf: float) -> pd.Series:
    """min(0, HWM − buf) — starts at −buf, trails up, locks at 0."""
    hwm = cum_net.cummax()
    return (hwm - buf).clip(upper=0.0)


def streak_calc(pnl: pd.Series):
    mw = ml = cw = cl = 0
    for v in pnl:
        if v > 0:
            cw += 1; cl = 0; mw = max(mw, cw)
        elif v < 0:
            cl += 1; cw = 0; ml = max(ml, cl)
        else:
            cw = cl = 0
    return mw, ml


def max_dd_val(cum: pd.Series) -> float:
    return float(abs((cum - cum.cummax()).min()))


def dist_from_peak(cum: pd.Series) -> float:
    return max(0.0, float(cum.max()) - float(cum.iloc[-1]))


def fmt_usd(v: float, sign=False) -> str:
    p = "+" if (sign and v > 0) else ""
    if abs(v) >= 1_000_000:
        return f"{p}${v/1e6:.2f}M"
    return f"{p}${v:,.2f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


# ──────────────────────────────────────────────────────────────────────────────
#  DEMO DATA  (realistic Tradovate-style CSV)
# ──────────────────────────────────────────────────────────────────────────────

def _demo() -> pd.DataFrame:
    rng  = np.random.default_rng(7)
    syms = ["NQ","MNQ","MNQ","NQ","ES","MNQ","NQ","MNQ","NQ","MNQ"]
    wts  = [0.20,0.25,0.10,0.15,0.05,0.08,0.07,0.05,0.03,0.02]
    base = pd.Timestamp("2025-10-06 09:35:00")
    rows = []
    for i in range(90):
        sym   = rng.choice(syms, p=wts)
        qty   = int(rng.choice([1,2,3,5]))
        win   = rng.random() < 0.575
        pnl   = round(float(abs(rng.normal(300,220))) if win
                      else -float(abs(rng.normal(170,120))), 2)
        bp    = round(float(rng.uniform(18000,22000)), 2)
        sp    = round(bp + pnl/qty, 2)
        bought= base + pd.Timedelta(days=int(i//5),
                                    hours=int(rng.integers(0,7)),
                                    minutes=int(rng.integers(0,55)))
        mins  = int(rng.integers(1,80))
        sold  = bought + pd.Timedelta(minutes=mins)
        pstr  = f"${pnl:.2f}" if pnl >= 0 else f"$({abs(pnl):.2f})"
        rows.append(dict(
            symbol=sym, _priceFormat="0.00", _priceFormatType="DECIMAL",
            _tickSize=0.25, buyFillId=f"B{i}", sellFillId=f"S{i}",
            qty=qty, buyPrice=bp, sellPrice=sp, pnl=pstr,
            boughtTimestamp=bought.strftime("%Y-%m-%dT%H:%M:%S"),
            soldTimestamp=sold.strftime("%Y-%m-%dT%H:%M:%S"),
            duration=f"{mins}m",
        ))
    # Add a withdrawal row
    rows.append(dict(
        symbol="Withdrawal", _priceFormat="", _priceFormatType="",
        _tickSize=0, buyFillId="", sellFillId="",
        qty=0, buyPrice=0, sellPrice=0, pnl="$(1500.00)",
        boughtTimestamp="2025-11-01T12:00:00",
        soldTimestamp="2025-11-01T12:00:00",
        duration="0m",
    ))
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────────────
#  DATA PROCESSING
# ──────────────────────────────────────────────────────────────────────────────

def process(raw: pd.DataFrame, starting: float,
            nq_fee: float, mnq_fee: float,
            dd_buf: float, profit_target: float) -> dict:
    """
    Returns a dict with:
      df          — clean trade rows (no withdrawals)
      withdrawals — withdrawal/transfer rows
      total_wd    — sum of withdrawal amounts (positive number)
    """
    df = raw.copy()

    # Parse timestamps first so we can sort
    df["soldTimestamp"]   = pd.to_datetime(df["soldTimestamp"],   errors="coerce")
    df["boughtTimestamp"] = pd.to_datetime(df["boughtTimestamp"], errors="coerce")

    # Split withdrawals out before any PnL math
    wd_mask   = df.apply(is_withdrawal, axis=1)
    wd_df     = df[wd_mask].copy()
    df        = df[~wd_mask].copy()

    total_wd  = float(wd_df["pnl"].apply(parse_pnl).abs().sum())

    # Drop rows without a valid sold timestamp
    df = df.dropna(subset=["soldTimestamp"]).sort_values("soldTimestamp").reset_index(drop=True)

    # ── Gross PnL ────────────────────────────────────────────────────────────
    df["gross_pnl"] = df["pnl"].apply(parse_pnl)

    # ── Fees (Tradovate round-trip per contract) ──────────────────────────────
    df["fees"] = df.apply(
        lambda r: calc_fee(r["symbol"], r.get("qty", 1), nq_fee, mnq_fee), axis=1
    )

    # ── Net PnL = Gross − Fee ─────────────────────────────────────────────────
    df["net_pnl"] = df["gross_pnl"] - df["fees"]

    # ── Cumulative series (both start at $0) ──────────────────────────────────
    df["cum_gross"] = df["gross_pnl"].cumsum()
    df["cum_net"]   = df["net_pnl"].cumsum()

    # ── Equity: Starting Balance + Cumulative Net PnL ─────────────────────────
    df["equity"] = starting + df["cum_net"]

    # ── Trailing drawdown ─────────────────────────────────────────────────────
    df["dd_limit"] = trailing_dd(df["cum_net"], buf=dd_buf)

    # ── Direction ─────────────────────────────────────────────────────────────
    df["direction"] = np.where(
        df["boughtTimestamp"] < df["soldTimestamp"], "Long", "Short"
    )

    # ── Trade hour ────────────────────────────────────────────────────────────
    df["hour"]       = df["soldTimestamp"].dt.hour
    df["trade_date"] = df["soldTimestamp"].dt.date
    df["day_of_week"]= df["soldTimestamp"].dt.day_name()
    df["month_label"]= df["soldTimestamp"].dt.strftime("%b '%y")
    df["trade_num"]  = range(1, len(df) + 1)

    return {"df": df, "withdrawals": wd_df, "total_wd": total_wd}


@st.cache_data(show_spinner=False)
def load_csv(data: bytes, starting: float, nq_fee: float, mnq_fee: float,
             dd_buf: float, profit_target: float) -> dict:
    raw = pd.read_csv(io.BytesIO(data))
    return process(raw, starting, nq_fee, mnq_fee, dd_buf, profit_target)


# ──────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Wordmark
    st.markdown("""
    <div style="padding:0.6rem 0 1.2rem">
      <div class="wordmark">Trade<span>Lore</span></div>
      <div class="wordmark-sub">Capital · Analytics</div>
    </div>""", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    if _HAS_MENU:
        active_tab = option_menu(
            menu_title=None,
            options=["Dashboard", "Calendar", "Journal"],
            icons=["graph-up-arrow", "calendar3", "journal-bookmark"],
            default_index=0,
            styles={
                "container":         {"padding":"4px 0","background":"transparent"},
                "icon":              {"color":GOLD,"font-size":"13px"},
                "nav-link":          {"font-family":"Inter,sans-serif",
                                      "font-size":"0.82rem","color":TEXT2,
                                      "border-radius":"7px",
                                      "--hover-color":CARD2},
                "nav-link-selected": {"background":f"rgba(197,163,80,0.12)",
                                      "color":GOLD,"font-weight":"600"},
            },
        )
    else:
        active_tab = st.radio("Navigation", ["Dashboard","Calendar","Journal"],
                              label_visibility="collapsed")

    st.markdown("---")

    # ── Account setup ─────────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;'
                f'text-transform:uppercase;color:{TEXT3};margin-bottom:0.5rem;">'
                f'Account Setup</div>', unsafe_allow_html=True)

    starting_balance = st.number_input(
        "Starting Balance ($)", min_value=0.0, value=50_000.0,
        step=1_000.0, format="%.2f",
    )
    dd_buffer = st.number_input(
        "Trailing Drawdown Buffer ($)", min_value=100.0, value=2_000.0,
        step=100.0, format="%.0f",
    )
    profit_target = st.number_input(
        "Profit Target ($)", min_value=0.0, value=3_000.0,
        step=100.0, format="%.0f",
    )

    st.markdown("---")

    # ── Commission inputs ─────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;'
                f'text-transform:uppercase;color:{TEXT3};margin-bottom:0.5rem;">'
                f'Tradovate Commissions</div>', unsafe_allow_html=True)

    nq_fee  = st.number_input("NQ Round-Trip Fee ($)",  min_value=0.0, value=4.14,
                               step=0.01, format="%.2f")
    mnq_fee = st.number_input("MNQ Round-Trip Fee ($)", min_value=0.0, value=1.14,
                               step=0.01, format="%.2f")

    st.markdown("---")

    # ── File upload ───────────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:0.64rem;font-weight:700;letter-spacing:0.12em;'
                f'text-transform:uppercase;color:{TEXT3};margin-bottom:0.5rem;">'
                f'Import Trades</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
    st.markdown('<div class="up-hint">symbol · pnl · qty · buyPrice · sellPrice<br>'
                'boughtTimestamp · soldTimestamp · duration</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    use_demo = st.checkbox("Load demo data", value=(uploaded is None))


# ──────────────────────────────────────────────────────────────────────────────
#  RESOLVE DATA
# ──────────────────────────────────────────────────────────────────────────────
_args = (starting_balance, nq_fee, mnq_fee, dd_buffer, profit_target)

if uploaded is not None:
    result      = load_csv(uploaded.read(), *_args)
    data_source = "live"
elif use_demo:
    result      = process(_demo(), *_args)
    data_source = "demo"
else:
    result      = None
    data_source = "none"


# ──────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER
# ──────────────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
_titles = {
    "Dashboard": ("Performance Dashboard",
                  "Tradovate-matched metrics · equity curve · analytics"),
    "Calendar":  ("Trading Calendar",    "Daily P&L heatmap"),
    "Journal":   ("Trade Journal",       "Daily reflection & notes"),
}
ttl, sub = _titles.get(active_tab, ("Dashboard",""))
with h1:
    st.markdown(f'<div class="pg-title">{ttl}</div>'
                f'<div class="pg-sub">{sub}</div>', unsafe_allow_html=True)
with h2:
    cls = {"live":"live","demo":"demo","none":"none"}[data_source]
    lbl = {"live":"● LIVE","demo":"◆ DEMO","none":"✕ NONE"}[data_source]
    st.markdown(f'<div style="text-align:right;margin-top:1rem;">'
                f'<span class="badge {cls}">{lbl}</span></div>',
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
#  EMPTY STATE
# ──────────────────────────────────────────────────────────────────────────────
if result is None:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:50vh;text-align:center;">
      <div style="font-size:2.8rem;margin-bottom:1rem;opacity:0.3">⬡</div>
      <div style="font-family:'Montserrat',sans-serif;font-size:1.3rem;font-weight:700;
                  color:{TEXT};margin-bottom:0.4rem;">No data loaded</div>
      <div style="font-family:'Inter',sans-serif;font-size:0.85rem;color:{TEXT3};
                  max-width:340px;line-height:1.7;">
        Upload a Tradovate CSV export or enable <strong style="color:{GOLD}">demo data</strong>
        from the sidebar to begin.
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df       = result["df"]
total_wd = result["total_wd"]

if len(df) == 0:
    st.warning("No valid trade rows found in this file.")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
#  CORE METRICS  (shared across tabs)
# ──────────────────────────────────────────────────────────────────────────────
n_trades    = len(df)
wins        = df[df["net_pnl"] > 0]
losses      = df[df["net_pnl"] < 0]
total_gross = float(df["gross_pnl"].sum())
total_fees  = float(df["fees"].sum())
total_net   = float(df["net_pnl"].sum())

# Tradovate-style stat breakdown
gross_profit_sum = float(wins["gross_pnl"].sum())   if len(wins)   else 0.0
gross_loss_sum   = float(df[df["gross_pnl"] < 0]["gross_pnl"].sum()) if len(losses) else 0.0

# Profit Factor = Gross Profit / |Gross Loss|
profit_factor    = (gross_profit_sum / abs(gross_loss_sum)) if gross_loss_sum else float("inf")

curr_equity  = starting_balance + total_net          # ← exact Tradovate formula
win_rate     = len(wins) / n_trades * 100 if n_trades else 0.0
avg_win      = float(wins["net_pnl"].mean())   if len(wins)   else 0.0
avg_loss     = float(losses["net_pnl"].mean()) if len(losses) else 0.0
rr           = (avg_win / abs(avg_loss))        if avg_loss    else float("inf")
_mdd         = max_dd_val(df["cum_net"])
_dfp         = dist_from_peak(df["cum_net"])
total_ret    = (total_net / starting_balance * 100) if starting_balance else 0.0
win_st, loss_st = streak_calc(df["net_pnl"])
expectancy   = total_net / n_trades if n_trades else 0.0


# ══════════════════════════════════════════════════════════════════════════════
#  TAB: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if active_tab == "Dashboard":

    # Withdrawal notice
    if total_wd > 0:
        st.markdown(
            f'<div class="wd-note">⬡ &nbsp;'
            f'<strong>${total_wd:,.2f}</strong> in withdrawals/transfers '
            f'detected and excluded from PnL calculations.</div>',
            unsafe_allow_html=True,
        )

    # ── KPI ROW 1: Tradovate stat breakdown ──────────────────────────────────
    st.markdown('<div class="lx-hdr">Account Overview</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Current Equity",
        f"${curr_equity:,.2f}",
        f"{fmt_usd(total_net, sign=True)}  ({fmt_pct(total_ret)})",
    )
    k2.metric(
        "Gross Profit",
        f"${gross_profit_sum:,.2f}",
        f"{len(wins)} winning trades", delta_color="off",
    )
    k3.metric(
        "Gross Loss",
        f"${gross_loss_sum:,.2f}",
        f"{len(losses)} losing trades", delta_color="off",
    )
    pf_s = f"{profit_factor:.2f}×" if profit_factor != float("inf") else "∞"
    k4.metric(
        "Profit Factor", pf_s,
        "strong" if profit_factor > 1.5 else ("neutral" if profit_factor > 0.9 else "review"),
        delta_color="off",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI ROW 2 ────────────────────────────────────────────────────────────
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Total Net P&L", fmt_usd(total_net, sign=True),
              f"after ${total_fees:,.2f} fees", delta_color="off")
    k6.metric("Win Rate", fmt_pct(win_rate), f"{n_trades} trades", delta_color="off")
    k7.metric("Max All-Time Drawdown", fmt_usd(-_mdd),
              f"−{_mdd/starting_balance*100:.1f}% of balance", delta_color="inverse")
    k8.metric("Distance from Peak",
              fmt_usd(-_dfp) if _dfp > 0 else "+$0.00",
              "current pullback from ATH",
              delta_color="inverse" if _dfp > 0 else "off")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI ROW 3 ────────────────────────────────────────────────────────────
    k9, k10, k11, k12 = st.columns(4)
    k9.metric("Avg Win",   fmt_usd(avg_win),   f"{len(wins)} trades",   delta_color="off")
    k10.metric("Avg Loss", fmt_usd(avg_loss),  f"{len(losses)} trades", delta_color="off")
    k11.metric("Win Streak",  f"{win_st} trades",  "best consecutive", delta_color="off")
    k12.metric("Loss Streak", f"{loss_st} trades", "worst consecutive",delta_color="off")

    if total_wd > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        tw1, tw2 = st.columns([1, 3])
        tw1.metric("Total Withdrawn", f"${total_wd:,.2f}",
                   "excluded from P&L", delta_color="off")

    # ── EQUITY CURVE ─────────────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">Equity Curve — Cumulative Net P&L</div>',
                unsafe_allow_html=True)

    # Build a clean time-sorted origin + trade series
    # Prepend $0 origin point to anchor the curve
    origin = pd.DataFrame({
        "soldTimestamp": [df["soldTimestamp"].iloc[0] - pd.Timedelta(minutes=5)],
        "cum_net":       [0.0],
        "dd_limit":      [-float(dd_buffer)],
        "trade_num":     [0],
        "net_pnl":       [0.0],
        "fees":          [0.0],
    })
    eq = pd.concat(
        [origin, df[["soldTimestamp","cum_net","dd_limit","trade_num","net_pnl","fees"]]],
        ignore_index=True,
    )

    # Smooth: enforce strictly monotone time by deduplicating on index
    # (trades with identical timestamps get unique fractional-second offsets)
    ts = eq["soldTimestamp"].copy()
    seen = {}
    for i, t in ts.items():
        key = str(t)
        cnt = seen.get(key, 0)
        if cnt > 0:
            ts.at[i] = t + pd.Timedelta(milliseconds=cnt * 100)
        seen[key] = cnt + 1
    eq["ts_plot"] = ts

    fig = go.Figure()

    # ① Gold/green equity line with fill-under
    fig.add_trace(go.Scatter(
        x=eq["ts_plot"], y=eq["cum_net"],
        mode="lines",
        line=dict(color=GOLD, width=2.4, shape="spline", smoothing=0.8),
        fill="tozeroy",
        fillcolor=GOLD_DIM,
        name="Net P&L",
        hovertemplate=(
            "<b>Trade #%{customdata[0]}</b><br>"
            "%{x|%b %d %H:%M}<br>"
            "Cum. Net: <b>$%{y:,.2f}</b><br>"
            "Trade: $%{customdata[1]:,.2f}  Fees: $%{customdata[2]:,.2f}"
            "<extra></extra>"
        ),
        customdata=np.column_stack([
            eq["trade_num"].to_numpy(),
            eq["net_pnl"].to_numpy(),
            eq["fees"].to_numpy(),
        ]),
    ))

    # ② Red dashed trailing drawdown
    fig.add_trace(go.Scatter(
        x=eq["ts_plot"], y=eq["dd_limit"],
        mode="lines",
        line=dict(color=RED, width=1.6, dash="dash"),
        name=f"DD Limit (−${dd_buffer:,.0f})",
        hovertemplate="%{x|%b %d %H:%M}<br>DD Limit: <b>$%{y:,.2f}</b><extra></extra>",
    ))

    # ③ Gold dashed profit target
    fig.add_trace(go.Scatter(
        x=[eq["ts_plot"].iloc[0], eq["ts_plot"].iloc[-1]],
        y=[float(profit_target), float(profit_target)],
        mode="lines",
        line=dict(color=GOLD_LT, width=1.4, dash="dot"),
        name=f"Target (${profit_target:,.0f})",
        hovertemplate=f"Profit Target: <b>${profit_target:,.0f}</b><extra></extra>",
    ))

    # $0 baseline
    fig.add_hline(
        y=0, line=dict(color="rgba(255,255,255,0.1)", width=1, dash="dot"),
        annotation_text=" $0",
        annotation_font=dict(color=TEXT3, size=10, family="JetBrains Mono, monospace"),
    )

    # Peak marker
    pk_i = int(eq["cum_net"].idxmax())
    pk_v = float(eq.loc[pk_i, "cum_net"])
    if pk_v > 0:
        fig.add_trace(go.Scatter(
            x=[eq.loc[pk_i, "ts_plot"]], y=[pk_v],
            mode="markers+text",
            marker=dict(color=GOLD, size=9, line=dict(color=OBS, width=2)),
            text=[f"  +${pk_v:,.0f}"],
            textposition="top right",
            textfont=dict(size=10, color=GOLD, family="JetBrains Mono, monospace"),
            name="Peak", showlegend=False,
            hovertemplate="ATH: +$%{y:,.2f}<extra></extra>",
        ))

    fig.update_layout(
        **PLOT,
        margin=_ML, height=400,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, family="Inter, sans-serif", color=TEXT2),
        ),
        xaxis=_ax(),
        yaxis=_ax(prefix="$", fmt=",", zeroline=True, zc="rgba(255,255,255,0.08)"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Drawdown status bar
    cur_dd  = float(df["dd_limit"].iloc[-1])
    cur_pnl = float(df["cum_net"].iloc[-1])
    headroom = cur_pnl - cur_dd
    locked   = cur_dd >= 0

    if locked:
        dd_c = GREEN; dd_note = "🔒 Locked at $0 — buffer fully secured"
    elif headroom > dd_buffer * 0.5:
        dd_c = GREEN; dd_note = f"✅  ${headroom:,.2f} headroom"
    elif headroom > dd_buffer * 0.2:
        dd_c = "#F0A500"; dd_note = f"⚠️  ${headroom:,.2f} — approaching limit"
    else:
        dd_c = RED; dd_note = f"🚨  DANGER — ${headroom:,.2f} before breach"

    st.markdown(
        f'<div class="dd-bar" style="background:rgba(248,81,73,0.05);'
        f'border-color:rgba(248,81,73,0.2);color:{dd_c};">'
        f'<strong>Trailing Drawdown</strong> &nbsp;·&nbsp; '
        f'Limit <strong>${cur_dd:,.2f}</strong>'
        f' &nbsp;|&nbsp; P&L <strong>${cur_pnl:,.2f}</strong>'
        f' &nbsp;|&nbsp; {dd_note}</div>',
        unsafe_allow_html=True,
    )

    # ── ANALYTICS ROW — Day of week + Win/Loss ────────────────────────────────
    st.markdown('<div class="lx-hdr">Trade Analytics</div>', unsafe_allow_html=True)
    al, ar = st.columns([3, 2])

    with al:
        st.markdown(f'<div style="font-size:0.75rem;font-weight:600;color:{TEXT2};'
                    f'margin-bottom:0.4rem;">Net P&L by Day of Week</div>',
                    unsafe_allow_html=True)
        DOW = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        dow = (df.groupby("day_of_week")["net_pnl"].sum()
                 .reindex(DOW, fill_value=0).reset_index())
        dow.columns = ["day","pnl"]
        fig_d = go.Figure(go.Bar(
            x=dow["day"], y=dow["pnl"],
            marker_color=dow["pnl"].apply(lambda v: GOLD if v >= 0 else RED),
            marker_line_width=0,
            text=dow["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="JetBrains Mono, monospace", color=TEXT2),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_d.update_layout(**PLOT, margin=_M, height=270, bargap=0.35,
                            xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","))
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar":False})

    with ar:
        st.markdown(f'<div style="font-size:0.75rem;font-weight:600;color:{TEXT2};'
                    f'margin-bottom:0.4rem;">Win / Loss Split</div>',
                    unsafe_allow_html=True)
        fig_p = go.Figure(go.Pie(
            labels=["Wins","Losses"],
            values=[max(len(wins), 0), max(len(losses), 0)],
            hole=0.62,
            marker=dict(
                colors=[GOLD, RED],
                line=dict(color=[OBS, OBS], width=3),
            ),
            textinfo="percent",
            textfont=dict(family="JetBrains Mono, monospace", size=12),
            hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
        ))
        fig_p.add_annotation(
            text=f"<b>{win_rate:.0f}%</b><br>"
                 f"<span style='font-size:11px;color:{TEXT2}'>Win Rate</span>",
            x=0.5, y=0.5,
            font=dict(size=22, family="Montserrat, sans-serif", color=TEXT),
            showarrow=False, align="center",
        )
        fig_p.update_layout(
            **PLOT, height=270, showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.12,
                        xanchor="center", x=0.5,
                        font=dict(size=11, family="Inter, sans-serif", color=TEXT2)),
            margin=dict(l=8, r=8, t=8, b=28),
        )
        st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar":False})

    # ── 100x ANALYSIS CHARTS ─────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">100× Analysis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # ① Performance by Hour
    with c1:
        st.markdown(f'<div style="font-size:0.75rem;font-weight:600;color:{TEXT2};'
                    f'margin-bottom:0.4rem;">Performance by Hour of Day</div>',
                    unsafe_allow_html=True)
        hourly = (df.groupby("hour")["net_pnl"].sum()
                    .reindex(range(24), fill_value=0.0)
                    .reset_index())
        hourly.columns = ["hour","pnl"]
        hourly["label"] = hourly["hour"].apply(
            lambda h: f"{'12' if h==12 else str(h%12 or 12)}"
                      f"{'AM' if h<12 else 'PM'}"
        )
        fig_h = go.Figure(go.Bar(
            x=hourly["label"],
            y=hourly["pnl"],
            marker=dict(
                color=hourly["pnl"],
                colorscale=[[0, RED],[0.5,"rgba(197,163,80,0.3)"],[1, GOLD]],
                line_width=0,
            ),
            text=hourly["pnl"].apply(
                lambda v: f"${v:,.0f}" if v != 0 else ""
            ),
            textposition="outside",
            textfont=dict(size=9, family="JetBrains Mono, monospace", color=TEXT3),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_h.update_layout(**PLOT, margin=_M, height=265, bargap=0.3,
                            xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","))
        st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})

    # ② Long vs Short
    with c2:
        st.markdown(f'<div style="font-size:0.75rem;font-weight:600;color:{TEXT2};'
                    f'margin-bottom:0.4rem;">Long vs. Short P&L</div>',
                    unsafe_allow_html=True)
        ls = df.groupby("direction")["net_pnl"].agg(
            total="sum", count="count", avg="mean"
        ).reindex(["Long","Short"], fill_value=0).reset_index()

        colors_ls = [GOLD if v >= 0 else RED for v in ls["total"]]
        fig_ls = go.Figure(go.Bar(
            x=ls["total"],
            y=ls["direction"],
            orientation="h",
            marker=dict(color=colors_ls, line_width=0),
            text=ls["total"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=12, family="JetBrains Mono, monospace",
                         color=[GOLD if v>=0 else RED for v in ls["total"]]),
            customdata=np.column_stack([ls["count"].to_numpy(), ls["avg"].to_numpy()]),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Total: <b>$%{x:,.2f}</b><br>"
                "Trades: %{customdata[0]}<br>"
                "Avg: $%{customdata[1]:,.2f}<extra></extra>"
            ),
        ))
        fig_ls.update_layout(
            **PLOT, margin=_M, height=265,
            xaxis=_ax(prefix="$", fmt=","),
            yaxis=dict(
                tickfont=dict(size=13, color=TEXT, family="Montserrat, sans-serif",
                              weight="bold"),
                showgrid=False, linecolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig_ls, use_container_width=True, config={"displayModeBar":False})

    # ── MONTHLY BAR ───────────────────────────────────────────────────────────
    monthly = (df.groupby("month_label")["net_pnl"].sum()
                 .reset_index().rename(columns={"month_label":"m","net_pnl":"pnl"}))
    if len(monthly) > 1:
        st.markdown('<div class="lx-hdr">Monthly Net P&L</div>', unsafe_allow_html=True)
        fig_m = go.Figure(go.Bar(
            x=monthly["m"], y=monthly["pnl"],
            marker_color=monthly["pnl"].apply(lambda v: GOLD if v>=0 else RED),
            marker_line_width=0,
            text=monthly["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="JetBrains Mono, monospace", color=TEXT2),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_m.update_layout(**PLOT, margin=_M, height=225, bargap=0.3,
                            xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","))
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})

    # ── TRADE HISTORY TABLE ───────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">Trade History</div>', unsafe_allow_html=True)

    tbl = df[["trade_num","soldTimestamp","symbol","direction","qty",
              "buyPrice","sellPrice","gross_pnl","fees","net_pnl","duration"]].copy()
    tbl.columns = ["#","Date","Symbol","Dir","Qty",
                   "Entry","Exit","Gross P&L","Fees","Net P&L","Dur"]

    tbl["Date"]    = tbl["Date"].dt.strftime("%b %d %Y  %H:%M")
    tbl["Entry"]   = tbl["Entry"].apply(lambda v: f"${v:,.2f}" if pd.notna(v) and v!=0 else "—")
    tbl["Exit"]    = tbl["Exit"].apply(lambda v: f"${v:,.2f}"  if pd.notna(v) and v!=0 else "—")

    # Keep numeric refs for styling BEFORE formatting
    _net_num = tbl["Net P&L"].copy()
    _dir_ref = tbl["Dir"].copy()

    tbl["Gross P&L"] = tbl["Gross P&L"].apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")
    tbl["Fees"]      = tbl["Fees"].apply(lambda v: f"-${v:,.2f}" if v>0 else "—")
    tbl["Net P&L"]   = _net_num.apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")

    tbl = tbl.iloc[::-1].reset_index(drop=True)
    _net_num = _net_num.iloc[::-1].reset_index(drop=True)
    _dir_ref = _dir_ref.iloc[::-1].reset_index(drop=True)

    styled = (
        tbl.style
        .apply(lambda col: [
            (f"color:{GOLD};font-weight:700" if _net_num.iloc[i] > 0
             else f"color:{RED};font-weight:700")
            for i in range(len(col))
        ], subset=["Net P&L"], axis=0)
        .apply(lambda col: [
            (f"color:{GREEN};font-weight:600" if _dir_ref.iloc[i] == "Long"
             else f"color:{RED};font-weight:600")
            for i in range(len(col))
        ], subset=["Dir"], axis=0)
        .set_properties(**{
            "font-family": "JetBrains Mono, monospace",
            "font-size": "0.78rem",
        })
        .set_table_styles([
            {"selector":"thead th",
             "props":[("background",CARD2),("color",TEXT3),
                      ("font-family","Inter, sans-serif"),("font-size","0.63rem"),
                      ("letter-spacing","0.1em"),("text-transform","uppercase"),
                      ("padding","10px 12px")]},
            {"selector":"tbody td",
             "props":[("background",CARD),("padding","8px 12px")]},
            {"selector":"tbody tr:hover td",
             "props":[("background",CARD2)]},
        ])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True,
                 height=min(40*len(tbl)+45, 500))

    # ── FOOTER PILLS ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2, p3, p4, p5, p6 = st.columns(6)

    def pill(col, lbl: str, val: str):
        col.markdown(f'<div class="pill">{lbl}<br><strong>{val}</strong></div>',
                     unsafe_allow_html=True)

    lw = f"${float(wins['net_pnl'].max()):,.2f}"   if len(wins)   else "—"
    ll = f"${float(losses['net_pnl'].min()):,.2f}" if len(losses) else "—"

    pill(p1, "Gross Profit",  f"${gross_profit_sum:,.2f}")
    pill(p2, "Total Fees",    f"-${total_fees:,.2f}")
    pill(p3, "Largest Win",   lw)
    pill(p4, "Largest Loss",  ll)
    pill(p5, "Expectancy",    f"${expectancy:,.2f}")
    pill(p6, "Symbols",       str(df["symbol"].nunique()))


# ══════════════════════════════════════════════════════════════════════════════
#  TAB: CALENDAR (Plotly heatmap — gold=profit, red=loss)
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Calendar":

    st.markdown('<div class="lx-hdr">Select Month</div>', unsafe_allow_html=True)

    all_months = sorted({d.replace(day=1) for d in df["trade_date"].unique()})
    month_opts = [d.strftime("%B %Y") for d in all_months]
    sel_str    = st.selectbox("Month", month_opts, index=len(month_opts)-1,
                               label_visibility="collapsed")
    sel_month  = pd.to_datetime(sel_str, format="%B %Y").date()

    yr, mo = sel_month.year, sel_month.month

    # Daily PnL
    daily = (
        df[(df["soldTimestamp"].dt.year  == yr) &
           (df["soldTimestamp"].dt.month == mo)]
        .groupby("trade_date")["net_pnl"]
        .sum()
    )

    # Month summary
    m_net = float(daily.sum()) if len(daily) else 0.0
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Month Net P&L",   fmt_usd(m_net, sign=True))
    s2.metric("Trading Days",    str(len(daily)))
    s3.metric("Green Days",      str(int((daily > 0).sum())))
    s4.metric("Red Days",        str(int((daily <= 0).sum())))

    st.markdown('<div class="lx-hdr">P&L Heatmap Calendar</div>', unsafe_allow_html=True)

    # Build a 7-column (Mon…Sun) grid for the Plotly heatmap
    cal_obj    = calendar.Calendar(firstweekday=0)
    weeks      = cal_obj.monthdayscalendar(yr, mo)
    n_weeks    = len(weeks)
    dow_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    z_matrix    = []
    text_matrix = []
    hover_matrix= []

    for week in weeks:
        z_row = []; t_row = []; h_row = []
        for day_n in week:
            if day_n == 0:
                z_row.append(None)
                t_row.append("")
                h_row.append("")
            else:
                d_obj = date(yr, mo, day_n)
                pnl_v = daily.get(d_obj, None)
                if pnl_v is not None:
                    z_row.append(float(pnl_v))
                    sign = "+" if pnl_v >= 0 else ""
                    t_row.append(f"<b>{day_n}</b><br>{sign}${pnl_v:,.0f}")
                    h_row.append(f"<b>{d_obj.strftime('%b %d')}</b><br>"
                                 f"Net P&L: <b>${pnl_v:,.2f}</b>")
                else:
                    z_row.append(0.0)
                    t_row.append(f"<b>{day_n}</b>")
                    h_row.append(f"<b>{d_obj.strftime('%b %d')}</b><br>No trades")
        z_matrix.append(z_row)
        text_matrix.append(t_row)
        hover_matrix.append(h_row)

    # Gold-to-Red diverging colorscale (centred at 0)
    max_abs = max(abs(daily.max()) if len(daily) else 1,
                  abs(daily.min()) if len(daily) else 1)

    colorscale = [
        [0.0,   "#7B1E1E"],   # deep red (large loss)
        [0.35,  RED],
        [0.49,  "#3A2020"],
        [0.5,   "#1C2330"],   # neutral (no trades / zero)
        [0.51,  "#2A2210"],
        [0.65,  "#8B6914"],
        [1.0,   GOLD],        # rich gold (large profit)
    ]

    fig_cal = go.Figure(go.Heatmap(
        z=z_matrix,
        text=text_matrix,
        customdata=hover_matrix,
        x=dow_labels,
        y=[f"W{i+1}" for i in range(n_weeks)],
        colorscale=colorscale,
        zmid=0,
        zmin=-max_abs,
        zmax=max_abs,
        showscale=True,
        colorbar=dict(
            title=dict(text="Net P&L", font=dict(family="Inter", color=TEXT2, size=11)),
            tickfont=dict(family="JetBrains Mono", color=TEXT3, size=10),
            tickprefix="$",
            thickness=12,
            len=0.8,
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
        ),
        texttemplate="%{text}",
        textfont=dict(family="Inter, sans-serif", size=11, color=TEXT),
        hovertemplate="%{customdata}<extra></extra>",
        xgap=4,
        ygap=4,
    ))

    fig_cal.update_layout(
        **PLOT,
        height=max(280, n_weeks * 80),
        margin=dict(l=40, r=40, t=20, b=10),
        xaxis=dict(
            side="top",
            tickfont=dict(size=11, color=TEXT2, family="Montserrat, sans-serif"),
            showgrid=False, linecolor="rgba(0,0,0,0)",
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=10, color=TEXT3, family="JetBrains Mono, monospace"),
            showgrid=False, linecolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig_cal, use_container_width=True, config={"displayModeBar":False})

    # Daily breakdown bar
    if len(daily) > 0:
        st.markdown('<div class="lx-hdr">Daily Breakdown</div>', unsafe_allow_html=True)
        dd2 = daily.reset_index()
        dd2.columns = ["date","pnl"]
        dd2["ds"] = dd2["date"].apply(lambda d: d.strftime("%b %d"))
        fig_db = go.Figure(go.Bar(
            x=dd2["ds"], y=dd2["pnl"],
            marker_color=dd2["pnl"].apply(lambda v: GOLD if v >= 0 else RED),
            marker_line_width=0,
            text=dd2["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, family="JetBrains Mono, monospace", color=TEXT2),
            hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_db.update_layout(**PLOT, margin=_M, height=240, bargap=0.28,
                             xaxis=_ax(), yaxis=_ax(prefix="$", fmt=","))
        st.plotly_chart(fig_db, use_container_width=True, config={"displayModeBar":False})


# ══════════════════════════════════════════════════════════════════════════════
#  TAB: JOURNAL
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Journal":

    st.markdown('<div class="lx-hdr">Daily Journal</div>', unsafe_allow_html=True)

    trade_dates = sorted(df["trade_date"].unique(), reverse=True)
    sel_date = st.date_input(
        "Select Date", value=trade_dates[0] if trade_dates else date.today(),
        min_value=trade_dates[-1] if trade_dates else date.today() - timedelta(days=365),
        max_value=trade_dates[0]  if trade_dates else date.today(),
    )

    day_df    = df[df["trade_date"] == sel_date].copy()
    day_net   = float(day_df["net_pnl"].sum())   if len(day_df) else 0.0
    day_gross = float(day_df["gross_pnl"].sum()) if len(day_df) else 0.0
    day_fees  = float(day_df["fees"].sum())       if len(day_df) else 0.0
    day_w     = int((day_df["net_pnl"] > 0).sum())
    day_l     = int((day_df["net_pnl"] < 0).sum())

    pnl_c  = GOLD if day_net >= 0 else RED
    pnl_sg = "+" if day_net >= 0 else ""

    st.markdown(f"""
    <div class="jnl-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div style="font-family:'Montserrat',sans-serif;font-size:0.62rem;
                      font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
                      color:{TEXT3};">{sel_date.strftime('%A')}</div>
          <div style="font-family:'Montserrat',sans-serif;font-size:1.45rem;
                      font-weight:800;color:{TEXT};letter-spacing:-0.02em;margin-top:3px;">
            {sel_date.strftime('%B %d, %Y')}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-family:'Montserrat',sans-serif;font-size:1.9rem;
                      font-weight:800;color:{pnl_c};letter-spacing:-0.03em;">
            {pnl_sg}${abs(day_net):,.2f}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                      color:{TEXT3};margin-top:1px;">
            NET · {day_w}W / {day_l}L</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    j1, j2, j3, j4 = st.columns(4)
    j1.metric("Gross P&L",  fmt_usd(day_gross, sign=True), delta_color="off")
    j2.metric("Total Fees", f"-${day_fees:,.2f}",          delta_color="off")
    j3.metric("Net P&L",    fmt_usd(day_net, sign=True))
    j4.metric("Trades",     str(len(day_df)),              delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)
    jl, jr = st.columns([3, 2])

    with jl:
        st.markdown('<div class="lx-hdr">Notes & Reflection</div>', unsafe_allow_html=True)
        key = f"note_{sel_date}"
        if key not in st.session_state:
            st.session_state[key] = ""
        note = st.text_area(
            "Notes", value=st.session_state[key], height=200,
            placeholder="What went well? What would you change? Market conditions, "
                        "discipline, setups missed...",
            label_visibility="collapsed",
            key=key + "_ta",
        )
        if st.button("💾  Save Note", type="secondary"):
            st.session_state[key] = note
            st.success("Note saved for this session.")

    with jr:
        st.markdown("<div class='lx-hdr'>Day's Trades</div>", unsafe_allow_html=True)
        if len(day_df) == 0:
            st.markdown(f'<div style="font-family:Inter,sans-serif;font-size:0.85rem;'
                        f'color:{TEXT3};padding:2rem 0;text-align:center;">'
                        f'No trades on this date.</div>', unsafe_allow_html=True)
        else:
            dt = day_df[["trade_num","symbol","direction","qty",
                         "gross_pnl","fees","net_pnl","duration"]].copy()
            dt.columns = ["#","Symbol","Dir","Qty","Gross","Fees","Net","Dur"]
            _nr = dt["Net"].copy()
            _dr = dt["Dir"].copy()
            dt["Gross"] = dt["Gross"].apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")
            dt["Fees"]  = dt["Fees"].apply(lambda v: f"-${v:,.2f}"  if v>0 else "—")
            dt["Net"]   = _nr.apply(lambda v: f"+${v:,.2f}" if v>0 else f"-${abs(v):,.2f}")
            sdt = (
                dt.style
                .apply(lambda col: [
                    (f"color:{GOLD};font-weight:700" if _nr.iloc[i]>0
                     else f"color:{RED};font-weight:700")
                    for i in range(len(col))
                ], subset=["Net"], axis=0)
                .apply(lambda col: [
                    (f"color:{GREEN};font-weight:600" if _dr.iloc[i]=="Long"
                     else f"color:{RED};font-weight:600")
                    for i in range(len(col))
                ], subset=["Dir"], axis=0)
                .set_properties(**{"font-family":"JetBrains Mono,monospace",
                                   "font-size":"0.76rem"})
            )
            st.dataframe(sdt, use_container_width=True, hide_index=True,
                         height=min(40*len(dt)+45, 360))
