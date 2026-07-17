# 投递跟进规则（Followup Rules）

用于在 `application-tracker.csv` 中填写 `followup_due` 和 `followup_action` 字段，确保每条投递都有明确的后续动作，不会断掉。

## 状态与跟进规则

| 当前状态（status） | 投递后天数 | followup_action |
| --- | --- | --- |
| `submitted`（已投递） | 第 5 天无回音 | 检查投递是否成功；考虑换平台重投或优化简历再投 |
| `submitted`（已投递） | 第 10 天无回音 | 标记为 `no_response`，放入观察池，不再等待 |
| `viewed`（已查看） | 第 3 天无进展 | 可尝试在平台上补充一条简短的求职意向备注（用户手动） |
| `interview_scheduled`（已约面试） | 面试前 1 天 | 复习岗位 JD、准备自我介绍、检查 interview-story-bank.md |
| `interviewed`（已面试） | 第 1 天 | 趁热写面试复盘到 review-log.md，记录被问到的问题和自己的回答 |
| `interviewed`（已面试） | 第 5 天无回音 | 可询问进度（用户手动）；同时继续投其他岗位 |
| `offer`（收到 offer） | 当天 | 核对薪资、职级、部门、试用期、签约条款；不要立即口头承诺 |
| `rejected`（被拒） | 当天 | 写复盘到 review-log.md：被拒原因假设、下次改进点 |
| `no_response`（无回应） | — | 每两周检查一次，岗位是否仍开放；考虑是否补强后重新申请 |
| `withdrawn`（主动放弃） | — | 记录原因，更新 target-roles.csv 中对该类岗位的评估 |

## followup_due 填写规则

- 格式：`yyyy-mm-dd`
- 等于投递日期加上上表对应的天数
- 若已有回音（如进入面试），更新为面试相关的跟进日期

## 复盘触发条件

满足以下任一条件时，提示用户做一次整体复盘：

- 累计投递达到 5 条
- 距离上次复盘超过 7 天
- 连续收到 3 条拒信
- 收到第一个 offer

复盘时更新 `review-log.md`，重点回答：
1. 哪类岗位回复率更高？
2. 哪份简历版本效果更好？
3. 面试中反复被追问的是什么？
4. 下一步要补强的证据是什么？
