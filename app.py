"""
聪明钱持仓追踪系统
Smart Money Holdings Tracker
追踪全球顶级投资大师的持仓动向
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from institutions_13f import (
    get_institution_list, get_institution_data_live, get_available_quarters,
    INSTITUTIONS, BUILTIN_HOLDINGS
)

# 页面配置
st.set_page_config(
    page_title="聪明钱持仓追踪",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #888;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #1E1E2E;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
    }
    .info-box {
        background-color: #1E1E2E;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ARK 基金配置
FUNDS_INFO = {
    "ARKK": {
        "name": "ARK Innovation ETF",
        "name_cn": "ARK 创新 ETF",
        "description": "主动管理型ETF，投资颠覆性创新领域的公司",
        "color": "#FF6B6B"
    },
    "ARKQ": {
        "name": "ARK Autonomous Tech. & Robotics ETF",
        "name_cn": "ARK 自动驾驶与机器人 ETF",
        "description": "投资自动驾驶、机器人和自动化技术",
        "color": "#4ECDC4"
    },
    "ARKW": {
        "name": "ARK Next Generation Internet ETF",
        "name_cn": "ARK 下一代互联网 ETF",
        "description": "投资下一代互联网技术，包括AI和区块链",
        "color": "#45B7D1"
    },
    "ARKG": {
        "name": "ARK Genomic Revolution ETF",
        "name_cn": "ARK 基因革命 ETF",
        "description": "投资基因编辑、分子诊断和干细胞治疗",
        "color": "#96CEB4"
    },
    "ARKF": {
        "name": "ARK Fintech Innovation ETF",
        "name_cn": "ARK 金融科技 ETF",
        "description": "投资金融科技创新的公司",
        "color": "#FFEAA7"
    },
    "ARKX": {
        "name": "ARK Space Exploration & Innovation ETF",
        "name_cn": "ARK 太空探索 ETF",
        "description": "投资太空探索和航天技术",
        "color": "#DDA0DD"
    },
    "ARKB": {
        "name": "ARK 21Shares Bitcoin ETF",
        "name_cn": "ARK 比特币 ETF",
        "description": "投资比特币的ETF",
        "color": "#F7931A"
    },
    "PRNT": {
        "name": "The 3D Printing ETF",
        "name_cn": "3D 打印 ETF",
        "description": "投资3D打印技术的公司",
        "color": "#A8E6CF"
    },
}

# API 基础URL
API_BASE_URL = "https://arkfunds.io/api/v2"

@st.cache_data(ttl=3600)
def fetch_etf_holdings(symbol, limit=50):
    """获取ETF持仓数据"""
    try:
        url = f"{API_BASE_URL}/etf/holdings"
        params = {"symbol": symbol, "limit": limit}
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_etf_trades(symbol, limit=50):
    """获取ETF交易数据"""
    try:
        url = f"{API_BASE_URL}/etf/trades"
        params = {"symbol": symbol, "limit": limit}
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_etf_profile(symbol):
    """获取ETF档案"""
    try:
        url = f"{API_BASE_URL}/etf/profile"
        params = {"symbol": symbol}
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_stock_price(symbol):
    """获取股票价格"""
    try:
        url = f"{API_BASE_URL}/stock/price"
        params = {"symbol": symbol}
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def render_header():
    """渲染头部"""
    st.markdown('<div class="main-header">💰 聪明钱持仓追踪系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">追踪巴菲特、段永平、李路等投资大师的持仓动向</div>', unsafe_allow_html=True)

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.image("https://ark-funds.com/wp-content/uploads/2020/03/ARK-Logo.png", width=200)
        st.title("🔍 导航菜单")
        
        page = st.radio(
            "选择功能",
            ["🏠 首页", "📊 ARK持仓", "💹 ARK交易", "🏛️ 聪明钱持仓", "🔎 股票查询", "📚 关于系统"]
        )
        
        st.divider()
        
        # 基金选择
        st.subheader("📌 选择ARK基金")
        selected_fund = st.selectbox(
            "ARK 基金",
            options=list(FUNDS_INFO.keys()),
            format_func=lambda x: f"{x} - {FUNDS_INFO[x]['name_cn']}"
        )
        
        st.divider()
        
        # 数据说明
        st.info("""
        **数据说明**
        - ARK数据: arkfunds.io API (每日)
        - 13F数据: SEC EDGAR (季度)
        - 13F延迟: 45天
        """)
        
        # 机构选择（如果是聪明钱持仓页面）
        selected_institution = None
        if page == "🏛️ 聪明钱持仓":
            st.divider()
            st.subheader("🏛️ 选择机构")
            institutions = get_institution_list()
            selected_institution = st.selectbox(
                "顶级投资机构",
                options=list(institutions.keys()),
                format_func=lambda x: f"{x} - {institutions[x]['name']}"
            )
            
            if selected_institution:
                info = institutions[selected_institution]
                st.markdown(f"""
                <div style="background-color: #1E1E2E; padding: 10px; border-radius: 8px; margin-top: 10px;">
                    <p style="margin: 0; font-size: 0.85rem; color: #888;">基金经理</p>
                    <p style="margin: 0; font-weight: bold; color: {info['color']};">{info['manager']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        return page, selected_fund, selected_institution

def render_home():
    """渲染首页"""
    st.markdown("""
    ## 🎯 欢迎来到聪明钱持仓追踪系统
    
    这是一个**非官方**的全球顶级投资大师持仓追踪平台，帮助您：
    
    - 📊 **ARK持仓分析** - 查看 Cathie Wood 的 ARK 基金持仓
    - 💹 **交易动态追踪** - 了解 ARK 最新的买入卖出操作
    - 🏛️ **聪明钱持仓** - 追踪巴菲特、段永平、李路等大师持仓
    - 🔎 **股票深度查询** - 查询特定股票在各机构组合中的情况
    - 📈 **可视化展示** - 直观的图表展示持仓分布和趋势
    
    ### 🚀 快速开始
    1. 在左侧选择您感兴趣的基金或机构
    2. 点击上方导航栏查看不同功能
    3. 探索数据，发现投资机会
    
    ### ⚠️ 免责声明
    本网站提供的数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。
    数据来源于 SEC EDGAR 13F 报告和 arkfunds.io API。
    """)
    
    # 展示所有基金卡片
    st.subheader("🌟 ARK 基金概览")
    
    cols = st.columns(4)
    for idx, (symbol, info) in enumerate(FUNDS_INFO.items()):
        with cols[idx % 4]:
            with st.container():
                st.markdown(f"""
                <div style="background-color: #1E1E2E; padding: 15px; border-radius: 10px; 
                            border-left: 4px solid {info['color']}; margin: 10px 0;">
                    <h4 style="color: {info['color']}; margin: 0;">{symbol}</h4>
                    <p style="font-size: 0.9rem; margin: 5px 0;">{info['name_cn']}</p>
                    <p style="font-size: 0.75rem; color: #888;">{info['description'][:30]}...</p>
                </div>
                """, unsafe_allow_html=True)

def render_holdings(fund):
    """渲染持仓分析"""
    st.header(f"📊 {fund} - {FUNDS_INFO[fund]['name_cn']} 持仓分析")
    
    # 获取数据
    data = fetch_etf_holdings(fund, limit=50)
    
    if not data or not data.get('holdings'):
        st.warning("暂无持仓数据")
        return
    
    holdings = data['holdings']
    df = pd.DataFrame(holdings)
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("持仓股票数", len(df))
    with col2:
        total_value = df['market_value'].sum() if 'market_value' in df.columns else 0
        st.metric("总持仓市值", f"${total_value/1e9:.2f}B" if total_value else "N/A")
    with col3:
        st.metric("数据日期", data.get('date_to', 'N/A'))
    with col4:
        top_holding = df.iloc[0]['company'] if len(df) > 0 else 'N/A'
        st.metric("最大持仓", top_holding[:15] + '...' if len(str(top_holding)) > 15 else top_holding)
    
    st.divider()
    
    # 持仓分布图
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 持仓权重分布 TOP 15")
        top15 = df.head(15)
        
        fig = px.bar(
            top15,
            x='weight',
            y='company',
            orientation='h',
            color='weight',
            color_continuous_scale='RdYlBu_r',
            title=f"{fund} 前15大持仓",
            labels={'weight': '权重 (%)', 'company': '公司名称'}
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 持仓占比")
        top10 = df.head(10).copy()
        others_weight = df.iloc[10:]['weight'].sum() if len(df) > 10 else 0
        
        pie_data = top10[['company', 'weight']].copy()
        if others_weight > 0:
            pie_data = pd.concat([
                pie_data,
                pd.DataFrame([{'company': '其他', 'weight': others_weight}])
            ], ignore_index=True)
        
        fig_pie = px.pie(
            pie_data,
            values='weight',
            names='company',
            title=f"{fund} 持仓分布"
        )
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # 详细持仓表格
    st.subheader("📋 详细持仓列表")
    
    # 格式化数据
    display_df = df.copy()
    if 'market_value' in display_df.columns:
        display_df['market_value'] = display_df['market_value'].apply(lambda x: f"${x/1e6:.2f}M" if x else '-')
    if 'weight' in display_df.columns:
        display_df['weight'] = display_df['weight'].apply(lambda x: f"{x:.2f}%" if x else '-')
    if 'shares' in display_df.columns:
        display_df['shares'] = display_df['shares'].apply(lambda x: f"{x:,}" if x else '-')
    
    # 重命名列
    column_names = {
        'company': '公司名称',
        'ticker': '股票代码',
        'shares': '持股数量',
        'market_value': '市值',
        'weight': '权重',
        'weight_rank': '排名'
    }
    display_df = display_df.rename(columns=column_names)
    
    # 选择显示列
    cols_to_show = ['排名', '公司名称', '股票代码', '持股数量', '市值', '权重']
    available_cols = [c for c in cols_to_show if c in display_df.columns]
    
    st.dataframe(
        display_df[available_cols],
        use_container_width=True,
        hide_index=True
    )

def render_trades(fund):
    """渲染交易动态"""
    st.header(f"💹 {fund} - {FUNDS_INFO[fund]['name_cn']} 交易动态")
    
    # 获取数据
    data = fetch_etf_trades(fund, limit=100)
    
    if not data or not data.get('trades'):
        st.warning("暂无交易数据")
        return
    
    trades = data['trades']
    df = pd.DataFrame(trades)
    
    # 交易统计
    col1, col2, col3 = st.columns(3)
    
    buy_count = len(df[df['direction'] == 'Buy']) if 'direction' in df.columns else 0
    sell_count = len(df[df['direction'] == 'Sell']) if 'direction' in df.columns else 0
    
    with col1:
        st.metric("总交易数", len(df))
    with col2:
        st.metric("买入次数", buy_count, delta=buy_count)
    with col3:
        st.metric("卖出次数", sell_count, delta=-sell_count)
    
    st.divider()
    
    # 筛选
    col1, col2 = st.columns(2)
    with col1:
        direction_filter = st.multiselect(
            "交易方向",
            options=['Buy', 'Sell'],
            default=['Buy', 'Sell'],
            format_func=lambda x: "买入" if x == 'Buy' else "卖出"
        )
    with col2:
        if 'date' in df.columns:
            dates = sorted(df['date'].unique(), reverse=True)
            date_filter = st.multiselect("交易日期", options=dates, default=dates[:5] if len(dates) > 5 else dates)
        else:
            date_filter = None
    
    # 筛选数据
    filtered_df = df.copy()
    if direction_filter and 'direction' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['direction'].isin(direction_filter)]
    if date_filter and 'date' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['date'].isin(date_filter)]
    
    st.divider()
    
    # 交易图表
    if len(filtered_df) > 0 and 'date' in filtered_df.columns:
        st.subheader("📊 交易趋势")
        
        # 按日期统计
        trade_counts = filtered_df.groupby(['date', 'direction']).size().reset_index(name='count')
        
        fig = px.bar(
            trade_counts,
            x='date',
            y='count',
            color='direction',
            title=f"{fund} 每日交易次数",
            labels={'date': '日期', 'count': '交易次数', 'direction': '方向'},
            color_discrete_map={'Buy': '#00C853', 'Sell': '#FF1744'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 交易列表
    st.subheader("📋 最近交易记录")
    
    display_df = filtered_df.copy()
    
    # 格式化
    if 'direction' in display_df.columns:
        display_df['direction'] = display_df['direction'].apply(lambda x: '🔥 买入' if x == 'Buy' else '❄️ 卖出')
    if 'shares' in display_df.columns:
        display_df['shares'] = display_df['shares'].apply(lambda x: f"{x:,}")
    if 'fund_percent' in display_df.columns:
        display_df['fund_percent'] = display_df['fund_percent'].apply(lambda x: f"{x:.2f}%" if x else '-')
    
    column_names = {
        'date': '日期',
        'fund': '基金',
        'company': '公司名称',
        'ticker': '股票代码',
        'cusip': 'CUSIP',
        'shares': '股数',
        'direction': '方向',
        'fund_percent': '基金占比'
    }
    display_df = display_df.rename(columns=column_names)
    
    cols_to_show = ['日期', '公司名称', '股票代码', '方向', '股数', '基金占比']
    available_cols = [c for c in cols_to_show if c in display_df.columns]
    
    st.dataframe(
        display_df[available_cols].head(50),
        use_container_width=True,
        hide_index=True
    )

def render_stock_search():
    """渲染股票查询"""
    st.header("🔎 股票深度查询")
    
    stock_symbol = st.text_input("输入股票代码 (如: TSLA, NVDA, COIN)", value="TSLA").upper()
    
    if st.button("🔍 查询", type="primary"):
        with st.spinner("正在获取数据..."):
            price_data = fetch_stock_price(stock_symbol)
            
            if price_data:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("股票代码", price_data.get('symbol', stock_symbol))
                with col2:
                    price = price_data.get('price', 'N/A')
                    st.metric("当前价格", f"${price}" if price != 'N/A' else 'N/A')
                with col3:
                    change = price_data.get('change', 0)
                    changep = price_data.get('changep', 0)
                    st.metric("涨跌额", f"${change}", f"{changep}%")
                with col4:
                    last_trade = price_data.get('last_trade', 'N/A')
                    st.metric("最后交易", last_trade)
            else:
                st.error("无法获取该股票数据")
    
    st.divider()
    
    st.info("""
    **💡 提示**
    - 输入股票代码查询该股票在各 ARK 基金中的持仓情况
    - 支持美股主流股票代码
    - 数据来源于 Yahoo Finance
    """)

def render_about():
    """渲染关于页面"""
    st.header("📚 关于聪明钱持仓追踪系统")
    
    st.markdown("""
    ### 🌟 系统简介
    
    **聪明钱持仓追踪系统**是一个追踪全球顶级投资大师持仓动向的数据平台。
    
    #### 📌 追踪的投资大师
    
    **🇺🇸 美国价值投资派**
    - **沃伦·巴菲特** - 伯克希尔·哈撒韦，价值投资鼻祖
    - **查理·芒格** - 每日期刊公司，巴菲特合伙人
    - **比尔·阿克曼** - 潘兴广场资本，维权投资
    
    **🇨🇳 中国投资大师**
    - **段永平** - H&H投资，重仓苹果、英伟达，"中国巴菲特"
    - **李路** - 喜马拉雅资本，芒格认可的投资人，重仓谷歌
    - **张磊** - 高瓴资本，重仓中概股和医疗
    
    **📊 量化投资**
    - **瑞·达里奥** - 桥水基金，全球最大对冲基金
    
    #### 📈 ARK Invest
    **Cathie Wood**（木头姐）- 专注于颠覆性创新的成长股投资者
    
    #### ⚠️ 数据说明
    - **ARK数据**：每日更新，来源于 arkfunds.io API
    - **13F数据**：季度更新，来源于 SEC EDGAR
    - **披露延迟**：13F报告有45天延迟，实际交易比报告早1.5-2个月
    
    #### 💡 使用建议
    聪明钱的持仓可以作为投资参考，但请注意：
    - 不要盲从，要有自己的判断
    - 考虑持仓成本和时间差
    - 了解每位投资大师的投资风格和策略
    """)
    
    # 外部链接
    st.subheader("🔗 相关链接")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.link_button("🏠 ARK 官网", "https://ark-funds.com")
    with col2:
        st.link_button("📺 YouTube", "https://www.youtube.com/c/ARKInvest")
    with col3:
        st.link_button("💻 GitHub", "https://github.com/frefrik/ark-invest-api")

def render_institutions(selected_institution):
    """渲染机构持仓页面 - 13F 季度报告
    打开页面时实时检查 SEC 是否有新数据
    """
    
    institutions = get_institution_list()
    info = institutions[selected_institution]
    
    # ========== 实时数据检查 ==========
    with st.spinner(f"🔍 正在检查 {info['name']} 的最新 13F 报告..."):
        data, quarter, status_msg = get_institution_data_live(selected_institution)
    
    if not data:
        st.error("❌ 无法获取数据")
        return
    
    # 显示数据状态
    col_status1, col_status2, col_btn = st.columns([2, 2, 1])
    
    with col_status1:
        # 根据状态显示不同颜色
        if "已是最新" in status_msg or "历史数据" in status_msg:
            st.success(f"✅ {status_msg}")
        elif "有新报告" in status_msg:
            st.warning(f"⚠️ {status_msg}")
        else:
            st.info(f"ℹ️ {status_msg}")
    
    with col_status2:
        st.caption(f"📅 当前数据季度: {data.get('quarter', 'N/A')} | 报告日期: {data.get('filing_date', 'N/A')}")
    
    with col_btn:
        if st.button("🔄 重新检查", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # 头部
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem; margin-top: 1rem;">
        <h1 style="color: {info['color']}; margin-bottom: 0.5rem;">🏛️ {info['name']}</h1>
        <p style="color: #888; font-size: 1.1rem;">{info['name_en']} | 基金经理: {info['manager']}</p>
        <p style="color: #666; font-size: 0.9rem; max-width: 600px; margin: 0 auto;">{info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 关键指标卡片
    st.subheader("📊 关键指标")
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("💰 现金比例", f"{info['cash_ratio']}%", 
                 delta="极高" if info['cash_ratio'] > 30 else "正常" if info['cash_ratio'] > 10 else "低")
    with cols[1]:
        st.metric("📈 管理规模", f"${info['aum']}B")
    with cols[2]:
        top10 = data.get('top10_weight', 0)
        st.metric("🎯 前10集中度", f"{top10}%", 
                 delta="高度集中" if top10 > 70 else "适中" if top10 > 40 else "分散")
    with cols[3]:
        st.metric("📅 报告日期", data.get('filing_date', 'N/A'))
    
    st.divider()
    
    # 现金 vs 股票饼图
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💵 资产配置")
        cash_ratio = info['cash_ratio']
        stock_ratio = 100 - cash_ratio
        
        fig = go.Figure(data=[go.Pie(
            labels=['股票持仓', '现金储备'],
            values=[stock_ratio, cash_ratio],
            hole=0.4,
            marker_colors=[info['color'], '#4B5563'],
            textinfo='label+percent',
            textfont_size=14
        )])
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 本季度调仓概况")
        changes = data.get('changes_summary', {})
        
        if changes:
            change_df = pd.DataFrame([
                {'操作': k, '数量': v} 
                for k, v in changes.items()
            ])
            
            colors = {'新建仓': '#00C853', '增持': '#64DD17', '持平': '#9E9E9E', 
                     '减持': '#FF9800', '清仓': '#FF1744'}
            
            fig = px.bar(change_df, x='操作', y='数量', color='操作',
                        color_discrete_map=colors,
                        title=f"{quarter} 调仓统计")
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无调仓数据")
    
    st.divider()
    
    # 持仓列表
    st.subheader(f"📋 {quarter} 持仓详情")
    
    holdings = data.get('holdings', [])
    if holdings:
        df = pd.DataFrame(holdings)
        
        # 格式化显示
        display_df = df.copy()
        display_df['value'] = display_df['value'].apply(lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else f"${x/1e6:.0f}M")
        display_df['weight'] = display_df['weight'].apply(lambda x: f"{x:.1f}%")
        display_df['shares'] = display_df['shares'].apply(lambda x: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
        
        # 变化颜色标记
        def color_change(val):
            if isinstance(val, str):
                if '增持' in val or '新建仓' in val:
                    return 'color: #00C853'
                elif '减持' in val or '清仓' in val:
                    return 'color: #FF1744'
            return ''
        
        display_df = display_df.rename(columns={
            'ticker': '代码',
            'company': '公司名称',
            'shares': '持股数',
            'value': '市值',
            'weight': '权重',
            'change': '变化'
        })
        
        st.dataframe(
            display_df[['代码', '公司名称', '持股数', '市值', '权重', '变化']].style.map(color_change, subset=['变化']),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # 持仓权重图
        st.subheader("📈 持仓权重分布")
        
        fig = px.bar(
            df.head(15),
            x='weight',
            y='company',
            orientation='h',
            color='weight',
            color_continuous_scale=[(0, info['color']), (1, info['color'])],
            title=f"前15大持仓 - {quarter}",
            labels={'weight': '权重 (%)', 'company': '公司名称'}
        )
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # 机构对比
    st.divider()
    st.subheader("🏛️ 顶级机构现金储备对比")
    
    comparison_data = []
    for code, inst in institutions.items():
        comparison_data.append({
            '机构': inst['name'],
            '现金比例': inst['cash_ratio'],
            '基金经理': inst['manager'],
            '颜色': inst['color']
        })
    
    comp_df = pd.DataFrame(comparison_data).sort_values('现金比例', ascending=True)
    
    fig = px.bar(
        comp_df,
        x='现金比例',
        y='机构',
        orientation='h',
        color='基金经理',
        title="各机构现金储备比例（%）",
        labels={'现金比例': '现金比例 (%)', '机构': ''}
    )
    fig.update_layout(height=350)
    fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="高现金警戒线")
    st.plotly_chart(fig, use_container_width=True)
    
    # 说明
    st.info("""
    **📌 关于 13F 报告说明**
    - 13F 报告是美国 SEC 要求机构每季度披露的投资持仓报告
    - 披露截止日期：季度结束后 45 天内
    - 数据延迟：比实际交易晚 1.5-2 个月
    - 只披露多头持仓，不包括空头和衍生品
    - 现金比例为估算值，来自各机构财报
    """)

# 主函数
def main():
    render_header()
    result = render_sidebar()
    
    # 处理返回值（可能是2个或3个）
    if len(result) == 3:
        page, selected_fund, selected_institution = result
    else:
        page, selected_fund = result
        selected_institution = None
    
    if page == "🏠 首页":
        render_home()
    elif page == "📊 持仓分析":
        render_holdings(selected_fund)
    elif page == "💹 交易动态":
        render_trades(selected_fund)
    elif page == "🏛️ 聪明钱持仓":
        render_institutions(selected_institution)
    elif page == "🔎 股票查询":
        render_stock_search()
    elif page == "📚 关于系统":
        render_about()
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>💰 聪明钱持仓追踪系统 | 数据来源于 SEC EDGAR & arkfunds.io</p>
        <p style="font-size: 0.8rem;">⚠️ 免责声明：本网站仅供学习研究使用，不构成投资建议</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
