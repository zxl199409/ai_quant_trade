#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份减仓后分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 100)
    print("迈为股份 (300751) 减仓后持仓分析")
    print("=" * 100)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    stock_code = "300751"
    original_cost = 170.0
    sell_price = 164.60
    sell_ratio = 0.5  # 卖出一半

    print("\n【一、你的操作回顾】\n")
    print(f"原始成本: {original_cost:.2f}元")
    print(f"减仓价格: {sell_price:.2f}元")
    print(f"减仓比例: {sell_ratio*100:.0f}%（一半仓位）")

    sell_loss = sell_price - original_cost
    sell_loss_pct = (sell_loss / original_cost) * 100
    print(f"卖出部分亏损: {sell_loss:.2f}元 ({sell_loss_pct:.2f}%)")

    try:
        # 获取今日实时行情
        print("\n【二、当前市场行情】\n")

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
        print(f"成交额: {amount/100000000:.2f}亿元")
        print(f"换手率: {turnover:.2f}%")

        # 计算当前持仓情况
        print("\n【三、当前持仓分析】\n")

        # 已卖出部分
        print("已卖出部分（50%）:")
        print(f"   卖出价格: {sell_price:.2f}元")
        print(f"   盈亏: {sell_loss:.2f}元/股 ({sell_loss_pct:.2f}%)")
        print(f"   状态: ✅ 已锁定亏损")

        # 持有部分
        print(f"\n持有部分（50%）:")
        print(f"   持仓成本: {original_cost:.2f}元")
        print(f"   当前价格: {current_price:.2f}元")
        hold_loss = current_price - original_cost
        hold_loss_pct = (hold_loss / original_cost) * 100
        print(f"   浮动盈亏: {hold_loss:.2f}元/股 ({hold_loss_pct:.2f}%)")

        # 整体仓位
        print(f"\n整体仓位计算:")
        # 卖出部分的亏损
        sold_part_loss_pct = sell_loss_pct * sell_ratio
        # 持有部分的浮亏
        hold_part_loss_pct = hold_loss_pct * (1 - sell_ratio)
        # 总亏损
        total_loss_pct = sold_part_loss_pct + hold_part_loss_pct

        print(f"   已卖部分贡献: {sold_part_loss_pct:.2f}%")
        print(f"   持有部分贡献: {hold_part_loss_pct:.2f}%")
        print(f"   总体盈亏: {total_loss_pct:.2f}%")

        if abs(total_loss_pct - (-8.0)) < 1:
            print(f"   ✅ 与你说的「亏8个点」基本一致")

        # 与164.60卖出时对比
        print("\n【四、卖出决策评估】\n")

        if current_price > sell_price:
            diff = current_price - sell_price
            diff_pct = (diff / sell_price) * 100
            print(f"❌ 现在价格 {current_price:.2f}元 > 卖出价 {sell_price:.2f}元")
            print(f"   差距: +{diff:.2f}元 (+{diff_pct:.2f}%)")
            print(f"   评价: 卖早了，但减仓降低风险是对的")
        elif current_price < sell_price:
            diff = sell_price - current_price
            diff_pct = (diff / sell_price) * 100
            print(f"✅ 现在价格 {current_price:.2f}元 < 卖出价 {sell_price:.2f}元")
            print(f"   差距: -{diff:.2f}元 (-{diff_pct:.2f}%)")
            print(f"   评价: 卖得好！避免了更大亏损")
        else:
            print(f"➖ 价格与卖出价持平")

        # 如果没卖会怎样
        print(f"\n如果没有卖出（对比分析）:")
        print(f"   全仓持有到现在: 浮亏 {hold_loss_pct:.2f}%")
        print(f"   减仓后实际亏损: {total_loss_pct:.2f}%")
        saved_loss = hold_loss_pct - total_loss_pct
        print(f"   减仓后减少亏损: {saved_loss:.2f}%")

        if saved_loss > 0:
            print(f"   ✅ 减仓是正确的决定，减少了 {saved_loss:.2f}% 的亏损！")
        else:
            print(f"   ⚠️  如果不减仓，亏损会更少 {abs(saved_loss):.2f}%")

        # 获取资金流向
        print("\n【五、今日资金流向】\n")

        try:
            stock_individual_fund_flow_df = ak.stock_individual_fund_flow_rank(indicator="今日")
            maiwei_flow = stock_individual_fund_flow_df[stock_individual_fund_flow_df['代码'] == stock_code]

            if not maiwei_flow.empty:
                flow = maiwei_flow.iloc[0]
                main_flow = float(flow['今日主力净流入-净额']) / 10000
                super_flow = float(flow['今日超大单净流入-净额']) / 10000
                big_flow = float(flow['今日大单净流入-净额']) / 10000

                print(f"主力净流入: {main_flow:+.2f}万元")
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

        # 剩余仓位建议
        print("\n" + "=" * 100)
        print("【六、剩余50%仓位操作建议】")
        print("=" * 100)

        print(f"\n当前持仓状态:")
        print(f"   持有比例: 50%")
        print(f"   持仓成本: {original_cost:.2f}元")
        print(f"   当前价格: {current_price:.2f}元")
        print(f"   浮动亏损: {hold_loss_pct:.2f}%")

        print(f"\n关键价位:")
        print(f"   当前价格: {current_price:.2f}元")
        print(f"   上次减仓: {sell_price:.2f}元")
        print(f"   持仓成本: {original_cost:.2f}元（需涨{(original_cost-current_price)/current_price*100:.2f}%）")
        print(f"   建议止损: {original_cost*0.9:.2f}元（-10%）")

        print(f"\n操作策略建议:\n")

        # 根据资金流向和价格给建议
        if 'main_flow' in locals():
            if current_price >= sell_price + 5 and main_flow > 5000:
                print("📈 【场景：价格反弹且主力流入】")
                print("   • 当前走势向好")
                print("   • 可以继续持有剩余50%")
                print("   • 目标：先看170元成本价")
                print("   • 止盈：如果涨到170元，可以考虑再卖一半")
                print("   • 止损：严格执行153元（-10%）")

            elif current_price < sell_price and main_flow < 0:
                print("📉 【场景：价格下跌且主力流出】")
                print("   • 当前走势偏弱")
                print("   • 建议：设好止损位")
                print("   • 止损位：153元（-10%）或150元")
                print("   • 如果跌破止损位，剩余仓位也要卖出")
                print("   • 保护原则：不能让剩余部分再亏10%以上")

            elif current_price >= sell_price and main_flow < 0:
                print("⚠️  【场景：价格反弹但主力流出】")
                print("   • 可能是反弹诱多")
                print("   • 建议：反弹到168-170元附近再减仓")
                print("   • 目标：接近成本价时再卖出部分")
                print("   • 止损：严守153元")

            else:
                print("➖ 【场景：震荡整理】")
                print("   • 当前方向不明")
                print("   • 建议：观望为主")
                print("   • 止损：设好153元止损位")
                print("   • 反弹：如果涨到168-170元考虑减仓")

        print("\n【三种策略对比】\n")

        print("策略A：继续持有剩余50%，等回本")
        print(f"   目标: {original_cost:.2f}元")
        print(f"   需要涨幅: {(original_cost-current_price)/current_price*100:.2f}%")
        print(f"   风险: 可能继续下跌")
        print(f"   适合: 风险承受能力较强")

        print("\n策略B：反弹到成本价附近再减仓")
        print(f"   目标: 168-170元")
        print(f"   操作: 涨到168元卖出剩余25%，170元卖出剩余25%")
        print(f"   优点: 分批退出，降低风险")
        print(f"   适合: 稳健型投资者")

        print("\n策略C：设好止损，被动防守")
        print(f"   止损位: 153元（-10%）")
        print(f"   操作: 跌破153元立即清仓")
        print(f"   优点: 控制最大亏损")
        print(f"   适合: 风险厌恶型")

        print("\n" + "=" * 100)
        print("【七、综合评价与建议】")
        print("=" * 100)

        print("\n1. 减仓决策评价:")
        print(f"   ✅ 在164.60元减仓一半是明智的")
        print(f"   ✅ 降低了仓位风险")
        print(f"   ✅ 锁定了部分亏损，避免更大损失")
        if current_price < sell_price:
            print(f"   ✅ 现在看来减仓价格还不错")

        print(f"\n2. 当前局势:")
        print(f"   • 整体亏损: {total_loss_pct:.2f}%（可控）")
        print(f"   • 持仓比例: 50%（风险降低）")
        print(f"   • 心理压力: 应该比之前小很多")

        print(f"\n3. 我的最终建议:")
        print(f"   🎯 【推荐：分批减仓策略】")
        print(f"   ")
        print(f"   第一步：设好止损153元（必须）")
        print(f"   第二步：如果涨到168元，再卖25%")
        print(f"   第三步：如果涨到170元，再卖25%")
        print(f"   第四步：剩余部分看情况")
        print(f"   ")
        print(f"   这样做的好处：")
        print(f"   ✅ 分批退出，心理压力小")
        print(f"   ✅ 如果反弹能减少亏损")
        print(f"   ✅ 如果下跌有止损保护")

        print("\n4. 风险控制:")
        print(f"   ⚠️  剩余50%仓位的止损位是关键")
        print(f"   ⚠️  不能让剩余部分亏损超过10%")
        print(f"   ⚠️  如果跌破153元，必须清仓")

        print("\n" + "=" * 100)
        print("总结：你已经做了正确的风险控制，继续保持理性！")
        print("=" * 100)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
