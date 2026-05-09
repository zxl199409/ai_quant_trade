#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票交易规则指南 - 新手实战版
帮助建立清晰的买卖决策系统
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_indicators(df):
    """计算常用技术指标"""
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

def check_buy_signals(df, current_price, stock_name="该股票"):
    """检查买入信号"""
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    print("\n" + "="*80)
    print(f"【买入信号检查】 {stock_name}")
    print("="*80)

    buy_signals = []
    buy_score = 0

    # 1. 均线多头排列
    if latest['MA5'] > latest['MA10'] > latest['MA20']:
        buy_signals.append("✓ 均线多头排列（MA5>MA10>MA20）")
        buy_score += 2
    elif latest['close'] > latest['MA5'] > latest['MA10']:
        buy_signals.append("✓ 股价站稳短期均线")
        buy_score += 1

    # 2. 股价位置
    if latest['close'] > latest['MA5']:
        buy_signals.append("✓ 股价在MA5之上")
        buy_score += 1

    if latest['close'] > latest['MA20']:
        buy_signals.append("✓ 股价在MA20之上（中期趋势向上）")
        buy_score += 1

    # 3. MACD金叉
    if latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal']:
        buy_signals.append("✓✓ MACD金叉（刚刚形成）")
        buy_score += 3
    elif latest['MACD'] > latest['Signal'] and latest['Histogram'] > prev['Histogram']:
        buy_signals.append("✓ MACD金叉向上发散")
        buy_score += 2

    # 4. RSI超卖反弹
    if latest['RSI'] < 30 and latest['RSI'] > prev['RSI']:
        buy_signals.append("✓✓ RSI超卖反弹（强烈信号）")
        buy_score += 3
    elif 30 <= latest['RSI'] <= 50:
        buy_signals.append("✓ RSI处于健康区间")
        buy_score += 1

    # 5. 成交量放大
    if latest['volume'] > latest['VOL_MA5'] * 1.5 and latest['close'] > prev['close']:
        buy_signals.append("✓✓ 放量上涨（资金进场）")
        buy_score += 2

    # 6. 连续上涨
    recent_5 = df.tail(5)
    up_days = sum(recent_5['close'].diff() > 0)
    if up_days >= 3:
        buy_signals.append(f"✓ 近5日有{up_days}天上涨")
        buy_score += 1

    # 7. 突破关键位置
    ma20_max = df.tail(20)['MA20'].max()
    if latest['close'] > ma20_max * 0.98:
        buy_signals.append("✓ 接近或突破20日均线高点")
        buy_score += 1

    print(f"\n当前价格: {current_price:.2f}元")
    print(f"买入评分: {buy_score}/15分\n")

    if buy_signals:
        print("发现的买入信号:")
        for signal in buy_signals:
            print(f"  {signal}")
    else:
        print("❌ 暂无明显买入信号")

    print("\n【买入建议】:")
    if buy_score >= 10:
        print("🟢🟢 强烈买入信号（评分>=10分）")
        print("   建议: 可以积极买入，但要分批建仓")
        print(f"   第一批: 买入30%仓位，价格{current_price:.2f}元")
        print(f"   第二批: 如回调至{current_price*0.97:.2f}元再买30%")
        print(f"   第三批: 确认突破后买入剩余40%")
    elif buy_score >= 7:
        print("🟢 中等买入信号（评分7-9分）")
        print("   建议: 可以小仓位试探，观察后续走势")
        print(f"   试探仓: 先买入20%仓位")
        print(f"   加仓条件: 站稳{latest['MA20']:.2f}元后再加仓")
    elif buy_score >= 4:
        print("🟡 弱买入信号（评分4-6分）")
        print("   建议: 继续观察，等待更好的买入时机")
        print("   关注: 是否突破关键均线或MACD金叉")
    else:
        print("🔴 无买入信号（评分<4分）")
        print("   建议: 不要买入，等待明确信号")
        print("   原因: 趋势不明朗，风险大于机会")

    return buy_score, buy_signals

