# FindUrCite - 智能文献与对标项目查找系统

这是一个自动化工具，旨在帮助研究人员根据观点自动查找支持文献和开源代码。

## 功能特点
1. **自动提取关键词**：利用本地大模型 (Qwen2.5) 理解您的研究观点。
2. **多源文献检索**：覆盖 Semantic Scholar 和 ArXiv。
3. **智能相关性分析**：自动阅读摘要，判断文献是否支持您的观点。
4. **对标项目查找**：自动在 GitHub 查找相关的开源实现。
5. **隐私安全**：所有分析在本地运行，无需上传数据。

## 安装与使用

### 1. 准备环境
确保您已安装：
- Python 3.8+
- Ollama (已为您自动配置)
- NVIDIA 显卡驱动 (CUDA 13.0)

### 2. 运行系统
只需双击运行目录下的脚本：
`run_system.bat`

或者在终端运行：
```bash
python src/main.py "您的研究观点或问题"
```

### 3. 查看结果
运行结束后，系统会生成 `research_result.md` 文件，包含：
- 相关论文列表
- 智能分析结果（支持/反驳/相关度评分）
- 对应的 GitHub 代码仓库链接

## 目录结构
- `src/`: 源代码
  - `searcher.py`: 文献检索模块
  - `analyzer.py`: LLM 分析模块
  - `code_finder.py`: 代码查找模块
  - `main.py`: 主程序
- `research_result.md`: 输出报告
- `requirements.txt`: Python 依赖

## 常见问题
- **Q: 运行速度慢？**
  - A: 第一次运行时需要下载 AI 模型 (4.7GB)，请耐心等待。
  - A: Semantic Scholar API 有访问频率限制，程序会自动等待重试。

- **Q: 报错 Ollama not reachable?**
  - A: 请确保 Ollama 服务已启动。`run_system.bat` 会尝试自动启动它。
