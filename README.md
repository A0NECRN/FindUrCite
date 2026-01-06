# FindUrCite - AI-Powered Research & Code Finder System
# FindUrCite - 智能文献与对标项目查找系统

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

FindUrCite is an advanced automated tool designed to help researchers find supporting literature and open-source code implementation based on their research ideas. It employs a **Multi-Agent Debate System** to ensure high-quality, hallucination-free analysis.

### 🌟 Key Features
1.  **Multi-Agent Adversarial Analysis**: Implements a "Student-Mentor" debate loop where one LLM agent analyzes the paper and another critiques it for hallucinations and weak reasoning, ensuring rigorous results.
2.  **Multi-Query Search Strategy**: Automatically generates diverse search queries (broad, specific, and technical) to maximize literature coverage across **Semantic Scholar** and **ArXiv**.
3.  **Deep Read Pipeline**: Automatically downloads PDFs for high-relevance papers and performs full-text analysis with **Evidence Quotes** extracted directly from the text.
4.  **Open-Source Project Discovery**: Automatically searches **GitHub** for relevant code implementations and benchmarks.
5.  **Privacy & Security**: All deep analysis runs locally via Ollama, ensuring your research ideas stay private.
6.  **Comprehensive Reports**: Generates a detailed 23-column Markdown report including problem definitions, methodologies, algorithm pseudocode, and limitations.

### 🚀 Installation & Usage

#### 1. Prerequisites
Ensure you have the following installed:
-   **Python 3.8+**
-   **Ollama** (The system will auto-configure the model)
-   **NVIDIA GPU Drivers** (Recommended CUDA 13.0 for local inference)

#### 2. Running the System
Simply double-click the startup script:
`run_system.bat`

Or run via terminal:
```bash
python src/main.py "Your research idea, draft text, or path/to/draft.txt" --output result.md
```

#### 3. View Results
The system generates a Markdown report containing:
-   **Full Paper Metadata**: Title, Year, Venue, Authors, Affiliations.
-   **Deep Analysis**: Problem math definitions, bottleneck analysis, algorithm flow, and experiments.
-   **Evidence Quotes**: Verbatim sentences from the paper supporting the analysis.
-   **Direct Links**: Links to papers, open-access PDFs, and GitHub repositories.

### 📁 Project Structure
-   `src/`: Source code
    -   `searcher.py`: Literature retrieval (Multi-query aggregation)
    -   `analyzer.py`: Multi-Agent Debate Logic (Student/Mentor)
    -   `code_finder.py`: GitHub code search (Parallel execution)
    -   `pdf_processor.py`: PDF download and text extraction
    -   `main.py`: Main workflow and report generation
-   `run_system.bat`: One-click startup script for Windows
-   `requirements.txt`: Python dependencies

---

<a name="chinese"></a>
## 中文

FindUrCite 是一个高级自动化工具，利用**多智能体博弈系统 (Multi-Agent Debate)** 来帮助研究人员查找支持文献和开源代码。

### 🌟 功能特点
1.  **多智能体对抗分析 (Multi-Agent Debate)**：引入“学生-导师”博弈机制。学生 Agent 分析论文，导师 Agent 进行严格审查（检查幻觉、证据缺失），通过多轮对话确保分析结果的真实性和高质量。
2.  **多维度搜索策略**：自动生成多组搜索关键词（涵盖宽泛主题、具体问题、细分术语），大幅提升在 **Semantic Scholar** 和 **ArXiv** 上的搜索广度。
3.  **深度阅读管线 (Deep Read Pipeline)**：对高相关性论文自动下载 PDF 并提取全文进行精读，直接从文中提取**原文佐证 (Evidence Quotes)**。
4.  **对标项目查找**：自动在 **GitHub** 查找相关的开源实现和对标项目。
5.  **隐私安全**：核心分析任务在本地通过 Ollama 运行，您的研究思路不会上传到云端。
6.  **详尽分析报告**：生成包含 23 个维度的详尽 Markdown 报告，涵盖问题数学定义、方法瓶颈、算法伪代码、缺陷分析等。

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
-   **原文佐证**：直接引用论文原文的关键句子，确保证据确凿。
-   **直接访问链接**：论文原文链接、Open Access PDF 下载链接、GitHub 仓库链接。

### 📁 目录结构
-   `src/`: 源代码
    -   `searcher.py`: 文献检索模块 (支持多查询聚合)
    -   `analyzer.py`: 多智能体博弈分析模块 (学生/导师模式)
    -   `code_finder.py`: GitHub 代码查找模块 (支持并行检索)
    -   `main.py`: 主程序与报告生成逻辑
-   `run_system.bat`: Windows 一键运行脚本
-   `requirements.txt`: Python 依赖项

### ⚠️ 注意事项
-   **首次运行**：系统会自动下载 AI 模型，请保持网络通畅。
-   **API 限制**：程序会自动处理 API 速率限制。
-   **免责声明**：分析结果由 AI 辅助生成，请务必核对原文。
