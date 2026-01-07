# FindUrCite: AI-Powered Research Assistant with Multi-Agent Debate
# FindUrCite: 基于多智能体博弈的 AI 科研助手

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## 🇬🇧 English

**FindUrCite** is a state-of-the-art academic research automation framework designed to transform how researchers discover, analyze, and synthesize literature. By integrating a **Multi-Agent Debate System** with robust search and processing pipelines, it ensures that every research insight is rigorous, evidence-based, and free from common AI hallucinations.

### 🌟 Core Capabilities

*   **Multi-Agent Debate (Student-Advisor)**: Features an iterative "Critique-Revision" loop between a **Student Agent** (responsible for drafting analysis) and an **Advisor Agent** (acting as a senior reviewer). This system simulates real-world academic peer review to refine relevance and depth.
*   **Adaptive Search Expansion**: Automatically adjusts filtering strictness. If strict keyword matching returns too few results, the system intelligently relaxes constraints and incorporates high-citation candidates to ensure comprehensive coverage.
*   **Zero-Hallucination Evidence System**: Every analytical claim is strictly backed by direct quotes ("Evidence Quotes") from the source text. Enhanced with **Chain-of-Thought (CoT)** reasoning and strict domain constraints to prevent unrelated linguistic or topical hallucinations.
*   **Deep Read Pipeline**: Beyond abstracts, the system automatically fetches full-text PDFs, extracts content using advanced methods, and performs multi-round debate analysis on high-relevance papers.
*   **Modern Web Interface**: A high-performance UI built with **FastAPI**, **WebSockets**, and **Vue 3**. Features real-time progress streaming, integrated PDF viewing, and persistent report access.
*   **Robust Scoring System**: Implements a strict 0-5 relevance scoring mechanism with automated normalization and type safety to ensure consistent and reliable evaluations.

### 🏗️ Technical Architecture

*   `src/agents/`: Specialized LLM personas (Student, Advisor) with distinct reasoning chains.
*   `src/workflow.py`: The "brain" of the system, orchestrating the debate logic and research stages.
*   `src/searcher.py`: Advanced multi-query engine for academic discovery.
*   `src/pdf_processor.py`: Robust handling of PDF downloads and text extraction.
*   `src/server.py`: FastAPI backend supporting real-time WebSocket communication.
*   `src/static/`: Modern, responsive frontend built with Vue 3 and Tailwind CSS.

### 🚀 Getting Started

#### Prerequisites
*   **Python 3.10+**
*   **[Ollama](https://ollama.com/)**: Installed and running locally.
*   **Default Model**: `qwen2.5:7b` (recommended for its strong reasoning and bilingual capabilities).

#### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/FindUrCite.git
cd FindUrCite

# Install dependencies (using Tsinghua mirror for optimized speed in China)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Running the System
1.  **Start the Web Interface (Recommended)**:
    ```bash
    python src/server.py
    ```
    Access the UI at `http://localhost:8000`.

2.  **Command Line Usage**:
    ```bash
    python src/main.py "Your research idea or abstract here"
    ```

---

<a name="chinese"></a>

## 🇨🇳 中文

**FindUrCite** 是一款尖端的自动化科研助手，旨在彻底改变科研人员检索、分析和综述文献的方式。通过将**多智能体博弈系统**与强大的搜索和处理流水线相结合，它确保了每一项研究见解都具备严谨性、证据支撑，并有效杜绝了 AI 常见的幻觉问题。

### 🌟 核心功能

*   **自适应搜索扩展 (Adaptive Search)**：自动调整过滤强度。当严格关键词匹配结果过少时，系统会智能放宽限制并引入高引用候选论文，确保文献覆盖的全面性。
*   **零幻觉证据系统**：每一项分析结论均附带原文直接引用（Evidence Quotes）。通过引入 **思维链 (CoT)** 推理和严格的领域约束，有效杜绝了无关语言（如 Arabic）或主题的幻觉。
*   **深度阅读流水线**：不仅限于摘要。系统自动获取 PDF 全文，利用先进技术提取文本，并针对高相关性论文进行多轮博弈分析。
*   **现代化 Web 界面**：基于 **FastAPI**、**WebSockets** 和 **Vue 3** 构建。支持实时进度流式显示、集成 PDF 查看以及报告的持久化访问。
*   **稳健的评分机制**：实现严格的 0-5 相关性评分体系，具备自动归一化和类型安全检查，确保评价结果的一致性与可靠性。

### 🏗️ 系统架构

*   `src/agents/`：针对特定角色优化的 LLM 智能体（学生、导师）。
*   `src/workflow.py`：系统核心逻辑，负责协调博弈流程与研究阶段。
*   `src/searcher.py`：集成多查询策略的高级学术搜索引擎。
*   `src/pdf_processor.py`：稳健的 PDF 下载与文本解析模块。
*   `src/server.py`：支持 WebSocket 实时通信的 FastAPI 后端。
*   `src/static/`：采用 Vue 3 和 Tailwind CSS 构建的响应式前端。

### 🚀 快速上手

#### 环境要求
*   **Python 3.10+**
*   **[Ollama](https://ollama.com/)**: 请确保已在本地安装并运行。
*   **默认模型**: `qwen2.5:7b` (因其卓越的推理能力及中英双语支持而被推荐)。

#### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/your-username/FindUrCite.git
cd FindUrCite

# 安装依赖 (推荐使用清华源以获得更快的下载速度)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 运行系统
1.  **启动 Web 界面 (推荐)**:
    ```bash
    python src/server.py
    ```
    访问地址：`http://localhost:8000`。

2.  **命令行运行**:
    ```bash
    python src/main.py "在此处输入您的研究想法或摘要"
    ```

---

## 📜 License / 许可证
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
