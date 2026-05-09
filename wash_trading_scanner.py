#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
倍量后洗盘股票筛选器
识别：倍量建仓 → 缩量回调 → 不破支撑 的洗盘形态
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class WashTradingScanner:
    """洗盘形态扫描器"""

    def __init__(self):
        self.lg = bs.login()
        print(f"Baostock登录: {self.lg.error_msg}")
        self.results = []

    def __del__(self):
        bs.logout()

    def fetch_daily_data(self, symbol, days=60):
        """获取日线数据"""
        try:
            if symbol.startswith('6'):
                bs_code = f'sh.{symbol}'
            else:
                bs_code = f'sz.{symbol}'

            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            rs = bs.query_history_k_data_plus(
                bs_code,
                'date,open,high,low,close,volume,amount,turn,pctChg',
                start_date=start_date,
                end_date=end_date,
                frequency='d',
                adjustflag='2'
            )

            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return None

            df = pd.DataFrame(data_list, columns=rs.fields)
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            return None

    def detect_wash_trading(self, df, symbol, name):
        """
        检测洗盘形态

        条件：
        1. 近10日内出现倍量日（成交额>前日2倍）
        2. 倍量日后连续缩量（至少2天成交额递减或维持低位）
        3. 价格回调有限（不超过倍量日涨幅的70%）
        4. 不破倍量日最低价
        5. 当前处于缩量状态
        """
        if df is None or len(df) < 20:
            return None

        # 计算成交额变化
        df['amo_ratio'] = df['amount'] / df['amount'].shift(1)
        df['is_double'] = df['amo_ratio'] >= 2  # 倍量
        df['is_triple'] = df['amo_ratio'] >= 3  # 三倍量
        df['is_shrink'] = df['amo_ratio'] <= 0.7  # 缩量（不足前日70%）

        # 计算均线
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA10'] = df['close'].rolling(10).mean()
        df['MA20'] = df['close'].rolling(20).mean()
        df['VOL_MA5'] = df['amount'].rolling(5).mean()

        # 在最近10个交易日内寻找倍量日
        recent_days = 10
        lookback_start = max(0, len(df) - recent_days - 1)

        wash_signals = []

        for i in range(lookback_start, len(df) - 2):
            row = df.iloc[i]

            # 条件1：是否是倍量日
            if not row['is_double']:
                continue

            double_day_idx = i
            double_day = row
            double_day_date = row['date']
            double_day_low = row['low']
            double_day_high = row['high']
            double_day_close = row['close']
            double_day_open = row['open']
            double_day_amount = row['amount']
            double_day_change = row['pctChg']

            # 倍量日应该是阳线或小阴线（涨幅>-2%）
            if double_day_change < -2:
                continue

            # 检查倍量日之后的走势
            days_after = len(df) - double_day_idx - 1
            if days_after < 2:
                continue

            after_data = df.iloc[double_day_idx + 1:]

            # 条件2：倍量后是否缩量
            shrink_count = 0
            for j in range(min(5, len(after_data))):
                if after_data.iloc[j]['amount'] < double_day_amount * 0.7:
                    shrink_count += 1

            if shrink_count < 2:
                continue

            # 条件3：价格回调是否有限
            lowest_after = after_data['low'].min()
            highest_after = after_data['high'].max()
            current_close = df.iloc[-1]['close']

            # 不破倍量日低点
            if lowest_after < double_day_low * 0.97:  # 允许3%的误差
                continue

            # 回调幅度（从倍量日高点到之后最低点）
            pullback_pct = (double_day_high - lowest_after) / double_day_high * 100

            # 回调不超过10%
            if pullback_pct > 10:
                continue

            # 条件4：当前是否处于缩量状态
            current_amount = df.iloc[-1]['amount']
            is_current_shrink = current_amount < double_day_amount * 0.6

            # 条件5：均线支撑
            current_ma5 = df.iloc[-1]['MA5']
            current_ma10 = df.iloc[-1]['MA10']
            ma_support = current_close >= current_ma5 * 0.98 or current_close >= current_ma10 * 0.98

            # 综合评分
            score = 0
            reasons = []

            # 倍量强度
            if row['is_triple']:
                score += 3
                reasons.append("三倍量建仓")
            else:
                score += 2
                reasons.append("倍量建仓")

            # 缩量程度
            avg_amount_after = after_data['amount'].mean()
            shrink_ratio = avg_amount_after / double_day_amount
            if shrink_ratio < 0.4:
                score += 2
                reasons.append(f"缩量明显({shrink_ratio:.0%})")
            elif shrink_ratio < 0.6:
                score += 1
                reasons.append(f"温和缩量({shrink_ratio:.0%})")

            # 回调幅度
            if pullback_pct < 5:
                score += 2
                reasons.append(f"回调极小({pullback_pct:.1f}%)")
            elif pullback_pct < 8:
                score += 1
                reasons.append(f"回调有限({pullback_pct:.1f}%)")

            # 均线支撑
            if ma_support:
                score += 1
                reasons.append("均线支撑有效")

            # 当前缩量
            if is_current_shrink:
                score += 1
                reasons.append("当前缩量待涨")

            # 洗盘天数
            wash_days = days_after
            if 3 <= wash_days <= 7:
                score += 1
                reasons.append(f"洗盘{wash_days}天，时机较好")

            if score >= 5:  # 达到阈值才记录
                wash_signals.append({
                    'symbol': symbol,
                    'name': name,
                    'double_day_date': double_day_date,
                    'double_day_change': double_day_change,
                    'double_day_amount': double_day_amount,
                    'amo_ratio': row['amo_ratio'],
                    'current_price': current_close,
                    'double_day_low': double_day_low,
                    'lowest_after': lowest_after,
                    'pullback_pct': pullback_pct,
                    'shrink_ratio': shrink_ratio,
                    'wash_days': wash_days,
                    'score': score,
                    'reasons': reasons,
                    'ma5': current_ma5,
                    'ma10': current_ma10,
                    'ma_support': ma_support
                })

        # 返回得分最高的信号
        if wash_signals:
            return max(wash_signals, key=lambda x: x['score'])
        return None

    def scan_stocks(self, stock_list):
        """扫描股票列表"""
        print("\n" + "=" * 70)
        print("🔍 倍量后洗盘形态扫描")
        print(f"   扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        self.results = []

        for symbol, name in stock_list:
            print(f"\n扫描: {name}({symbol})...", end=" ")
            df = self.fetch_daily_data(symbol)
            result = self.detect_wash_trading(df, symbol, name)

            if result:
                self.results.append(result)
                print(f"✅ 发现洗盘形态! 得分:{result['score']}")
            else:
                print("⚪ 未发现")

        return self.results

    def print_report(self):
        """打印报告"""
        print("\n\n" + "=" * 70)
        print("📊 洗盘形态扫描结果")
        print("=" * 70)

        if not self.results:
            print("\n⚠️ 未发现符合条件的洗盘形态")
            return

        # 按得分排序
        self.results.sort(key=lambda x: x['score'], reverse=True)

        print(f"\n🎯 发现 {len(self.results)} 只股票存在洗盘形态:\n")

        for i, r in enumerate(self.results, 1):
            print(f"{'='*60}")
            print(f"🏆 #{i} {r['name']}({r['symbol']}) - 得分: {r['score']}/10")
            print(f"{'='*60}")
            print(f"   倍量日期: {r['double_day_date'].strftime('%Y-%m-%d')}")
            print(f"   倍量倍数: {r['amo_ratio']:.1f}倍")
            print(f"   倍量日涨幅: {r['double_day_change']:+.2f}%")
            print(f"   洗盘天数: {r['wash_days']}天")
            print(f"   缩量程度: {r['shrink_ratio']:.0%} (相对倍量日)")
            print(f"   回调幅度: {r['pullback_pct']:.1f}%")
            print(f"   当前价格: ¥{r['current_price']:.2f}")
            print(f"   关键支撑: ¥{r['double_day_low']:.2f} (倍量日低点)")
            print(f"   MA5/MA10: ¥{r['ma5']:.2f} / ¥{r['ma10']:.2f}")
            print(f"\n   📋 特征:")
            for reason in r['reasons']:
                print(f"      • {reason}")

            # 操作建议
            print(f"\n   💡 操作建议:")
            print(f"      买入参考: ¥{r['current_price']:.2f} 附近")
            print(f"      止损位: ¥{r['double_day_low'] * 0.97:.2f} (破倍量日低点)")
            target = r['current_price'] * 1.1
            print(f"      目标位: ¥{target:.2f} (+10%)")

        print("\n" + "=" * 70)
        print("⚠️ 风险提示:")
        print("   • 洗盘形态需结合大盘环境判断")
        print("   • 破倍量日低点必须止损")
        print("   • 放量突破时可加仓确认")
        print("=" * 70)


def main():
    # AI军事化概念股 + 一些热门股票
    stock_list = [
        # AI军事化
        ("688297", "中航无人机"),
        ("002389", "航天彩虹"),
        ("688070", "纵横股份"),
        ("002049", "紫光国微"),
        ("000733", "振华科技"),
        ("600562", "国睿科技"),
        ("688002", "睿创微纳"),
        ("600435", "北方导航"),
        ("600879", "航天电子"),
        ("600118", "中国卫星"),
        ("300496", "中科创达"),
        ("002268", "卫士通"),
        ("002465", "海格通信"),
        ("000519", "中兵红箭"),
        ("300123", "亚光科技"),
        # 用户持仓
        ("301171", "易点天下"),
    ]

    scanner = WashTradingScanner()
    scanner.scan_stocks(stock_list)
    scanner.print_report()


if __name__ == "__main__":
    main()
