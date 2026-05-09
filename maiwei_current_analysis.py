#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份当前持仓分析（成本175.21元）
"""

import akshare as ak
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 100)
    print("迈为股份 (300751) 当前持仓分析")
    print("=" * 100)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    stock_code = "300751"
    current_cost = 175.21  # 当前成本
    position = 2  # 2手 = 200股

    print("\n【你的持仓情况】\n")
    print(f"持仓成本: {current_cost:.2f}元")
    print(f"持仓数量: {position}手（{position * 100}股）")

    try:
        # 获取实时行情
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_info = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == stock_code].iloc[0]

        current_price = float(stock_info['最新价'])
        change_pct = float(stock_info['涨跌幅'])
        high_price = float(stock_info['最高'])
        low_price = float(stock_info['最低'])
        amount = float(stock_info['成交额'])
        turnover = float(stock_info['换手率'])

        print(f"当前价格: {current_price:.2f}元")
        print(f"今日涨跌幅: {change_pct:+.2f}%")
        print(f"今日最高: {high_price:.2f}元")
        print(f"今日最低: {low_price:.2f}元")

        # 计算盈亏
        print("\n【盈亏分析】\n")

        loss_per_share = current_price - current_cost
        loss_pct = (loss_per_share / current_cost) * 100
        total_loss = loss_per_share * position * 100

        print(f"单股亏损: {loss_per_share:.2f}元 ({loss_pct:.2f}%)")
        print(f"总体亏损: {total_loss:.2f}元")

        if abs(loss_pct - (-8)) < 1:
            print(f"\n✅ 确认浮亏约8个点")

        # 关键价位
        print("\n【关键价位分析】\n")

        print(f"当前价格: {current_price:.2f}元 ⬅️ 你在这")
        print(f"距离成本: {loss_per_share:.2f}元 ({loss_pct:.2f}%)")
        print()

        # 重要价位
        target_170 = 170.00
        target_175 = 175.21
        target_180 = 180.00
        stop_loss_10 = current_cost * 0.90
        stop_loss_15 = current_cost * 0.85

        print(f"目标价位:")
        print(f"  180.00元: +{(180-current_price)/current_price*100:.2f}% (前高区域)")
        print(f"  175.21元: +{(current_cost-current_price)/current_price*100:.2f}% (你的成本价，回本)")
        print(f"  170.00元: +{(170-current_price)/current_price*100:.2f}% (心理关口)")
        print()
        print(f"止损位参考:")
        print(f"  {stop_loss_10:.2f}元: -10% (建议止损位)")
        print(f"  {stop_loss_15:.2f}元: -15% (最后防线)")

        # 获取资金流向
        print("\n【资金流向】\n")

        try:
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow_rank(indicator="今日")
            maiwei_flow = stock_individual_fund_flow_df[stock_individual_fund_flow_df['代码'] == stock_code]

            if not maiwei_flow.empty:
                flow = maiwei_flow.iloc[0]
                main_flow = float(flow['今日主力净流入-净额']) / 10000
                super_flow = float(flow['今日超大单净流入-净额']) / 10000
                big_flow = float(flow['今日大单净流入-净额']) / 10000

                print(f"今日主力: {main_flow:+.2f}万元")
                print(f"  ├─ 超大单: {super_flow:+.2f}万元")
                print(f"  └─ 大单: {big_flow:+.2f}万元")

                if main_flow > 0:
                    print(f"\n✅ 今日主力净流入，资金面向好")
                else:
                    print(f"\n❌ 今日主力净流出，资金面偏弱")

                # 多日对比
                print("\n多日资金流向:")
                for indicator in ["3日", "5日", "10日"]:
                    df_flow = ak.stock_individual_fund_flow_rank(indicator=indicator)
                    maiwei_data = df_flow[df_flow['代码'] == stock_code]
                    if not maiwei_data.empty:
                        flow_data = maiwei_data.iloc[0]
                        flow_value = flow_data[f'{indicator}主力净流入-净额'] / 10000
                        mark = "✅" if flow_value > 0 else "❌"
                        print(f"   {indicator}: {flow_value:+.2f}万元 {mark}")

        except Exception as e:
            print(f"资金流向数据获取失败: {e}")

        # 回本需要涨幅
        print("\n【回本分析】\n")

        need_rise = (current_cost - current_price) / current_price * 100
        print(f"回到成本价({current_cost:.2f}元)需要:")
        print(f"   股价从 {current_price:.2f}元 涨到 {current_cost:.2f}元")
        print(f"   需要涨幅: {need_rise:.2f}%")
        print(f"   涨幅需要: {current_cost - current_price:.2f}元")

        # 不同价位的盈亏
        print("\n【不同价位盈亏测算】\n")

        scenarios = [
            ("如果涨到170元", 170, (170-current_cost)*position*100),
            ("如果涨到175元（回本）", 175.21, 0),
            ("如果涨到180元", 180, (180-current_cost)*position*100),
            ("如果跌到158元（-10%）", current_cost*0.9, (current_cost*0.9-current_cost)*position*100),
            ("如果跌到150元", 150, (150-current_cost)*position*100),
        ]

        for desc, price, profit in scenarios:
            pct = (price - current_cost) / current_cost * 100
            print(f"{desc}:")
            print(f"   价格: {price:.2f}元 ({pct:+.2f}%)")
            print(f"   盈亏: {profit:+.2f}元")
            print()

        # 操作建议
        print("=" * 100)
        print("【操作建议】")
        print("=" * 100)

        print(f"\n你的持仓成本{current_cost:.2f}元比较高，当前浮亏{abs(loss_pct):.2f}%\n")

        print("【三种策略】\n")

        print("策略A：等待反弹到成本价附近再减仓 ⭐⭐⭐⭐⭐（推荐）")
        print(f"   目标: 170-175元区间")
        print(f"   操作: ")
        print(f"   - 涨到170元，卖出1手（减仓50%）")
        print(f"   - 涨到175元，再卖出1手（完全清仓）")
        print(f"   优点: 分批退出，心理压力小")
        print(f"   风险: 可能等不到")
        print(f"   止损: 设好157.69元（-10%）")
        print()

        print("策略B：设好止损，等待机会 ⭐⭐⭐⭐")
        print(f"   止损位: 157.69元（-10%）")
        print(f"   操作: 跌破止损位立即清仓")
        print(f"   目标: 如果反弹到170元以上考虑减仓")
        print(f"   优点: 控制最大亏损")
        print(f"   风险: 可能震荡止损")
        print()

        print("策略C：趁反弹立即减仓 ⭐⭐⭐")
        print(f"   操作: 股价反弹到165-168元就卖1手")
        print(f"   优点: 快速降低风险敞口")
        print(f"   缺点: 可能卖在半山腰")
        print(f"   适合: 不想承受压力的投资者")
        print()

        # 基于今日资金流向给建议
        if 'main_flow' in locals():
            print("\n【基于今日资金流向的建议】\n")

            if main_flow > 10000:
                print("✅ 今日主力大幅流入（超过1亿）")
                print("   • 资金面向好，可能有反弹")
                print("   • 建议：持股观望，等待反弹")
                print("   • 目标：170元卖1手，175元清仓")
                print("   • 止损：严守157.69元")
            elif main_flow > 5000:
                print("✅ 今日主力流入（5000万以上）")
                print("   • 资金面转好，观察持续性")
                print("   • 建议：再观察1-2天")
                print("   • 如果明天继续流入，可以持有")
                print("   • 止损：设好157.69元")
            elif main_flow > 0:
                print("➖ 今日主力小幅流入")
                print("   • 资金面偏中性")
                print("   • 建议：观望为主")
                print("   • 反弹到165元以上考虑减仓")
            else:
                print("❌ 今日主力流出")
                print("   • 资金面偏弱")
                print("   • 建议：反弹就减仓")
                print("   • 不要等到成本价")

        print("\n" + "=" * 100)
        print("【风险提示】")
        print("=" * 100)

        print(f"""
1. 你的成本{current_cost:.2f}元位于高位
   • 12月11日高点182.79元，你的成本接近高点
   • 需要股价回升较多才能回本

2. 当前浮亏{abs(loss_pct):.2f}%，接近10%
   • 如果继续下跌，亏损会扩大
   • 必须设好止损位保护本金

3. 回本需要涨{need_rise:.2f}%
   • 不是不可能，但需要时间
   • 要有耐心，不要急于求成

4. 建议行动：
   ✅ 设好止损157.69元（-10%）
   ✅ 如果涨到170元，立即减仓50%
   ✅ 如果涨到175元，考虑清仓
   ✅ 不要贪心，见好就收
        """)

        print("=" * 100)
        print("总结：成本偏高，需要耐心等待反弹，严格止损！")
        print("=" * 100)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
