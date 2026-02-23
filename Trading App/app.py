import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import re
from datetime import datetime

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
#  CUSTOM CSS  — dark, refined, SaaS-grade
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ───────────────────────────────────────── */
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
    --accent-purple: #a78bfa;
    --accent-green:  #22c55e;
    --accent-red:    #f43f5e;
    --accent-amber:  #f59e0b;
    --glow-blue:     rgba(79,142,247,0.15);
    --glow-green:    rgba(34,197,94,0.12);
    --glow-red:      rgba(244,63,94,0.12);
}

/* ── Global reset ─────────────────────────────────────────── */
html, body, [data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stTextInput input {
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

/* ── Hide default header/toolbar ─────────────────────────── */
header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
.block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 100% !important; }

/* ── Divider ──────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Metric cards ─────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.1rem 1.4rem !important;
    transition: border-color 0.2s ease, background 0.2s ease;
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
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── Dataframe ────────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
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
    border-bottom: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
}
.stDataFrame tbody tr:hover td { background: var(--bg-card-hover) !important; }

/* ── Section headers ──────────────────────────────────────── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Page title ───────────────────────────────────────────── */
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.page-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
}

/* ── Status badge ─────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}
.badge-green  { background: var(--glow-green); color: var(--accent-green); border: 1px solid rgba(34,197,94,0.25); }
.badge-red    { background: var(--glow-red);   color: var(--accent-red);   border: 1px solid rgba(244,63,94,0.25); }
.badge-blue   { background: var(--glow-blue);  color: var(--accent-blue);  border: 1px solid rgba(79,142,247,0.25); }

/* ── Stat pill row ────────────────────────────────────────── */
.stat-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-align: center;
}
.stat-pill strong { color: var(--text-primary); font-weight: 600; }

/* ── Upload area ──────────────────────────────────────────── */
.upload-hint {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    color: var(--text-muted);
    text-align: center;
    margin-top: 0.5rem;
    line-height: 1.5;
}

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Plotly chart bg fix ──────────────────────────────────── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_pnl(value: str) -> float:
    """Convert broker PnL strings to float.
    '$105.00' → 105.0   |   '$(230.00)' → -230.0   |   '-105' → -105.0
    """
    if pd.isna(value):
        return 0.0
    s = str(value).strip()
    negative = s.startswith("$(") or s.startswith("-(") or (s.startswith("-") and "(" not in s and s.count("-") == 1 and not s.startswith("-$"))
    # Remove all non-numeric except dot and minus
    cleaned = re.sub(r"[^0-9\.\-]", "", s)
    if not cleaned:
        return 0.0
    try:
        num = float(cleaned)
        # parentheses always mean negative
        if "(" in s:
            num = -abs(num)
        return num
    except ValueError:
        return 0.0


def compute_max_drawdown(equity_series: pd.Series) -> float:
    """Peak-to-trough max drawdown as a positive dollar amount."""
    peak = equity_series.cummax()
    drawdown = equity_series - peak
    return abs(drawdown.min())


def fmt_currency(val: float, sign: bool = True) -> str:
    prefix = "+" if (sign and val > 0) else ""
    if abs(val) >= 1_000_000:
        return f"{prefix}${val/1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"{prefix}${val:,.0f}"
    return f"{prefix}${val:,.2f}"


