#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多级别股票分析器
基于缠中说禅理论的专业技术分析工具

Author: AI量化交易操盘手
Date: 2025-07-16
Version: 1.0
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ChanTheoryAnalyzer:
    """缠论分析器主类"""
    
    def __init__(self):
        """初始化分析器"""
        self.periods = {
            '5': '5分钟',
            '30': '30分钟',
            '60': '60分钟', 
            'daily': '日线'
        }
        
    def get_stock_data(self, symbol, period='daily', limit=200):
        """
        获取股票数据
        
        Args:
            symbol: 股票代码
            period: 时间周期 ('5', '60', 'daily')
            limit: 数据条数限制
            
        Returns:
            DataFrame: 股票K线数据
        """
        try:
            if period == 'daily':
                df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='qfq')
            else:
                df = ak.stock_zh_a_hist_min_em(symbol=symbol, period=period, adjust='qfq')
            
            return df.tail(limit) if len(df) > limit else df
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None
    
    def calculate_indicators(self, df):
        """
        计算技术指标
        
        Args:
            df: K线数据DataFrame
            
        Returns:
            DataFrame: 包含技术指标的数据
        """
        # MACD指标
        exp1 = df['收盘'].ewm(span=12).mean()
        exp2 = df['收盘'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # 均线系统
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        df['MA60'] = df['收盘'].rolling(window=60).mean()
        
        # 成交量均线
        df['vol_ma5'] = df['成交量'].rolling(window=5).mean()
        df['vol_ma10'] = df['成交量'].rolling(window=10).mean()
        df['vol_ma20'] = df['成交量'].rolling(window=20).mean()
        
        # 成交量比率
        df['vol_ratio'] = df['成交量'] / df['vol_ma5']
        
        # 量价关系
        df['price_change'] = df['收盘'].pct_change()
        df['volume_change'] = df['成交量'].pct_change()
        
        return df
    
    def identify_pivot_points(self, df, window=5):
        """
        识别高低点
        
        Args:
            df: K线数据
            window: 识别窗口大小
            
        Returns:
            tuple: (高点列表, 低点列表)
        """
        highs = []
        lows = []
        
        for i in range(window, len(df) - window):
            # 高点识别：比前后window个点都高
            if all(df.iloc[i]['最高'] >= df.iloc[j]['最高'] 
                   for j in range(i-window, i+window+1) if j != i):
                highs.append({
                    'index': i,
                    'price': df.iloc[i]['最高'],
                    'time': df.index[i],
                    'macd': df.iloc[i]['MACD']
                })
            
            # 低点识别：比前后window个点都低
            if all(df.iloc[i]['最低'] <= df.iloc[j]['最低'] 
                   for j in range(i-window, i+window+1) if j != i):
                lows.append({
                    'index': i,
                    'price': df.iloc[i]['最低'],
                    'time': df.index[i],
                    'macd': df.iloc[i]['MACD']
                })
        
        return highs, lows
    
    def analyze_center_structure(self, highs, lows):
        """
        分析中枢结构
        
        Args:
            highs: 高点列表
            lows: 低点列表
            
        Returns:
            dict: 中枢信息或None
        """
        if len(highs) < 2 or len(lows) < 2:
            return None
        
        # 取最近的高低点构建中枢
        recent_highs = [h['price'] for h in highs[-3:]]
        recent_lows = [l['price'] for l in lows[-3:]]
        
        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            center_high = min(recent_highs)  # 中枢上沿取较低的高点
            center_low = max(recent_lows)    # 中枢下沿取较高的低点
            
            if center_high > center_low:
                return {
                    'center_high': center_high,
                    'center_low': center_low,
                    'center_mid': (center_high + center_low) / 2,
                    'center_height': center_high - center_low
                }
        
        return None
    
    def detect_divergence(self, highs, lows, current_price):
        """
        检测背驰信号
        
        Args:
            highs: 高点列表
            lows: 低点列表
            current_price: 当前价格
            
        Returns:
            list: 背驰信号列表
        """
        divergence_signals = []
        
        # 顶背驰检测
        if len(highs) >= 2:
            last_two_highs = highs[-2:]
            if (last_two_highs[1]['price'] > last_two_highs[0]['price'] and 
                last_two_highs[1]['macd'] < last_two_highs[0]['macd']):
                divergence_signals.append('顶背驰')
        
        # 底背驰检测
        if len(lows) >= 2:
            last_two_lows = lows[-2:]
            if (last_two_lows[1]['price'] < last_two_lows[0]['price'] and 
                last_two_lows[1]['macd'] > last_two_lows[0]['macd']):
                divergence_signals.append('底背驰')
        
        return divergence_signals if divergence_signals else ['同步运行']
    
    def generate_trading_signals(self, center, current_price, divergence, trend):
        """
        生成交易信号
        
        Args:
            center: 中枢信息
            current_price: 当前价格
            divergence: 背驰信号
            trend: 趋势状态
            
        Returns:
            list: 交易信号列表
        """
        signals = []
        
        if not center:
            return ['等待中枢形成']
        
        # 判断当前位置
        if current_price > center['center_high']:
            # 中枢上方
            if '同步运行' in divergence:
                signals.append('三买确认')
            elif '顶背驰' in divergence:
                signals.append('一卖警告')
        elif current_price < center['center_low']:
            # 中枢下方
            if '底背驰' in divergence:
                signals.append('一买机会')
            else:
                signals.append('观望等待')
        else:
            # 中枢内部
            signals.append('二买区域')
        
        return signals
    
    def single_level_analysis(self, symbol, period='daily'):
        """
        单级别分析
        
        Args:
            symbol: 股票代码
            period: 时间周期
            
        Returns:
            dict: 分析结果
        """
        # 获取数据
        df = self.get_stock_data(symbol, period)
        if df is None or len(df) < 50:
            return None
        
        # 计算指标
        df = self.calculate_indicators(df)
        
        # 识别高低点
        window = 3 if period == '5' else 5
        highs, lows = self.identify_pivot_points(df, window)
        
        # 分析中枢
        center = self.analyze_center_structure(highs, lows)
        
        # 当前状态
        latest = df.iloc[-1]
        current_price = latest['收盘']
        
        # 趋势判断
        if latest['MA5'] > latest['MA10'] > latest['MA20']:
            trend = '多头排列'
        elif latest['MA5'] < latest['MA10'] < latest['MA20']:
            trend = '空头排列'
        else:
            trend = '震荡整理'
        
        # 背驰检测
        divergence = self.detect_divergence(highs, lows, current_price)
        
        # 交易信号
        signals = self.generate_trading_signals(center, current_price, divergence, trend)
        
        # 成交量分析
        volume_analysis = self.analyze_volume(df)
        
        return {
            'period': self.periods.get(period, period),
            'current_price': current_price,
            'trend': trend,
            'center': center,
            'divergence': divergence,
            'signals': signals,
            'volume_analysis': volume_analysis,
            'highs_count': len(highs),
            'lows_count': len(lows)
        }
    
    def multi_level_analysis(self, symbol, name):
        """
        多级别联立分析
        
        Args:
            symbol: 股票代码
            name: 股票名称
            
        Returns:
            dict: 多级别分析结果
        """
        print(f"=== {name} ({symbol}) 缠论多级别分析 ===\n")
        
        results = {}
        periods = ['5', '30', '60', 'daily']
        
        # 各级别分析
        for period in periods:
            result = self.single_level_analysis(symbol, period)
            if result:
                results[period] = result
                self.print_single_level_result(result)
        
        # 多级别综合分析
        if len(results) >= 2:
            self.multi_level_synthesis(results)
        
        return results
    
    def print_single_level_result(self, result):
        """
        打印单级别分析结果
        
        Args:
            result: 单级别分析结果
        """
        print(f"📊 {result['period']}级别分析")
        print("-" * 40)
        print(f"   💰 当前价格: {result['current_price']:.2f}元")
        print(f"   📈 趋势状态: {result['trend']}")
        
        if result['center']:
            center = result['center']
            print(f"   🎯 中枢区间: {center['center_low']:.2f}-{center['center_high']:.2f}元")
            
            # 判断位置
            if result['current_price'] > center['center_high']:
                position = '中枢上方'
            elif result['current_price'] < center['center_low']:
                position = '中枢下方'
            else:
                position = '中枢内部'
            print(f"   📍 中枢位置: {position}")
        else:
            print(f"   🎯 中枢区间: 未识别")
        
        print(f"   ⚠️  背驰状态: {' | '.join(result['divergence'])}")
        print(f"   💡 交易信号: {' | '.join(result['signals'])}")
        
        # 成交量信息
        if result.get('volume_analysis'):
            vol = result['volume_analysis']
            print(f"   📊 成交量: {vol['current_volume']:.0f}手 (量比{vol['vol_ratio']:.2f})")
            print(f"   📈 量价关系: {vol['vol_price_relation']} | {vol['vol_trend']}")
            print(f"   ⭐ 量能评分: {vol['vol_score']}/5")
        
        print(f"   🔢 高低点数: 高点{result['highs_count']}个, 低点{result['lows_count']}个")
        print()
    
    def multi_level_synthesis(self, results):
        """
        多级别综合分析
        
        Args:
            results: 各级别分析结果
        """
        print("🔄 多级别联立分析")
        print("=" * 50)
        
        # 趋势一致性分析
        trends = [r['trend'] for r in results.values()]
        signals = [r['signals'][0] if r['signals'] else '观望' for r in results.values()]
        
        print("📈 各级别趋势状态:")
        for period, result in results.items():
            period_name = self.periods.get(period, period)
            print(f"   • {period_name}: {result['trend']}")
        
        print("\n💡 各级别交易信号:")
        for period, result in results.items():
            period_name = self.periods.get(period, period)
            print(f"   • {period_name}: {' | '.join(result['signals'])}")
        
        # 综合建议
        print("\n🎯 综合操作建议:")
        
        # 多级别共振判断
        bullish_count = sum(1 for t in trends if '多头' in t)
        bearish_count = sum(1 for t in trends if '空头' in t)
        
        buy_signals = sum(1 for s in signals if '买' in s)
        sell_signals = sum(1 for s in signals if '卖' in s)
        
        if bullish_count > bearish_count and buy_signals > 0:
            if '三买' in ' '.join(signals):
                suggestion = "✅ 多级别上涨趋势+三买信号，积极买入"
            elif '二买' in ' '.join(signals):
                suggestion = "🟡 多级别上涨趋势+二买信号，适量买入"
            else:
                suggestion = "🟢 多级别上涨趋势，可考虑买入"
        elif bearish_count > bullish_count or sell_signals > 0:
            suggestion = "🔴 趋势偏弱或有卖出信号，建议观望或减仓"
        else:
            suggestion = "🟡 级别间分歧，建议观望等待明确信号"
        
        print(f"   {suggestion}")
        
        # 关键价位
        centers = []
        for result in results.values():
            if result['center']:
                centers.append(f"{result['center']['center_low']:.2f}-{result['center']['center_high']:.2f}")
        
        if centers:
            print(f"\n🎯 关键中枢区间: {' | '.join(centers)}")
    
    def analyze_volume(self, df):
        """
        分析成交量特征
        
        Args:
            df: K线数据DataFrame
            
        Returns:
            dict: 成交量分析结果
        """
        if df is None or len(df) < 20:
            return None
            
        current_vol = df['成交量'].iloc[-1]
        vol_ma5 = df['vol_ma5'].iloc[-1]
        vol_ma10 = df['vol_ma10'].iloc[-1]
        vol_ma20 = df['vol_ma20'].iloc[-1]
        vol_ratio = df['vol_ratio'].iloc[-1]
        
        # 成交量趋势
        vol_trend = "放量" if vol_ratio > 1.5 else "缩量" if vol_ratio < 0.8 else "正常"
        
        # 量价关系
        price_change = df['price_change'].iloc[-1]
        volume_change = df['volume_change'].iloc[-1]
        
        if price_change > 0 and volume_change > 0:
            vol_price_relation = "量价齐升"
        elif price_change > 0 and volume_change < 0:
            vol_price_relation = "价升量缩"
        elif price_change < 0 and volume_change > 0:
            vol_price_relation = "价跌量增"
        elif price_change < 0 and volume_change < 0:
            vol_price_relation = "量价齐跌"
        else:
            vol_price_relation = "量价平衡"
        
        # 成交量评分
        vol_score = 0
        if vol_ratio > 2.0:
            vol_score = 5  # 大幅放量
        elif vol_ratio > 1.5:
            vol_score = 4  # 明显放量
        elif vol_ratio > 1.2:
            vol_score = 3  # 温和放量
        elif vol_ratio > 0.8:
            vol_score = 2  # 正常成交
        else:
            vol_score = 1  # 缩量
        
        return {
            'current_volume': current_vol,
            'vol_ma5': vol_ma5,
            'vol_ma10': vol_ma10,
            'vol_ma20': vol_ma20,
            'vol_ratio': vol_ratio,
            'vol_trend': vol_trend,
            'vol_price_relation': vol_price_relation,
            'vol_score': vol_score
        }
    
    def batch_analysis(self, stock_list):
        """
        批量分析多只股票
        
        Args:
            stock_list: 股票列表 [(代码, 名称), ...]
            
        Returns:
            dict: 批量分析结果
        """
        batch_results = {}
        
        for symbol, name in stock_list:
            print(f"\n{'='*60}")
            try:
                result = self.multi_level_analysis(symbol, name)
                batch_results[symbol] = result
            except Exception as e:
                print(f"分析 {name}({symbol}) 失败: {e}")
                continue
        
        return batch_results
    
    def real_time_monitor(self, symbol, name=None, interval=300):
        """
        实时监控模式
        
        Args:
            symbol: 股票代码
            name: 股票名称
            interval: 更新间隔(秒)
        """
        if not name:
            name = symbol
            
        print(f"开始实时监控 {name}({symbol})，更新间隔: {interval}秒")
        print("按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.multi_level_analysis(symbol, name)
                
                import time
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n监控已停止")


def main():
    """主函数 - 使用示例"""
    analyzer = ChanTheoryAnalyzer()
    
    # 单股票分析示例
    print("=== 缠论分析示例 ===\n")
    
    # 分析哈三联
    result = analyzer.multi_level_analysis('002900', '哈三联')
    
    # 批量分析示例
    # stocks = [
    #     ('002900', '哈三联'),
    #     ('000001', '平安银行'),
    #     ('600036', '招商银行')
    # ]
    # batch_results = analyzer.batch_analysis(stocks)
    
    # 实时监控示例（取消注释使用）
    # analyzer.real_time_monitor('002900', '哈三联', interval=300)


if __name__ == "__main__":
    main()
