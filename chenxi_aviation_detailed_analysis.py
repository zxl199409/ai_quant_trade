#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晨曦航空(300581)专项分析
基于AI量化交易工程的深度分析
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChenxiAviationAnalyzer:
    """晨曦航空专项分析器"""
    
    def __init__(self):
        self.stock_code = "300581"
        self.stock_name = "晨曦航空"
        self.data = None
        self.company_info = None
        
    def fetch_basic_info(self):
        """获取基本信息"""
        try:
            print(f"📊 获取{self.stock_name}基本信息...")
            
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=self.stock_code)
            
            print(f"✅ 股票代码: {self.stock_code}")
            print(f"✅ 股票名称: {self.stock_name}")
            
            if not stock_info.empty:
                for idx, row in stock_info.iterrows():
                    print(f"   {row['item']}: {row['value']}")
            
            return True
        except Exception as e:
            print(f"❌ 基本信息获取失败: {e}")
            return False
    
    def fetch_price_data(self, period="daily", start_date="20220101"):
        """获取价格数据"""
        try:
            print(f"📈 获取{self.stock_name}价格数据...")
            
            # 获取历史数据
            self.data = ak.stock_zh_a_hist(
                symbol=self.stock_code, 
                period=period, 
                start_date=start_date,
                adjust="qfq"  # 前复权
            )
            
            if self.data is not None and not self.data.empty:
                # 重命名列名以符合标准格式
                self.data.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_Pct', 'Change_Amount', 'Turnover']
                self.data['Date'] = pd.to_datetime(self.data['Date'])
                self.data.set_index('Date', inplace=True)
                
                print(f"✅ 成功获取数据，共 {len(self.data)} 条记录")
                print(f"   数据时间范围: {self.data.index[0].date()} 到 {self.data.index[-1].date()}")
                return True
            else:
                print("❌ 未获取到价格数据")
                return False
                
        except Exception as e:
            print(f"❌ 价格数据获取失败: {e}")
            return False
    
    def calculate_technical_indicators(self):
        """计算技术指标"""
        if self.data is None or self.data.empty:
            print("❌ 请先获取价格数据")
            return
        
        print("🔧 计算技术指标...")
        
        # 移动平均线
        self.data['MA5'] = self.data['Close'].rolling(window=5).mean()
        self.data['MA10'] = self.data['Close'].rolling(window=10).mean()
        self.data['MA20'] = self.data['Close'].rolling(window=20).mean()
        self.data['MA60'] = self.data['Close'].rolling(window=60).mean()
        
        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = self.data['Close'].ewm(span=12).mean()
        exp2 = self.data['Close'].ewm(span=26).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['MACD_Signal'] = self.data['MACD'].ewm(span=9).mean()
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['MACD_Signal']
        
        # 布林带
        self.data['BB_Middle'] = self.data['Close'].rolling(window=20).mean()
        bb_std = self.data['Close'].rolling(window=20).std()
        self.data['BB_Upper'] = self.data['BB_Middle'] + (bb_std * 2)
        self.data['BB_Lower'] = self.data['BB_Middle'] - (bb_std * 2)
        
        # 成交量指标
        self.data['Volume_MA'] = self.data['Volume'].rolling(window=20).mean()
        self.data['Volume_Ratio'] = self.data['Volume'] / self.data['Volume_MA']
        
        print("✅ 技术指标计算完成")
    
    def analyze_current_status(self):
        """分析当前状态"""
        if self.data is None or self.data.empty:
            return
        
        latest = self.data.iloc[-1]
        prev_day = self.data.iloc[-2] if len(self.data) > 1 else latest
        
        print(f"\n📊 {self.stock_name} 最新状态分析")
        print("=" * 60)
        
        # 基本价格信息
        print(f"最新价格: ¥{latest['Close']:.2f}")
        print(f"涨跌幅: {latest['Change_Pct']:.2f}%")
        print(f"涨跌额: ¥{latest['Change_Amount']:.2f}")
        print(f"成交量: {latest['Volume']:,.0f}手")
        print(f"成交额: ¥{latest['Amount']:,.0f}万")
        print(f"换手率: {latest['Turnover']:.2f}%")
        
        # 技术指标状态
        print(f"\n📈 技术指标状态:")
        print(f"MA5: ¥{latest['MA5']:.2f}")
        print(f"MA20: ¥{latest['MA20']:.2f}")
        print(f"MA60: ¥{latest['MA60']:.2f}")
        print(f"RSI: {latest['RSI']:.1f}")
        print(f"MACD: {latest['MACD']:.4f}")
        
        # 趋势判断
        self._analyze_trend(latest)
        
        return latest
    
    def _analyze_trend(self, latest):
        """趋势分析"""
        print(f"\n🎯 趋势分析:")
        
        # 均线趋势
        if latest['Close'] > latest['MA5'] > latest['MA20'] > latest['MA60']:
            trend = "🟢 强势多头趋势"
        elif latest['Close'] > latest['MA5'] > latest['MA20']:
            trend = "🟡 温和多头趋势"
        elif latest['Close'] < latest['MA5'] < latest['MA20'] < latest['MA60']:
            trend = "🔴 强势空头趋势"
        elif latest['Close'] < latest['MA5'] < latest['MA20']:
            trend = "🟠 温和空头趋势"
        else:
            trend = "⚪ 震荡整理"
        
        print(f"均线趋势: {trend}")
        
        # RSI分析
        rsi = latest['RSI']
        if rsi > 80:
            rsi_signal = "🔴 严重超买"
        elif rsi > 70:
            rsi_signal = "🟠 超买"
        elif rsi < 20:
            rsi_signal = "🟢 严重超卖"
        elif rsi < 30:
            rsi_signal = "🟡 超卖"
        else:
            rsi_signal = "⚪ 正常区间"
        
        print(f"RSI状态: {rsi_signal}")
        
        # MACD分析
        if latest['MACD'] > latest['MACD_Signal'] and latest['MACD'] > 0:
            macd_signal = "🟢 强势多头"
        elif latest['MACD'] > latest['MACD_Signal']:
            macd_signal = "🟡 弱势多头"
        elif latest['MACD'] < latest['MACD_Signal'] and latest['MACD'] < 0:
            macd_signal = "🔴 强势空头"
        else:
            macd_signal = "🟠 弱势空头"
        
        print(f"MACD信号: {macd_signal}")
    
    def risk_assessment(self):
        """风险评估"""
        if self.data is None or self.data.empty:
            return
        
        print(f"\n⚠️  {self.stock_name} 风险评估")
        print("=" * 60)
        
        # 计算收益率
        returns = self.data['Close'].pct_change().dropna()
        
        # 波动率
        volatility_daily = returns.std()
        volatility_annual = volatility_daily * np.sqrt(252)
        
        print(f"日波动率: {volatility_daily:.4f}")
        print(f"年化波动率: {volatility_annual:.2%}")
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        print(f"最大回撤: {max_drawdown:.2%}")
        
        # 风险等级评估
        if volatility_annual > 0.5:
            risk_level = "🔴 高风险"
        elif volatility_annual > 0.3:
            risk_level = "🟡 中等风险"
        else:
            risk_level = "🟢 低风险"
        
        print(f"风险等级: {risk_level}")
        
        # 近期表现
        recent_30d = returns.tail(30)
        recent_return = recent_30d.mean() * 30
        print(f"近30日平均收益: {recent_return:.2%}")
        
        return {
            'volatility_annual': volatility_annual,
            'max_drawdown': max_drawdown,
            'risk_level': risk_level,
            'recent_return': recent_return
        }
    
    def generate_investment_advice(self):
        """生成投资建议"""
        if self.data is None or self.data.empty:
            return
        
        print(f"\n💡 {self.stock_name} 投资建议")
        print("=" * 60)
        
        latest = self.data.iloc[-1]
        score = 0
        reasons = []
        
        # 技术面评分
        if latest['Close'] > latest['MA20']:
            score += 2
            reasons.append("✅ 价格位于20日均线之上")
        else:
            score -= 2
            reasons.append("❌ 价格位于20日均线之下")
        
        if latest['RSI'] < 70 and latest['RSI'] > 30:
            score += 1
            reasons.append("✅ RSI处于合理区间")
        elif latest['RSI'] > 70:
            score -= 2
            reasons.append("❌ RSI超买")
        elif latest['RSI'] < 30:
            score += 1
            reasons.append("✅ RSI超卖，可能反弹")
        
        if latest['MACD'] > latest['MACD_Signal']:
            score += 1
            reasons.append("✅ MACD金叉")
        else:
            score -= 1
            reasons.append("❌ MACD死叉")
        
        if latest['Volume_Ratio'] > 1.2:
            score += 1
            reasons.append("✅ 成交量放大")
        elif latest['Volume_Ratio'] < 0.8:
            score -= 1
            reasons.append("❌ 成交量萎缩")
        
        # 生成建议
        if score >= 3:
            advice = "🟢 建议买入"
            confidence = "高"
        elif score >= 1:
            advice = "🟡 谨慎看多"
            confidence = "中"
        elif score <= -3:
            advice = "🔴 建议卖出"
            confidence = "高"
        elif score <= -1:
            advice = "🟠 谨慎看空"
            confidence = "中"
        else:
            advice = "⚪ 观望等待"
            confidence = "低"
        
        print(f"综合评分: {score}/7")
        print(f"投资建议: {advice}")
        print(f"建议置信度: {confidence}")
        
        print(f"\n📋 分析依据:")
        for reason in reasons:
            print(f"  {reason}")
        
        print(f"\n⚠️  风险提示:")
        print("  • 本分析基于技术指标，仅供参考")
        print("  • 股市有风险，投资需谨慎")
        print("  • 建议结合基本面分析和市场环境")
        
        return {
            'score': score,
            'advice': advice,
            'confidence': confidence,
            'reasons': reasons
        }
    
    def plot_comprehensive_analysis(self):
        """绘制综合分析图表"""
        if self.data is None or self.data.empty:
            return
        
        fig, axes = plt.subplots(4, 1, figsize=(15, 16))
        
        # 1. 价格和均线图
        ax1 = axes[0]
        ax1.plot(self.data.index, self.data['Close'], label='收盘价', linewidth=2, color='black')
        ax1.plot(self.data.index, self.data['MA5'], label='MA5', alpha=0.8, color='red')
        ax1.plot(self.data.index, self.data['MA20'], label='MA20', alpha=0.8, color='blue')
        ax1.plot(self.data.index, self.data['MA60'], label='MA60', alpha=0.8, color='green')
        ax1.fill_between(self.data.index, self.data['BB_Upper'], self.data['BB_Lower'], 
                        alpha=0.1, color='gray', label='布林带')
        ax1.set_title(f'{self.stock_name}({self.stock_code}) - 价格走势与均线系统')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 成交量图
        ax2 = axes[1]
        colors = ['red' if x > 0 else 'green' for x in self.data['Change_Pct']]
        ax2.bar(self.data.index, self.data['Volume'], color=colors, alpha=0.6)
        ax2.plot(self.data.index, self.data['Volume_MA'], label='成交量均线', color='orange', linewidth=2)
        ax2.set_title('成交量分析')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. RSI图
        ax3 = axes[2]
        ax3.plot(self.data.index, self.data['RSI'], label='RSI', color='purple', linewidth=2)
        ax3.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='超买线(80)')
        ax3.axhline(y=70, color='orange', linestyle='--', alpha=0.7, label='警戒线(70)')
        ax3.axhline(y=30, color='orange', linestyle='--', alpha=0.7, label='警戒线(30)')
        ax3.axhline(y=20, color='g', linestyle='--', alpha=0.7, label='超卖线(20)')
        ax3.set_title('RSI相对强弱指标')
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. MACD图
        ax4 = axes[3]
        ax4.plot(self.data.index, self.data['MACD'], label='MACD', color='blue', linewidth=2)
        ax4.plot(self.data.index, self.data['MACD_Signal'], label='Signal', color='red', linewidth=2)
        colors = ['red' if x > 0 else 'green' for x in self.data['MACD_Hist']]
        ax4.bar(self.data.index, self.data['MACD_Hist'], label='Histogram', color=colors, alpha=0.6)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.set_title('MACD指标')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.stock_name}_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✅ 图表已保存为 {self.stock_name}_analysis.png")

def main():
    """主函数"""
    print("🚀 晨曦航空(300581) AI量化分析系统")
    print("=" * 70)
    
    # 创建分析器
    analyzer = ChenxiAviationAnalyzer()
    
    # 获取基本信息
    analyzer.fetch_basic_info()
    
    # 获取价格数据
    if not analyzer.fetch_price_data():
        print("❌ 无法获取价格数据，分析终止")
        return
    
    # 计算技术指标
    analyzer.calculate_technical_indicators()
    
    # 分析当前状态
    analyzer.analyze_current_status()
    
    # 风险评估
    analyzer.risk_assessment()
    
    # 生成投资建议
    analyzer.generate_investment_advice()
    
    # 绘制分析图表
    try:
        analyzer.plot_comprehensive_analysis()
    except Exception as e:
        print(f"⚠️  图表绘制失败: {e}")
    
    print(f"\n🎯 分析完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
