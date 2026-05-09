#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI量化交易项目环境搭建
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import akshare as ak

def test_basic_imports():
    """测试基础包导入"""
    print("✅ 测试基础包导入...")
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        print("   - pandas, numpy, matplotlib 导入成功")
        
        import sklearn
        print("   - scikit-learn 导入成功")
        
        import mplfinance as mpf
        print("   - mplfinance 导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 基础包导入失败: {e}")
        return False

def test_data_sources():
    """测试数据源"""
    print("\n✅ 测试数据源...")
    
    # 测试yfinance
    try:
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="5d")
        if not data.empty:
            print("   - yfinance (Yahoo Finance) 数据获取成功")
        else:
            print("   ⚠️ yfinance 数据为空")
    except Exception as e:
        print(f"   ❌ yfinance 测试失败: {e}")
    
    # 测试akshare
    try:
        # 获取A股实时行情
        stock_info = ak.stock_zh_a_spot_em()
        if not stock_info.empty:
            print("   - akshare (A股数据) 获取成功")
            print(f"     获取到 {len(stock_info)} 只股票数据")
        else:
            print("   ⚠️ akshare 数据为空")
    except Exception as e:
        print(f"   ❌ akshare 测试失败: {e}")

def test_quant_brain():
    """测试量化核心模块"""
    print("\n✅ 测试量化核心模块...")
    try:
        # 测试导入核心模块
        sys.path.append('/Users/foxfire/Desktop/Zxl-AI/ai_quant_trade')
        from quant_brain.data_io import data_loader
        print("   - quant_brain.data_io 导入成功")
        
        from quant_brain.back_test import back_tester
        print("   - quant_brain.back_test 导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 量化核心模块导入失败: {e}")
        return False

def create_simple_example():
    """创建一个简单的示例"""
    print("\n✅ 创建简单的量化示例...")
    try:
        # 获取苹果股票数据
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="1mo")
        
        # 计算简单移动平均线
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        
        # 生成交易信号
        data['Signal'] = 0
        data.loc[data['MA5'] > data['MA20'], 'Signal'] = 1  # 买入信号
        data.loc[data['MA5'] < data['MA20'], 'Signal'] = -1  # 卖出信号
        
        print("   - 成功创建双均线策略示例")
        print(f"   - 数据时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")
        print(f"   - 买入信号数量: {len(data[data['Signal'] == 1])}")
        print(f"   - 卖出信号数量: {len(data[data['Signal'] == -1])}")
        
        return True
    except Exception as e:
        print(f"   ❌ 示例创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 AI量化交易项目环境测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # 测试基础包
    if test_basic_imports():
        success_count += 1
    
    # 测试数据源
    test_data_sources()  # 这个测试不计入成功率，因为可能受网络影响
    
    # 测试量化核心模块
    if test_quant_brain():
        success_count += 1
    
    # 创建简单示例
    if create_simple_example():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 测试完成: {success_count}/{total_tests-1} 项测试通过")
    
    if success_count >= 2:
        print("✅ 环境搭建成功！您可以开始使用AI量化交易项目了。")
        print("\n📚 建议下一步:")
        print("   1. 查看 egs_trade/vanilla/double_ma 目录下的双均线策略")
        print("   2. 配置 tushare token (如需要中国A股数据)")
        print("   3. 探索 egs_alpha 目录下的因子挖掘功能")
        print("   4. 尝试 egs_llm 目录下的大模型应用")
    else:
        print("❌ 环境搭建存在问题，请检查依赖安装。")

if __name__ == "__main__":
    main()
