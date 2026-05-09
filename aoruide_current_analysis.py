#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奥瑞德(600666)当前走势分析
成本价: 3.80元
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_ma(data, periods=[5, 10, 20, 60]):
    """计算移动平均线"""
    for period in periods:
        data[f'MA{period}'] = data['close'].rolling(window=period).mean()
    return data

def calculate_macd(data, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    exp1 = data['close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['close'].ewm(span=slow, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal'] = data['MACD'].ewm(span=signal, adjust=False).mean()
    data['Histogram'] = data['MACD'] - data['Signal']
    return data

def calculate_rsi(data, period=14):
    """计算RSI指标"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def calculate_kdj(data, n=9, m1=3, m2=3):
    """计算KDJ指标"""
    low_list = data['low'].rolling(window=n).min()
    high_list = data['high'].rolling(window=n).max()

    rsv = (data['close'] - low_list) / (high_list - low_list) * 100
    data['K'] = rsv.ewm(com=m1-1, adjust=False).mean()
    data['D'] = data['K'].ewm(com=m2-1, adjust=False).mean()
    data['J'] = 3 * data['K'] - 2 * data['D']
    return data

def analyze_trend(data, cost_price=3.80):
    """综合分析走势"""
    latest = data.iloc[-1]
    prev = data.iloc[-2]

    print("=" * 80)
    print(f"奥瑞德(600666)走势分析报告")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"您的成本价: {cost_price:.2f}元")
    print("=" * 80)

    # 基本信息
    print(f"\n【最新行情】")
    print(f"最新价格: {latest['close']:.2f}元")
    print(f"涨跌幅: {((latest['close']/prev['close']-1)*100):.2f}%")
    print(f"成交量: {latest['volume']/10000:.2f}万手")
    print(f"成交额: {latest['amount']/100000000:.2f}亿元")
    print(f"换手率: {latest.get('turnover', 0):.2f}%")

    # 盈亏情况
    profit_loss = latest['close'] - cost_price
    profit_loss_pct = (profit_loss / cost_price) * 100
    print(f"\n【持仓情况】")
    print(f"浮动盈亏: {profit_loss:+.2f}元 ({profit_loss_pct:+.2f}%)")

    if profit_loss < 0:
        print(f"当前亏损: {abs(profit_loss):.2f}元/股")
        print(f"亏损幅度: {abs(profit_loss_pct):.2f}%")
    else:
        print(f"当前盈利: {profit_loss:.2f}元/股")
        print(f"盈利幅度: {profit_loss_pct:.2f}%")

    # 均线分析
    print(f"\n【均线系统】")
    print(f"MA5:  {latest['MA5']:.2f}元  当前价{'>' if latest['close'] > latest['MA5'] else '<'}MA5 ({((latest['close']/latest['MA5']-1)*100):+.2f}%)")
    print(f"MA10: {latest['MA10']:.2f}元  当前价{'>' if latest['close'] > latest['MA10'] else '<'}MA10 ({((latest['close']/latest['MA10']-1)*100):+.2f}%)")
    print(f"MA20: {latest['MA20']:.2f}元  当前价{'>' if latest['close'] > latest['MA20'] else '<'}MA20 ({((latest['close']/latest['MA20']-1)*100):+.2f}%)")
    print(f"MA60: {latest['MA60']:.2f}元  当前价{'>' if latest['close'] > latest['MA60'] else '<'}MA60 ({((latest['close']/latest['MA60']-1)*100):+.2f}%)")

    # 均线排列
    ma_arrangement = ""
    if latest['MA5'] > latest['MA10'] > latest['MA20']:
        ma_arrangement = "多头排列(看涨)"
    elif latest['MA5'] < latest['MA10'] < latest['MA20']:
        ma_arrangement = "空头排列(看跌)"
    else:
        ma_arrangement = "缠绕状态(方向不明)"
    print(f"均线排列: {ma_arrangement}")

    # 技术指标
    print(f"\n【技术指标】")
    print(f"MACD: {latest['MACD']:.4f}")
    print(f"Signal: {latest['Signal']:.4f}")
    print(f"Histogram: {latest['Histogram']:.4f} ({'金叉' if latest['MACD'] > latest['Signal'] else '死叉'})")
    print(f"RSI(14): {latest['RSI']:.2f} ", end="")
    if latest['RSI'] > 70:
        print("(超买区)")
    elif latest['RSI'] < 30:
        print("(超卖区)")
    else:
        print("(正常区间)")

    print(f"KDJ: K={latest['K']:.2f}, D={latest['D']:.2f}, J={latest['J']:.2f}")
    if latest['K'] > 80 and latest['D'] > 80:
        print("     (超买区)")
    elif latest['K'] < 20 and latest['D'] < 20:
        print("     (超卖区)")

    # 近期走势
    print(f"\n【近期表现】")
    recent_5 = data.tail(5)
    print(f"近5日涨跌幅: {((recent_5['close'].iloc[-1]/recent_5['close'].iloc[0]-1)*100):+.2f}%")
    recent_10 = data.tail(10)
    print(f"近10日涨跌幅: {((recent_10['close'].iloc[-1]/recent_10['close'].iloc[0]-1)*100):+.2f}%")
    recent_20 = data.tail(20)
    print(f"近20日涨跌幅: {((recent_20['close'].iloc[-1]/recent_20['close'].iloc[0]-1)*100):+.2f}%")

    # 支撑位和压力位
    print(f"\n【关键价位】")
    recent_60 = data.tail(60)
    support1 = recent_60['low'].min()
    resistance1 = recent_60['high'].max()
    print(f"60日最低: {support1:.2f}元 (重要支撑)")
    print(f"60日最高: {resistance1:.2f}元 (重要压力)")
    print(f"成本价位: {cost_price:.2f}元 (您的心理关口)")

    # 止损建议分析
    print(f"\n{'=' * 80}")
    print("【综合判断与操作建议】")
    print("=" * 80)

    risk_score = 0
    warnings_list = []
    positive_list = []

    # 1. 亏损程度
    if profit_loss_pct < -10:
        risk_score += 3
        warnings_list.append(f"⚠️ 亏损已达{abs(profit_loss_pct):.2f}%,超过10%警戒线")
    elif profit_loss_pct < -7:
        risk_score += 2
        warnings_list.append(f"⚠️ 亏损{abs(profit_loss_pct):.2f}%,接近止损线")
    elif profit_loss_pct < -5:
        risk_score += 1
        warnings_list.append(f"⚠️ 亏损{abs(profit_loss_pct):.2f}%,需要关注")
    else:
        if profit_loss_pct > 0:
            positive_list.append(f"✓ 当前盈利{profit_loss_pct:.2f}%")
        else:
            positive_list.append(f"✓ 亏损在可控范围内({abs(profit_loss_pct):.2f}%)")

    # 2. 均线系统
    if latest['close'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
        risk_score += 2
        warnings_list.append("⚠️ 均线空头排列,趋势较弱")
    elif latest['close'] < latest['MA20']:
        risk_score += 1
        warnings_list.append("⚠️ 股价跌破20日均线")
    else:
        if latest['close'] > latest['MA5'] > latest['MA10']:
            positive_list.append("✓ 均线多头排列,趋势较好")
        else:
            positive_list.append("✓ 股价站稳短期均线")

    # 3. MACD
    if latest['MACD'] < 0 and latest['Histogram'] < 0:
        risk_score += 1
        warnings_list.append("⚠️ MACD在零轴下方且走弱")
    elif latest['MACD'] > 0 and latest['Histogram'] > 0:
        positive_list.append("✓ MACD金叉向上")

    # 4. RSI
    if latest['RSI'] < 30:
        positive_list.append(f"✓ RSI={latest['RSI']:.2f},处于超卖区,可能反弹")
    elif latest['RSI'] > 70:
        risk_score += 1
        warnings_list.append(f"⚠️ RSI={latest['RSI']:.2f},超买需警惕")

    # 5. 近期趋势
    recent_trend_5 = (recent_5['close'].iloc[-1]/recent_5['close'].iloc[0]-1)*100
    if recent_trend_5 < -5:
        risk_score += 1
        warnings_list.append(f"⚠️ 近5日持续下跌{abs(recent_trend_5):.2f}%")
    elif recent_trend_5 > 5:
        positive_list.append(f"✓ 近5日上涨{recent_trend_5:.2f}%,短期走强")

    # 6. 成交量分析
    avg_volume = recent_20['volume'].mean()
    if latest['volume'] > avg_volume * 1.5 and latest['close'] < prev['close']:
        risk_score += 1
        warnings_list.append("⚠️ 放量下跌,抛压较重")
    elif latest['volume'] > avg_volume * 1.5 and latest['close'] > prev['close']:
        positive_list.append("✓ 放量上涨,资金进场")

    print("\n【风险提示】")
    for warning in warnings_list:
        print(warning)

    print("\n【积极因素】")
    for positive in positive_list:
        print(positive)

    print(f"\n【风险评分】: {risk_score}/10分")

    # 给出操作建议
    print("\n" + "=" * 80)
    print("【操作建议】")
    print("=" * 80)

    if risk_score >= 6:
        print("\n🔴 建议:考虑止损")
        print(f"   • 风险较高({risk_score}分),建议及时止损")
        print(f"   • 止损价位建议: {latest['close'] * 0.97:.2f}元(跌破3%止损)")
        print(f"   • 或设置成本价附近止损: {cost_price * 0.98:.2f}元")
    elif risk_score >= 4:
        print("\n🟡 建议:减仓观望")
        print(f"   • 风险中等({risk_score}分),建议减仓一半")
        print(f"   • 设置止损价: {latest['close'] * 0.95:.2f}元(跌破5%止损)")
        print(f"   • 反弹至{cost_price:.2f}元附近可考虑减仓")
    elif risk_score >= 2:
        print("\n🟢 建议:持股观察")
        print(f"   • 风险较低({risk_score}分),可继续持有")
        print(f"   • 设置止损价: {cost_price * 0.92:.2f}元(成本价-8%)")
        print(f"   • 目标价位: {latest['MA20']:.2f}元(20日均线)")
    else:
        print("\n🟢 建议:持股待涨")
        print(f"   • 风险低({risk_score}分),趋势较好")
        print(f"   • 设置止损价: {cost_price * 0.90:.2f}元(成本价-10%)")
        print(f"   • 目标价位: {resistance1:.2f}元(前期高点)")

    print("\n【重要提醒】")
    print("1. 以上分析仅供参考,不构成投资建议")
    print("2. 股市有风险,投资需谨慎")
    print("3. 建议结合自己的风险承受能力和持仓比例决策")
    print("4. 如果该股票占比过大,建议适当分散风险")
    print("=" * 80)

def main():
    try:
        print("正在获取奥瑞德(600666)最新数据...")

        # 获取日线数据(近6个月)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol="600666", period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if df is None or len(df) == 0:
            print("❌ 无法获取股票数据,请检查股票代码或网络连接")
            return

        # 数据预处理
        df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'volume',
                      'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # 计算技术指标
        df = calculate_ma(df)
        df = calculate_macd(df)
        df = calculate_rsi(df)
        df = calculate_kdj(df)

        # 分析走势
        analyze_trend(df, cost_price=3.80)

    except Exception as e:
        print(f"❌ 分析出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
