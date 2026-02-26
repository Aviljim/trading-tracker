"""
TradeLore Capital — Luxury Trading Journal v3
==============================================
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
from datetime import date, datetime, timedelta

try:
    from streamlit_option_menu import option_menu
    _HAS_MENU = True
except ImportError:
    _HAS_MENU = False

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeLore Capital",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
# — App structural colours (gold / obsidian)
OBS      = "#0E1117"        # obsidian base
CARD     = "#161B22"        # card background
CARD2    = "#1C2330"        # elevated card
BORDER   = "#21262D"        # default border
BORDER_G = "#C5A350"        # gold border highlight
GOLD     = "#C5A350"        # brushed gold — headers, borders, logo
GOLD_LT  = "#D4B86A"        # lighter gold — hover
GOLD_DIM = "rgba(197,163,80,0.12)"
TEXT     = "#E6EDF3"        # primary text
TEXT2    = "#8B949E"        # secondary text
TEXT3    = "#484F58"        # muted text

# — Financial data colours (classic Green / Red)
GREEN    = "#22C55E"        # profit  — equity line, positive bars, wins
RED      = "#F43F5E"        # loss    — drawdown line, negative bars, losses
GREEN_D  = "rgba(34,197,94,0.10)"
RED_D    = "rgba(244,63,94,0.10)"
AMBER    = "#F59E0B"        # tilt meter mid-warning
ORANGE   = "#FB923C"        # tilt meter high-warning

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Playfair+Display:wght@400;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── CSS variables ────────────────────────────────────────────────────────── */
:root {{
    --obs:    {OBS};
    --card:   {CARD};
    --card2:  {CARD2};
    --bdr:    {BORDER};
    --bdr-g:  {GOLD};
    --gold:   {GOLD};
    --goldl:  {GOLD_LT};
    --text:   {TEXT};
    --text2:  {TEXT2};
    --text3:  {TEXT3};
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
    background: #0A0D12 !important;
    border-right: 1px solid rgba(197,163,80,0.20) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebar"] input {{
    background: #12171E !important;
    border: 1px solid #2A3040 !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}}
[data-testid="stFileUploader"] {{
    background: #12171E !important;
    border: 1px dashed rgba(197,163,80,0.30) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: {TEXT3} !important;
}}

/* ── Hide chrome ─────────────────────────────────────────────────────────── */
header[data-testid="stHeader"], #MainMenu, footer {{ display: none !important; }}
.block-container {{ padding: 1.5rem 2.2rem 3rem !important; max-width: 100% !important; }}
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 0.8rem 0 !important; }}

/* ── Metric cards ────────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {{
    background: var(--card) !important;
    border: 1px solid var(--bdr) !important;
    border-top: 2px solid var(--gold) !important;
    border-radius: 10px !important;
    padding: 0.95rem 1.2rem 0.85rem !important;
    transition: border-color 0.2s, background 0.2s;
}}
div[data-testid="metric-container"]:hover {{
    background: var(--card2) !important;
    border-color: var(--bdr-g) !important;
}}
div[data-testid="metric-container"] label {{
    font-family: 'Cinzel', serif !important;
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: {GOLD} !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.01em !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
}}

/* ── Dataframe ───────────────────────────────────────────────────────────── */
.stDataFrame {{
    border: 1px solid var(--bdr) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Section headers ─────────────────────────────────────────────────────── */
.lx-hdr {{
    font-family: 'Cinzel', serif;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: {GOLD};
    margin: 1.8rem 0 0.9rem;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.lx-hdr::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(197,163,80,0.4), transparent);
}}

/* ── Page wordmark ───────────────────────────────────────────────────────── */
.wm {{
    font-family: 'Cinzel', serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--text);
    line-height: 1;
}}
.wm span {{ color: {GOLD}; }}
.wm-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 0.62rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: {TEXT3};
    margin-top: 4px;
}}

/* ── Page title ──────────────────────────────────────────────────────────── */
.pg-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.01em;
    line-height: 1.15;
}}
.pg-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: {TEXT2};
    margin-top: 3px;
}}

/* ── Badge ───────────────────────────────────────────────────────────────── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 11px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
}}
.live {{ background: {GREEN_D}; color: {GREEN}; border: 1px solid rgba(34,197,94,0.30); }}
.demo {{ background: {GOLD_DIM}; color: {GOLD};  border: 1px solid rgba(197,163,80,0.30); }}

/* ── Stat pills ──────────────────────────────────────────────────────────── */
.pill {{
    background: var(--card);
    border: 1px solid var(--bdr);
    border-top: 1px solid rgba(197,163,80,0.25);
    border-radius: 9px;
    padding: 0.65rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {TEXT2};
    text-align: center;
    line-height: 1.9;
}}
.pill strong {{
    display: block;
    color: var(--text);
    font-size: 0.9rem;
    font-family: 'Playfair Display', serif;
    font-weight: 700;
}}

/* ── Tilt meter ──────────────────────────────────────────────────────────── */
.tilt-card {{
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    text-align: center;
    border: 1px solid;
    font-family: 'Inter', sans-serif;
}}
.tilt-lbl {{
    font-family: 'Cinzel', serif;
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 4px;
}}
.tilt-num {{
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
}}
.tilt-sub {{
    font-size: 0.68rem;
    margin-top: 3px;
    font-family: 'JetBrains Mono', monospace;
}}

/* ── Drawdown bar ────────────────────────────────────────────────────────── */
.dd-bar {{
    border-radius: 8px;
    padding: 0.55rem 0.95rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.77rem;
    margin-bottom: 0.5rem;
    border: 1px solid;
}}

/* ── Projection card ─────────────────────────────────────────────────────── */
.proj-card {{
    background: var(--card);
    border: 1px solid var(--bdr);
    border-left: 3px solid {GOLD};
    border-radius: 9px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
}}

/* ── Journal card ────────────────────────────────────────────────────────── */
.jnl-card {{
    background: var(--card);
    border: 1px solid var(--bdr);
    border-left: 3px solid {GOLD};
    border-radius: 9px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}}

/* ── Upload hint ─────────────────────────────────────────────────────────── */
.up-hint {{
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    color: {TEXT3};
    text-align: center;
    margin-top: 5px;
    line-height: 1.65;
}}

/* ── Withdrawal bar ──────────────────────────────────────────────────────── */
.wd-bar {{
    background: {GOLD_DIM};
    border: 1px solid rgba(197,163,80,0.22);
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: {GOLD};
    margin-bottom: 0.6rem;
}}

/* ── Sliders ─────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div {{
    background: {GOLD} !important;
}}

/* ── Text area ───────────────────────────────────────────────────────────── */
textarea {{
    background: #12171E !important;
    color: var(--text) !important;
    border: 1px solid #2A3040 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
}}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: var(--obs); }}
::-webkit-scrollbar-thumb {{ background: rgba(197,163,80,0.25); border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY BASE THEME
#  RULE: PLOT dict NEVER contains xaxis / yaxis / margin — always pass those
#  explicitly to update_layout() to avoid "multiple values for keyword" errors.
# ─────────────────────────────────────────────────────────────────────────────
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TEXT2, size=12),
    hoverlabel=dict(
        bgcolor=CARD2,
        bordercolor=BORDER,
        font=dict(family="JetBrains Mono, monospace", size=12, color=TEXT),
    ),
)

def _ax(prefix="", fmt=",", zeroline=False, zc="rgba(255,255,255,0.07)"):
    """Standard dark-mode axis dict — safe to pass as xaxis= or yaxis=."""
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

_M  = dict(l=8,  r=8,  t=28, b=8)
_ML = dict(l=8,  r=8,  t=50, b=8)
_MH = dict(l=40, r=40, t=20, b=8)


# ─────────────────────────────────────────────────────────────────────────────
#  PURE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_pnl(raw) -> float:
    """Strict broker PnL parser — handles $ , ( ) negative notation."""
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


def is_cashflow(row) -> bool:
    """True for withdrawals, transfers, deposits — exclude from PnL math."""
    sym = str(row.get("symbol", "")).upper().strip()
    keywords = ("WITHDRAWAL", "TRANSFER", "DEPOSIT", "CASH", "WIRE")
    if any(k in sym for k in keywords):
        return True
    try:
        if float(str(row.get("qty", 1))) == 0:
            return True
    except (ValueError, TypeError):
        pass
    return False


def trailing_dd_line(cum_pnl: pd.Series, buf: float) -> pd.Series:
    """
    Trailing drawdown floor:
      floor_i = min(0, HWM_i - buf)
    Starts at -buf, trails up with new highs, permanently locks at 0.
    """
    hwm = cum_pnl.cummax()
    return (hwm - buf).clip(upper=0.0)


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


def max_drawdown(cum: pd.Series) -> float:
    """Largest peak-to-trough drop (positive value)."""
    return float(abs((cum - cum.cummax()).min()))


def dist_from_peak(cum: pd.Series) -> float:
    """Gap between all-time high and current value."""
    return max(0.0, float(cum.max()) - float(cum.iloc[-1]))


def fmt_usd(v: float, sign=False) -> str:
    p = "+" if (sign and v > 0) else ""
    if abs(v) >= 1_000_000:
        return f"{p}${v/1e6:.2f}M"
    return f"{p}${v:,.2f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


def smooth_ts(ts: pd.Series) -> pd.Series:
    """Ensure strictly monotone timestamps by adding ms offsets to dupes."""
    out = ts.copy()
    seen: dict = {}
    for i, t in ts.items():
        k = str(t)
        n = seen.get(k, 0)
        if n:
            out.at[i] = t + pd.Timedelta(milliseconds=n * 150)
        seen[k] = n + 1
    return out


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO DATA
# ─────────────────────────────────────────────────────────────────────────────

def _demo() -> pd.DataFrame:
    rng  = np.random.default_rng(11)
    syms = ["NQ","MNQ","MNQ","NQ","ES","MNQ","NQ","NQ"]
    wts  = [0.22,0.28,0.10,0.15,0.05,0.09,0.07,0.04]
    base = pd.Timestamp("2025-10-06 09:35:00")
    rows = []
    for i in range(90):
        sym   = rng.choice(syms, p=wts)
        qty   = int(rng.choice([1, 2, 3, 5]))
        win   = rng.random() < 0.565
        pnl   = round(float(abs(rng.normal(290, 210))) if win
                      else -float(abs(rng.normal(165, 115))), 2)
        bp    = round(float(rng.uniform(18_000, 22_000)), 2)
        sp    = round(bp + pnl / qty, 2)
        bought = base + pd.Timedelta(
            days=int(i // 5),
            hours=int(rng.integers(0, 7)),
            minutes=int(rng.integers(0, 55)),
        )
        mins  = int(rng.integers(1, 90))
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
    # Withdrawal row
    rows.append(dict(
        symbol="Withdrawal", _priceFormat="", _priceFormatType="", _tickSize=0,
        buyFillId="", sellFillId="", qty=0, buyPrice=0, sellPrice=0,
        pnl="$(1500.00)",
        boughtTimestamp="2025-11-10T12:00:00",
        soldTimestamp="2025-11-10T12:00:00",
        duration="0m",
    ))
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA PROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def calc_fee(symbol: str, qty, nq_fee: float, mnq_fee: float) -> float:
    """
    Tradovate / Take Profit Trader published round-trip commission per contract.

    MNQ MUST be checked before NQ — 'NQ' is a substring of 'MNQ'.
      MNQ: $0.57/side × 2 sides = $1.14 round-trip  (default)
      NQ:  $2.07/side × 2 sides = $4.14 round-trip  (default)
      Anything else (ES, MES, CL…): $0.00
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


