#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易点天下(301171) 近15个交易日 分时深度分析
数据源: 本地已保存 5 分钟 K 线 CSV
"""

import pandas as pd
import numpy as np
from datetime import datetime

pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

CSV = "易点天下_5min分时_20260424_1011.csv"
df = pd.read_csv(CSV)
df['时间'] = pd.to_datetime(df['时间'])
df['日期'] = df['时间'].dt.strftime('%Y-%m-%d')
df['时分'] = df['时间'].dt.strftime('%H:%M')

# 找出最近 15 个交易日
dates = sorted(df['日期'].unique())
last15 = dates[-15:]
print(f"分析区间: {last15[0]} ~ {last15[-1]}  ({len(last15)} 个交易日)")
print(f"数据精度: 5 分钟 K 线 (单日约 48 根)\n")

sub = df[df['日期'].isin(last15)].copy()

# ============ 1. 按日聚合概览 ============
print("="*100)
print("  一、每日核心数据（收盘前若不完整则到当前时点为止）")
print("="*100)

daily = sub.groupby('日期').agg(
    开盘=('开盘', 'first'),
    最高=('最高', 'max'),
    最低=('最低', 'min'),
    收盘=('收盘', 'last'),
    成交量=('成交量', 'sum'),
    成交额=('成交额', 'sum'),
).reset_index()

daily['昨收'] = daily['收盘'].shift(1)
daily['高开%'] = ((daily['开盘'] - daily['昨收']) / daily['昨收'] * 100).round(2)
daily['日涨跌%'] = ((daily['收盘'] - daily['昨收']) / daily['昨收'] * 100).round(2)
daily['日振幅%'] = ((daily['最高'] - daily['最低']) / daily['昨收'] * 100).round(2)
daily['VWAP'] = (daily['成交额'] / daily['成交量'] / 100).round(2)
daily['成交额_亿'] = (daily['成交额'] / 1e8).round(2)
daily['成交量_万手'] = (daily['成交量'] / 1e4).round(1)

# 5日均量
daily['5日均量_万手'] = daily['成交量_万手'].rolling(5).mean().round(1)
daily['量比'] = (daily['成交量_万手'] / daily['5日均量_万手'].shift(1)).round(2)

show = daily[['日期','开盘','最高','最低','收盘','VWAP','高开%','日涨跌%','日振幅%','成交量_万手','成交额_亿','量比']]
print(show.to_string(index=False))

# ============ 2. 每日日内形态识别 ============
print("\n" + "="*100)
print("  二、每日分时形态识别")
print("="*100)

def day_shape(g):
    """识别单日分时走势形态"""
    if len(g) < 20:
        return pd.Series({
            '形态': '⚪ 盘中-未完整', '日内最高时点':'-', '日内最低时点':'-',
            '开→收%': 0, '开→前30分%':0, '尾盘30分%':0, 'VWAP':0, '收-VWAP%':0
        })
    g = g.sort_values('时间').reset_index(drop=True)
    opens = g['开盘'].iloc[0]
    close = g['收盘'].iloc[-1]
    high = g['最高'].max()
    low = g['最低'].min()

    # 找最高点/最低点的时段
    high_idx = g['最高'].idxmax()
    low_idx = g['最低'].idxmin()
    high_time = g.loc[high_idx, '时分']
    low_time = g.loc[low_idx, '时分']

    # 均价
    vwap = (g['成交额'].sum() / g['成交量'].sum() / 100)

    # 早盘(前30分钟)和尾盘(最后30分钟)
    first30 = g.head(6)  # 6根5分钟
    last30 = g.tail(6)
    first_close = first30['收盘'].iloc[-1]
    last_close = last30['收盘'].iloc[-1]

    # 形态分类
    change = (close - opens) / opens * 100
    first_change = (first_close - opens) / opens * 100
    last_change = (last_close - first_close) / first_close * 100

    # 判定
    if high_time <= '09:45' and change < -1:
        pattern = "🔴 高开低走"
    elif low_time <= '09:45' and change > 1:
        pattern = "🟢 低开高走"
    elif change > 3:
        pattern = "🟢 全天强势"
    elif change < -3:
        pattern = "🔴 全天弱势"
    elif abs(change) < 1 and (high - low) / opens < 0.02:
        pattern = "⚪ 窄幅横盘"
    elif first_change > 1 and last_change < -1:
        pattern = "🟡 早强午弱"
    elif first_change < -1 and last_change > 1:
        pattern = "🟡 早弱午强"
    elif high_time < '11:30' and change < 0:
        pattern = "🔴 冲高回落"
    elif low_time < '11:30' and change > 0:
        pattern = "🟢 探底回升"
    else:
        pattern = "⚪ 震荡整理"

    return pd.Series({
        '形态': pattern,
        '日内最高时点': high_time,
        '日内最低时点': low_time,
        '开→收%': round(change, 2),
        '开→前30分%': round(first_change, 2),
        '尾盘30分%': round(last_change, 2),
        'VWAP': round(vwap, 2),
        '收-VWAP%': round((close-vwap)/vwap*100, 2),
    })

shapes = sub.groupby('日期').apply(day_shape).reset_index()
print(shapes.to_string(index=False))

# ============ 3. 量能分布：哪天最热 ============
print("\n" + "="*100)
print("  三、量能排名（15日内成交异动）")
print("="*100)
vol_rank = daily[['日期','收盘','日涨跌%','成交量_万手','成交额_亿','量比']].sort_values('成交额_亿', ascending=False)
print("TOP 5 放量日:")
print(vol_rank.head(5).to_string(index=False))
print("\n缩量尾部 3 日:")
print(vol_rank.tail(3).to_string(index=False))

# ============ 4. 分时段平均行为（15天均值）=============
print("\n" + "="*100)
print("  四、15日平均日内规律（同一时点的平均收益）")
print("="*100)

sub['分钟'] = sub['时间'].dt.strftime('%H:%M')
# 每日以开盘价为基准的相对变化
daily_open = sub.groupby('日期')['开盘'].first().to_dict()
sub['日内相对%'] = sub.apply(lambda r: (r['收盘'] - daily_open[r['日期']]) / daily_open[r['日期']] * 100, axis=1)

pattern = sub.groupby('分钟').agg(
    平均相对=('日内相对%', 'mean'),
    平均换手率=('换手率', 'mean'),
    标准差=('日内相对%', 'std'),
).round(3)
# 精简打印：每 15 分钟采样
pattern = pattern.reset_index()
sample_times = ['09:35','09:45','09:55','10:05','10:15','10:30','10:45','11:00','11:15','11:30',
                '13:05','13:15','13:30','13:45','14:00','14:15','14:30','14:45','15:00']
print(pattern[pattern['分钟'].isin(sample_times)].to_string(index=False))

# ============ 5. 最近 3 日 vs 之前 12 日：结构变化 ============
print("\n" + "="*100)
print("  五、近 3 日 vs 前 12 日 关键指标对比")
print("="*100)

recent3 = daily.tail(3)
before12 = daily.head(12)

def stats(x):
    return {
        '均价': round(x['收盘'].mean(), 2),
        '日均成交额_亿': round(x['成交额_亿'].mean(), 2),
        '日均振幅%': round(x['日振幅%'].mean(), 2),
        '平均日涨跌%': round(x['日涨跌%'].mean(), 2),
        '涨跌天数': f"{(x['日涨跌%']>0).sum()}涨/{(x['日涨跌%']<0).sum()}跌",
        '最高价': round(x['最高'].max(), 2),
        '最低价': round(x['最低'].min(), 2),
    }

print(">> 前 12 日（早期）:")
for k, v in stats(before12).items():
    print(f"   {k}: {v}")
print(">> 近 3 日:")
for k, v in stats(recent3).items():
    print(f"   {k}: {v}")

# ============ 6. 每日最大单笔放量点 ============
print("\n" + "="*100)
print("  六、每日单根 5 分钟最大放量点（主力动作痕迹）")
print("="*100)
big = sub.loc[sub.groupby('日期')['成交量'].idxmax()].copy()
big['成交额_万'] = (big['成交额'] / 1e4).round(0)
big['5min_涨跌%'] = ((big['收盘'] - big['开盘']) / big['开盘'] * 100).round(2)
print(big[['日期','时分','开盘','收盘','最高','最低','成交量','成交额_万','5min_涨跌%']].to_string(index=False))

# 保存汇总
out = f"易点天下_近15日_汇总_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
daily.to_csv(out, index=False, encoding='utf-8-sig')
print(f"\n已保存: {out}")
