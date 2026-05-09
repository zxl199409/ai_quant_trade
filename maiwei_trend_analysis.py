#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迈为股份资金流向趋势分析（基于汇总数据推算）
"""

print("=" * 100)
print("迈为股份 (300751) 资金流向趋势分析")
print("=" * 100)
print("基于今日、3日、5日、10日的汇总数据进行推算")
print("=" * 100)

# 已知数据（单位：万元）
today_main = 5796.10
day3_main = None  # 需要获取
day5_main = -1206.86
day10_main = 46360.22

today_super = 2535.68
day5_super = -6347.95
day10_super = 43550.53

today_big = 3260.42
day5_big = 5141.08
day10_big = 2809.69

print("\n【已知数据汇总】\n")
print(f"今日主力净流入: {today_main:>10.2f}万元 ✅")
print(f"5日主力净流入: {day5_main:>10.2f}万元 ❌")
print(f"10日主力净流入: {day10_main:>10.2f}万元 ✅")
print()
print(f"今日超大单: {today_super:>10.2f}万元 ✅")
print(f"5日超大单: {day5_super:>10.2f}万元 ❌")
print(f"10日超大单: {day10_super:>10.2f}万元 ✅")
print()
print(f"今日大单: {today_big:>10.2f}万元 ✅")
print(f"5日大单: {day5_big:>10.2f}万元 ✅")
print(f"10日大单: {day10_big:>10.2f}万元 ✅")

print("\n" + "=" * 100)
print("【推算分析】\n")

# 推算近4日（昨天到第4天）的资金流向
recent_4days_main = day5_main - today_main
recent_4days_super = day5_super - today_super
recent_4days_big = day5_big - today_big

print("1. 近4日（昨天到第4天）推算:")
print(f"   主力净流入: {recent_4days_main:.2f}万元")
print(f"   超大单净流入: {recent_4days_super:.2f}万元")
print(f"   大单净流入: {recent_4days_big:.2f}万元")

if recent_4days_main < 0:
    print(f"   👉 前4天主力累计流出{abs(recent_4days_main):.0f}万元")
else:
    print(f"   👉 前4天主力累计流入{recent_4days_main:.0f}万元")

# 推算第6-10日的资金流向
day6_to_10_main = day10_main - day5_main
day6_to_10_super = day10_super - day5_super
day6_to_10_big = day10_big - day5_big

print("\n2. 第6-10日推算:")
print(f"   主力净流入: {day6_to_10_main:.2f}万元")
print(f"   超大单净流入: {day6_to_10_super:.2f}万元")
print(f"   大单净流入: {day6_to_10_big:.2f}万元")

if day6_to_10_main > 0:
    print(f"   👉 第6-10日主力累计流入{day6_to_10_main:.0f}万元")
else:
    print(f"   👉 第6-10日主力累计流出{abs(day6_to_10_main):.0f}万元")

print("\n" + "=" * 100)
print("【资金流向时间轴分析】\n")

print("时间段分解:")
print(f"  第6-10日: 主力流入 {day6_to_10_main:>10.2f}万元  (5天前到10天前)")
print(f"  第2-5日:  主力流出 {recent_4days_main:>10.2f}万元  (昨天到第4天)")
print(f"  今日:     主力流入 {today_main:>10.2f}万元  (今天)")
print("  " + "-" * 60)
print(f"  5日累计:  主力 {day5_main:>10.2f}万元")
print(f"  10日累计: 主力 {day10_main:>10.2f}万元")

print("\n" + "=" * 100)
print("【趋势判断】\n")

print("📊 资金流向三阶段:")
print()
print("阶段1: 第6-10日（一周前）")
if day6_to_10_main > 40000:
    print(f"   ✅ 主力大举流入 {day6_to_10_main:.0f}万元")
    print(f"   ✅ 超大单流入 {day6_to_10_super:.0f}万元")
    print("   💡 这是主力大规模建仓阶段")
else:
    print(f"   主力流入 {day6_to_10_main:.0f}万元")

print()
print("阶段2: 第2-5日（昨天到4天前）")
if recent_4days_main < 0:
    print(f"   ⚠️  主力流出 {abs(recent_4days_main):.0f}万元")
    print(f"   ⚠️  超大单流出 {abs(recent_4days_super):.0f}万元")
    if recent_4days_big > 0:
        print(f"   ✅ 但大单流入 {recent_4days_big:.0f}万元")
        print("   💡 机构在减仓，但大户在接盘")
    else:
        print("   💡 这是洗盘或调整阶段")
else:
    print(f"   主力流入 {recent_4days_main:.0f}万元")

print()
print("阶段3: 今日")
print(f"   ✅ 主力流入 {today_main:.0f}万元")
print(f"   ✅ 超大单流入 {today_super:.0f}万元")
print(f"   ✅ 大单流入 {today_big:.0f}万元")
print("   💡 今日主力重新大举流入！")

print("\n" + "=" * 100)
print("【综合结论】\n")

print("资金流向路径:")
print("  第6-10日 → 主力大举建仓 (流入4.76亿)")
print("       ↓")
print("  第2-5日  → 短期洗盘调整 (流出0.70亿)")
print("       ↓")
print("  今日     → 主力重新流入 (流入0.58亿)")
print()

print("💡 核心结论:")
print("  1. 10日维度：主力累计流入4.64亿，趋势向好 ✅")
print("  2. 5日维度：近期有调整，累计小幅流出1207万 ⚠️")
print("  3. 今日表现：主力重新大举流入5796万 ✅")
print()
print("  综合判断：")
print("  👉 第6-10日是主力大规模建仓期（流入4.76亿）")
print("  👉 第2-5日是洗盘调整期（流出0.70亿，洗掉了约15%的筹码）")
print("  👉 今日是重新吸筹期（流入0.58亿，主力回来了！）")
print()
print("  📈 操作建议：")
print("  ✅ 主力建仓逻辑完整：大举建仓 → 洗盘 → 继续吸筹")
print("  ✅ 今日逆势流入说明主力看好后市")
print("  ✅ 建议继续持有，等待主力拉升")
print("  ⚠️  设置止损位144元（-15%），控制风险")

print("\n" + "=" * 100)
print("风险提示：以上分析基于资金流向数据推算，仅供参考")
print("=" * 100)
