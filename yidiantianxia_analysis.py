#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易点天下(301171) 深度分析
被套解套策略分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TrapAnalyzer:
    """被套股票深度分析器"""

    def __init__(self, symbol, name, trap_percent):
        self.symbol = symbol
        self.name = name
        self.trap_percent = trap_percent  # 被套幅度

    def get_stock_data(self, days=180):
        """获取股票历史数据"""
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=self.symbol, start_date=start_date,
                                 end_date=end_date, adjust='qfq')
        return df

    def calculate_indicators(self, df):
        """计算技术指标"""
        # 移动平均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        df['MA60'] = df['收盘'].rolling(window=60).mean()

        # RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['收盘'].ewm(span=12).mean()
        exp2 = df['收盘'].ewm(span=26).mean()
        df['DIF'] = exp1 - exp2
        df['DEA'] = df['DIF'].ewm(span=9).mean()
        df['MACD'] = (df['DIF'] - df['DEA']) * 2

        # KDJ
        low_min = df['最低'].rolling(window=9).min()
        high_max = df['最高'].rolling(window=9).max()
        rsv = (df['收盘'] - low_min) / (high_max - low_min) * 100
        df['K'] = rsv.ewm(com=2).mean()
        df['D'] = df['K'].ewm(com=2).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']

        # 布林带
        df['BB_middle'] = df['收盘'].rolling(window=20).mean()
        bb_std = df['收盘'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle'] * 100

        # 成交量均线
        df['VOL_MA5'] = df['成交量'].rolling(window=5).mean()
        df['VOL_MA20'] = df['成交量'].rolling(window=20).mean()

        # 涨跌幅
        df['涨跌幅'] = df['收盘'].pct_change() * 100

        return df

    def find_support_resistance(self, df):
        """寻找支撑位和阻力位"""
        recent = df.tail(60)

        # 近期高点和低点
        high_52w = df.tail(250)['最高'].max() if len(df) >= 250 else df['最高'].max()
        low_52w = df.tail(250)['最低'].min() if len(df) >= 250 else df['最低'].min()

        recent_high = recent['最高'].max()
        recent_low = recent['最低'].min()

        current_price = df.iloc[-1]['收盘']

        # 寻找密集成交区
        price_bins = pd.cut(recent['收盘'], bins=20)
        volume_by_price = recent.groupby(price_bins)['成交量'].sum()

        return {
            '52周最高': high_52w,
            '52周最低': low_52w,
            '近60日最高': recent_high,
            '近60日最低': recent_low,
            '当前价': current_price,
            '距离52周高点': (current_price - high_52w) / high_52w * 100,
            '距离52周低点': (current_price - low_52w) / low_52w * 100
        }

    def analyze_trend(self, df):
        """趋势分析"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 均线排列
        ma_alignment = "多头排列" if latest['MA5'] > latest['MA10'] > latest['MA20'] else \
                       "空头排列" if latest['MA5'] < latest['MA10'] < latest['MA20'] else "震荡整理"

        # 价格位置
        price_vs_ma = {
            'vs_MA5': '上方' if latest['收盘'] > latest['MA5'] else '下方',
            'vs_MA10': '上方' if latest['收盘'] > latest['MA10'] else '下方',
            'vs_MA20': '上方' if latest['收盘'] > latest['MA20'] else '下方',
            'vs_MA60': '上方' if latest['收盘'] > latest['MA60'] else '下方'
        }

        # MACD趋势
        macd_trend = "金叉向上" if latest['DIF'] > latest['DEA'] else "死叉向下"
        macd_momentum = "增强" if latest['MACD'] > prev['MACD'] else "减弱"

        return {
            '均线排列': ma_alignment,
            '价格位置': price_vs_ma,
            'MACD趋势': macd_trend,
            'MACD动能': macd_momentum
        }

    def get_fund_flow(self):
        """获取资金流向"""
        try:
            # 个股资金流向
            flow = ak.stock_individual_fund_flow(stock=self.symbol, market="sz")
            return flow.tail(10) if flow is not None else None
        except:
            return None

    def calculate_cost_estimate(self, df):
        """估算成本价和解套点位"""
        current_price = df.iloc[-1]['收盘']
        # 根据被套幅度反推成本价
        cost_price = current_price / (1 - self.trap_percent / 100)

        # 计算不同补仓比例后的成本
        补仓方案 = []
        for ratio in [0.25, 0.5, 1.0]:
            # 假设补仓后，新成本 = (原成本*原仓位 + 现价*补仓量) / (原仓位+补仓量)
            new_cost = (cost_price * 1 + current_price * ratio) / (1 + ratio)
            new_trap_percent = (new_cost - current_price) / current_price * 100
            补仓方案.append({
                '补仓比例': f'{int(ratio*100)}%',
                '新成本': new_cost,
                '新套幅': new_trap_percent,
                '解套涨幅': (new_cost - current_price) / current_price * 100
            })

        return {
            '估算成本价': cost_price,
            '当前价': current_price,
            '补仓方案': 补仓方案
        }

    def generate_strategy(self, df, trend, levels):
        """生成操作策略"""
        latest = df.iloc[-1]

        strategies = []

        # 根据技术面判断
        rsi = latest['RSI']
        kdj_j = latest['J']
        macd = latest['MACD']

        # 超卖信号
        if rsi < 30:
            strategies.append("RSI超卖(<30)，短线有反弹需求")
        elif rsi < 40:
            strategies.append("RSI偏弱(30-40)，观望为主")
        elif rsi > 70:
            strategies.append("RSI超买(>70)，注意回调风险")

        # KDJ信号
        if kdj_j < 0:
            strategies.append("KDJ的J值<0，极度超卖，可能有反弹")
        elif kdj_j < 20:
            strategies.append("KDJ低位，可能形成底部")

        # MACD信号
        if macd > 0 and latest['DIF'] > latest['DEA']:
            strategies.append("MACD金叉且红柱，短期偏多")
        elif macd < 0 and latest['DIF'] < latest['DEA']:
            strategies.append("MACD死叉且绿柱，短期偏空")

        # 布林带位置
        bb_pos = (latest['收盘'] - latest['BB_lower']) / (latest['BB_upper'] - latest['BB_lower']) * 100
        if bb_pos < 20:
            strategies.append("股价接近布林带下轨，超跌区域")
        elif bb_pos > 80:
            strategies.append("股价接近布林带上轨，注意压力")

        return strategies

    def run_analysis(self):
        """运行完整分析"""
        print(f"\n{'='*60}")
        print(f"📊 {self.name}({self.symbol}) 深度分析报告")
        print(f"被套幅度: {self.trap_percent}%")
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")

        # 获取数据
        print("\n📥 正在获取数据...")
        df = self.get_stock_data(180)

        if df.empty or len(df) < 30:
            print("❌ 无法获取足够的历史数据")
            return

        # 计算指标
        df = self.calculate_indicators(df)
        latest = df.iloc[-1]

        # 基本信息
        print(f"\n📈 【基本行情】")
        print(f"   当前价格: {latest['收盘']:.2f}元")
        print(f"   今日涨跌: {latest['涨跌幅']:.2f}%")
        print(f"   今日振幅: {((latest['最高'] - latest['最低']) / latest['开盘'] * 100):.2f}%")
        print(f"   成交量: {latest['成交量']/10000:.0f}万手")
        print(f"   成交额: {latest['成交额']/100000000:.2f}亿元")

        # 支撑阻力
        levels = self.find_support_resistance(df)
        print(f"\n📊 【关键价位】")
        print(f"   52周最高: {levels['52周最高']:.2f}元 (距今 {levels['距离52周高点']:.1f}%)")
        print(f"   52周最低: {levels['52周最低']:.2f}元 (距今 {levels['距离52周低点']:.1f}%)")
        print(f"   近60日最高: {levels['近60日最高']:.2f}元")
        print(f"   近60日最低: {levels['近60日最低']:.2f}元")

        # 技术指标
        print(f"\n📉 【技术指标】")
        print(f"   MA5/10/20/60: {latest['MA5']:.2f} / {latest['MA10']:.2f} / {latest['MA20']:.2f} / {latest['MA60']:.2f}")
        print(f"   RSI(14): {latest['RSI']:.1f}")
        print(f"   MACD: DIF={latest['DIF']:.3f}, DEA={latest['DEA']:.3f}, MACD={latest['MACD']:.3f}")
        print(f"   KDJ: K={latest['K']:.1f}, D={latest['D']:.1f}, J={latest['J']:.1f}")
        print(f"   布林带: 上轨{latest['BB_upper']:.2f} / 中轨{latest['BB_middle']:.2f} / 下轨{latest['BB_lower']:.2f}")

        # 趋势分析
        trend = self.analyze_trend(df)
        print(f"\n📊 【趋势分析】")
        print(f"   均线排列: {trend['均线排列']}")
        print(f"   MACD趋势: {trend['MACD趋势']}, 动能{trend['MACD动能']}")
        for ma, pos in trend['价格位置'].items():
            print(f"   价格在{ma}: {pos}")

        # 成本分析
        cost = self.calculate_cost_estimate(df)
        print(f"\n💰 【成本与解套分析】")
        print(f"   您的估算成本: {cost['估算成本价']:.2f}元")
        print(f"   当前市价: {cost['当前价']:.2f}元")
        print(f"   被套幅度: {self.trap_percent}%")
        print(f"\n   补仓摊薄成本方案:")
        for plan in cost['补仓方案']:
            print(f"   - 补仓{plan['补仓比例']}: 新成本{plan['新成本']:.2f}元, 解套需涨{plan['解套涨幅']:.1f}%")

        # 资金流向
        print(f"\n💹 【资金流向】")
        try:
            flow = self.get_fund_flow()
            if flow is not None and not flow.empty:
                recent_flow = flow.tail(5)
                print("   近5日资金流向:")
                for _, row in recent_flow.iterrows():
                    date = row.get('日期', row.name)
                    main_flow = row.get('主力净流入-净额', 0)
                    if isinstance(main_flow, (int, float)):
                        flow_str = f"{main_flow/10000:.0f}万" if abs(main_flow) > 10000 else f"{main_flow:.0f}"
                        print(f"   {date}: 主力净流入 {flow_str}")
            else:
                print("   暂无资金流向数据")
        except Exception as e:
            print(f"   资金流向数据获取失败: {e}")

        # 操作建议
        strategies = self.generate_strategy(df, trend, levels)
        print(f"\n🎯 【技术信号】")
        for s in strategies:
            print(f"   • {s}")

        # 综合建议
        print(f"\n💡 【综合操作建议】")

        # 判断逻辑
        rsi = latest['RSI']
        kdj_j = latest['J']
        is_oversold = rsi < 35 or kdj_j < 10
        is_macd_golden = latest['DIF'] > latest['DEA']
        is_below_ma = latest['收盘'] < latest['MA20']
        price_position = (latest['收盘'] - levels['52周最低']) / (levels['52周最高'] - levels['52周最低']) * 100

        if is_oversold and is_macd_golden:
            print("   📈 技术面显示超卖后有反弹迹象")
            print("   • 可考虑小仓位补仓摊薄成本(建议补仓25-50%)")
            print("   • 反弹至成本价附近考虑减仓")
        elif is_oversold:
            print("   ⚠️ 技术面超卖，但趋势未明确反转")
            print("   • 暂时观望，等待MACD金叉确认")
            print("   • 若继续下跌可在更低位置分批补仓")
        elif price_position < 30:
            print("   📉 股价处于相对低位区域")
            print("   • 可分批建仓或小额补仓")
            print("   • 关注成交量变化和资金流向")
        else:
            print("   ⚖️ 当前位置需要谨慎操作")
            print("   • 建议持股观望，不急于补仓")
            print("   • 关注大盘走势和板块联动")

        # 止损建议
        stop_loss = levels['近60日最低'] * 0.95
        print(f"\n⚠️ 【风险控制】")
        print(f"   建议止损位: {stop_loss:.2f}元 (近60日最低的95%)")
        print(f"   如跌破此位，建议认赔出局，避免更大损失")

        # 解套路径
        print(f"\n🛣️ 【可能的解套路径】")
        print(f"   1. 持股等待: 需上涨{self.trap_percent:.1f}%才能解套")
        print(f"   2. 补仓25%: 成本降至{cost['补仓方案'][0]['新成本']:.2f}元，需涨{cost['补仓方案'][0]['解套涨幅']:.1f}%")
        print(f"   3. 补仓50%: 成本降至{cost['补仓方案'][1]['新成本']:.2f}元，需涨{cost['补仓方案'][1]['解套涨幅']:.1f}%")
        print(f"   4. 做T降成本: 在振幅较大时高抛低吸")

        print(f"\n{'='*60}")
        print("⚠️ 免责声明: 以上分析仅供参考，不构成投资建议")
        print("投资有风险，入市需谨慎，请根据自身情况做出决策")
        print(f"{'='*60}")

        return df

def main():
    # 易点天下 301171
    analyzer = TrapAnalyzer(
        symbol="301171",
        name="易点天下",
        trap_percent=16  # 被套16%
    )
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
