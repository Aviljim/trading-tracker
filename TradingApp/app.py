import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import io

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeLog — Professional Trading Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg-base:       #09090f;
    --bg-surface:    #111118;
    --bg-card:       #16161f;
    --bg-card-hover: #1c1c28;
    --bg-input:      #1a1a25;
    --border:        #242435;
    --border-accent: #2e2e45;
    --text-primary:  #f0f0fa;
    --text-secondary:#8888aa;
    --text-muted:    #55556a;
    --accent-blue:   #4f8ef7;
    --accent-teal:   #2dd4bf;
    --accent-green:  #22c55e;
    --accent-red:    #f43f5e;
    --accent-amber:  #f59e0b;
    --glow-blue:     rgba(79,142,247,0.15);
    --glow-green:    rgba(34,197,94,0.12);
    --glow-red:      rgba(244,63,94,0.12);
}

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stFileUploader"] {
    background: var(--bg-input) !important;
    border: 1px dashed var(--border-accent) !important;
    border-radius: 10px !important;
}

header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
.block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 100% !important; }

hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.1rem 1.4rem !important;
    transition: border-color 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--border-accent) !important;
}
div[data-testid="metric-container"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
}

.stDataFrame { border: 1px solid var(--border) !important; border-radius: 12px !important; overflow: hidden !important; }
.stDataFrame thead th {
    background: var(--bg-input) !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-accent) !important;
}
.stDataFrame tbody td {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
}

.section-hdr {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-hdr::after { content:''; flex:1; height:1px; background: var(--border); }

.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.page-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}
.badge-green { background: var(--glow-green); color: var(--accent-green); border: 1px solid rgba(34,197,94,0.25); }
.badge-blue  { background: var(--glow-blue);  color: var(--accent-blue);  border: 1px solid rgba(79,142,247,0.25); }

.stat-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-align: center;
    line-height: 1.8;
}
.stat-pill strong { color: var(--text-primary); font-size: 0.9rem; }

.upload-hint {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.76rem;
    color: var(--text-muted);
    text-align: center;
    margin-top: 0.5rem;
    line-height: 1.6;
}

::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius:3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_pnl(value) -> float:
    """
    Broker PnL string → float:
        '$105.00'   →  105.0
        '$(230.00)' → -230.0
        '-105'      → -105.0
        105.0       →  105.0
    """
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    is_negative = "(" in s
    cleaned = re.sub(r"[^0-9\.]", "", s)
    if not cleaned:
        return 0.0
    try:
        num = float(cleaned)
        return -num if is_negative else num
    except ValueError:
        return 0.0


def calc_fees(symbol: str, qty: int) -> float:
    """
    Per-contract fee estimate based on symbol:
      MNQ  → $1.14/contract
      NQ   → $4.14/contract
      other→ $0.00 (extend as needed)
    """
    sym = str(symbol).upper().strip()
    qty = int(qty) if pd.notna(qty) else 1
    if "MNQ" in sym:
        return round(1.14 * qty, 2)
    elif "NQ" in sym:
        return round(4.14 * qty, 2)
    return 0.0


def calc_trailing_drawdown(cum_net_pnl: pd.Series, buffer: float = 2000.0) -> pd.Series:
    """
    Trailing drawdown line for a funded account.

    Rules:
      - Starts at -buffer (e.g. -$2000)
      - Trails up with every new High Water Mark in cum_net_pnl
      - NEVER drops when PnL drops — stays locked at highest point
      - Locks permanently at $0 once the HWM reaches buffer
        Formula: limit_i = min(0,  HWM_i - buffer)
    """
    hwm    = cum_net_pnl.cummax()          # high-water mark at each step
    limit  = (hwm - buffer).clip(upper=0)  # never rises above $0
    return limit


