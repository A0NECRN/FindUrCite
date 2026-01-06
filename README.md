# FindUrCite: AI-Powered Research Assistant with Multi-Agent Debate
# FindUrCite: 基于多智能体博弈的 AI 科研助手

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## English

**FindUrCite** is an advanced academic research automation tool designed to streamline literature review, code discovery, and deep paper analysis. By leveraging a **Multi-Agent Debate System**, it ensures high-quality, rigorous, and hallucination-free research outcomes.

### 🌟 Key Features

*   **Multi-Agent Debate (Student-Advisor)**: Implements an iterative critique-revision loop between a "Student" agent (drafting analysis) and an "Advisor" agent (reviewing and critiquing), ensuring academic rigor.
*   **Deep Read Pipeline**: Automatically fetches full-text PDFs, extracts content, and performs comprehensive analysis for the most relevant papers.
*   **Smart Query Expansion**: Generates multi-dimensional search queries (Broad, Specific, Niche) to maximize discovery across Semantic Scholar and ArXiv.
*   **Automated Code Discovery**: Scours GitHub for relevant repositories, including star counts and direct links, to bridge the gap between theory and implementation.
*   **Evidence-Based Analysis**: Every claim in the analysis is backed by direct quotes from the source text to prevent LLM hallucinations.
*   **Excel-Compatible Reports**: Generates detailed Markdown reports with 23 data columns, structured for easy import into Excel or other analysis tools.
*   **High Efficiency**: Utilizes parallel processing for PDF downloads and code searches to minimize execution time.

### 🏗️ Architecture

*   `src/agents/`: Role-specific LLM agents (Base, Student, Advisor).
*   `src/workflow.py`: Orchestration of the multi-agent debate and research pipeline.
*   `src/searcher.py`: Multi-query search engine integration.
*   `src/pdf_processor.py`: Robust PDF handling and text extraction.
*   `src/code_finder.py`: GitHub API integration for code discovery.
*   `src/cache.py`: Efficient analysis caching to save tokens and time.

### 🚀 Getting Started

#### Prerequisites
*   Python 3.8+
*   [Ollama](https://ollama.com/) (Default model: `qwen2.5:7b`)

#### Installation
```bash
# Install dependencies using Tsinghua mirror for faster speed in China
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Usage
1.  Place your research abstract or idea in a file (e.g., `draft.txt`).
2.  Run the main pipeline:
    ```bash
    python src/main.py draft.txt
    ```

---

<a name="chinese"></a>

## 中文

**FindUrCite** 是一款先进的自动化科研助手，旨在简化文献综述、代码搜索和深度论文分析流程。通过引入 **多智能体博弈系统 (Multi-Agent Debate)**，确保研究结果的高质量、严谨性且无幻觉。

### 🌟 核心特性

*   **多智能体博弈 (导师-学生模型)**：模拟“学生”起草分析与“导师”审核质疑的反复迭代过程，通过多轮辩论提升学术分析的深度与准确性。
*   **深度阅读流水线 (Deep Read Pipeline)**：自动获取 PDF 全文、提取文本，并针对高相关性论文进行全方位的深度解析。
*   **智能搜索扩展**：自动生成多维度搜索查询（广度、精度、深度），覆盖 Semantic Scholar 和 ArXiv，最大程度挖掘潜在参考文献。
*   **自动化代码发现**：自动检索 GitHub 相关仓库及其 Star 数，直观展示论文的开源实现情况。
*   **证据驱动分析**：所有分析结论均需附带原文直接引用（Evidence），从根源上杜绝大模型的“一本正经胡说八道”。
*   **兼容 Excel 的报告**：生成包含 23 个数据维度的详细 Markdown 报告，支持直接导入 Excel 进行后续处理。
*   **高效并发处理**：在 PDF 下载和代码检索环节采用并发机制，显著缩短等待时间。

### 🏗️ 系统架构

*   `src/agents/`：包含不同角色的 LLM 智能体（基础、学生、导师）。
*   `src/workflow.py`：负责协调多智能体博弈及整体科研工作流。
*   `src/searcher.py`：多查询搜索引擎集成。
*   `src/pdf_processor.py`：PDF 下载与文本提取核心模块。
*   `src/code_finder.py`：GitHub 代码检索模块。
*   `src/cache.py`：分析结果缓存机制，节省 Token 与运行时间。

### 🚀 快速上手

#### 环境要求
*   Python 3.8+
*   [Ollama](https://ollama.com/) (默认模型：`qwen2.5:7b`)

#### 安装步骤
```bash
# 使用清华源快速安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 使用方法
1.  将你的研究摘要或想法写入文件（如 `draft.txt`）。
2.  启动程序：
    ```bash
    python src/main.py draft.txt
    ```

---

## 📜 License / 许可证

MIT License
