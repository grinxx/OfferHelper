# FAQ

## OfferHelper 适合什么人用？

主要面向**应届生和在校生**，包括：

- 大三/大四找暑期实习或校招的本科生；
- 研究生找实习或校招；
- 应届毕业生找第一份全职工作。

如果你已经有几年工作经验在找跳槽机会，OfferHelper 目前不是最合适的工具。

## OfferHelper 是自动投递工具吗？

不是。OfferHelper 只做求职准备、岗位整理、匹配分析、简历建议和面试训练。任何投递动作都应由用户自己确认并执行。

## 它能帮我编项目经历吗？

不能。OfferHelper 会拒绝伪造经历，并把需求转成合规替代方案，例如：补一个真实 Demo、整理已有课程项目、写清实际参与部分。

## 没有实习经历能用吗？

可以。OfferHelper 会从课程作业、社团、比赛、自学、兼职、作品集、失败经历中挖掘可证明的能力，但不会把普通经历包装成不存在的实习。

## 需要联网吗？

基础流程不需要联网。岗位信息默认由用户粘贴、截图或导出提供。安装可选依赖、从 GitHub 更新 Skill 时需要联网。

## 支持 Boss 直聘、猎聘、领英吗？

支持整理用户提供的 JD、截图、链接和导出表。不支持绕过登录、不支持批量抓取、不支持自动私信或自动投递。

## 支持 PDF 和 DOCX 简历吗？

支持，但需要安装可选依赖：

```bash
python3 -m pip install -r requirements-optional.txt
```

国内网络可以用清华 PyPI 镜像：

```bash
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements-optional.txt
```

## 触发名是什么？

安装后在 Agent 中输入：

```text
$offer-helper
```

## 可以商用或二次修改吗？

可以。项目使用 MIT License。二次发布时请保留许可证声明，并自行承担合规责任。
