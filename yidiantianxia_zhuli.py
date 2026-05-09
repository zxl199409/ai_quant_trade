#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易点天下(301171) 主力资金深度分析
回答: 主力在干嘛? 为什么大跌?
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

SYMBOL = "301171"
NAME = "易点天下"

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')


def separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ============= 1. 当日逐笔：分级资金流 =============
def analyze_tick():
    separator("1. 当日逐笔成交 · 按单量分级的主力行为")
    df = ak.stock_intraday_em(symbol=SYMBOL)
    df['金额'] = df['成交价'] * df['手数'] * 100  # 元
    df['方向'] = df['买卖盘性质'].map({'买盘': 1, '卖盘': -1, '中性盘': 0})

    # 按单量分级 (A股习惯): 小单<50手, 中单50-200, 大单200-500, 特大单>=500
    def level(x):
        if x >= 500: return '特大单'
        if x >= 200: return '大单'
        if x >= 50:  return '中单'
        return '小单'
    df['级别'] = df['手数'].apply(level)

    print(f"逐笔总数: {len(df)}  时间: {df['时间'].iloc[0]} ~ {df['时间'].iloc[-1]}")

    # 按级别 × 方向 统计
    grp = df.groupby(['级别', '买卖盘性质']).agg(
        笔数=('手数', 'count'),
        手数=('手数', 'sum'),
        金额_万=('金额', lambda s: s.sum() / 1e4),
    ).reset_index()
    print("\n>> 按单量级别 × 买卖方向：")
    print(grp.to_string(index=False))

    # 净流入 (只按大单/特大单算主力)
    big = df[df['级别'].isin(['大单', '特大单'])]
    big_buy = big[big['买卖盘性质'] == '买盘']['金额'].sum() / 1e4
    big_sell = big[big['买卖盘性质'] == '卖盘']['金额'].sum() / 1e4
    small = df[df['级别'].isin(['小单', '中单'])]
    small_buy = small[small['买卖盘性质'] == '买盘']['金额'].sum() / 1e4
    small_sell = small[small['买卖盘性质'] == '卖盘']['金额'].sum() / 1e4

    print(f"\n>> 主力净流 (大单+特大单):")
    print(f"   买入: {big_buy:>10.2f} 万 | 卖出: {big_sell:>10.2f} 万 | 净额: {big_buy-big_sell:>+10.2f} 万")
    print(f">> 散户净流 (中小单):")
    print(f"   买入: {small_buy:>10.2f} 万 | 卖出: {small_sell:>10.2f} 万 | 净额: {small_buy-small_sell:>+10.2f} 万")

    # 分时段主力行为 (每30分钟)
    df['时间dt'] = pd.to_datetime('2026-04-24 ' + df['时间'])
    df['时段'] = df['时间dt'].dt.floor('30min').dt.strftime('%H:%M')
    big_seg = df[df['级别'].isin(['大单', '特大单'])].groupby(['时段', '买卖盘性质'])['金额'].sum().unstack(fill_value=0) / 1e4
    if '买盘' not in big_seg.columns: big_seg['买盘'] = 0
    if '卖盘' not in big_seg.columns: big_seg['卖盘'] = 0
    big_seg['净额_万'] = big_seg['买盘'] - big_seg['卖盘']
    print(f"\n>> 主力资金分时段流向 (每30分钟，万元):")
    print(big_seg[['买盘', '卖盘', '净额_万']].round(2).to_string())

    # TOP 10 特大单
    top = df[df['级别'] == '特大单'].copy()
    top = top.nlargest(15, '手数')
    print(f"\n>> TOP 15 特大单明细:")
    print(top[['时间', '成交价', '手数', '买卖盘性质', '金额']].assign(
        金额_万=lambda x: (x['金额'] / 1e4).round(2)
    )[['时间', '成交价', '手数', '买卖盘性质', '金额_万']].to_string(index=False))

    return df


