#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易点天下(301171) 分时数据获取
"""

import akshare as ak
import pandas as pd
from datetime import datetime

SYMBOL = "301171"
NAME = "易点天下"

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 200)


def get_today_tick():
    """当日分时 tick (逐笔成交近似，1分钟)"""
    df = ak.stock_zh_a_hist_min_em(
        symbol=SYMBOL,
        period="1",
        adjust=""
    )
    return df


def get_minute_kline(period="5"):
    """多日分时 K 线，period: 1/5/15/30/60 分钟"""
    df = ak.stock_zh_a_hist_min_em(
        symbol=SYMBOL,
        period=period,
        adjust="qfq"
    )
    return df


def get_intraday_pre_post():
    """盘中分时（含前一交易日）—— 东财接口"""
    df = ak.stock_intraday_em(symbol=SYMBOL)
    return df


if __name__ == "__main__":
    print(f"=== {NAME}({SYMBOL}) 分时数据 ===")
    print(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1分钟分时 K 线
    print(">>> 1分钟分时K线（最近）")
    df1 = get_minute_kline(period="1")
    print(f"共 {len(df1)} 条, 时间范围: {df1['时间'].iloc[0]} ~ {df1['时间'].iloc[-1]}")
    print(df1.tail(30).to_string(index=False))
    out1 = f"易点天下_1min分时_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df1.to_csv(out1, index=False, encoding='utf-8-sig')
    print(f"已保存: {out1}\n")

    # 5分钟分时
    print(">>> 5分钟分时K线（最近）")
    df5 = get_minute_kline(period="5")
    print(f"共 {len(df5)} 条, 时间范围: {df5['时间'].iloc[0]} ~ {df5['时间'].iloc[-1]}")
    print(df5.tail(20).to_string(index=False))
    out5 = f"易点天下_5min分时_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df5.to_csv(out5, index=False, encoding='utf-8-sig')
    print(f"已保存: {out5}\n")

    # 当日逐笔
    print(">>> 当日盘中分时（逐笔/成交明细）")
    try:
        df_tick = get_intraday_pre_post()
        print(f"共 {len(df_tick)} 条")
        print(df_tick.tail(30).to_string(index=False))
        out_tick = f"易点天下_逐笔_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df_tick.to_csv(out_tick, index=False, encoding='utf-8-sig')
        print(f"已保存: {out_tick}")
    except Exception as e:
        print(f"逐笔数据获取失败: {e}")