def fmt_pct(val: float) -> str:
    return f"{val:.1f}%"


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#8888aa", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#55556a"),
        zeroline=False,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#55556a"),
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.06)",
        font=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor="#1c1c28",
        bordercolor="#2e2e45",
        font=dict(family="DM Mono, monospace", size=12, color="#f0f0fa"),
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.2rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                    color:#f0f0fa;letter-spacing:-0.02em;">TradeLog</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:0.75rem;
                    color:#55556a;margin-top:2px;">Professional Trading Journal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;
                font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                color:#55556a;margin-bottom:0.7rem;">Account Setup</div>""",
                unsafe_allow_html=True)

    starting_balance = st.number_input(
        "Starting Account Balance ($)",
        min_value=0.0,
        value=50_000.0,
        step=1_000.0,
        format="%.2f",
        help="Your account balance before the first trade in this CSV.",
    )

    st.markdown("---")

    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.72rem;
                font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                color:#55556a;margin-bottom:0.7rem;">Import Trades</div>""",
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        label_visibility="collapsed",
    )
    st.markdown("""<div class="upload-hint">
        Expected columns:<br>
        <code style="color:#4f8ef7;">symbol · pnl · qty · buyPrice · sellPrice · boughtTimestamp · soldTimestamp · duration</code>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Demo data toggle
    use_demo = st.checkbox("Load demo data", value=(uploaded_file is None))

    st.markdown("""
    <div style="position:absolute;bottom:1.5rem;left:1.5rem;right:1.5rem;
                font-family:'DM Sans',sans-serif;font-size:0.7rem;color:#2e2e45;
                text-align:center;">
        TradeLog v1.0 · Built with Streamlit
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  DEMO DATA GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_demo_data() -> pd.DataFrame:
    np.random.seed(42)
    symbols  = ["NQ", "ES", "TSLA", "AAPL", "SPY", "QQQ", "NVDA", "MSFT", "AMZN", "META"]
    n        = 80
    base_ts  = pd.Timestamp("2024-11-01 09:35:00")
    records  = []
    for i in range(n):
        sym     = np.random.choice(symbols, p=[0.25,0.2,0.1,0.1,0.1,0.1,0.05,0.05,0.03,0.02])
        qty     = np.random.choice([1, 2, 3, 5, 10])
        win     = np.random.random() < 0.56
        pnl_raw = abs(np.random.normal(350, 280)) if win else -abs(np.random.normal(210, 150))
        pnl_raw = round(pnl_raw, 2)
        bp      = round(np.random.uniform(100, 500), 2)
        sp      = round(bp + pnl_raw / qty, 2)
        bought  = base_ts + pd.Timedelta(days=i // 3, hours=np.random.randint(0, 6), minutes=np.random.randint(0, 55))
        mins    = np.random.randint(1, 120)
        sold    = bought + pd.Timedelta(minutes=mins)
        pnl_str = f"${pnl_raw:.2f}" if pnl_raw >= 0 else f"$({abs(pnl_raw):.2f})"
        records.append({
            "symbol":          sym,
            "_priceFormat":    "0.00",
            "_priceFormatType":"DECIMAL",
            "_tickSize":       0.25,
            "buyFillId":       f"B{10000+i}",
            "sellFillId":      f"S{10000+i}",
            "qty":             qty,
            "buyPrice":        bp,
            "sellPrice":       sp,
            "pnl":             pnl_str,
            "boughtTimestamp": bought.strftime("%Y-%m-%dT%H:%M:%S"),
            "soldTimestamp":   sold.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration":        f"{mins}m",
        })
    return pd.DataFrame(records)


# ─────────────────────────────────────────────────────────────────────────────
#  LOAD & PARSE DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(file_bytes, starting_balance: float) -> pd.DataFrame:
    import io
    df = pd.read_csv(io.BytesIO(file_bytes))
    return process_df(df, starting_balance)


def process_df(df: pd.DataFrame, starting_balance: float) -> pd.DataFrame:
    df = df.copy()
    df["pnl_clean"]       = df["pnl"].apply(parse_pnl)
    df["soldTimestamp"]   = pd.to_datetime(df["soldTimestamp"], errors="coerce")
    df["boughtTimestamp"] = pd.to_datetime(df["boughtTimestamp"], errors="coerce")
    df = df.sort_values("soldTimestamp").reset_index(drop=True)
    df["cumulative_pnl"]  = df["pnl_clean"].cumsum()
    df["equity"]          = starting_balance + df["cumulative_pnl"]
    df["day_of_week"]     = df["soldTimestamp"].dt.day_name()
    df["trade_num"]       = range(1, len(df) + 1)
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  DECIDE DATA SOURCE
# ─────────────────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    df = load_data(uploaded_file.read(), starting_balance)
    data_source = "uploaded"
elif use_demo:
    raw = generate_demo_data()
    df  = process_df(raw, starting_balance)
    data_source = "demo"
else:
    df          = None
    data_source = "none"


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
header_col, badge_col = st.columns([3, 1])
with header_col:
    st.markdown("""<div class="page-title">Performance Dashboard</div>
    <div class="page-subtitle">Real-time trade analytics & equity tracking</div>""",
    unsafe_allow_html=True)
with badge_col:
    if data_source == "demo":
        st.markdown("""<div style="text-align:right;margin-top:0.8rem;">
            <span class="badge badge-blue">DEMO DATA</span></div>""",
            unsafe_allow_html=True)
    elif data_source == "uploaded":
        st.markdown("""<div style="text-align:right;margin-top:0.8rem;">
            <span class="badge badge-green">LIVE DATA</span></div>""",
            unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  NO DATA STATE
# ─────────────────────────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                height:55vh;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">📂</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;
                    color:#f0f0fa;margin-bottom:0.5rem;">No trades loaded</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:0.9rem;color:#55556a;
                    max-width:380px;line-height:1.6;">
            Upload a CSV file in the sidebar, or enable <strong style="color:#8888aa;">demo data</strong>
            to explore the dashboard.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  COMPUTE METRICS
# ─────────────────────────────────────────────────────────────────────────────
total_trades  = len(df)
wins          = df[df["pnl_clean"] > 0]
losses        = df[df["pnl_clean"] < 0]
total_pnl     = df["pnl_clean"].sum()
current_equity= starting_balance + total_pnl
win_rate      = len(wins) / total_trades * 100 if total_trades else 0
gross_profit  = wins["pnl_clean"].sum()
gross_loss    = losses["pnl_clean"].sum()
profit_factor = (gross_profit / abs(gross_loss)) if gross_loss != 0 else float("inf")
avg_win       = wins["pnl_clean"].mean()  if len(wins)   else 0
avg_loss      = losses["pnl_clean"].mean() if len(losses) else 0
rr_ratio      = (avg_win / abs(avg_loss)) if avg_loss != 0 else float("inf")
max_dd        = compute_max_drawdown(df["equity"])
total_return  = (total_pnl / starting_balance) * 100


# ─────────────────────────────────────────────────────────────────────────────
#  METRICS ROW 1  — primary KPIs
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Account Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(
        "Current Equity",
        f"${current_equity:,.2f}",
        delta=f"{fmt_currency(total_pnl, sign=True)} ({fmt_pct(total_return)})",
        delta_color="normal",
    )
with c2:
    st.metric(
        "Net PnL",
        fmt_currency(total_pnl, sign=True),
        delta=f"{len(wins)}W / {len(losses)}L",
        delta_color="off",
    )
with c3:
    st.metric(
        "Win Rate",
        fmt_pct(win_rate),
        delta=f"{total_trades} total trades",
        delta_color="off",
    )
with c4:
    pf_display = f"{profit_factor:.2f}x" if profit_factor != float("inf") else "∞"
    pf_delta   = "strong edge" if profit_factor > 1.5 else ("break-even" if profit_factor > 0.9 else "review needed")
    st.metric("Profit Factor", pf_display, delta=pf_delta, delta_color="off")

st.markdown("<br>", unsafe_allow_html=True)

# METRICS ROW 2 — secondary KPIs
c5, c6, c7, c8 = st.columns(4)
with c5:
    st.metric("Avg Win", fmt_currency(avg_win), delta=f"{len(wins)} winning trades", delta_color="off")
with c6:
    st.metric("Avg Loss", fmt_currency(avg_loss), delta=f"{len(losses)} losing trades", delta_color="off")
with c7:
    rr_display = f"{rr_ratio:.2f}" if rr_ratio != float("inf") else "∞"
    st.metric("Risk / Reward", f"{rr_display}R", delta="avg win ÷ avg loss", delta_color="off")
with c8:
    dd_pct = (max_dd / starting_balance * 100)
    st.metric("Max Drawdown", fmt_currency(-max_dd), delta=f"-{dd_pct:.1f}% from peak", delta_color="inverse")


# ─────────────────────────────────────────────────────────────────────────────
#  EQUITY CURVE CHART
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Equity Curve</div>', unsafe_allow_html=True)

# Add starting point
start_row = pd.DataFrame({
    "soldTimestamp": [df["soldTimestamp"].iloc[0] - pd.Timedelta(minutes=5)],
    "equity":        [starting_balance],
    "trade_num":     [0],
    "pnl_clean":     [0],
})
eq_df = pd.concat([start_row, df[["soldTimestamp","equity","trade_num","pnl_clean"]]], ignore_index=True)

# Color breakpoints
line_color   = "#4f8ef7"
profit_color = "rgba(79,142,247,0.12)"
loss_color   = "rgba(244,63,94,0.08)"

fig_eq = go.Figure()

# Fill under curve (profit zone above start, loss zone below)
fig_eq.add_trace(go.Scatter(
    x=eq_df["soldTimestamp"], y=eq_df["equity"],
    mode="lines",
    line=dict(color=line_color, width=2.5, shape="spline"),
    fill="tonexty",
    fillcolor=profit_color,
    name="Equity",
    hovertemplate=(
        "<b>Trade #%{customdata[0]}</b><br>"
        "Time: %{x|%b %d, %H:%M}<br>"
        "Equity: <b>$%{y:,.2f}</b><br>"
        "PnL: $%{customdata[1]:,.2f}<extra></extra>"
    ),
    customdata=np.stack([eq_df["trade_num"], eq_df["pnl_clean"]], axis=-1),
))

# Starting balance reference line
fig_eq.add_hline(
    y=starting_balance,
    line=dict(color="rgba(255,255,255,0.12)", width=1, dash="dot"),
    annotation_text=f"  Start ${starting_balance:,.0f}",
    annotation_font=dict(color="#55556a", size=11, family="DM Mono, monospace"),
)

# Peak equity marker
peak_idx  = eq_df["equity"].idxmax()
peak_eq   = eq_df.loc[peak_idx]
fig_eq.add_trace(go.Scatter(
    x=[peak_eq["soldTimestamp"]], y=[peak_eq["equity"]],
    mode="markers+text",
    marker=dict(color="#22c55e", size=9, symbol="circle",
                line=dict(color="#09090f", width=2)),
    text=[f" Peak ${peak_eq['equity']:,.0f}"],
    textposition="top right",
    textfont=dict(size=11, color="#22c55e", family="DM Mono, monospace"),
    name="Peak Equity",
    hovertemplate="Peak: $%{y:,.2f}<extra></extra>",
))

fig_eq.update_layout(
    **PLOTLY_LAYOUT,
    height=370,
    xaxis_title=None,
    yaxis_title=None,
    yaxis_tickprefix="$",
    yaxis_tickformat=",",
    showlegend=False,
    xaxis=dict(**PLOTLY_LAYOUT["xaxis"], rangeslider=dict(visible=False)),
)

st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  BOTTOM ROW: Day-of-Week bars  +  PnL Distribution
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Trade Analytics</div>', unsafe_allow_html=True)

chart_l, chart_r = st.columns([3, 2])

# ── Day of Week PnL ────────────────────────────────────────────────────────
with chart_l:
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                font-weight:600;color:#8888aa;margin-bottom:0.8rem;">
                P&L by Day of Week</div>""", unsafe_allow_html=True)

    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    dow_df    = (df.groupby("day_of_week")["pnl_clean"]
                   .sum()
                   .reindex(dow_order, fill_value=0)
                   .reset_index())
    dow_df.columns = ["day", "pnl"]
    dow_df["color"] = dow_df["pnl"].apply(
        lambda v: "#22c55e" if v > 0 else "#f43f5e"
    )

    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(
        x=dow_df["day"],
        y=dow_df["pnl"],
        marker_color=dow_df["color"],
        marker_line_width=0,
        text=dow_df["pnl"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(size=11, family="DM Mono, monospace", color="#8888aa"),
        hovertemplate="%{x}<br>PnL: <b>$%{y:,.2f}</b><extra></extra>",
    ))
    fig_dow.update_layout(
        **PLOTLY_LAYOUT,
        height=290,
        yaxis_tickprefix="$",
        yaxis_tickformat=",",
        bargap=0.35,
    )
    st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

# ── Win/Loss donut ─────────────────────────────────────────────────────────
with chart_r:
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                font-weight:600;color:#8888aa;margin-bottom:0.8rem;">
                Win / Loss Distribution</div>""", unsafe_allow_html=True)

    fig_pie = go.Figure(go.Pie(
        labels=["Wins", "Losses"],
        values=[len(wins), len(losses)],
        hole=0.62,
        marker=dict(
            colors=["#22c55e", "#f43f5e"],
            line=dict(color=["#09090f","#09090f"], width=3),
        ),
        textinfo="percent",
        textfont=dict(family="DM Mono, monospace", size=12),
        hovertemplate="%{label}: <b>%{value} trades</b> (%{percent})<extra></extra>",
    ))
    fig_pie.add_annotation(
        text=f"<b>{win_rate:.0f}%</b><br><span style='font-size:11px'>Win Rate</span>",
        x=0.5, y=0.5,
        font=dict(size=22, family="Syne, sans-serif", color="#f0f0fa"),
        showarrow=False,
        align="center",
    )
    fig_pie.update_layout(
        **PLOTLY_LAYOUT,
        height=290,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.12,
            xanchor="center", x=0.5,
            font=dict(size=11, family="DM Sans, sans-serif"),
        ),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  MONTHLY PnL HEATMAP-STYLE BAR
# ─────────────────────────────────────────────────────────────────────────────
if df["soldTimestamp"].notna().any():
    df["month_str"] = df["soldTimestamp"].dt.strftime("%b '%y")
    monthly = (df.groupby("month_str")["pnl_clean"]
                 .sum()
                 .reset_index()
                 .rename(columns={"month_str": "month", "pnl_clean": "pnl"}))

    if len(monthly) > 1:
        st.markdown('<div class="section-header">Monthly P&L</div>', unsafe_allow_html=True)
        fig_month = go.Figure()
        fig_month.add_trace(go.Bar(
            x=monthly["month"],
            y=monthly["pnl"],
            marker_color=monthly["pnl"].apply(lambda v: "#2dd4bf" if v > 0 else "#f43f5e"),
            marker_line_width=0,
            text=monthly["pnl"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, family="DM Mono, monospace", color="#8888aa"),
            hovertemplate="%{x}<br>Monthly PnL: <b>$%{y:,.2f}</b><extra></extra>",
        ))
        fig_month.update_layout(
            **PLOTLY_LAYOUT,
            height=230,
            yaxis_tickprefix="$",
            yaxis_tickformat=",",
            bargap=0.3,
        )
        st.plotly_chart(fig_month, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  TRADE HISTORY TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Trade History</div>', unsafe_allow_html=True)

display_cols = {
    "trade_num":      "#",
    "soldTimestamp":  "Date / Time",
    "symbol":         "Symbol",
    "qty":            "Qty",
    "buyPrice":       "Entry",
    "sellPrice":      "Exit",
    "pnl_clean":      "PnL ($)",
    "duration":       "Duration",
}

tbl = df[list(display_cols.keys())].copy().rename(columns=display_cols)
tbl["Date / Time"] = tbl["Date / Time"].dt.strftime("%b %d, %Y  %H:%M")
tbl["Entry"]       = tbl["Entry"].apply(lambda v: f"${v:,.2f}" if pd.notna(v) else "—")
tbl["Exit"]        = tbl["Exit"].apply(lambda v: f"${v:,.2f}"  if pd.notna(v) else "—")

# Style the PnL column
def style_pnl(val):
    color = "#22c55e" if val > 0 else ("#f43f5e" if val < 0 else "#8888aa")
    prefix = "+" if val > 0 else ""
    return f"color: {color}; font-weight: 600; font-family: 'DM Mono', monospace;"

def format_pnl(val):
    prefix = "+" if val > 0 else ""
    return f"{prefix}${val:,.2f}"

tbl["PnL ($)"] = tbl["PnL ($)"].apply(format_pnl)

# Reverse to show most recent first
tbl = tbl.iloc[::-1].reset_index(drop=True)

st.dataframe(
    tbl,
    use_container_width=True,
    hide_index=True,
    height=min(36 * len(tbl) + 40, 480),
)


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER STAT PILLS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
p1, p2, p3, p4, p5, p6 = st.columns(6)
pills = [
    (p1, "Gross Profit",   f"${gross_profit:,.2f}"),
    (p2, "Gross Loss",     f"${gross_loss:,.2f}"),
    (p3, "Largest Win",    f"${wins['pnl_clean'].max():,.2f}"  if len(wins)   else "—"),
    (p4, "Largest Loss",   f"${losses['pnl_clean'].min():,.2f}" if len(losses) else "—"),
    (p5, "Avg Duration",   df["duration"].mode()[0] if len(df) else "—"),
    (p6, "Symbols Traded", str(df["symbol"].nunique())),
]
for col, label, val in pills:
    col.markdown(f"""<div class="stat-pill">{label}<br>
        <strong>{val}</strong></div>""", unsafe_allow_html=True)
