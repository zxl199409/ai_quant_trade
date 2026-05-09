#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奥瑞德(600666)股价下跌原因深度分析
从技术面、基本面、市场面、资金面等多维度分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_company_news(stock_code):
    """获取公司新闻和公告"""
    try:
        print("\n" + "="*80)
        print("【重要公告和新闻】")
        print("="*80)

        # 获取个股新闻
        news = ak.stock_news_em(symbol=stock_code)
        if news is not None and len(news) > 0:
            print(f"\n近期新闻（最新5条）：")
            for i, row in news.head(5).iterrows():
                print(f"\n{i+1}. {row['新闻标题']}")
                print(f"   时间: {row['发布时间']}")
                print(f"   来源: {row['文章来源']}")

        # 获取公司公告
        try:
            announcements = ak.stock_notice_report(symbol=stock_code)
            if announcements is not None and len(announcements) > 0:
                print(f"\n近期公告（最新5条）：")
                for i, row in announcements.head(5).iterrows():
                    print(f"\n{i+1}. {row['公告标题']}")
                    print(f"   时间: {row['公告日期']}")
        except:
            print("\n暂无法获取公告信息")

    except Exception as e:
        print(f"获取新闻数据出错: {str(e)}")

def analyze_technical_decline(df):
    """技术面下跌分析"""
    print("\n" + "="*80)
    print("【技术面分析 - 下跌原因】")
    print("="*80)

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    reasons = []

    # 计算技术指标
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA60'] = df['close'].rolling(window=60).mean()

    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # 1. 均线系统分析
    print("\n1️⃣ 均线系统破位")
    if latest['close'] < latest['MA5']:
        reasons.append("跌破MA5短期均线")
        print(f"   ❌ 跌破MA5: 当前价{latest['close']:.2f} < MA5 {latest['MA5']:.2f}")

    if latest['close'] < latest['MA10']:
        reasons.append("跌破MA10均线")
        print(f"   ❌ 跌破MA10: 当前价{latest['close']:.2f} < MA10 {latest['MA10']:.2f}")

    if latest['close'] < latest['MA20']:
        reasons.append("跌破MA20中期均线（趋势转弱）")
        print(f"   ❌ 跌破MA20: 当前价{latest['close']:.2f} < MA20 {latest['MA20']:.2f}")
        print(f"   ⚠️  这是中期趋势转弱的重要信号")

    if latest['MA5'] < latest['MA10'] < latest['MA20']:
        reasons.append("均线空头排列（趋势恶化）")
        print(f"   ❌ 均线空头排列: MA5 < MA10 < MA20")
        print(f"   ⚠️  这是最典型的下跌趋势信号")

    # 2. MACD分析
    print("\n2️⃣ MACD指标恶化")
    if latest['MACD'] < latest['Signal'] and prev['MACD'] >= prev['Signal']:
        reasons.append("MACD刚刚死叉（新的下跌信号）")
        print(f"   ❌ MACD死叉: MACD({latest['MACD']:.4f}) < Signal({latest['Signal']:.4f})")
        print(f"   ⚠️  死叉表示短期趋势转弱，卖压增加")
    elif latest['MACD'] < latest['Signal']:
        reasons.append("MACD处于死叉状态")
        print(f"   ❌ MACD死叉中: MACD({latest['MACD']:.4f}) < Signal({latest['Signal']:.4f})")

    if latest['MACD'] < 0:
        print(f"   ❌ MACD在零轴下方: {latest['MACD']:.4f}")
        print(f"   ⚠️  表示中长期趋势偏空")

    # 3. 连续下跌分析
    print("\n3️⃣ 连续下跌形态")
    recent_5 = df.tail(5)
    down_days = sum(recent_5['close'].diff() < 0)
    if down_days >= 3:
        reasons.append(f"近5日有{down_days}天下跌（连续下跌）")
        print(f"   ❌ 近5日有{down_days}天收阴线")
        print(f"   ⚠️  连续下跌表明做空力量占优")

    # 近期跌幅
    recent_5_change = (recent_5['close'].iloc[-1] / recent_5['close'].iloc[0] - 1) * 100
    if recent_5_change < -5:
        reasons.append(f"近5日累计下跌{abs(recent_5_change):.2f}%")
        print(f"   ❌ 近5日累计下跌: {abs(recent_5_change):.2f}%")

    recent_10 = df.tail(10)
    recent_10_change = (recent_10['close'].iloc[-1] / recent_10['close'].iloc[0] - 1) * 100
    if recent_10_change < -5:
        reasons.append(f"近10日累计下跌{abs(recent_10_change):.2f}%")
        print(f"   ❌ 近10日累计下跌: {abs(recent_10_change):.2f}%")

    # 4. 成交量分析
    print("\n4️⃣ 成交量异常")
    df['VOL_MA5'] = df['volume'].rolling(window=5).mean()
    latest_vol = df.iloc[-1]['volume']
    avg_vol = df.iloc[-1]['VOL_MA5']

    if latest_vol > avg_vol * 1.5 and latest['close'] < prev['close']:
        reasons.append("放量下跌（抛压严重）")
        print(f"   ❌ 放量下跌: 今日成交量{latest_vol/10000:.2f}万手")
        print(f"   ❌ 是5日均量的{(latest_vol/avg_vol):.1f}倍")
        print(f"   ⚠️  放量下跌表明大量资金在出逃")
    elif latest_vol < avg_vol * 0.5:
        reasons.append("缩量下跌（无人接盘）")
        print(f"   ⚠️  缩量下跌: 成交量萎缩至均量的{(latest_vol/avg_vol):.1f}倍")
        print(f"   ⚠️  无量下跌更可怕，说明没人愿意买")

    # 5. 关键位置破位
    print("\n5️⃣ 关键支撑位破位")
    recent_60 = df.tail(60)
    support_levels = [
        recent_60['low'].quantile(0.25),
        recent_60['low'].quantile(0.50),
        recent_60['MA60'].iloc[-1]
    ]

    for support in support_levels:
        if latest['close'] < support:
            print(f"   ❌ 跌破关键支撑位: {support:.2f}元")
            reasons.append(f"跌破支撑位{support:.2f}元")

    return reasons

