#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易点天下(301171) 实时主力动作（最近30分钟聚焦）
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
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            print(f"  [重试 {i+1}] {type(e).__name__} - {sleep:.1f}s后重试")
            time.sleep(sleep)
            sleep *= 1.5
    return None


NOW = datetime.now().strftime('%H:%M:%S')
print(f"\n{'='*70}")
print(f"  易点天下 301171  实时主力监控  @{TODAY} {NOW}")
print(f"{'='*70}\n")

# 1. 最新 1 分钟分时
print(">>> 拉取最新 1 分钟分时...")
df = retry(lambda: ak.stock_zh_a_hist_min_em(symbol=SYMBOL, period="1", adjust=""))
today = df[df['时间'].str.startswith(TODAY)].copy().reset_index(drop=True)
total_bars = len(today)
last_bar = today.iloc[-1]
last_price = last_bar['收盘']
open_price = today['开盘'].iloc[0]
high_price = today['最高'].max()
low_price = today['最低'].min()
total_vol = today['成交量'].sum()
total_amt = today['成交额'].sum()
vwap = total_amt / total_vol / 100 if total_vol > 0 else 0

print(f"已有 1 分钟 K 线 {total_bars} 根")
print(f"当前时点: {last_bar['时间']}")
print(f"现价: {last_price:.2f}  |  开: {open_price:.2f}  |  高: {high_price:.2f}  |  低: {low_price:.2f}  |  VWAP: {vwap:.2f}")
print(f"距开盘: {(last_price-open_price)/open_price*100:+.2f}%")
print(f"距昨收(47.60): {(last_price-47.60)/47.60*100:+.2f}%")
print(f"距VWAP: {(last_price-vwap)/vwap*100:+.2f}%")
print(f"累计成交: {total_vol/1e4:.1f}万手 / {total_amt/1e8:.2f}亿")

# 2. 最近 30 根 1 分钟 (最近30分钟)
print(f"\n>>> 最近 30 分钟 1 分钟分时:")
tail30 = today.tail(30)[['时间','开盘','收盘','最高','最低','成交量','成交额']].copy()
tail30['时间'] = tail30['时间'].str[-8:]
tail30['成交额_万'] = (tail30['成交额']/1e4).round(0).astype(int)
tail30['涨跌%'] = ((tail30['收盘']-tail30['开盘'])/tail30['开盘']*100).round(2)
tail30 = tail30.drop(columns=['成交额'])
print(tail30.to_string(index=False))

# 3. 最新逐笔（最近 100 条）
print(f"\n>>> 拉取最新逐笔成交...")
time.sleep(5)
tick = retry(lambda: ak.stock_intraday_em(symbol=SYMBOL))
if tick is None or len(tick) == 0:
    print("逐笔数据获取失败")
else:
    tick['金额'] = tick['成交价'] * tick['手数'] * 100
    tick['金额_万'] = (tick['金额']/1e4).round(1)
    print(f"逐笔共 {len(tick)} 笔")

    # 最近 100 笔的买卖比
    recent = tick.tail(200)
    buy_amt = recent[recent['买卖盘性质']=='买盘']['金额_万'].sum()
    sell_amt = recent[recent['买卖盘性质']=='卖盘']['金额_万'].sum()
    print(f"\n最近 200 笔买卖比:")
    print(f"  主动买: {buy_amt:>8.1f} 万")
    print(f"  主动卖: {sell_amt:>8.1f} 万")
    print(f"  买卖净: {buy_amt-sell_amt:+.1f} 万 ({'买方占优' if buy_amt>sell_amt else '卖方占优'})")

    # 最近 20 笔大单（>= 100手）
    big_recent = recent[recent['手数'] >= 100].tail(20)
    print(f"\n>>> 最近 20 笔大单(≥100手):")
    print(big_recent[['时间','成交价','手数','买卖盘性质','金额_万']].to_string(index=False))

    # 全天对比: 开盘30分钟 vs 近30分钟
    tick['时间dt'] = pd.to_datetime(f'{TODAY} ' + tick['时间'])
    # 全天大单(>=200手)
    big_all = tick[tick['手数'] >= 200]
    # 最近30分钟大单
    last30_cut = pd.Timestamp.now() - pd.Timedelta(minutes=30)
    recent30_big = big_all[big_all['时间dt'] >= last30_cut]
    print(f"\n>>> 最近 30 分钟大单(≥200手)汇总:")
    if len(recent30_big) > 0:
        rb_buy = recent30_big[recent30_big['买卖盘性质']=='买盘']['金额_万'].sum()
        rb_sell = recent30_big[recent30_big['买卖盘性质']=='卖盘']['金额_万'].sum()
        print(f"  大单主动买: {rb_buy:.1f} 万 ({len(recent30_big[recent30_big['买卖盘性质']=='买盘'])}笔)")
        print(f"  大单主动卖: {rb_sell:.1f} 万 ({len(recent30_big[recent30_big['买卖盘性质']=='卖盘'])}笔)")
        print(f"  大单净额:   {rb_buy-rb_sell:+.1f} 万")
        print(f"\n  近 30 分钟大单明细:")
        print(recent30_big[['时间','成交价','手数','买卖盘性质','金额_万']].to_string(index=False))
    else:
        print("  近30分钟无 ≥200 手的大单，买卖清淡")

# 4. 盘口五档
print(f"\n>>> 拉取实时盘口...")
time.sleep(3)
try:
    q = retry(lambda: ak.stock_bid_ask_em(symbol=SYMBOL), tries=3)
    if q is not None:
        print(q.to_string(index=False))
except Exception as e:
    print(f"盘口失败: {e}")
