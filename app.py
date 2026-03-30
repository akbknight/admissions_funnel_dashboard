
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import duckdb  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
from datetime import datetime
import os
import textwrap
import io
from fpdf import FPDF  # type: ignore
import asyncio
import sys

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# --- CONFIGURATION (Must be first) ---
st.set_page_config(page_title="Kogod Admissions Funnel", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (Themed & High Density) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Theme-Aware Colors */
    :root {
        --brand-blue: #004F9F;
        --brand-red: #C41130;
        
        --card-bg: var(--secondary-background-color); 
        --app-bg: var(--background-color);
        --text-main: var(--text-color);
        --border-subtle: color-mix(in srgb, var(--text-color), transparent 85%);
    }

    .stApp { background-color: var(--app-bg); }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: var(--card-bg);
        border-radius: 6px;
        border: 1px solid var(--border-subtle);
        color: var(--text-main);
        font-weight: 600;
        font-size: 14px;
        padding: 4px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--brand-blue) !important;
        color: white !important;
        border-color: var(--brand-blue) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: white !important;
    }

    /* FUNNEL GRID */
    .funnel-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .metric-row {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .row-title {
        font-size: 13px;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 10px;
        border-bottom: 2px solid var(--brand-red);
        padding-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .sub-metric {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px dashed var(--border-subtle);
    }
    .sub-metric:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .sub-label {
        font-size: 12px;
        font-weight: 500;
        opacity: 0.8;
    }
    
    .sub-val-group {
        text-align: right;
        display: flex;
        align-items: baseline;
        gap: 8px;
    }
    .sub-value {
        font-size: 15px;
        font-weight: 700;
    }
    
    .sub-delta {
        font-size: 11px;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .pos { color: #047857; background-color: #D1FAE5; }
    .neg { color: #B91C1C; background-color: #FEE2E2; } 

    @media (prefers-color-scheme: dark) {
        .pos { color: #6EE7B7; background-color: rgba(5, 150, 105, 0.2); }
        .neg { color: #FCA5A5; background-color: rgba(220, 38, 38, 0.2); }
    }

    /* DEPOSITS */
    .deposit-container {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .dep-high-level {
        background: linear-gradient(135deg, var(--brand-blue) 0%, #002855 100%);
        border-radius: 8px;
        padding: 20px;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .dep-hl-label { font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }
    .dep-hl-val { font-size: 36px; font-weight: 700; margin: 4px 0; }
    
    .dep-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    
    .dep-mini-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 12px 16px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute("SELECT * FROM 'data/processed/master_funnel_data.parquet'").fetchdf()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df_master = load_data()
if df_master.empty: st.stop()

# --- PROGRAM CONSOLIDATION ---
def remap_program(prog):
    p = str(prog)
    if 'Real Estate' in p or 'Taxation' in p:
        return None
    if 'Certificate in' in p:
        return 'Certificates (Combined)'
        
    if p.startswith('Bach/MS'):
        p = p.replace('Bach/MS', 'MS')
        
    if p == 'MS in Analytics':
        return 'MS in Business Analytics and AI'
    if p == 'MS in Analytics (Online)':
        return 'MS in Business Analytics and AI (Online)'

    if 'MBA' in p:
        if p.strip() in ['Online MBA', 'LGEP MBA']:
            return p.strip()
        return 'Full-Time MBA'
        
    return p

df_master['program_display'] = df_master['program'].apply(remap_program)
df_master = df_master.dropna(subset=['program_display'])

# --- LOGIC ---
df_master['category'] = df_master['program_display'].apply(
    lambda x: 'MBA' if 'mba' in str(x).lower() 
    else ('Online' if 'online' in str(x).lower() else 'Specialized Masters')
)

def calc_metrics(df, term):
    sub = df[df['term'] == term]
    m = {
        'Started': sub['is_ytd_started'].sum(),
        'Submitted': sub['is_ytd_submitted'].sum(),
        'Completed': sub['is_ytd_completed'].sum(),
        'Admitted': sub['is_ytd_admitted'].sum(),
        'Deposited_Total': sub['is_ytd_deposited'].sum(),
        'Deferred': sub['is_ytd_deferred'].sum(),
    }
    m['Net_New_Deposits'] = m['Deposited_Total'] - m['Deferred']
    
    dom = sub[sub['residency'] == 'Domestic']
    intl = sub[sub['residency'] == 'International']
    
    for k in ['Started', 'Submitted', 'Completed', 'Admitted', 'Deposited_Total', 'Deferred']:
        m[f'{k}_Dom'] = dom[f'is_ytd_{k.lower()}'].sum() if k != 'Deposited_Total' else dom['is_ytd_deposited'].sum()
        m[f'{k}_Int'] = intl[f'is_ytd_{k.lower()}'].sum() if k != 'Deposited_Total' else intl['is_ytd_deposited'].sum()
        
    m['Net_New_Dom'] = m['Deposited_Total_Dom'] - m['Deferred_Dom']
    m['Net_New_Int'] = m['Deposited_Total_Int'] - m['Deferred_Int']
    return m

def fmt_pct(curr, prev):
    if prev == 0: return ""
    delta = (curr - prev) / prev * 100
    cls = "pos" if delta >= 0 else "neg"
    icon = "▲" if delta >= 0 else "▼"
    return f"<span class='sub-delta {cls}'>{icon} {abs(delta):.1f}%</span>"

def html_metric_row(title, k_tot, k_dom, k_int, m26, m25):
    def row_dat(key):
        c, p = m26.get(key,0), m25.get(key,0)
        return f"{c:,}", fmt_pct(c, p)
    
    v_tot, d_tot = row_dat(k_tot)
    v_dom, d_dom = row_dat(k_dom)
    v_int, d_int = row_dat(k_int)
    
    # Flattened HTML to absolutely prevent Markdown code block parsing
    return (
        f'<div class="metric-row">'
        f'<div class="row-title">{title}</div>'
        f'<div class="sub-metric"><span class="sub-label">Total</span><div class="sub-val-group"><span class="sub-value">{v_tot}</span>{d_tot}</div></div>'
        f'<div class="sub-metric"><span class="sub-label">Domestic</span><div class="sub-val-group"><span class="sub-value">{v_dom}</span>{d_dom}</div></div>'
        f'<div class="sub-metric"><span class="sub-label">International</span><div class="sub-val-group"><span class="sub-value">{v_int}</span>{d_int}</div></div>'
        f'</div>'
    )

def html_dep_mini(label, key, m26, m25):
    c, p = m26.get(key,0), m25.get(key,0)
    delta = fmt_pct(c, p)
    
    return (
        f'<div class="dep-mini-card">'
        f'<span class="sub-label" style="margin-bottom:4px;">{label}</span>'
        f'<div style="display:flex; align-items:baseline; justify-content:space-between;">'
        f'<span class="sub-value" style="font-size:20px;">{c:,}</span>{delta}'
        f'</div></div>'
    )

def generate_pdf_report(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_text_color(0, 79, 159) # AU Brand Blue
    pdf.cell(0, 10, f'Kogod Admissions Funnel - Fall 2026 vs Fall 2025 ({datetime.now().strftime("%Y-%m-%d")})', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Table Header
    pdf.set_font('helvetica', 'B', 8)
    pdf.set_fill_color(0, 79, 159)
    pdf.set_text_color(255, 255, 255)
    cols = ['Program', 'Started', 'Submitted', 'Completed', 'Admitted', 'Net Deposits']
    col_widths = {0: 80, 1: 39, 2: 39, 3: 39, 4: 39, 5: 39}
    for i, col in enumerate(cols):
        pdf.cell(col_widths[i], 8, col, border=1, fill=True, align='C')
    pdf.ln(8)
    
    pdf.set_text_color(0, 0, 0)
    programs = sorted(df['program_display'].unique())
    
    for p in programs + ['Total']:
        sub = df if p == 'Total' else df[df['program_display'] == p]
        if sub.empty: continue
        
        m26 = calc_metrics(sub, 'Fall 2026')
        m25 = calc_metrics(sub, 'Fall 2025')
        
        pdf.set_font('helvetica', 'B' if p == 'Total' else '', 8)
        
        # Determine cell fill
        fill = True if p == 'Total' else False
        if p == 'Total':
            pdf.set_fill_color(240, 240, 240)
            
        pdf.cell(col_widths[0], 10, p, border=1, fill=fill)
        
        for i, metric in enumerate(['Started', 'Submitted', 'Completed', 'Admitted', 'Net_New_Deposits']):
            c = m26.get(metric, 0)
            prev = m25.get(metric, 0)
            
            c_dom = m26.get(f"{metric}_Dom" if metric != 'Net_New_Deposits' else "Net_New_Dom", 0)
            c_int = m26.get(f"{metric}_Int" if metric != 'Net_New_Deposits' else "Net_New_Int", 0)
            
            val_txt = f"F26: {c} | F25: {prev}"
            detail_txt = f"Dom: {c_dom} | Int: {c_int}"
            pct = ""
            if prev > 0:
                delta = (c - prev) / prev * 100
                pct = f"{delta:+.1f}%"
            
            x, y = pdf.get_x(), pdf.get_y()
            cw = col_widths.get(i+1, 39)
            pdf.rect(x, y, cw, 10, style='FD' if fill else 'D')
            pdf.set_xy(x, y + 1)
            pdf.cell(cw, 4, f"{val_txt} ({pct})" if pct else val_txt, align='C')
            pdf.set_xy(x, y + 5)
            pdf.set_font('helvetica', '', 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(cw, 4, detail_txt, align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('helvetica', 'B' if p == 'Total' else '', 8)
            pdf.set_xy(x + cw, y)
            
        pdf.ln(10)
        
    return bytes(pdf.output())

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Filters")
    opts = ["All Programs"] + sorted(df_master['program_display'].dropna().unique().tolist())
    sel = st.selectbox("Academic Program", opts)
    
    st.markdown("---")
    pdf_bytes = generate_pdf_report(df_master)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name=f"Kogod_Funnel_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

df_filt = df_master if sel == "All Programs" else df_master[df_master['program_display'] == sel]

# --- MAIN PAGE ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"## Kogod Admissions Funnel")
    st.markdown(f"<span style='opacity:0.7; font-weight:500;'>Year-over-Year Comparison: Fall 2026 vs Fall 2025</span>", unsafe_allow_html=True)

st.markdown("---")

def render_view(df_view):
    if df_view.empty:
        st.info("No Data Available for this selection.")
        return
        
    m26 = calc_metrics(df_view, 'Fall 2026')
    m25 = calc_metrics(df_view, 'Fall 2025')
    
    # 1. DEPOSIT SECTION
    st.markdown("#### Deposit Analysis")
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            curr, prev = m26['Net_New_Deposits'], m25['Net_New_Deposits']
            d_txt = f"{((curr-prev)/prev*100):+.1f}% YoY" if prev > 0 else "N/A"
            gross = m26['Deposited_Total']
            
            # Flattened HTML
            st.markdown((
                f'<div class="dep-high-level">'
                f'<div class="dep-hl-item">'
                f'<div class="dep-hl-label">Total Net New Deposits</div>'
                f'<div class="dep-hl-val">{curr:,}</div>'
                f'<div class="dep-hl-delta" style="width:fit-content;">{d_txt}</div>'
                f'</div>'
                f'<div style="border-top:1px solid rgba(255,255,255,0.2); margin:12px 0; padding-top:8px;">'
                f'<div class="dep-hl-label">Total Gross Deposits</div>'
                f'<div style="font-size:20px; font-weight:700;">{gross:,}</div>'
                f'</div></div>'
            ), unsafe_allow_html=True)
        
        with c2:
            st.markdown((
                f'<div class="dep-grid">'
                f'{html_dep_mini("Net New Domestic", "Net_New_Dom", m26, m25)}'
                f'{html_dep_mini("Net New Int\'l", "Net_New_Int", m26, m25)}'
                f'{html_dep_mini("Deferred Domestic", "Deferred_Dom", m26, m25)}'
                f'{html_dep_mini("Deferred Int\'l", "Deferred_Int", m26, m25)}'
                f'</div>'
            ), unsafe_allow_html=True)
            
    # 2. FUNNEL GRID
    st.markdown("#### Funnel Progression")
    st.markdown((
        f'<div class="funnel-grid">'
        f'{html_metric_row("Started", "Started", "Started_Dom", "Started_Int", m26, m25)}'
        f'{html_metric_row("Submitted", "Submitted", "Submitted_Dom", "Submitted_Int", m26, m25)}'
        f'{html_metric_row("Completed", "Completed", "Completed_Dom", "Completed_Int", m26, m25)}'
        f'{html_metric_row("Admitted", "Admitted", "Admitted_Dom", "Admitted_Int", m26, m25)}'
        f'</div>'
    ), unsafe_allow_html=True)
    
    # 3. CHARTS
    chart_c1, chart_c2 = st.columns(2)
    with chart_c1:
        # Pacing
        pacing = df_view[(df_view['is_ytd_deposited']==1) & (df_view['is_ytd_deferred']==0)].copy()
        if not pacing.empty:
            agg = pacing.groupby(['term', 'activity_doy'])['id'].count().reset_index().sort_values('activity_doy')
            piv = agg.pivot(index='activity_doy', columns='term', values='id').fillna(0).cumsum().reset_index()
            clean_pacing = piv.melt(id_vars='activity_doy', var_name='term', value_name='count')
            
            fig = px.line(clean_pacing, x='activity_doy', y='count', color='term', title="Net New Deposit Pacing",
                          color_discrete_map={'Fall 2026': '#004F9F', 'Fall 2025': '#94A3B8'})
            fig.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              margin={"l": 20, "r": 20, "t": 40, "b": 20}, height=280)
            st.plotly_chart(fig, use_container_width=True)
            
    with chart_c2:
        # Funnel Bar
        dat = [
            {'Stage': 'Started', 'Val': m26['Started'], 'Term': 'Fall 2026'},
            {'Stage': 'Started', 'Val': m25['Started'], 'Term': 'Fall 2025'},
            {'Stage': 'Submitted', 'Val': m26['Submitted'], 'Term': 'Fall 2026'},
            {'Stage': 'Submitted', 'Val': m25['Submitted'], 'Term': 'Fall 2025'},
            {'Stage': 'Admitted', 'Val': m26['Admitted'], 'Term': 'Fall 2026'},
            {'Stage': 'Admitted', 'Val': m25['Admitted'], 'Term': 'Fall 2025'},
            {'Stage': 'Net New', 'Val': m26['Net_New_Deposits'], 'Term': 'Fall 2026'},
            {'Stage': 'Net New', 'Val': m25['Net_New_Deposits'], 'Term': 'Fall 2025'}
        ]
        fig2 = px.funnel(pd.DataFrame(dat), x='Val', y='Stage', color='Term', orientation='h', title="Funnel Volume",
                         color_discrete_map={'Fall 2026': '#004F9F', 'Fall 2025': '#94A3B8'})
        fig2.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           margin={"l": 20, "r": 20, "t": 40, "b": 20}, height=280, legend={"orientation": "h", "y": -0.2})
        st.plotly_chart(fig2, use_container_width=True)


# --- RENDER LOGIC: SMART TABS VS SINGLE PROGRAM ---
if sel == "All Programs":
    # Show Tabs
    st.caption("View by Program Category:")
    t_mba, t_online, t_spec = st.tabs(["MBA", "Online Programs", "Specialized Masters"])
    with t_mba: render_view(df_filt[df_filt['category'] == 'MBA'])
    with t_online: render_view(df_filt[df_filt['category'] == 'Online'])
    with t_spec: render_view(df_filt[df_filt['category'] == 'Specialized Masters'])
else:
    # Single Program Mode - No Tabs, just show the data
    st.markdown(f"### Performance: {sel}")
    render_view(df_filt)
