#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用当前工程的数据获取方法分析奥瑞德
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_technical_indicators(df):
    """计算技术指标"""
    # 移动平均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA60'] = df['close'].rolling(window=60).mean()

    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 成交量均线
    df['VOL_MA5'] = df['volume'].rolling(window=5).mean()
    df['VOL_MA10'] = df['volume'].rolling(window=10).mean()

    return df

def get_stock_data_baostock(stock_code, start_date, end_date):
    """使用baostock获取股票数据"""
    print(f"\n正在使用 baostock 获取 {stock_code} 的数据...")

    # 登录系统
    lg = bs.login()
    if lg.error_code != '0':
        print(f'登录失败: {lg.error_msg}')
        return None

    # 获取数据
    fields = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"

    rs = bs.query_history_k_data_plus(
        stock_code,
        fields,
        start_date=start_date,
        end_date=end_date,
        frequency="d",  # 日线
        adjustflag="2"  # 后复权
    )

    # 获取结果
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    # 登出系统
    bs.logout()

    if not data_list:
        print("❌ 未获取到数据")
        return None

    # 转换为DataFrame
    df = pd.DataFrame(data_list, columns=rs.fields)

    # 数据类型转换
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    print(f"✓ 成功获取 {len(df)} 条数据")
    return df

def analyze_aoruide_with_project_data(stock_code, cost_price):
    """使用工程数据方法分析奥瑞德"""

    print("="*80)
    print(f"奥瑞德({stock_code})完整分析")
    print(f"使用工程中的 baostock 数据源")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 获取数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

    df = get_stock_data_baostock(stock_code, start_date, end_date)

    if df is None or len(df) == 0:
        print("❌ 无法获取数据，请检查网络连接或股票代码")
        return

    # 计算技术指标
    df = calculate_technical_indicators(df)

    # 获取最新数据
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # 显示基本信息
    print("\n" + "="*80)
    print("【最新行情】")
    print("="*80)
    print(f"日期: {latest['date']}")
    print(f"最新价: {latest['close']:.2f}元")
    print(f"涨跌幅: {latest['pctChg']:.2f}%")
    print(f"成交量: {latest['volume']/10000:.2f}万手")
    print(f"成交额: {latest['amount']/10000:.2f}万元")
    print(f"换手率: {latest['turn']:.2f}%")

    # 持仓情况
    print("\n" + "="*80)
    print("【持仓情况】")
    print("="*80)
    profit_loss = latest['close'] - cost_price
    profit_loss_pct = (profit_loss / cost_price) * 100

    print(f"成本价: {cost_price:.2f}元")
    print(f"当前价: {latest['close']:.2f}元")
    print(f"浮动盈亏: {profit_loss:+.2f}元 ({profit_loss_pct:+.2f}%)")

    if profit_loss < 0:
        print(f"\n⚠️  当前亏损 {abs(profit_loss):.2f}元/股")
        print(f"⚠️  亏损幅度 {abs(profit_loss_pct):.2f}%")

    # 均线分析
    print("\n" + "="*80)
    print("【均线系统分析】")
    print("="*80)
    print(f"MA5:  {latest['MA5']:.2f}元")
    print(f"MA10: {latest['MA10']:.2f}元")
    print(f"MA20: {latest['MA20']:.2f}元")
    print(f"MA60: {latest['MA60']:.2f}元")

    print(f"\n当前价格位置:")
    if latest['close'] < latest['MA5']:
        print(f"  ❌ 跌破MA5 (差距: {((latest['close']/latest['MA5']-1)*100):.2f}%)")
    else:
        print(f"  ✓ 站上MA5 (强度: {((latest['close']/latest['MA5']-1)*100):.2f}%)")

    if latest['close'] < latest['MA10']:
        print(f"  ❌ 跌破MA10 (差距: {((latest['close']/latest['MA10']-1)*100):.2f}%)")
    else:
        print(f"  ✓ 站上MA10 (强度: {((latest['close']/latest['MA10']-1)*100):.2f}%)")

    if latest['close'] < latest['MA20']:
        print(f"  ❌ 跌破MA20 (差距: {((latest['close']/latest['MA20']-1)*100):.2f}%)")
    else:
        print(f"  ✓ 站上MA20 (强度: {((latest['close']/latest['MA20']-1)*100):.2f}%)")

    # 均线排列
    if latest['MA5'] > latest['MA10'] > latest['MA20']:
        print(f"\n均线排列: 多头排列 ✓ (看涨)")
    elif latest['MA5'] < latest['MA10'] < latest['MA20']:
        print(f"\n均线排列: 空头排列 ❌ (看跌)")
    else:
        print(f"\n均线排列: 缠绕状态 ⚠️ (方向不明)")

    # MACD分析
    print("\n" + "="*80)
    print("【MACD指标分析】")
    print("="*80)
    print(f"MACD: {latest['MACD']:.4f}")
    print(f"Signal: {latest['Signal']:.4f}")
    print(f"Histogram: {latest['Histogram']:.4f}")

    if latest['MACD'] > latest['Signal']:
        if prev['MACD'] <= prev['Signal']:
            print("\n✓ MACD刚刚金叉 (买入信号)")
        else:
            print("\n✓ MACD金叉中 (多头状态)")
    else:
        if prev['MACD'] >= prev['Signal']:
            print("\n❌ MACD刚刚死叉 (卖出信号)")
        else:
            print("\n❌ MACD死叉中 (空头状态)")

    # RSI分析
    print("\n" + "="*80)
    print("【RSI指标分析】")
    print("="*80)
    print(f"RSI(14): {latest['RSI']:.2f}")

    if latest['RSI'] > 70:
        print("状态: 超买区 ⚠️ (可能回调)")
    elif latest['RSI'] < 30:
        print("状态: 超卖区 ✓ (可能反弹)")
    else:
        print("状态: 正常区间")

    # 近期走势
    print("\n" + "="*80)
    print("【近期走势分析】")
    print("="*80)

    recent_5 = df.tail(5)
    recent_10 = df.tail(10)
    recent_20 = df.tail(20)

    change_5 = (recent_5['close'].iloc[-1] / recent_5['close'].iloc[0] - 1) * 100
    change_10 = (recent_10['close'].iloc[-1] / recent_10['close'].iloc[0] - 1) * 100
    change_20 = (recent_20['close'].iloc[-1] / recent_20['close'].iloc[0] - 1) * 100

    print(f"近5日涨跌幅: {change_5:+.2f}%")
    print(f"近10日涨跌幅: {change_10:+.2f}%")
    print(f"近20日涨跌幅: {change_20:+.2f}%")

    # 连续阴阳线统计
    down_days = sum(recent_5['close'].diff() < 0)
    up_days = sum(recent_5['close'].diff() > 0)
    print(f"\n近5日: {up_days}天上涨, {down_days}天下跌")

    if down_days >= 3:
        print("⚠️  连续下跌，趋势偏空")
    elif up_days >= 3:
        print("✓ 连续上涨，趋势向好")

    # 支撑压力位
    print("\n" + "="*80)
    print("【关键价位】")
    print("="*80)

    recent_60 = df.tail(60)
    support = recent_60['low'].min()
    resistance = recent_60['high'].max()

    print(f"60日最低(支撑): {support:.2f}元")
    print(f"60日最高(压力): {resistance:.2f}元")
    print(f"当前价格: {latest['close']:.2f}元")
    print(f"成本价: {cost_price:.2f}元 (心理关口)")

    # 距离支撑位
    to_support = ((latest['close'] - support) / support) * 100
    to_resistance = ((resistance - latest['close']) / latest['close']) * 100

    print(f"\n距离支撑位: {to_support:.2f}% ({'安全' if to_support > 5 else '接近'})")
    print(f"距离压力位: {to_resistance:.2f}% ({'较远' if to_resistance > 10 else '临近'})")

    # 综合分析
    print("\n" + "="*80)
    print("【综合评估】")
    print("="*80)

    risk_score = 0
    buy_score = 0

    # 计算风险评分
    if profit_loss_pct < -10:
        risk_score += 3
    elif profit_loss_pct < -7:
        risk_score += 2
    elif profit_loss_pct < -5:
        risk_score += 1

    if latest['close'] < latest['MA20']:
        risk_score += 2

    if latest['MACD'] < latest['Signal']:
        risk_score += 1

    if down_days >= 3:
        risk_score += 1

    # 计算买入评分
    if latest['close'] > latest['MA5'] > latest['MA10']:
        buy_score += 2

    if latest['MACD'] > latest['Signal'] and latest['Histogram'] > 0:
        buy_score += 2

    if latest['RSI'] < 50 and latest['RSI'] > 30:
        buy_score += 1

    if change_5 > 0:
        buy_score += 1

    print(f"风险评分: {risk_score}/10 ({'高' if risk_score >= 6 else '中' if risk_score >= 3 else '低'})")
    print(f"买入评分: {buy_score}/10 ({'强' if buy_score >= 6 else '中' if buy_score >= 3 else '弱'})")

    # 操作建议
    print("\n" + "="*80)
    print("【操作建议】")
    print("="*80)

    if risk_score >= 6:
        print("\n🔴 建议: 立即止损")
        print(f"   理由: 风险过高({risk_score}/10)")
        print(f"   操作: 明天开盘卖出50-100%")
        print(f"   止损价: {latest['close'] * 0.95:.2f}元")
    elif risk_score >= 3:
        print("\n🟡 建议: 减仓观望")
        print(f"   理由: 风险中等({risk_score}/10)")
        print(f"   操作: 减仓30-50%")
        print(f"   止损价: {cost_price * 0.90:.2f}元")
    else:
        if buy_score >= 6:
            print("\n🟢 建议: 持股待涨")
            print(f"   理由: 买入信号较强({buy_score}/10)")
            print(f"   操作: 继续持有")
            print(f"   止损价: {cost_price * 0.92:.2f}元")
        else:
            print("\n🟡 建议: 谨慎持有")
            print(f"   理由: 信号不明确")
            print(f"   操作: 密切观察")
            print(f"   止损价: {cost_price * 0.90:.2f}元")

    print("\n重要提醒:")
    print("1. 以上分析基于技术面，仅供参考")
    print("2. 建议关注基本面消息和行业动态")
    print("3. 严格执行止损纪律")
    print("4. 不要满仓单一股票")

    print("\n" + "="*80)

    return df

def main():
    """主函数"""
    # 上海股票代码需要加sh前缀
    stock_code = "sh.600666"  # 奥瑞德
    cost_price = 3.80

    try:
        df = analyze_aoruide_with_project_data(stock_code, cost_price)

        if df is not None:
            print("\n✓ 分析完成")
            print(f"✓ 数据来源: baostock (工程数据接口)")
            print(f"✓ 数据条数: {len(df)}")

    except Exception as e:
        print(f"\n❌ 分析出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