def check_sell_signals(df, current_price, cost_price, stock_name="该股票"):
    """检查卖出信号"""
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    print("\n" + "="*80)
    print(f"【卖出信号检查】 {stock_name}")
    print("="*80)

    sell_signals = []
    sell_score = 0
    profit_loss_pct = (current_price - cost_price) / cost_price * 100

    # 1. 止损信号（最重要！）
    if profit_loss_pct <= -10:
        sell_signals.append("❗❗ 亏损达到10%，触发止损线")
        sell_score += 5
    elif profit_loss_pct <= -7:
        sell_signals.append("❗ 亏损达到7%，接近止损线")
        sell_score += 3
    elif profit_loss_pct <= -5:
        sell_signals.append("⚠ 亏损达到5%，需要警惕")
        sell_score += 2

    # 2. 均线死叉
    if latest['MA5'] < latest['MA10'] < latest['MA20']:
        sell_signals.append("❗ 均线空头排列（趋势转弱）")
        sell_score += 3
    elif latest['close'] < latest['MA5']:
        sell_signals.append("⚠ 跌破MA5均线")
        sell_score += 1

    if latest['close'] < latest['MA20']:
        sell_signals.append("❗ 跌破MA20均线（中期趋势转弱）")
        sell_score += 2

    # 3. MACD死叉
    if latest['MACD'] < latest['Signal'] and prev['MACD'] >= prev['Signal']:
        sell_signals.append("❗❗ MACD死叉（刚刚形成）")
        sell_score += 3
    elif latest['MACD'] < latest['Signal'] and latest['Histogram'] < prev['Histogram']:
        sell_signals.append("❗ MACD死叉向下发散")
        sell_score += 2

    # 4. RSI超买
    if latest['RSI'] > 70:
        sell_signals.append("⚠ RSI超买（需警惕回调）")
        sell_score += 2

    # 5. 放量下跌
    if latest['volume'] > latest['VOL_MA5'] * 1.5 and latest['close'] < prev['close']:
        sell_signals.append("❗ 放量下跌（抛压较重）")
        sell_score += 2

    # 6. 连续下跌
    recent_5 = df.tail(5)
    down_days = sum(recent_5['close'].diff() < 0)
    if down_days >= 3:
        sell_signals.append(f"⚠ 近5日有{down_days}天下跌")
        sell_score += 1

    # 7. 高位滞涨
    recent_10_high = df.tail(10)['high'].max()
    if latest['close'] >= recent_10_high * 0.98 and latest['close'] <= prev['close']:
        sell_signals.append("⚠ 高位滞涨（上涨乏力）")
        sell_score += 1

    # 8. 止盈信号
    if profit_loss_pct >= 20:
        sell_signals.append(f"✓ 盈利{profit_loss_pct:.1f}%，建议分批止盈")
        sell_score += 2
    elif profit_loss_pct >= 10:
        sell_signals.append(f"✓ 盈利{profit_loss_pct:.1f}%，可考虑减仓保护利润")
        sell_score += 1

    print(f"\n当前价格: {current_price:.2f}元")
    print(f"成本价格: {cost_price:.2f}元")
    print(f"盈亏情况: {profit_loss_pct:+.2f}%")
    print(f"卖出评分: {sell_score}/20分\n")

    if sell_signals:
        print("发现的卖出信号:")
        for signal in sell_signals:
            print(f"  {signal}")
    else:
        print("✓ 暂无明显卖出信号，可继续持有")

    print("\n【卖出建议】:")
    if sell_score >= 10:
        print("🔴🔴 强烈卖出信号（评分>=10分）")
        print("   建议: 立即卖出，不要犹豫")
        if profit_loss_pct < -5:
            print(f"   操作: 明天开盘卖出至少50%仓位")
            print(f"   止损价: {current_price * 0.97:.2f}元")
        else:
            print(f"   操作: 分批卖出，先卖50%")
    elif sell_score >= 7:
        print("🔴 中等卖出信号（评分7-9分）")
        print("   建议: 减仓50%，降低风险")
        print(f"   止损价: {current_price * 0.95:.2f}元")
        if profit_loss_pct > 0:
            print("   目标: 保护已有利润")
    elif sell_score >= 4:
        print("🟡 弱卖出信号（评分4-6分）")
        print("   建议: 密切观察，设好止损")
        print(f"   止损价: {cost_price * 0.90:.2f}元（成本价-10%）")
        print("   如果继续走弱，及时减仓")
    else:
        print("🟢 无卖出信号（评分<4分）")
        print("   建议: 继续持有，保持耐心")
        print(f"   止损价: {cost_price * 0.92:.2f}元（成本价-8%）")

    return sell_score, sell_signals

