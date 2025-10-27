import streamlit as st
from design_system_google import inject_google_css, GOOGLE_COLORS, TYPOGRAPHY, SPACING, RADIUS

inject_google_css()

# 顶部横幅 - 修复布局
st.markdown(f"""<div style="background:{GOOGLE_COLORS['bg_secondary']};padding:{SPACING['3']} {SPACING['6']};display:flex;gap:{SPACING['8']};border-bottom:1px solid {GOOGLE_COLORS['border']};margin:-60px -60px {SPACING['6']} -60px;">
<div style="display:flex;align-items:center;gap:{SPACING['2']};white-space:nowrap;">
<span style="color:{GOOGLE_COLORS['text_secondary']};font-weight:500;">BTC</span>
<span style="color:{GOOGLE_COLORS['text_primary']};font-weight:400;">$67,245.32</span>
<span style="color:{GOOGLE_COLORS['green']};font-size:14px;">▲ +2.14%</span>
<span style="color:{GOOGLE_COLORS['green']};font-size:14px;">+$1,409</span>
</div>
<div style="display:flex;align-items:center;gap:{SPACING['2']};white-space:nowrap;">
<span style="color:{GOOGLE_COLORS['text_secondary']};font-weight:500;">ETH</span>
<span style="color:{GOOGLE_COLORS['text_primary']};font-weight:400;">$2,584.67</span>
<span style="color:{GOOGLE_COLORS['red']};font-size:14px;">▼ -0.82%</span>
<span style="color:{GOOGLE_COLORS['red']};font-size:14px;">-$21.34</span>
</div>
</div>""", unsafe_allow_html=True)

# 搜索框 - 修复样式
st.markdown(f"""<div style="max-width:720px;margin:{SPACING['8']} auto {SPACING['10']} auto;">
<input type="text" placeholder="搜索股票、加密货币、ETF等" style="width:100%;padding:{SPACING['4']} {SPACING['4']} {SPACING['4']} 48px;font-size:14px;font-family:'Google Sans','Roboto',sans-serif;border:1px solid {GOOGLE_COLORS['border']};border-radius:24px;background:{GOOGLE_COLORS['bg_primary']};color:{GOOGLE_COLORS['text_primary']};outline:none;box-sizing:border-box;" />
</div>""", unsafe_allow_html=True)

# 两栏布局
col1, col2 = st.columns([7, 3])

with col1:
    st.markdown(f"""<h2 style="font-size:22px;font-weight:400;color:{GOOGLE_COLORS['text_primary']};margin:0 0 {SPACING['4']} 0;letter-spacing:-0.5px;">列表中变动幅度最大的标的</h2>""", unsafe_allow_html=True)
    
    assets = [
        {"symbol": "AMD", "name": "AMD", "price": 252.92, "change_abs": 17.93, "change_pct": 7.63, "color": "#FF6F00"},
        {"symbol": "TSLA", "name": "特斯拉汽车", "price": 433.72, "change_abs": -15.26, "change_pct": -3.40, "color": "#CC0000"},
        {"symbol": "GOOG", "name": "Alphabet", "price": 260.51, "change_abs": 6.78, "change_pct": 2.67, "color": "#1A73E8"},
        {"symbol": "NVDA", "name": "英伟达", "price": 186.26, "change_abs": 4.10, "change_pct": 2.25, "color": "#76B900"},
    ]
    
    for a in assets:
        pos = a["change_pct"] >= 0
        c = GOOGLE_COLORS["green"] if pos else GOOGLE_COLORS["red"]
        bg = GOOGLE_COLORS["green_bg"] if pos else GOOGLE_COLORS["red_bg"]
        arrow = "▲" if pos else "▼"
        
        st.markdown(f"""<div style="display:flex;align-items:center;padding:{SPACING['4']} 0;border-bottom:1px solid {GOOGLE_COLORS['bg_secondary']};cursor:pointer;transition:background 150ms;" onmouseover="this.style.background='{GOOGLE_COLORS['bg_secondary']}'" onmouseout="this.style.background='transparent'">
<div style="background:{a['color']};color:white;padding:{SPACING['1']} {SPACING['2']};border-radius:4px;font-size:11px;font-weight:700;min-width:65px;text-align:center;">{a['symbol']}</div>
<div style="flex:1;margin-left:{SPACING['3']};font-size:14px;color:{GOOGLE_COLORS['text_primary']};">{a['name']}</div>
<div style="text-align:right;margin-right:{SPACING['8']};font-size:16px;color:{GOOGLE_COLORS['text_primary']};font-weight:400;">${a['price']:,.2f}</div>
<div style="display:inline-block;background:{bg};color:{c};padding:{SPACING['1']} {SPACING['2']};border-radius:4px;font-size:13px;font-weight:500;min-width:140px;text-align:center;">{arrow} {abs(a['change_abs']):,.2f} ({abs(a['change_pct']):.2f}%)</div>
<div style="margin-left:{SPACING['3']};color:{GOOGLE_COLORS['text_secondary']};font-size:20px;">✓</div>
</div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div style="background:{GOOGLE_COLORS['bg_primary']};border:1px solid {GOOGLE_COLORS['border']};border-radius:8px;padding:{SPACING['5']};margin-bottom:{SPACING['4']};">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:{SPACING['4']};">
<h3 style="font-size:16px;font-weight:400;color:{GOOGLE_COLORS['text_primary']};margin:0;">您的投资组合</h3>
<span style="font-size:20px;cursor:pointer;">👁️</span>
</div>
<div style="font-size:12px;color:{GOOGLE_COLORS['text_secondary']};margin-bottom:{SPACING['3']};">只有您可以看到这项信息</div>
<div style="font-size:28px;font-weight:400;color:{GOOGLE_COLORS['text_primary']};margin-bottom:{SPACING['4']};letter-spacing:2px;">$ • • • • • •</div>
<div style="font-size:12px;color:{GOOGLE_COLORS['text_secondary']};margin-bottom:{SPACING['5']};">财富通路<br/>• • • • •</div>
<button style="border:1px solid {GOOGLE_COLORS['blue']};color:{GOOGLE_COLORS['blue']};background:transparent;padding:{SPACING['2']} {SPACING['4']};border-radius:4px;width:100%;cursor:pointer;font-size:14px;font-weight:500;transition:background 150ms;" onmouseover="this.style.background='{GOOGLE_COLORS['blue_bg']}'" onmouseout="this.style.background='transparent'">+ 创建投资组合</button>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div style="margin-top:{SPACING['10']};padding:{SPACING['4']};background:{GOOGLE_COLORS['green_bg']};border-left:4px solid {GOOGLE_COLORS['green']};border-radius:4px;">
<div style="font-size:14px;color:{GOOGLE_COLORS['green_dark']};font-weight:500;">✅ Google Finance UI 运行中 - 已修复所有布局问题</div>
</div>""", unsafe_allow_html=True)