# ============= 2. 开盘抛压分析 =============
def analyze_opening(tick_df):
    separator("2. 开盘抛压 · 为什么暴跌?")
    # 开盘 9:30-9:35 集中抛压
    open_df = tick_df[tick_df['时间'] < '09:35:00']
    print(f"开盘 5 分钟内逐笔: {len(open_df)} 笔")
    sell = open_df[open_df['买卖盘性质'] == '卖盘']
    buy = open_df[open_df['买卖盘性质'] == '买盘']
    print(f"  卖盘: {len(sell)}笔, {sell['手数'].sum()}手, 均价 {sell['成交价'].mean():.2f}")
    print(f"  买盘: {len(buy)}笔,  {buy['手数'].sum()}手, 均价 {buy['成交价'].mean():.2f}")
    print(f"  价格: {open_df['成交价'].iloc[0]:.2f} → {open_df['成交价'].iloc[-1]:.2f}")

    # 开盘 15 分钟内超大单卖出
    first15 = tick_df[tick_df['时间'] < '09:45:00']
    big_sell = first15[(first15['手数'] >= 200) & (first15['买卖盘性质'] == '卖盘')]
    print(f"\n开盘 15 分钟内大单卖盘({len(big_sell)}笔):")
    if len(big_sell) > 0:
        print(big_sell.nlargest(10, '手数')[['时间', '成交价', '手数']].to_string(index=False))
        print(f"累计卖出: {big_sell['手数'].sum()}手 ≈ {big_sell['金额'].sum()/1e4:.2f}万元")


# ============= 3. 资金流历史（5日/10日）=============
def analyze_fund_flow():
    separator("3. 近期资金流向（东财/同花顺口径，多日）")
    try:
        # 东财个股资金流向
        df = ak.stock_individual_fund_flow(stock=SYMBOL, market="sz")
        df = df.sort_values('日期', ascending=False).head(10)
        cols = [c for c in df.columns if c in ['日期', '收盘价', '涨跌幅',
                '主力净流入-净额', '主力净流入-净占比',
                '超大单净流入-净额', '大单净流入-净额',
                '中单净流入-净额', '小单净流入-净额']]
        print(">> 东财·近10日资金流 (单位: 元, 净额 = 流入-流出):")
        show = df[cols].copy()
        for c in show.columns:
            if '净流入-净额' in c:
                show[c] = (show[c] / 1e4).round(1).astype(str) + '万'
            elif '净占比' in c:
                show[c] = show[c].round(2).astype(str) + '%'
        print(show.to_string(index=False))
    except Exception as e:
        print(f"东财资金流失败: {e}")


# ============= 4. 龙虎榜 =============
def analyze_lhb():
    separator("4. 近期龙虎榜（机构 / 游资行为）")
    try:
        end = datetime.now().strftime('%Y%m%d')
        start = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
        df = ak.stock_lhb_detail_em(start_date=start, end_date=end)
        hit = df[df['代码'] == SYMBOL]
        if len(hit) == 0:
            print(f"近60天无龙虎榜记录")
        else:
            print(f"近60天上榜 {len(hit)} 次:")
            print(hit.to_string(index=False))
    except Exception as e:
        print(f"龙虎榜查询失败: {e}")


# ============= 5. 近期K线 + 量价 =============
def analyze_kline():
    separator("5. 近10日日K · 量价配合看主力意图")
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=25)).strftime('%Y%m%d')
    df = ak.stock_zh_a_hist(symbol=SYMBOL, start_date=start, end_date=end, adjust='qfq')
    df = df.tail(12)
    df = df[['日期','开盘','收盘','最高','最低','成交量','成交额','涨跌幅','换手率']].copy()
    df['量比5'] = (df['成交量'] / df['成交量'].rolling(5).mean()).round(2)
    df['成交额_亿'] = (df['成交额'] / 1e8).round(2)
    df = df.drop(columns=['成交额'])
    print(df.to_string(index=False))


# ============= 6. 盘口五档 =============
def analyze_orderbook():
    separator("6. 当前盘口五档 + 实时快照")
    try:
        q = ak.stock_bid_ask_em(symbol=SYMBOL)
        print(q.to_string(index=False))
    except Exception as e:
        print(f"盘口获取失败: {e}")


# ============= 7. 近期公告 =============
def analyze_news():
    separator("7. 近期公告/新闻（可能的利空触发）")
    try:
        news = ak.stock_news_em(symbol=SYMBOL)
        print(news.head(15)[['发布时间', '新闻标题']].to_string(index=False))
    except Exception as e:
        print(f"公告获取失败: {e}")


if __name__ == "__main__":
    print(f"\n{'#'*70}")
    print(f"#  {NAME}({SYMBOL}) 主力资金深度分析")
    print(f"#  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}")

    tick_df = analyze_tick()
    analyze_opening(tick_df)
    analyze_kline()
    analyze_orderbook()
    analyze_fund_flow()
    analyze_lhb()
    analyze_news()
