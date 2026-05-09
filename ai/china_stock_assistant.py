#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国股市投资助手
基于AKShare数据和量化策略，为中国股市投资提供决策支持
"""

import akshare as ak
import pandas as pd
import numpy as np
import datetime
import warnings
warnings.filterwarnings('ignore')

class ChinaStockAssistant:
    """中国股市投资助手"""
    
    def __init__(self):
        self.name = "中国股市投资助手"
        print(f"🚀 {self.name} 已启动")
        print("基于AKShare免费数据，为您的投资决策提供支持")
    
    def get_market_overview(self):
        """获取市场概览"""
        print("\n📊 今日市场概览")
        print("="*50)
        
        try:
            # 主要指数
            indices = {
                "000001": "上证指数",
                "399001": "深证成指", 
                "399006": "创业板指",
                "000300": "沪深300"
            }
            
            today = datetime.datetime.now().strftime('%Y%m%d')
            
            print("指数名称    | 最新点位 | 涨跌幅 | 趋势")
            print("-" * 45)
            
            for code, name in indices.items():
                try:
                    data = ak.index_zh_a_hist(symbol=code, period="daily", 
                                            start_date=today, end_date=today)
                    if len(data) > 0:
                        close = data['收盘'].iloc[0]
                        pct_chg = data['涨跌幅'].iloc[0]
                        trend = "📈" if pct_chg > 0 else "📉" if pct_chg < 0 else "➡️"
                        print(f"{name:<10} | {close:>8.2f} | {pct_chg:>6.2f}% | {trend}")
                except:
                    print(f"{name:<10} | 获取失败   | 获取失败 | ❌")
            
            # 热门板块
            print(f"\n🔥 今日热门板块 (涨幅前5)")
            sectors = ak.stock_board_industry_name_em()
            top_sectors = sectors.nlargest(5, '涨跌幅')
            
            for _, sector in top_sectors.iterrows():
                print(f"📈 {sector['板块名称']}: +{sector['涨跌幅']:.2f}%")
                
        except Exception as e:
            print(f"❌ 市场概览获取失败: {str(e)}")
    
    def analyze_stock(self, symbol, days=30):
        """分析单只股票"""
        print(f"\n🔍 股票分析: {symbol}")
        print("="*50)
        
        try:
            # 获取历史数据
            end_date = datetime.datetime.now().strftime('%Y%m%d')
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y%m%d')
            
            data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                    start_date=start_date, end_date=end_date, adjust="")
            
            if len(data) == 0:
                print("❌ 未获取到数据")
                return None
            
            # 数据预处理 - 动态处理列名
            if len(data.columns) == 11:
                data.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            elif len(data.columns) == 12:
                data.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率', '额外列']
                data = data.drop('额外列', axis=1)
            else:
                print(f"⚠️ 数据列数异常: {len(data.columns)}列")
                print(f"原始列名: {list(data.columns)}")
                # 使用原始列名
                pass
            
            data['日期'] = pd.to_datetime(data['日期'])
            data = data.sort_values('日期').reset_index(drop=True)
            
            # 技术指标计算
            data['MA5'] = data['收盘'].rolling(window=5).mean()
            data['MA10'] = data['收盘'].rolling(window=10).mean()
            data['MA20'] = data['收盘'].rolling(window=20).mean()
            
            # RSI计算
            delta = data['收盘'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # 布林带
            data['BB_middle'] = data['收盘'].rolling(window=20).mean()
            bb_std = data['收盘'].rolling(window=20).std()
            data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
            data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
            
            latest = data.iloc[-1]
            
            # 基本信息
            print(f"📈 基本信息:")
            print(f"最新价格: {latest['收盘']:.2f} 元")
            print(f"日涨跌幅: {latest['涨跌幅']:.2f}%")
            print(f"成交量: {latest['成交量']:,.0f} 手")
            print(f"换手率: {latest['换手率']:.2f}%")
            
            # 技术分析
            print(f"\n📊 技术指标:")
            print(f"MA5:  {latest['MA5']:.2f}")
            print(f"MA10: {latest['MA10']:.2f}")
            print(f"MA20: {latest['MA20']:.2f}")
            print(f"RSI:  {latest['RSI']:.2f}")
            
            # 趋势判断
            print(f"\n🎯 趋势分析:")
            
            # 均线趋势
            if latest['收盘'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
                ma_trend = "🟢 强势多头排列"
            elif latest['收盘'] > latest['MA5'] > latest['MA10']:
                ma_trend = "🟡 短期多头"
            elif latest['收盘'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
                ma_trend = "🔴 强势空头排列"
            elif latest['收盘'] < latest['MA5'] < latest['MA10']:
                ma_trend = "🟠 短期空头"
            else:
                ma_trend = "⚪ 震荡整理"
            
            print(f"均线趋势: {ma_trend}")
            
            # RSI判断
            if latest['RSI'] > 70:
                rsi_signal = "🔴 超买区域，注意风险"
            elif latest['RSI'] < 30:
                rsi_signal = "🟢 超卖区域，关注机会"
            else:
                rsi_signal = "🟡 正常区域"
            
            print(f"RSI信号: {rsi_signal}")
            
            # 布林带位置
            if latest['收盘'] > latest['BB_upper']:
                bb_signal = "🔴 突破上轨，可能回调"
            elif latest['收盘'] < latest['BB_lower']:
                bb_signal = "🟢 跌破下轨，可能反弹"
            else:
                bb_signal = "🟡 在布林带内运行"
            
            print(f"布林带: {bb_signal}")
            
            # 综合评分
            score = 0
            if latest['收盘'] > latest['MA5']:
                score += 1
            if latest['MA5'] > latest['MA10']:
                score += 1
            if latest['MA10'] > latest['MA20']:
                score += 1
            if 30 < latest['RSI'] < 70:
                score += 1
            if latest['涨跌幅'] > 0:
                score += 1
            
            print(f"\n⭐ 综合评分: {score}/5")
            
            if score >= 4:
                recommendation = "🟢 建议关注，技术面较好"
            elif score >= 3:
                recommendation = "🟡 中性，可适量关注"
            else:
                recommendation = "🔴 谨慎，技术面偏弱"
            
            print(f"投资建议: {recommendation}")
            
            return data
            
        except Exception as e:
            print(f"❌ 股票分析失败: {str(e)}")
            return None
    
    def find_opportunities(self, min_price=5, max_price=50, min_volume=100000):
        """寻找投资机会"""
        print(f"\n🔍 寻找投资机会")
        print("="*50)
        print(f"筛选条件: 价格 {min_price}-{max_price}元, 成交量>{min_volume:,}手")
        
        try:
            # 获取实时行情
            stocks = ak.stock_zh_a_spot_em()
            
            # 筛选条件
            filtered = stocks[
                (stocks['最新价'] >= min_price) & 
                (stocks['最新价'] <= max_price) &
                (stocks['成交量'] >= min_volume) &
                (stocks['涨跌幅'] > -5) &  # 跌幅不超过5%
                (stocks['涨跌幅'] < 10)    # 涨幅不超过10%
            ].copy()
            
            if len(filtered) == 0:
                print("❌ 未找到符合条件的股票")
                return
            
            # 按成交额排序
            filtered = filtered.sort_values('成交额', ascending=False)
            
            print(f"✅ 找到 {len(filtered)} 只符合条件的股票")
            print(f"\n📈 推荐关注 (按成交额排序):")
            
            top_stocks = filtered.head(10)
            print("代码     | 名称     | 价格   | 涨跌幅 | 成交额(亿)")
            print("-" * 50)
            
            for _, stock in top_stocks.iterrows():
                volume_yi = stock['成交额'] / 1e8
                print(f"{stock['代码']:<8} | {stock['名称']:<8} | {stock['最新价']:>6.2f} | {stock['涨跌幅']:>6.2f}% | {volume_yi:>8.2f}")
            
            return top_stocks
            
        except Exception as e:
            print(f"❌ 机会筛选失败: {str(e)}")
            return None
    
    def portfolio_suggestion(self, risk_level="medium"):
        """投资组合建议"""
        print(f"\n💼 投资组合建议 (风险偏好: {risk_level})")
        print("="*50)
        
        try:
            # 获取行业板块数据
            sectors = ak.stock_board_industry_name_em()
            
            if risk_level == "low":
                # 低风险：银行、公用事业
                target_sectors = ['银行', '电力行业', '公用事业']
                allocation = "建议配置: 银行股40%, 公用事业30%, 现金30%"
            elif risk_level == "high":
                # 高风险：科技、新能源
                target_sectors = ['软件开发', '半导体', '新能源']
                allocation = "建议配置: 科技股50%, 新能源30%, 其他20%"
            else:
                # 中等风险：均衡配置
                target_sectors = ['银行', '医药生物', '食品饮料', '软件开发']
                allocation = "建议配置: 金融25%, 消费25%, 医药25%, 科技25%"
            
            print(f"🎯 {allocation}")
            print(f"\n📊 相关板块今日表现:")
            
            for sector_name in target_sectors:
                sector_data = sectors[sectors['板块名称'].str.contains(sector_name, na=False)]
                if len(sector_data) > 0:
                    sector = sector_data.iloc[0]
                    trend = "📈" if sector['涨跌幅'] > 0 else "📉" if sector['涨跌幅'] < 0 else "➡️"
                    print(f"{trend} {sector['板块名称']}: {sector['涨跌幅']:+.2f}%")
            
            print(f"\n⚠️  投资提醒:")
            print(f"1. 分散投资，不要集中持股")
            print(f"2. 定期调仓，保持组合平衡")
            print(f"3. 关注宏观经济和政策变化")
            print(f"4. 设置止损，控制风险")
            
        except Exception as e:
            print(f"❌ 组合建议生成失败: {str(e)}")

def main():
    """主函数"""
    assistant = ChinaStockAssistant()
    
    while True:
        print(f"\n" + "="*60)
        print(f"🎯 中国股市投资助手 - 请选择功能:")
        print(f"1. 📊 市场概览")
        print(f"2. 🔍 股票分析")
        print(f"3. 💎 寻找机会")
        print(f"4. 💼 组合建议")
        print(f"5. 🚪 退出")
        print(f"="*60)
        
        try:
            choice = input("请输入选项 (1-5): ").strip()
            
            if choice == "1":
                assistant.get_market_overview()
                
            elif choice == "2":
                symbol = input("请输入股票代码 (如: 000001): ").strip()
                if symbol:
                    assistant.analyze_stock(symbol)
                else:
                    print("❌ 请输入有效的股票代码")
                    
            elif choice == "3":
                print("设置筛选条件:")
                min_price = float(input("最低价格 (默认5): ") or "5")
                max_price = float(input("最高价格 (默认50): ") or "50")
                min_volume = int(input("最小成交量 (默认100000): ") or "100000")
                assistant.find_opportunities(min_price, max_price, min_volume)
                
            elif choice == "4":
                risk = input("风险偏好 (low/medium/high, 默认medium): ").strip() or "medium"
                assistant.portfolio_suggestion(risk)
                
            elif choice == "5":
                print("👋 感谢使用中国股市投资助手！")
                break
                
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n👋 程序已退出")
            break
        except Exception as e:
            print(f"❌ 操作失败: {str(e)}")

if __name__ == "__main__":
    main()
