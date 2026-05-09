#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain 完整使用指南
详细介绍 LangChain 的安装、配置和各种使用场景
"""

"""
================================================================================
                        LangChain 使用指南
================================================================================

【什么是 LangChain？】

LangChain 是一个用于构建 AI 应用的框架，特别适合开发：
- 聊天机器人
- 问答系统
- 智能代理（Agent）
- RAG（检索增强生成）应用
- 自动化工作流

核心优势：
✓ 统一的接口对接多个 LLM（OpenAI、Claude、Gemini等）
✓ 丰富的工具和集成
✓ 模块化设计，易于扩展
✓ 生产级别的监控和调试工具

================================================================================
                            安装 LangChain
================================================================================

【基础安装】

1. 安装核心包：
   pip install langchain

2. 安装常用组件：
   pip install langchain-openai      # OpenAI 集成
   pip install langchain-anthropic   # Claude 集成
   pip install langchain-google-genai # Google Gemini 集成
   pip install langchain-community   # 社区集成

3. 安装向量数据库（用于 RAG）：
   pip install langchain-chroma      # Chroma 向量数据库
   pip install langchain-pinecone    # Pinecone 向量数据库
   pip install faiss-cpu             # FAISS 向量搜索

4. 安装工具包：
   pip install langchain-experimental # 实验性功能
   pip install langgraph             # 高级 Agent 工作流
   pip install langsmith             # 监控和调试

【环境配置】

创建 .env 文件：
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

================================================================================
                        核心概念和组件
================================================================================

【1. Models（模型）】
- LLMs: 文本生成模型（GPT-4、Claude等）
- Chat Models: 对话模型
- Embeddings: 文本向量化模型

【2. Prompts（提示词）】
- Prompt Templates: 提示词模板
- Few-shot Examples: 少样本学习
- Output Parsers: 输出解析器

【3. Chains（链）】
- LLMChain: 基础链
- Sequential Chain: 顺序链
- Router Chain: 路由链

【4. Agents（智能代理）】
- Tools: 工具集
- Agent Executor: 代理执行器
- Memory: 记忆系统

【5. Memory（记忆）】
- ConversationBufferMemory: 对话缓冲记忆
- ConversationSummaryMemory: 对话摘要记忆
- VectorStoreMemory: 向量存储记忆

【6. RAG（检索增强生成）】
- Document Loaders: 文档加载器
- Text Splitters: 文本分割器
- Vector Stores: 向量存储
- Retrievers: 检索器

================================================================================
"""

# ============================================================================
# 示例 1: 基础 LLM 调用
# ============================================================================

def example_1_basic_llm():
    """最基础的 LLM 调用示例"""
    print("\n" + "="*80)
    print("示例 1: 基础 LLM 调用")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# 使用 OpenAI
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# 或使用 Claude
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.7)

# 简单调用
response = llm.invoke("用一句话解释什么是量化交易")
print(response.content)

# 批量调用
responses = llm.batch([
    "什么是MACD指标？",
    "如何使用均线判断趋势？"
])
for resp in responses:
    print(resp.content)
    """)

# ============================================================================
# 示例 2: 使用 Prompt Template
# ============================================================================

def example_2_prompt_template():
    """使用提示词模板"""
    print("\n" + "="*80)
    print("示例 2: Prompt Template（提示词模板）")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# 创建提示词模板
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}"),
    ("user", "{input}")
])

# 创建链
llm = ChatOpenAI(model="gpt-4")
chain = template | llm

# 使用
response = chain.invoke({
    "role": "量化交易分析师",
    "input": "分析一下奥瑞德(600666)的技术指标"
})
print(response.content)

# 更复杂的模板
template = ChatPromptTemplate.from_messages([
    ("system", '''你是一个股票分析专家。
    给定以下信息：
    - 股票代码: {stock_code}
    - 当前价格: {current_price}
    - 成本价: {cost_price}
    - 技术指标: {indicators}

    请给出买卖建议。'''),
    ("user", "请分析")
])