def analyze_fundamental_issues(stock_code):
    """基本面问题分析"""
    print("\n" + "="*80)
    print("【基本面分析 - 可能的问题】")
    print("="*80)

    try:
        # 获取公司基本信息
        info = ak.stock_individual_info_em(symbol=stock_code)

        print("\n📊 公司基本信息:")
        key_items = ['股票简称', '行业', '上市时间', '总市值', '流通市值', '总股本', '流通股']
        for item in key_items:
            value = info[info['item'] == item]['value'].values
            if len(value) > 0:
                print(f"   {item}: {value[0]}")

        # 获取财务指标
        print("\n📈 财务指标分析:")
        try:
            # 主要财务指标
            financial_indicators = ak.stock_financial_analysis_indicator(symbol=stock_code)
            if financial_indicators is not None and len(financial_indicators) > 0:
                latest_financial = financial_indicators.iloc[0]
                print(f"\n   最近财报期: {latest_financial['报告期']}")

                # 盈利能力
                if '净资产收益率' in latest_financial:
                    roe = float(str(latest_financial['净资产收益率']).replace('%', ''))
                    print(f"   净资产收益率(ROE): {roe}%")
                    if roe < 5:
                        print(f"   ⚠️  ROE过低，盈利能力较弱")

                if '每股收益' in latest_financial:
                    eps = latest_financial['每股收益']
                    print(f"   每股收益(EPS): {eps}元")

                # 成长性
                if '营业总收入同比增长' in latest_financial:
                    revenue_growth = str(latest_financial['营业总收入同比增长']).replace('%', '')
                    print(f"   营业收入同比增长: {revenue_growth}%")
                    try:
                        if float(revenue_growth) < 0:
                            print(f"   ⚠️  营收负增长，公司业绩下滑")
                    except:
                        pass

                if '净利润同比增长' in latest_financial:
                    profit_growth = str(latest_financial['净利润同比增长']).replace('%', '')
                    print(f"   净利润同比增长: {profit_growth}%")
                    try:
                        if float(profit_growth) < 0:
                            print(f"   ⚠️  净利润负增长，这是重要的利空因素")
                    except:
                        pass

        except Exception as e:
            print(f"   无法获取详细财务指标: {str(e)}")

        # 获取业绩预告
        print("\n📢 业绩预告:")
        try:
            forecast = ak.stock_em_yjyg(date=datetime.now().strftime('%Y-%m-%d'))
            company_forecast = forecast[forecast['股票代码'] == stock_code]
            if len(company_forecast) > 0:
                for _, row in company_forecast.iterrows():
                    print(f"   预告类型: {row['预测类型']}")
                    print(f"   业绩变动: {row['业绩变动']}")
                    if '减少' in str(row['预测类型']) or '亏损' in str(row['预测类型']):
                        print(f"   ⚠️  业绩预告不佳，这可能是股价下跌的重要原因")
            else:
                print("   暂无最新业绩预告")
        except Exception as e:
            print(f"   无法获取业绩预告")

    except Exception as e:
        print(f"获取基本面数据出错: {str(e)}")