def process(raw: pd.DataFrame, starting: float, dd_buf: float,
            profit_target: float,
            nq_fee: float = 4.14, mnq_fee: float = 1.14) -> dict:
    """
    Full pipeline:
      1. Split out cash-flow rows (withdrawals / transfers).
      2. Parse gross PnL from the broker string.
      3. Deduct Tradovate round-trip commissions → net_pnl.
      4. Cumulate net_pnl from $0 for the equity curve.
      5. Current Equity = starting + cum_net  (auto-calculated, no user guess).

    Returns dict: df, cashflows, total_cf, starting.
    """
    df = raw.copy()

    df["soldTimestamp"]   = pd.to_datetime(df["soldTimestamp"],   errors="coerce")
    df["boughtTimestamp"] = pd.to_datetime(df["boughtTimestamp"], errors="coerce")

    # ── Split withdrawals / transfers out before any PnL math ────────────────
    cf_mask  = df.apply(is_cashflow, axis=1)
    cf_df    = df[cf_mask].copy()
    df       = df[~cf_mask].copy()
    total_cf = float(cf_df["pnl"].apply(parse_pnl).abs().sum()) if len(cf_df) else 0.0

    df = (df.dropna(subset=["soldTimestamp"])
            .sort_values("soldTimestamp")
            .reset_index(drop=True))

    # ── Gross PnL from broker string ──────────────────────────────────────────
    df["gross_pnl"] = df["pnl"].apply(parse_pnl)

    # ── Tradovate round-trip commissions (MNQ checked before NQ) ─────────────
    df["fees"] = df.apply(
        lambda r: calc_fee(r["symbol"], r.get("qty", 1), nq_fee, mnq_fee),
        axis=1,
    )

    # ── Net PnL = Gross − Fees ────────────────────────────────────────────────
    df["net_pnl"] = df["gross_pnl"] - df["fees"]

    # ── Cumulative net PnL from $0 (equity curve baseline) ───────────────────
    df["cum_pnl"] = df["net_pnl"].cumsum()

    # ── Trailing drawdown floor ───────────────────────────────────────────────
    df["dd_limit"] = trailing_dd_line(df["cum_pnl"], buf=dd_buf)

    # ── Direction ─────────────────────────────────────────────────────────────
    df["direction"] = np.where(
        df["boughtTimestamp"] < df["soldTimestamp"], "Long", "Short"
    )

    # ── Time-based grouping fields ────────────────────────────────────────────
    df["hour"]        = df["soldTimestamp"].dt.hour
    df["trade_date"]  = df["soldTimestamp"].dt.date
    df["day_of_week"] = df["soldTimestamp"].dt.day_name()
    df["month_label"] = df["soldTimestamp"].dt.strftime("%b '%y")
    df["trade_num"]   = range(1, len(df) + 1)

    # ── Monotone timestamps for smooth Plotly rendering ───────────────────────
    df["ts_plot"] = smooth_ts(df["soldTimestamp"])

    return {
        "df":        df,
        "cashflows": cf_df,
        "total_cf":  total_cf,
        "starting":  starting,
    }