response = chain.invoke({
    "stock_code": "600666",
    "current_price": 3.51,
    "cost_price": 3.80,
    "indicators": "MACD死叉, RSI=61, MA5<MA10"
})
    """)

# ============================================================================
# 示例 3: Chains（链式调用）
# ============================================================================

def example_3_chains():
    """链式调用示例"""
    print("\n" + "="*80)
    print("示例 3: Chains（链式调用）")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# 定义输出结构
class StockAnalysis(BaseModel):
    recommendation: str = Field(description="买入/卖出/持有")
    confidence: float = Field(description="信心度0-1")
    reason: str = Field(description="推荐理由")
    stop_loss: float = Field(description="止损价")

# 创建解析器
parser = PydanticOutputParser(pydantic_object=StockAnalysis)

# 创建提示词
template = ChatPromptTemplate.from_messages([
    ("system", "你是股票分析师。{format_instructions}"),
    ("user", "分析 {stock_code}，当前价{price}，成本{cost}")
])

# 构建链
llm = ChatOpenAI(model="gpt-4")
chain = template | llm | parser

# 执行
result = chain.invoke({
    "stock_code": "600666",
    "price": 3.51,
    "cost": 3.80,
    "format_instructions": parser.get_format_instructions()
})

print(f"建议: {result.recommendation}")
print(f"信心: {result.confidence}")
print(f"理由: {result.reason}")
print(f"止损: {result.stop_loss}")
    """)

# ============================================================================
# 示例 4: Agents（智能代理）
# ============================================================================

def example_4_agents():
    """智能代理示例"""
    print("\n" + "="*80)
    print("示例 4: Agents（智能代理）- 最强大的功能")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
import akshare as ak

# 定义工具
@tool
def get_stock_price(stock_code: str) -> str:
    '''获取股票实时价格'''
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date="20250101", end_date="20251119", adjust="qfq")
        latest = df.iloc[-1]
        return f"{stock_code}最新价格: {latest['收盘']}元"
    except:
        return f"无法获取{stock_code}的数据"

@tool
def calculate_profit_loss(current_price: float, cost_price: float) -> str:
    '''计算盈亏比例'''
    profit = (current_price - cost_price) / cost_price * 100
    return f"盈亏: {profit:.2f}%"

@tool
def get_buy_signal(stock_code: str) -> str:
    '''分析买入信号'''
    # 这里可以调用你的技术分析代码
    return "当前无明显买入信号，建议观望"

# 创建提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个股票分析助手，可以使用工具来帮助用户做决策"),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# 创建 Agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
tools = [get_stock_price, calculate_profit_loss, get_buy_signal]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 使用 Agent
response = agent_executor.invoke({
    "input": "帮我分析奥瑞德(600666)，我的成本价是3.80元，现在应该怎么操作？"
})
print(response['output'])

# Agent 会自动：
# 1. 调用 get_stock_price 获取当前价格
# 2. 调用 calculate_profit_loss 计算盈亏
# 3. 调用 get_buy_signal 分析信号
# 4. 综合所有信息给出建议
    """)

# ============================================================================
# 示例 5: Memory（记忆系统）
# ============================================================================

def example_5_memory():
    """记忆系统示例"""
    print("\n" + "="*80)
    print("示例 5: Memory（对话记忆）")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 创建记忆
memory = ConversationBufferMemory()

# 创建对话链
llm = ChatOpenAI(model="gpt-4")
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 多轮对话
response1 = conversation.predict(input="我持有奥瑞德，成本3.80元")
print(response1)

response2 = conversation.predict(input="现在价格是3.51元，我该怎么办？")
print(response2)
# Agent 记住了你之前说的成本价！

response3 = conversation.predict(input="如果跌到3.30元呢？")
print(response3)
# Agent 记住了整个对话历史！

# 查看记忆
print(memory.load_memory_variables({}))
    """)

# ============================================================================
# 示例 6: RAG（检索增强生成）
# ============================================================================

def example_6_rag():
    """RAG 示例 - 基于文档问答"""
    print("\n" + "="*80)
    print("示例 6: RAG（检索增强生成）- 基于自己的数据")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# 1. 加载文档
loader = TextLoader("股票分析报告.txt")  # 或 PyPDFLoader("report.pdf")
documents = loader.load()

# 2. 分割文本
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(documents)

# 3. 创建向量数据库
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)

