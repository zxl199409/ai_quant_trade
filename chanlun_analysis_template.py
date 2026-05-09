#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠中说缠理论股票分析模板
基于缠论核心理论：分型、笔、线段、中枢、买卖点分析
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChanLunAnalyzer:
    """缠中说缠理论分析器"""
    
    def __init__(self, symbol, name=None):
        self.symbol = symbol
        self.name = name or symbol
        self.data = None
        self.fenxing = []  # 分型
        self.bi = []      # 笔
        self.zhongshu = []  # 中枢
        self.buy_points = []  # 买点
        self.sell_points = []  # 卖点
        
    def fetch_data(self, period="daily", start_date="20230101"):
        """获取股票数据"""
        try:
            print(f"📊 获取 {self.name} 数据...")
            
            # 尝试不同的数据获取方式
            if self.symbol.isdigit() and len(self.symbol) == 6:
                # A股代码
                raw_data = ak.stock_zh_a_hist(
                    symbol=self.symbol, 
                    period=period, 
                    start_date=start_date,
                    adjust="qfq"
                )
                if not raw_data.empty:
                    raw_data.columns = ['Date', 'Code', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_Pct', 'Change_Amount', 'Turnover']
            else:
                # 尝试获取股票名称对应的代码
                stock_list = ak.stock_zh_a_spot_em()
                matched = stock_list[stock_list['名称'].str.contains(self.symbol, na=False)]
                if not matched.empty:
                    code = matched.iloc[0]['代码']
                    self.symbol = code
                    print(f"✅ 找到股票: {matched.iloc[0]['名称']} ({code})")
                    raw_data = ak.stock_zh_a_hist(
                        symbol=code, 
                        period=period, 
                        start_date=start_date,
                        adjust="qfq"
                    )
                    raw_data.columns = ['Date', 'Code', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_Pct', 'Change_Amount', 'Turnover']
                else:
                    print(f"❌ 未找到股票: {self.symbol}")
                    return False
            
            if raw_data is not None and not raw_data.empty:
                self.data = raw_data.copy()
                self.data['Date'] = pd.to_datetime(self.data['Date'])
                self.data.set_index('Date', inplace=True)
                
                print(f"✅ 成功获取数据，共 {len(self.data)} 条记录")
                print(f"   数据时间范围: {self.data.index[0].date()} 到 {self.data.index[-1].date()}")
                return True
            else:
                print("❌ 未获取到数据")
                return False
                
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return False
    
    def find_fenxing(self):
        """识别分型（顶分型和底分型）"""
        if self.data is None or len(self.data) < 3:
            return
        
        print("🔍 识别分型...")
        self.fenxing = []
        
        for i in range(1, len(self.data) - 1):
            current = self.data.iloc[i]
            prev = self.data.iloc[i-1]
            next_bar = self.data.iloc[i+1]
            
            # 顶分型：当前K线的高点是三根K线中最高的，低点也不是最低的
            if (current['High'] >= prev['High'] and current['High'] >= next_bar['High'] and
                current['Low'] >= min(prev['Low'], next_bar['Low'])):
                self.fenxing.append({
                    'index': i,
                    'date': current.name,
                    'type': 'top',
                    'price': current['High'],
                    'high': current['High'],
                    'low': current['Low']
                })
            
            # 底分型：当前K线的低点是三根K线中最低的，高点也不是最高的
            elif (current['Low'] <= prev['Low'] and current['Low'] <= next_bar['Low'] and
                  current['High'] <= max(prev['High'], next_bar['High'])):
                self.fenxing.append({
                    'index': i,
                    'date': current.name,
                    'type': 'bottom',
                    'price': current['Low'],
                    'high': current['High'],
                    'low': current['Low']
                })
        
        print(f"✅ 识别到 {len(self.fenxing)} 个分型")
        return self.fenxing
    
    def find_bi(self):
        """识别笔"""
        if not self.fenxing:
            self.find_fenxing()
        
        print("🔍 识别笔...")
        self.bi = []
        
        if len(self.fenxing) < 2:
            return self.bi
        
        # 笔的形成需要相邻的分型类型不同
        current_bi = None
        
        for i, fx in enumerate(self.fenxing):
            if current_bi is None:
                current_bi = fx
            else:
                # 如果分型类型不同，形成一笔
                if fx['type'] != current_bi['type']:
                    self.bi.append({
                        'start': current_bi,
                        'end': fx,
                        'direction': 'up' if current_bi['type'] == 'bottom' else 'down',
                        'strength': abs(fx['price'] - current_bi['price'])
                    })
                    current_bi = fx
                else:
                    # 同类型分型，选择更极端的
                    if fx['type'] == 'top' and fx['price'] > current_bi['price']:
                        current_bi = fx
                    elif fx['type'] == 'bottom' and fx['price'] < current_bi['price']:
                        current_bi = fx
        
        print(f"✅ 识别到 {len(self.bi)} 笔")
        return self.bi
    
    def find_zhongshu(self):
        """识别中枢"""
        if not self.bi:
            self.find_bi()
        
        print("🔍 识别中枢...")
        self.zhongshu = []
        
        if len(self.bi) < 3:
            return self.zhongshu
        
        # 中枢的形成需要至少三笔，且有重叠区间
        for i in range(len(self.bi) - 2):
            bi1 = self.bi[i]
            bi2 = self.bi[i + 1]
            bi3 = self.bi[i + 2]
            
            # 计算三笔的价格区间
            prices = []
            for bi in [bi1, bi2, bi3]:
                prices.extend([bi['start']['price'], bi['end']['price']])
            
            # 找出重叠区间
            max_low = max(min(bi1['start']['price'], bi1['end']['price']),
                         min(bi2['start']['price'], bi2['end']['price']),
                         min(bi3['start']['price'], bi3['end']['price']))
            
            min_high = min(max(bi1['start']['price'], bi1['end']['price']),
                          max(bi2['start']['price'], bi2['end']['price']),
                          max(bi3['start']['price'], bi3['end']['price']))
            
            # 如果有重叠区间，形成中枢
            if max_low < min_high:
                zhongshu_center = (max_low + min_high) / 2
                zhongshu_height = min_high - max_low
                
                self.zhongshu.append({
                    'start_date': bi1['start']['date'],
                    'end_date': bi3['end']['date'],
                    'high': min_high,
                    'low': max_low,
                    'center': zhongshu_center,
                    'height': zhongshu_height,
                    'strength': zhongshu_height / zhongshu_center * 100,  # 中枢强度
                    'bi_count': 3
                })
        
        # 合并相邻的中枢
        self.zhongshu = self._merge_zhongshu(self.zhongshu)
        
        print(f"✅ 识别到 {len(self.zhongshu)} 个中枢")
        return self.zhongshu
    
    def _merge_zhongshu(self, zhongshu_list):
        """合并相邻的中枢"""
        if len(zhongshu_list) <= 1:
            return zhongshu_list
        
        merged = []
        current = zhongshu_list[0]
        
        for i in range(1, len(zhongshu_list)):
            next_zs = zhongshu_list[i]
            
            # 如果两个中枢有重叠，合并它们
            if (current['low'] <= next_zs['high'] and current['high'] >= next_zs['low']):
                current = {
                    'start_date': current['start_date'],
                    'end_date': next_zs['end_date'],
                    'high': max(current['high'], next_zs['high']),
                    'low': min(current['low'], next_zs['low']),
                    'center': (max(current['high'], next_zs['high']) + min(current['low'], next_zs['low'])) / 2,
                    'height': max(current['high'], next_zs['high']) - min(current['low'], next_zs['low']),
                    'strength': (max(current['high'], next_zs['high']) - min(current['low'], next_zs['low'])) / 
                               ((max(current['high'], next_zs['high']) + min(current['low'], next_zs['low'])) / 2) * 100,
                    'bi_count': current['bi_count'] + next_zs['bi_count'] - 1
                }
            else:
                merged.append(current)
                current = next_zs
        
        merged.append(current)
        return merged
    
    def find_buy_sell_points(self):
        """识别买卖点"""
        if not self.zhongshu:
            self.find_zhongshu()
        
        print("🔍 识别买卖点...")
        self.buy_points = []
        self.sell_points = []
        
        current_price = self.data['Close'].iloc[-1]
        
        for zs in self.zhongshu:
            # 一类买点：中枢下方的底分型
            for fx in self.fenxing:
                if (fx['type'] == 'bottom' and 
                    fx['price'] < zs['low'] and 
                    fx['date'] >= zs['start_date'] and 
                    fx['date'] <= zs['end_date']):
                    
                    self.buy_points.append({
                        'date': fx['date'],
                        'price': fx['price'],
                        'type': '一类买点',
                        'zhongshu': zs,
                        'confidence': self._calculate_confidence(fx, zs, 'buy')
                    })
            
            # 二类买点：回测中枢下沿不破
            for fx in self.fenxing:
                if (fx['type'] == 'bottom' and 
                    fx['price'] > zs['low'] and 
                    fx['price'] < zs['center'] and
                    fx['date'] > zs['end_date']):
                    
                    self.buy_points.append({
                        'date': fx['date'],
                        'price': fx['price'],
                        'type': '二类买点',
                        'zhongshu': zs,
                        'confidence': self._calculate_confidence(fx, zs, 'buy')
                    })
            
            # 一类卖点：中枢上方的顶分型
            for fx in self.fenxing:
                if (fx['type'] == 'top' and 
                    fx['price'] > zs['high'] and 
                    fx['date'] >= zs['start_date'] and 
                    fx['date'] <= zs['end_date']):
                    
                    self.sell_points.append({
                        'date': fx['date'],
                        'price': fx['price'],
                        'type': '一类卖点',
                        'zhongshu': zs,
                        'confidence': self._calculate_confidence(fx, zs, 'sell')
                    })
            
            # 二类卖点：回测中枢上沿不破
            for fx in self.fenxing:
                if (fx['type'] == 'top' and 
                    fx['price'] < zs['high'] and 
                    fx['price'] > zs['center'] and
                    fx['date'] > zs['end_date']):
                    
                    self.sell_points.append({
                        'date': fx['date'],
                        'price': fx['price'],
                        'type': '二类卖点',
                        'zhongshu': zs,
                        'confidence': self._calculate_confidence(fx, zs, 'sell')
                    })
        
        print(f"✅ 识别到 {len(self.buy_points)} 个买点，{len(self.sell_points)} 个卖点")
        return self.buy_points, self.sell_points
    
    def _calculate_confidence(self, fenxing, zhongshu, point_type):
        """计算买卖点的置信度"""
        confidence = 50  # 基础置信度
        
        # 根据中枢强度调整
        if zhongshu['strength'] > 10:
            confidence += 20
        elif zhongshu['strength'] > 5:
            confidence += 10
        
        # 根据笔的数量调整
        if zhongshu['bi_count'] >= 5:
            confidence += 15
        elif zhongshu['bi_count'] >= 3:
            confidence += 10
        
        # 根据距离中枢的远近调整
        if point_type == 'buy':
            distance_ratio = (zhongshu['low'] - fenxing['price']) / zhongshu['height']
        else:
            distance_ratio = (fenxing['price'] - zhongshu['high']) / zhongshu['height']
        
        if distance_ratio > 0.5:
            confidence += 10
        elif distance_ratio > 0.2:
            confidence += 5
        
        return min(confidence, 95)  # 最高95%置信度
    
    def analyze_current_position(self):
        """分析当前位置"""
        if not self.zhongshu:
            return
        
        current_price = self.data['Close'].iloc[-1]
        current_date = self.data.index[-1]
        
        print(f"\n📊 {self.name} 当前位置分析")
        print("=" * 60)
        print(f"当前价格: ¥{current_price:.2f}")
        print(f"分析时间: {current_date.date()}")
        
        # 找到最近的中枢
        recent_zhongshu = None
        for zs in reversed(self.zhongshu):
            if zs['end_date'] <= current_date:
                recent_zhongshu = zs
                break
        
        if recent_zhongshu:
            print(f"\n🎯 最近中枢分析:")
            print(f"中枢区间: ¥{recent_zhongshu['low']:.2f} - ¥{recent_zhongshu['high']:.2f}")
            print(f"中枢中心: ¥{recent_zhongshu['center']:.2f}")
            print(f"中枢强度: {recent_zhongshu['strength']:.2f}%")
            
            # 判断当前位置
            if current_price > recent_zhongshu['high']:
                position = "🟢 中枢上方"
                suggestion = "关注回调买点或突破确认"
            elif current_price < recent_zhongshu['low']:
                position = "🔴 中枢下方"
                suggestion = "关注反弹卖点或支撑确认"
            else:
                position = "🟡 中枢内部"
                suggestion = "等待突破方向确认"
            
            print(f"当前位置: {position}")
            print(f"操作建议: {suggestion}")
        
        # 最近的买卖点
        recent_buy = None
        recent_sell = None
        
        for bp in reversed(self.buy_points):
            if bp['date'] <= current_date:
                recent_buy = bp
                break
        
        for sp in reversed(self.sell_points):
            if sp['date'] <= current_date:
                recent_sell = sp
                break
        
        if recent_buy:
            print(f"\n🟢 最近买点:")
            print(f"   时间: {recent_buy['date'].date()}")
            print(f"   价格: ¥{recent_buy['price']:.2f}")
            print(f"   类型: {recent_buy['type']}")
            print(f"   置信度: {recent_buy['confidence']:.0f}%")
        
        if recent_sell:
            print(f"\n🔴 最近卖点:")
            print(f"   时间: {recent_sell['date'].date()}")
            print(f"   价格: ¥{recent_sell['price']:.2f}")
            print(f"   类型: {recent_sell['type']}")
            print(f"   置信度: {recent_sell['confidence']:.0f}%")
    
    def plot_chanlun_analysis(self):
        """绘制缠论分析图"""
        if self.data is None:
            return
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # 绘制K线图（简化版）
        for i, (date, row) in enumerate(self.data.iterrows()):
            color = 'red' if row['Close'] > row['Open'] else 'green'
            ax.plot([i, i], [row['Low'], row['High']], color='black', linewidth=0.5)
            ax.plot([i, i], [row['Open'], row['Close']], color=color, linewidth=2)
        
        # 绘制分型
        for fx in self.fenxing:
            idx = fx['index']
            if fx['type'] == 'top':
                ax.scatter(idx, fx['price'], color='red', marker='v', s=50, zorder=5)
                ax.annotate('顶', (idx, fx['price']), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8, color='red')
            else:
                ax.scatter(idx, fx['price'], color='green', marker='^', s=50, zorder=5)
                ax.annotate('底', (idx, fx['price']), xytext=(5, -15), 
                           textcoords='offset points', fontsize=8, color='green')
        
        # 绘制笔
        for bi in self.bi:
            start_idx = bi['start']['index']
            end_idx = bi['end']['index']
            color = 'blue' if bi['direction'] == 'up' else 'orange'
            ax.plot([start_idx, end_idx], [bi['start']['price'], bi['end']['price']], 
                   color=color, linewidth=2, alpha=0.7)
        
        # 绘制中枢
        for i, zs in enumerate(self.zhongshu):
            # 找到中枢对应的索引范围
            start_idx = 0
            end_idx = len(self.data) - 1
            
            for j, (date, _) in enumerate(self.data.iterrows()):
                if date >= zs['start_date'] and start_idx == 0:
                    start_idx = j
                if date <= zs['end_date']:
                    end_idx = j
            
            # 绘制中枢矩形
            rect = patches.Rectangle((start_idx, zs['low']), end_idx - start_idx, 
                                   zs['height'], linewidth=1, edgecolor='purple', 
                                   facecolor='purple', alpha=0.2)
            ax.add_patch(rect)
            
            # 标注中枢
            ax.text(start_idx + (end_idx - start_idx) / 2, zs['center'], 
                   f'中枢{i+1}', ha='center', va='center', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # 绘制买卖点
        for bp in self.buy_points:
            # 找到对应的索引
            for j, (date, _) in enumerate(self.data.iterrows()):
                if date >= bp['date']:
                    ax.scatter(j, bp['price'], color='red', marker='o', s=100, zorder=6)
                    ax.annotate(f"B{bp['type'][-3:]}", (j, bp['price']), 
                               xytext=(10, 10), textcoords='offset points', 
                               fontsize=10, color='red', weight='bold')
                    break
        
        for sp in self.sell_points:
            # 找到对应的索引
            for j, (date, _) in enumerate(self.data.iterrows()):
                if date >= sp['date']:
                    ax.scatter(j, sp['price'], color='blue', marker='o', s=100, zorder=6)
                    ax.annotate(f"S{sp['type'][-3:]}", (j, sp['price']), 
                               xytext=(10, -20), textcoords='offset points', 
                               fontsize=10, color='blue', weight='bold')
                    break
        
        ax.set_title(f'{self.name} 缠中说缠理论分析', fontsize=16, fontweight='bold')
        ax.set_xlabel('时间')
        ax.set_ylabel('价格 (¥)')
        ax.grid(True, alpha=0.3)
        
        # 设置x轴标签
        step = max(1, len(self.data) // 10)
        ax.set_xticks(range(0, len(self.data), step))
        ax.set_xticklabels([self.data.index[i].strftime('%Y-%m-%d') 
                           for i in range(0, len(self.data), step)], rotation=45)
        
        plt.tight_layout()
        
        # 保存图表
        filename = f'{self.name}_缠论分析_{datetime.now().strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ 缠论分析图已保存为: {filename}")
        
        plt.show()
    
    def generate_report(self):
        """生成分析报告"""
        print(f"\n📋 {self.name} 缠中说缠分析报告")
        print("=" * 70)
        
        if not self.data is None:
            print(f"📊 基本信息:")
            print(f"   股票代码: {self.symbol}")
            print(f"   分析周期: {self.data.index[0].date()} 至 {self.data.index[-1].date()}")
            print(f"   当前价格: ¥{self.data['Close'].iloc[-1]:.2f}")
        
        print(f"\n🔍 缠论要素统计:")
        print(f"   分型数量: {len(self.fenxing)} 个")
        print(f"   笔的数量: {len(self.bi)} 个")
        print(f"   中枢数量: {len(self.zhongshu)} 个")
        print(f"   买点数量: {len(self.buy_points)} 个")
        print(f"   卖点数量: {len(self.sell_points)} 个")
        
        if self.zhongshu:
            print(f"\n🎯 中枢详情:")
            for i, zs in enumerate(self.zhongshu):
                print(f"   中枢{i+1}: ¥{zs['low']:.2f}-¥{zs['high']:.2f} "
                      f"(强度: {zs['strength']:.1f}%, 笔数: {zs['bi_count']})")
        
        if self.buy_points:
            print(f"\n🟢 买点详情:")
            for bp in self.buy_points[-3:]:  # 显示最近3个买点
                print(f"   {bp['date'].date()}: ¥{bp['price']:.2f} "
                      f"({bp['type']}, 置信度: {bp['confidence']:.0f}%)")
        
        if self.sell_points:
            print(f"\n🔴 卖点详情:")
            for sp in self.sell_points[-3:]:  # 显示最近3个卖点
                print(f"   {sp['date'].date()}: ¥{sp['price']:.2f} "
                      f"({sp['type']}, 置信度: {sp['confidence']:.0f}%)")
        
        print(f"\n⚠️  风险提示:")
        print("   • 缠论分析具有一定主观性，仅供参考")
        print("   • 买卖点需要结合市场环境和基本面分析")
        print("   • 投资有风险，决策需谨慎")

def main():
    """主函数 - 交互式分析"""
    print("🚀 缠中说缠理论股票分析系统")
    print("=" * 50)
    
    # 获取用户输入
    symbol = input("请输入股票代码或名称: ").strip()
    if not symbol:
        print("❌ 请输入有效的股票代码或名称")
        return
    
    # 创建分析器
    analyzer = ChanLunAnalyzer(symbol)
    
    # 获取数据
    if not analyzer.fetch_data():
        return
    
    print("\n🔧 开始缠论分析...")
    
    # 执行分析
    analyzer.find_fenxing()
    analyzer.find_bi()
    analyzer.find_zhongshu()
    analyzer.find_buy_sell_points()
    
    # 分析当前位置
    analyzer.analyze_current_position()
    
    # 生成报告
    analyzer.generate_report()
    
    # 询问是否绘制图表
    plot_choice = input("\n是否绘制缠论分析图? (y/n): ").strip().lower()
    if plot_choice in ['y', 'yes', '是']:
        try:
            analyzer.plot_chanlun_analysis()
        except Exception as e:
            print(f"⚠️  图表绘制失败: {e}")

if __name__ == "__main__":
    main()