def compute_streaks(pnl_series: pd.Series):
    """Return (max_win_streak, max_loss_streak) from a net PnL series."""
    max_win = max_loss = cur_win = cur_loss = 0
    for v in pnl_series:
        if v > 0:
            cur_win  += 1
            cur_loss  = 0
            max_win   = max(max_win, cur_win)
        elif v < 0:
            cur_loss += 1
            cur_win   = 0
            max_loss  = max(max_loss, cur_loss)
        else:
            cur_win = cur_loss = 0
    return max_win, max_loss


def max_drawdown_from_series(pnl_series: pd.Series) -> float:
    """Max peak-to-trough drawdown (positive number) from a cumulative PnL series."""
    peak = pnl_series.cummax()
    return float(abs((pnl_series - peak).min()))


def fmt_usd(v: float, sign: bool = False) -> str:
    prefix = "+" if (sign and v > 0) else ""
    if abs(v) >= 1_000_000:
        return f"{prefix}${v/1_000_000:.2f}M"
    return f"{prefix}${v:,.2f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


# Shared Plotly dark layout — NO margin key here to avoid duplicate-kwarg errors
_M = dict(l=10, r=10, t=30, b=10)

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#8888aa", size=12),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
               linecolor="rgba(255,255,255,0.06)",
               tickfont=dict(size=11, color="#55556a"), zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
               linecolor="rgba(255,255,255,0.06)",
               tickfont=dict(size=11, color="#55556a"), zeroline=False),
    hoverlabel=dict(bgcolor="#1c1c28", bordercolor="#2e2e45",
                    font=dict(family="DM Mono, monospace", size=12, color="#f0f0fa")),
)


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO DATA  (uses NQ + MNQ so fee calc is exercised)
# ─────────────────────────────────────────────────────────────────────────────