# 4. 创建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 5. 创建问答链
llm = ChatOpenAI(model="gpt-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# 6. 提问
question = "报告中对奥瑞德的技术面分析是什么？"
answer = qa_chain.run(question)
print(answer)

# RAG 的优势：
# - 基于你自己的文档/数据回答问题
# - 不受 LLM 知识截止日期限制
# - 可以引用具体的文档内容
# - 适合企业内部知识库、研报分析等
    """)

# ============================================================================
# 示例 7: 实战 - 股票分析 Agent
# ============================================================================

def example_7_stock_agent():
    """完整的股票分析 Agent"""
    print("\n" + "="*80)
    print("示例 7: 实战 - 完整的股票分析 Agent")
    print("="*80)

    print("""
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import akshare as ak
import pandas as pd

# ===== 定义工具集 =====

@tool
def get_stock_info(stock_code: str) -> str:
    '''获取股票基本信息'''
    try:
        info = ak.stock_individual_info_em(symbol=stock_code)
        name = info[info['item'] == '股票简称']['value'].values[0]
        industry = info[info['item'] == '行业']['value'].values[0]
        return f"股票名称: {name}, 行业: {industry}"
    except:
        return "获取失败"

@tool
def get_realtime_data(stock_code: str) -> str:
    '''获取实时行情数据'''
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date="20250101", end_date="20251119", adjust="qfq")
        latest = df.iloc[-1]
        return f'''
        最新价: {latest['收盘']}元
        涨跌幅: {latest['涨跌幅']}%
        成交量: {latest['成交量']/10000:.2f}万手
        成交额: {latest['成交额']/100000000:.2f}亿元
        '''
    except:
        return "获取失败"

@tool
def analyze_technical(stock_code: str) -> str:
    '''技术分析'''
    # 这里可以调用你之前写的技术分析代码
    return "MACD死叉，均线空头排列，建议观望"

@tool
def calculate_signals(stock_code: str) -> str:
    '''计算买卖信号'''
    # 调用你的买卖信号分析代码
    return "买入信号: 0/15分, 卖出信号: 10/20分"

@tool
def suggest_operation(current_price: float, cost_price: float) -> str:
    '''给出操作建议'''
    profit = (current_price - cost_price) / cost_price * 100
    if profit < -7:
        return f"亏损{abs(profit):.1f}%, 建议立即减仓50%"
    elif profit < -5:
        return f"亏损{abs(profit):.1f}%, 建议减仓30%并设止损"
    elif profit > 10:
        return f"盈利{profit:.1f}%, 建议止盈30%"
    else:
        return "继续持有，密切观察"

# ===== 创建 Agent =====

tools = [
    get_stock_info,
    get_realtime_data,
    analyze_technical,
    calculate_signals,
    suggest_operation
]

