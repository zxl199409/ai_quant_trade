# 🎯 AI量化交易选股完全指南

基于ai_quant_trade项目的选股工具使用手册

## 📋 目录
- [快速开始](#快速开始)
- [选股工具概览](#选股工具概览)
- [详细使用方法](#详细使用方法)
- [选股策略组合](#选股策略组合)
- [实战案例](#实战案例)
- [进阶技巧](#进阶技巧)

---

## 🚀 快速开始

### 环境准备
```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 确保依赖已安装
pip install -r requirements.txt

# 3. 测试数据连接
python -c "import akshare as ak; print('AKShare连接正常')"
```

### 30秒快速选股
```bash
# 启动AI投资助手
python china_stock_assistant.py

# 或者直接分析特定股票
python -c "
from china_stock_assistant import ChinaStockAssistant
assistant = ChinaStockAssistant()
assistant.analyze_stock('000001')  # 分析平安银行
"
```

---

## 🛠 选股工具概览

### 1️⃣ **AI投资助手** (推荐新手)
- **文件**: `china_stock_assistant.py`
- **特点**: 
  - ✅ 一键启动，界面友好
  - ✅ 技术指标自动分析
  - ✅ 综合评分系统
  - ✅ 支持批量分析
- **适用**: 技术分析选股

### 2️⃣ **机器学习选股** (推荐进阶)
- **位置**: `egs_alpha/auto_alpha/tsfresh/`
- **特点**:
  - 🤖 自动挖掘5000+因子
  - 📊 机器学习预测
  - 🎯 量化评分
- **适用**: 因子选股、趋势预测

### 3️⃣ **因子库选股** (推荐专业)
- **位置**: `egs_alpha/alpha_libs/`
- **包含**:
  - Alpha101经典因子
  - TA-Lib技术指标
  - StockStats统计因子
- **适用**: 多因子选股模型

### 4️⃣ **策略回测选股** (推荐验证)
- **位置**: `egs_trade/`
- **包含**:
  - 强化学习策略
  - 深度学习策略
  - 传统技术策略
- **适用**: 策略验证选股

---

## 📖 详细使用方法

### 方法一：AI投资助手选股

#### 🎯 单股分析
```python
from china_stock_assistant import ChinaStockAssistant

# 创建助手实例
assistant = ChinaStockAssistant()

# 分析单只股票
result = assistant.analyze_stock('000001')  # 平安银行
print(f"投资建议: {result['recommendation']}")
print(f"技术评分: {result['score']}/5.0")
```

#### 🎯 批量选股
```python
# 批量分析多只股票
stocks = ['000001', '000002', '600036', '600519']
results = []

for stock in stocks:
    result = assistant.analyze_stock(stock)
    if result:
        results.append(result)

# 按评分排序
results.sort(key=lambda x: x['score'], reverse=True)

# 输出前3名
print("🏆 推荐股票TOP3:")
for i, stock in enumerate(results[:3], 1):
    print(f"{i}. {stock['name']} - 评分: {stock['score']:.1f}")
```

#### 🎯 行业选股
```python
# 获取特定行业股票
def get_industry_stocks(industry_keyword):
    """根据行业关键词筛选股票"""
    stock_list = ak.stock_zh_a_spot_em()
    industry_stocks = stock_list[
        stock_list['名称'].str.contains(industry_keyword, na=False)
    ]
    return industry_stocks['代码'].tolist()

# 分析银行股
bank_stocks = get_industry_stocks('银行')
bank_results = []

for stock in bank_stocks[:10]:  # 分析前10只
    result = assistant.analyze_stock(stock)
    if result and result['score'] > 2:  # 只要评分>2的
        bank_results.append(result)

print("🏦 优质银行股推荐:")
for stock in sorted(bank_results, key=lambda x: x['score'], reverse=True):
    print(f"• {stock['name']}: {stock['score']:.1f}分")
```

### 方法二：机器学习选股

#### 🤖 TSFresh因子挖掘选股
```bash
# 进入机器学习选股目录
cd egs_alpha/auto_alpha/tsfresh/

# 运行因子挖掘
python factor_mining.py

# 查看结果
python stock_prediction.py
```

#### 📊 自定义因子选股
```python
# 使用项目中的因子库
import sys
sys.path.append('egs_alpha/alpha_libs/alpha101')

from alpha101_factors import Alpha101

# 创建因子计算器
alpha = Alpha101()

# 计算Alpha001因子
factor_data = alpha.alpha001(stock_data)

# 根据因子值选股
top_stocks = factor_data.nlargest(10)  # 选择因子值最大的10只股票
```

### 方法三：技术指标选股

#### 📈 使用TA-Lib选股
```python
import talib
import akshare as ak

def technical_screening():
    """技术指标选股"""
    # 获取股票列表
    stock_list = ak.stock_zh_a_spot_em()
    selected_stocks = []
    
    for _, stock in stock_list.head(100).iterrows():  # 分析前100只
        try:
            # 获取历史数据
            data = ak.stock_zh_a_hist(
                symbol=stock['代码'], 
                period="daily", 
                adjust="qfq"
            )
            
            if len(data) < 30:
                continue
                
            # 计算技术指标
            close = data['收盘'].values
            rsi = talib.RSI(close, timeperiod=14)
            macd, signal, hist = talib.MACD(close)
            
            # 选股条件
            if (rsi[-1] > 30 and rsi[-1] < 70 and  # RSI不超买不超卖
                macd[-1] > signal[-1] and  # MACD金叉
                close[-1] > close[-5]):  # 价格上涨
                
                selected_stocks.append({
                    'code': stock['代码'],
                    'name': stock['名称'],
                    'price': close[-1],
                    'rsi': rsi[-1]
                })
                
        except Exception as e:
            continue
    
    return selected_stocks

# 执行技术选股
tech_stocks = technical_screening()
print(f"技术面选出 {len(tech_stocks)} 只股票")
```

---

## 🎯 选股策略组合

### 策略一：稳健型选股
```python
def conservative_selection():
    """稳健型选股策略"""
    criteria = {
        'rsi_range': (30, 70),      # RSI适中
        'ma_trend': 'up',           # 均线向上
        'volume_ratio': (0.8, 2.0), # 成交量正常
        'score_min': 2.0            # 技术评分≥2
    }
    
    # 实施选股逻辑
    # ...
    
    return selected_stocks
```

### 策略二：成长型选股
```python
def growth_selection():
    """成长型选股策略"""
    criteria = {
        'price_momentum': 0.1,      # 近期涨幅>10%
        'volume_surge': 1.5,        # 成交量放大
        'macd_signal': 'golden',    # MACD金叉
        'score_min': 1.5            # 技术评分≥1.5
    }
    
    # 实施选股逻辑
    # ...
    
    return selected_stocks
```

### 策略三：价值型选股
```python
def value_selection():
    """价值型选股策略"""
    criteria = {
        'pe_ratio': (0, 20),        # 市盈率<20
        'pb_ratio': (0, 2),         # 市净率<2
        'rsi_oversold': 40,         # RSI偏低
        'support_level': True       # 接近支撑位
    }
    
    # 实施选股逻辑
    # ...
    
    return selected_stocks
```

---

## 💡 实战案例

### 案例1：寻找反弹机会
```python
def find_rebound_opportunities():
    """寻找超跌反弹机会"""
    assistant = ChinaStockAssistant()
    
    # 筛选条件
    conditions = {
        'rsi_oversold': 30,         # RSI超卖
        'price_drop': -0.2,         # 近期下跌20%
        'volume_normal': True,      # 成交量正常
        'support_near': True        # 接近支撑位
    }
    
    candidates = []
    stock_list = ak.stock_zh_a_spot_em()
    
    for _, stock in stock_list.head(200).iterrows():
        result = assistant.analyze_stock(stock['代码'])
        
        if (result and 
            result['rsi'] < 35 and 
            result['recent_20d'] < -15):
            candidates.append(result)
    
    # 按技术评分排序
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print("🔥 超跌反弹候选股:")
    for stock in candidates[:5]:
        print(f"• {stock['name']}: RSI={stock['rsi']:.1f}, 评分={stock['score']:.1f}")
    
    return candidates

# 执行反弹选股
rebound_stocks = find_rebound_opportunities()
```

### 案例2：强势股追踪
```python
def track_strong_stocks():
    """追踪强势股"""
    assistant = ChinaStockAssistant()
    
    strong_stocks = []
    stock_list = ak.stock_zh_a_spot_em()
    
    for _, stock in stock_list.head(300).iterrows():
        result = assistant.analyze_stock(stock['代码'])
        
        if (result and 
            result['score'] >= 2.5 and 
            result['recent_20d'] > 20 and
            result['rsi'] < 75):  # 强势但未超买
            strong_stocks.append(result)
    
    # 按近期表现排序
    strong_stocks.sort(key=lambda x: x['recent_20d'], reverse=True)
    
    print("🚀 强势股排行:")
    for i, stock in enumerate(strong_stocks[:10], 1):
        print(f"{i}. {stock['name']}: +{stock['recent_20d']:.1f}% (评分{stock['score']:.1f})")
    
    return strong_stocks

# 执行强势股追踪
strong_stocks = track_strong_stocks()
```

---

## 🔧 进阶技巧

### 1. 自定义选股函数
```python
def custom_stock_screener(conditions):
    """自定义选股器"""
    assistant = ChinaStockAssistant()
    results = []
    
    # 获取股票池
    stock_pool = get_stock_pool(conditions.get('market', 'all'))
    
    for stock_code in stock_pool:
        result = assistant.analyze_stock(stock_code)
        
        if result and meets_conditions(result, conditions):
            results.append(result)
    
    return sorted(results, key=lambda x: x['score'], reverse=True)

# 使用示例
my_conditions = {
    'score_min': 2.0,
    'rsi_range': (40, 65),
    'volume_ratio_min': 1.2,
    'price_trend': 'up'
}

selected = custom_stock_screener(my_conditions)
```

### 2. 多时间框架分析
```python
def multi_timeframe_analysis(stock_code):
    """多时间框架分析"""
    timeframes = ['daily', 'weekly', 'monthly']
    results = {}
    
    for tf in timeframes:
        # 获取不同周期数据
        data = get_stock_data(stock_code, period=tf)
        
        # 计算技术指标
        indicators = calculate_indicators(data)
        
        # 评估趋势
        trend = evaluate_trend(indicators)
        
        results[tf] = {
            'trend': trend,
            'strength': calculate_strength(indicators),
            'signals': generate_signals(indicators)
        }
    
    return results
```

### 3. 组合优化选股
```python
def portfolio_optimization_selection(target_stocks, weights=None):
    """基于组合优化的选股"""
    import numpy as np
    from scipy.optimize import minimize
    
    # 获取历史收益率数据
    returns = get_returns_matrix(target_stocks)
    
    # 计算协方差矩阵
    cov_matrix = returns.cov()
    
    # 优化目标函数
    def objective(weights):
        portfolio_return = np.sum(returns.mean() * weights)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -portfolio_return / portfolio_risk  # 最大化夏普比率
    
    # 约束条件
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 0.3) for _ in range(len(target_stocks)))  # 单只股票不超过30%
    
    # 执行优化
    result = minimize(objective, 
                     x0=np.array([1/len(target_stocks)] * len(target_stocks)),
                     method='SLSQP',
                     bounds=bounds,
                     constraints=constraints)
    
    # 返回优化后的权重
    optimal_weights = result.x
    
    return dict(zip(target_stocks, optimal_weights))
```

---

## 📊 选股结果评估

### 回测验证
```python
def backtest_selection(selected_stocks, start_date, end_date):
    """回测选股结果"""
    portfolio_returns = []
    
    for stock in selected_stocks:
        # 获取历史数据
        data = ak.stock_zh_a_hist(
            symbol=stock['code'],
            start_date=start_date,
            end_date=end_date
        )
        
        # 计算收益率
        returns = data['收盘'].pct_change().dropna()
        portfolio_returns.append(returns)
    
    # 等权重组合
    portfolio = pd.concat(portfolio_returns, axis=1).mean(axis=1)
    
    # 计算绩效指标
    total_return = (1 + portfolio).prod() - 1
    annual_return = (1 + total_return) ** (252 / len(portfolio)) - 1
    volatility = portfolio.std() * np.sqrt(252)
    sharpe_ratio = annual_return / volatility
    
    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio
    }
```

---

## ⚠️ 注意事项

### 数据质量
- 确保网络连接稳定
- 定期更新数据源
- 处理缺失数据

### 风险控制
- 分散投资，避免集中持股
- 设置止损位
- 定期复盘调整

### 策略优化
- 持续监控选股效果
- 根据市场变化调整参数
- 结合基本面分析

---

## 🎯 总结

ai_quant_trade项目为您提供了完整的选股工具链：

1. **新手推荐**: 使用AI投资助手快速上手
2. **进阶用户**: 结合机器学习和因子库
3. **专业投资者**: 自定义策略和组合优化

记住：**选股只是投资的第一步，风险控制和资金管理同样重要！**

---

## 🎯 实战分析案例记录

### 案例1：30万短线投资完整分析流程 (2025-07-13)

#### 📊 投资者需求
- **资金规模**: 30万人民币
- **投资风格**: 短线交易
- **风险偏好**: 能接受较少回撤
- **板块偏好**: 创业板优先
- **收益目标**: 快速获利

#### 🛠️ 使用的分析脚本

##### 1. 基础选股脚本
```bash
# 激活环境
source venv/bin/activate

# 运行智能选股系统
python smart_stock_screener.py
```

##### 2. 多指标分析脚本
```python
# 多指标综合分析
python -c "
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MultiIndicatorAnalyzer:
    def calculate_all_indicators(self, df):
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

# 使用示例
analyzer = MultiIndicatorAnalyzer()
# 分析目标股票...
"
```

##### 3. 基本面分析脚本
```python
# 基本面与技术面结合分析
python -c "
# 分析业绩风险和中报时间
stocks_analysis = {
    '300142': {
        'name': '沃森生物',
        'business': '疫苗研发生产',
        'risks': ['新冠疫苗需求下降', '研发投入大', '监管严格'],
        'advantages': ['技术壁垒高', '产品管线丰富']
    },
    '300782': {
        'name': '卓胜微', 
        'business': '射频芯片设计',
        'risks': ['半导体周期下行', '研发占比高', '客户集中'],
        'advantages': ['5G需求增长', '技术实力强']
    }
}

# 中报时间安排
midyear_report_schedule = {
    'disclosure_period': '2025年7月1日-8月31日',
    'forecast_period': '7月15日前',
    'peak_period': '7月20日-8月10日'
}
"
```

#### 📈 分析结果记录

##### 技术面TOP10股票
| 排名 | 股票名称 | 代码 | 评分 | RSI | 主要信号 |
|------|----------|------|------|-----|----------|
| 1 | 沃森生物 | 300142 | 6.6 | 65.2 | 多头排列+RSI健康 |
| 2 | 东方财富 | 300059 | 6.3 | 72.9 | 多头排列+成交量放大 |
| 3 | 智飞生物 | 300122 | 6.3 | 74.7 | 多头排列+RSI偏高 |
| 4 | 爱尔眼科 | 300015 | 6.0 | 70.2 | 多头排列+RSI偏高 |
| 5 | 立讯精密 | 002475 | 5.8 | 68.8 | 多头排列+RSI正常 |
| 6 | 卓胜微 | 300782 | 5.8 | 63.2 | 多头排列+RSI最佳 |

##### 多指标分析结果
- **沃森生物**: 技术评分4.5/5.0，MACD金叉，但布林带91.5%位置偏高
- **卓胜微**: 技术评分4.0/5.0，RSI最健康(63.2)，各项指标均衡
- **东方财富**: 技术评分3.0/5.0，成交量大增(量比2.33)，但RSI超买

##### 基本面风险识别
- **沃森生物**: 新冠疫苗需求下降，研发投入大
- **卓胜微**: 半导体周期下行，研发占比高
- **关键时点**: 7月15日前业绩预告，需要关注

#### 🎯 最终投资组合调整

##### 修正前组合 (纯技术面)
- 核心持仓60%：沃森生物15% + 东方财富12% + 其他
- 机会仓位30%：其他技术面标的
- 现金储备10%

##### 修正后组合 (技术面+基本面)
- **核心稳健仓位50%**: 招商银行17% + 海康威视13% + 立讯精密10% + 东方财富10%
- **技术面机会仓位30%**: 沃森生物8% + 卓胜微8% + 爱尔眼科7% + 圣邦股份7%
- **现金储备20%**: 等待中报明朗

#### 📋 操作时间表
- **7月13-20日**: 适当减仓风险标的
- **7月20日-8月10日**: 关注中报披露
- **8月10-31日**: 根据业绩调整仓位
- **9月份**: 重新评估投资组合

#### 💡 关键经验总结

##### ✅ 成功要点
1. **多指标验证**: 不依赖单一RSI指标，结合MACD、KDJ、布林带等
2. **基本面检查**: 技术面强势不等于基本面健康
3. **时间节点**: 关注财报季等关键时点
4. **风险控制**: 适当降低风险标的权重，提高现金比例

##### ⚠️ 风险提醒
1. **技术陷阱**: RSI健康但基本面有问题的股票需谨慎
2. **时间风险**: 财报季前后需要调整策略
3. **仓位管理**: 单只股票权重不宜过高
4. **止损纪律**: 严格执行技术止损和基本面止损

#### 🔧 实用脚本模板

##### 快速多指标分析模板
```python
def quick_multi_indicator_analysis(symbol, name):
    # 获取数据
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
    
    # 计算指标
    df = calculate_all_indicators(df)
    latest = df.iloc[-1]
    
    # 综合评分
    score = 0
    if latest['收盘'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
        score += 2
    if 30 <= latest['RSI'] <= 70:
        score += 1
    if latest['MACD'] > latest['MACD_signal']:
        score += 1
    if 20 <= latest['BB_position'] <= 80:
        score += 0.5
        
    return {
        'name': name,
        'price': latest['收盘'],
        'rsi': latest['RSI'],
        'score': score,
        'recommendation': '买入' if score >= 3 else '观望'
    }
```

##### 基本面风险检查模板
```python
def fundamental_risk_check(symbol):
    risk_factors = {
        '300142': ['疫苗需求下降', '研发投入大'],
        '300782': ['半导体周期', '客户集中'],
        # 添加更多股票的风险因子
    }
    
    return risk_factors.get(symbol, ['需要进一步研究'])
```

---

*最后更新: 2025-07-13*
*版本: v2.0 - 新增实战案例*
