# -*- coding: utf-8 -*-
"""
数据下载工具

使用 AKShare 免费下载A股数据
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime

try:
    import akshare as ak
    print("✓ AKShare 已安装")
except ImportError:
    print("❌ 未安装 AKShare")
    print("请运行: pip install akshare")
    sys.exit(1)


def download_stock_data(stock_code, start_date, end_date, save_dir='./data'):
    """
    下载单只股票数据

    Args:
        stock_code: 股票代码，如 '000001.SZ'
        start_date: 开始日期，格式 'YYYY-MM-DD'
        end_date: 结束日期，格式 'YYYY-MM-DD'
        save_dir: 保存目录
    """
    # 转换股票代码格式（去掉市场后缀）
    if '.' in stock_code:
        symbol = stock_code.split('.')[0]
    else:
        symbol = stock_code

    print(f"\n下载 {stock_code} 数据...")
    print(f"时间范围: {start_date} 至 {end_date}")

    try:
        # 转换日期格式（AKShare需要YYYYMMDD格式）
        start_date_fmt = start_date.replace('-', '')
        end_date_fmt = end_date.replace('-', '')

        # 下载数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date_fmt,
            end_date=end_date_fmt,
            adjust="qfq"  # 前复权
        )

        if df is None or len(df) == 0:
            print(f"❌ 未获取到 {stock_code} 的数据")
            return False

        # 重命名列以匹配回测程序格式
        df = df.rename(columns={
            '日期': 'trade_date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'vol'
        })

        # 只保留需要的列
        required_cols = ['trade_date', 'open', 'high', 'low', 'close', 'vol']
        df = df[required_cols]

        # 确保数据类型正确
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        for col in ['open', 'high', 'low', 'close', 'vol']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 删除包含NaN的行
        df = df.dropna()

        # 保存文件
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{stock_code}.csv")
        df.to_csv(file_path, index=False)

        print(f"✓ 成功下载 {len(df)} 条数据")
        print(f"✓ 保存至: {file_path}")

        return True

    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("A股数据下载工具（基于AKShare）")
    print("=" * 60)

    # 读取配置文件
    config_path = 'conf/double_signal.yaml'

    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return

    with open(config_path, 'r', encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    data_config = config['data_condition']
    stock_list = data_config['stock_lst']
    start_date = data_config['start_time']
    end_date = data_config['end_time']
    save_dir = data_config.get('csv_dir', './data')

    print(f"\n配置信息:")
    print(f"  股票数量: {len(stock_list)}")
    print(f"  时间范围: {start_date} 至 {end_date}")
    print(f"  保存目录: {save_dir}")

    # 下载所有股票数据
    success_count = 0
    for stock_code in stock_list:
        if download_stock_data(stock_code, start_date, end_date, save_dir):
            success_count += 1

    print(f"\n" + "=" * 60)
    print(f"下载完成!")
    print(f"成功: {success_count}/{len(stock_list)}")
    print(f"=" * 60)

    if success_count == len(stock_list):
        print("\n✓ 所有数据下载成功，可以开始回测了！")
        print("运行命令: python3 back_tester.py --config conf/double_signal.yaml")
    else:
        print("\n⚠️  部分数据下载失败，请检查股票代码是否正确")


if __name__ == '__main__':
    main()
