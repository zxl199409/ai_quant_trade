#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晨曦航空股票分析
基于AI量化交易工程的分析逻辑
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class StockAnalyzer:
    """股票分析器 - 基于量化工程逻辑"""
    
    def __init__(self, symbol, name="股票"):
        self.symbol = symbol
        self.name = name
        self.data = None
        
    def fetch_data(self, period="2y"):
        """获取股票数据"""
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(period=period)
            print(f"✅ 成功获取 {self.name} 数据，共 {len(self.data)} 条记录")
            return True
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return False
    
    def calculate_technical_indicators(self):
        """计算技术指标 - 基于工程中的因子库逻辑"""
        if self.data is None:
            print("❌ 请先获取数据")
            return
        
        df = self.data.copy()
        
        # 移动平均线
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        # RSI相对强弱指标
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD指标
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 布林带
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # 成交量指标
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # 价格变化率
        df['Price_Change'] = df['Close'].pct_change()
        df['Price_Change_5d'] = df['Close'].pct_change(5)
        df['Price_Change_20d'] = df['Close'].pct_change(20)
        
        self.data = df
        print("✅ 技术指标计算完成")
    
    def analyze_trend(self):
        """趋势分析 - 基于双均线策略逻辑"""
        if self.data is None:
            return
        
        latest = self.data.iloc[-1]
        prev_5 = self.data.iloc[-6:-1]
        
        print(f"\n📊 {self.name} 趋势分析")
        print("=" * 50)
        
        # 价格趋势
        current_price = latest['Close']
        ma5 = latest['MA5']
        ma20 = latest['MA20']
        ma60 = latest['MA60']
        
        print(f"当前价格: ${current_price:.2f}")
        print(f"MA5: ${ma5:.2f}")
        print(f"MA20: ${ma20:.2f}")
        print(f"MA60: ${ma60:.2f}")
        
        # 趋势判断
        if current_price > ma5 > ma20 > ma60:
            trend = "🟢 强势上涨趋势"
        elif current_price > ma5 > ma20:
            trend = "🟡 温和上涨趋势"
        elif current_price < ma5 < ma20 < ma60:
            trend = "🔴 强势下跌趋势"
        elif current_price < ma5 < ma20:
            trend = "🟠 温和下跌趋势"
        else:
            trend = "⚪ 震荡整理"
        
        print(f"趋势判断: {trend}")
        
        # RSI分析
        rsi = latest['RSI']
        if rsi > 70:
            rsi_signal = "🔴 超买区域，注意回调风险"
        elif rsi < 30:
            rsi_signal = "🟢 超卖区域，可能反弹"
        else:
            rsi_signal = "⚪ 正常区域"
        
        print(f"RSI({rsi:.1f}): {rsi_signal}")
        
        # MACD分析
        macd = latest['MACD']
        macd_signal = latest['MACD_Signal']
        if macd > macd_signal and macd > 0:
            macd_trend = "🟢 多头趋势"
        elif macd < macd_signal and macd < 0:
            macd_trend = "🔴 空头趋势"
        else:
            macd_trend = "⚪ 趋势不明"
        
        print(f"MACD: {macd_trend}")
        
        return {
            'trend': trend,
            'rsi_signal': rsi_signal,
            'macd_trend': macd_trend,
            'current_price': current_price
        }
    
    def risk_analysis(self):
        """风险分析"""
        if self.data is None:
            return
        
        print(f"\n⚠️  {self.name} 风险分析")
        print("=" * 50)
        
        # 波动率分析
        returns = self.data['Price_Change'].dropna()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        print(f"年化波动率: {volatility:.2%}")
        
        if volatility > 0.4:
            vol_risk = "🔴 高风险 - 波动率较大"
        elif volatility > 0.25:
            vol_risk = "🟡 中等风险"
        else:
            vol_risk = "🟢 低风险"
        
        print(f"波动率风险: {vol_risk}")
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        print(f"最大回撤: {max_drawdown:.2%}")
        
        # 成交量分析
        latest_volume_ratio = self.data['Volume_Ratio'].iloc[-1]
        if latest_volume_ratio > 2:
            volume_signal = "🟢 成交量放大，关注度高"
        elif latest_volume_ratio < 0.5:
            volume_signal = "🔴 成交量萎缩，流动性不足"
        else:
            volume_signal = "⚪ 成交量正常"
        
        print(f"成交量状况: {volume_signal}")
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'volume_signal': volume_signal
        }
    
    def generate_signals(self):
        """生成交易信号 - 基于多因子模型"""
        if self.data is None:
            return
        
        print(f"\n📈 {self.name} 交易信号")
        print("=" * 50)
        
        latest = self.data.iloc[-1]
        signals = []
        score = 0
        
        # 趋势信号
        if latest['Close'] > latest['MA5'] > latest['MA20']:
            signals.append("🟢 均线多头排列")
            score += 2
        elif latest['Close'] < latest['MA5'] < latest['MA20']:
            signals.append("🔴 均线空头排列")
            score -= 2
        
        # RSI信号
        if 30 < latest['RSI'] < 70:
            signals.append("🟢 RSI处于健康区间")
            score += 1
        elif latest['RSI'] > 70:
            signals.append("🔴 RSI超买")
            score -= 1
        elif latest['RSI'] < 30:
            signals.append("🟡 RSI超卖，可能反弹")
            score += 1
        
        # MACD信号
        if latest['MACD'] > latest['MACD_Signal']:
            signals.append("🟢 MACD金叉")
            score += 1
        else:
            signals.append("🔴 MACD死叉")
            score -= 1
        
        # 布林带信号
        if latest['Close'] > latest['BB_Upper']:
            signals.append("🔴 价格突破布林带上轨")
            score -= 1
        elif latest['Close'] < latest['BB_Lower']:
            signals.append("🟢 价格跌破布林带下轨，可能反弹")
            score += 1
        
        # 成交量信号
        if latest['Volume_Ratio'] > 1.5:
            signals.append("🟢 成交量放大")
            score += 1
        
        # 综合评分
        if score >= 3:
            recommendation = "🟢 建议买入"
        elif score >= 1:
            recommendation = "🟡 谨慎看多"
        elif score <= -3:
            recommendation = "🔴 建议卖出"
        elif score <= -1:
            recommendation = "🟠 谨慎看空"
        else:
            recommendation = "⚪ 观望"
        
        print("技术信号:")
        for signal in signals:
            print(f"  {signal}")
        
        print(f"\n综合评分: {score}")
        print(f"操作建议: {recommendation}")
        
        return {
            'signals': signals,
            'score': score,
            'recommendation': recommendation
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        if self.data is None:
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # 价格和均线图
        ax1 = axes[0]
        ax1.plot(self.data.index, self.data['Close'], label='收盘价', linewidth=2)
        ax1.plot(self.data.index, self.data['MA5'], label='MA5', alpha=0.7)
        ax1.plot(self.data.index, self.data['MA20'], label='MA20', alpha=0.7)
        ax1.plot(self.data.index, self.data['MA60'], label='MA60', alpha=0.7)
        ax1.fill_between(self.data.index, self.data['BB_Upper'], self.data['BB_Lower'], 
                        alpha=0.1, color='gray', label='布林带')
        ax1.set_title(f'{self.name} - 价格走势与技术指标')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # RSI图
        ax2 = axes[1]
        ax2.plot(self.data.index, self.data['RSI'], label='RSI', color='purple')
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线')
        ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线')
        ax2.set_title('RSI相对强弱指标')
        ax2.set_ylim(0, 100)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # MACD图
        ax3 = axes[2]
        ax3.plot(self.data.index, self.data['MACD'], label='MACD', color='blue')
        ax3.plot(self.data.index, self.data['MACD_Signal'], label='Signal', color='red')
        ax3.bar(self.data.index, self.data['MACD_Hist'], label='Histogram', alpha=0.3)
        ax3.set_title('MACD指标')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def main():
    """主函数 - 分析晨曦航空"""
    print("🚀 AI量化交易 - 晨曦航空分析")
    print("=" * 60)
    
    # 注意：这里需要晨曦航空的正确股票代码
    # 由于我不确定具体的股票代码，这里使用示例代码
    # 请替换为正确的股票代码，例如：
    # - 如果是A股：需要添加.SS或.SZ后缀
    # - 如果是港股：需要添加.HK后缀
    # - 如果是美股：直接使用股票代码
    
    # 示例：假设晨曦航空的代码（请替换为实际代码）
    stock_symbol = "CHENXI"  # 请替换为实际股票代码
    
    # 创建分析器
    analyzer = StockAnalyzer(stock_symbol, "晨曦航空")
    
    # 获取数据
    if not analyzer.fetch_data():
        print("❌ 无法获取股票数据，请检查股票代码是否正确")
        print("💡 提示：请将代码中的 'CHENXI' 替换为晨曦航空的实际股票代码")
        return
    
    # 计算技术指标
    analyzer.calculate_technical_indicators()
    
    # 进行分析
    trend_analysis = analyzer.analyze_trend()
    risk_analysis = analyzer.risk_analysis()
    signals = analyzer.generate_signals()
    
    # 生成报告
    print(f"\n📋 {analyzer.name} 综合分析报告")
    print("=" * 60)
    print("本分析基于AI量化交易工程的多因子模型")
    print("包含技术分析、风险评估和交易信号生成")
    print("\n⚠️  免责声明：本分析仅供参考，不构成投资建议")
    
    # 绘制图表
    try:
        analyzer.plot_analysis()
    except Exception as e:
        print(f"⚠️  图表绘制失败: {e}")

if __name__ == "__main__":
    main()