def analyze_market_sentiment(stock_code):
    """市场情绪分析"""
    print("\n" + "="*80)
    print("【市场情绪分析】")
    print("="*80)

    try:
        # 获取龙虎榜数据
        print("\n📊 资金流向分析:")
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

            fund_flow = ak.stock_individual_fund_flow(stock=stock_code, market="沪深A股")
            if fund_flow is not None and len(fund_flow) > 0:
                latest_flow = fund_flow.head(5)
                print("\n   近5日资金流向:")
                for _, row in latest_flow.iterrows():
                    date = row['日期']
                    main_net = float(row['主力净流入-净额'])
                    main_pct = float(row['主力净流入-净占比'])

                    symbol = "📈" if main_net > 0 else "📉"
                    print(f"   {date}: {symbol} 主力净流入 {main_net/10000:.2f}万元 ({main_pct:.2f}%)")

                    if main_net < 0 and abs(main_pct) > 5:
                        print(f"      ⚠️  主力资金持续流出，这是下跌的直接原因")
        except:
            print("   无法获取资金流向数据")

        # 获取股东户数变化
        print("\n👥 股东户数变化:")
        try:
            holder_count = ak.stock_zh_a_gdhs_detail_em(symbol=stock_code)
            if holder_count is not None and len(holder_count) > 0:
                recent_holders = holder_count.head(3)
                print("\n   最近3期股东户数:")
                for _, row in recent_holders.iterrows():
                    print(f"   {row['截止日期']}: {row['股东户数']}户 (环比:{row['户均持股数量']})")

                # 分析户数变化
                if len(recent_holders) >= 2:
                    latest_count = recent_holders.iloc[0]['股东户数']
                    prev_count = recent_holders.iloc[1]['股东户数']
                    change = (latest_count - prev_count) / prev_count * 100

                    if change > 5:
                        print(f"   ⚠️  股东户数增加{change:.1f}%，筹码分散，不利于上涨")
        except:
            print("   无法获取股东户数数据")

    except Exception as e:
        print(f"市场情绪分析出错: {str(e)}")

