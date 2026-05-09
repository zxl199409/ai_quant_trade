#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI量化交易项目配置文件模板
请复制此文件为 config.py 并填入您的API密钥
"""

# ================================
# 数据源API配置
# ================================

# Tushare API Token (中国A股数据)
# 注册地址: https://tushare.pro/register
TUSHARE_TOKEN = "your_tushare_token_here"

# Alpha Vantage API Key (美股数据)
# 注册地址: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key_here"

# Quandl API Key (金融数据)
# 注册地址: https://www.quandl.com/
QUANDL_API_KEY = "your_quandl_key_here"

# ================================
# 交易相关配置
# ================================

# 初始资金
INITIAL_CAPITAL = 100000

# 手续费率
COMMISSION_RATE = 0.0003

# 滑点
SLIPPAGE = 0.001

# ================================
# 回测配置
# ================================

# 回测开始日期
BACKTEST_START_DATE = "2020-01-01"

# 回测结束日期
BACKTEST_END_DATE = "2023-12-31"

# 基准指数 (沪深300: '000300.SH', 标普500: '^GSPC')
BENCHMARK = "000300.SH"

# ================================
# 风险管理配置
# ================================

# 最大回撤限制
MAX_DRAWDOWN = 0.2

# 单只股票最大仓位
MAX_POSITION_PER_STOCK = 0.1

# 止损比例
STOP_LOSS_RATIO = 0.05

# 止盈比例
TAKE_PROFIT_RATIO = 0.15

# ================================
# 使用说明
# ================================
"""
1. 将此文件复制为 config.py
2. 填入您的API密钥
3. 根据需要调整其他配置参数
4. 在策略代码中导入: from config import TUSHARE_TOKEN

注意: config.py 文件已被添加到 .gitignore，不会被提交到版本控制
"""
