#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奥瑞德股票分析
股票代码: 600666
使用akshare获取数据并进行技术分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AoruideAnalyzer:
    """奥瑞德股票分析器"""

    def __init__(self):
        self.symbol = '600666'
        self.name = '奥瑞德'
        self.df = None
        print(f"🎯 {self.name} ({self.symbol}) 股票分析系统")
        print("=" * 60)

    def calculate_all_indicators(self, df):
        """计算所有技术指标"""
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
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']

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
        df['BB_position'] = (df['收盘'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower']) * 100

        # 成交量相关
        df['VOL_MA5'] = df['成交量'].rolling(window=5).mean()
        df['VOL_ratio'] = df['成交量'] / df['VOL_MA5']

        return df

    def analyze_trend(self, df):
        """趋势分析"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        print("\n📈 趋势分析")
        print("-" * 60)

        # 当前价格信息
        price_change = ((latest['收盘'] - prev['收盘']) / prev['收盘']) * 100
        print(f"📊 最新价格: {latest['收盘']:.2f}元")
        print(f"📊 今日涨跌: {price_change:+.2f}%")
        print(f"📊 成交量: {latest['成交量']:.0f}手 (量比: {latest['VOL_ratio']:.2f})")

        # 均线系统
        print(f"\n📉 均线系统:")
        print(f"   MA5:  {latest['MA5']:.2f}元")
        print(f"   MA10: {latest['MA10']:.2f}元")
        print(f"   MA20: {latest['MA20']:.2f}元")
        print(f"   MA60: {latest['MA60']:.2f}元")

        # 判断趋势
        trend_score = 0
        trend_signals = []

        if latest['收盘'] > latest['MA5']:
            trend_score += 1
            trend_signals.append("价格在MA5上方")
        if latest['MA5'] > latest['MA10']:
            trend_score += 1
            trend_signals.append("MA5上穿MA10")
        if latest['MA10'] > latest['MA20']:
            trend_score += 1
            trend_signals.append("MA10上穿MA20")
        if latest['收盘'] > latest['MA60']:
            trend_score += 1
            trend_signals.append("价格在MA60上方")

        print(f"\n✅ 趋势信号 ({trend_score}/4):")
        for signal in trend_signals:
            print(f"   • {signal}")

        if trend_score >= 3:
            trend_status = "🔥 强势上涨趋势"
        elif trend_score == 2:
            trend_status = "📈 偏多趋势"
        elif trend_score == 1:
            trend_status = "⚖️ 震荡整理"
        else:
            trend_status = "📉 弱势下跌趋势"

        print(f"\n🎯 趋势判断: {trend_status}")

        return trend_score, trend_status

    def analyze_oscillators(self, df):
        """震荡指标分析"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        print("\n📊 震荡指标分析")
        print("-" * 60)

        # RSI分析
        print(f"📈 RSI指标: {latest['RSI']:.2f}")
        if latest['RSI'] > 70:
            rsi_signal = "⚠️ 超买区域，注意回调风险"
        elif latest['RSI'] < 30:
            rsi_signal = "✅ 超卖区域，可能反弹"
        elif 40 <= latest['RSI'] <= 60:
            rsi_signal = "➡️ 中性区域，震荡为主"
        else:
            rsi_signal = "➡️ 正常区域"
        print(f"   {rsi_signal}")

        # MACD分析
        print(f"\n📈 MACD指标:")
        print(f"   MACD: {latest['MACD']:.4f}")
        print(f"   信号线: {latest['MACD_signal']:.4f}")
        print(f"   柱状图: {latest['MACD_hist']:.4f}")

        if latest['MACD'] > latest['MACD_signal'] and prev['MACD'] <= prev['MACD_signal']:
            macd_signal = "🔥 金叉信号，看涨"
        elif latest['MACD'] < latest['MACD_signal'] and prev['MACD'] >= prev['MACD_signal']:
            macd_signal = "⚠️ 死叉信号，看跌"
        elif latest['MACD'] > latest['MACD_signal']:
            macd_signal = "✅ 多头排列"
        else:
            macd_signal = "📉 空头排列"
        print(f"   {macd_signal}")

        # KDJ分析
        print(f"\n📈 KDJ指标:")
        print(f"   K: {latest['K']:.2f}")
        print(f"   D: {latest['D']:.2f}")
        print(f"   J: {latest['J']:.2f}")

        if latest['K'] > latest['D'] and prev['K'] <= prev['D']:
            kdj_signal = "🔥 金叉信号"
        elif latest['K'] < latest['D'] and prev['K'] >= prev['D']:
            kdj_signal = "⚠️ 死叉信号"
        elif latest['J'] > 100:
            kdj_signal = "⚠️ 超买，注意风险"
        elif latest['J'] < 0:
            kdj_signal = "✅ 超卖，关注机会"
        else:
            kdj_signal = "➡️ 正常运行"
        print(f"   {kdj_signal}")

        # 布林带分析
        print(f"\n📈 布林带分析:")
        print(f"   上轨: {latest['BB_upper']:.2f}")
        print(f"   中轨: {latest['BB_middle']:.2f}")
        print(f"   下轨: {latest['BB_lower']:.2f}")
        print(f"   位置: {latest['BB_position']:.1f}%")

        if latest['BB_position'] > 90:
            bb_signal = "⚠️ 接近上轨，超买"
        elif latest['BB_position'] < 10:
            bb_signal = "✅ 接近下轨，超卖"
        elif 40 <= latest['BB_position'] <= 60:
            bb_signal = "➡️ 中轨附近，震荡"
        else:
            bb_signal = "➡️ 正常运行"
        print(f"   {bb_signal}")

        return {
            'rsi': latest['RSI'],
            'macd': macd_signal,
            'kdj': kdj_signal,
            'bb_position': latest['BB_position']
        }

    def analyze_volume(self, df):
        """成交量分析"""
        latest = df.iloc[-1]

        print("\n📊 成交量分析")
        print("-" * 60)

        recent_vol = df['成交量'].tail(5)
        avg_vol = recent_vol.mean()

        print(f"📊 今日成交量: {latest['成交量']:.0f}手")
        print(f"📊 5日均量: {latest['VOL_MA5']:.0f}手")
        print(f"📊 量比: {latest['VOL_ratio']:.2f}")

        if latest['VOL_ratio'] > 2:
            vol_signal = "🔥 放量突破，资金活跃"
        elif latest['VOL_ratio'] > 1.5:
            vol_signal = "✅ 温和放量"
        elif latest['VOL_ratio'] < 0.5:
            vol_signal = "⚠️ 缩量明显，观望情绪浓"
        else:
            vol_signal = "➡️ 成交正常"

        print(f"\n{vol_signal}")

        return latest['VOL_ratio']

    def generate_recommendation(self, trend_score, oscillators, vol_ratio):
        """生成投资建议"""
        print("\n" + "=" * 60)
        print("💡 投资建议")
        print("=" * 60)

        # 计算综合评分
        total_score = 0

        # 趋势得分 (0-4分)
        total_score += trend_score

        # RSI得分 (0-2分)
        if 30 <= oscillators['rsi'] <= 70:
            total_score += 1.5
        elif oscillators['rsi'] < 30:
            total_score += 2
        elif oscillators['rsi'] > 80:
            total_score -= 1

        # MACD得分 (0-1分)
        if "金叉" in oscillators['macd']:
            total_score += 1

        # 成交量得分 (0-1分)
        if vol_ratio > 1.2:
            total_score += 1

        print(f"\n📊 综合技术评分: {total_score:.1f}/8.0")

        # 生成建议
        if total_score >= 6:
            recommendation = "🔥 强烈买入"
            confidence = "高"
            action = "可积极建仓"
        elif total_score >= 4:
            recommendation = "📈 买入"
            confidence = "中高"
            action = "可分批建仓"
        elif total_score >= 2:
            recommendation = "✅ 持有/观望"
            confidence = "中等"
            action = "观察后续走势"
        else:
            recommendation = "⚠️ 观望/减仓"
            confidence = "低"
            action = "暂不建议操作"

        print(f"\n💰 操作建议: {recommendation}")
        print(f"🎯 置信度: {confidence}")
        print(f"📝 具体操作: {action}")

        # 风险提示
        print(f"\n⚠️ 风险提示:")
        print(f"   • 奥瑞德属于蓝宝石材料行业，周期性较强")
        print(f"   • 注意LED行业景气度变化")
        print(f"   • 关注公司业绩公告和行业政策")
        print(f"   • 建议设置止损位，控制风险")

        return recommendation

    def analyze_support_resistance(self, df):
        """支撑位和阻力位分析"""
        print("\n💎 支撑位与阻力位分析")
        print("-" * 60)

        latest = df.iloc[-1]
        current_price = latest['收盘']

        # 计算近期高低点
        recent_30 = df.tail(30)
        recent_60 = df.tail(60)

        # 最近30天的高低点
        high_30 = recent_30['最高'].max()
        low_30 = recent_30['最低'].min()

        # 最近60天的高低点
        high_60 = recent_60['最高'].max()
        low_60 = recent_60['最低'].min()

        print(f"📊 当前价格: {current_price:.2f}元")
        print(f"\n📈 阻力位分析:")
        print(f"   近期阻力位1 (MA20): {latest['MA20']:.2f}元 ({((latest['MA20']/current_price - 1) * 100):+.2f}%)")
        print(f"   近期阻力位2 (30日高点): {high_30:.2f}元 ({((high_30/current_price - 1) * 100):+.2f}%)")
        print(f"   近期阻力位3 (布林上轨): {latest['BB_upper']:.2f}元 ({((latest['BB_upper']/current_price - 1) * 100):+.2f}%)")
        print(f"   中期阻力位 (60日高点): {high_60:.2f}元 ({((high_60/current_price - 1) * 100):+.2f}%)")

        print(f"\n📉 支撑位分析:")
        print(f"   近期支撑位1 (MA10): {latest['MA10']:.2f}元 ({((latest['MA10']/current_price - 1) * 100):+.2f}%)")
        print(f"   近期支撑位2 (30日低点): {low_30:.2f}元 ({((low_30/current_price - 1) * 100):+.2f}%)")
        print(f"   近期支撑位3 (布林下轨): {latest['BB_lower']:.2f}元 ({((latest['BB_lower']/current_price - 1) * 100):+.2f}%)")
        print(f"   中期支撑位 (60日低点): {low_60:.2f}元 ({((low_60/current_price - 1) * 100):+.2f}%)")

        return {
            'resistance': [latest['MA20'], high_30, latest['BB_upper']],
            'support': [latest['MA10'], low_30, latest['BB_lower']]
        }

    def analyze_volatility_risk(self, df):
        """波动率和风险评估"""
        print("\n⚡ 波动率与风险评估")
        print("-" * 60)

        # 计算收益率
        df['return'] = df['收盘'].pct_change()

        # 计算不同周期的波动率
        volatility_5 = df['return'].tail(5).std() * np.sqrt(252) * 100
        volatility_20 = df['return'].tail(20).std() * np.sqrt(252) * 100
        volatility_60 = df['return'].tail(60).std() * np.sqrt(252) * 100

        print(f"📊 年化波动率:")
        print(f"   5日波动率: {volatility_5:.2f}%")
        print(f"   20日波动率: {volatility_20:.2f}%")
        print(f"   60日波动率: {volatility_60:.2f}%")

        # 最大回撤
        df['cummax'] = df['收盘'].cummax()
        df['drawdown'] = (df['收盘'] - df['cummax']) / df['cummax'] * 100
        max_drawdown = df['drawdown'].min()

        print(f"\n📉 最大回撤分析:")
        print(f"   近期最大回撤: {max_drawdown:.2f}%")

        # 风险等级评估
        if volatility_20 > 50:
            risk_level = "🔴 极高风险"
        elif volatility_20 > 40:
            risk_level = "🟠 高风险"
        elif volatility_20 > 30:
            risk_level = "🟡 中高风险"
        elif volatility_20 > 20:
            risk_level = "🟢 中等风险"
        else:
            risk_level = "🔵 低风险"

        print(f"\n🎯 风险等级: {risk_level}")

        return {
            'volatility_20': volatility_20,
            'max_drawdown': max_drawdown,
            'risk_level': risk_level
        }

    def analyze_price_momentum(self, df):
        """价格动量分析"""
        print("\n🚀 价格动量分析")
        print("-" * 60)

        latest = df.iloc[-1]

        # 计算不同周期涨跌幅
        price_change_5 = ((latest['收盘'] - df.iloc[-6]['收盘']) / df.iloc[-6]['收盘']) * 100
        price_change_10 = ((latest['收盘'] - df.iloc[-11]['收盘']) / df.iloc[-11]['收盘']) * 100
        price_change_20 = ((latest['收盘'] - df.iloc[-21]['收盘']) / df.iloc[-21]['收盘']) * 100
        price_change_60 = ((latest['收盘'] - df.iloc[-61]['收盘']) / df.iloc[-61]['收盘']) * 100

        print(f"📊 周期涨跌幅:")
        print(f"   5日涨跌: {price_change_5:+.2f}%")
        print(f"   10日涨跌: {price_change_10:+.2f}%")
        print(f"   20日涨跌: {price_change_20:+.2f}%")
        print(f"   60日涨跌: {price_change_60:+.2f}%")

        # 动量评分
        momentum_score = 0
        if price_change_5 > 0:
            momentum_score += 1
        if price_change_10 > 0:
            momentum_score += 1
        if price_change_20 > 0:
            momentum_score += 1
        if price_change_60 > 0:
            momentum_score += 1

        print(f"\n🎯 动量评分: {momentum_score}/4")

        if momentum_score == 4:
            momentum_status = "🔥 强势上涨动能"
        elif momentum_score == 3:
            momentum_status = "📈 偏强动能"
        elif momentum_score == 2:
            momentum_status = "⚖️ 中性动能"
        else:
            momentum_status = "📉 偏弱动能"

        print(f"💡 动量状态: {momentum_status}")

        return momentum_score

    def analyze_capital_flow(self, df):
        """资金流向分析"""
        print("\n💰 资金流向分析")
        print("-" * 60)

        # 计算资金流向指标
        df['money_flow'] = df['成交量'] * df['收盘']

        recent_5 = df.tail(5)
        recent_10 = df.tail(10)

        # 计算近期资金变化
        avg_money_5 = recent_5['money_flow'].mean()
        avg_money_10 = recent_10['money_flow'].mean()

        latest_money = df.iloc[-1]['money_flow']

        print(f"📊 成交额分析:")
        print(f"   今日成交额: {latest_money/10000:.2f}万元")
        print(f"   5日平均成交额: {avg_money_5/10000:.2f}万元")
        print(f"   10日平均成交额: {avg_money_10/10000:.2f}万元")

        # 资金流向判断
        money_ratio = latest_money / avg_money_5

        if money_ratio > 1.5:
            capital_flow = "🔥 资金大幅流入"
        elif money_ratio > 1.2:
            capital_flow = "📈 资金流入"
        elif money_ratio > 0.8:
            capital_flow = "➡️ 资金平稳"
        else:
            capital_flow = "📉 资金流出"

        print(f"\n💡 资金流向: {capital_flow}")

        # 计算大单占比（近5日放量天数）
        vol_increase_days = (recent_5['成交量'] > recent_5['成交量'].shift(1)).sum()
        print(f"📊 近5日放量天数: {vol_increase_days}天")

        return capital_flow

    def plot_technical_chart(self, df):
        """绘制技术分析图表"""
        print("\n📊 正在生成技术分析图表...")

        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        fig.suptitle(f'{self.name} ({self.symbol}) 技术分析图', fontsize=16, fontweight='bold')

        # 准备数据
        plot_df = df.tail(60).copy()
        plot_df['日期'] = pd.to_datetime(plot_df['日期'])

        # 图1: K线和均线
        ax1 = axes[0]
        ax1.plot(plot_df['日期'], plot_df['收盘'], label='收盘价', linewidth=2, color='black')
        ax1.plot(plot_df['日期'], plot_df['MA5'], label='MA5', linewidth=1, color='red', alpha=0.7)
        ax1.plot(plot_df['日期'], plot_df['MA10'], label='MA10', linewidth=1, color='blue', alpha=0.7)
        ax1.plot(plot_df['日期'], plot_df['MA20'], label='MA20', linewidth=1, color='green', alpha=0.7)
        ax1.plot(plot_df['日期'], plot_df['MA60'], label='MA60', linewidth=1, color='purple', alpha=0.7)
        ax1.fill_between(plot_df['日期'], plot_df['BB_lower'], plot_df['BB_upper'], alpha=0.1, color='gray')
        ax1.set_title('价格走势与均线系统', fontsize=12, fontweight='bold')
        ax1.set_ylabel('价格 (元)', fontsize=10)
        ax1.legend(loc='best', fontsize=8)
        ax1.grid(True, alpha=0.3)

        # 图2: 成交量
        ax2 = axes[1]
        colors = ['red' if plot_df.iloc[i]['收盘'] >= plot_df.iloc[i]['开盘'] else 'green'
                  for i in range(len(plot_df))]
        ax2.bar(plot_df['日期'], plot_df['成交量'], color=colors, alpha=0.6)
        ax2.plot(plot_df['日期'], plot_df['VOL_MA5'], label='5日均量', linewidth=1, color='blue')
        ax2.set_title('成交量', fontsize=12, fontweight='bold')
        ax2.set_ylabel('成交量 (手)', fontsize=10)
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)

        # 图3: MACD
        ax3 = axes[2]
        ax3.plot(plot_df['日期'], plot_df['MACD'], label='MACD', linewidth=1, color='blue')
        ax3.plot(plot_df['日期'], plot_df['MACD_signal'], label='Signal', linewidth=1, color='red')
        colors_macd = ['red' if x > 0 else 'green' for x in plot_df['MACD_hist']]
        ax3.bar(plot_df['日期'], plot_df['MACD_hist'], color=colors_macd, alpha=0.5, label='Histogram')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_title('MACD指标', fontsize=12, fontweight='bold')
        ax3.set_ylabel('MACD', fontsize=10)
        ax3.legend(loc='best', fontsize=8)
        ax3.grid(True, alpha=0.3)

        # 图4: RSI和KDJ
        ax4 = axes[3]
        ax4_twin = ax4.twinx()

        # RSI
        ax4.plot(plot_df['日期'], plot_df['RSI'], label='RSI', linewidth=1.5, color='purple')
        ax4.axhline(y=70, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
        ax4.axhline(y=30, color='green', linestyle='--', linewidth=0.8, alpha=0.5)
        ax4.set_ylabel('RSI', fontsize=10, color='purple')
        ax4.set_ylim([0, 100])
        ax4.tick_params(axis='y', labelcolor='purple')

        # KDJ
        ax4_twin.plot(plot_df['日期'], plot_df['K'], label='K', linewidth=1, color='blue', alpha=0.7)
        ax4_twin.plot(plot_df['日期'], plot_df['D'], label='D', linewidth=1, color='orange', alpha=0.7)
        ax4_twin.plot(plot_df['日期'], plot_df['J'], label='J', linewidth=1, color='red', alpha=0.7)
        ax4_twin.set_ylabel('KDJ', fontsize=10)
        ax4_twin.set_ylim([0, 120])

        ax4.set_title('RSI与KDJ指标', fontsize=12, fontweight='bold')
        ax4.set_xlabel('日期', fontsize=10)
        ax4.grid(True, alpha=0.3)

        # 合并图例
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=8)

        # 格式化x轴日期
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # 保存图表
        chart_filename = f'{self.name}_技术分析图_{datetime.now().strftime("%Y%m%d")}.png'
        plt.savefig(chart_filename, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存: {chart_filename}")

        plt.close()

        return chart_filename

    def run_analysis(self):
        """运行完整分析"""
        try:
            # 获取历史数据（最近180天）
            print(f"\n📥 正在获取{self.name}历史数据...")
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

            df = ak.stock_zh_a_hist(
                symbol=self.symbol,
                start_date=start_date,
                end_date=end_date,
                adjust='qfq'
            )

            if df.empty:
                print(f"❌ 无法获取数据，请检查股票代码或网络连接")
                return

            print(f"✅ 成功获取{len(df)}条数据记录")

            # 计算技术指标
            print(f"🔧 正在计算技术指标...")
            df = self.calculate_all_indicators(df)
            self.df = df

            # 执行各项分析
            trend_score, trend_status = self.analyze_trend(df)
            oscillators = self.analyze_oscillators(df)
            vol_ratio = self.analyze_volume(df)

            # 深度分析
            self.analyze_support_resistance(df)
            risk_info = self.analyze_volatility_risk(df)
            momentum_score = self.analyze_price_momentum(df)
            capital_flow = self.analyze_capital_flow(df)

            # 生成投资建议
            recommendation = self.generate_recommendation(trend_score, oscillators, vol_ratio)

            # 生成图表
            chart_file = self.plot_technical_chart(df)

            print(f"\n" + "=" * 60)
            print(f"✅ 深度分析完成！")
            print(f"=" * 60)

        except Exception as e:
            print(f"❌ 分析过程中出错: {e}")
            print(f"💡 提示: 请确保已安装akshare库 (pip install akshare)")

def main():
    """主函数"""
    analyzer = AoruideAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
