#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奥瑞德深度分析 - 基于已获取数据的完整分析
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

def deep_analysis():
    """执行深度分析"""
    symbol = '600666'
    name = '奥瑞德'

    print(f"{'='*80}")
    print(f"{name} ({symbol}) 深度分析报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")

    try:
        # 获取数据
        print(f"\n📥 正在获取历史数据...")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust='qfq')

        if df.empty:
            print("❌ 无法获取数据")
            return

        print(f"✅ 成功获取 {len(df)} 条数据")

        # 计算技术指标
        print(f"\n🔧 正在计算技术指标...")

        # 均线
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

        # 成交量
        df['VOL_MA5'] = df['成交量'].rolling(window=5).mean()
        df['VOL_ratio'] = df['成交量'] / df['VOL_MA5']

        latest = df.iloc[-1]

        # ========== 1. 基础信息 ==========
        print(f"\n{'='*80}")
        print(f"一、基础信息")
        print(f"{'='*80}")
        print(f"最新价格: {latest['收盘']:.2f} 元")
        print(f"今日涨跌: {((latest['收盘'] - df.iloc[-2]['收盘'])/df.iloc[-2]['收盘']*100):+.2f}%")
        print(f"成交量: {latest['成交量']:.0f} 手")
        print(f"成交额: {latest['成交量'] * latest['收盘'] / 10000:.2f} 万元")

        # ========== 2. 支撑阻力位 ==========
        print(f"\n{'='*80}")
        print(f"二、支撑位与阻力位分析")
        print(f"{'='*80}")

        recent_30 = df.tail(30)
        recent_60 = df.tail(60)
        high_30 = recent_30['最高'].max()
        low_30 = recent_30['最低'].min()
        high_60 = recent_60['最高'].max()
        low_60 = recent_60['最低'].min()

        print(f"\n📈 关键阻力位:")
        resistances = [
            ("MA20", latest['MA20']),
            ("30日高点", high_30),
            ("布林上轨", latest['BB_upper']),
            ("60日高点", high_60)
        ]
        for name, price in resistances:
            distance = ((price / latest['收盘'] - 1) * 100)
            print(f"   {name:12} {price:6.2f}元  距离: {distance:+6.2f}%")

        print(f"\n📉 关键支撑位:")
        supports = [
            ("MA10", latest['MA10']),
            ("30日低点", low_30),
            ("布林下轨", latest['BB_lower']),
            ("60日低点", low_60)
        ]
        for name, price in supports:
            distance = ((price / latest['收盘'] - 1) * 100)
            print(f"   {name:12} {price:6.2f}元  距离: {distance:+6.2f}%")

        # ========== 3. 价格动量分析 ==========
        print(f"\n{'='*80}")
        print(f"三、价格动量分析")
        print(f"{'='*80}")

        changes = []
        for days in [5, 10, 20, 60]:
            if len(df) > days:
                change = ((latest['收盘'] - df.iloc[-(days+1)]['收盘']) / df.iloc[-(days+1)]['收盘']) * 100
                changes.append((f"{days}日", change))
                print(f"{days:3}日涨跌幅: {change:+7.2f}%")

        momentum_score = sum(1 for _, change in changes if change > 0)
        print(f"\n动量评分: {momentum_score}/{len(changes)}")

        if momentum_score >= 3:
            momentum_status = "🔥 强势上涨"
        elif momentum_score == 2:
            momentum_status = "⚖️ 震荡整理"
        else:
            momentum_status = "📉 偏弱下跌"
        print(f"动量状态: {momentum_status}")

        # ========== 4. 波动率和风险 ==========
        print(f"\n{'='*80}")
        print(f"四、波动率与风险评估")
        print(f"{'='*80}")

        df['return'] = df['收盘'].pct_change()
        vol_5 = df['return'].tail(5).std() * np.sqrt(252) * 100
        vol_20 = df['return'].tail(20).std() * np.sqrt(252) * 100
        vol_60 = df['return'].tail(60).std() * np.sqrt(252) * 100

        print(f"年化波动率:")
        print(f"   5日:  {vol_5:6.2f}%")
        print(f"   20日: {vol_20:6.2f}%")
        print(f"   60日: {vol_60:6.2f}%")

        # 最大回撤
        df['cummax'] = df['收盘'].cummax()
        df['drawdown'] = (df['收盘'] - df['cummax']) / df['cummax'] * 100
        max_dd = df['drawdown'].min()

        print(f"\n最大回撤: {max_dd:.2f}%")

        if vol_20 > 40:
            risk = "🔴 高风险"
        elif vol_20 > 30:
            risk = "🟡 中高风险"
        elif vol_20 > 20:
            risk = "🟢 中等风险"
        else:
            risk = "🔵 低风险"
        print(f"风险等级: {risk}")

        # ========== 5. 技术指标综合 ==========
        print(f"\n{'='*80}")
        print(f"五、技术指标综合分析")
        print(f"{'='*80}")

        print(f"\n均线系统:")
        print(f"   MA5:  {latest['MA5']:.2f}")
        print(f"   MA10: {latest['MA10']:.2f}")
        print(f"   MA20: {latest['MA20']:.2f}")
        print(f"   MA60: {latest['MA60']:.2f}")

        trend_score = 0
        if latest['收盘'] > latest['MA5']:
            trend_score += 1
        if latest['MA5'] > latest['MA10']:
            trend_score += 1
        if latest['MA10'] > latest['MA20']:
            trend_score += 1
        if latest['收盘'] > latest['MA60']:
            trend_score += 1
        print(f"   趋势评分: {trend_score}/4")

        print(f"\nRSI指标: {latest['RSI']:.2f}")
        if latest['RSI'] > 70:
            print(f"   ⚠️ 超买，注意回调")
        elif latest['RSI'] < 30:
            print(f"   ✅ 超卖，关注反弹")
        else:
            print(f"   ➡️ 正常区间")

        print(f"\nMACD指标:")
        print(f"   MACD: {latest['MACD']:.4f}")
        print(f"   信号线: {latest['MACD_signal']:.4f}")
        if latest['MACD'] > latest['MACD_signal']:
            print(f"   ✅ 多头排列")
        else:
            print(f"   ⚠️ 空头排列")

        print(f"\nKDJ指标:")
        print(f"   K={latest['K']:.1f}, D={latest['D']:.1f}, J={latest['J']:.1f}")
        if latest['J'] < 20:
            print(f"   ✅ 超卖区域")
        elif latest['J'] > 80:
            print(f"   ⚠️ 超买区域")

        print(f"\n布林带位置: {latest['BB_position']:.1f}%")

        # ========== 6. 资金流向 ==========
        print(f"\n{'='*80}")
        print(f"六、资金流向分析")
        print(f"{'='*80}")

        df['money_flow'] = df['成交量'] * df['收盘']
        avg_money_5 = df['money_flow'].tail(5).mean()
        latest_money = df.iloc[-1]['money_flow']

        print(f"今日成交额: {latest_money/10000:.2f} 万元")
        print(f"5日均成交额: {avg_money_5/10000:.2f} 万元")
        print(f"量比: {latest['VOL_ratio']:.2f}")

        if latest['VOL_ratio'] > 1.5:
            capital = "🔥 资金流入"
        elif latest['VOL_ratio'] > 0.8:
            capital = "➡️ 资金平稳"
        else:
            capital = "📉 资金流出"
        print(f"资金流向: {capital}")

        # ========== 7. 投资建议 ==========
        print(f"\n{'='*80}")
        print(f"七、投资建议")
        print(f"{'='*80}")

        total_score = trend_score
        if 30 <= latest['RSI'] <= 70:
            total_score += 1.5
        if latest['MACD'] > latest['MACD_signal']:
            total_score += 1
        if latest['VOL_ratio'] > 1.2:
            total_score += 1

        print(f"\n综合技术评分: {total_score:.1f}/8.0")

        if total_score >= 6:
            advice = "🔥 强烈买入"
            action = "可积极建仓，建议仓位30-50%"
        elif total_score >= 4:
            advice = "📈 买入"
            action = "可分批建仓，建议仓位20-30%"
        elif total_score >= 2:
            advice = "✅ 持有/观望"
            action = "持股观望，等待明确信号"
        else:
            advice = "⚠️ 观望/减仓"
            action = "暂不建议操作，规避风险"

        print(f"\n操作建议: {advice}")
        print(f"具体策略: {action}")

        print(f"\n建议止损位: {latest['BB_lower']:.2f} 元 ({((latest['BB_lower']/latest['收盘']-1)*100):.1f}%)")
        print(f"建议止盈位: {latest['BB_upper']:.2f} 元 ({((latest['BB_upper']/latest['收盘']-1)*100):.1f}%)")

        # ========== 8. 风险提示 ==========
        print(f"\n{'='*80}")
        print(f"八、风险提示")
        print(f"{'='*80}")
        print(f"1. 行业风险: 蓝宝石材料行业周期性强，受LED行业景气度影响大")
        print(f"2. 技术风险: 当前趋势不明朗，建议等待突破信号")
        print(f"3. 成交风险: 成交量萎缩，市场观望情绪较重")
        print(f"4. 价格风险: 注意3.24元支撑位，跌破需及时止损")
        print(f"5. 操作建议: 严格止损，控制仓位，不建议重仓")

        # ========== 生成图表 ==========
        print(f"\n📊 正在生成技术分析图表...")

        fig, axes = plt.subplots(4, 1, figsize=(16, 14))
        fig.suptitle(f'{name} ({symbol}) 技术分析图表\n生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                     fontsize=16, fontweight='bold')

        plot_df = df.tail(60).copy()
        plot_df['日期'] = pd.to_datetime(plot_df['日期'])

        # 图1: 价格和均线
        ax1 = axes[0]
        ax1.plot(plot_df['日期'], plot_df['收盘'], 'k-', linewidth=2, label='收盘价')
        ax1.plot(plot_df['日期'], plot_df['MA5'], 'r-', linewidth=1, alpha=0.7, label='MA5')
        ax1.plot(plot_df['日期'], plot_df['MA10'], 'b-', linewidth=1, alpha=0.7, label='MA10')
        ax1.plot(plot_df['日期'], plot_df['MA20'], 'g-', linewidth=1, alpha=0.7, label='MA20')
        ax1.plot(plot_df['日期'], plot_df['MA60'], 'm-', linewidth=1, alpha=0.7, label='MA60')
        ax1.fill_between(plot_df['日期'], plot_df['BB_lower'], plot_df['BB_upper'],
                         alpha=0.15, color='gray', label='布林带')
        ax1.set_title('价格走势与均线系统', fontsize=12, fontweight='bold', pad=10)
        ax1.set_ylabel('价格 (元)', fontsize=10)
        ax1.legend(loc='best', fontsize=9, ncol=3)
        ax1.grid(True, alpha=0.3, linestyle='--')

        # 图2: 成交量
        ax2 = axes[1]
        colors = ['red' if plot_df.iloc[i]['收盘'] >= plot_df.iloc[i]['开盘']
                  else 'green' for i in range(len(plot_df))]
        ax2.bar(plot_df['日期'], plot_df['成交量'], color=colors, alpha=0.6, width=0.8)
        ax2.plot(plot_df['日期'], plot_df['VOL_MA5'], 'b-', linewidth=1.5, label='5日均量')
        ax2.set_title('成交量分析', fontsize=12, fontweight='bold', pad=10)
        ax2.set_ylabel('成交量 (手)', fontsize=10)
        ax2.legend(loc='best', fontsize=9)
        ax2.grid(True, alpha=0.3, linestyle='--')

        # 图3: MACD
        ax3 = axes[2]
        ax3.plot(plot_df['日期'], plot_df['MACD'], 'b-', linewidth=1.5, label='MACD')
        ax3.plot(plot_df['日期'], plot_df['MACD_signal'], 'r-', linewidth=1.5, label='信号线')
        colors_macd = ['red' if x > 0 else 'green' for x in plot_df['MACD_hist']]
        ax3.bar(plot_df['日期'], plot_df['MACD_hist'], color=colors_macd, alpha=0.5, width=0.8)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax3.set_title('MACD指标', fontsize=12, fontweight='bold', pad=10)
        ax3.set_ylabel('MACD', fontsize=10)
        ax3.legend(loc='best', fontsize=9)
        ax3.grid(True, alpha=0.3, linestyle='--')

        # 图4: RSI和KDJ
        ax4 = axes[3]
        ax4_twin = ax4.twinx()

        # RSI
        ax4.plot(plot_df['日期'], plot_df['RSI'], color='purple', linewidth=2, label='RSI')
        ax4.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax4.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax4.axhline(y=50, color='gray', linestyle=':', linewidth=0.8, alpha=0.3)
        ax4.set_ylabel('RSI', fontsize=10, color='purple')
        ax4.set_ylim([0, 100])
        ax4.tick_params(axis='y', labelcolor='purple')

        # KDJ
        ax4_twin.plot(plot_df['日期'], plot_df['K'], 'b-', linewidth=1.2, alpha=0.8, label='K')
        ax4_twin.plot(plot_df['日期'], plot_df['D'], color='orange', linewidth=1.2, alpha=0.8, label='D')
        ax4_twin.plot(plot_df['日期'], plot_df['J'], 'r--', linewidth=1, alpha=0.8, label='J')
        ax4_twin.set_ylabel('KDJ', fontsize=10)
        ax4_twin.set_ylim([0, 120])

        ax4.set_title('RSI与KDJ指标', fontsize=12, fontweight='bold', pad=10)
        ax4.set_xlabel('日期', fontsize=10)
        ax4.grid(True, alpha=0.3, linestyle='--')

        # 合并图例
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=9, ncol=2)

        # 格式化日期
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        # 保存图表
        chart_file = f'{name}_深度分析_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存: {chart_file}")
        plt.close()

        print(f"\n{'='*80}")
        print(f"✅ 深度分析完成！")
        print(f"{'='*80}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deep_analysis()
