# AKShare 数据接口配置
# AKShare是免费的，无需Token配置

import akshare as ak
import pandas as pd

class AKShareData:
    """AKShare数据接口封装"""
    
    def __init__(self):
        self.name = "AKShare免费数据接口"
    
    def get_stock_realtime(self):
        """获取股票实时行情"""
        return ak.stock_zh_a_spot_em()
    
    def get_stock_history(self, symbol, start_date, end_date):
        """获取股票历史数据"""
        return ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                start_date=start_date, end_date=end_date)
    
    def get_index_data(self, symbol, start_date, end_date):
        """获取指数数据"""
        return ak.index_zh_a_hist(symbol=symbol, period="daily",
                                start_date=start_date, end_date=end_date)

# 使用示例
if __name__ == "__main__":
    data_api = AKShareData()
    
    # 获取实时行情
    realtime = data_api.get_stock_realtime()
    print("实时行情前5只:")
    print(realtime.head())
    
    # 获取历史数据
    history = data_api.get_stock_history("000001", "20241201", "20241231")
    print("\n平安银行历史数据:")
    print(history.tail())
