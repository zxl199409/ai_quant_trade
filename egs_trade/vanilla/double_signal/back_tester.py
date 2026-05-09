# -*- coding: utf-8 -*-
"""
双信号策略回测程序

回测参数：
- 时间范围：2024-01-01 至 2025-10-27
- 初始资金：10万
- 仓位管理：满仓买入
- 止盈：10%
- 止损：10%
"""

import argparse
import os
import sys
import pandas as pd
import yaml
import numpy as np
from datetime import datetime

# 添加项目路径
path = os.getcwd()
sys.path.append(os.path.abspath(path + ('/..' * 3)))

from strategy import DoubleSignalStrategy

# 尝试导入项目模块
try:
    from quant_brain.back_test.account_info import Account
    from quant_brain.data_io.api_tushare_data import TuShareData
    from tools.log.log_util import log
    HAS_QUANT_BRAIN = True
except ImportError:
    HAS_QUANT_BRAIN = False
    print("警告：未找到quant_brain模块，使用简化版回测")


class DoubleSignalBackTester:
    """双信号策略回测器"""

    def __init__(self, config_path):
        """
        初始化回测器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf8') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        self.data_config = self.config['data_condition']
        self.test_config = self.config['test_condition']
        self.order_cost = self.config['order_cost']

        # 初始化策略
        self.strategy = DoubleSignalStrategy(
            bollinger_period=self.test_config.get('bollinger_period', 20),
            profit_target=self.test_config.get('profit_target', 0.10),
            stop_loss=self.test_config.get('stop_loss', 0.10)
        )

        # 初始化账户
        self.initial_capital = self.test_config['capital']
        self.reset_account()

        # 交易记录
        self.trades = []

    def reset_account(self):
        """重置账户状态"""
        self.cash = self.initial_capital
        self.position = 0  # 持仓数量
        self.position_cost = 0  # 持仓成本
        self.total_value = self.initial_capital

    def load_data_simple(self, stock_code):
        """
        简化版数据加载（使用CSV文件或模拟数据）

        Args:
            stock_code: 股票代码

        Returns:
            DataFrame: 股票数据
        """
        csv_path = f"{self.data_config.get('csv_dir', './data')}/{stock_code}.csv"

        if os.path.exists(csv_path):
            print(f"从CSV加载数据: {csv_path}")
            df = pd.read_csv(csv_path)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
        else:
            print(f"警告：未找到 {csv_path}，生成模拟数据")
            return self.generate_mock_data()

    def generate_mock_data(self):
        """生成模拟数据用于测试"""
        np.random.seed(42)
        start_date = pd.to_datetime(self.data_config['start_time'])
        end_date = pd.to_datetime(self.data_config['end_time'])
        dates = pd.date_range(start_date, end_date, freq='D')

        # 过滤掉周末
        dates = [d for d in dates if d.weekday() < 5]

        n = len(dates)
        base_price = 20.0
        prices = base_price + np.random.randn(n).cumsum() * 0.5

        data = {
            'trade_date': dates,
            'open': prices + np.random.randn(n) * 0.1,
            'high': prices + abs(np.random.randn(n)) * 0.3,
            'low': prices - abs(np.random.randn(n)) * 0.3,
            'close': prices,
            'vol': np.random.randint(1000000, 10000000, n)
        }

        df = pd.DataFrame(data)
        # 确保high是最高，low是最低
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)

        return df

    def calculate_cost(self, price, volume, is_buy=True):
        """
        计算交易成本

        Args:
            price: 价格
            volume: 数量
            is_buy: 是否买入

        Returns:
            float: 手续费
        """
        value = price * volume

        if is_buy:
            # 买入：佣金
            commission = max(value * self.order_cost['open_commission'],
                           self.order_cost['min_commission'])
            return commission
        else:
            # 卖出：佣金 + 印花税
            commission = max(value * self.order_cost['close_commission'],
                           self.order_cost['min_commission'])
            tax = value * self.order_cost['close_tax']
            return commission + tax

    def execute_trade(self, date, price, action, reason=''):
        """
        执行交易

        Args:
            date: 交易日期
            price: 交易价格
            action: 'buy' or 'sell'
            reason: 交易原因
        """
        if action == 'buy' and self.position == 0:
            # 满仓买入
            available_cash = self.cash
            # 计算可买数量（100股为一手）
            shares = int(available_cash / price / 100) * 100

            if shares >= 100:
                cost = self.calculate_cost(price, shares, is_buy=True)
                total_cost = price * shares + cost

                if total_cost <= self.cash:
                    self.position = shares
                    self.position_cost = price
                    self.cash -= total_cost

                    trade_record = {
                        'date': date,
                        'action': 'buy',
                        'price': price,
                        'shares': shares,
                        'cost': cost,
                        'cash': self.cash,
                        'reason': reason
                    }
                    self.trades.append(trade_record)
                    print(f"[买入] {date.date()} 价格:{price:.2f} 数量:{shares} 成本:{cost:.2f}")

        elif action == 'sell' and self.position > 0:
            # 卖出全部持仓
            shares = self.position
            cost = self.calculate_cost(price, shares, is_buy=False)
            revenue = price * shares - cost

            profit = (price - self.position_cost) * shares - cost
            profit_rate = profit / (self.position_cost * shares)

            self.cash += revenue
            self.position = 0
            self.position_cost = 0

            trade_record = {
                'date': date,
                'action': 'sell',
                'price': price,
                'shares': shares,
                'cost': cost,
                'profit': profit,
                'profit_rate': profit_rate,
                'cash': self.cash,
                'reason': reason
            }
            self.trades.append(trade_record)
            print(f"[卖出] {date.date()} 价格:{price:.2f} 数量:{shares} 盈亏:{profit:.2f} "
                  f"({profit_rate*100:.2f}%) 原因:{reason}")

    def backtest_stock(self, stock_code):
        """
        回测单个股票

        Args:
            stock_code: 股票代码
        """
        print(f"\n{'='*60}")
        print(f"开始回测股票: {stock_code}")
        print(f"{'='*60}")

        # 加载数据
        df = self.load_data_simple(stock_code)

        # 生成信号
        df = self.strategy.generate_signals(df)

        # 过滤时间范围
        start_time = pd.to_datetime(self.data_config['start_time'])
        end_time = pd.to_datetime(self.data_config['end_time'])
        df = df[(df['trade_date'] >= start_time) & (df['trade_date'] <= end_time)]

        print(f"数据范围: {df['trade_date'].min().date()} 至 {df['trade_date'].max().date()}")
        print(f"交易日数量: {len(df)}")

        # 逐日回测
        for idx, row in df.iterrows():
            date = row['trade_date']
            price = row['close']

            # 检查卖出信号（持仓时）
            if self.position > 0:
                should_sell, reason = self.strategy.check_sell_signal(price, self.position_cost)
                if should_sell:
                    self.execute_trade(date, price, 'sell', reason)

            # 检查买入信号（空仓时）
            elif row['buy_signal']:
                self.execute_trade(date, price, 'buy', 'double_signal')

        # 最后一天强制平仓
        if self.position > 0:
            last_price = df.iloc[-1]['close']
            last_date = df.iloc[-1]['trade_date']
            self.execute_trade(last_date, last_price, 'sell', 'final_close')

    def backtest_multiple_stocks(self):
        """回测多个股票"""
        stock_list = self.data_config['stock_lst']

        for stock_code in stock_list:
            self.reset_account()
            self.backtest_stock(stock_code)
            self.print_results(stock_code)

    def print_results(self, stock_code=''):
        """
        打印回测结果

        Args:
            stock_code: 股票代码
        """
        print(f"\n{'='*60}")
        print(f"回测结果汇总 {stock_code}")
        print(f"{'='*60}")

        if len(self.trades) == 0:
            print("没有交易记录")
            return

        # 计算最终权益
        final_value = self.cash + self.position * self.trades[-1].get('price', 0)

        # 统计数据
        buy_trades = [t for t in self.trades if t['action'] == 'buy']
        sell_trades = [t for t in self.trades if t['action'] == 'sell']

        total_profit = sum([t.get('profit', 0) for t in sell_trades])
        win_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        loss_trades = [t for t in sell_trades if t.get('profit', 0) < 0]

        # 打印结果
        print(f"\n初始资金: {self.initial_capital:,.2f}")
        print(f"最终资金: {final_value:,.2f}")
        print(f"总收益: {total_profit:,.2f}")
        print(f"收益率: {(final_value/self.initial_capital - 1)*100:.2f}%")

        print(f"\n交易次数: {len(buy_trades)}")
        print(f"盈利次数: {len(win_trades)}")
        print(f"亏损次数: {len(loss_trades)}")

        if len(sell_trades) > 0:
            win_rate = len(win_trades) / len(sell_trades)
            print(f"胜率: {win_rate*100:.2f}%")

            avg_profit = sum([t['profit'] for t in win_trades]) / len(win_trades) if len(win_trades) > 0 else 0
            avg_loss = sum([t['profit'] for t in loss_trades]) / len(loss_trades) if len(loss_trades) > 0 else 0
            print(f"平均盈利: {avg_profit:,.2f}")
            print(f"平均亏损: {avg_loss:,.2f}")

            if avg_loss != 0:
                profit_loss_ratio = abs(avg_profit / avg_loss)
                print(f"盈亏比: {profit_loss_ratio:.2f}")

        print(f"\n交易明细:")
        print(f"{'日期':<12} {'操作':<6} {'价格':<8} {'数量':<8} {'盈亏':<12} {'原因':<15}")
        print("-" * 70)
        for trade in self.trades:
            profit_str = f"{trade.get('profit', 0):,.2f}" if 'profit' in trade else '-'
            print(f"{str(trade['date'].date()):<12} {trade['action']:<6} "
                  f"{trade['price']:<8.2f} {trade['shares']:<8} "
                  f"{profit_str:<12} {trade.get('reason', ''):<15}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='双信号策略回测')
    parser.add_argument('--config', type=str,
                       default='conf/double_signal.yaml',
                       help='配置文件路径')
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("双信号策略回测系统")
    print("策略：布林带紫色信号 + 主力资金箭头信号")
    print(f"{'='*60}\n")

    # 创建回测器
    backtester = DoubleSignalBackTester(args.config)

    # 执行回测
    backtester.backtest_multiple_stocks()

    print(f"\n{'='*60}")
    print("回测完成!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
