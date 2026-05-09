#!/bin/bash

# AI量化交易项目启动脚本
echo "🚀 启动AI量化交易环境..."

# 进入项目目录
cd /Users/foxfire/Desktop/Zxl-AI/ai_quant_trade

# 激活虚拟环境
source venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "📍 当前目录: $(pwd)"
echo "🐍 Python版本: $(python --version)"

echo ""
echo "🎯 可用的示例:"
echo "   1. 双均线策略: cd egs_trade/vanilla/double_ma"
echo "   2. 强化学习策略: cd egs_trade/rl"
echo "   3. 因子挖掘: cd egs_alpha"
echo "   4. 大模型应用: cd egs_llm"
echo "   5. 数据获取: cd egs_data"

echo ""
echo "💡 使用提示:"
echo "   - 运行 'python test_setup.py' 测试环境"
echo "   - 查看 README.md 了解更多信息"
echo "   - 退出环境请输入 'deactivate'"

# 启动交互式shell
exec bash