@st.cache_data(show_spinner=False)
def load_csv(data: bytes, starting: float, dd_buf: float,
             profit_target: float,
             nq_fee: float = 4.14, mnq_fee: float = 1.14) -> dict:
    raw = pd.read_csv(io.BytesIO(data))
    return process(raw, starting=starting, dd_buf=dd_buf,
                   profit_target=profit_target,
                   nq_fee=nq_fee, mnq_fee=mnq_fee)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Wordmark
    st.markdown("""
    <div style="padding:0.5rem 0 1.1rem">
      <div class="wm">Trade<span>Lore</span></div>
      <div class="wm-sub">Capital · Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    if _HAS_MENU:
        active_tab = option_menu(
            menu_title=None,
            options=["Dashboard", "Calendar", "Projections", "Journal"],
            icons=["graph-up-arrow", "calendar3", "rocket-takeoff", "journal-bookmark"],
            default_index=0,
            styles={
                "container":         {"padding": "4px 0", "background": "transparent"},
                "icon":              {"color": GOLD, "font-size": "13px"},
                "nav-link":          {
                    "font-family": "Inter,sans-serif",
                    "font-size": "0.81rem",
                    "color": TEXT2,
                    "border-radius": "7px",
                    "--hover-color": CARD2,
                },
                "nav-link-selected": {
                    "background": GOLD_DIM,
                    "color": GOLD,
                    "font-weight": "600",
                },
            },
        )
    else:
        active_tab = st.radio(
            "Navigation",
            ["Dashboard", "Calendar", "Projections", "Journal"],
            label_visibility="collapsed",
        )

    st.markdown("---")

    # ── Account anchor ────────────────────────────────────────────────────────
    _sec = (f'<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.14em;'
            f'text-transform:uppercase;color:{TEXT3};margin-bottom:0.5rem;">')

    st.markdown(_sec + "Account Setup</div>", unsafe_allow_html=True)

    starting_balance = st.number_input(
        "Starting Balance ($)",
        min_value=0.0,
        value=50_000.0,
        step=100.0,
        format="%.2f",
        help="Your account balance before the first trade in this CSV. "
             "Current Equity is calculated automatically: "
             "Starting Balance + Cumulative Net P&L (after commissions).",
    )

    dd_buffer = st.number_input(
        "Trailing Drawdown Buffer ($)",
        min_value=100.0,
        value=2_000.0,
        step=100.0,
        format="%.0f",
        help="Your funded-account trailing stop size.",
    )

    profit_target = st.number_input(
        "Profit Target ($)",
        min_value=0.0,
        value=3_000.0,
        step=100.0,
        format="%.0f",
        help="Gold dashed line shown on equity curve.",
    )

    st.markdown("---")

    # ── Tradovate commission rates ────────────────────────────────────────────
    st.markdown(_sec + "Tradovate Commissions</div>", unsafe_allow_html=True)
    st.markdown(
        '''<div style="font-family:'Inter',sans-serif;font-size:0.67rem;
        color:#484F58;line-height:1.7;margin-bottom:0.55rem;">
        Pre-filled with Take Profit Trader published rates.<br>
        <span style="color:#C5A350;">MNQ:</span>
        $0.57/side &times; 2 =
        <strong style="color:#C5A350;">$1.14/contract</strong><br>
        <span style="color:#C5A350;">NQ:</span>
        $2.07/side &times; 2 =
        <strong style="color:#C5A350;">$4.14/contract</strong><br>
        <em style="color:#484F58;">Edit only if your plan differs.</em>
        </div>''',
        unsafe_allow_html=True,
    )
    nq_fee = st.number_input(
        "NQ Round-Trip Fee ($/contract)",
        min_value=0.0, value=4.14, step=0.01, format="%.2f",
    )
    mnq_fee = st.number_input(
        "MNQ Round-Trip Fee ($/contract)",
        min_value=0.0, value=1.14, step=0.01, format="%.2f",
    )

    st.markdown("---")

    # ── File upload ───────────────────────────────────────────────────────────
    st.markdown(_sec + "Import Trades</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
    st.markdown(
        '<div class="up-hint">'
        'symbol · pnl · qty · buyPrice · sellPrice<br>'
        'boughtTimestamp · soldTimestamp · duration'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    use_demo = st.checkbox("Load demo data", value=(uploaded is None))


# ─────────────────────────────────────────────────────────────────────────────
#  RESOLVE DATA
# ─────────────────────────────────────────────────────────────────────────────
_proc_args = (starting_balance, dd_buffer, profit_target, nq_fee, mnq_fee)

if uploaded is not None:
    result      = load_csv(uploaded.read(), *_proc_args)
    data_source = "live"
elif use_demo:
    result      = process(_demo(), *_proc_args)
    data_source = "demo"
else:
    result      = None
    data_source = "none"


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
_tab_meta = {
    "Dashboard":   ("Performance Dashboard",
                    "Broker-anchored equity · analytics · risk metrics"),
    "Calendar":    ("Trading Calendar",
                    "Monthly P&L heatmap by day"),
    "Projections": ("Long Game Projections",
                    "Growth modelling based on your daily target"),
    "Journal":     ("Trade Journal",
                    "Daily reflection & notes"),
}
ttl, sub = _tab_meta.get(active_tab, ("Dashboard", ""))

h1, h2 = st.columns([5, 1])
with h1:
    st.markdown(
        f'<div class="pg-title">{ttl}</div>'
        f'<div class="pg-sub">{sub}</div>',
        unsafe_allow_html=True,
    )
with h2:
    cls = "live" if data_source == "live" else "demo"
    lbl = "● LIVE" if data_source == "live" else "◆ DEMO"
    st.markdown(
        f'<div style="text-align:right;margin-top:0.9rem;">'
        f'<span class="badge {cls}">{lbl}</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
if result is None:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:52vh;text-align:center;">
      <div style="font-size:2.8rem;margin-bottom:1rem;opacity:0.25;">⬡</div>
      <div style="font-family:'Playfair Display',serif;font-size:1.35rem;font-weight:700;
                  color:{TEXT};margin-bottom:0.4rem;">No data loaded</div>
      <div style="font-family:'Inter',sans-serif;font-size:0.86rem;color:{TEXT3};
                  max-width:340px;line-height:1.7;">
        Upload a Tradovate CSV export or enable
        <strong style="color:{GOLD};">demo data</strong> from the sidebar.
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df            = result["df"]
total_cf      = result["total_cf"]
starting_used = result["starting"]

if len(df) == 0:
    st.warning("No valid trade rows found in this file.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED METRICS
# ─────────────────────────────────────────────────────────────────────────────
n_trades    = len(df)
total_fees  = float(df["fees"].sum())

# Net PnL-based classification matches broker reality (wins = trades where net > 0)
wins        = df[df["net_pnl"] > 0]
losses      = df[df["net_pnl"] < 0]

total_net   = float(df["net_pnl"].sum())   # after commissions
total_gross = float(df["gross_pnl"].sum()) # before commissions

# Gross Profit / Gross Loss from raw gross pnl (matches Tradovate statement format)
gross_wins  = float(wins["gross_pnl"].sum())   if len(wins)   else 0.0
gross_loss  = float(losses["gross_pnl"].sum()) if len(losses) else 0.0

profit_fac  = (gross_wins / abs(gross_loss))  if gross_loss  else float("inf")
win_rate    = len(wins) / n_trades * 100 if n_trades else 0.0
avg_win     = float(wins["net_pnl"].mean())    if len(wins)   else 0.0
avg_loss    = float(losses["net_pnl"].mean())  if len(losses) else 0.0
rr          = (avg_win / abs(avg_loss))         if avg_loss    else float("inf")
_mdd        = max_drawdown(df["cum_pnl"])
_dfp        = dist_from_peak(df["cum_pnl"])
win_st, loss_st = streak_calc(df["net_pnl"])
expectancy  = total_net / n_trades if n_trades else 0.0

# ← THE CORRECT FORMULA: Starting Balance + Cumulative Net PnL after commissions
curr_equity = starting_used + total_net

# Tilt meter — trades taken today
_today = date.today()
trades_today = int((df["trade_date"] == _today).sum())

# Risk of ruin — consecutive net-loss trades before drawdown breached
ror_count = (dd_buffer / abs(avg_loss)) if avg_loss else float("inf")

# Current drawdown status from curve
cur_pnl  = float(df["cum_pnl"].iloc[-1])
cur_dd   = float(df["dd_limit"].iloc[-1])
headroom = cur_pnl - cur_dd


# ══════════════════════════════════════════════════════════════════════════════
#  TAB ▶  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if active_tab == "Dashboard":

    # Cash-flow notice
    if total_cf > 0:
        st.markdown(
            f'<div class="wd-bar">⬡ &nbsp;<strong>${total_cf:,.2f}</strong> '
            f'in withdrawals/transfers detected and excluded from P&L calculations.</div>',
            unsafe_allow_html=True,
        )

    # ── KPI ROW 1 ─────────────────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">Account Overview</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    # Current Equity = Starting Balance + Cumulative Net PnL (auto-calculated)
    k1.metric(
        "Current Equity",
        f"${curr_equity:,.2f}",
        f"Net {fmt_usd(total_net, sign=True)} after ${total_fees:,.2f} fees",
    )
    k2.metric(
        "Gross Profit",
        f"${gross_wins:,.2f}",
        f"{len(wins)} winning trades",
        delta_color="off",
    )
    k3.metric(
        "Gross Loss",
        f"${gross_loss:,.2f}",
        f"{len(losses)} losing trades",
        delta_color="off",
    )
    pf_s = f"{profit_fac:.2f}×" if profit_fac != float("inf") else "∞"
    pf_note = "strong edge" if profit_fac > 1.5 else ("neutral" if profit_fac > 0.9 else "review")
    k4.metric("Profit Factor", pf_s, pf_note, delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI ROW 2 ─────────────────────────────────────────────────────────────
    k5, k6, k7, k8 = st.columns(4)
    k5.metric(
        "Total Net P&L",
        fmt_usd(total_net, sign=True),
        f"{n_trades} trades",
        delta_color="off",
    )
    k6.metric("Win Rate", fmt_pct(win_rate), f"R/R {rr:.2f}×", delta_color="off")
    k7.metric(
        "Max All-Time Drawdown",
        fmt_usd(-_mdd),
        f"−{_mdd/curr_equity*100:.1f}% of equity" if curr_equity else "—",
        delta_color="inverse",
    )
    k8.metric(
        "Distance from Peak",
        fmt_usd(-_dfp) if _dfp > 0 else "+$0.00",
        "current pullback from ATH",
        delta_color="inverse" if _dfp > 0 else "off",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI ROW 3 — Streaks, Tilt Meter, Risk of Ruin ─────────────────────────
    k9, k10, k11, k12 = st.columns(4)
    k9.metric("Win Streak",  f"{win_st}",  "best consecutive",  delta_color="off")
    k10.metric("Loss Streak", f"{loss_st}", "worst consecutive", delta_color="off")

    # Tilt Meter
    if trades_today < 6:
        tilt_c = GOLD; tilt_bg = GOLD_DIM; tilt_lbl = "In the Zone"
    elif trades_today <= 10:
        tilt_c = ORANGE; tilt_bg = "rgba(251,146,60,0.10)"; tilt_lbl = "Caution"
    else:
        tilt_c = RED; tilt_bg = RED_D; tilt_lbl = "TILT RISK"

    with k11:
        st.markdown(
            f'<div class="tilt-card" style="background:{tilt_bg};border-color:{tilt_c};">'
            f'<div class="tilt-lbl" style="color:{tilt_c};">Trades Today</div>'
            f'<div class="tilt-num" style="color:{tilt_c};">{trades_today}</div>'
            f'<div class="tilt-sub" style="color:{tilt_c};">{tilt_lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Risk of Ruin
    with k12:
        if ror_count == float("inf"):
            ror_str = "∞"
            ror_note = "no losing trades yet"
        else:
            ror_str = f"{ror_count:.1f}"
            ror_note = "consecutive losses to breach"
        st.metric("Risk of Ruin", ror_str, ror_note, delta_color="off")

    # ── EQUITY CURVE ─────────────────────────────────────────────────────────
    st.markdown(
        '<div class="lx-hdr">Equity Curve — Cumulative P&L from $0</div>',
        unsafe_allow_html=True,
    )

    # Prepend a true $0 origin point just before first trade
    origin = pd.DataFrame({
        "ts_plot":   [df["ts_plot"].iloc[0] - pd.Timedelta(minutes=5)],
        "cum_pnl":   [0.0],
        "dd_limit":  [-float(dd_buffer)],
        "trade_num": [0],
        "net_pnl":   [0.0],
        "fees":      [0.0],
    })
    eq = pd.concat(
        [origin, df[["ts_plot", "cum_pnl", "dd_limit", "trade_num", "net_pnl", "fees"]]],
        ignore_index=True,
    )

    fig_eq = go.Figure()

    # ① Green equity line + fill (financial colour rule)
    fig_eq.add_trace(go.Scatter(
        x=eq["ts_plot"],
        y=eq["cum_pnl"],
        mode="lines",
        line=dict(color=GREEN, width=2.4, shape="spline", smoothing=0.9),
        fill="tozeroy",
        fillcolor=GREEN_D,
        name="Cum. P&L",
        hovertemplate=(
            "<b>Trade #%{customdata[0]}</b><br>"
            "%{x|%b %d  %H:%M}<br>"
            "Cum. Net P&L: <b>$%{y:,.2f}</b><br>"
            "Trade net: $%{customdata[1]:,.2f}  |  Fees: $%{customdata[2]:,.2f}"
            "<extra></extra>"
        ),
        customdata=np.column_stack([
            eq["trade_num"].to_numpy(),
            eq["net_pnl"].to_numpy(),
            eq["fees"].to_numpy(),
        ]),
    ))

    # ② Red dashed trailing drawdown (financial colour rule)
    fig_eq.add_trace(go.Scatter(
        x=eq["ts_plot"],
        y=eq["dd_limit"],
        mode="lines",
        line=dict(color=RED, width=1.6, dash="dash"),
        name=f"DD Limit (−${dd_buffer:,.0f})",
        hovertemplate=(
            "%{x|%b %d  %H:%M}<br>"
            "DD Floor: <b>$%{y:,.2f}</b><extra></extra>"
        ),
    ))

    # ③ Gold dashed profit target (app-element colour)
    fig_eq.add_trace(go.Scatter(
        x=[eq["ts_plot"].iloc[0], eq["ts_plot"].iloc[-1]],
        y=[float(profit_target)] * 2,
        mode="lines",
        line=dict(color=GOLD, width=1.4, dash="dot"),
        name=f"Target (${profit_target:,.0f})",
        hovertemplate=f"Profit Target: <b>${profit_target:,.0f}</b><extra></extra>",
    ))

    # $0 baseline
    fig_eq.add_hline(
        y=0,
        line=dict(color="rgba(255,255,255,0.10)", width=1, dash="dot"),
        annotation_text="  $0",
        annotation_font=dict(color=TEXT3, size=10, family="JetBrains Mono, monospace"),
    )

    # ATH peak marker
    pk_i = int(eq["cum_pnl"].idxmax())
    pk_v = float(eq.loc[pk_i, "cum_pnl"])
    if pk_v > 0:
        fig_eq.add_trace(go.Scatter(
            x=[eq.loc[pk_i, "ts_plot"]],
            y=[pk_v],
            mode="markers+text",
            marker=dict(color=GREEN, size=9, line=dict(color=OBS, width=2)),
            text=[f"  +${pk_v:,.0f}"],
            textposition="top right",
            textfont=dict(size=10, color=GREEN, family="JetBrains Mono, monospace"),
            name="ATH Peak",
            showlegend=False,
            hovertemplate="ATH: +$%{y:,.2f}<extra></extra>",
        ))

    fig_eq.update_layout(
        **PLOT,
        margin=_ML,
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, family="Inter, sans-serif", color=TEXT2),
        ),
        xaxis=_ax(),
        yaxis=_ax(prefix="$", fmt=",", zeroline=True, zc="rgba(255,255,255,0.08)"),
    )
    st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})

    # Drawdown status banner
    locked = cur_dd >= 0
    if locked:
        dd_c = GREEN; dd_msg = "🔒 Locked at $0 — buffer fully secured"
    elif headroom > dd_buffer * 0.5:
        dd_c = GREEN; dd_msg = f"✅  ${headroom:,.2f} headroom remaining"
    elif headroom > dd_buffer * 0.2:
        dd_c = AMBER;  dd_msg = f"⚠️  Only ${headroom:,.2f} — approaching limit"
    else:
        dd_c = RED;   dd_msg = f"🚨  DANGER — ${headroom:,.2f} before breach!"

    st.markdown(
        f'<div class="dd-bar" style="background:{RED_D};'
        f'border-color:rgba(244,63,94,0.25);color:{dd_c};">'
        f'<strong>Trailing Drawdown</strong>&nbsp; Floor&nbsp;<strong>${cur_dd:,.2f}</strong>'
        f'&nbsp;|&nbsp; Cum. P&L&nbsp;<strong>${cur_pnl:,.2f}</strong>'
        f'&nbsp;|&nbsp; {dd_msg}</div>',
        unsafe_allow_html=True,
    )

    # ── ANALYTICS ROW ─────────────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">Trade Analytics</div>', unsafe_allow_html=True)
    al, ar = st.columns([3, 2])

    with al:
        st.markdown(
            f'<div style="font-size:0.73rem;font-weight:600;color:{TEXT2};'
            f'margin-bottom:0.4rem;">Net P&L by Day of Week</div>',
            unsafe_allow_html=True,
        )
        DOW = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        dow = (df.groupby("day_of_week")["net_pnl"]
                 .sum()
                 .reindex(DOW, fill_value=0.0)
                 .reset_index())
        dow.columns = ["day","pnl"]
        fig_dow = go.Figure(go.Bar(
            x=dow["day"], y=dow["pnl"],
            marker_color=dow["pnl"].apply(lambda v: GREEN if v >= 0 else RED),
            marker_line_width=0,
            text=dow["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="JetBrains Mono, monospace", color=TEXT2),
            hovertemplate="%{x}<br>P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_dow.update_layout(
            **PLOT, margin=_M, height=265, bargap=0.38,
            xaxis=_ax(),
            yaxis=_ax(prefix="$", fmt=","),
        )
        st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

    with ar:
        st.markdown(
            f'<div style="font-size:0.73rem;font-weight:600;color:{TEXT2};'
            f'margin-bottom:0.4rem;">Win / Loss Split</div>',
            unsafe_allow_html=True,
        )
        fig_pie = go.Figure(go.Pie(
            labels=["Wins","Losses"],
            values=[max(len(wins), 0), max(len(losses), 0)],
            hole=0.62,
            marker=dict(
                colors=[GREEN, RED],
                line=dict(color=[OBS, OBS], width=3),
            ),
            textinfo="percent",
            textfont=dict(family="JetBrains Mono, monospace", size=12),
            hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=(
                f"<b>{win_rate:.0f}%</b><br>"
                f"<span style='font-size:11px;color:{TEXT2}'>Win Rate</span>"
            ),
            x=0.5, y=0.5,
            font=dict(size=22, family="Playfair Display, serif", color=TEXT),
            showarrow=False, align="center",
        )
        fig_pie.update_layout(
            **PLOT, height=265, showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.15,
                xanchor="center", x=0.5,
                font=dict(size=11, family="Inter, sans-serif", color=TEXT2),
            ),
            margin=dict(l=8, r=8, t=8, b=30),
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # ── 100× ANALYSIS ─────────────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">100× Analysis</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    # Performance by Hour
    with c1:
        st.markdown(
            f'<div style="font-size:0.73rem;font-weight:600;color:{TEXT2};'
            f'margin-bottom:0.4rem;">Performance by Hour of Day</div>',
            unsafe_allow_html=True,
        )
        hourly = (df.groupby("hour")["net_pnl"]
                    .sum()
                    .reindex(range(24), fill_value=0.0)
                    .reset_index())
        hourly.columns = ["h","pnl"]
        hourly["lbl"] = hourly["h"].apply(
            lambda h: f"{'12' if h==12 else str(h%12 or 12)}{'am' if h<12 else 'pm'}"
        )
        fig_hr = go.Figure(go.Bar(
            x=hourly["lbl"], y=hourly["pnl"],
            marker_color=hourly["pnl"].apply(lambda v: GREEN if v >= 0 else RED),
            marker_line_width=0,
            text=hourly["pnl"].apply(lambda v: f"${v:,.0f}" if v != 0 else ""),
            textposition="outside",
            textfont=dict(size=9, family="JetBrains Mono, monospace", color=TEXT3),
            hovertemplate="%{x}<br>P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_hr.update_layout(
            **PLOT, margin=_M, height=260, bargap=0.28,
            xaxis=_ax(),
            yaxis=_ax(prefix="$", fmt=","),
        )
        st.plotly_chart(fig_hr, use_container_width=True, config={"displayModeBar": False})

    # Long vs Short
    with c2:
        st.markdown(
            f'<div style="font-size:0.73rem;font-weight:600;color:{TEXT2};'
            f'margin-bottom:0.4rem;">Long vs. Short P&L</div>',
            unsafe_allow_html=True,
        )
        ls = (df.groupby("direction")["net_pnl"]
                .agg(total="sum", count="count", avg="mean")
                .reindex(["Long","Short"], fill_value=0)
                .reset_index())
        fig_ls = go.Figure(go.Bar(
            x=ls["total"],
            y=ls["direction"],
            orientation="h",
            marker_color=ls["total"].apply(lambda v: GREEN if v >= 0 else RED),
            marker_line_width=0,
            text=ls["total"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(
                size=12, family="JetBrains Mono, monospace",
                color=[GREEN if v >= 0 else RED for v in ls["total"]],
            ),
            customdata=np.column_stack([ls["count"].to_numpy(), ls["avg"].to_numpy()]),
            hovertemplate=(
                "<b>%{y}</b><br>Total: <b>$%{x:,.2f}</b><br>"
                "Trades: %{customdata[0]}<br>Avg: $%{customdata[1]:,.2f}"
                "<extra></extra>"
            ),
        ))
        fig_ls.update_layout(
            **PLOT, margin=_M, height=260,
            xaxis=_ax(prefix="$", fmt=","),
            yaxis=dict(
                tickfont=dict(size=13, color=TEXT, family="Playfair Display, serif"),
                showgrid=False,
                linecolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig_ls, use_container_width=True, config={"displayModeBar": False})

    # Monthly bar
    monthly = (df.groupby("month_label")["net_pnl"]
                 .sum()
                 .reset_index()
                 .rename(columns={"month_label": "m", "net_pnl": "pnl"}))
    if len(monthly) > 1:
        st.markdown('<div class="lx-hdr">Monthly P&L</div>', unsafe_allow_html=True)
        fig_mo = go.Figure(go.Bar(
            x=monthly["m"], y=monthly["pnl"],
            marker_color=monthly["pnl"].apply(lambda v: GREEN if v >= 0 else RED),
            marker_line_width=0,
            text=monthly["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="JetBrains Mono, monospace", color=TEXT2),
            hovertemplate="%{x}<br>P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_mo.update_layout(
            **PLOT, margin=_M, height=230, bargap=0.3,
            xaxis=_ax(),
            yaxis=_ax(prefix="$", fmt=","),
        )
        st.plotly_chart(fig_mo, use_container_width=True, config={"displayModeBar": False})

    # ── TRADE TABLE ───────────────────────────────────────────────────────────
    st.markdown('<div class="lx-hdr">Trade History</div>', unsafe_allow_html=True)

    tbl = df[[
        "trade_num","soldTimestamp","symbol","direction",
        "qty","buyPrice","sellPrice","gross_pnl","fees","net_pnl","duration",
    ]].copy().rename(columns={
        "trade_num": "#", "soldTimestamp": "Date",
        "symbol": "Symbol", "direction": "Dir",
        "qty": "Qty", "buyPrice": "Entry", "sellPrice": "Exit",
        "gross_pnl": "Gross", "fees": "Fees", "net_pnl": "Net P&L", "duration": "Dur",
    })

    tbl["Date"]  = tbl["Date"].dt.strftime("%b %d %Y  %H:%M")
    tbl["Entry"] = tbl["Entry"].apply(lambda v: f"${v:,.2f}" if pd.notna(v) and v != 0 else "—")
    tbl["Exit"]  = tbl["Exit"].apply(lambda v:  f"${v:,.2f}" if pd.notna(v) and v != 0 else "—")
    tbl["Gross"] = tbl["Gross"].apply(lambda v: f"+${v:,.2f}" if v > 0 else f"-${abs(v):,.2f}")
    tbl["Fees"]  = tbl["Fees"].apply(lambda v: f"-${v:,.2f}" if v > 0 else "—")

    _pnl_num = tbl["Net P&L"].copy()
    _dir_ref = tbl["Dir"].copy()
    tbl["Net P&L"] = _pnl_num.apply(lambda v: f"+${v:,.2f}" if v > 0 else f"-${abs(v):,.2f}")

    tbl      = tbl.iloc[::-1].reset_index(drop=True)
    _pnl_num = _pnl_num.iloc[::-1].reset_index(drop=True)
    _dir_ref = _dir_ref.iloc[::-1].reset_index(drop=True)

    styled = (
        tbl.style
        .apply(lambda col: [
            (f"color:{GREEN};font-weight:700" if _pnl_num.iloc[i] > 0
             else f"color:{RED};font-weight:700")
            for i in range(len(col))
        ], subset=["Net P&L"], axis=0)
        .apply(lambda col: [
            (f"color:{GREEN};font-weight:600" if _dir_ref.iloc[i] == "Long"
             else f"color:{RED};font-weight:600")
            for i in range(len(col))
        ], subset=["Dir"], axis=0)
        .set_properties(**{"font-family": "JetBrains Mono,monospace", "font-size": "0.78rem"})
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background", CARD2), ("color", TEXT3),
                ("font-family", "Cinzel, serif"), ("font-size", "0.6rem"),
                ("letter-spacing", "0.12em"), ("text-transform", "uppercase"),
                ("padding", "10px 12px"),
            ]},
            {"selector": "tbody td", "props": [
                ("background", CARD), ("padding", "8px 12px"),
            ]},
            {"selector": "tbody tr:hover td", "props": [("background", CARD2)]},
        ])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True,
                 height=min(40 * len(tbl) + 45, 500))

    # ── FOOTER PILLS ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2, p3, p4, p5, p6 = st.columns(6)

    def _pill(col, lbl: str, val: str):
        col.markdown(
            f'<div class="pill">{lbl}<br><strong>{val}</strong></div>',
            unsafe_allow_html=True,
        )

    lw = f"${float(wins['net_pnl'].max()):,.2f}"   if len(wins)   else "—"
    ll = f"${float(losses['net_pnl'].min()):,.2f}" if len(losses) else "—"

    _pill(p1, "Gross Profit",  f"${gross_wins:,.2f}")
    _pill(p2, "Total Fees",    f"-${total_fees:,.2f}")
    _pill(p3, "Largest Win",   lw)
    _pill(p4, "Largest Loss",  ll)
    _pill(p5, "Expectancy",    f"${expectancy:,.2f}/trade")
    _pill(p6, "Symbols",       str(df["symbol"].nunique()))


# ══════════════════════════════════════════════════════════════════════════════
#  TAB ▶  CALENDAR  (Plotly heatmap — Green profit, Red loss)
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Calendar":

    st.markdown('<div class="lx-hdr">Select Month</div>', unsafe_allow_html=True)

    all_months = sorted({d.replace(day=1) for d in df["trade_date"].unique()})
    month_opts = [d.strftime("%B %Y") for d in all_months]
    sel_str    = st.selectbox("Month", month_opts,
                               index=len(month_opts) - 1,
                               label_visibility="collapsed")
    sel_month  = pd.to_datetime(sel_str, format="%B %Y").date()
    yr, mo     = sel_month.year, sel_month.month

    daily = (
        df[(df["soldTimestamp"].dt.year == yr) &
           (df["soldTimestamp"].dt.month == mo)]
        .groupby("trade_date")["net_pnl"]
        .sum()
    )

    m_net   = float(daily.sum()) if len(daily) else 0.0
    m_days  = len(daily)
    m_green = int((daily > 0).sum())
    m_red   = int((daily <= 0).sum())

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Month P&L",    fmt_usd(m_net, sign=True))
    s2.metric("Trading Days", str(m_days))
    s3.metric("Green Days",   str(m_green))
    s4.metric("Red Days",     str(m_red))

    st.markdown('<div class="lx-hdr">P&L Heatmap</div>', unsafe_allow_html=True)

    cal_obj    = calendar.Calendar(firstweekday=0)
    weeks      = cal_obj.monthdayscalendar(yr, mo)
    n_weeks    = len(weeks)
    dow_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    z_mat, txt_mat, hov_mat = [], [], []
    for week in weeks:
        zr, tr, hr = [], [], []
        for day_n in week:
            if day_n == 0:
                zr.append(None); tr.append(""); hr.append("")
            else:
                d_obj = date(yr, mo, day_n)
                pnl_v = daily.get(d_obj, None)
                if pnl_v is not None:
                    sign = "+" if pnl_v >= 0 else ""
                    zr.append(float(pnl_v))
                    tr.append(f"<b>{day_n}</b><br>{sign}${pnl_v:,.0f}")
                    hr.append(
                        f"<b>{d_obj.strftime('%b %d')}</b><br>"
                        f"Net P&L: <b>${pnl_v:,.2f}</b>"
                    )
                else:
                    zr.append(0.0)
                    tr.append(f"<b>{day_n}</b>")
                    hr.append(f"<b>{d_obj.strftime('%b %d')}</b><br>No trades")
        z_mat.append(zr); txt_mat.append(tr); hov_mat.append(hr)

    max_abs = max(
        abs(daily.max()) if len(daily) and daily.max() > 0 else 1,
        abs(daily.min()) if len(daily) and daily.min() < 0 else 1,
    )

    # Green ↔ Red diverging colorscale (centred at 0 = near-black)
    colorscale = [
        [0.00, "#7B1010"],   # deep crimson — large loss
        [0.35, "#C0392B"],
        [0.48, "#2D1010"],
        [0.50, "#161B22"],   # neutral — no trades
        [0.52, "#0E2A1A"],
        [0.65, "#196E38"],
        [1.00, "#22C55E"],   # vibrant green — large profit
    ]

    fig_cal = go.Figure(go.Heatmap(
        z=z_mat,
        text=txt_mat,
        customdata=hov_mat,
        x=dow_labels,
        y=[f"Wk {i+1}" for i in range(n_weeks)],
        colorscale=colorscale,
        zmid=0,
        zmin=-max_abs,
        zmax=max_abs,
        showscale=True,
        colorbar=dict(
            title=dict(
                text="P&L",
                font=dict(family="Cinzel, serif", color=GOLD, size=10),
            ),
            tickfont=dict(family="JetBrains Mono, monospace", color=TEXT3, size=10),
            tickprefix="$",
            thickness=12,
            len=0.85,
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
        height=max(290, n_weeks * 85),
        margin=_MH,
        xaxis=dict(
            side="top",
            tickfont=dict(size=11, color=TEXT2, family="Cinzel, serif"),
            showgrid=False,
            linecolor="rgba(0,0,0,0)",
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=10, color=TEXT3, family="JetBrains Mono, monospace"),
            showgrid=False,
            linecolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig_cal, use_container_width=True, config={"displayModeBar": False})

    if len(daily) > 0:
        st.markdown('<div class="lx-hdr">Daily Breakdown</div>', unsafe_allow_html=True)
        dd2 = daily.reset_index()
        dd2.columns = ["date","pnl"]
        dd2["ds"] = dd2["date"].apply(lambda d: d.strftime("%b %d"))
        fig_db = go.Figure(go.Bar(
            x=dd2["ds"], y=dd2["pnl"],
            marker_color=dd2["pnl"].apply(lambda v: GREEN if v >= 0 else RED),
            marker_line_width=0,
            text=dd2["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, family="JetBrains Mono, monospace", color=TEXT2),
            hovertemplate="%{x}<br>P&L: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_db.update_layout(
            **PLOT, margin=_M, height=240, bargap=0.28,
            xaxis=_ax(),
            yaxis=_ax(prefix="$", fmt=","),
        )
        st.plotly_chart(fig_db, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
#  TAB ▶  PROJECTIONS  (The Long Game)
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Projections":

    st.markdown('<div class="lx-hdr">Growth Parameters</div>', unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        daily_target = st.slider(
            "Daily Profit Target ($)",
            min_value=50, max_value=2_000,
            value=240, step=10,
            help="Your realistic daily net target.",
        )
    with pc2:
        trading_days_pm = st.slider(
            "Trading Days per Month",
            min_value=10, max_value=23,
            value=20, step=1,
        )
    with pc3:
        start_eq = st.number_input(
            "Starting Equity ($)",
            min_value=0.0,
            value=float(curr_equity),
            step=500.0,
            format="%.2f",
            help="Defaults to your calculated current equity.",
        )

    # Projection horizons
    horizons = {
        "1 Month":  trading_days_pm * 1,
        "3 Months": trading_days_pm * 3,
        "6 Months": trading_days_pm * 6,
        "1 Year":   trading_days_pm * 12,
    }

    proj_data = []
    for label, days in horizons.items():
        gain    = daily_target * days
        final   = start_eq + gain
        ret_pct = (gain / start_eq * 100) if start_eq else 0
        proj_data.append({
            "label": label, "days": days,
            "gain": gain, "final_equity": final, "return_pct": ret_pct,
        })

    proj_df = pd.DataFrame(proj_data)

    st.markdown('<div class="lx-hdr">Projected Growth</div>', unsafe_allow_html=True)

    # Summary metric cards
    pm1, pm2, pm3, pm4 = st.columns(4)
    cols_m = [pm1, pm2, pm3, pm4]
    for i, row in proj_df.iterrows():
        cols_m[i].metric(
            row["label"],
            f"${row['final_equity']:,.0f}",
            f"+${row['gain']:,.0f}  ({row['return_pct']:.1f}%)",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Projection bar chart — all green (financial colour for profit)
    fig_proj = go.Figure()

    fig_proj.add_trace(go.Bar(
        x=proj_df["label"],
        y=proj_df["final_equity"],
        marker=dict(
            color=[GREEN] * len(proj_df),
            opacity=[0.55, 0.68, 0.82, 1.0],
            line=dict(color=GREEN, width=1),
        ),
        text=proj_df["final_equity"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(size=13, family="Playfair Display, serif", color=GREEN),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Final Equity: <b>$%{y:,.2f}</b><br>"
            "Gain: $%{customdata[0]:,.0f}  (%{customdata[1]:.1f}%)"
            "<extra></extra>"
        ),
        customdata=np.column_stack([
            proj_df["gain"].to_numpy(),
            proj_df["return_pct"].to_numpy(),
        ]),
    ))

    # Starting equity reference line
    fig_proj.add_hline(
        y=start_eq,
        line=dict(color=GOLD, width=1.2, dash="dot"),
        annotation_text=f"  Starting ${start_eq:,.0f}",
        annotation_font=dict(color=GOLD, size=11, family="Cinzel, serif"),
    )

    fig_proj.update_layout(
        **PLOT,
        margin=dict(l=8, r=8, t=50, b=8),
        height=420,
        showlegend=False,
        xaxis=_ax(),
        yaxis=_ax(prefix="$", fmt=","),
        title=dict(
            text=f"Projected Equity at ${daily_target}/day  ·  {trading_days_pm} trading days/month",
            font=dict(family="Cinzel, serif", size=13, color=GOLD),
            x=0.0, xanchor="left",
        ),
    )
    st.plotly_chart(fig_proj, use_container_width=True, config={"displayModeBar": False})

    # Growth curve line chart
    st.markdown('<div class="lx-hdr">Day-by-Day Growth Curve</div>', unsafe_allow_html=True)

    max_days  = trading_days_pm * 12
    day_range = np.arange(0, max_days + 1)
    equity_curve = start_eq + daily_target * day_range

    fig_gc = go.Figure()
    fig_gc.add_trace(go.Scatter(
        x=day_range,
        y=equity_curve,
        mode="lines",
        line=dict(color=GREEN, width=2.5),
        fill="tozeroy",
        fillcolor=GREEN_D,
        name="Projected Equity",
        hovertemplate="Day %{x}<br>Equity: <b>$%{y:,.2f}</b><extra></extra>",
    ))

    # Milestone markers
    for lbl, d in horizons.items():
        eq_v = float(start_eq + daily_target * d)
        fig_gc.add_trace(go.Scatter(
            x=[d], y=[eq_v],
            mode="markers+text",
            marker=dict(color=GOLD, size=10, line=dict(color=OBS, width=2)),
            text=[f"  {lbl}<br>  ${eq_v:,.0f}"],
            textposition="top right",
            textfont=dict(size=10, color=GOLD, family="JetBrains Mono, monospace"),
            showlegend=False,
            hovertemplate=f"{lbl}: <b>${eq_v:,.2f}</b><extra></extra>",
        ))

    fig_gc.update_layout(
        **PLOT,
        margin=_ML,
        height=340,
        showlegend=False,
        xaxis=dict(
            title=dict(text="Trading Days", font=dict(family="Inter", color=TEXT2, size=11)),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=11, color=TEXT3, family="JetBrains Mono, monospace"),
            zeroline=False,
        ),
        yaxis=_ax(prefix="$", fmt=","),
    )
    st.plotly_chart(fig_gc, use_container_width=True, config={"displayModeBar": False})

    # Projection breakdown table
    st.markdown('<div class="lx-hdr">Summary Table</div>', unsafe_allow_html=True)
    tbl_p = proj_df[["label","days","gain","final_equity","return_pct"]].copy()
    tbl_p.columns = ["Horizon","Trading Days","Profit Gained","Final Equity","Return %"]
    tbl_p["Profit Gained"] = tbl_p["Profit Gained"].apply(lambda v: f"+${v:,.2f}")
    tbl_p["Final Equity"]  = tbl_p["Final Equity"].apply(lambda v: f"${v:,.2f}")
    tbl_p["Return %"]      = tbl_p["Return %"].apply(lambda v: f"{v:.1f}%")
    st.dataframe(tbl_p, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div style="font-family:JetBrains Mono,monospace;font-size:0.72rem;'
        f'color:{TEXT3};margin-top:0.8rem;line-height:1.7;">'
        f'⬡ Projections assume a flat <strong style="color:{GOLD}">'
        f'${daily_target}/day</strong> net target and '
        f'<strong style="color:{GOLD}">{trading_days_pm} trading days/month</strong>. '
        f'Past performance does not guarantee future results. '
        f'These figures are for planning purposes only.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB ▶  JOURNAL
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "Journal":

    st.markdown('<div class="lx-hdr">Daily Journal</div>', unsafe_allow_html=True)

    trade_dates = sorted(df["trade_date"].unique(), reverse=True)
    sel_date = st.date_input(
        "Select Date",
        value=trade_dates[0] if trade_dates else date.today(),
        min_value=trade_dates[-1] if trade_dates else date.today() - timedelta(days=365),
        max_value=trade_dates[0]  if trade_dates else date.today(),
    )

    day_df    = df[df["trade_date"] == sel_date].copy()
    day_pnl   = float(day_df["net_pnl"].sum()) if len(day_df) else 0.0
    day_wins  = int((day_df["net_pnl"] > 0).sum())
    day_losses= int((day_df["net_pnl"] < 0).sum())

    pnl_c  = GREEN if day_pnl >= 0 else RED
    pnl_sg = "+" if day_pnl >= 0 else ""

    st.markdown(f"""
    <div class="jnl-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div style="font-family:'Cinzel',serif;font-size:0.58rem;font-weight:700;
                      letter-spacing:0.18em;text-transform:uppercase;color:{GOLD};">
            {sel_date.strftime('%A')}</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                      font-weight:800;color:{TEXT};letter-spacing:-0.01em;margin-top:3px;">
            {sel_date.strftime('%B %d, %Y')}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-family:'Playfair Display',serif;font-size:2rem;
                      font-weight:800;color:{pnl_c};letter-spacing:-0.02em;">
            {pnl_sg}${abs(day_pnl):,.2f}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                      color:{TEXT3};margin-top:1px;">
            {day_wins}W / {day_losses}L &nbsp;·&nbsp; {len(day_df)} trades</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    j1, j2, j3 = st.columns(3)
    j1.metric("Day P&L",   fmt_usd(day_pnl, sign=True))
    j2.metric("Trades",    str(len(day_df)), delta_color="off")
    j3.metric("W / L",     f"{day_wins} / {day_losses}", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)
    jl, jr = st.columns([3, 2])

    with jl:
        st.markdown('<div class="lx-hdr">Notes & Reflection</div>', unsafe_allow_html=True)
        key_ss = f"note_{sel_date}"
        if key_ss not in st.session_state:
            st.session_state[key_ss] = ""
        note = st.text_area(
            "Notes",
            value=st.session_state[key_ss],
            height=200,
            placeholder=(
                "What went well? What would you change?\n"
                "Market conditions, discipline, setups missed..."
            ),
            label_visibility="collapsed",
            key=key_ss + "_ta",
        )
        if st.button("💾  Save Note", type="secondary"):
            st.session_state[key_ss] = note
            st.success("Note saved for this session.")

    with jr:
        st.markdown("<div class='lx-hdr'>Day's Trades</div>", unsafe_allow_html=True)
        if len(day_df) == 0:
            st.markdown(
                f'<div style="font-family:Inter,sans-serif;font-size:0.85rem;'
                f'color:{TEXT3};padding:2rem 0;text-align:center;">No trades on this date.</div>',
                unsafe_allow_html=True,
            )
        else:
            dt = day_df[["trade_num","symbol","direction","qty","gross_pnl","fees","net_pnl","duration"]].copy()
            dt.columns = ["#","Symbol","Dir","Qty","Gross","Fees","Net","Dur"]
            _nr = dt["Net"].copy()
            _dr = dt["Dir"].copy()
            dt["Gross"] = dt["Gross"].apply(lambda v: f"+${v:,.2f}" if v > 0 else f"-${abs(v):,.2f}")
            dt["Fees"] = dt["Fees"].apply(lambda v: f"-${v:,.2f}" if v > 0 else "—")
            dt["Net"] = _nr.apply(lambda v: f"+${v:,.2f}" if v > 0 else f"-${abs(v):,.2f}")
            sdt = (
                dt.style
                .apply(lambda col: [
                    (f"color:{GREEN};font-weight:700" if _nr.iloc[i] > 0
                     else f"color:{RED};font-weight:700")
                    for i in range(len(col))
                ], subset=["Net"], axis=0)
                .apply(lambda col: [
                    (f"color:{GREEN};font-weight:600" if _dr.iloc[i] == "Long"
                     else f"color:{RED};font-weight:600")
                    for i in range(len(col))
                ], subset=["Dir"], axis=0)
                .set_properties(**{
                    "font-family": "JetBrains Mono,monospace",
                    "font-size": "0.76rem",
                })
            )
            st.dataframe(sdt, use_container_width=True, hide_index=True,
                         height=min(40 * len(dt) + 45, 380))
