"""
Design System - 统一设计规范
"""
import streamlit as st

TOKENS = {
    'bg_start': '#0B0B0F',
    'bg_end': '#14141A',
    'panel': '#16161D',
    'panel_border': 'rgba(255,255,255,0.06)',
    'divider': 'rgba(255,255,255,0.08)',
    'accent_start': '#FF6A00',
    'accent_end': '#FFA54C',
    'accent': '#FF7A29',
    'aux': '#75B2B2',
    'text': '#FFFFFF',
    'text_secondary': 'rgba(255,255,255,0.78)',
    'text_weak': 'rgba(255,255,255,0.56)',
    'shadow': '0 8px 40px rgba(0,0,0,0.45)',
    'glow': '0 0 24px rgba(255,140,64,0.35)',
}

def inject_css():
    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root {{
        --bg:{TOKENS['bg_start']};--bg-end:{TOKENS['bg_end']};--panel:{TOKENS['panel']};
        --panel-border:{TOKENS['panel_border']};--divider:{TOKENS['divider']};
        --accent:{TOKENS['accent']};--accent-start:{TOKENS['accent_start']};--accent-end:{TOKENS['accent_end']};
        --aux:{TOKENS['aux']};--text:{TOKENS['text']};--text-weak:{TOKENS['text_weak']};
        --shadow:{TOKENS['shadow']};--glow:{TOKENS['glow']};
    }}
    *{{font-variant-numeric:tabular-nums}}
    body{{font-family:'Inter','Noto Sans SC',sans-serif;background:linear-gradient(135deg,var(--bg),var(--bg-end));color:var(--text)}}
    .main{{background:transparent;padding:1.5rem 2rem}}
    .block-container{{max-width:1400px;padding:1.5rem 0}}
    [data-testid="stSidebar"]{{background:linear-gradient(180deg,var(--bg-end),var(--bg));border-right:1px solid var(--panel-border)}}
    [data-testid="stSidebar"]>div:first-child{{padding:1.5rem 1rem}}
    .icon svg{{display:inline-block;vertical-align:middle;width:1em;height:1em}}
    .card{{background:var(--panel);border:1px solid var(--panel-border);border-radius:18px;padding:1.5rem;box-shadow:var(--shadow);transition:all 0.25s cubic-bezier(0.22,1,0.36,1)}}
    .card:hover{{transform:translateY(-3px);box-shadow:var(--shadow),var(--glow)}}
    .stButton>button{{background:linear-gradient(135deg,var(--accent-start),var(--accent-end));color:white;border:none;border-radius:12px;padding:0.75rem 2rem;font-weight:600;transition:all 0.25s cubic-bezier(0.22,1,0.36,1)}}
    .stButton>button:hover{{transform:translateY(-2px);box-shadow:0 6px 24px rgba(255,106,0,0.4)}}
    .stButton>button:active{{transform:translateY(0)}}
    .pill-badge{{display:inline-flex;padding:0.35rem 0.75rem;border-radius:999px;font-size:0.85rem;font-weight:600}}
    .pill-accent{{background:rgba(255,106,0,0.15);color:var(--accent)}}
    .pill-neutral{{background:rgba(255,255,255,0.1);color:var(--text-weak)}}
    .pill-critical{{background:rgba(239,83,80,0.15);color:#EF5350}}
    .pill-success{{background:rgba(76,175,80,0.15);color:#4CAF50}}
    .kpi-card{{background:var(--panel);border:1px solid var(--panel-border);border-radius:18px;padding:1.5rem;text-align:center;transition:all 0.25s cubic-bezier(0.22,1,0.36,1)}}
    .kpi-card:hover{{transform:translateY(-3px)}}
    .kpi-value{{font-size:2.5rem;font-weight:700;line-height:1.2;margin:0.5rem 0}}
    .kpi-label{{color:var(--text-weak);font-size:0.9rem;font-weight:500}}
    .positive{{color:#4CAF50}}.negative{{color:#EF5350}}
    .dataframe{{background:var(--panel);border-radius:18px;border:1px solid var(--panel-border);overflow:hidden}}
    .dataframe thead tr{{background:rgba(255,255,255,0.03);color:var(--text-weak)}}
    .dataframe tbody tr:nth-child(even){{background:rgba(255,255,255,0.02)}}
    .dataframe tbody tr:hover{{background:rgba(255,255,255,0.05);transform:translateY(-1px)}}
    .stTabs [data-baseweb="tab-list"]{{gap:1rem;background:transparent;border-bottom:1px solid var(--divider)}}
    .stTabs [data-baseweb="tab"]{{background:transparent;color:var(--text-weak);border:none;padding:0.75rem 1.5rem;font-weight:600;position:relative}}
    .stTabs [data-baseweb="tab"]::after{{content:'';position:absolute;bottom:-1px;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent-start),var(--accent-end));transform:scaleX(0);transition:transform 0.3s cubic-bezier(0.22,1,0.36,1)}}
    .stTabs [data-baseweb="tab"][aria-selected="true"]{{color:var(--accent)}}
    .stTabs [data-baseweb="tab"][aria-selected="true"]::after{{transform:scaleX(1)}}
    [data-testid="stMetric"]{{background:var(--panel);border:1px solid var(--panel-border);border-radius:18px;padding:1.5rem}}
    .stTextInput>div>div>input,.stSelectbox>div>div>select{{background:rgba(255,255,255,0.05);border:1px solid var(--panel-border);border-radius:12px;color:var(--text);padding:0.75rem 1rem}}
    .stTextInput>div>div>input:focus,.stSelectbox>div>div>select:focus{{border-color:var(--accent);box-shadow:0 0 0 2px rgba(255,122,41,0.2)}}
    ::-webkit-scrollbar{{width:8px;height:8px}}
    ::-webkit-scrollbar-track{{background:var(--bg)}}
    ::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.2);border-radius:4px}}
    ::-webkit-scrollbar-thumb:hover{{background:var(--accent)}}
    *:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
    @keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
    @keyframes slideIn{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
    .fade-in{{animation:fadeIn 0.25s cubic-bezier(0.22,1,0.36,1)}}
    .slide-in{{animation:slideIn 0.3s cubic-bezier(0.22,1,0.36,1)}}
    #MainMenu{{visibility:hidden}}footer{{visibility:hidden}}
    </style>""", unsafe_allow_html=True)
