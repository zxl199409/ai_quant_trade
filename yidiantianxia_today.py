#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易点天下(301171) 今日分时 - 精简观察版
数据源: akshare stock_zh_a_hist_min_em + stock_intraday_em
"""

import akshare as ak
import pandas as pd
import time
from datetime import datetime

SYMBOL = "301171"
TODAY = datetime.now().strftime('%Y-%m-%d')

pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 180)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')


def retry(fn, tries=5, sleep=3):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            last = e
            print(f"  [重试 {i+1}/{tries}] {type(e).__name__}, {sleep}s 后重试...")
            time.sleep(sleep)
            sleep *= 1.5
    raise last


# 1. 今日 1 分钟分时
print("拉取 1 分钟分时...")
df = retry(lambda: ak.stock_zh_a_hist_min_em(symbol=SYMBOL, period="1", adjust=""))
today = df[df['时间'].str.startswith(TODAY)].copy().reset_index(drop=True)

# 计算当日关键指标
open_px = today['开盘'].iloc[0]
high_px = today['最高'].max()
low_px = today['最低'].min()
last_px = today['收盘'].iloc[-1]
total_vol = today['成交量'].sum()
total_amt = today['成交额'].sum()
vwap = total_amt / total_vol / 100 if total_vol > 0 else 0

print(f"\n=== 易点天下(301171) {TODAY} 分时速览 ===")
print(f"时间区间: {today['时间'].iloc[0][-8:]} ~ {today['时间'].iloc[-1][-8:]}  ({len(today)} 根1分钟)")
print(f"开盘: {open_px:.2f}   最高: {high_px:.2f}   最低: {low_px:.2f}   现价: {last_px:.2f}")
print(f"当日振幅: {(high_px-low_px)/open_px*100:.2f}%   当日涨跌(开→现): {(last_px-open_px)/open_px*100:+.2f}%")
print(f"累计成交: {total_vol/1e4:.1f} 万手 / {total_amt/1e8:.2f} 亿元   均价(VWAP): {vwap:.2f}")

# 关键时点（每 15 分钟采样）
print(f"\n>> 15 分钟关键点采样:")
today['hhmm'] = today['时间'].str[-8:-3]
mark_pts = ['09:30','09:35','09:45','10:00','10:15','10:30','10:45','11:00','11:15','11:30',
            '13:00','13:15','13:30','13:45','14:00','14:15','14:30','14:45','15:00']
mk = today[today['hhmm'].isin(mark_pts)][['时间','开盘','收盘','最高','最低','成交量','成交额']].copy()
mk['时间'] = mk['时间'].str[-8:-3]
mk['累计手数'] = mk['成交量'].cumsum() // 1
print(mk.to_string(index=False))

# 成交量最大的 10 根 1 分钟
print(f"\n>> 今日放量 TOP 10 (1分钟):")
hot = today.nlargest(10, '成交量')[['时间','开盘','收盘','最高','最低','成交量','成交额']].copy()
hot['时间'] = hot['时间'].str[-8:]
hot['成交额_万'] = (hot['成交额'] / 1e4).round(0).astype(int)
hot = hot.drop(columns=['成交额'])
print(hot.to_string(index=False))

# 2. 逐笔（当日成交明细）看大单
print(f"\n>> 今日 TOP 15 大单成交 (逐笔):")
print("\n拉取当日逐笔...")
tick = retry(lambda: ak.stock_intraday_em(symbol=SYMBOL))
tick['金额_万'] = (tick['成交价'] * tick['手数'] * 100 / 1e4).round(1)
big = tick.nlargest(15, '手数')[['时间','成交价','手数','买卖盘性质','金额_万']]
print(big.to_string(index=False))

# 大单买卖比
BIG = 200  # 200手以上算大单
big_all = tick[tick['手数'] >= BIG]
buy_amt = big_all[big_all['买卖盘性质']=='买盘']['金额_万'].sum()
sell_amt = big_all[big_all['买卖盘性质']=='卖盘']['金额_万'].sum()
neutral_amt = big_all[big_all['买卖盘性质']=='中性盘']['金额_万'].sum()
print(f"\n>> 大单(≥200手)汇总:")
print(f"   主动买: {buy_amt:>8.1f} 万 | 主动卖: {sell_amt:>8.1f} 万 | 中性: {neutral_amt:>8.1f} 万 | 买卖净: {buy_amt-sell_amt:+.1f} 万")

# 保存
out = f"易点天下_{TODAY.replace('-','')}_分时速览.csv"
today.to_csv(out, index=False, encoding='utf-8-sig')
print(f"\n已保存 1 分钟分时: {out}")
