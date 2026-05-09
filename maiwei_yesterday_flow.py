#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询昨天的资金流向
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 80)
    print("查询迈为股份昨天的资金流向")
    print("=" * 80)

    stock_code = "300751"

    # 先获取1日、3日、5日的数据，通过计算得出昨天的
    try:
        print("\n【方法一：通过汇总数据推算】\n")

        # 获取不同周期的数据
        today_data = None
        day3_data = None
        day5_data = None

        for indicator in ["今日", "3日", "5日"]:
            df = ak.stock_individual_fund_flow_rank(indicator=indicator)
            maiwei = df[df['代码'] == stock_code]

            if not maiwei.empty:
                flow = maiwei.iloc[0]
                main_flow = flow[f'{indicator}主力净流入-净额'] / 10000
                super_flow = flow[f'{indicator}超大单净流入-净额'] / 10000
                big_flow = flow[f'{indicator}大单净流入-净额'] / 10000

                print(f"{indicator}资金流向:")
                print(f"   主力: {main_flow:>10.2f}万元")
                print(f"   超大单: {super_flow:>10.2f}万元")
                print(f"   大单: {big_flow:>10.2f}万元")
                print()

                if indicator == "今日":
                    today_data = {'main': main_flow, 'super': super_flow, 'big': big_flow}
                elif indicator == "3日":
                    day3_data = {'main': main_flow, 'super': super_flow, 'big': big_flow}
                elif indicator == "5日":
                    day5_data = {'main': main_flow, 'super': super_flow, 'big': big_flow}

        # 推算昨天和前天
        if today_data and day3_data and day5_data:
            print("=" * 80)
            print("【推算结果】\n")

            # 前两天 = 3日 - 今日
            day_2_3_main = day3_data['main'] - today_data['main']
            day_2_3_super = day3_data['super'] - today_data['super']
            day_2_3_big = day3_data['big'] - today_data['big']

            print("昨天+前天（合计）:")
            print(f"   主力: {day_2_3_main:>10.2f}万元")
            print(f"   超大单: {day_2_3_super:>10.2f}万元")
            print(f"   大单: {day_2_3_big:>10.2f}万元")
            print()

            # 第3-5天 = 5日 - 3日
            day_3_5_main = day5_data['main'] - day3_data['main']
            day_3_5_super = day5_data['super'] - day3_data['super']
            day_3_5_big = day5_data['big'] - day3_data['big']

            print("第3天+第4天（合计）:")
            print(f"   主力: {day_3_5_main:>10.2f}万元")
            print(f"   超大单: {day_3_5_super:>10.2f}万元")
            print(f"   大单: {day_3_5_big:>10.2f}万元")
            print()

            # 估算昨天的大致情况（假设昨天和前天平分）
            yesterday_main_est = day_2_3_main / 2
            yesterday_super_est = day_2_3_super / 2
            yesterday_big_est = day_2_3_big / 2

            print("=" * 80)
            print("【昨天资金流向估算】（假设昨天和前天均分）\n")
            print(f"主力净流入: {yesterday_main_est:>10.2f}万元")
            print(f"超大单: {yesterday_super_est:>10.2f}万元")
            print(f"大单: {yesterday_big_est:>10.2f}万元")
            print()

            if yesterday_main_est > 0:
                print("💡 昨天主力可能是 ✅ 净流入")
            else:
                print("💡 昨天主力可能是 ❌ 净流出")

        print("\n" + "=" * 80)
        print("【方法二：查看K线走势判断】\n")

        # 获取最近几天的K线
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if not df.empty:
            df = df.rename(columns={'日期': 'date', '涨跌幅': 'change_pct', '收盘': 'close',
                                   '成交额': 'amount', '换手率': 'turnover'})

            recent = df.tail(5)
            print(f"{'日期':<15} {'涨跌幅':>10} {'收盘价':>10} {'成交额(亿)':>12} {'换手率':>10}")
            print("-" * 80)

            for _, row in recent.iterrows():
                amount_yi = row['amount'] / 100000000
                print(f"{row['date']:<15} {row['change_pct']:>9.2f}% {row['close']:>10.2f} "
                      f"{amount_yi:>11.2f} {row['turnover']:>9.2f}%")

            print("\n根据K线判断:")
            if len(recent) >= 2:
                yesterday = recent.iloc[-2]
                print(f"\n昨天（{yesterday['date']}）:")
                print(f"   涨跌幅: {yesterday['change_pct']:.2f}%")
                print(f"   收盘价: {yesterday['close']:.2f}元")
                print(f"   成交额: {yesterday['amount']/100000000:.2f}亿元")
                print(f"   换手率: {yesterday['turnover']:.2f}%")

                if yesterday['change_pct'] >= 0:
                    print(f"\n   股价微涨，资金面可能偏中性或小幅流入")
                else:
                    print(f"\n   股价下跌，资金面可能偏弱")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"查询出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
