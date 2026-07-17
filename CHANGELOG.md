# Changelog

## 0.2.0

- 改名为 OfferHelper，触发名更新为 `$offer-helper`。
- 全面中文化 references/ 目录下的规则文件，保留技术术语英文。
- 新增首次启动三问引导流程，支持应届/换工作/转行三条路径。
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
- 简化 Quick Start：推荐使用 Agent 一句话安装，手动安装降级为备用方式。
- 安装说明面向 Codex、Claude Code 和其他支持 Skill 的 Agent。
