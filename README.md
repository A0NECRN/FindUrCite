# FindUrCite: AI-Powered Research Assistant with Multi-Agent Dialectical Debate
# FindUrCite: 基于多智能体辩证博弈的 AI 科研深度分析系统

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## 🇬🇧 English

**FindUrCite** is a professional-grade academic research automation framework designed to mitigate LLM hallucinations and enhance the rigor of literature analysis. By implementing a **Dialectical Multi-Agent System (MAS)**, it simulates a high-stakes academic defense between a **Student Agent** and a **Senior Advisor Agent**, ensuring that every research insight is grounded in empirical evidence.

### 核心设计哲学 / Core Philosophy: "Dialectic over Generative"
Unlike traditional AI tools that merely summarize, FindUrCite **challenges** findings. It treats every paper as a hypothesis that must survive a multi-round "adversarial interrogation" before being accepted into the final report.

---

### 🌟 Key Capabilities

#### 1. Dialectical Multi-Agent Debate (Student-Advisor Loop)
The system orchestrates a sophisticated interaction between two specialized LLM personas:
*   **Student Agent**: Responsible for initial hypothesis generation, deep reading, and evidence extraction.
*   **Advisor Agent**: Acts as a "Devil's Advocate." It performs strict evidence-checking, identifies logical inconsistencies, and challenges the relevance of the paper to the user's specific context.
*   **Dynamic Debate Phases**:
    *   **Phase 1: Screening**: Rapid relevance and validity check.
    *   **Phase 2: Interrogation**: For high-potential papers, the Advisor demands direct quotes and scrutinizes methodology, forcing the Student to "reflect" and "defend" their analysis.

#### 2. Advanced Multi-Dimensional Scoring (0-10 Granularity)
Each candidate paper is evaluated across four critical academic dimensions:
*   **Relevance**: Degree of alignment with the user's core research problem.
*   **Innovation**: Novelty of the proposed methodology or theoretical framework.
*   **Reliability**: Technical rigor, experimental design, and reproducibility.
*   **Potential**: Strategic value for future research and gap filling.

#### 3. Zero-Hallucination Evidence System
Utilizing a **Chain-of-Thought (CoT)** reasoning engine, the system enforces a strict "No Evidence, No Claim" policy. Every analytical point must be mapped to a direct quote from the source text, ensuring the output is purely evidence-grounded.

#### 4. Heuristic Search & Deep Read Pipeline
*   **Adaptive Search**: Automatically expands or constrains search queries based on initial result quality.
*   **Full-Text Extraction**: Automatically downloads and parses PDFs for high-relevance candidates, performing analysis on the actual body text rather than just the abstract.

---

### 🏗️ Technical Architecture

*   **`src/agents/`**: Optimized LLM personas with distinct system prompts and reasoning chains.
*   **`src/workflow.py`**: The orchestration engine managing the state-machine of the debate and consensus reaching.
*   **`src/pdf_processor.py`**: Robust PDF ingestion and semantic text extraction.
*   **`src/server.py`**: High-concurrency FastAPI backend with WebSocket-based real-time event streaming.

---

### 🚀 Getting Started

#### Prerequisites
*   **Python 3.10+**
*   **[Ollama](https://ollama.com/)**: Local LLM inference engine.
*   **Recommended Model**: `qwen2.5:7b` or higher for optimal dialectical reasoning.

#### One-Click Installation (Windows)
FindUrCite provides a fully automated deployment script. Simply run:
```bash
run.bat
```
This script automates:
1. Environment verification (Python, Ollama).
2. Virtual environment (`venv`) initialization and dependency installation.
3. Automated model pulling (`ollama pull qwen2.5:7b`).
4. Server deployment and automatic browser launch.

---

<a name="chinese"></a>

## 🇨🇳 中文

**FindUrCite** 是一款面向专业科研人员的自动化文献深度分析系统。它通过构建**辩证式多智能体博弈 (MAS)** 架构，模拟了导师（Advisor）与学生（Student）之间的学术辩论，旨在解决大语言模型在科研分析中的“幻觉”问题，确保每一项结论都具备严谨的证据支撑。

### 核心设计哲学：“辩证优于生成”
不同于传统的 AI 摘要工具，FindUrCite 强调 **“质疑”**。它将每一篇论文视为一个需要经受多轮“对抗式质询”的假设，只有通过导师 Agent 严格审核的论文，才能进入最终的合成报告。

---

### 🌟 核心功能特性

#### 1. 辩证式多智能体博弈逻辑
系统通过两个具备不同思维倾向的智能体进行交互：
*   **学生智能体 (Student)**：负责初步分析、全文阅读及证据提取。
*   **导师智能体 (Advisor)**：扮演“魔鬼代言人”。负责严格审查证据、识别逻辑矛盾、挑战论文与用户课题的相关性。
*   **动态博弈阶段**：
    *   **初筛阶段 (Screening)**：快速评估论文的相关性与基础效度。
    *   **质询阶段 (Interrogation)**：针对高分论文，导师会强制要求提供原文引证，并对实验细节进行深度挖掘，迫使学生进行“反思”与“辩护”。

#### 2. 精细化多维度评分体系 (0-10 分制)
系统从四个核心学术维度对文献进行量化评估：
*   **相关性 (Relevance)**：与用户核心研究问题的契合程度。
*   **创新性 (Innovation)**：所提方法或理论框架的新颖性。
*   **可靠性 (Reliability)**：技术严谨性、实验设计及可复现性。
*   **潜力 (Potential)**：对未来工作的启发价值及补位空间。

#### 3. 零幻觉证据支撑系统
基于 **思维链 (CoT)** 推理引擎，系统执行严格的“无证据不结论”策略。所有的分析结论必须映射到原文的直接引用（Evidence Quotes），从根本上杜绝了 AI 编造实验数据或结论的可能。

#### 4. 启发式搜索与深度阅读流水线
*   **自适应搜索**：根据初始搜索质量，智能扩展或收缩查询关键词。
*   **全文解析**：针对高价值文献，系统自动下载并解析 PDF 全文，跳过摘要表象，深入分析核心算法与实验部分。

---

### 🚀 快速上手

#### 环境准备
*   **Python 3.10+**
*   **[Ollama](https://ollama.com/)**: 本地 LLM 推理引擎。
*   **推荐模型**: `qwen2.5:7b` 或更高版本。

#### 一键启动 (Windows)
FindUrCite 提供全自动化部署脚本，只需运行：
```bash
run.bat
```
脚本将自动完成：
1. 环境检查（Python, Ollama）。
2. 虚拟环境创建及依赖安装（自动使用清华源）。
3. 模型自动下载 (`qwen2.5:7b`)。
4. 启动后端服务并自动打开 Web 研究界面。

---

## 📜 许可证
本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
