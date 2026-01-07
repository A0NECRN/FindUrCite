# 错误日志

| 日期 | 错误描述 | 修复状态 | 解决方案 |
|---|---|---|---|
| 2026-01-04 | `Analyzer` 对象缺少 `check_model` 属性导致初始化失败 | 已修复 | 在构造函数中移除对不存在方法的调用 |
| 2026-01-04 | Semantic Scholar API 访问频率限制 (429 Error) | 已修复 | 实现指数退避重试机制 (Exponential Backoff) |
| 2026-01-04 | LLM 在分析论文摘要时产生幻觉（编造方法或数据集） | 已修复 | 在 Prompt 中加入严格反幻觉指令及 "Not mentioned" 强制输出规则 |
| 2026-01-04 | 报告格式与用户 Excel 模板不一致 | 已修复 | 重构 `main.py` 和 `analyzer.py` 适配 21 列完整字段输出 |
| 2026-01-04 | 多源搜索串行执行导致响应缓慢 | 已优化 | 引入 `ThreadPoolExecutor` 实现并发搜索 (SS + ArXiv) |
| 2026-01-04 | 重复分析相同论文浪费 LLM 算力 | 已优化 | 实现 `AnalysisCache` 缓存机制，基于观点和摘要哈希命中缓存 |
| 2026-01-04 | 相关性评分不够精准，缺乏解释 | 已优化 | 引入 CoT 思维链，增加 `match_reasoning` 字段及报告“契合度”列 |
| 2026-01-04 | LLM 仅阅读摘要导致分析不够深入，缺乏原文佐证 | 已修复 | 构建“初筛-精读”双阶段流水线，对高分论文自动下载 PDF 并基于全文提取 Evidence Quotes |
| 2026-01-07 | `TypeError: '<' not supported between instances of 'dict' and 'int'` (Score Normalization) | 已修复 | 在 `WorkflowOrchestrator` 中增加 `_normalize_score` 方法，兼容处理 dict/int 类型输入并进行钳位 |
| 2026-01-07 | Windows 批处理脚本 `run.bat` 语法错误 (`&` 未转义) | 已修复 | 使用 `^&` 转义字符修复 echo 命令中的特殊符号 |
| 2026-01-07 | `[Errno 2] No such file or directory` (Report Generation) | 已修复 | 修复路径拼接问题（改用绝对路径）并在写入前增加目录存在性检查 |

