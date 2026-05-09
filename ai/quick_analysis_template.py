#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速股票分析模板
基于实战经验总结的完整分析流程
使用方法: python quick_analysis_template.py
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class QuickStockAnalyzer:
    """快速股票分析器"""
    
    def __init__(self):
        self.name = "🎯 快速股票分析器"
        print(f"{self.name} - 基于实战经验的完整分析流程")
        print("=" * 60)
    
    def calculate_all_indicators(self, df):
        """计算所有技术指标"""
        # 移动平均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        
        # RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['收盘'].ewm(span=12).mean()
        exp2 = df['收盘'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        
        # KDJ
        low_min = df['最低'].rolling(window=9).min()
        high_max = df['最高'].rolling(window=9).max()
        rsv = (df['收盘'] - low_min) / (high_max - low_min) * 100
        df['K'] = rsv.ewm(com=2).mean()
        df['D'] = df['K'].ewm(com=2).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        # 布林带
        df['BB_middle'] = df['收盘'].rolling(window=20).mean()
        bb_std = df['收盘'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        df['BB_position'] = (df['收盘'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower']) * 100
        
        return df
    
    def get_fundamental_risks(self, symbol):
        """获取基本面风险因子"""
        risk_database = {
            '300142': {
                'name': '沃森生物',
                'risks': ['新冠疫苗需求下降', '研发投入大', '监管严格'],
                'advantages': ['技术壁垒高', '产品管线丰富']
            },
            '300782': {
                'name': '卓胜微',
                'risks': ['半导体周期下行', '研发占比高', '客户集中'],
                'advantages': ['5G需求增长', '技术实力强']
            },
            '300059': {
                'name': '东方财富',
                'risks': ['券商业务周期性', '市场波动影响'],
                'advantages': ['互联网券商龙头', '用户基数大']
            },
            '300015': {
                'name': '爱尔眼科',
                'risks': ['医疗政策变化', '扩张速度过快'],
                'advantages': ['眼科连锁龙头', '消费升级受益']
            }
        }
        
        return risk_database.get(symbol, {
            'name': '未知',
            'risks': ['需要进一步研究'],
            'advantages': ['需要进一步研究']
        })
    
    def comprehensive_analysis(self, symbol, name=None):
        """综合分析单只股票"""
        try:
            # 获取数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=120)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust='qfq')
            
            if df.empty or len(df) < 30:
                print(f"❌ 无法获取{symbol}的数据")
                return None
            
            # 计算技术指标
            df = self.calculate_all_indicators(df)
            latest = df.iloc[-1]
            
            # 获取基本面信息
            fundamental = self.get_fundamental_risks(symbol)
            if not name:
                name = fundamental['name']
            
            print(f"\\n🎯 {name} ({symbol}) 综合分析")
            print("=" * 50)
            
            # 基本信息
            print(f"📊 基本信息:")
            print(f"   当前价格: {latest['收盘']:.2f}元")
            print(f"   今日涨跌: {((latest['收盘'] - df.iloc[-2]['收盘']) / df.iloc[-2]['收盘'] * 100):+.2f}%")
            
            # 技术指标
            print(f"\\n📈 技术指标:")
            print(f"   MA5/10/20: {latest['MA5']:.2f} / {latest['MA10']:.2f} / {latest['MA20']:.2f}")
            print(f"   RSI: {latest['RSI']:.1f}")
            print(f"   MACD: {latest['MACD']:.3f} (信号线: {latest['MACD_signal']:.3f})")
            print(f"   KDJ: K={latest['K']:.1f}, D={latest['D']:.1f}, J={latest['J']:.1f}")
            print(f"   布林带位置: {latest['BB_position']:.1f}%")
            
            # 技术评分
            tech_score = 0
            tech_signals = []
            
            # 趋势评分
            if latest['收盘'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
                tech_score += 2
                tech_signals.append('多头排列')
            elif latest['收盘'] > latest['MA5']:
                tech_score += 1
                tech_signals.append('短期向上')
            
            # RSI评分
            if 30 <= latest['RSI'] <= 70:
                tech_score += 1
                tech_signals.append('RSI健康')
            elif latest['RSI'] < 30:
                tech_score += 1.5
                tech_signals.append('RSI超卖')
            elif latest['RSI'] > 75:
                tech_score -= 1
                tech_signals.append('RSI超买')
            
            # MACD评分
            if latest['MACD'] > latest['MACD_signal']:
                tech_score += 1
                tech_signals.append('MACD金叉')
            
            # 布林带评分
            if 20 <= latest['BB_position'] <= 80:
                tech_score += 0.5
                tech_signals.append('布林带正常')
            elif latest['BB_position'] > 90:
                tech_score -= 0.5
                tech_signals.append('接近上轨')
            
            print(f"\\n🎯 技术面评分: {tech_score:.1f}/5.0")
            print(f"   主要信号: {' | '.join(tech_signals[:3])}")
            
            # 基本面分析
            print(f"\\n🏢 基本面分析:")
            print(f"   投资亮点:")
            for advantage in fundamental['advantages']:
                print(f"   ✅ {advantage}")
            print(f"   风险因素:")
            for risk in fundamental['risks']:
                print(f"   ⚠️ {risk}")
            
            # 综合建议
            if tech_score >= 3 and len(fundamental['risks']) <= 2:
                recommendation = "🔥 强烈买入"
                risk_level = "中等风险"
            elif tech_score >= 2:
                recommendation = "📈 买入"
                risk_level = "中高风险" if len(fundamental['risks']) > 2 else "中等风险"
            elif tech_score >= 1:
                recommendation = "✅ 持有"
                risk_level = "中高风险"
            else:
                recommendation = "⚖️ 观望"
                risk_level = "高风险"
            
            print(f"\\n💡 综合建议: {recommendation}")
            print(f"🛡️ 风险等级: {risk_level}")
            
            # 操作建议
            if tech_score >= 2:
                stop_loss = latest['收盘'] * 0.92  # -8%止损
                target_price = latest['收盘'] * 1.15  # +15%目标
                print(f"\\n📊 操作建议:")
                print(f"   建议买入价: {latest['收盘']:.2f}元附近")
                print(f"   止损位: {stop_loss:.2f}元 (-8%)")
                print(f"   目标位: {target_price:.2f}元 (+15%)")
            
            return {
                'symbol': symbol,
                'name': name,
                'price': latest['收盘'],
                'tech_score': tech_score,
                'recommendation': recommendation,
                'risk_level': risk_level,
                'signals': tech_signals
            }
            
        except Exception as e:
            print(f"❌ 分析{symbol}时出错: {e}")
            return None
    
    def batch_analysis(self, stock_list):
        """批量分析股票"""
        print("\\n🎯 开始批量分析...")
        results = []
        
        for i, (symbol, name) in enumerate(stock_list, 1):
            print(f"\\n进度: {i}/{len(stock_list)}")
            result = self.comprehensive_analysis(symbol, name)
            if result:
                results.append(result)
        
        # 排序和总结
        if results:
            results.sort(key=lambda x: x['tech_score'], reverse=True)
            
            print("\\n" + "=" * 60)
            print("🏆 批量分析结果汇总")
            print("=" * 60)
            print(f"{'排名':<4} {'股票名称':<12} {'代码':<8} {'价格':<8} {'评分':<6} {'建议'}")
            print("-" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"{i:<4} {result['name']:<12} {result['symbol']:<8} "
                      f"{result['price']:<8.2f} {result['tech_score']:<6.1f} {result['recommendation']}")
        
        return results

def main():
    """主函数 - 使用示例"""
    analyzer = QuickStockAnalyzer()
    
    print("请选择分析模式:")
    print("1. 单股分析")
    print("2. 批量分析 (使用预设股票池)")
    print("3. 自定义批量分析")
    
    try:
        choice = input("\\n请输入选择 (1-3): ").strip()
        
        if choice == '1':
            symbol = input("请输入股票代码 (如: 300142): ").strip()
            analyzer.comprehensive_analysis(symbol)
            
        elif choice == '2':
            # 预设股票池 (基于实战经验)
            preset_stocks = [
                ('300142', '沃森生物'),
                ('300782', '卓胜微'),
                ('300059', '东方财富'),
                ('300015', '爱尔眼科'),
                ('002475', '立讯精密'),
                ('002415', '海康威视'),
                ('600036', '招商银行')
            ]
            analyzer.batch_analysis(preset_stocks)
            
        elif choice == '3':
            print("请输入股票代码，用逗号分隔 (如: 300142,300782,300059)")
            symbols_input = input("股票代码: ").strip()
            symbols = [s.strip() for s in symbols_input.split(',')]
            stock_list = [(symbol, '') for symbol in symbols]
            analyzer.batch_analysis(stock_list)
            
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\\n👋 用户取消操作")
    except Exception as e:
        print(f"❌ 程序出错: {e}")

if __name__ == "__main__":
    main()