prompt = ChatPromptTemplate.from_messages([
    ("system", '''你是一个专业的股票分析师助手。
    你可以使用以下工具来帮助用户分析股票：
    - get_stock_info: 获取股票基本信息
    - get_realtime_data: 获取实时行情
    - analyze_technical: 技术分析
    - calculate_signals: 计算买卖信号
    - suggest_operation: 操作建议

    请按照以下步骤分析：
    1. 获取股票基本信息
    2. 获取实时行情数据
    3. 进行技术分析
    4. 计算买卖信号
    5. 综合给出操作建议
    '''),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10
)

# ===== 使用 Agent =====

# 场景 1: 新股票分析
response = agent_executor.invoke({
    "input": "帮我全面分析一下奥瑞德(600666)"
})
print(response['output'])

# 场景 2: 持仓建议
response = agent_executor.invoke({
    "input": "我持有奥瑞德，成本3.80元，现价3.51元，请给我操作建议"
})
print(response['output'])

# 场景 3: 对比分析
response = agent_executor.invoke({
    "input": "对比分析奥瑞德(600666)和天地在线(002995)，哪个更值得买入？"
})
print(response['output'])
    """)

# ============================================================================
# 示例 8: LangGraph - 高级工作流
# ============================================================================

def example_8_langgraph():
    """LangGraph 高级工作流"""
    print("\n" + "="*80)
    print("示例 8: LangGraph（高级 Agent 工作流）")
    print("="*80)

    print("""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 定义状态
class AgentState(TypedDict):
    stock_code: str
    cost_price: float
    current_price: float
    analysis_result: Annotated[list, operator.add]
    recommendation: str

# 定义节点
def fetch_data(state):
    # 获取数据
    return {"current_price": 3.51}

def technical_analysis(state):
    # 技术分析
    result = "MACD死叉，均线空头排列"
    return {"analysis_result": [result]}

def calculate_profit(state):
    # 计算盈亏
    profit = (state['current_price'] - state['cost_price']) / state['cost_price'] * 100
    result = f"盈亏: {profit:.2f}%"
    return {"analysis_result": [result]}

def make_decision(state):
    # 综合决策
    if state['current_price'] < state['cost_price'] * 0.93:
        return {"recommendation": "立即止损"}
    else:
        return {"recommendation": "减仓观望"}

# 构建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("fetch_data", fetch_data)
workflow.add_node("technical_analysis", technical_analysis)
workflow.add_node("calculate_profit", calculate_profit)
workflow.add_node("make_decision", make_decision)

# 定义边（执行顺序）
workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", "technical_analysis")
workflow.add_edge("fetch_data", "calculate_profit")  # 并行执行
workflow.add_edge("technical_analysis", "make_decision")
workflow.add_edge("calculate_profit", "make_decision")
workflow.add_edge("make_decision", END)

# 编译并运行
app = workflow.compile()
result = app.invoke({
    "stock_code": "600666",
    "cost_price": 3.80
})

print(result['recommendation'])

# LangGraph 的优势：
# - 复杂的多步骤工作流
# - 条件分支和循环
# - 并行执行
# - 人机协作（可以在某些节点暂停等待人工确认）
    """)

# ============================================================================
# 实用建议
# ============================================================================

def practical_tips():
    """实用建议"""
    print("\n" + "="*80)
    print("LangChain 实用建议")
    print("="*80)

    print("""
【1. 新手入门路径】

第一步：基础 LLM 调用
- 学会使用 ChatOpenAI/ChatAnthropic
- 理解 temperature、max_tokens 等参数

第二步：Prompt Template
- 学会写好的提示词模板
- 使用变量和格式化

第三步：Chains
- 学会链式调用
- 使用 Output Parser 结构化输出

第四步：Agents
- 学会定义 Tools
- 理解 Agent 的思考过程

第五步：RAG
- 学会处理文档
- 构建向量数据库

【2. 常见问题】

Q: LangChain 和直接调用 API 有什么区别？
A: LangChain 提供了更高层的抽象，让你可以：
   - 轻松切换不同的 LLM
   - 使用丰富的工具和集成
   - 构建复杂的 Agent 和工作流
   - 内置记忆和上下文管理

Q: 什么时候用 Chains，什么时候用 Agents？
A:
   - Chains: 流程固定、步骤明确的任务
   - Agents: 需要 LLM 自主决策、动态调用工具的任务

Q: 如何降低成本？
A:
   - 使用便宜的模型（gpt-3.5-turbo）做简单任务
   - 使用缓存避免重复调用
   - RAG 时减少 chunk 数量
   - 设置 max_tokens 限制

【3. 最佳实践】

✓ 始终设置错误处理
✓ 使用环境变量管理 API Key
✓ 记录日志方便调试（verbose=True）
✓ 使用 LangSmith 监控生产环境
✓ 对敏感操作添加人工确认
✓ 定期更新 LangChain 版本

【4. 进阶学习】

- LangChain 官方文档: https://python.langchain.com
- LangGraph 文档: https://langchain-ai.github.io/langgraph/
- LangSmith: https://smith.langchain.com
- 社区示例: https://github.com/langchain-ai/langchain/tree/master/templates

【5. 在量化交易中的应用】

✓ 自动化股票分析报告生成
✓ 智能选股助手
✓ 交易策略回测解读
✓ 市场情绪分析
✓ 风险管理助手
✓ 投资组合优化建议
    """)

# ============================================================================
# 主函数
# ============================================================================

def main():
    print("""

    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║                   LangChain 完整使用指南                              ║
    ║                                                                      ║
    ║          从零开始学习 LangChain，构建智能 AI 应用                      ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝

    """)

    # 显示所有示例
    example_1_basic_llm()
    example_2_prompt_template()
    example_3_chains()
    example_4_agents()
    example_5_memory()
    example_6_rag()
    example_7_stock_agent()
    example_8_langgraph()
    practical_tips()

    print("\n" + "="*80)
    print("📚 所有示例代码都已展示，您可以直接复制使用")
    print("💡 建议从示例1开始，逐步学习")
    print("🚀 祝您学习愉快！")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
