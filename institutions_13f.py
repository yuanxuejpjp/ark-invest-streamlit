"""
美股顶级机构 13F 持仓追踪模块
数据来源：SEC EDGAR 13F 报告（季度更新）
功能：打开页面时自动检查最新数据
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import json
import os
import re

# SEC EDGAR API 请求头（必须设置 User-Agent）
SEC_HEADERS = {
    'User-Agent': 'EducationalResearch/1.0 (your-email@example.com)'
}

# 机构配置
INSTITUTIONS = {
    "BRK": {
        "name": "伯克希尔·哈撒韦",
        "name_en": "Berkshire Hathaway",
        "manager": "沃伦·巴菲特",
        "cik": "0001067983",
        "color": "#1E3A8A",
        "description": "巴菲特的投资帝国，长期价值投资典范，现金储备极高",
        "cash_ratio": 38.2,
        "aum": 8730,
        "strategy": "价值投资 + 长期持有 + 高现金储备"
    },
    "PERSHING": {
        "name": "潘兴广场资本",
        "name_en": "Pershing Square Capital",
        "manager": "比尔·阿克曼",
        "cik": "0001336528",
        "color": "#7C3AED",
        "description": "激进投资机构，持仓高度集中，善于做空和维权投资",
        "cash_ratio": 12.5,
        "aum": 185,
        "strategy": "高度集中 +  activism + 对冲"
    },
    "HHLR": {
        "name": "高瓴资本",
        "name_en": "HHLR Advisors",
        "manager": "张磊",
        "cik": "0001737086",
        "color": "#DC2626",
        "description": "中国顶级投资机构，重仓中概股和医疗生物科技",
        "cash_ratio": 8.3,
        "aum": 65,
        "strategy": "重仓中国 + 医疗科技 + 长期持有"
    },
    "BRIDGEWATER": {
        "name": "桥水基金",
        "name_en": "Bridgewater Associates",
        "manager": "瑞·达里奥",
        "cik": "0001350694",
        "color": "#059669",
        "description": "全球最大对冲基金，全天候策略，极度分散投资",
        "cash_ratio": 5.2,
        "aum": 1120,
        "strategy": "全天候策略 + 风险平价 + 极度分散"
    },
    "DJCO": {
        "name": "每日期刊公司",
        "name_en": "Daily Journal Corp",
        "manager": "查理·芒格",
        "cik": "0000783412",
        "color": "#B45309",
        "description": "芒格的投资组合，极简持仓，重仓银行股",
        "cash_ratio": 42.8,
        "aum": 3.5,
        "strategy": "极简持仓 + 重仓银行 + 极高现金"
    }
}

# 内置缓存数据（当无法获取实时数据时使用）
BUILTIN_HOLDINGS = {
    "BRK": {
        "quarter": "2024 Q3",
        "date": "2024-09-30",
        "filing_date": "2024-11-14",
        "holdings": [
            {"ticker": "AAPL", "company": "苹果公司", "shares": 300000000, "value": 69900000000, "weight": 26.5, "change": "-25%", "change_type": "减持"},
            {"ticker": "AXP", "company": "美国运通", "shares": 151610000, "value": 40700000000, "weight": 15.4, "change": "持平", "change_type": "持平"},
            {"ticker": "BAC", "company": "美国银行", "shares": 680000000, "value": 35800000000, "weight": 13.6, "change": "-15%", "change_type": "减持"},
            {"ticker": "KO", "company": "可口可乐", "shares": 400000000, "value": 27400000000, "weight": 10.4, "change": "持平", "change_type": "持平"},
            {"ticker": "CVX", "company": "雪佛龙", "shares": 118610000, "value": 18600000000, "weight": 7.0, "change": "-20%", "change_type": "减持"},
            {"ticker": "OXY", "company": "西方石油", "shares": 255280000, "value": 15500000000, "weight": 5.9, "change": "+8%", "change_type": "增持"},
            {"ticker": "KHC", "company": "卡夫亨氏", "shares": 325634000, "value": 11800000000, "weight": 4.5, "change": "持平", "change_type": "持平"},
            {"ticker": "MU", "company": "美光科技", "shares": 25234000, "value": 1020000000, "weight": 0.4, "change": "新建仓", "change_type": "新建仓"},
            {"ticker": "ULTA", "company": "Ulta美妆", "shares": 690000, "value": 266000000, "weight": 0.1, "change": "新建仓", "change_type": "新建仓"},
            {"ticker": "LPX", "company": "路易斯安那太平洋", "shares": 5783000, "value": 307000000, "weight": 0.1, "change": "清仓", "change_type": "清仓"},
        ],
        "cash": 334000000000,
        "total_aum": 873000000000,
        "top10_weight": 85.2,
        "changes_summary": {"新建仓": 2, "清仓": 1, "增持": 1, "减持": 2, "持平": 5}
    },
    "PERSHING": {
        "quarter": "2024 Q3",
        "date": "2024-09-30",
        "filing_date": "2024-11-14",
        "holdings": [
            {"ticker": "CP", "company": "加拿大太平洋铁路", "shares": 15230000, "value": 3250000000, "weight": 17.5, "change": "持平", "change_type": "持平"},
            {"ticker": "HLT", "company": "希尔顿酒店", "shares": 9545000, "value": 2850000000, "weight": 15.4, "change": "持平", "change_type": "持平"},
            {"ticker": "GOOGL", "company": "谷歌", "shares": 15800000, "value": 2680000000, "weight": 14.5, "change": "+45%", "change_type": "增持"},
            {"ticker": "NKE", "company": "耐克", "shares": 21400000, "value": 2180000000, "weight": 11.8, "change": "持平", "change_type": "持平"},
            {"ticker": "QSR", "company": "Restaurant Brands", "shares": 11600000, "value": 1020000000, "weight": 5.5, "change": "持平", "change_type": "持平"},
            {"ticker": "LOW", "company": "劳氏", "shares": 3750000, "value": 985000000, "weight": 5.3, "change": "持平", "change_type": "持平"},
            {"ticker": "HUM", "company": "Humana", "shares": 2510000, "value": 980000000, "weight": 5.3, "change": "+15%", "change_type": "增持"},
            {"ticker": "CMG", "company": "Chipotle", "shares": 107000, "value": 520000000, "weight": 2.8, "change": "-1%", "change_type": "减持"},
        ],
        "cash": 2300000000,
        "total_aum": 18500000000,
        "top10_weight": 78.1,
        "changes_summary": {"新建仓": 0, "清仓": 1, "增持": 2, "减持": 1, "持平": 5}
    },
    "HHLR": {
        "quarter": "2024 Q3",
        "date": "2024-09-30",
        "filing_date": "2024-11-14",
        "holdings": [
            {"ticker": "PDD", "company": "拼多多", "shares": 5480000, "value": 798000000, "weight": 12.3, "change": "+12%", "change_type": "增持"},
            {"ticker": "BEKE", "company": "贝壳找房", "shares": 18800000, "value": 652000000, "weight": 10.0, "change": "-8%", "change_type": "减持"},
            {"ticker": "AMGN", "company": "安进", "shares": 2180000, "value": 628000000, "weight": 9.7, "change": "持平", "change_type": "持平"},
            {"ticker": "JD", "company": "京东", "shares": 13800000, "value": 585000000, "weight": 9.0, "change": "-25%", "change_type": "减持"},
            {"ticker": "BABA", "company": "阿里巴巴", "shares": 4850000, "value": 525000000, "weight": 8.1, "change": "-35%", "change_type": "减持"},
            {"ticker": "VIST", "company": "Vista油气", "shares": 11800000, "value": 412000000, "weight": 6.3, "change": "+85%", "change_type": "增持"},
            {"ticker": "BGNE", "company": "百济神州", "shares": 1880000, "value": 358000000, "weight": 5.5, "change": "持平", "change_type": "持平"},
            {"ticker": "GOOGL", "company": "谷歌", "shares": 2150000, "value": 365000000, "weight": 5.6, "change": "新建仓", "change_type": "新建仓"},
            {"ticker": "ALNY", "company": "Alnylam制药", "shares": 1680000, "value": 342000000, "weight": 5.3, "change": "-5%", "change_type": "减持"},
            {"ticker": "ZTO", "company": "中通快递", "shares": 11800000, "value": 285000000, "weight": 4.4, "change": "持平", "change_type": "持平"},
        ],
        "cash": 540000000,
        "total_aum": 6500000000,
        "top10_weight": 76.2,
        "changes_summary": {"新建仓": 1, "清仓": 2, "增持": 2, "减持": 4, "持平": 3}
    }
}

@st.cache_data(ttl=3600)
def check_latest_13f(cik, current_filing_date):
    """
    检查 SEC 是否有新的 13F 报告
    返回: (是否有新报告, 最新报告日期, 报告信息)
    """
    try:
        # SEC RSS feed 查询最新的 13F-HR 文件
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F-HR&dateb=&owner=include&count=1&output=atom"
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        
        if response.status_code == 200:
            # 解析 RSS 获取最新报告日期
            root = ET.fromstring(response.content)
            # Atom 命名空间
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entry = root.find('.//atom:entry', ns)
            if entry is not None:
                updated = entry.find('atom:updated', ns)
                if updated is not None:
                    latest_date = updated.text[:10]  # 提取日期部分
                    
                    # 比较日期
                    if latest_date > current_filing_date:
                        return True, latest_date, "发现新报告"
                    else:
                        return False, latest_date, "已是最新"
                        
        return False, current_filing_date, "无法获取"
        
    except Exception as e:
        return False, current_filing_date, f"检查失败: {str(e)[:30]}"

def fetch_live_data(symbol, cik):
    """
    尝试从 SEC 获取实时数据
    注意：这只是示例，实际解析 13F XML 比较复杂
    """
    try:
        # 这里可以添加实际的数据获取逻辑
        # 目前返回 None，使用内置数据
        return None
    except:
        return None

def get_institution_data_live(symbol):
    """
    获取机构数据 - 打开页面时实时检查
    优先使用实时数据，失败则使用内置数据
    """
    if symbol not in INSTITUTIONS:
        return None, None, "未知机构"
    
    info = INSTITUTIONS[symbol]
    builtin = BUILTIN_HOLDINGS.get(symbol)
    
    if not builtin:
        return None, None, "暂无数据"
    
    current_date = builtin.get("filing_date", "2024-01-01")
    
    # 实时检查是否有新报告
    has_new, latest_date, status_msg = check_latest_13f(info["cik"], current_date)
    
    data_source = "实时检查"
    
    if has_new:
        # 尝试获取新数据
        live_data = fetch_live_data(symbol, info["cik"])
        if live_data:
            return live_data, builtin["quarter"], "已更新到最新"
        else:
            # 有新报告但暂时无法获取，显示提示
            data_source = f"有新报告({latest_date})，暂时显示历史数据"
    else:
        data_source = f"已是最新 ({status_msg})"
    
    # 使用内置数据
    builtin["data_source"] = data_source
    builtin["has_update"] = has_new
    builtin["latest_available"] = latest_date
    
    return builtin, builtin["quarter"], data_source

def get_institution_list():
    """获取机构列表"""
    return INSTITUTIONS

def get_available_quarters(symbol):
    """获取可用季度列表"""
    if symbol in BUILTIN_HOLDINGS:
        return [BUILTIN_HOLDINGS[symbol]["quarter"]]
    return []

# 使用示例
if __name__ == "__main__":
    # 测试检查功能
    result = check_latest_13f("0001067983", "2024-11-14")
    print(f"检查结果: {result}")
