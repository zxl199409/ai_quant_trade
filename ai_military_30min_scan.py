#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI军事化概念股 30分钟级别 缠论买点扫描
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ChanLun30MinScanner:
    """30分钟级别缠论扫描器"""

    def __init__(self):
        self.results = []

    def fetch_30min_data(self, symbol, name):
        """获取30分钟K线数据"""
        try:
            # akshare获取分钟级别数据
            data = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period="30",
                adjust="qfq"
            )

            if data is None or data.empty:
                return None

            # 重命名列
            data.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Latest']
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)

            # 只取最近的数据（约10个交易日的30分钟K线）
            data = data.tail(160)  # 8根/天 * 20天

            return data

        except Exception as e:
            print(f"  获取 {name}({symbol}) 数据失败: {e}")
            return None

    def find_fenxing(self, data):
        """识别分型"""
        fenxing = []

        for i in range(1, len(data) - 1):
            current = data.iloc[i]
            prev = data.iloc[i-1]
            next_bar = data.iloc[i+1]

            # 顶分型
            if (current['High'] >= prev['High'] and current['High'] >= next_bar['High'] and
                current['Low'] >= min(prev['Low'], next_bar['Low'])):
                fenxing.append({
                    'index': i,
                    'date': data.index[i],
                    'type': 'top',
                    'price': current['High'],
                    'high': current['High'],
                    'low': current['Low']
                })

            # 底分型
            elif (current['Low'] <= prev['Low'] and current['Low'] <= next_bar['Low'] and
                  current['High'] <= max(prev['High'], next_bar['High'])):
                fenxing.append({
                    'index': i,
                    'date': data.index[i],
                    'type': 'bottom',
                    'price': current['Low'],
                    'high': current['High'],
                    'low': current['Low']
                })

        return fenxing

    def find_bi(self, fenxing):
        """识别笔"""
        bi = []

        if len(fenxing) < 2:
            return bi

        current_bi = None

        for fx in fenxing:
            if current_bi is None:
                current_bi = fx
            else:
                if fx['type'] != current_bi['type']:
                    # 笔至少需要跨越5根K线
                    if fx['index'] - current_bi['index'] >= 4:
                        bi.append({
                            'start': current_bi,
                            'end': fx,
                            'direction': 'up' if current_bi['type'] == 'bottom' else 'down',
                            'strength': abs(fx['price'] - current_bi['price'])
                        })
                        current_bi = fx
                else:
                    if fx['type'] == 'top' and fx['price'] > current_bi['price']:
                        current_bi = fx
                    elif fx['type'] == 'bottom' and fx['price'] < current_bi['price']:
                        current_bi = fx

        return bi

    def find_zhongshu(self, bi):
        """识别中枢"""
        zhongshu = []

        if len(bi) < 3:
            return zhongshu

        for i in range(len(bi) - 2):
            bi1 = bi[i]
            bi2 = bi[i + 1]
            bi3 = bi[i + 2]

            max_low = max(min(bi1['start']['price'], bi1['end']['price']),
                         min(bi2['start']['price'], bi2['end']['price']),
                         min(bi3['start']['price'], bi3['end']['price']))

            min_high = min(max(bi1['start']['price'], bi1['end']['price']),
                          max(bi2['start']['price'], bi2['end']['price']),
                          max(bi3['start']['price'], bi3['end']['price']))

            if max_low < min_high:
                zhongshu.append({
                    'start_date': bi1['start']['date'],
                    'end_date': bi3['end']['date'],
                    'high': min_high,
                    'low': max_low,
                    'center': (max_low + min_high) / 2,
                    'height': min_high - max_low,
                    'bi_count': 3
                })

        return self._merge_zhongshu(zhongshu)

    def _merge_zhongshu(self, zhongshu_list):
        """合并重叠的中枢"""
        if len(zhongshu_list) <= 1:
            return zhongshu_list

        merged = []
        current = zhongshu_list[0]

        for i in range(1, len(zhongshu_list)):
            next_zs = zhongshu_list[i]

            if current['low'] <= next_zs['high'] and current['high'] >= next_zs['low']:
                current = {
                    'start_date': current['start_date'],
                    'end_date': next_zs['end_date'],
                    'high': max(current['high'], next_zs['high']),
                    'low': min(current['low'], next_zs['low']),
                    'center': (max(current['high'], next_zs['high']) + min(current['low'], next_zs['low'])) / 2,
                    'height': max(current['high'], next_zs['high']) - min(current['low'], next_zs['low']),
                    'bi_count': current['bi_count'] + next_zs['bi_count'] - 1
                }
            else:
                merged.append(current)
                current = next_zs

        merged.append(current)
        return merged

    def check_beichi(self, bi, data):
        """检查背驰"""
        if len(bi) < 2:
            return None

        # 获取最近两笔
        last_bi = bi[-1]
        prev_bi = bi[-2] if len(bi) >= 2 else None

        if prev_bi is None:
            return None

        # 同向的两笔比较
        if last_bi['direction'] == prev_bi['direction']:
            return None

        # 找同向的上一笔
        same_dir_bi = None
        for i in range(len(bi) - 3, -1, -1):
            if bi[i]['direction'] == last_bi['direction']:
                same_dir_bi = bi[i]
                break

        if same_dir_bi is None:
            return None

        # 比较力度（用价格幅度简化）
        last_strength = last_bi['strength']
        same_strength = same_dir_bi['strength']

        # 背驰条件：当前笔力度小于前同向笔
        if last_strength < same_strength * 0.8:
            return {
                'type': '背驰',
                'direction': last_bi['direction'],
                'strength_ratio': last_strength / same_strength
            }

        return None

    def find_buy_points(self, data, fenxing, bi, zhongshu):
        """寻找买点"""
        buy_points = []

        if not zhongshu or not bi:
            return buy_points

        current_price = data['Close'].iloc[-1]
        current_date = data.index[-1]
        last_zs = zhongshu[-1]

        # 检查背驰
        beichi = self.check_beichi(bi, data)

        # 一类买点：下跌背驰后的底分型
        if beichi and beichi['direction'] == 'down':
            # 找最近的底分型
            for fx in reversed(fenxing):
                if fx['type'] == 'bottom' and fx['price'] < last_zs['low']:
                    buy_points.append({
                        'type': '一类买点',
                        'date': fx['date'],
                        'price': fx['price'],
                        'current_price': current_price,
                        'distance': (current_price - fx['price']) / fx['price'] * 100,
                        'confidence': 85,
                        'reason': f"30分钟级别下跌背驰，底分型确认"
                    })
                    break

        # 二类买点：回调不破中枢下沿
        recent_bottoms = [fx for fx in fenxing[-10:] if fx['type'] == 'bottom']
        for fx in recent_bottoms:
            if last_zs['low'] <= fx['price'] <= last_zs['center']:
                # 检查是否在中枢结束之后
                if fx['date'] > last_zs['end_date']:
                    buy_points.append({
                        'type': '二类买点',
                        'date': fx['date'],
                        'price': fx['price'],
                        'current_price': current_price,
                        'distance': (current_price - fx['price']) / fx['price'] * 100,
                        'confidence': 75,
                        'reason': f"30分钟级别回调不破中枢下沿"
                    })

        # 三类买点：突破中枢后回踩不破中枢上沿
        if current_price > last_zs['high']:
            for fx in recent_bottoms:
                if fx['price'] > last_zs['high'] * 0.98 and fx['date'] > last_zs['end_date']:
                    buy_points.append({
                        'type': '三类买点',
                        'date': fx['date'],
                        'price': fx['price'],
                        'current_price': current_price,
                        'distance': (current_price - fx['price']) / fx['price'] * 100,
                        'confidence': 70,
                        'reason': f"30分钟级别突破中枢后回踩确认"
                    })

        return buy_points

    def analyze_stock(self, symbol, name):
        """分析单只股票"""
        data = self.fetch_30min_data(symbol, name)

        if data is None or len(data) < 30:
            return None

        fenxing = self.find_fenxing(data)
        bi = self.find_bi(fenxing)
        zhongshu = self.find_zhongshu(bi)
        buy_points = self.find_buy_points(data, fenxing, bi, zhongshu)

        current_price = data['Close'].iloc[-1]

        # 计算技术指标
        data['MA5'] = data['Close'].rolling(5).mean()
        data['MA20'] = data['Close'].rolling(20).mean()

        ma5 = data['MA5'].iloc[-1]
        ma20 = data['MA20'].iloc[-1]

        # 趋势判断
        if ma5 > ma20:
            trend = "多头排列"
        else:
            trend = "空头排列"

        result = {
            'symbol': symbol,
            'name': name,
            'current_price': current_price,
            'trend': trend,
            'fenxing_count': len(fenxing),
            'bi_count': len(bi),
            'zhongshu_count': len(zhongshu),
            'buy_points': buy_points,
            'last_zhongshu': zhongshu[-1] if zhongshu else None
        }

        return result

    def scan_stocks(self, stock_list):
        """扫描股票列表"""
        print("=" * 70)
        print("🔍 AI军事化概念股 30分钟级别 缠论买点扫描")
        print(f"   扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        self.results = []

        for symbol, name in stock_list:
            print(f"\n正在分析: {name}({symbol})...")
            result = self.analyze_stock(symbol, name)

            if result:
                self.results.append(result)

                if result['buy_points']:
                    print(f"  ✅ 发现 {len(result['buy_points'])} 个买点!")
                else:
                    print(f"  ⚪ 暂无明确买点")

        return self.results

    def print_report(self):
        """打印扫描报告"""
        print("\n")
        print("=" * 70)
        print("📊 扫描结果汇总")
        print("=" * 70)

        # 筛选有买点的股票
        stocks_with_buy = [r for r in self.results if r['buy_points']]

        if not stocks_with_buy:
            print("\n⚠️  当前扫描的股票中暂无明确的30分钟级别买点")
            print("\n📋 各股票当前状态:")
            for r in self.results:
                zs_info = ""
                if r['last_zhongshu']:
                    zs = r['last_zhongshu']
                    pos = ""
                    if r['current_price'] > zs['high']:
                        pos = "中枢上方"
                    elif r['current_price'] < zs['low']:
                        pos = "中枢下方"
                    else:
                        pos = "中枢内部"
                    zs_info = f"| 中枢:{zs['low']:.2f}-{zs['high']:.2f} | {pos}"

                print(f"  {r['name']:8s}({r['symbol']}) | 价格:{r['current_price']:8.2f} | {r['trend']:6s} {zs_info}")
        else:
            print(f"\n🎯 发现 {len(stocks_with_buy)} 只股票有买点信号:\n")

            # 按置信度排序
            all_signals = []
            for r in stocks_with_buy:
                for bp in r['buy_points']:
                    all_signals.append({
                        'name': r['name'],
                        'symbol': r['symbol'],
                        'current_price': r['current_price'],
                        'trend': r['trend'],
                        **bp
                    })

            all_signals.sort(key=lambda x: x['confidence'], reverse=True)

            for i, sig in enumerate(all_signals, 1):
                print(f"\n{'='*60}")
                print(f"🏆 推荐 #{i}: {sig['name']}({sig['symbol']})")
                print(f"{'='*60}")
                print(f"   买点类型: {sig['type']}")
                print(f"   买点价格: ¥{sig['price']:.2f}")
                print(f"   当前价格: ¥{sig['current_price']:.2f}")
                print(f"   距离买点: {sig['distance']:+.2f}%")
                print(f"   趋势状态: {sig['trend']}")
                print(f"   置信度:   {sig['confidence']}%")
                print(f"   买点原因: {sig['reason']}")
                print(f"   信号时间: {sig['date']}")

        print("\n" + "=" * 70)
        print("⚠️  风险提示:")
        print("   • 缠论分析仅供参考，需结合大盘环境和基本面")
        print("   • 30分钟级别买点适合短线操作，注意设置止损")
        print("   • 建议结合日线级别趋势确认")
        print("=" * 70)


def main():
    """主函数"""

    # AI军事化概念股列表
    stock_list = [
        # 无人机
        ("688297", "中航无人机"),
        ("002389", "航天彩虹"),
        ("688070", "纵横股份"),

        # 军工电子/AI芯片
        ("002049", "紫光国微"),
        ("000733", "振华科技"),
        ("600562", "国睿科技"),
        ("688002", "睿创微纳"),

        # 精确制导
        ("600435", "北方导航"),
        ("600879", "航天电子"),
        ("600118", "中国卫星"),

        # AI+国防信息化
        ("300496", "中科创达"),
        ("002268", "卫士通"),
        ("002465", "海格通信"),

        # 其他军工
        ("000519", "中兵红箭"),
        ("300123", "亚光科技"),
    ]

    scanner = ChanLun30MinScanner()
    scanner.scan_stocks(stock_list)
    scanner.print_report()


if __name__ == "__main__":
    main()
