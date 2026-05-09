#!/bin/bash
# 双信号策略回测运行脚本

echo "=================================="
echo "  双信号策略回测系统"
echo "=================================="
echo ""

# 激活虚拟环境（如果有的话）
if [ -d "../../../venv" ]; then
    source ../../../venv/bin/activate
    echo "✓ 已激活虚拟环境"
fi

# 运行回测
python back_tester.py --config conf/double_signal.yaml

echo ""
echo "=================================="
echo "  回测完成"
echo "=================================="