def generate_demo() -> pd.DataFrame:
    rng     = np.random.default_rng(42)
    symbols = ["NQ", "MNQ", "MNQ", "NQ", "ES", "MNQ", "NQ", "MNQ", "ES", "NQ"]
    weights = [0.20, 0.25, 0.10, 0.15, 0.10, 0.08, 0.05, 0.04, 0.02, 0.01]
    n       = 80
    base_ts = pd.Timestamp("2024-11-01 09:35:00")
    rows    = []
    for i in range(n):
        sym    = rng.choice(symbols, p=weights)
        qty    = int(rng.choice([1, 2, 3, 5, 10]))
        win    = rng.random() < 0.56
        pnl    = round(float(abs(rng.normal(350, 280))) if win
                       else -float(abs(rng.normal(210, 150))), 2)
        bp     = round(float(rng.uniform(100, 500)), 2)
        sp     = round(bp + pnl / qty, 2)
        bought = base_ts + pd.Timedelta(
                     days=int(i // 3),
                     hours=int(rng.integers(0, 6)),
                     minutes=int(rng.integers(0, 55)))
        mins   = int(rng.integers(1, 120))
        sold   = bought + pd.Timedelta(minutes=mins)
        pstr   = f"${pnl:.2f}" if pnl >= 0 else f"$({abs(pnl):.2f})"
        rows.append({
            "symbol":           sym,
            "_priceFormat":     "0.00",
            "_priceFormatType": "DECIMAL",
            "_tickSize":        0.25,
            "buyFillId":        f"B{10000+i}",
            "sellFillId":       f"S{10000+i}",
            "qty":              qty,
            "buyPrice":         bp,
            "sellPrice":        sp,
            "pnl":              pstr,
            "boughtTimestamp":  bought.strftime("%Y-%m-%dT%H:%M:%S"),
            "soldTimestamp":    sold.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration":         f"{mins}m",
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA PROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def process(raw: pd.DataFrame, starting: float) -> pd.DataFrame:
    df = raw.copy()

    # Parse gross PnL
    df["gross_pnl"]       = df["pnl"].apply(parse_pnl)

    # Calculate per-trade fees
    df["fees"]            = df.apply(
        lambda r: calc_fees(r["symbol"], r.get("qty", 1)), axis=1)

    # Net PnL = Gross - Fees
    df["net_pnl"]         = df["gross_pnl"] - df["fees"]

    # Timestamps
    df["soldTimestamp"]   = pd.to_datetime(df["soldTimestamp"],   errors="coerce")
    df["boughtTimestamp"] = pd.to_datetime(df["boughtTimestamp"], errors="coerce")
    df = df.dropna(subset=["soldTimestamp"]).sort_values("soldTimestamp").reset_index(drop=True)

    # Cumulative series — both gross and net, both starting from $0
    df["cum_gross_pnl"]   = df["gross_pnl"].cumsum()
    df["cum_net_pnl"]     = df["net_pnl"].cumsum()

    # Equity (absolute balance) — used for drawdown calc based on net
    df["equity"]          = starting + df["cum_net_pnl"]

    # Trailing drawdown limit (relative to $0 PnL baseline)
    df["drawdown_limit"]  = calc_trailing_drawdown(df["cum_net_pnl"], buffer=2000.0)

    # Metadata
    df["day_of_week"]     = df["soldTimestamp"].dt.day_name()
    df["month_label"]     = df["soldTimestamp"].dt.strftime("%b '%y")
    df["trade_num"]       = range(1, len(df) + 1)

    # Keep pnl_clean as alias for net_pnl (used in charts/tables)
    df["pnl_clean"]       = df["net_pnl"]

    return df


@st.cache_data(show_spinner=False)
def load_csv(data: bytes, starting: float) -> pd.DataFrame:
    raw = pd.read_csv(io.BytesIO(data))
    return process(raw, starting)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.4rem 0 1.2rem">
      <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                  color:#f0f0fa;letter-spacing:-0.02em;">TradeLog</div>
      <div style="font-family:'DM Sans',sans-serif;font-size:0.74rem;
                  color:#55556a;margin-top:2px;">Professional Trading Journal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:#55556a;
                margin-bottom:0.6rem;">Account Setup</div>""", unsafe_allow_html=True)

    starting_balance = st.number_input(
        "Starting Account Balance ($)",
        min_value=0.0, value=50_000.0, step=1_000.0, format="%.2f",
        help="Your balance before the first trade in this CSV.",
    )

    drawdown_buffer = st.number_input(
        "Trailing Drawdown Buffer ($)",
        min_value=0.0, value=2_000.0, step=100.0, format="%.0f",
        help="The trailing drawdown limit for your funded account (e.g. $2,000).",
    )

    st.markdown("---")

    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:#55556a;
                margin-bottom:0.6rem;">Import Trades</div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    st.markdown("""<div class="upload-hint">
      Required columns:<br>
      <code style="color:#4f8ef7;font-size:0.7rem;">
        symbol · pnl · qty · buyPrice · sellPrice<br>
        boughtTimestamp · soldTimestamp · duration
      </code>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    use_demo = st.checkbox("Use demo data", value=(uploaded is None))


# ─────────────────────────────────────────────────────────────────────────────
#  RESOLVE DATA SOURCE
# ─────────────────────────────────────────────────────────────────────────────
if uploaded is not None:
    df          = load_csv(uploaded.read(), starting_balance)
    data_source = "live"
elif use_demo:
    df          = process(generate_demo(), starting_balance)
    data_source = "demo"
else:
    df          = None
    data_source = "none"

# Recompute drawdown line if buffer slider changed (not cached)
if df is not None:
    df["drawdown_limit"] = calc_trailing_drawdown(df["cum_net_pnl"], buffer=drawdown_buffer)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
hcol, bcol = st.columns([4, 1])
with hcol:
    st.markdown("""<div class="page-title">Performance Dashboard</div>
    <div class="page-sub">Real-time trade analytics &amp; equity tracking</div>""",
    unsafe_allow_html=True)
with bcol:
    if data_source == "live":
        st.markdown("""<div style="text-align:right;margin-top:0.9rem;">
            <span class="badge badge-green">LIVE DATA</span></div>""",
            unsafe_allow_html=True)
    else:
        st.markdown("""<div style="text-align:right;margin-top:0.9rem;">
            <span class="badge badge-blue">DEMO DATA</span></div>""",
            unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
if df is None or len(df) == 0:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;height:55vh;text-align:center;">
      <div style="font-size:3rem;margin-bottom:1rem;">📂</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;
                  color:#f0f0fa;margin-bottom:0.5rem;">No trades loaded</div>
      <div style="font-family:'DM Sans',sans-serif;font-size:0.9rem;color:#55556a;
                  max-width:380px;line-height:1.6;">
        Upload a CSV or enable <strong style="color:#8888aa;">demo data</strong>
        in the sidebar to get started.
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  COMPUTE METRICS
# ─────────────────────────────────────────────────────────────────────────────
total_trades  = len(df)

# Gross metrics (before fees)
gross_wins    = df[df["gross_pnl"] > 0]
gross_losses  = df[df["gross_pnl"] < 0]
total_gross   = float(df["gross_pnl"].sum())
gross_profit  = float(gross_wins["gross_pnl"].sum())  if len(gross_wins)   else 0.0
gross_loss    = float(gross_losses["gross_pnl"].sum()) if len(gross_losses) else 0.0

# Fee totals
total_fees    = float(df["fees"].sum())

# Net metrics (after fees) — use these for win/loss classification
wins          = df[df["net_pnl"] > 0]
losses        = df[df["net_pnl"] < 0]
total_net     = float(df["net_pnl"].sum())
net_profit    = float(wins["net_pnl"].sum())   if len(wins)   else 0.0
net_loss      = float(losses["net_pnl"].sum()) if len(losses) else 0.0

curr_equity   = starting_balance + total_net
win_rate      = len(wins) / total_trades * 100 if total_trades else 0.0
pf            = (gross_profit / abs(gross_loss)) if gross_loss else float("inf")
avg_win       = float(wins["net_pnl"].mean())   if len(wins)   else 0.0
avg_loss      = float(losses["net_pnl"].mean()) if len(losses) else 0.0
rr            = (avg_win / abs(avg_loss))        if avg_loss    else float("inf")
max_dd        = max_drawdown_from_series(df["cum_net_pnl"])
total_return  = (total_net / starting_balance) * 100

# Streaks (based on net PnL)
win_streak, loss_streak = compute_streaks(df["net_pnl"])


# ─────────────────────────────────────────────────────────────────────────────
#  KPI ROW 1 — Equity, Gross PnL, Fees, Net PnL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Account Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Current Equity (Net)",
    f"${curr_equity:,.2f}",
    f"{fmt_usd(total_net, sign=True)}  ({fmt_pct(total_return)})",
)
c2.metric(
    "Gross P&L",
    fmt_usd(total_gross, sign=True),
    f"before fees · {total_trades} trades",
    delta_color="off",
)
c3.metric(
    "Total Fees",
    f"-${total_fees:,.2f}",
    f"avg ${total_fees/total_trades:.2f}/trade" if total_trades else "—",
    delta_color="inverse",
)
c4.metric(
    "Net P&L",
    fmt_usd(total_net, sign=True),
    f"{len(wins)} wins  /  {len(losses)} losses",
    delta_color="off",
)

st.markdown("<br>", unsafe_allow_html=True)

# KPI ROW 2 — Win Rate, Profit Factor, R/R, Max Drawdown
c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Win Rate",
    fmt_pct(win_rate),
    f"{total_trades} total trades",
    delta_color="off",
)
pf_str  = f"{pf:.2f}×" if pf != float("inf") else "∞"
pf_note = "strong edge" if pf > 1.5 else ("neutral" if pf > 0.9 else "review needed")
c6.metric("Profit Factor", pf_str, pf_note, delta_color="off")

rr_str = f"{rr:.2f}R" if rr != float("inf") else "∞R"
c7.metric("Risk / Reward", rr_str, "avg win ÷ |avg loss|", delta_color="off")

dd_pct = (max_dd / starting_balance * 100)
c8.metric("Max Drawdown", fmt_usd(-max_dd), f"−{dd_pct:.1f}% from peak", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# KPI ROW 3 — Avg Win, Avg Loss, Win Streak, Loss Streak
c9, c10, c11, c12 = st.columns(4)

c9.metric("Avg Win",  fmt_usd(avg_win),  f"{len(wins)} winning trades",   delta_color="off")
c10.metric("Avg Loss", fmt_usd(avg_loss), f"{len(losses)} losing trades",  delta_color="off")
c11.metric(
    "Largest Win Streak",
    f"{win_streak} trades",
    "consecutive wins",
    delta_color="off",
)
c12.metric(
    "Largest Loss Streak",
    f"{loss_streak} trades",
    "consecutive losses",
    delta_color="off",
)


# ─────────────────────────────────────────────────────────────────────────────
#  EQUITY CURVE  (Y-axis = Cumulative Net PnL, starts at $0)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Equity Curve — Cumulative Net P&L</div>',
            unsafe_allow_html=True)

# Prepend a $0 start point
start_pt = pd.DataFrame({
    "soldTimestamp":  [df["soldTimestamp"].iloc[0] - pd.Timedelta(minutes=5)],
    "cum_net_pnl":    [0.0],
    "drawdown_limit": [-float(drawdown_buffer)],   # starts at -buffer
    "trade_num":      [0],
    "net_pnl":        [0.0],
    "fees":           [0.0],
    "gross_pnl":      [0.0],
})
eq_df = pd.concat(
    [start_pt,
     df[["soldTimestamp","cum_net_pnl","drawdown_limit",
         "trade_num","net_pnl","fees","gross_pnl"]]],
    ignore_index=True,
)

fig_eq = go.Figure()

# ── Shaded fill under equity line ────────────────────────────────────────────
fig_eq.add_trace(go.Scatter(
    x=eq_df["soldTimestamp"],
    y=eq_df["cum_net_pnl"],
    mode="lines",
    line=dict(color="#4f8ef7", width=2.5, shape="spline"),
    fill="tozeroy",
    fillcolor="rgba(79,142,247,0.09)",
    name="Net P&L",
    hovertemplate=(
        "<b>Trade #%{customdata[0]}</b><br>"
        "%{x|%b %d, %H:%M}<br>"
        "Cum. Net P&L: <b>$%{y:,.2f}</b><br>"
        "This trade: $%{customdata[1]:,.2f}  |  Fees: $%{customdata[2]:,.2f}<extra></extra>"
    ),
    customdata=np.column_stack([
        eq_df["trade_num"].to_numpy(),
        eq_df["net_pnl"].to_numpy(),
        eq_df["fees"].to_numpy(),
    ]),
))

# ── Trailing drawdown limit line (red dashed) ─────────────────────────────
fig_eq.add_trace(go.Scatter(
    x=eq_df["soldTimestamp"],
    y=eq_df["drawdown_limit"],
    mode="lines",
    line=dict(color="#f43f5e", width=1.8, dash="dash"),
    fill=None,
    name=f"Drawdown Limit (−${drawdown_buffer:,.0f} trail)",
    hovertemplate=(
        "%{x|%b %d, %H:%M}<br>"
        "Drawdown Limit: <b>$%{y:,.2f}</b><extra></extra>"
    ),
))

# ── $0 reference line ─────────────────────────────────────────────────────
fig_eq.add_hline(
    y=0,
    line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"),
    annotation_text="  $0 Baseline",
    annotation_font=dict(color="#55556a", size=11, family="DM Mono, monospace"),
)

# ── Peak marker ───────────────────────────────────────────────────────────
peak_idx = int(eq_df["cum_net_pnl"].idxmax())
peak_val = float(eq_df.loc[peak_idx, "cum_net_pnl"])
if peak_val > 0:
    fig_eq.add_trace(go.Scatter(
        x=[eq_df.loc[peak_idx, "soldTimestamp"]],
        y=[peak_val],
        mode="markers+text",
        marker=dict(color="#22c55e", size=9, line=dict(color="#09090f", width=2)),
        text=[f" Peak +${peak_val:,.0f}"],
        textposition="top right",
        textfont=dict(size=11, color="#22c55e", family="DM Mono, monospace"),
        name="Peak",
        hovertemplate="Peak: +$%{y:,.2f}<extra></extra>",
    ))

fig_eq.update_layout(
    **PLOT,
    margin=dict(l=10, r=10, t=30, b=10),
    height=400,
    showlegend=True,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(size=11, family="DM Sans, sans-serif"),
        bgcolor="rgba(0,0,0,0)",
    ),
    yaxis_tickprefix="$",
    yaxis_tickformat=",",
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#55556a"),
        zeroline=True, zerolinecolor="rgba(255,255,255,0.10)", zerolinewidth=1,
        tickprefix="$", tickformat=",",
    ),
)
st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})

