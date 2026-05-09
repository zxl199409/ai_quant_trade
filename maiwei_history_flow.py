#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份 (300751) 历史资金流向分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 100)
    print("迈为股份 (300751) 历史资金流向详细分析")
    print("=" * 100)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    stock_code = "300751"

    try:
        # 获取个股历史资金流向
        print("\n【近期逐日资金流向明细】\n")

        # 尝试获取历史资金流向数据
        try:
            # 使用个股资金流向接口
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow(stock=stock_code, market="sz")

            if not stock_individual_fund_flow_df.empty:
                # 获取最近15天的数据
                recent_flows = stock_individual_fund_flow_df.head(15)

                print("=" * 100)
                print(f"{'日期':<12} {'收盘价':>8} {'涨跌幅':>8} {'主力净额':>12} {'超大单':>12} {'大单':>12} {'中单':>12} {'小单':>12}")
                print("=" * 100)

                for idx, row in recent_flows.iterrows():
                    date_str = str(row['日期'])
                    close_price = float(row['收盘价'])
                    change_pct = float(row['涨跌幅'])
                    main_flow = float(row['主力净流入-净额']) / 10000
                    super_flow = float(row['超大单净流入-净额']) / 10000
                    big_flow = float(row['大单净流入-净额']) / 10000
                    mid_flow = float(row['中单净流入-净额']) / 10000
                    small_flow = float(row['小单净流入-净额']) / 10000

                    # 标记流入流出
                    main_mark = "✅" if main_flow > 0 else "❌"

                    print(f"{date_str:<12} {close_price:>8.2f} {change_pct:>7.2f}% "
                          f"{main_flow:>11.2f}万 {super_flow:>11.2f}万 "
                          f"{big_flow:>11.2f}万 {mid_flow:>11.2f}万 "
                          f"{small_flow:>11.2f}万 {main_mark}")

                print("=" * 100)

                # 重点分析最近3天
                print("\n【最近3个交易日详细分析】\n")

                for i in range(min(3, len(recent_flows))):
                    row = recent_flows.iloc[i]
                    date_str = str(row['日期'])

                    if i == 0:
                        day_name = "今天"
                    elif i == 1:
                        day_name = "昨天"
                    elif i == 2:
                        day_name = "前天"
                    else:
                        day_name = f"{i}天前"

                    print(f"【{day_name} - {date_str}】")
                    print(f"├─ 收盘价: {row['收盘价']:.2f}元")
                    print(f"├─ 涨跌幅: {row['涨跌幅']:.2f}%")
                    print(f"├─ 主力净流入: {row['主力净流入-净额']/10000:.2f}万元 ({row['主力净流入-净占比']:.2f}%)")
                    print(f"│  ├─ 超大单: {row['超大单净流入-净额']/10000:.2f}万元 ({row['超大单净流入-净占比']:.2f}%)")
                    print(f"│  └─ 大单: {row['大单净流入-净额']/10000:.2f}万元 ({row['大单净流入-净占比']:.2f}%)")
                    print(f"├─ 中单净流入: {row['中单净流入-净额']/10000:.2f}万元 ({row['中单净流入-净占比']:.2f}%)")
                    print(f"└─ 小单净流入: {row['小单净流入-净额']/10000:.2f}万元 ({row['小单净流入-净占比']:.2f}%)")

                    # 资金分析
                    main_flow = float(row['主力净流入-净额'])
                    super_flow = float(row['超大单净流入-净额'])
                    price_change = float(row['涨跌幅'])

                    print(f"\n   💡 {day_name}资金特征:")
                    if main_flow > 0 and price_change > 0:
                        print(f"      ✅ 量价齐升 - 主力流入{main_flow/10000:.0f}万，股价涨{price_change:.2f}%")
                    elif main_flow > 0 and price_change < 0:
                        print(f"      ⭐ 逆势吸筹 - 主力流入{main_flow/10000:.0f}万，股价跌{price_change:.2f}%（主力低吸）")
                    elif main_flow < 0 and price_change > 0:
                        print(f"      ⚠️  散户拉升 - 主力流出{abs(main_flow)/10000:.0f}万，股价涨{price_change:.2f}%（需警惕）")
                    else:
                        print(f"      ❌ 量价齐跌 - 主力流出{abs(main_flow)/10000:.0f}万，股价跌{price_change:.2f}%")

                    if super_flow > 5000000:  # 超过500万
                        print(f"      🏢 机构大举买入 - 超大单流入{super_flow/10000:.0f}万（机构看好）")
                    elif super_flow < -5000000:
                        print(f"      🏢 机构大举卖出 - 超大单流出{abs(super_flow)/10000:.0f}万（机构离场）")

                    print()

                # 统计分析
                print("=" * 100)
                print("【统计分析】\n")

                # 近3日统计
                recent_3 = recent_flows.head(3)
                main_3d = recent_3['主力净流入-净额'].sum() / 10000
                super_3d = recent_3['超大单净流入-净额'].sum() / 10000
                big_3d = recent_3['大单净流入-净额'].sum() / 10000

                print("近3个交易日累计:")
                print(f"   主力净流入: {main_3d:.2f}万元")
                print(f"   超大单净流入: {super_3d:.2f}万元")
                print(f"   大单净流入: {big_3d:.2f}万元")

                main_in_3d = len(recent_3[recent_3['主力净流入-净额'] > 0])
                print(f"   主力流入天数: {main_in_3d}/3天")

                # 近5日统计
                recent_5 = recent_flows.head(5)
                main_5d = recent_5['主力净流入-净额'].sum() / 10000
                super_5d = recent_5['超大单净流入-净额'].sum() / 10000
                big_5d = recent_5['大单净流入-净额'].sum() / 10000

                print("\n近5个交易日累计:")
                print(f"   主力净流入: {main_5d:.2f}万元")
                print(f"   超大单净流入: {super_5d:.2f}万元")
                print(f"   大单净流入: {big_5d:.2f}万元")

                main_in_5d = len(recent_5[recent_5['主力净流入-净额'] > 0])
                print(f"   主力流入天数: {main_in_5d}/5天")

                # 近10日统计
                recent_10 = recent_flows.head(10)
                main_10d = recent_10['主力净流入-净额'].sum() / 10000
                super_10d = recent_10['超大单净流入-净额'].sum() / 10000
                big_10d = recent_10['大单净流入-净额'].sum() / 10000

                print("\n近10个交易日累计:")
                print(f"   主力净流入: {main_10d:.2f}万元")
                print(f"   超大单净流入: {super_10d:.2f}万元")
                print(f"   大单净流入: {big_10d:.2f}万元")

                main_in_10d = len(recent_10[recent_10['主力净流入-净额'] > 0])
                print(f"   主力流入天数: {main_in_10d}/10天")

                # 资金流向趋势判断
                print("\n" + "=" * 100)
                print("【资金趋势判断】\n")

                if main_3d > 0 and main_5d > 0 and main_10d > 0:
                    print("✅ 短中期资金持续流入，趋势向好")
                    print("   主力连续建仓，看好后市")
                elif main_3d > 0 and main_5d < 0:
                    print("⚠️  短期资金转强，但中期仍在流出")
                    print("   需观察短期流入能否持续")
                elif main_3d < 0 and main_10d > 0:
                    print("⚠️  中期资金向好，但短期有调整")
                    print("   可能是回调洗盘，关注是否重新流入")
                else:
                    print("❌ 资金面偏弱，建议谨慎")

                # 超大单分析
                if super_3d > 10000 and super_5d > 10000:
                    print("\n✅ 机构资金持续流入")
                    print(f"   近3日机构流入{super_3d:.0f}万，近5日流入{super_5d:.0f}万")
                    print("   机构看好，资金面强劲")
                elif super_3d < -10000:
                    print("\n⚠️  机构资金近期流出")
                    print(f"   近3日机构流出{abs(super_3d):.0f}万")
                    print("   需警惕机构撤离")

                print("\n" + "=" * 100)

        except Exception as e:
            print(f"数据获取失败: {str(e)}")
            print("尝试使用备用方法...")

            # 备用方法：通过排名接口获取数据
            try:
                for indicator in ["今日", "3日", "5日", "10日"]:
                    print(f"\n【{indicator}资金流向】")
                    df = ak.stock_individual_fund_flow_rank(indicator=indicator)
                    maiwei = df[df['代码'] == stock_code]
                    if not maiwei.empty:
                        row = maiwei.iloc[0]
                        print(f"主力净流入: {row[f'{indicator}主力净流入-净额']/10000:.2f}万元")
                        print(f"超大单净流入: {row[f'{indicator}超大单净流入-净额']/10000:.2f}万元")
                        print(f"大单净流入: {row[f'{indicator}大单净流入-净额']/10000:.2f}万元")
            except Exception as e2:
                print(f"备用方法也失败: {str(e2)}")

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
