# FindUrCite - AI-Powered Research & Code Finder System
# FindUrCite - 智能文献与对标项目查找系统

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

FindUrCite is an automated tool designed to help researchers automatically find supporting literature and open-source code implementation based on their research ideas or draft texts.

### 🌟 Key Features
1.  **Automatic Keyword Extraction**: Uses local LLM (Qwen2.5) to understand your research viewpoints and extract precise search terms.
2.  **Multi-Source Literature Search**: Covers **Semantic Scholar** and **ArXiv** for comprehensive academic coverage.
3.  **Intelligent Relevance Analysis**: Automatically analyzes abstracts to evaluate support/relevance against your viewpoint with **strict anti-hallucination** rules.
4.  **Open-Source Project Discovery**: Automatically searches **GitHub** for relevant code implementations and benchmarks.
5.  **Privacy & Security**: All deep analysis runs locally via Ollama, ensuring your research ideas stay private.
6.  **Comprehensive Reports**: Generates a detailed 21-column Markdown report including problem definitions, methodologies, algorithm pseudocode, and limitations.

### 🚀 Installation & Usage

#### 1. Prerequisites
Ensure you have the following installed:
-   **Python 3.8+**
-   **Ollama** (The system will attempt to auto-configure the model)
-   **NVIDIA GPU Drivers** (Recommended CUDA 13.0 for local inference)

#### 2. Running the System
Simply double-click the startup script:
`run_system.bat`

Or run via terminal:
```bash
python src/main.py "Your research idea, draft text, or path/to/draft.txt" --output result.md
```

#### 3. View Results
The system generates a Markdown report (e.g., `research_result.md`) containing:
-   **Full Paper Metadata**: Title, Year, Venue, Authors, Affiliations.
-   **Deep Analysis**: Problem math definitions, bottleneck analysis, algorithm flow, and experiments.
-   **Direct Links**: Links to papers, open-access PDFs, and GitHub repositories (with star counts).

### 📁 Project Structure
-   `src/`: Source code
    -   `searcher.py`: Literature retrieval (Semantic Scholar & ArXiv)
    -   `analyzer.py`: LLM Analysis & Input Processing
    -   `code_finder.py`: GitHub code search (Parallel execution)
    -   `main.py`: Main workflow and report generation
-   `run_system.bat`: One-click startup script for Windows
-   `requirements.txt`: Python dependencies

---

<a name="chinese"></a>
## 中文

FindUrCite 这是一个自动化工具，旨在帮助研究人员根据研究观点或草稿自动查找支持文献和开源代码实现。

### 🌟 功能特点
1.  **自动提取关键词**：利用本地大模型 (Qwen2.5) 深度理解您的研究观点，提取精确的搜索关键词。
2.  **多源文献检索**：同时覆盖 **Semantic Scholar** 和 **ArXiv**，确保学术覆盖面。
3.  **智能相关性分析**：自动阅读摘要，分析文献是否支持您的观点，并遵循**严格的反幻觉**指令。
4.  **对标项目查找**：自动在 **GitHub** 查找相关的开源实现和对标项目。
5.  **隐私安全**：核心分析任务在本地通过 Ollama 运行，您的研究思路不会上传到云端。
6.  **详尽分析报告**：生成包含 21 个维度的详尽 Markdown 报告，涵盖问题数学定义、方法瓶颈、算法伪代码、缺陷分析等。

### 🚀 安装与使用

#### 1. 准备环境
确保您已安装：
-   **Python 3.8+**
-   **Ollama** (系统会自动尝试配置所需模型)
-   **NVIDIA 显卡驱动** (推荐 CUDA 13.0 以支持本地推理加速)

#### 2. 运行系统
只需双击运行目录下的脚本：
`run_system.bat`

或者在终端运行：
```bash
python src/main.py "您的研究观点、草稿内容或 .txt 文件路径" --output 结果.md
```

#### 3. 查看结果
运行结束后，系统会生成 Markdown 报告文件，包含：
-   **完整论文元数据**：题目、年份、发表期刊/会议、作者信息、单位信息。
-   **深度学术分析**：问题定义、方法论、算法流程、实验设置。
-   **直接访问链接**：论文原文链接、Open Access PDF 下载链接、GitHub 仓库链接（含 Star 数）。

### 📁 目录结构
-   `src/`: 源代码
    -   `searcher.py`: 文献检索模块 (支持 SS 与 ArXiv)
    -   `analyzer.py`: LLM 分析与输入处理模块
    -   `code_finder.py`: GitHub 代码查找模块 (支持并行检索)
    -   `main.py`: 主程序与报告生成逻辑
-   `run_system.bat`: Windows 一键运行脚本
-   `requirements.txt`: Python 依赖项

### ⚠️ 注意事项
-   **首次运行**：系统会自动下载约 4.7GB 的 AI 模型，请保持网络通畅。
-   **API 限制**：Semantic Scholar API 有访问频率限制，程序遇到限制时会自动指数退避并重试。
-   **免责声明**：分析结果由 AI 基于摘要推断，仅供参考，请务必核对原文。
