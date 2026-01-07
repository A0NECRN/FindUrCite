# FindUrCite: AI-Powered Research Assistant with Multi-Agent Debate
# FindUrCite: 基于多智能体博弈的 AI 科研助手

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## English

**FindUrCite** is an advanced academic research automation tool designed to streamline literature review, code discovery, and deep paper analysis. By leveraging a **Multi-Agent Debate System** (Student-Advisor model), it ensures high-quality, rigorous, and hallucination-free research outcomes. 

Equipped with a modern **FastAPI + Vue 3** web interface and **WebSocket** real-time streaming, FindUrCite provides a seamless and interactive research experience.

### 🌟 Key Features

*   **Multi-Agent Debate (Student-Advisor)**: Implements an iterative critique-revision loop. A "Student" agent drafts analysis while an "Advisor" agent (simulating a strict conference reviewer) provides evidence-based critiques.
*   **Chain-of-Thought (CoT) Reasoning**: Agents use CoT to analyze user inputs and research papers, ensuring deep understanding of core contributions and methodologies.
*   **Real-Time Streaming UI**: A modern Vue 3 + Tailwind CSS dashboard that displays the research process live via WebSockets.
*   **Deep Read Pipeline**: Automatically fetches full-text PDFs from ArXiv and Semantic Scholar, extracts content, and performs comprehensive analysis.
*   **Smart Query Expansion**: Generates multi-dimensional search queries (Broad, Specific, Niche) to maximize discovery across academic databases.
*   **Automated Code Discovery**: Scours GitHub for relevant repositories, including star counts and direct links, bridging the gap between theory and implementation.
*   **Anti-Hallucination Constraints**: Strict prompts and evidence-based requirements ensure all claims are backed by source text, preventing LLM "hallucinations."
*   **Comprehensive Reports**: Generates detailed Markdown reports with 23+ data columns, including core ideas, methodologies, and critiques.

### 🏗️ Architecture

*   `src/agents/`: Role-specific LLM agents (Student with CoT, Advisor with strict review logic).
*   `src/server.py`: FastAPI backend supporting WebSocket streaming and static file serving.
*   `src/static/`: Modern Vue 3 + Tailwind CSS frontend.
*   `src/workflow.py`: Orchestration of the multi-agent debate and research pipeline.
*   `src/searcher.py`: Integration with Semantic Scholar and ArXiv API.
*   `src/pdf_processor.py`: Robust PDF handling, downloading, and text extraction.
*   `src/code_finder.py`: GitHub API integration for code discovery.

### 🚀 Getting Started

#### Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.com/) (Recommended model: `qwen2.5:7b`)
*   CUDA-enabled GPU (Optional but recommended for faster LLM inference)

#### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/FindUrCite.git
cd FindUrCite

# Install dependencies using Tsinghua mirror
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Usage

**1. Start the Web Server (Recommended)**
```bash
python src/server.py
```
Open your browser at `http://localhost:8000` to access the modern research dashboard.

**2. Start via Batch Script (CLI)**
Double-click `run_system.bat` or run:
```bash
run_system.bat
```

### 🛠️ Maintenance & Quality Assurance
We maintain an `error_log.md` to track, resolve, and prevent recurring issues, ensuring the system's reliability and continuous improvement.

---

<a name="chinese"></a>

## 中文

**FindUrCite** 是一款先进的自动化科研助手，旨在简化文献综述、代码搜索和深度论文分析流程。通过引入 **多智能体博弈系统 (Student-Advisor 模型)**，确保研究结果的高质量、严谨性且无幻觉。

系统配备了基于 **FastAPI + Vue 3** 的现代 Web 界面，并通过 **WebSocket** 实现实时流式输出，为用户提供流畅且互动的科研体验。

### 🌟 核心特性

*   **多智能体博弈 (导师-学生模型)**：模拟“学生”起草分析与“导师”（模拟严厉的顶会审稿人）审核质疑的反复迭代过程，通过多轮辩论提升学术分析的深度。
*   **思维链 (CoT) 推理**：智能体采用思维链技术分析用户需求和论文内容，确保对核心贡献和方法论的深度理解。
*   **实时流式 UI**：基于 Vue 3 + Tailwind CSS 开发的现代控制面板，通过 WebSocket 实时展示搜索、辩论和分析进度。
*   **深度阅读流水线 (Deep Read Pipeline)**：自动从 ArXiv 和 Semantic Scholar 获取 PDF 全文、提取文本，并进行全方位的深度解析。
*   **智能搜索扩展**：自动生成多维度搜索查询（广度、精度、深度），最大程度挖掘潜在参考文献。
*   **自动化代码发现**：自动检索 GitHub 相关仓库及其 Star 数，直观展示论文的开源实现情况。
*   **抗幻觉约束**：通过严格的 Prompt 工程和证据驱动要求，确保所有结论均有原文支撑，杜绝大模型“一本正经胡说八道”。
*   **全方位研究报告**：生成包含 23+ 数据维度的详细 Markdown 报告，涵盖核心思想、方法论、局限性及专家点评。

### 🏗️ 系统架构

*   `src/agents/`：包含不同角色的 LLM 智能体（具备 CoT 的学生，具备严谨逻辑的导师）。
*   `src/server.py`：基于 FastAPI 的后端，支持 WebSocket 流式传输和静态资源分发。
*   `src/static/`：基于 Vue 3 + Tailwind CSS 的现代前端界面。
*   `src/workflow.py`：负责协调多智能体博弈及整体科研工作流。
*   `src/searcher.py`：Semantic Scholar 与 ArXiv API 集成模块。
*   `src/pdf_processor.py`：PDF 下载、处理与文本提取核心模块。
*   `src/code_finder.py`：GitHub 代码检索模块。

### 🚀 快速上手

#### 环境要求
*   Python 3.10+
*   [Ollama](https://ollama.com/) (推荐模型：`qwen2.5:7b`)
*   支持 CUDA 的 GPU (可选，推荐以提升推理速度)

#### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/yourusername/FindUrCite.git
cd FindUrCite

# 使用清华源快速安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 使用方法

**1. 启动 Web 服务器 (推荐)**
```bash
python src/server.py
```
在浏览器中访问 `http://localhost:8000` 即可进入现代科研控制面板。

**2. 通过批处理脚本启动 (命令行)**
双击 `run_system.bat` 或在终端运行：
```bash
run_system.bat
```

### 🛠️ 维护与质量保证
我们通过 `error_log.md` 统一记录、解决并预防重复性错误，确保系统的可靠性与持续优化。

---

## 📜 License / 许可证
MIT License
