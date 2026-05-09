# -*- coding: utf-8 -*-
"""
双信号选股策略：布林带紫色信号 + 主力资金箭头信号

策略逻辑：
1. 主图紫色信号：当日收盘价站上布林上轨(+1std)且涨幅>=3%
2. 附图箭头信号：主力资金、MA5、MA20三线向上 且 主力资金突破60日高点
3. 买入：两个信号同时满足
4. 卖出：止盈10% 或 止损10%
"""

import pandas as pd
import numpy as np


class DoubleSignalStrategy:
    """双信号选股策略"""

    def __init__(self, bollinger_period=20, profit_target=0.10, stop_loss=0.10):
        """
        初始化策略参数

        Args:
            bollinger_period: 布林带周期，默认20
            profit_target: 止盈比例，默认0.10 (10%)
            stop_loss: 止损比例，默认0.10 (10%)
        """
        self.bollinger_period = bollinger_period
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.big_order_ratio = 0.7  # 大单比例

    def calculate_bollinger_bands(self, df):
        """
        计算布林带指标

        Args:
            df: DataFrame with 'close' column

        Returns:
            df: 添加了 'boll_mid', 'boll_upper', 'boll_lower' 列的DataFrame
        """
        df = df.copy()

        # 中轨：N日均线
        df['boll_mid'] = df['close'].rolling(window=self.bollinger_period).mean()

        # 标准差
        std = df['close'].rolling(window=self.bollinger_period).std()

        # 上轨：中轨 + 1倍标准差
        df['boll_upper'] = df['boll_mid'] + 1 * std

        # 下轨：中轨 - 1倍标准差
        df['boll_lower'] = df['boll_mid'] - 1 * std

        return df

    def calculate_main_fund_flow(self, df):
        """
        计算主力资金流指标

        Args:
            df: DataFrame with 'open', 'high', 'low', 'close', 'vol' columns

        Returns:
            df: 添加了 'main_fund', 'main_fund_ma5', 'main_fund_ma20' 列的DataFrame
        """
        df = df.copy()

        # 计算净流入
        buy_estimate = np.where(
            df['close'] > df['open'],
            df['vol'] * (df['close'] - df['open']) / (df['high'] - df['low'] + 0.01) * self.big_order_ratio,
            0
        )

        sell_estimate = np.where(
            df['close'] < df['open'],
            df['vol'] * (df['open'] - df['close']) / (df['high'] - df['low'] + 0.01) * self.big_order_ratio,
            0
        )

        net_inflow = (buy_estimate - sell_estimate) / 100

        # 累积主力资金
        df['main_fund'] = net_inflow.cumsum()

        # 主力资金均线
        df['main_fund_ma5'] = df['main_fund'].rolling(window=5).mean()
        df['main_fund_ma20'] = df['main_fund'].rolling(window=20).mean()

        return df

    def check_purple_signal(self, row):
        """
        检查主图紫色信号

        条件：
        1. 收盘价 > 布林上轨
        2. 涨幅 >= 3%
        3. 不是第二天确认信号（这里简化处理，只判断当日）

        Args:
            row: DataFrame的一行数据

        Returns:
            bool: 是否满足紫色信号条件
        """
        if pd.isna(row['boll_upper']):
            return False

        # 站上黄线
        above_upper = row['close'] > row['boll_upper']

        # 涨幅 >= 3%
        increase_rate = (row['close'] / row['boll_upper'] - 1)
        enough_increase = increase_rate >= 0.03

        return above_upper and enough_increase

    def check_arrow_signal(self, df, idx):
        """
        检查附图箭头信号

        条件：
        1. 主力资金、MA5、MA20 三线向上
        2. 主力资金突破前60日高点

        Args:
            df: 完整的DataFrame
            idx: 当前行的索引

        Returns:
            bool: 是否满足箭头信号条件
        """
        if idx < 1:
            return False

        row = df.iloc[idx]
        prev_row = df.iloc[idx - 1]

        # 检查必要列是否存在且不为NaN
        required_cols = ['main_fund', 'main_fund_ma5', 'main_fund_ma20']
        if any(pd.isna(row[col]) for col in required_cols):
            return False

        # 条件1：三线向上
        main_fund_up = row['main_fund'] > prev_row['main_fund']
        ma5_up = row['main_fund_ma5'] > prev_row['main_fund_ma5']
        ma20_up = row['main_fund_ma20'] > prev_row['main_fund_ma20']
        three_lines_up = main_fund_up and ma5_up and ma20_up

        # 条件2：突破60日高点
        if idx < 60:
            return False

        # 前60日最高资金（不包括当天）
        prev_60_high = df.iloc[idx-60:idx]['main_fund'].max()
        breakthrough_60d = row['main_fund'] > prev_60_high and prev_60_high != 0

        return three_lines_up and breakthrough_60d

    def generate_signals(self, df):
        """
        生成买入卖出信号

        Args:
            df: 股票数据DataFrame

        Returns:
            df: 添加了 'buy_signal', 'sell_signal' 列的DataFrame
        """
        df = df.copy()

        # 计算布林带
        df = self.calculate_bollinger_bands(df)

        # 计算主力资金流
        df = self.calculate_main_fund_flow(df)

        # 初始化信号列
        df['purple_signal'] = False
        df['arrow_signal'] = False
        df['buy_signal'] = False
        df['sell_signal'] = False

        # 逐行检查信号
        for idx in range(len(df)):
            # 主图紫色信号
            df.loc[df.index[idx], 'purple_signal'] = self.check_purple_signal(df.iloc[idx])

            # 附图箭头信号
            df.loc[df.index[idx], 'arrow_signal'] = self.check_arrow_signal(df, idx)

            # 买入信号：双信号同时满足
            df.loc[df.index[idx], 'buy_signal'] = (
                df.iloc[idx]['purple_signal'] and df.iloc[idx]['arrow_signal']
            )

        return df

    def check_sell_signal(self, current_price, buy_price):
        """
        检查是否触发卖出信号（止盈或止损）

        Args:
            current_price: 当前价格
            buy_price: 买入价格

        Returns:
            tuple: (是否卖出, 卖出原因)
        """
        if buy_price is None or buy_price <= 0:
            return False, None

        profit_rate = (current_price - buy_price) / buy_price

        # 止盈
        if profit_rate >= self.profit_target:
            return True, 'profit_target'

        # 止损
        if profit_rate <= -self.stop_loss:
            return True, 'stop_loss'

        return False, None


def test_strategy():
    """测试策略函数"""
    # 创建测试数据
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='D')

    data = {
        'trade_date': dates,
        'open': 10 + np.random.randn(200).cumsum() * 0.5,
        'high': 10 + np.random.randn(200).cumsum() * 0.5 + 0.5,
        'low': 10 + np.random.randn(200).cumsum() * 0.5 - 0.5,
        'close': 10 + np.random.randn(200).cumsum() * 0.5,
        'vol': np.random.randint(1000000, 10000000, 200)
    }

    df = pd.DataFrame(data)

    # 测试策略
    strategy = DoubleSignalStrategy()
    df = strategy.generate_signals(df)

    print("策略测试结果：")
    print(f"总交易日数: {len(df)}")
    print(f"紫色信号次数: {df['purple_signal'].sum()}")
    print(f"箭头信号次数: {df['arrow_signal'].sum()}")
    print(f"买入信号次数: {df['buy_signal'].sum()}")
    print("\n买入信号日期:")
    print(df[df['buy_signal']][['trade_date', 'close', 'main_fund']])


if __name__ == '__main__':
    test_strategy()
