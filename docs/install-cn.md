# 安装说明

## 最简方式：一行命令安装（推荐）

打开终端，粘贴并运行：

```bash
npx skills add grinxx/OfferHelper
```

命令会 clone 仓库、列出可安装的 Agent 供你选择，并在安装前展示安全扫描结果。安装完成后，重启 Agent 或新开会话，输入：

```text
$offer-helper
```

能触发 Skill 即安装成功。

> 这也是让 OfferHelper 出现在 [skills.sh](https://skills.sh/grinxx/OfferHelper) 统计中的方式——每次通过该命令安装都会计入匿名安装量。

---

## 方式二：让 Agent 帮你安装

在 Claude Code 或其他支持 Skill 的 Agent 里说：

```text
帮我安装这个 Skill：https://github.com/grinxx/OfferHelper
```

Agent 会自动完成安装，重启后生效。

---

## 方式三：手动安装（备用）

### 下载 ZIP（不需要 git）

1. 打开 https://github.com/grinxx/OfferHelper
2. 点击绿色 **Code** 按钮 → **Download ZIP**
3. 解压后，将整个文件夹复制到对应目录：

| Agent | 安装目录 |
| --- | --- |
| Claude Code | `~/.claude/skills/offer-helper` |
| Codex | `~/.codex/skills/offer-helper` |
| 项目级（所有 Agent）| `.agents/skills/offer-helper`（在项目根目录） |

### 使用安装脚本指定 Agent

```bash
# 安装到 Claude Code（默认）
python3 scripts/install_local.py

# 安装到 Codex
python3 scripts/install_local.py --agent codex

# 安装到当前项目（项目级）
python3 scripts/install_local.py --project

# 覆盖已有安装
python3 scripts/install_local.py --force
```

### 使用 git clone

```bash
# Claude Code 个人级
git clone https://github.com/grinxx/OfferHelper.git ~/.claude/skills/offer-helper

# 项目级
git clone https://github.com/grinxx/OfferHelper.git .agents/skills/offer-helper
```

---

## 国内网络建议

- GitHub 访问慢时，优先使用 ZIP 下载方式。
- 安装可选的 PDF/DOCX 解析依赖（不影响基础使用）：

```bash
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements-optional.txt
```

---

## 验证安装

重启 Agent 或新开会话后输入：

```text
$offer-helper
```

看到 Skill 响应即安装成功。如果没有响应，检查文件夹是否放对了目录。
