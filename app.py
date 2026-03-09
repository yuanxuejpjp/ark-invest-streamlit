"""
ARK Invest 持仓追踪系统 - 汉化版
ARK Invest Holdings Tracker - Chinese Version
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# 页面配置
st.set_page_config(
    page_title="ARK Invest 持仓追踪",
    page_icon="📈",
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
    st.markdown('<div class="main-header">📈 ARK Invest 持仓追踪系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">实时追踪 Cathie Wood 的 ARK 基金持仓与交易动态</div>', unsafe_allow_html=True)

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.image("https://ark-funds.com/wp-content/uploads/2020/03/ARK-Logo.png", width=200)
        st.title("🔍 导航菜单")
        
        page = st.radio(
            "选择功能",
            ["🏠 首页", "📊 持仓分析", "💹 交易动态", "🔎 股票查询", "📚 关于 ARK"]
        )
        
        st.divider()
        
        # 基金选择
        st.subheader("📌 选择基金")
        selected_fund = st.selectbox(
            "ARK 基金",
            options=list(FUNDS_INFO.keys()),
            format_func=lambda x: f"{x} - {FUNDS_INFO[x]['name_cn']}"
        )
        
        st.divider()
        
        # 数据说明
        st.info("""
        **数据说明**
        - 数据来源: arkfunds.io API
        - 更新频率: 每日更新
        - 延迟: T+1
        """)
        
        return page, selected_fund

def render_home():
    """渲染首页"""
    st.markdown("""
    ## 🎯 欢迎来到 ARK Invest 持仓追踪系统
    
    这是一个**非官方**的 ARK Invest 数据追踪平台，帮助您：
    
    - 📊 **实时持仓分析** - 查看各基金的最新持仓情况
    - 💹 **交易动态追踪** - 了解最新的买入卖出操作
    - 🔎 **股票深度查询** - 查询特定股票在 ARK 组合中的情况
    - 📈 **可视化展示** - 直观的图表展示持仓分布和趋势
    
    ### 🚀 快速开始
    1. 在左侧选择您感兴趣的 ARK 基金
    2. 点击上方导航栏查看不同功能
    3. 探索数据，发现投资机会
    
    ### ⚠️ 免责声明
    本网站提供的数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。
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
    st.header("📚 关于 ARK Invest")
    
    st.markdown("""
    ### 🌟 ARK Invest 简介
    
    **ARK Invest**（方舟投资）是一家成立于 2014 年的美国资产管理公司，由 **Cathie Wood**（凯瑟琳·伍德）创立。
    
    #### 📌 投资理念
    ARK Invest 专注于**颠覆性创新**领域，认为创新是未来增长的主要驱动力。他们的投资主题包括：
    
    - 🤖 **人工智能与自动化**
    - 🧬 **基因技术**（基因编辑、分子诊断、干细胞治疗）
    - 🚀 **太空探索**
    - 💰 **金融科技**
    - 🌐 **下一代互联网**
    
    #### 👩‍💼 关于 Cathie Wood
    Cathie Wood 是 ARK Invest 的创始人兼 CEO，被誉为"女版巴菲特"。她以对科技股的前瞻性投资而闻名，
    特别是在 Tesla、Coinbase、Roku 等公司的早期投资上取得了巨大成功。
    
    #### 📊 ARK 的透明文化
    ARK Invest 以其高度透明而著称：
    - 每日公布所有交易活动
    - 定期发布研究报告和市场评论
    - 通过 YouTube 等平台分享投资观点
    
    #### ⚠️ 风险提示
    ARK 基金的投资策略具有较高的波动性，主要因为：
    - 重仓高成长科技股
    - 集中度较高（前十大持仓占比大）
    - 创新领域本身具有不确定性
    
    **历史表现**：ARKK 在 2020 年取得了超过 150% 的回报，但在 2021-2022 年也经历了大幅回调。
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

# 主函数
def main():
    render_header()
    page, selected_fund = render_sidebar()
    
    if page == "🏠 首页":
        render_home()
    elif page == "📊 持仓分析":
        render_holdings(selected_fund)
    elif page == "💹 交易动态":
        render_trades(selected_fund)
    elif page == "🔎 股票查询":
        render_stock_search()
    elif page == "📚 关于 ARK":
        render_about()
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>📈 ARK Invest 持仓追踪系统 | 数据来源于 arkfunds.io API</p>
        <p style="font-size: 0.8rem;">⚠️ 免责声明：本网站仅供学习研究使用，不构成投资建议</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
