import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import io

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  — must be first Streamlit call
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
    Converts broker PnL strings to float:
        '$105.00'    →  105.0
        '$(230.00)'  → -230.0
        '-105'       → -105.0
        105.0        →  105.0  (already numeric)
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


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float(abs((equity - peak).min()))


def fmt_usd(v: float, sign: bool = False) -> str:
    prefix = "+" if (sign and v > 0) else ""
    if abs(v) >= 1_000_000:
        return f"{prefix}${v/1_000_000:.2f}M"
    return f"{prefix}${v:,.2f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


_M = dict(l=10, r=10, t=30, b=10)   # default margin — each chart merges this in manually

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
#  DEMO DATA
# ─────────────────────────────────────────────────────────────────────────────

def generate_demo() -> pd.DataFrame:
    rng     = np.random.default_rng(42)
    symbols = ["NQ","ES","TSLA","AAPL","SPY","QQQ","NVDA","MSFT","AMZN","META"]
    weights = [0.25,0.20,0.10,0.10,0.10,0.10,0.05,0.05,0.03,0.02]
    n       = 80
    base_ts = pd.Timestamp("2024-11-01 09:35:00")
    rows    = []
    for i in range(n):
        sym    = rng.choice(symbols, p=weights)
        qty    = int(rng.choice([1,2,3,5,10]))
        win    = rng.random() < 0.56
        pnl    = round(float(abs(rng.normal(350,280))) if win
                       else -float(abs(rng.normal(210,150))), 2)
        bp     = round(float(rng.uniform(100,500)), 2)
        sp     = round(bp + pnl / qty, 2)
        bought = base_ts + pd.Timedelta(
                     days=int(i//3),
                     hours=int(rng.integers(0,6)),
                     minutes=int(rng.integers(0,55)))
        mins   = int(rng.integers(1,120))
        sold   = bought + pd.Timedelta(minutes=mins)
        pstr   = f"${pnl:.2f}" if pnl >= 0 else f"$({abs(pnl):.2f})"
        rows.append({
            "symbol":          sym,
            "_priceFormat":    "0.00",
            "_priceFormatType":"DECIMAL",
            "_tickSize":       0.25,
            "buyFillId":       f"B{10000+i}",
            "sellFillId":      f"S{10000+i}",
            "qty":             qty,
            "buyPrice":        bp,
            "sellPrice":       sp,
            "pnl":             pstr,
            "boughtTimestamp": bought.strftime("%Y-%m-%dT%H:%M:%S"),
            "soldTimestamp":   sold.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration":        f"{mins}m",
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA PROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def process(df: pd.DataFrame, starting: float) -> pd.DataFrame:
    df = df.copy()
    df["pnl_clean"]       = df["pnl"].apply(parse_pnl)
    df["soldTimestamp"]   = pd.to_datetime(df["soldTimestamp"],   errors="coerce")
    df["boughtTimestamp"] = pd.to_datetime(df["boughtTimestamp"], errors="coerce")
    df = df.dropna(subset=["soldTimestamp"]).sort_values("soldTimestamp").reset_index(drop=True)
    df["cumulative_pnl"]  = df["pnl_clean"].cumsum()
    df["equity"]          = starting + df["cumulative_pnl"]
    df["day_of_week"]     = df["soldTimestamp"].dt.day_name()
    df["month_label"]     = df["soldTimestamp"].dt.strftime("%b '%y")
    df["trade_num"]       = range(1, len(df)+1)
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
total_trades = len(df)
wins         = df[df["pnl_clean"] > 0]
losses       = df[df["pnl_clean"] < 0]
total_pnl    = float(df["pnl_clean"].sum())
curr_equity  = starting_balance + total_pnl
win_rate     = len(wins) / total_trades * 100 if total_trades else 0.0
gross_profit = float(wins["pnl_clean"].sum())   if len(wins)   else 0.0
gross_loss   = float(losses["pnl_clean"].sum())  if len(losses) else 0.0
pf           = (gross_profit / abs(gross_loss))  if gross_loss  else float("inf")
avg_win      = float(wins["pnl_clean"].mean())   if len(wins)   else 0.0
avg_loss     = float(losses["pnl_clean"].mean()) if len(losses) else 0.0
rr           = (avg_win / abs(avg_loss))          if avg_loss    else float("inf")
max_dd       = max_drawdown(df["equity"])
total_return = (total_pnl / starting_balance) * 100


# ─────────────────────────────────────────────────────────────────────────────
#  KPI ROW 1
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Account Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Equity",
          f"${curr_equity:,.2f}",
          f"{fmt_usd(total_pnl, sign=True)} ({fmt_pct(total_return)})")
c2.metric("Net P&L",
          fmt_usd(total_pnl, sign=True),
          f"{len(wins)} wins  /  {len(losses)} losses",
          delta_color="off")
c3.metric("Win Rate",
          fmt_pct(win_rate),
          f"{total_trades} total trades",
          delta_color="off")
pf_str  = f"{pf:.2f}×" if pf != float("inf") else "∞"
pf_note = "strong edge" if pf > 1.5 else ("neutral" if pf > 0.9 else "review needed")
c4.metric("Profit Factor", pf_str, pf_note, delta_color="off")

st.markdown("<br>", unsafe_allow_html=True)

# KPI ROW 2
c5, c6, c7, c8 = st.columns(4)
c5.metric("Avg Win",       fmt_usd(avg_win),  f"{len(wins)} trades",   delta_color="off")
c6.metric("Avg Loss",      fmt_usd(avg_loss), f"{len(losses)} trades", delta_color="off")
rr_str = f"{rr:.2f}R" if rr != float("inf") else "∞R"
c7.metric("Risk / Reward", rr_str, "avg win ÷ |avg loss|", delta_color="off")
dd_pct = max_dd / starting_balance * 100
c8.metric("Max Drawdown",  fmt_usd(-max_dd),  f"−{dd_pct:.1f}% from peak", delta_color="inverse")


# ─────────────────────────────────────────────────────────────────────────────
#  EQUITY CURVE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Equity Curve</div>', unsafe_allow_html=True)

start_pt = pd.DataFrame({
    "soldTimestamp": [df["soldTimestamp"].iloc[0] - pd.Timedelta(minutes=5)],
    "equity":        [float(starting_balance)],
    "trade_num":     [0],
    "pnl_clean":     [0.0],
})
eq_df = pd.concat(
    [start_pt, df[["soldTimestamp","equity","trade_num","pnl_clean"]]],
    ignore_index=True
)

fig_eq = go.Figure()

fig_eq.add_trace(go.Scatter(
    x=eq_df["soldTimestamp"],
    y=eq_df["equity"],
    mode="lines",
    line=dict(color="#4f8ef7", width=2.5, shape="spline"),
    fill="tozeroy",
    fillcolor="rgba(79,142,247,0.08)",
    name="Equity",
    hovertemplate=(
        "<b>Trade #%{customdata[0]}</b><br>"
        "%{x|%b %d, %H:%M}<br>"
        "Equity: <b>$%{y:,.2f}</b><br>"
        "Trade P&L: $%{customdata[1]:,.2f}<extra></extra>"
    ),
    customdata=np.column_stack([
        eq_df["trade_num"].to_numpy(),
        eq_df["pnl_clean"].to_numpy(),
    ]),
))

fig_eq.add_hline(
    y=float(starting_balance),
    line=dict(color="rgba(255,255,255,0.12)", width=1, dash="dot"),
    annotation_text=f"  Start ${starting_balance:,.0f}",
    annotation_font=dict(color="#55556a", size=11, family="DM Mono, monospace"),
)

peak_idx = int(eq_df["equity"].idxmax())
fig_eq.add_trace(go.Scatter(
    x=[eq_df.loc[peak_idx, "soldTimestamp"]],
    y=[float(eq_df.loc[peak_idx, "equity"])],
    mode="markers+text",
    marker=dict(color="#22c55e", size=9, line=dict(color="#09090f", width=2)),
    text=[f" Peak ${float(eq_df.loc[peak_idx,'equity']):,.0f}"],
    textposition="top right",
    textfont=dict(size=11, color="#22c55e", family="DM Mono, monospace"),
    name="Peak",
    hovertemplate="Peak: $%{y:,.2f}<extra></extra>",
))

fig_eq.update_layout(
    **PLOT,
    margin=_M,
    height=370,
    showlegend=False,
    yaxis_tickprefix="$",
    yaxis_tickformat=",",
)
st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  ANALYTICS ROW
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Trade Analytics</div>', unsafe_allow_html=True)

left, right = st.columns([3, 2])

with left:
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                font-weight:600;color:#8888aa;margin-bottom:0.6rem;">
                P&L by Day of Week</div>""", unsafe_allow_html=True)

    DOW_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    dow = (df.groupby("day_of_week")["pnl_clean"]
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
        hovertemplate="%{x}<br>P&L: <b>$%{y:,.2f}</b><extra></extra>",
    ))
    fig_dow.update_layout(**PLOT, margin=_M, height=290,
                          yaxis_tickprefix="$", yaxis_tickformat=",", bargap=0.35)
    st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

with right:
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;
                font-weight:600;color:#8888aa;margin-bottom:0.6rem;">
                Win / Loss Split</div>""", unsafe_allow_html=True)

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
#  MONTHLY P&L (only shown when > 1 month of data)
# ─────────────────────────────────────────────────────────────────────────────
monthly = (df.groupby("month_label")["pnl_clean"]
             .sum()
             .reset_index()
             .rename(columns={"month_label":"month","pnl_clean":"pnl"}))

if len(monthly) > 1:
    st.markdown('<div class="section-hdr">Monthly P&L</div>', unsafe_allow_html=True)
    fig_mo = go.Figure(go.Bar(
        x=monthly["month"],
        y=monthly["pnl"],
        marker_color=monthly["pnl"].apply(lambda v: "#2dd4bf" if v >= 0 else "#f43f5e"),
        marker_line_width=0,
        text=monthly["pnl"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(size=11, family="DM Mono, monospace", color="#8888aa"),
        hovertemplate="%{x}<br>P&L: <b>$%{y:,.2f}</b><extra></extra>",
    ))
    fig_mo.update_layout(**PLOT, margin=_M, height=240,
                         yaxis_tickprefix="$", yaxis_tickformat=",", bargap=0.3)
    st.plotly_chart(fig_mo, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
#  TRADE HISTORY TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">Trade History</div>', unsafe_allow_html=True)

tbl = df[["trade_num","soldTimestamp","symbol","qty",
          "buyPrice","sellPrice","pnl_clean","duration"]].copy()
tbl.columns = ["#","Date / Time","Symbol","Qty","Entry","Exit","P&L ($)","Duration"]

tbl["Date / Time"] = tbl["Date / Time"].dt.strftime("%b %d, %Y  %H:%M")
tbl["Entry"]       = tbl["Entry"].apply(
    lambda v: f"${v:,.2f}" if pd.notna(v) and v != 0 else "—")
tbl["Exit"]        = tbl["Exit"].apply(
    lambda v: f"${v:,.2f}" if pd.notna(v) and v != 0 else "—")
tbl["P&L ($)"]     = tbl["P&L ($)"].apply(
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
        unsafe_allow_html=True
    )

largest_win  = f"${float(wins['pnl_clean'].max()):,.2f}"  if len(wins)   else "—"
largest_loss = f"${float(losses['pnl_clean'].min()):,.2f}" if len(losses) else "—"
mode_result  = df["duration"].mode()
common_dur   = str(mode_result.iloc[0]) if len(mode_result) > 0 else "—"

pill(p1, "Gross Profit",    f"${gross_profit:,.2f}")
pill(p2, "Gross Loss",      f"${gross_loss:,.2f}")
pill(p3, "Largest Win",     largest_win)
pill(p4, "Largest Loss",    largest_loss)
pill(p5, "Common Duration", common_dur)
pill(p6, "Symbols Traded",  str(df["symbol"].nunique()))
