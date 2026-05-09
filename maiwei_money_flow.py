#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份 (300751) 资金流向分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 80)
    print("迈为股份 (300751) 资金流向深度分析")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    stock_code = "300751"
    stock_name = "迈为股份"

    try:
        # 1. 获取个股资金流向
        print("\n【一、个股资金流向分析】")
        print("\n1. 近期资金流向明细:")

        try:
            # 获取个股资金流向
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow_rank(indicator="今日")
            maiwei_flow = stock_individual_fund_flow_df[stock_individual_fund_flow_df['代码'] == stock_code]

            if not maiwei_flow.empty:
                flow = maiwei_flow.iloc[0]
                print(f"\n今日实时资金流向:")
                print(f"   最新价: {flow['最新价']:.2f}元")
                print(f"   今日涨跌幅: {flow['今日涨跌幅']:.2f}%")
                print(f"   今日主力净流入-净额: {flow['今日主力净流入-净额']/10000:.2f}万元")
                print(f"   今日主力净流入-净占比: {flow['今日主力净流入-净占比']:.2f}%")
                print(f"   今日超大单净流入-净额: {flow['今日超大单净流入-净额']/10000:.2f}万元")
                print(f"   今日超大单净流入-净占比: {flow['今日超大单净流入-净占比']:.2f}%")
                print(f"   今日大单净流入-净额: {flow['今日大单净流入-净额']/10000:.2f}万元")
                print(f"   今日大单净流入-净占比: {flow['今日大单净流入-净占比']:.2f}%")
                print(f"   今日中单净流入-净额: {flow['今日中单净流入-净额']/10000:.2f}万元")
                print(f"   今日中单净流入-净占比: {flow['今日中单净流入-净占比']:.2f}%")
                print(f"   今日小单净流入-净额: {flow['今日小单净流入-净额']/10000:.2f}万元")
                print(f"   今日小单净流入-净占比: {flow['今日小单净流入-净占比']:.2f}%")
        except Exception as e:
            print(f"   今日资金流向数据获取失败: {str(e)}")

        # 2. 获取历史资金流向
        print("\n2. 近5日资金流向趋势:")
        try:
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow_rank(indicator="5日")
            maiwei_flow_5d = stock_individual_fund_flow_df[stock_individual_fund_flow_df['代码'] == stock_code]

            if not maiwei_flow_5d.empty:
                flow_5d = maiwei_flow_5d.iloc[0]
                print(f"   5日主力净流入: {flow_5d['5日主力净流入-净额']/10000:.2f}万元")
                print(f"   5日主力净占比: {flow_5d['5日主力净流入-净占比']:.2f}%")
                print(f"   5日超大单净流入: {flow_5d['5日超大单净流入-净额']/10000:.2f}万元")
                print(f"   5日大单净流入: {flow_5d['5日大单净流入-净额']/10000:.2f}万元")
                print(f"   5日中单净流入: {flow_5d['5日中单净流入-净额']/10000:.2f}万元")
                print(f"   5日小单净流入: {flow_5d['5日小单净流入-净额']/10000:.2f}万元")
        except Exception as e:
            print(f"   5日资金流向数据获取失败: {str(e)}")

        print("\n3. 近10日资金流向趋势:")
        try:
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow_rank(indicator="10日")
            maiwei_flow_10d = stock_individual_fund_flow_df[stock_individual_fund_flow_df['代码'] == stock_code]

            if not maiwei_flow_10d.empty:
                flow_10d = maiwei_flow_10d.iloc[0]
                print(f"   10日主力净流入: {flow_10d['10日主力净流入-净额']/10000:.2f}万元")
                print(f"   10日主力净占比: {flow_10d['10日主力净流入-净占比']:.2f}%")
                print(f"   10日超大单净流入: {flow_10d['10日超大单净流入-净额']/10000:.2f}万元")
                print(f"   10日大单净流入: {flow_10d['10日大单净流入-净额']/10000:.2f}万元")
        except Exception as e:
            print(f"   10日资金流向数据获取失败: {str(e)}")

        # 3. 获取个股历史资金流向详细数据
        print("\n【二、历史资金流向详细数据】")
        try:
            stock_individual_fund_flow = ak.stock_individual_fund_flow(stock=stock_code, market="sh_sz")

            if not stock_individual_fund_flow.empty:
                recent_flows = stock_individual_fund_flow.head(10)
                print("\n最近10个交易日资金流向:")
                print(f"{'日期':<12} {'收盘价':>8} {'涨跌幅':>8} {'主力净流入':>12} {'超大单':>12} {'大单':>12} {'中单':>12} {'小单':>12}")
                print("-" * 100)

                for _, row in recent_flows.iterrows():
                    print(f"{row['日期']:<12} {row['收盘价']:>8.2f} {row['涨跌幅']:>7.2f}% "
                          f"{row['主力净流入-净额']/10000:>11.2f}万 {row['超大单净流入-净额']/10000:>11.2f}万 "
                          f"{row['大单净流入-净额']/10000:>11.2f}万 {row['中单净流入-净额']/10000:>11.2f}万 "
                          f"{row['小单净流入-净额']/10000:>11.2f}万")

                # 统计分析
                print("\n统计分析（近10日）:")
                main_flow_sum = recent_flows['主力净流入-净额'].sum() / 10000
                super_flow_sum = recent_flows['超大单净流入-净额'].sum() / 10000
                big_flow_sum = recent_flows['大单净流入-净额'].sum() / 10000
                mid_flow_sum = recent_flows['中单净流入-净额'].sum() / 10000
                small_flow_sum = recent_flows['小单净流入-净额'].sum() / 10000

                print(f"   主力净流入合计: {main_flow_sum:.2f}万元")
                print(f"   超大单净流入合计: {super_flow_sum:.2f}万元")
                print(f"   大单净流入合计: {big_flow_sum:.2f}万元")
                print(f"   中单净流入合计: {mid_flow_sum:.2f}万元")
                print(f"   小单净流入合计: {small_flow_sum:.2f}万元")

                # 主力流入天数统计
                main_in_days = len(recent_flows[recent_flows['主力净流入-净额'] > 0])
                main_out_days = len(recent_flows[recent_flows['主力净流入-净额'] < 0])
                print(f"\n   主力流入天数: {main_in_days}天")
                print(f"   主力流出天数: {main_out_days}天")

        except Exception as e:
            print(f"   历史资金流向数据获取失败: {str(e)}")

        # 4. 获取龙虎榜数据
        print("\n【三、龙虎榜数据】")
        try:
            # 获取最近的龙虎榜数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

            stock_lhb_detail = ak.stock_lhb_detail_em(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date
            )

            if not stock_lhb_detail.empty:
                print(f"\n最近30天上榜 {len(stock_lhb_detail)} 次:")
                for _, row in stock_lhb_detail.iterrows():
                    print(f"\n   上榜日期: {row['上榜日']}")
                    print(f"   解读: {row['解读']}")
                    print(f"   收盘价: {row['收盘价']}元")
                    print(f"   涨跌幅: {row['涨跌幅']}%")
                    print(f"   龙虎榜净买额: {row['龙虎榜净买额']/10000:.2f}万元")
                    print(f"   龙虎榜买入额: {row['龙虎榜买入额']/10000:.2f}万元")
                    print(f"   龙虎榜卖出额: {row['龙虎榜卖出额']/10000:.2f}万元")
            else:
                print("   近30天未上榜")
        except Exception as e:
            print(f"   龙虎榜数据获取失败: {str(e)}")

        # 5. 北向资金持股
        print("\n【四、北向资金（沪深股通）】")
        try:
            stock_hsgt_hold_detail = ak.stock_hsgt_hold_detail_em(
                symbol=stock_code,
                indicator="沪股通"
            )

            if not stock_hsgt_hold_detail.empty:
                recent_hsgt = stock_hsgt_hold_detail.head(10)
                print("\n最近10个交易日北向资金持股:")
                print(f"{'日期':<12} {'持股数量(股)':>15} {'持股市值(元)':>15} {'占流通股比':>12} {'占总股本比':>12}")
                print("-" * 80)

                for _, row in recent_hsgt.iterrows():
                    print(f"{row['日期']:<12} {row['持股数量']:>15.0f} {row['持股市值']:>15.0f} "
                          f"{row['持股数量占A股百分比']:>11.2f}% {row['持股数量占总股本百分比']:>11.2f}%")

                # 计算增减持
                if len(recent_hsgt) >= 2:
                    latest_hold = recent_hsgt.iloc[0]['持股数量']
                    prev_hold = recent_hsgt.iloc[1]['持股数量']
                    change = latest_hold - prev_hold
                    change_pct = (change / prev_hold * 100) if prev_hold > 0 else 0

                    print(f"\n   最新持股变化: {change:,.0f}股 ({change_pct:+.2f}%)")
                    if change > 0:
                        print(f"   状态: ✅ 北向资金增持")
                    elif change < 0:
                        print(f"   状态: ⚠️ 北向资金减持")
                    else:
                        print(f"   状态: ➖ 北向资金持平")
            else:
                print("   暂无北向资金持股数据")
        except Exception as e:
            print(f"   北向资金数据获取失败: {str(e)}")

        # 6. 综合评估
        print("\n" + "=" * 80)
        print("【五、资金面综合评估】")
        print("=" * 80)

        print("\n资金流向解读:")

        # 根据获取的数据给出评估
        if 'flow' in locals():
            main_flow_today = flow['今日主力净流入-净额'] / 10000
            super_flow_today = flow['今日超大单净流入-净额'] / 10000

            print(f"\n1. 今日资金动向:")
            if main_flow_today > 0:
                print(f"   ✅ 主力资金净流入 {main_flow_today:.2f}万元")
                if super_flow_today > 0:
                    print(f"   ✅ 超大单资金净流入 {super_flow_today:.2f}万元（机构或大资金看好）")
                else:
                    print(f"   ⚠️ 超大单资金净流出 {abs(super_flow_today):.2f}万元")
            else:
                print(f"   ⚠️ 主力资金净流出 {abs(main_flow_today):.2f}万元")
                print(f"   资金呈流出态势，需警惕调整风险")

        if 'main_flow_sum' in locals():
            print(f"\n2. 近期资金趋势（10日）:")
            if main_flow_sum > 0:
                print(f"   ✅ 主力资金累计净流入 {main_flow_sum:.2f}万元")
                print(f"   资金面整体向好")
                if main_in_days >= 6:
                    print(f"   主力连续流入天数较多（{main_in_days}天），持续性较好")
            else:
                print(f"   ⚠️ 主力资金累计净流出 {abs(main_flow_sum):.2f}万元")
                print(f"   资金面承压")

        print("\n3. 操作建议:")
        if 'main_flow_today' in locals() and 'main_flow_sum' in locals():
            if main_flow_today > 0 and main_flow_sum > 0:
                print("   ✅ 资金面配合较好，可继续持有")
                print("   关注后续是否能持续获得资金青睐")
            elif main_flow_today < 0 and main_flow_sum < 0:
                print("   ⚠️ 资金面偏弱，建议谨慎观望")
                print("   等待资金重新流入信号再考虑加仓")
            else:
                print("   ➖ 资金面信号不一致，建议观望")
                print("   等待方向明朗后再做决策")

        print("\n" + "=" * 80)
        print("风险提示: 资金流向数据仅供参考，不构成投资建议。")
        print("请结合技术面、基本面综合判断，控制好仓位风险。")
        print("=" * 80)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
