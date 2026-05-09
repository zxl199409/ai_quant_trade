#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份今日实时分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 100)
    print("迈为股份 (300751) 今日实时分析")
    print("=" * 100)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    stock_code = "300751"
    cost_price = 170.0
    yesterday_close = 156.35  # 昨天收盘价

    try:
        # 1. 获取实时行情
        print("\n【一、今日实时行情】\n")

        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_info = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == stock_code].iloc[0]

        current_price = float(stock_info['最新价'])
        change_pct = float(stock_info['涨跌幅'])
        change_amount = float(stock_info['涨跌额'])
        open_price = float(stock_info['今开'])
        high_price = float(stock_info['最高'])
        low_price = float(stock_info['最低'])
        volume = float(stock_info['成交量'])
        amount = float(stock_info['成交额'])
        turnover = float(stock_info['换手率'])
        amplitude = float(stock_info['振幅'])

        print(f"当前价格: {current_price:.2f}元")
        print(f"今日涨跌幅: {change_pct:+.2f}%")
        print(f"涨跌额: {change_amount:+.2f}元")
        print(f"今开: {open_price:.2f}元")
        print(f"最高: {high_price:.2f}元")
        print(f"最低: {low_price:.2f}元")
        print(f"振幅: {amplitude:.2f}%")
        print(f"成交量: {volume/10000:.2f}万手")
        print(f"成交额: {amount/100000000:.2f}亿元")
        print(f"换手率: {turnover:.2f}%")

        # 判断涨跌
        if change_pct > 0:
            trend_mark = "📈 上涨"
        elif change_pct < 0:
            trend_mark = "📉 下跌"
        else:
            trend_mark = "➖平盘"

        print(f"\n今日走势: {trend_mark}")

        # 相对成本价
        vs_cost = (current_price - cost_price) / cost_price * 100
        print(f"相对成本({cost_price}元): {vs_cost:+.2f}%")

        # 2. 与昨天对比
        print("\n【二、与昨天对比】\n")

        print(f"昨天收盘: {yesterday_close:.2f}元")
        print(f"今天价格: {current_price:.2f}元")
        change_vs_yesterday = current_price - yesterday_close
        change_pct_vs_yesterday = (change_vs_yesterday / yesterday_close) * 100
        print(f"对比昨天: {change_vs_yesterday:+.2f}元 ({change_pct_vs_yesterday:+.2f}%)")

        if change_pct > 0:
            print("\n✅ 今天上涨，止跌反弹")
        elif change_pct < 0:
            print("\n❌ 今天继续下跌，延续弱势")
        else:
            print("\n➖ 今天平盘，观望中")

        # 3. 获取今日资金流向
        print("\n【三、今日资金流向】\n")

        try:
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow_rank(indicator="今日")
            maiwei_flow = stock_individual_fund_flow_df[stock_individual_fund_flow_df['代码'] == stock_code]

            if not maiwei_flow.empty:
                flow = maiwei_flow.iloc[0]

                main_flow = float(flow['今日主力净流入-净额']) / 10000
                main_pct = float(flow['今日主力净流入-净占比'])
                super_flow = float(flow['今日超大单净流入-净额']) / 10000
                super_pct = float(flow['今日超大单净流入-净占比'])
                big_flow = float(flow['今日大单净流入-净额']) / 10000
                big_pct = float(flow['今日大单净流入-净占比'])
                mid_flow = float(flow['今日中单净流入-净额']) / 10000
                mid_pct = float(flow['今日中单净流入-净占比'])
                small_flow = float(flow['今日小单净流入-净额']) / 10000
                small_pct = float(flow['今日小单净流入-净占比'])

                print(f"主力净流入: {main_flow:+.2f}万元 ({main_pct:+.2f}%)")
                print(f"  ├─ 超大单: {super_flow:+.2f}万元 ({super_pct:+.2f}%)")
                print(f"  └─ 大单: {big_flow:+.2f}万元 ({big_pct:+.2f}%)")
                print(f"中单净流入: {mid_flow:+.2f}万元 ({mid_pct:+.2f}%)")
                print(f"小单净流入: {small_flow:+.2f}万元 ({small_pct:+.2f}%)")

                # 与昨天对比
                yesterday_main = 5796.10  # 昨天的主力流入
                print("\n【与昨天资金流向对比】")
                print(f"昨天主力: {yesterday_main:+.2f}万元 ✅")
                print(f"今天主力: {main_flow:+.2f}万元", end="")
                if main_flow > 0:
                    print(" ✅")
                else:
                    print(" ❌")

                if main_flow > 0 and yesterday_main > 0:
                    print("\n💡 连续2天主力流入！资金面向好 ✅✅")
                elif main_flow < 0 and yesterday_main > 0:
                    print("\n⚠️  昨天流入，今天流出！资金摇摆 ❌")
                elif main_flow > 0 and yesterday_main < 0:
                    print("\n💡 昨天流出，今天流入！资金转向 ✅")
                else:
                    print("\n❌ 连续2天主力流出！资金面偏弱 ❌❌")

                # 4. 资金与股价配合度分析
                print("\n【四、资金与股价配合度】\n")

                if change_pct > 0 and main_flow > 0:
                    print("✅ 量价齐升：股价上涨 + 主力流入")
                    print("   配合度：完美")
                    print("   信号：强势")
                elif change_pct < 0 and main_flow > 0:
                    print("⭐ 逆势吸筹：股价下跌 + 主力流入")
                    print("   配合度：背离")
                    print("   信号：主力低吸，可能是底部信号")
                elif change_pct > 0 and main_flow < 0:
                    print("⚠️  散户拉升：股价上涨 + 主力流出")
                    print("   配合度：背离")
                    print("   信号：主力出货，需警惕")
                else:
                    print("❌ 量价齐跌：股价下跌 + 主力流出")
                    print("   配合度：完美")
                    print("   信号：弱势")

                # 5. 获取多日资金流向对比
                print("\n【五、多日资金流向对比】\n")

                for indicator in ["3日", "5日", "10日"]:
                    df_flow = ak.stock_individual_fund_flow_rank(indicator=indicator)
                    maiwei_data = df_flow[df_flow['代码'] == stock_code]
                    if not maiwei_data.empty:
                        flow_data = maiwei_data.iloc[0]
                        flow_value = flow_data[f'{indicator}主力净流入-净额'] / 10000
                        print(f"{indicator}主力累计: {flow_value:+.2f}万元", end="")
                        if flow_value > 0:
                            print(" ✅")
                        else:
                            print(" ❌")

        except Exception as e:
            print(f"资金流向数据获取失败: {e}")

        # 6. 综合判断
        print("\n" + "=" * 100)
        print("【六、综合判断与建议】")
        print("=" * 100)

        print("\n1. 今日表现总结:")
        if change_pct >= 2:
            print(f"   ✅ 今日上涨{change_pct:.2f}%，表现强势")
        elif change_pct >= 0:
            print(f"   ➖ 今日小涨{change_pct:.2f}%，震荡偏强")
        elif change_pct >= -2:
            print(f"   ⚠️  今日小跌{abs(change_pct):.2f}%，震荡偏弱")
        else:
            print(f"   ❌ 今日下跌{abs(change_pct):.2f}%，表现较弱")

        print("\n2. 资金面评估:")
        if 'main_flow' in locals():
            if main_flow >= 5000:
                print(f"   ✅ 主力流入{main_flow:.0f}万元，资金面向好")
            elif main_flow > 0:
                print(f"   ➖ 主力小幅流入{main_flow:.0f}万元，资金面偏中性")
            elif main_flow > -5000:
                print(f"   ⚠️  主力小幅流出{abs(main_flow):.0f}万元，资金面偏弱")
            else:
                print(f"   ❌ 主力大幅流出{abs(main_flow):.0f}万元，资金面较弱")

        print("\n3. 关键价位:")
        print(f"   当前价格: {current_price:.2f}元")
        print(f"   持仓成本: {cost_price:.2f}元 (差距{current_price-cost_price:+.2f}元)")
        print(f"   止损位: 150.00元 (差距{current_price-150:.2f}元)")
        print(f"   今日最低: {low_price:.2f}元", end="")
        if low_price <= 150:
            print(" ⚠️  已触及止损位附近")
        else:
            print()

        print("\n4. 操作建议:")

        # 根据今日表现和资金流向给建议
        if 'main_flow' in locals():
            if change_pct > 0 and main_flow > 5000:
                print("   ✅ 股价上涨 + 主力大幅流入")
                print("   建议：继续持有，观察能否持续")
            elif change_pct < 0 and main_flow > 5000:
                print("   ⭐ 股价下跌 + 主力流入（逆势吸筹）")
                print("   建议：可能是底部，继续持有观察")
            elif change_pct < 0 and main_flow < -5000:
                print("   ❌ 股价下跌 + 主力大幅流出")
                print("   建议：警惕风险，严守止损位150元")
            elif change_pct > 0 and main_flow < 0:
                print("   ⚠️  股价上涨 + 主力流出（散户拉升）")
                print("   建议：警惕主力出货，不要追高")
            else:
                print("   ➖ 信号不明确")
                print("   建议：继续观察，严守止损")

            # 连续性判断
            if main_flow > 0 and yesterday_main > 0:
                print("\n   💡 连续2天主力流入，趋势可能反转")
                print("   可继续持有2-3天，观察趋势确认")
            elif main_flow < 0:
                print("\n   ⚠️  今日主力流出，昨天的流入可能是假信号")
                print("   需警惕继续下跌，严守止损位")

        print("\n5. 明天关注点:")
        print("   • 主力资金是否继续流入")
        print("   • 股价能否站稳并突破160元")
        print("   • 成交量是否持续放大")
        print("   • 是否跌破150元（止损位）")

        print("\n" + "=" * 100)
        print("风险提示：请严格执行止损纪律，保护本金")
        print("=" * 100)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
