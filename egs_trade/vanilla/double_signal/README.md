# 双信号策略回测系统

基于布林带紫色信号和主力资金箭头信号的量化交易回测系统。

## 📊 策略说明

### 买入条件（必须同时满足）

**1. 主图紫色信号**
- 当日收盘价站上布林上轨（中轨+1倍标准差）
- 涨幅 >= 3%
- 必须是当日首次突破（非第二天确认）

**2. 附图箭头信号**
- 主力资金、MA5、MA20 三线同时向上
- 主力资金突破前60日最高点

### 卖出条件（满足任一即可）

- 止盈：盈利达到 10%
- 止损：亏损达到 10%

### 资金管理

- 初始资金：10万元
- 仓位管理：满仓买入
- 交易单位：100股（1手）

---

## 📁 文件结构

```
double_signal/
├── back_tester.py          # 回测主程序
├── strategy.py             # 策略逻辑
├── conf/
│   └── double_signal.yaml  # 配置文件
├── run.sh                  # 运行脚本
└── README.md               # 说明文档
```

---

## 🚀 快速开始

### 方式一：使用脚本运行（推荐）

```bash
cd /Users/foxfire/Desktop/Zxl-AI/ai_quant_trade/egs_trade/vanilla/double_signal
./run.sh
```

### 方式二：直接运行Python

```bash
cd /Users/foxfire/Desktop/Zxl-AI/ai_quant_trade/egs_trade/vanilla/double_signal
python back_tester.py --config conf/double_signal.yaml
```

---

## ⚙️ 配置说明

编辑 `conf/double_signal.yaml` 可以修改以下参数：

### 数据配置

```yaml
data_condition:
  stock_lst:              # 股票列表
    - '000001.SZ'         # 平安银行
    - '600000.SH'         # 浦发银行

  start_time: 2024-01-01  # 开始日期
  end_time: 2025-10-27    # 结束日期
  csv_dir: ./data         # 数据目录
```

### 策略参数

```yaml
test_condition:
  capital: 100000            # 初始资金（元）
  bollinger_period: 20       # 布林带周期
  profit_target: 0.10        # 止盈比例（10%）
  stop_loss: 0.10            # 止损比例（10%）
```

### 交易成本

```yaml
order_cost:
  close_tax: 0.001           # 印花税 0.1%
  open_commission: 0.0003    # 买入佣金 0.03%
  close_commission: 0.0003   # 卖出佣金 0.03%
  min_commission: 5          # 最低佣金 5元
```

---

## 📊 数据准备

### 选项1：使用模拟数据（默认）

程序会自动生成模拟数据进行回测，无需额外配置。

### 选项2：使用真实数据

#### A. 使用 Tushare

1. 注册 Tushare 账号：https://tushare.pro/register
2. 获取 token
3. 修改 `back_tester.py` 中的数据加载逻辑

#### B. 使用 AKShare（免费）

```bash
pip install akshare
```

下载数据并保存为CSV：

```python
import akshare as ak

# 下载平安银行数据
df = ak.stock_zh_a_hist(symbol="000001",
                        start_date="20240101",
                        end_date="20251027")
df.to_csv('./data/000001.SZ.csv', index=False)
```

#### C. 使用通达信导出的CSV

将通达信导出的CSV文件放到 `./data/` 目录下，文件名格式：`股票代码.csv`

例如：
- `000001.SZ.csv`
- `600000.SH.csv`

---

## 📈 回测结果

运行后会显示：

### 汇总指标
- 初始资金 / 最终资金
- 总收益 / 收益率
- 交易次数
- 盈利次数 / 亏损次数
- 胜率
- 平均盈利 / 平均亏损
- 盈亏比

### 交易明细
- 每笔交易的日期、价格、数量
- 盈亏金额和比例
- 交易原因（买入信号、止盈、止损等）

---

## 🔧 进阶使用

### 测试单只股票

编辑 `conf/double_signal.yaml`：

```yaml
data_condition:
  stock_lst:
    - '600519.SH'  # 只测试贵州茅台
```

### 调整止盈止损

```yaml
test_condition:
  profit_target: 0.15  # 改为15%止盈
  stop_loss: 0.05      # 改为5%止损
```

### 修改布林带参数

```yaml
test_condition:
  bollinger_period: 30  # 改为30日布林带
```

---

## 🐛 常见问题

### Q1: 提示找不到模块

```bash
# 安装依赖
cd /Users/foxfire/Desktop/Zxl-AI/ai_quant_trade
pip install -r requirements.txt
```

### Q2: 没有交易信号

可能原因：
- 数据时间范围太短
- 策略条件过于严格
- 数据质量问题

解决：
- 延长回测时间范围
- 适当放宽策略条件
- 检查数据完整性

### Q3: 收益率为负

这是正常的，说明策略在该时间段表现不佳。可以：
- 优化策略参数
- 更换回测时间段
- 测试更多股票

---

## 📝 策略优化建议

1. **参数优化**
   - 使用网格搜索寻找最优布林带周期
   - 测试不同的止盈止损比例

2. **仓位管理**
   - 改为固定仓位（如每次30%）
   - 实现金字塔加仓

3. **风险控制**
   - 添加最大回撤限制
   - 实现动态止损

4. **信号优化**
   - 增加成交量确认
   - 添加市场环境判断

---

## 📞 支持

如有问题，请提Issue或联系开发者。

---

## 📄 许可证

Apache License 2.0
