#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI军事化概念股 30分钟级别 缠论买点扫描 (baostock数据源)
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ChanLun30MinScanner:
    """30分钟级别缠论扫描器"""

    def __init__(self):
        self.results = []
        # 登录baostock
        self.lg = bs.login()
        print(f"Baostock登录: {self.lg.error_msg}")

    def __del__(self):
        bs.logout()

    def fetch_30min_data(self, symbol, name):
        """获取30分钟K线数据"""
        try:
            # 构造baostock格式的代码
            if symbol.startswith('6'):
                bs_code = f'sh.{symbol}'
            else:
                bs_code = f'sz.{symbol}'

            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            rs = bs.query_history_k_data_plus(
                bs_code,
                'date,time,code,open,high,low,close,volume',
                start_date=start_date,
                end_date=end_date,
                frequency='30',
                adjustflag='2'  # 前复权
            )

            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return None

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'].str[:8].str[:2] + ':' +
                                           df['time'].str[:8].str[2:4] + ':' + df['time'].str[:8].str[4:6])
            df.set_index('datetime', inplace=True)

            # 重命名列
            df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low',
                                   'close': 'Close', 'volume': 'Volume'})

            return df[['Open', 'High', 'Low', 'Close', 'Volume']]

        except Exception as e:
            print(f"  获取 {name}({symbol}) 数据失败: {e}")
            return None

    def find_fenxing(self, data):
        """识别分型（包含关系处理）"""
        if len(data) < 5:
            return []

        # 先处理包含关系
        processed = self._process_inclusion(data)

        fenxing = []

        for i in range(1, len(processed) - 1):
            current = processed.iloc[i]
            prev = processed.iloc[i-1]
            next_bar = processed.iloc[i+1]

            # 顶分型：中间K线高点最高
            if (current['High'] > prev['High'] and current['High'] > next_bar['High'] and
                current['Low'] >= prev['Low'] and current['Low'] >= next_bar['Low']):
                fenxing.append({
                    'index': i,
                    'date': processed.index[i],
                    'type': 'top',
                    'price': current['High'],
                    'high': current['High'],
                    'low': current['Low']
                })

            # 底分型：中间K线低点最低
            elif (current['Low'] < prev['Low'] and current['Low'] < next_bar['Low'] and
                  current['High'] <= prev['High'] and current['High'] <= next_bar['High']):
                fenxing.append({
                    'index': i,
                    'date': processed.index[i],
                    'type': 'bottom',
                    'price': current['Low'],
                    'high': current['High'],
                    'low': current['Low']
                })

        return fenxing

    def _process_inclusion(self, data):
        """处理K线包含关系"""
        result = data.copy()
        # 简化处理，不做复杂的包含关系合并
        return result

    def find_bi(self, fenxing):
        """识别笔"""
        bi = []

        if len(fenxing) < 2:
            return bi

        current_fx = fenxing[0]

        for fx in fenxing[1:]:
            if fx['type'] != current_fx['type']:
                # 笔至少跨越4根K线
                if abs(fx['index'] - current_fx['index']) >= 4:
                    bi.append({
                        'start': current_fx,
                        'end': fx,
                        'direction': 'up' if current_fx['type'] == 'bottom' else 'down',
                        'strength': abs(fx['price'] - current_fx['price']),
                        'bars': abs(fx['index'] - current_fx['index'])
                    })
                    current_fx = fx
            else:
                # 同类型分型，取更极端的
                if fx['type'] == 'top' and fx['price'] > current_fx['price']:
                    current_fx = fx
                elif fx['type'] == 'bottom' and fx['price'] < current_fx['price']:
                    current_fx = fx

        return bi

    def find_zhongshu(self, bi):
        """识别中枢"""
        zhongshu = []

        if len(bi) < 3:
            return zhongshu

        i = 0
        while i <= len(bi) - 3:
            bi1 = bi[i]
            bi2 = bi[i + 1]
            bi3 = bi[i + 2]

            # 计算三笔的重叠区间
            ranges = []
            for b in [bi1, bi2, bi3]:
                ranges.append((min(b['start']['price'], b['end']['price']),
                              max(b['start']['price'], b['end']['price'])))

            max_low = max(r[0] for r in ranges)
            min_high = min(r[1] for r in ranges)

            if max_low < min_high:
                # 形成中枢，尝试延伸
                zs_bi_count = 3
                zs_end = bi3

                # 检查后续笔是否继续在中枢范围内
                for j in range(i + 3, len(bi)):
                    b = bi[j]
                    b_low = min(b['start']['price'], b['end']['price'])
                    b_high = max(b['start']['price'], b['end']['price'])

                    if b_low < min_high and b_high > max_low:
                        zs_bi_count += 1
                        zs_end = b
                    else:
                        break

                zhongshu.append({
                    'start_date': bi1['start']['date'],
                    'end_date': zs_end['end']['date'],
                    'high': min_high,
                    'low': max_low,
                    'center': (max_low + min_high) / 2,
                    'height': min_high - max_low,
                    'bi_count': zs_bi_count
                })

                i += zs_bi_count
            else:
                i += 1

        return zhongshu

    def analyze_buy_point(self, data, fenxing, bi, zhongshu):
        """分析买点"""
        if not bi or len(bi) < 2:
            return None, "笔数不足"

        current_price = data['Close'].iloc[-1]
        last_bi = bi[-1]
        last_fx = fenxing[-1] if fenxing else None

        result = {
            'has_buy_point': False,
            'buy_type': None,
            'buy_price': None,
            'current_price': current_price,
            'reason': '',
            'confidence': 0,
            'zhongshu': None
        }

        # 获取最近的中枢
        if zhongshu:
            last_zs = zhongshu[-1]
            result['zhongshu'] = last_zs

            # 判断当前位置
            if current_price > last_zs['high']:
                position = "中枢上方"
            elif current_price < last_zs['low']:
                position = "中枢下方"
            else:
                position = "中枢内部"

            # 一类买点：最后一笔是下跌笔，且创新低后形成底分型
            if last_bi['direction'] == 'down' and last_fx and last_fx['type'] == 'bottom':
                # 检查是否背驰
                same_dir_bi = [b for b in bi[:-1] if b['direction'] == 'down']
                if same_dir_bi:
                    prev_down = same_dir_bi[-1]
                    if last_bi['strength'] < prev_down['strength'] * 0.9:
                        # 力度背驰
                        if last_fx['price'] < last_zs['low']:
                            result['has_buy_point'] = True
                            result['buy_type'] = '一类买点'
                            result['buy_price'] = last_fx['price']
                            result['reason'] = f"30分钟下跌背驰，底分型确认。中枢区间:{last_zs['low']:.2f}-{last_zs['high']:.2f}"
                            result['confidence'] = 85

            # 二类买点：回调不破中枢下沿
            if not result['has_buy_point'] and last_fx and last_fx['type'] == 'bottom':
                if last_zs['low'] * 0.99 <= last_fx['price'] <= last_zs['center']:
                    if last_fx['date'] > last_zs['end_date']:
                        result['has_buy_point'] = True
                        result['buy_type'] = '二类买点'
                        result['buy_price'] = last_fx['price']
                        result['reason'] = f"30分钟回调不破中枢下沿。{position}"
                        result['confidence'] = 75

            # 三类买点：突破中枢后回踩
            if not result['has_buy_point'] and current_price > last_zs['high']:
                if last_fx and last_fx['type'] == 'bottom':
                    if last_fx['price'] >= last_zs['high'] * 0.97:
                        result['has_buy_point'] = True
                        result['buy_type'] = '三类买点'
                        result['buy_price'] = last_fx['price']
                        result['reason'] = f"30分钟突破中枢后回踩确认。中枢上沿:{last_zs['high']:.2f}"
                        result['confidence'] = 70

        if not result['has_buy_point']:
            # 判断当前走势状态
            if last_bi['direction'] == 'up':
                result['reason'] = f"当前处于上涨笔中，等待回调"
            else:
                result['reason'] = f"当前处于下跌笔中，关注底分型形成"

        return result, None

    def analyze_stock(self, symbol, name):
        """分析单只股票"""
        data = self.fetch_30min_data(symbol, name)

        if data is None or len(data) < 30:
            return None

        fenxing = self.find_fenxing(data)
        bi = self.find_bi(fenxing)
        zhongshu = self.find_zhongshu(bi)

        result, error = self.analyze_buy_point(data, fenxing, bi, zhongshu)

        if error:
            return None

        # 计算技术指标
        data['MA5'] = data['Close'].rolling(5).mean()
        data['MA20'] = data['Close'].rolling(20).mean()

        ma5 = data['MA5'].iloc[-1]
        ma20 = data['MA20'].iloc[-1]
        trend = "多头排列" if ma5 > ma20 else "空头排列"

        return {
            'symbol': symbol,
            'name': name,
            'current_price': result['current_price'],
            'trend': trend,
            'fenxing_count': len(fenxing),
            'bi_count': len(bi),
            'zhongshu_count': len(zhongshu),
            'has_buy_point': result['has_buy_point'],
            'buy_type': result['buy_type'],
            'buy_price': result['buy_price'],
            'confidence': result['confidence'],
            'reason': result['reason'],
            'zhongshu': result['zhongshu']
        }

    def scan_stocks(self, stock_list):
        """扫描股票列表"""
        print("\n" + "=" * 70)
        print("🔍 AI军事化概念股 30分钟级别 缠论买点扫描")
        print(f"   扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        self.results = []

        for symbol, name in stock_list:
            print(f"\n正在分析: {name}({symbol})...", end=" ")
            result = self.analyze_stock(symbol, name)

            if result:
                self.results.append(result)
                if result['has_buy_point']:
                    print(f"✅ {result['buy_type']}!")
                else:
                    print(f"⚪ {result['reason'][:30]}...")
            else:
                print("❌ 数据不足")

        return self.results

    def print_report(self):
        """打印扫描报告"""
        print("\n\n" + "=" * 70)
        print("📊 扫描结果汇总")
        print("=" * 70)

        # 有买点的股票
        buy_signals = [r for r in self.results if r['has_buy_point']]

        if buy_signals:
            # 按置信度排序
            buy_signals.sort(key=lambda x: x['confidence'], reverse=True)

            print(f"\n🎯 发现 {len(buy_signals)} 个买点信号:\n")

            for i, sig in enumerate(buy_signals, 1):
                print(f"\n{'='*60}")
                print(f"🏆 推荐 #{i}: {sig['name']}({sig['symbol']})")
                print(f"{'='*60}")
                print(f"   买点类型: {sig['buy_type']}")
                print(f"   买点价格: ¥{sig['buy_price']:.2f}")
                print(f"   当前价格: ¥{sig['current_price']:.2f}")
                distance = (sig['current_price'] - sig['buy_price']) / sig['buy_price'] * 100
                print(f"   距离买点: {distance:+.2f}%")
                print(f"   趋势状态: {sig['trend']}")
                print(f"   置信度:   {sig['confidence']}%")
                print(f"   分析依据: {sig['reason']}")
                if sig['zhongshu']:
                    zs = sig['zhongshu']
                    print(f"   中枢区间: ¥{zs['low']:.2f} - ¥{zs['high']:.2f} (含{zs['bi_count']}笔)")
        else:
            print("\n⚠️  当前扫描的股票中暂无明确的30分钟级别买点")

        # 所有股票状态
        print("\n\n📋 全部股票状态:")
        print("-" * 70)
        print(f"{'股票名称':10s} {'代码':8s} {'价格':>10s} {'趋势':8s} {'笔数':>6s} {'中枢':>6s} {'状态'}")
        print("-" * 70)

        for r in self.results:
            status = f"✅{r['buy_type']}" if r['has_buy_point'] else r['reason'][:20]
            print(f"{r['name']:10s} {r['symbol']:8s} {r['current_price']:>10.2f} {r['trend']:8s} "
                  f"{r['bi_count']:>6d} {r['zhongshu_count']:>6d} {status}")

        print("-" * 70)
        print(f"\n⚠️  风险提示:")
        print("   • 缠论分析仅供参考，需结合大盘环境和基本面")
        print("   • 30分钟级别买点适合短线操作，注意设置止损")
        print("   • 建议结合日线级别趋势确认，避免逆势操作")
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
