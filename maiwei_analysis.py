#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份 (300751) 分析脚本
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_technical_indicators(df):
    """计算技术指标"""
    # 计算均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA60'] = df['close'].rolling(window=60).mean()
    df['MA120'] = df['close'].rolling(window=120).mean()

    # 计算MACD
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2

    # 计算RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 计算KDJ
    low_list = df['low'].rolling(window=9).min()
    high_list = df['high'].rolling(window=9).max()
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['K'] = rsv.ewm(com=2, adjust=False).mean()
    df['D'] = df['K'].ewm(com=2, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    return df

def analyze_support_resistance(df, current_price):
    """分析支撑位和压力位"""
    recent_df = df.tail(120)  # 最近120个交易日

    # 找出最近的高点和低点
    highs = recent_df.nlargest(5, 'high')['high'].values
    lows = recent_df.nsmallest(5, 'low')['low'].values

    # 压力位：高于当前价的高点
    resistances = sorted([h for h in highs if h > current_price])[:3]
    # 支撑位：低于当前价的低点
    supports = sorted([l for l in lows if l < current_price], reverse=True)[:3]

    return supports, resistances

def main():
    print("=" * 80)
    print("迈为股份 (300751) 深度分析报告")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"持仓成本: 170元")
    print("=" * 80)

    # 获取股票信息
    try:
        stock_code = "300751"

        # 获取实时行情
        print("\n【一、当前市场行情】")
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_info = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == stock_code].iloc[0]

        current_price = float(stock_info['最新价'])
        change_pct = float(stock_info['涨跌幅'])
        volume = float(stock_info['成交量'])
        amount = float(stock_info['成交额'])
        turnover = float(stock_info['换手率'])

        print(f"当前价格: {current_price:.2f}元")
        print(f"涨跌幅: {change_pct:.2f}%")
        print(f"成交量: {volume/10000:.2f}万手")
        print(f"成交额: {amount/100000000:.2f}亿元")
        print(f"换手率: {turnover:.2f}%")

        # 计算浮亏情况
        cost_price = 170.0
        loss_amount = current_price - cost_price
        loss_pct = (loss_amount / cost_price) * 100

        print(f"\n【持仓情况】")
        print(f"持仓成本: {cost_price:.2f}元")
        print(f"当前价格: {current_price:.2f}元")
        print(f"浮动盈亏: {loss_amount:.2f}元 ({loss_pct:.2f}%)")

        # 获取历史行情数据
        print("\n【二、技术分析】")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if df.empty:
            print("无法获取历史数据")
            return

        df = df.rename(columns={
            '日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume'
        })

        # 计算技术指标
        df = calculate_technical_indicators(df)
        latest = df.iloc[-1]

        print(f"\n1. 均线系统:")
        print(f"   MA5:  {latest['MA5']:.2f}元")
        print(f"   MA10: {latest['MA10']:.2f}元")
        print(f"   MA20: {latest['MA20']:.2f}元")
        print(f"   MA60: {latest['MA60']:.2f}元")
        print(f"   MA120: {latest['MA120']:.2f}元")

        # 均线形态分析
        if current_price < latest['MA5'] < latest['MA10'] < latest['MA20']:
            ma_trend = "空头排列，趋势较弱"
        elif current_price > latest['MA5'] > latest['MA10'] > latest['MA20']:
            ma_trend = "多头排列，趋势较强"
        else:
            ma_trend = "均线粘合，方向不明"
        print(f"   均线形态: {ma_trend}")

        print(f"\n2. MACD指标:")
        print(f"   DIF: {latest['DIF']:.2f}")
        print(f"   DEA: {latest['DEA']:.2f}")
        print(f"   MACD: {latest['MACD']:.2f}")

        if latest['DIF'] > latest['DEA'] and latest['MACD'] > 0:
            macd_signal = "多头信号"
        elif latest['DIF'] < latest['DEA'] and latest['MACD'] < 0:
            macd_signal = "空头信号"
        else:
            macd_signal = "震荡信号"
        print(f"   MACD信号: {macd_signal}")

        print(f"\n3. RSI指标:")
        print(f"   RSI(14): {latest['RSI']:.2f}")
        if latest['RSI'] > 70:
            rsi_status = "超买区域，注意回调风险"
        elif latest['RSI'] < 30:
            rsi_status = "超卖区域，可能存在反弹机会"
        else:
            rsi_status = "正常区域"
        print(f"   RSI状态: {rsi_status}")

        print(f"\n4. KDJ指标:")
        print(f"   K: {latest['K']:.2f}")
        print(f"   D: {latest['D']:.2f}")
        print(f"   J: {latest['J']:.2f}")

        if latest['K'] > 80 and latest['D'] > 80:
            kdj_status = "超买区域"
        elif latest['K'] < 20 and latest['D'] < 20:
            kdj_status = "超卖区域"
        else:
            kdj_status = "正常区域"
        print(f"   KDJ状态: {kdj_status}")

        # 支撑位和压力位
        supports, resistances = analyze_support_resistance(df, current_price)
        print(f"\n5. 关键价位:")
        print(f"   支撑位: {', '.join([f'{s:.2f}元' for s in supports]) if supports else '暂无明显支撑'}")
        print(f"   压力位: {', '.join([f'{r:.2f}元' for r in resistances]) if resistances else '暂无明显压力'}")

        # 价格区间分析
        high_120 = df.tail(120)['high'].max()
        low_120 = df.tail(120)['low'].min()
        position = (current_price - low_120) / (high_120 - low_120) * 100

        print(f"\n6. 价格位置 (120日):")
        print(f"   最高价: {high_120:.2f}元")
        print(f"   最低价: {low_120:.2f}元")
        print(f"   当前位置: {position:.1f}% (0%最低, 100%最高)")

        # 获取财务数据
        print("\n【三、基本面分析】")
        try:
            # 获取主要财务指标
            stock_financial_abstract_df = ak.stock_financial_abstract(symbol=stock_code)
            if not stock_financial_abstract_df.empty:
                latest_finance = stock_financial_abstract_df.iloc[0]
                print(f"\n最新财务数据 ({latest_finance['报告日']})")
                print(f"   营业总收入: {latest_finance.get('营业总收入', 'N/A')}")
                print(f"   净利润: {latest_finance.get('净利润', 'N/A')}")
                print(f"   净利润增长率: {latest_finance.get('净利润同比增长率', 'N/A')}")

            # 获取业绩预告
            try:
                stock_yjyg_df = ak.stock_yjyg_em(date=datetime.now().strftime('%Y-%m-%d'))
                yjyg = stock_yjyg_df[stock_yjyg_df['股票代码'] == stock_code]
                if not yjyg.empty:
                    print(f"\n业绩预告:")
                    for _, row in yjyg.iterrows():
                        print(f"   {row['业绩变动']}: {row['预测指标']}")
            except:
                pass

        except Exception as e:
            print(f"   财务数据获取失败: {str(e)}")

        # 获取行业信息
        try:
            stock_individual_info_df = ak.stock_individual_info_em(symbol=stock_code)
            industry = stock_individual_info_df[stock_individual_info_df['item'] == '行业']['value'].values
            if len(industry) > 0:
                print(f"\n所属行业: {industry[0]}")
        except:
            print("\n所属行业: 光伏设备")

        # 综合评估
        print("\n" + "=" * 80)
        print("【四、综合评估与建议】")
        print("=" * 80)

        # 风险评估
        risk_score = 0
        if loss_pct < -20:
            risk_score += 2
        elif loss_pct < -10:
            risk_score += 1

        if latest['RSI'] < 30:
            risk_score -= 1
        elif latest['RSI'] > 70:
            risk_score += 1

        if position < 30:
            risk_score -= 1
        elif position > 70:
            risk_score += 1

        print(f"\n1. 技术面评估:")
        tech_signals = []
        if current_price < latest['MA20']:
            tech_signals.append("股价位于20日均线下方，短期趋势偏弱")
        if latest['MACD'] < 0:
            tech_signals.append("MACD处于零轴下方，中期趋势偏空")
        if latest['RSI'] < 40:
            tech_signals.append("RSI偏低，存在超卖迹象")

        for signal in tech_signals:
            print(f"   • {signal}")

        print(f"\n2. 持仓风险评估:")
        print(f"   当前浮亏: {loss_pct:.2f}%")
        if loss_pct < -20:
            print(f"   风险等级: 较高 - 已跌破成本20%")
        elif loss_pct < -10:
            print(f"   风险等级: 中等 - 已跌破成本10%")
        else:
            print(f"   风险等级: 可控")

        print(f"\n3. 操作建议:")

        # 根据不同情况给出建议
        if loss_pct < -25:
            print(f"   ⚠️  建议: 风险较大，建议减仓或止损")
            print(f"   • 当前亏损已达{abs(loss_pct):.1f}%，超过常规止损线")
            print(f"   • 若持续下跌，建议在重要支撑位附近止损")
        elif loss_pct < -15:
            print(f"   ⚠️  建议: 密切关注，设置止损位")
            print(f"   • 当前亏损{abs(loss_pct):.1f}%，接近止损警戒线")
            print(f"   • 建议设置止损位在{cost_price * 0.85:.2f}元附近（-15%）")
            print(f"   • 若跌破关键支撑位，及时止损")
        else:
            print(f"   📊 建议: 观望为主，关注趋势变化")
            print(f"   • 当前亏损{abs(loss_pct):.1f}%，在可控范围内")
            print(f"   • 关注是否能企稳并回升至重要均线上方")

        # 关键价位提示
        print(f"\n4. 关键价位参考:")
        if supports:
            print(f"   支撑位: {supports[0]:.2f}元 (重要)")
            print(f"   止损位参考: {cost_price * 0.85:.2f}元 (-15%)")

        if resistances:
            print(f"   压力位: {resistances[0]:.2f}元")
            print(f"   解套位: {cost_price:.2f}元 (成本价)")

        print(f"\n5. 后市展望:")
        print(f"   • 关注是否能在当前价位企稳")
        print(f"   • 注意成交量变化，放量企稳为好")
        print(f"   • 关注光伏行业政策和公司基本面变化")
        print(f"   • 严格执行止损纪律，控制风险")

        print("\n" + "=" * 80)
        print("风险提示: 以上分析仅供参考，不构成投资建议。")
        print("股市有风险，投资需谨慎。请根据自己的风险承受能力做出决策。")
        print("=" * 80)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
