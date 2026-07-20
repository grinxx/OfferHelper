# Changelog

## 0.3.1

- 评分脚本修正长 JD 惩罚：匹配度分母改为 `min(JD词数, 8)`，详细的长 JD 不再被系统性压低分数。
- 评分脚本修正 fit/hard 重复计分：岗位未单列 `hard_requirements` 时不再回退到 `jd_text`，改给中性基准分并提示人工核对。
- 岗位匹配只使用真实经历（`experience-assets.md` + `strengths.md` + 教育背景），新增 `--experience` 参数；`target_roles`/`preferred_industries` 等意向字段不再被误当作经历。
- 评分脚本增强：PyYAML 缺失时回退到内置轻量解析器；中文优先用 jieba 分词，缺失时回退 bigram。
- `normalize_jobs.py` 修正：文件首个文本块能被正确解析、标题行不混入 `jd_text`；Markdown 表格漏写 `|---|` 分隔行时不再丢弃首个数据行；移除未使用导入。
- 新增 `tests/` 回归测试（评分与解析），覆盖可选依赖缺失的降级路径。
- README 新增“更新到最新版本”说明。

## 0.3.0

- 目标群体聚焦为**应届生和在校生**，移除换工作/转行分支。
- 首次启动引导改为三分支：在校找实习/校招、应届找全职、其他。
- `profile.yaml` 模板新增 `accept_conversion` 字段（是否接受实习转正）。
- `references/job-matching-rubric.md` 新增校招专项评估模块，经历维度改为课程项目/竞赛/实习。
- `references/interview-training.md` 新增应届生高频 10 题和职业规划表达审查。
- `references/intake-flow.md` 经历挖掘重写，优先课程项目、竞赛、社团、实习。
- README 和文档定位更新为"应届生/在校生专属"。

## 0.2.0

- 改名为 OfferHelper，触发名更新为 `$offer-helper`。
- 全面中文化 references/ 目录下的规则文件，保留技术术语英文。
- 新增首次启动三问引导流程。
- 新增 `references/followup-rules.md`，定义各投递状态的后续动作和复盘触发条件。
- `application-tracker.csv` 新增 `followup_due`、`followup_action` 字段。
- `review-log.md` 新增周复盘模板。
- 所有模板字段改为中文，降低普通用户门槛。
- 安装脚本默认目录改为 Claude Code，新增 `--agent` 参数支持多 Agent。
- 评分脚本加入局限性说明，输出新增 `score_note` 字段。

## 0.1.0

- 初始发布 Skill。
- 支持中文求职 Intake、优势挖掘、岗位匹配、简历优化、面试训练和投递跟踪。
- 提供 PDF/DOCX/TXT/Markdown 简历文本提取脚本。
- 提供 JD 标准化和岗位匹配评分脚本。
- 提供国内用户安装说明、使用指南、FAQ 和安全边界说明。
- 简化 Quick Start：推荐使用 `npx skills add` 安装，手动安装降级为备用方式。
- 安装说明面向 Codex、Claude Code 和其他支持 Skill 的 Agent。
