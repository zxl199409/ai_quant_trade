#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份 2周完整分析（K线+资金流向）
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 120)
    print("迈为股份 (300751) 最近2周完整分析")
    print("=" * 120)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)

    stock_code = "300751"
    cost_price = 170.0

    try:
        # 1. 获取K线数据
        print("\n【一、最近2周K线走势】\n")

        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=20)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if df.empty:
            print("无法获取K线数据")
            return

        df = df.rename(columns={
            '日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume',
            '成交额': 'amount', '振幅': 'amplitude', '涨跌幅': 'change_pct',
            '涨跌额': 'change', '换手率': 'turnover'
        })

        # 获取最近12个交易日
        recent_df = df.tail(12).copy()

        print("=" * 120)
        print(f"{'日期':<12} {'开盘':>8} {'收盘':>8} {'涨跌幅':>8} {'振幅':>8} "
              f"{'成交额(亿)':>12} {'换手率':>8} {'相对成本':>10} {'标记':>15}")
        print("=" * 120)

        for idx, row in recent_df.iterrows():
            amount_yi = row['amount'] / 100000000
            vs_cost = (row['close'] - cost_price) / cost_price * 100

            # 标记
            mark = ""
            if row['change_pct'] >= 10:
                mark = "🚀 涨停"
            elif row['change_pct'] >= 5:
                mark = "📈 大涨"
            elif row['change_pct'] >= 2:
                mark = "📈 上涨"
            elif row['change_pct'] <= -10:
                mark = "💥 暴跌"
            elif row['change_pct'] <= -5:
                mark = "📉 大跌"
            elif row['change_pct'] <= -2:
                mark = "📉 下跌"
            else:
                mark = "➖ 震荡"

            # 标注成本价位置
            cost_mark = ""
            if vs_cost >= 0:
                cost_mark = f"+{vs_cost:.1f}%"
            else:
                cost_mark = f"{vs_cost:.1f}%"

            print(f"{row['date']:<12} {row['open']:>8.2f} {row['close']:>8.2f} "
                  f"{row['change_pct']:>7.2f}% {row['amplitude']:>7.2f}% "
                  f"{amount_yi:>11.2f} {row['turnover']:>7.2f}% "
                  f"{cost_mark:>10} {mark:>15}")

        print("=" * 120)

        # 2. 关键价格分析
        print("\n【二、关键价格统计】\n")

        highest = recent_df['high'].max()
        lowest = recent_df['low'].min()
        current = recent_df.iloc[-1]['close']
        start_price = recent_df.iloc[0]['close']

        total_change = (current - start_price) / start_price * 100
        vs_cost = (current - cost_price) / cost_price * 100
        position = (current - lowest) / (highest - lowest) * 100

        print(f"2周期间最高价: {highest:.2f}元")
        print(f"2周期间最低价: {lowest:.2f}元")
        print(f"2周期首日收盘: {start_price:.2f}元")
        print(f"当前价格: {current:.2f}元")
        print(f"2周累计涨跌幅: {total_change:+.2f}%")
        print(f"相对持仓成本({cost_price}元): {vs_cost:+.2f}%")
        print(f"当前价格位置: {position:.1f}% (0%=最低, 100%=最高)")

        # 3. 成交量分析
        print("\n【三、成交量分析】\n")

        avg_amount = recent_df['amount'].mean() / 100000000
        avg_turnover = recent_df['turnover'].mean()
        total_amount = recent_df['amount'].sum() / 100000000

        max_amount_day = recent_df.loc[recent_df['amount'].idxmax()]
        min_amount_day = recent_df.loc[recent_df['amount'].idxmin()]

        print(f"2周平均成交额: {avg_amount:.2f}亿元/天")
        print(f"2周平均换手率: {avg_turnover:.2f}%")
        print(f"2周总成交额: {total_amount:.2f}亿元")
        print(f"\n最大成交额: {max_amount_day['amount']/100000000:.2f}亿元 ({max_amount_day['date']})")
        print(f"   当日涨跌幅: {max_amount_day['change_pct']:.2f}%")
        print(f"最小成交额: {min_amount_day['amount']/100000000:.2f}亿元 ({min_amount_day['date']})")
        print(f"   当日涨跌幅: {min_amount_day['change_pct']:.2f}%")

        # 4. 获取资金流向汇总数据
        print("\n【四、资金流向分析】\n")

        try:
            # 获取今日、3日、5日、10日数据
            flow_data = {}
            for indicator in ["今日", "3日", "5日", "10日"]:
                df_flow = ak.stock_individual_fund_flow_rank(indicator=indicator)
                maiwei_flow = df_flow[df_flow['代码'] == stock_code]

                if not maiwei_flow.empty:
                    flow = maiwei_flow.iloc[0]
                    flow_data[indicator] = {
                        'main': flow[f'{indicator}主力净流入-净额'] / 10000,
                        'super': flow[f'{indicator}超大单净流入-净额'] / 10000,
                        'big': flow[f'{indicator}大单净流入-净额'] / 10000,
                        'mid': flow[f'{indicator}中单净流入-净额'] / 10000,
                        'small': flow[f'{indicator}小单净流入-净额'] / 10000,
                    }

            # 显示资金流向
            print("资金流向汇总:")
            print(f"{'周期':<8} {'主力净流入':>12} {'超大单':>12} {'大单':>12} {'中单':>12} {'小单':>12}")
            print("-" * 80)

            for indicator in ["今日", "3日", "5日", "10日"]:
                if indicator in flow_data:
                    d = flow_data[indicator]
                    print(f"{indicator:<8} {d['main']:>11.2f}万 {d['super']:>11.2f}万 "
                          f"{d['big']:>11.2f}万 {d['mid']:>11.2f}万 {d['small']:>11.2f}万")

            # 推算各阶段
            if "今日" in flow_data and "3日" in flow_data and "5日" in flow_data and "10日" in flow_data:
                print("\n" + "=" * 80)
                print("分阶段资金流向推算:")
                print("=" * 80)

                # 今日
                today = flow_data["今日"]
                print(f"\n今日: 主力 {today['main']:+.2f}万元")

                # 前2日
                day2_3 = flow_data["3日"]['main'] - today['main']
                print(f"昨天+前天: 主力 {day2_3:+.2f}万元")

                # 第3-5日
                day3_5 = flow_data["5日"]['main'] - flow_data["3日"]['main']
                print(f"第3-5日: 主力 {day3_5:+.2f}万元")

                # 第6-10日
                day6_10 = flow_data["10日"]['main'] - flow_data["5日"]['main']
                print(f"第6-10日: 主力 {day6_10:+.2f}万元")

                print("\n" + "=" * 80)

        except Exception as e:
            print(f"资金流向数据获取失败: {e}")

        # 5. K线形态分析
        print("\n【五、K线形态分析】\n")

        # 找出大涨大跌日
        big_up = recent_df[recent_df['change_pct'] >= 5]
        big_down = recent_df[recent_df['change_pct'] <= -5]

        if not big_up.empty:
            print(f"大涨日（涨幅≥5%）: {len(big_up)}天")
            for idx, row in big_up.iterrows():
                print(f"   {row['date']}: +{row['change_pct']:.2f}% (收盘{row['close']:.2f}元)")
        else:
            print("大涨日（涨幅≥5%）: 0天")

        if not big_down.empty:
            print(f"\n大跌日（跌幅≥5%）: {len(big_down)}天")
            for idx, row in big_down.iterrows():
                print(f"   {row['date']}: {row['change_pct']:.2f}% (收盘{row['close']:.2f}元)")
        else:
            print("\n大跌日（跌幅≥5%）: 0天")

        # 涨跌统计
        up_days = len(recent_df[recent_df['change_pct'] > 0])
        down_days = len(recent_df[recent_df['change_pct'] < 0])
        flat_days = len(recent_df[recent_df['change_pct'] == 0])

        print(f"\n涨跌统计:")
        print(f"   上涨天数: {up_days}天")
        print(f"   下跌天数: {down_days}天")
        print(f"   平盘天数: {flat_days}天")
        print(f"   胜率: {up_days/len(recent_df)*100:.1f}%")

        # 6. 综合分析
        print("\n" + "=" * 120)
        print("【六、综合分析与判断】")
        print("=" * 120)

        print("\n1. 趋势判断:")

        if total_change > 20:
            print(f"   ✅ 2周上涨{total_change:.1f}%，处于明显上升趋势")
        elif total_change > 10:
            print(f"   ✅ 2周上涨{total_change:.1f}%，趋势向好")
        elif total_change > 0:
            print(f"   ➖ 2周上涨{total_change:.1f}%，震荡偏强")
        elif total_change > -10:
            print(f"   ⚠️  2周下跌{abs(total_change):.1f}%，震荡偏弱")
        else:
            print(f"   ❌ 2周下跌{abs(total_change):.1f}%，处于下降趋势")

        print("\n2. 价格位置:")
        if position > 70:
            print(f"   ⚠️  当前位于2周高位区域({position:.1f}%)，注意回调风险")
        elif position > 30:
            print(f"   ➖ 当前位于2周中位区域({position:.1f}%)，震荡整理")
        else:
            print(f"   ✅ 当前位于2周低位区域({position:.1f}%)，可能存在反弹机会")

        print("\n3. 成交量特征:")
        if len(big_down) > 0 and big_down.iloc[0]['amount'] > avg_amount * 100000000 * 1.5:
            print(f"   ⚠️  出现放量大跌，警惕主力出货风险")
        elif len(big_up) > 0 and big_up.iloc[-1]['amount'] > avg_amount * 100000000 * 1.5:
            print(f"   ✅ 放量上涨，资金活跃")
        else:
            print(f"   ➖ 成交量平稳")

        print("\n4. 资金面判断:")
        if "10日" in flow_data:
            flow_10d = flow_data["10日"]['main']
            if flow_10d > 30000:
                print(f"   ✅ 10日主力流入{flow_10d:.0f}万元，资金面强劲")
            elif flow_10d > 10000:
                print(f"   ✅ 10日主力流入{flow_10d:.0f}万元，资金面向好")
            elif flow_10d > 0:
                print(f"   ➖ 10日主力小幅流入{flow_10d:.0f}万元")
            elif flow_10d > -10000:
                print(f"   ⚠️  10日主力小幅流出{abs(flow_10d):.0f}万元")
            else:
                print(f"   ❌ 10日主力大幅流出{abs(flow_10d):.0f}万元，资金面偏弱")

            if "今日" in flow_data:
                today_flow = flow_data["今日"]['main']
                if today_flow > 0 and flow_10d > 0:
                    print(f"   ✅ 今日主力流入，与10日趋势一致")
                elif today_flow > 0 and flow_10d < 0:
                    print(f"   ⚠️  今日主力流入，但10日累计流出，需观察持续性")
                elif today_flow < 0 and flow_10d > 0:
                    print(f"   ⚠️  今日主力流出，但10日累计流入，可能短期调整")
                else:
                    print(f"   ❌ 今日主力流出，且10日累计流出，资金面偏弱")

        print("\n5. 持仓建议（成本{:.2f}元）:".format(cost_price))
        if vs_cost >= 0:
            print(f"   ✅ 当前已盈利{vs_cost:.1f}%")
            if position > 70:
                print(f"   建议: 考虑减仓，锁定利润")
            else:
                print(f"   建议: 可继续持有，设好止盈位")
        else:
            print(f"   ❌ 当前浮亏{abs(vs_cost):.1f}%")
            if abs(vs_cost) > 15:
                print(f"   建议: 浮亏超15%，建议止损或严格设置止损位")
            elif abs(vs_cost) > 10:
                print(f"   建议: 浮亏超10%，密切关注，设好止损位")
            else:
                print(f"   建议: 浮亏可控，可继续观察，止损位建议{cost_price*0.85:.2f}元")

            # 根据资金流向给建议
            if "今日" in flow_data and "10日" in flow_data:
                if flow_data["今日"]['main'] > 5000 and flow_data["10日"]['main'] > 30000:
                    print(f"   💡 资金面向好，有回本可能，建议继续持有观察")
                elif flow_data["今日"]['main'] < -5000:
                    print(f"   ⚠️  今日资金流出，警惕继续下跌，严守止损位")

        print("\n6. 关键价位参考:")
        print(f"   2周最高: {highest:.2f}元 (压力位)")
        print(f"   2周最低: {lowest:.2f}元 (支撑位)")
        print(f"   持仓成本: {cost_price:.2f}元 (解套位)")
        print(f"   止损建议: {cost_price*0.85:.2f}元 (-15%)")

        print("\n" + "=" * 120)
        print("风险提示: 以上分析仅供参考，请结合自身风险承受能力做决策")
        print("=" * 120)

    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
