#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
倍量后地量企稳选股器
核心逻辑：放量建仓 → 缩量回调 → 地量 → 企稳上涨
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class DiLiangScanner:
    """地量企稳扫描器"""

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

    def detect_diliang_pattern(self, df, symbol, name):
        """
        检测：放量 → 缩量回调 → 地量 → 上涨

        条件：
        1. 近15日内有倍量日（成交额>前日2倍）
        2. 倍量后出现地量（成交额是近20日最低或接近最低）
        3. 地量日后股价企稳或上涨（不破地量日低点，且有阳线）
        4. 当前处于上涨状态
        """
        if df is None or len(df) < 25:
            return None

        # 计算指标
        df['amo_ratio'] = df['amount'] / df['amount'].shift(1)
        df['vol_ma5'] = df['amount'].rolling(5).mean()
        df['vol_ma20'] = df['amount'].rolling(20).mean()
        df['is_yang'] = df['close'] > df['open']  # 阳线
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA10'] = df['close'].rolling(10).mean()

        # 计算近20日最低成交额
        df['vol_min20'] = df['amount'].rolling(20).min()

        best_signal = None
        best_score = 0

        # 寻找倍量日（在近15日内）
        for i in range(len(df) - 15, len(df) - 3):
            if i < 1:
                continue

            row = df.iloc[i]

            # 条件1：是倍量日
            if row['amo_ratio'] < 2:
                continue

            # 倍量日应该是阳线
            if not row['is_yang']:
                continue

            double_idx = i
            double_day = row
            double_amount = row['amount']
            double_low = row['low']
            double_high = row['high']
            double_date = row['date']
            double_change = row['pctChg']

            # 倍量日之后的数据
            after_data = df.iloc[double_idx + 1:]
            if len(after_data) < 2:
                continue

            # 条件2：找地量日（倍量后成交额最低的那天）
            diliang_idx_rel = after_data['amount'].idxmin()
            diliang_idx = df.index.get_loc(diliang_idx_rel)
            diliang_day = df.iloc[diliang_idx]
            diliang_amount = diliang_day['amount']
            diliang_date = diliang_day['date']
            diliang_low = diliang_day['low']

            # 地量需要足够小（小于倍量日的40%，或者是近20日最低）
            is_diliang = (diliang_amount < double_amount * 0.4) or \
                        (diliang_amount <= df.iloc[diliang_idx]['vol_min20'] * 1.1)

            if not is_diliang:
                continue

            # 条件3：地量后股价企稳或上涨
            after_diliang = df.iloc[diliang_idx + 1:]
            if len(after_diliang) < 1:
                continue

            # 地量后不能破地量日低点
            if after_diliang['low'].min() < diliang_low * 0.98:
                continue

            # 地量后要有阳线（企稳上涨信号）
            yang_count = after_diliang['is_yang'].sum()
            if yang_count < 1:
                continue

            # 条件4：当前处于上涨状态
            current = df.iloc[-1]
            current_price = current['close']
            prev_price = df.iloc[-2]['close']

            # 当前价格高于地量日收盘价
            if current_price < diliang_day['close']:
                continue

            # 计算得分
            score = 0
            reasons = []

            # 1. 倍量强度
            if row['amo_ratio'] >= 3:
                score += 3
                reasons.append(f"三倍量建仓({row['amo_ratio']:.1f}倍)")
            else:
                score += 2
                reasons.append(f"倍量建仓({row['amo_ratio']:.1f}倍)")

            # 2. 地量程度
            diliang_ratio = diliang_amount / double_amount
            if diliang_ratio < 0.25:
                score += 3
                reasons.append(f"极度缩量({diliang_ratio:.0%})")
            elif diliang_ratio < 0.4:
                score += 2
                reasons.append(f"明显缩量({diliang_ratio:.0%})")

            # 3. 地量后涨幅
            rise_after_diliang = (current_price - diliang_day['close']) / diliang_day['close'] * 100
            if rise_after_diliang > 5:
                score += 2
                reasons.append(f"地量后涨{rise_after_diliang:.1f}%")
            elif rise_after_diliang > 0:
                score += 1
                reasons.append(f"地量后企稳(+{rise_after_diliang:.1f}%)")

            # 4. 回调幅度（从倍量日高点到地量日低点）
            pullback = (double_high - diliang_low) / double_high * 100
            if pullback < 8:
                score += 2
                reasons.append(f"回调浅({pullback:.1f}%)")
            elif pullback < 15:
                score += 1
                reasons.append(f"回调适中({pullback:.1f}%)")

            # 5. 均线状态
            if current_price > current['MA5'] and current['MA5'] > current['MA10']:
                score += 1
                reasons.append("均线多头")
            elif current_price > current['MA5']:
                score += 1
                reasons.append("站上MA5")

            # 6. 最近阳线
            recent_yang = df.iloc[-3:]['is_yang'].sum()
            if recent_yang >= 2:
                score += 1
                reasons.append(f"近3日{recent_yang}阳")

            # 7. 当日是阳线
            if current['is_yang']:
                score += 1
                reasons.append("今日收阳")

            if score > best_score:
                best_score = score
                best_signal = {
                    'symbol': symbol,
                    'name': name,
                    'double_date': double_date,
                    'double_change': double_change,
                    'double_amount': double_amount,
                    'amo_ratio': row['amo_ratio'],
                    'diliang_date': diliang_date,
                    'diliang_amount': diliang_amount,
                    'diliang_ratio': diliang_ratio,
                    'diliang_low': diliang_low,
                    'pullback': pullback,
                    'rise_after_diliang': rise_after_diliang,
                    'current_price': current_price,
                    'ma5': current['MA5'],
                    'ma10': current['MA10'],
                    'score': score,
                    'reasons': reasons,
                    'double_low': double_low,
                }

        return best_signal if best_score >= 5 else None

    def scan_stocks(self, stock_list):
        """扫描股票列表"""
        print("\n" + "=" * 70)
        print("🔍 放量→地量→上涨 形态扫描")
        print(f"   扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   筛选条件: 倍量阳线 → 缩至地量 → 企稳上涨")
        print("=" * 70)

        self.results = []

        for symbol, name in stock_list:
            print(f"扫描: {name}({symbol})...", end=" ")
            df = self.fetch_daily_data(symbol)
            result = self.detect_diliang_pattern(df, symbol, name)

            if result:
                self.results.append(result)
                print(f"✅ 得分:{result['score']}")
            else:
                print("⚪")

        return self.results

    def print_report(self):
        """打印报告"""
        print("\n\n" + "=" * 70)
        print("📊 放量→地量→上涨 扫描结果")
        print("=" * 70)

        if not self.results:
            print("\n⚠️ 未发现符合条件的股票")
            return

        # 按得分排序
        self.results.sort(key=lambda x: x['score'], reverse=True)

        print(f"\n🎯 发现 {len(self.results)} 只符合条件:\n")

        for i, r in enumerate(self.results, 1):
            print(f"{'='*65}")
            print(f"🏆 #{i} {r['name']}({r['symbol']}) - 综合得分: {r['score']}/13")
            print(f"{'='*65}")
            print()
            print(f"   📈 放量阶段:")
            print(f"      日期: {r['double_date'].strftime('%Y-%m-%d')}")
            print(f"      倍数: {r['amo_ratio']:.1f}倍量")
            print(f"      涨幅: {r['double_change']:+.2f}%")
            print()
            print(f"   📉 地量阶段:")
            print(f"      日期: {r['diliang_date'].strftime('%Y-%m-%d')}")
            print(f"      缩量: {r['diliang_ratio']:.0%} (相对倍量日)")
            print(f"      回调: {r['pullback']:.1f}%")
            print()
            print(f"   📊 当前状态:")
            print(f"      现价: ¥{r['current_price']:.2f}")
            print(f"      地量后涨: {r['rise_after_diliang']:+.1f}%")
            print(f"      MA5/MA10: ¥{r['ma5']:.2f} / ¥{r['ma10']:.2f}")
            print()
            print(f"   ✅ 形态特征:")
            for reason in r['reasons']:
                print(f"      • {reason}")
            print()
            print(f"   💡 操作建议:")
            print(f"      介入价: ¥{r['current_price']:.2f} 附近")
            stop_loss = min(r['diliang_low'], r['double_low']) * 0.97
            print(f"      止损位: ¥{stop_loss:.2f} (破地量/倍量低点)")
            target = r['current_price'] * 1.15
            print(f"      目标位: ¥{target:.2f} (+15%)")
            risk = (r['current_price'] - stop_loss) / r['current_price'] * 100
            reward = 15
            print(f"      盈亏比: 1:{reward/risk:.1f}")

        print("\n" + "=" * 70)
        print("📋 形态示意:")
        print()
        print("   倍量阳线        缩量回调         地量企稳        上涨启动")
        print("      ┃              ┃                ┃               ┃")
        print("      ▓▓▓            ░                ·               ▓")
        print("      ▓▓▓           ░░               ··              ▓▓")
        print("      ▓▓▓          ░░░              ···             ▓▓▓")
        print("     ─┴─┴─────────┴──┴────────────┴───┴───────────┴───┴─→")
        print("     放量建仓      获利盘洗出      地量=洗盘结束    新一轮上涨")
        print()
        print("⚠️ 风险提示: 破地量日低点必须止损!")
        print("=" * 70)


def main():
    # 扫描列表
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
        ("301171", "易点天下"),
    ]

    scanner = DiLiangScanner()
    scanner.scan_stocks(stock_list)
    scanner.print_report()


if __name__ == "__main__":
    main()
