#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份最近K线和资金流向详细分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 100)
    print("迈为股份 (300751) 最近K线详细分析")
    print("=" * 100)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    stock_code = "300751"

    try:
        # 获取最近的日K线数据
        print("\n【最近15个交易日K线数据】\n")

        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if not df.empty:
            # 重命名列
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume',
                '成交额': 'amount', '振幅': 'amplitude', '涨跌幅': 'change_pct',
                '涨跌额': 'change', '换手率': 'turnover'
            })

            # 获取最近15个交易日
            recent_df = df.tail(15)

            print("=" * 120)
            print(f"{'日期':<12} {'开盘':>8} {'收盘':>8} {'最高':>8} {'最低':>8} {'涨跌幅':>8} {'成交额(亿)':>10} {'换手率':>8} {'振幅':>8}")
            print("=" * 120)

            for idx, row in recent_df.iterrows():
                change_mark = "📈" if row['change_pct'] > 0 else "📉" if row['change_pct'] < 0 else "➖"

                # 特别标注大跌
                if row['change_pct'] <= -10:
                    change_mark = "💥💥💥"
                elif row['change_pct'] <= -5:
                    change_mark = "⚠️"

                amount_yi = row['amount'] / 100000000

                print(f"{row['date']:<12} {row['open']:>8.2f} {row['close']:>8.2f} "
                      f"{row['high']:>8.2f} {row['low']:>8.2f} "
                      f"{row['change_pct']:>7.2f}% {amount_yi:>10.2f} "
                      f"{row['turnover']:>7.2f}% {row['amplitude']:>7.2f}% {change_mark}")

            print("=" * 120)

            # 找出大跌日
            print("\n【异常波动日分析】\n")

            big_drop_days = recent_df[recent_df['change_pct'] <= -5].copy()

            if not big_drop_days.empty:
                print(f"找到 {len(big_drop_days)} 个大跌日（跌幅≥5%）:\n")

                for idx, row in big_drop_days.iterrows():
                    print(f"💥 {row['date']}")
                    print(f"   跌幅: {row['change_pct']:.2f}%")
                    print(f"   收盘: {row['close']:.2f}元")
                    print(f"   最低: {row['low']:.2f}元")
                    print(f"   成交额: {row['amount']/100000000:.2f}亿元")
                    print(f"   换手率: {row['turnover']:.2f}%")
                    print(f"   振幅: {row['amplitude']:.2f}%")
                    print()
            else:
                print("最近15个交易日无大跌（跌幅≥5%）")

            # 计算最近5日、10日的涨跌幅
            print("【累计涨跌幅统计】\n")

            if len(recent_df) >= 5:
                recent_5 = recent_df.tail(5)
                price_5_start = recent_5.iloc[0]['close']
                price_5_end = recent_5.iloc[-1]['close']
                change_5d = (price_5_end - price_5_start) / price_5_start * 100

                print(f"近5日累计涨跌幅: {change_5d:.2f}%")
                print(f"   5日前收盘价: {price_5_start:.2f}元")
                print(f"   当前收盘价: {price_5_end:.2f}元")

            if len(recent_df) >= 10:
                recent_10 = recent_df.tail(10)
                price_10_start = recent_10.iloc[0]['close']
                price_10_end = recent_10.iloc[-1]['close']
                change_10d = (price_10_end - price_10_start) / price_10_start * 100

                print(f"\n近10日累计涨跌幅: {change_10d:.2f}%")
                print(f"   10日前收盘价: {price_10_start:.2f}元")
                print(f"   当前收盘价: {price_10_end:.2f}元")

            # 获取今日实时行情
            print("\n【今日实时行情】\n")
            try:
                stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                stock_info = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == stock_code].iloc[0]

                print(f"当前价格: {stock_info['最新价']}元")
                print(f"今日涨跌幅: {stock_info['涨跌幅']:.2f}%")
                print(f"今日最高: {stock_info['最高']}元")
                print(f"今日最低: {stock_info['最低']}元")
                print(f"今日成交额: {stock_info['成交额']/100000000:.2f}亿元")
                print(f"今日换手率: {stock_info['换手率']:.2f}%")
            except:
                pass

            # 现在尝试匹配资金流向数据
            print("\n【尝试匹配资金流向数据】\n")

            try:
                # 获取今日、5日、10日资金流向
                for indicator in ["今日", "5日", "10日"]:
                    df_flow = ak.stock_individual_fund_flow_rank(indicator=indicator)
                    maiwei_flow = df_flow[df_flow['代码'] == stock_code]

                    if not maiwei_flow.empty:
                        flow = maiwei_flow.iloc[0]
                        print(f"{indicator}资金流向:")
                        print(f"   主力净流入: {flow[f'{indicator}主力净流入-净额']/10000:.2f}万元")
                        print(f"   超大单: {flow[f'{indicator}超大单净流入-净额']/10000:.2f}万元")
                        print(f"   大单: {flow[f'{indicator}大单净流入-净额']/10000:.2f}万元")
                        print()
            except Exception as e:
                print(f"资金流向数据获取失败: {e}")

            print("=" * 100)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