def print_trading_rules():
    """打印交易规则总结"""
    print("\n" + "="*80)
    print("【完整交易规则 - 新手必读】")
    print("="*80)

    print("\n📈 【买入规则】- 满足3个以上条件才考虑买入\n")
    print("1. 趋势条件（必须满足）:")
    print("   ✓ 股价站上MA5或MA10")
    print("   ✓ 均线开始向上或已经多头排列")
    print("   ✓ MACD在零轴附近或金叉\n")

    print("2. 时机条件（至少满足2个）:")
    print("   ✓ RSI在30-50区间（超卖反弹或健康状态）")
    print("   ✓ 放量上涨（成交量比5日均量大50%以上）")
    print("   ✓ 连续2-3天收阳线")
    print("   ✓ 突破重要压力位或均线\n")

    print("3. 买入策略:")
    print("   • 永远不要一次性满仓！")
    print("   • 分3批建仓: 30% → 30% → 40%")
    print("   • 第一批买入后设止损（-5%）")
    print("   • 确认趋势后再加仓\n")

    print("4. 买入禁忌:")
    print("   ✗ 追高买入（涨幅超过5%不追）")
    print("   ✗ 均线空头排列时买入")
    print("   ✗ RSI>70超买区买入")
    print("   ✗ 盲目抄底（持续下跌不抄底）")

    print("\n" + "-"*80)
    print("\n📉 【卖出规则】- 铁的纪律，必须执行\n")
    print("1. 止损规则（无条件执行！）:")
    print("   ❗ 亏损达到-7%: 必须减仓50%")
    print("   ❗ 亏损达到-10%: 必须全部止损")
    print("   ❗ 跌破关键支撑位: 立即止损")
    print("   → 止损是保命的！宁可错卖，不可死扛！\n")

    print("2. 止盈规则:")
    print("   ✓ 盈利10%: 卖出30%，锁定部分利润")
    print("   ✓ 盈利20%: 卖出50%，落袋为安")
    print("   ✓ 盈利30%: 卖出70%，留少量仓位")
    print("   → 会买的是徒弟，会卖的是师傅！\n")

    print("3. 技术卖出信号（满足2个就减仓）:")
    print("   ⚠ MACD死叉")
    print("   ⚠ 跌破MA20")
    print("   ⚠ 均线空头排列")
    print("   ⚠ 放量下跌")
    print("   ⚠ 连续3天收阴线\n")

    print("4. 卖出策略:")
    print("   • 分批卖出，不要一次性清仓（除非止损）")
    print("   • 先卖50% → 观察 → 再决定")
    print("   • 卖出后不要后悔，保住本金最重要")

    print("\n" + "-"*80)
    print("\n💰 【仓位管理】- 比买卖点更重要\n")
    print("1. 总仓位控制:")
    print("   • 永远不要满仓！保留30%现金")
    print("   • 单只股票不超过总资产的30%")
    print("   • 同一板块不超过总资产的50%\n")

    print("2. 亏损后的仓位:")
    print("   • 亏损后必须减仓，不能加仓摊成本")
    print("   • 除非出现明确的买入信号")
    print("   • 宁可踏空，不可套牢\n")

    print("3. 盈利后的仓位:")
    print("   • 盈利10%后，把止损价提高到成本价")
    print("   • 盈利20%后，止损价提高到成本价+5%")
    print("   • 用利润博弈，不用本金冒险")

    print("\n" + "-"*80)
    print("\n🧠 【心态管理】- 决定成败的关键\n")
    print("1. 克服贪婪:")
    print("   • 不追涨杀跌")
    print("   • 设定目标，达到就卖")
    print("   • 不要幻想买在最低，卖在最高\n")

    print("2. 克服恐惧:")
    print("   • 严格按规则止损，不要心存侥幸")
    print("   • 止损后不要懊悔，这是保护你的")
    print("   • 市场永远有机会，本金没了就没有了\n")

    print("3. 克服幻想:")
    print("   • 不要相信\"别人说\"")
    print("   • 不要相信\"一定会涨回来\"")
    print("   • 只相信技术信号和客观数据")

    print("\n" + "="*80)
    print("记住: 活下来，比赚钱更重要！")
    print("="*80 + "\n")

def analyze_current_position(stock_code, cost_price):
    """分析当前持仓"""
    try:
        print(f"\n正在分析您的持仓 {stock_code}...")

        # 获取股票名称
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        stock_name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]

        # 获取数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if df is None or len(df) == 0:
            print("❌ 无法获取数据")
            return

        # 数据处理
        df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'volume',
                      'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # 计算指标
        df = calculate_indicators(df)

        current_price = df.iloc[-1]['close']

        # 打印交易规则
        print_trading_rules()

        # 检查买入信号
        buy_score, buy_signals = check_buy_signals(df, current_price, stock_name)

        # 检查卖出信号
        sell_score, sell_signals = check_sell_signals(df, current_price, cost_price, stock_name)

        # 综合判断
        print("\n" + "="*80)
        print("【综合操作建议】")
        print("="*80)

        print(f"\n股票: {stock_name}({stock_code})")
        print(f"当前价: {current_price:.2f}元")
        print(f"成本价: {cost_price:.2f}元")
        print(f"盈亏: {((current_price-cost_price)/cost_price*100):+.2f}%")
        print(f"\n买入评分: {buy_score}/15分")
        print(f"卖出评分: {sell_score}/20分")

        print("\n【最终建议】:")
        if sell_score >= 7:
            print("🔴 建议: 立即卖出或减仓")
            print(f"   理由: 卖出信号强烈({sell_score}分)")
            print("   操作: 明天开盘卖出50%仓位")
            print(f"   止损: {current_price * 0.95:.2f}元")
        elif sell_score >= 4:
            print("🟡 建议: 减仓观望")
            print(f"   理由: 有卖出信号({sell_score}分)")
            print("   操作: 先减仓30%，剩余设止损")
            print(f"   止损: {cost_price * 0.90:.2f}元")
        elif buy_score >= 7:
            print("🟢 建议: 继续持有")
            print(f"   理由: 买入信号较强({buy_score}分)")
            print("   操作: 持股待涨")
            print(f"   止损: {cost_price * 0.92:.2f}元")
        else:
            print("🟡 建议: 谨慎观察")
            print("   理由: 买卖信号都不强")
            print("   操作: 保持现有仓位，密切观察")
            print(f"   止损: {cost_price * 0.90:.2f}元")

        print("\n" + "="*80)

    except Exception as e:
        print(f"❌ 分析出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 分析奥瑞德当前持仓
    analyze_current_position("600666", 3.80)