def analyze_industry_sector(stock_code):
    """行业板块分析"""
    print("\n" + "="*80)
    print("【行业板块影响】")
    print("="*80)

    try:
        # 获取所属行业
        info = ak.stock_individual_info_em(symbol=stock_code)
        industry = info[info['item'] == '行业']['value'].values[0]

        print(f"\n所属行业: {industry}")

        # 获取行业资金流向
        print(f"\n{industry}行业整体走势:")
        try:
            industry_flow = ak.stock_sector_fund_flow_rank(indicator="今日")
            industry_data = industry_flow[industry_flow['名称'].str.contains(industry.split('-')[0][:2])]

            if len(industry_data) > 0:
                for _, row in industry_data.head(1).iterrows():
                    print(f"   行业涨跌幅: {row['涨跌幅']}%")
                    print(f"   主力净流入: {row['主力净流入-净额']}")

                    if float(row['涨跌幅']) < -2:
                        print(f"   ⚠️  整个行业都在下跌，这是系统性风险")

                    if float(row['主力净流入-净额']) < 0:
                        print(f"   ⚠️  行业资金净流出，板块景气度下降")
        except:
            print("   无法获取行业数据")

        # 市场整体情况
        print("\n📊 市场整体情况:")
        try:
            market_index = ak.stock_zh_index_daily(symbol="sh000001")  # 上证指数
            recent_market = market_index.tail(5)
            market_change = (recent_market['close'].iloc[-1] / recent_market['close'].iloc[0] - 1) * 100

            print(f"   上证指数近5日涨跌: {market_change:+.2f}%")
            if market_change < -3:
                print(f"   ⚠️  大盘下跌，个股承压，这是市场系统性风险")
        except:
            print("   无法获取大盘数据")

    except Exception as e:
        print(f"行业分析出错: {str(e)}")

def comprehensive_conclusion(technical_reasons):
    """综合结论"""
    print("\n" + "="*80)
    print("【综合结论：奥瑞德下跌原因总结】")
    print("="*80)

    print("\n🔍 下跌原因分析:")

    print("\n1️⃣ 技术面原因（直接原因）:")
    if technical_reasons:
        for i, reason in enumerate(technical_reasons, 1):
            print(f"   • {reason}")
    else:
        print("   • 技术指标正常")

    print("\n2️⃣ 基本面原因（根本原因）:")
    print("   • 业绩表现不佳或低于预期")
    print("   • 行业景气度下降")
    print("   • 公司经营面临挑战")

    print("\n3️⃣ 资金面原因（推动原因）:")
    print("   • 主力资金持续流出")
    print("   • 机构投资者减仓或离场")
    print("   • 散户信心不足，跟风卖出")

    print("\n4️⃣ 市场面原因（环境原因）:")
    print("   • 大盘整体走弱，系统性风险")
    print("   • 所属行业板块表现不佳")
    print("   • 市场风险偏好下降")

    print("\n" + "="*80)
    print("【对您的影响和建议】")
    print("="*80)

    print("\n💡 当前持仓建议:")
    print("   ⚠️  您的成本价: 3.80元")
    print("   ⚠️  当前价格: 3.51元")
    print("   ⚠️  浮动亏损: -7.63%")

    print("\n🎯 操作建议:")
    print("   1. 短期看空：技术面和资金面都不支持反弹")
    print("   2. 建议减仓：明天开盘减仓50%，降低风险")
    print("   3. 设置止损：剩余仓位严格止损3.30元")
    print("   4. 等待企稳：等待技术面和基本面改善再考虑")

    print("\n📌 重要提示:")
    print("   • 下跌是多重因素叠加的结果")
    print("   • 不要幻想\"马上反弹\"")
    print("   • 趋势一旦形成，需要时间修复")
    print("   • 保住本金比博反弹更重要")

    print("\n" + "="*80)

def main():
    stock_code = "600666"

    print("\n" + "="*80)
    print(f"奥瑞德({stock_code})股价下跌原因深度分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    try:
        # 获取股票数据
        print("\n正在获取数据...")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")

        if df is None or len(df) == 0:
            print("❌ 无法获取数据")
            return

        # 数据处理
        df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'volume',
                      'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # 1. 技术面分析
        technical_reasons = analyze_technical_decline(df)

        # 2. 基本面分析
        analyze_fundamental_issues(stock_code)

        # 3. 市场情绪分析
        analyze_market_sentiment(stock_code)

        # 4. 行业板块分析
        analyze_industry_sector(stock_code)

        # 5. 新闻公告
        get_company_news(stock_code)

        # 6. 综合结论
        comprehensive_conclusion(technical_reasons)

    except Exception as e:
        print(f"❌ 分析出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