# Drawdown callout
current_dd_limit = float(df["drawdown_limit"].iloc[-1])
current_pnl_val  = float(df["cum_net_pnl"].iloc[-1])
headroom         = current_pnl_val - current_dd_limit
locked           = current_dd_limit >= 0

dd_color  = "#22c55e" if headroom > drawdown_buffer * 0.5 else (
            "#f59e0b" if headroom > drawdown_buffer * 0.2 else "#f43f5e")
lock_note = "🔒 Limit locked at $0 — buffer fully secured" if locked else (
            f"⚠️ ${headroom:,.2f} of headroom remaining before breach")

st.markdown(
    f"""<div style="background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.2);
        border-radius:10px;padding:0.7rem 1.2rem;margin-bottom:0.5rem;
        font-family:'DM Mono',monospace;font-size:0.82rem;color:{dd_color};">
      <strong>Trailing Drawdown:</strong>
      &nbsp; Limit now at <strong>${current_dd_limit:,.2f}</strong>
      &nbsp;|&nbsp; Current P&L <strong>${current_pnl_val:,.2f}</strong>
      &nbsp;|&nbsp; {lock_note}
    </div>""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
#  ANALYTICS ROW  — Day-of-Week + Win/Loss donut
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Trade Analytics</div>', unsafe_allow_html=True)

left, right = st.columns([3, 2])

with left:
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                font-weight:600;color:#8888aa;margin-bottom:0.6rem;">
                Net P&L by Day of Week</div>""", unsafe_allow_html=True)

    DOW_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    dow = (df.groupby("day_of_week")["net_pnl"]
             .sum()
             .reindex(DOW_ORDER, fill_value=0.0)
             .reset_index())
    dow.columns = ["day", "pnl"]

    fig_dow = go.Figure(go.Bar(
        x=dow["day"],
        y=dow["pnl"],
        marker_color=dow["pnl"].apply(lambda v: "#22c55e" if v >= 0 else "#f43f5e"),
        marker_line_width=0,
        text=dow["pnl"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(size=11, family="DM Mono, monospace", color="#8888aa"),
        hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
    ))
    fig_dow.update_layout(**PLOT, margin=_M, height=290,
                          yaxis_tickprefix="$", yaxis_tickformat=",", bargap=0.35)
    st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

with right:
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                font-weight:600;color:#8888aa;margin-bottom:0.6rem;">
                Win / Loss Split (Net)</div>""", unsafe_allow_html=True)

    fig_pie = go.Figure(go.Pie(
        labels=["Wins", "Losses"],
        values=[max(len(wins), 0), max(len(losses), 0)],
        hole=0.62,
        marker=dict(colors=["#22c55e","#f43f5e"],
                    line=dict(color=["#09090f","#09090f"], width=3)),
        textinfo="percent",
        textfont=dict(family="DM Mono, monospace", size=12),
        hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
    ))
    fig_pie.add_annotation(
        text=f"<b>{win_rate:.0f}%</b><br><span style='font-size:11px'>Win Rate</span>",
        x=0.5, y=0.5,
        font=dict(size=22, family="Syne, sans-serif", color="#f0f0fa"),
        showarrow=False, align="center",
    )
    fig_pie.update_layout(
        **PLOT,
        height=290,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12,
                    xanchor="center", x=0.5,
                    font=dict(size=11, family="DM Sans, sans-serif")),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  MONTHLY P&L (net, only if > 1 month)
# ─────────────────────────────────────────────────────────────────────────────
monthly = (df.groupby("month_label")["net_pnl"]
             .sum()
             .reset_index()
             .rename(columns={"month_label":"month","net_pnl":"pnl"}))

if len(monthly) > 1:
    st.markdown('<div class="section-hdr">Monthly Net P&L</div>', unsafe_allow_html=True)
    fig_mo = go.Figure(go.Bar(
        x=monthly["month"],
        y=monthly["pnl"],
        marker_color=monthly["pnl"].apply(lambda v: "#2dd4bf" if v >= 0 else "#f43f5e"),
        marker_line_width=0,
        text=monthly["pnl"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(size=11, family="DM Mono, monospace", color="#8888aa"),
        hovertemplate="%{x}<br>Net P&L: <b>$%{y:,.2f}</b><extra></extra>",
    ))
    fig_mo.update_layout(**PLOT, margin=_M, height=240,
                         yaxis_tickprefix="$", yaxis_tickformat=",", bargap=0.3)
    st.plotly_chart(fig_mo, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  TRADE HISTORY TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Trade History</div>', unsafe_allow_html=True)

tbl = df[["trade_num","soldTimestamp","symbol","qty",
          "buyPrice","sellPrice","gross_pnl","fees","net_pnl","duration"]].copy()
tbl.columns = ["#","Date / Time","Symbol","Qty","Entry","Exit",
               "Gross P&L","Fees","Net P&L","Duration"]

tbl["Date / Time"] = tbl["Date / Time"].dt.strftime("%b %d, %Y  %H:%M")
tbl["Entry"]       = tbl["Entry"].apply(
    lambda v: f"${v:,.2f}" if pd.notna(v) and v != 0 else "—")
tbl["Exit"]        = tbl["Exit"].apply(
    lambda v: f"${v:,.2f}" if pd.notna(v) and v != 0 else "—")
tbl["Gross P&L"]   = tbl["Gross P&L"].apply(
    lambda v: f"+${v:,.2f}" if v > 0 else f"-${abs(v):,.2f}")
tbl["Fees"]        = tbl["Fees"].apply(lambda v: f"-${v:,.2f}" if v > 0 else "—")
tbl["Net P&L"]     = tbl["Net P&L"].apply(
    lambda v: f"+${v:,.2f}" if v > 0 else f"-${abs(v):,.2f}")

tbl = tbl.iloc[::-1].reset_index(drop=True)

st.dataframe(
    tbl,
    use_container_width=True,
    hide_index=True,
    height=min(38 * len(tbl) + 42, 500),
)


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER STAT PILLS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
p1, p2, p3, p4, p5, p6 = st.columns(6)

def pill(col, label: str, val: str) -> None:
    col.markdown(
        f'<div class="stat-pill">{label}<br><strong>{val}</strong></div>',
        unsafe_allow_html=True,
    )

largest_win  = f"${float(wins['net_pnl'].max()):,.2f}"   if len(wins)   else "—"
largest_loss = f"${float(losses['net_pnl'].min()):,.2f}" if len(losses) else "—"
mode_result  = df["duration"].mode()
common_dur   = str(mode_result.iloc[0]) if len(mode_result) > 0 else "—"

pill(p1, "Gross Profit",    f"${gross_profit:,.2f}")
pill(p2, "Total Fees Paid", f"-${total_fees:,.2f}")
pill(p3, "Largest Win",     largest_win)
pill(p4, "Largest Loss",    largest_loss)
pill(p5, "Common Duration", common_dur)
pill(p6, "Symbols Traded",  str(df["symbol"].nunique()))
