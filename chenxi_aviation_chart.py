#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晨曦航空(300581)可视化分析
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_chenxi_analysis_chart():
    """创建晨曦航空分析图表"""
    
    # 获取数据
    print("📊 获取晨曦航空数据...")
    try:
        data = ak.stock_zh_a_hist(symbol='300581', period='daily', start_date='20240101', adjust='qfq')
        data.columns = ['Date', 'Code', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_Pct', 'Change_Amount', 'Turnover']
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
        
        # 计算技术指标
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA60'] = data['Close'].rolling(window=60).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        data['MACD'] = exp1 - exp2
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        print(f"✅ 数据获取成功，共{len(data)}条记录")
        
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        return
    
    # 创建图表
    fig, axes = plt.subplots(4, 1, figsize=(16, 20))
    fig.suptitle('晨曦航空(300581) AI量化分析报告', fontsize=20, fontweight='bold')
    
    # 1. 价格走势图
    ax1 = axes[0]
    ax1.plot(data.index, data['Close'], label='收盘价', linewidth=2.5, color='black')
    ax1.plot(data.index, data['MA5'], label='MA5', alpha=0.8, color='red', linewidth=1.5)
    ax1.plot(data.index, data['MA20'], label='MA20', alpha=0.8, color='blue', linewidth=1.5)
    ax1.plot(data.index, data['MA60'], label='MA60', alpha=0.8, color='green', linewidth=1.5)
    
    # 标注重要价格点
    current_price = data['Close'].iloc[-1]
    ax1.axhline(y=current_price, color='red', linestyle='--', alpha=0.7, label=f'当前价格: ¥{current_price:.2f}')
    
    ax1.set_title('价格走势与均线系统', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel('价格 (¥)')
    
    # 2. 成交量图
    ax2 = axes[1]
    colors = ['red' if x > 0 else 'green' for x in data['Change_Pct']]
    bars = ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6, width=1)
    
    # 成交量均线
    volume_ma = data['Volume'].rolling(window=20).mean()
    ax2.plot(data.index, volume_ma, label='成交量20日均线', color='orange', linewidth=2)
    
    ax2.set_title('成交量分析', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel('成交量 (手)')
    
    # 3. RSI指标
    ax3 = axes[2]
    ax3.plot(data.index, data['RSI'], label='RSI', color='purple', linewidth=2)
    ax3.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='超买线(80)')
    ax3.axhline(y=70, color='orange', linestyle='--', alpha=0.7, label='警戒线(70)')
    ax3.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='中线(50)')
    ax3.axhline(y=30, color='orange', linestyle='--', alpha=0.7, label='警戒线(30)')
    ax3.axhline(y=20, color='g', linestyle='--', alpha=0.7, label='超卖线(20)')
    
    # 填充超买超卖区域
    ax3.fill_between(data.index, 70, 80, alpha=0.1, color='red', label='超买区域')
    ax3.fill_between(data.index, 20, 30, alpha=0.1, color='green', label='超卖区域')
    
    ax3.set_title('RSI相对强弱指标', fontsize=14, fontweight='bold')
    ax3.set_ylim(0, 100)
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylabel('RSI')
    
    # 4. MACD指标
    ax4 = axes[3]
    ax4.plot(data.index, data['MACD'], label='MACD', color='blue', linewidth=2)
    ax4.plot(data.index, data['MACD_Signal'], label='Signal', color='red', linewidth=2)
    
    # MACD柱状图
    colors = ['red' if x > 0 else 'green' for x in data['MACD_Hist']]
    ax4.bar(data.index, data['MACD_Hist'], label='Histogram', color=colors, alpha=0.6, width=1)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    ax4.set_title('MACD指标', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylabel('MACD')
    ax4.set_xlabel('日期')
    
    # 格式化x轴日期
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # 保存图表
    filename = f'晨曦航空_分析报告_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 图表已保存为: {filename}")
    
    # 显示图表
    plt.show()
    
    # 生成分析总结
    print_analysis_summary(data)

def print_analysis_summary(data):
    """打印分析总结"""
    latest = data.iloc[-1]
    
    print("\n" + "="*80)
    print("📊 晨曦航空(300581) 分析总结")
    print("="*80)
    
    print(f"📈 当前价格: ¥{latest['Close']:.2f}")
    print(f"📊 今日涨跌: {latest['Change_Pct']:+.2f}% (¥{latest['Change_Amount']:+.2f})")
    print(f"💰 成交额: ¥{latest['Amount']:,.0f}万")
    print(f"🔄 换手率: {latest['Turnover']:.2f}%")
    
    # 技术指标总结
    print(f"\n🔧 技术指标:")
    print(f"   RSI: {latest['RSI']:.1f} ({'超买' if latest['RSI'] > 70 else '超卖' if latest['RSI'] < 30 else '正常'})")
    print(f"   MACD: {latest['MACD']:.4f} ({'金叉' if latest['MACD'] > latest['MACD_Signal'] else '死叉'})")
    
    # 均线分析
    ma_trend = "多头" if latest['Close'] > latest['MA5'] > latest['MA20'] else "空头" if latest['Close'] < latest['MA5'] < latest['MA20'] else "震荡"
    print(f"   均线趋势: {ma_trend}")
    
    # 近期表现
    print(f"\n📈 近期表现:")
    periods = [5, 20, 60]
    for period in periods:
        if len(data) > period:
            past_price = data['Close'].iloc[-period-1]
            return_rate = (latest['Close'] - past_price) / past_price * 100
            print(f"   {period}日收益率: {return_rate:+.2f}%")
    
    # 投资建议
    score = 0
    if latest['Close'] > latest['MA20']: score += 2
    if 30 < latest['RSI'] < 70: score += 1
    if latest['MACD'] > latest['MACD_Signal']: score += 1
    
    if score >= 3:
        advice = "🟢 建议关注"
    elif score >= 1:
        advice = "🟡 谨慎观望"
    else:
        advice = "🔴 规避风险"
    
    print(f"\n💡 综合建议: {advice}")
    print(f"⚠️  风险提示: 本分析仅供参考，投资需谨慎")

if __name__ == "__main__":
    create_chenxi_analysis_chart()
