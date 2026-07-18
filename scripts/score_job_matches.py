#!/usr/bin/env python3
"""Score normalized jobs against a profile and strengths text.

重要说明：
本脚本只做关键词初筛，不替代人工判断。评分有以下局限性：

1. 行业差异：互联网、国企、外企、金融、咨询的录用逻辑差别很大，脚本无法感知。
2. 校招 vs 社招：应届生校招更看重学校背景和潜力，社招更看重具体经验，脚本不区分。
3. 硬性条件：学历、专业、证书等硬性卡线需要用户人工核对，脚本只做关键词匹配。
4. 公司规模与阶段：同一岗位在大厂和初创公司的要求和机会完全不同，脚本不区分。
5. 潜规则：部分岗位有隐性要求（如背景、关系、特定学校），脚本无法识别。

评分仅用于初步排序，最终是否投递请用户自己判断。
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re


RISK_TERMS = ["培训贷", "贷款", "包就业", "无经验高薪", "先交费", "保offer", "刷流水", "纯销售"]

SCORE_DISCLAIMER = (
    "⚠️ 关键词初筛分数，不反映真实录取概率。"
    "行业/公司类型/校招社招差异需人工判断。"
)


def read_text(path: str | None) -> str:
    if not path:
        return ""
    file_path = pathlib.Path(path)
    return file_path.read_text(encoding="utf-8") if file_path.exists() else ""


def load_profile(text: str) -> dict:
    """Parse profile.yaml into a dict.

    优先使用 PyYAML（若已安装），否则回退到一个能处理常见嵌套/列表结构的
    轻量解析器。回退解析器只覆盖本项目模板用到的两级缩进，不追求完整 YAML。
    """
    if not text.strip():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return _fallback_parse_yaml(text)
    try:
        data = yaml.safe_load(text)
    except Exception:
        return _fallback_parse_yaml(text)
    return data if isinstance(data, dict) else {}


def _fallback_parse_yaml(text: str) -> dict:
    """Handle flat keys, one-level nested maps, and `- ` list items."""
    result: dict = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.strip().startswith("#") else ""
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if stripped.startswith("- "):
            item = _clean_scalar(stripped[2:])
            if current_key is not None:
                if not isinstance(result.get(current_key), list):
                    result[current_key] = []
                result[current_key].append(item)
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if indent == 0:
            current_key = key
            result[key] = _clean_scalar(value) if value else None
        else:
            # 嵌套 key: value —— 该顶层键是一个 map。
            if not isinstance(result.get(current_key), dict):
                result[current_key] = {}
            result[current_key][key] = _clean_scalar(value) if value else ""
    return result


def _clean_scalar(value: str) -> str:
    return value.strip().strip('"').strip("'").strip()


def _flatten_values(node) -> list[str]:
    """Collect all scalar string values from a nested structure."""
    values: list[str] = []
    if isinstance(node, dict):
        for v in node.values():
            values.extend(_flatten_values(v))
    elif isinstance(node, list):
        for v in node:
            values.extend(_flatten_values(v))
    elif node is not None:
        text = str(node).strip()
        if text:
            values.append(text)
    return values


INTEREST_FIELDS = ["target_roles", "preferred_industries", "target_city"]
CONSTRAINT_FIELDS = ["constraints", "target_city", "unavailable_roles"]


def profile_interest_text(profile: dict) -> str:
    """User's stated direction/interest — target roles and industries.

    这与岗位匹配度（fit/hard）不同：它衡量用户*想去哪个方向*，而不是经历是否
    符合岗位要求。因此只取目标岗位、偏好行业和目标城市等意向字段。
    """
    parts: list[str] = []
    for field in INTEREST_FIELDS:
        parts.extend(_flatten_values(profile.get(field)))
    return " ".join(parts)


def profile_constraint_text(profile: dict) -> str:
    """Realistic constraints — job type, availability, city, exclusions."""
    parts: list[str] = []
    for field in CONSTRAINT_FIELDS:
        parts.extend(_flatten_values(profile.get(field)))
    return " ".join(parts)


def tokens(text: str) -> list[str]:
    """Tokenize mixed CN/EN text.

    英文/数字按词切分。中文优先用 jieba 切成真实词（若已安装），
    否则回退到相邻两字的 bigram 滑窗，保证 "数据分析" 与 "数据的分析"
    仍能通过 "数据" 部分重叠。
    """
    result: list[str] = []
    for chunk in re.findall(r"[A-Za-z0-9+#.]+|[一-鿿]+", text.lower()):
        if chunk[0].isascii():
            if len(chunk.strip()) >= 2:
                result.append(chunk)
        else:
            result.extend(_segment_chinese(chunk))
    return result


def _bigrams(chunk: str) -> list[str]:
    if len(chunk) < 2:
        return []
    return [chunk[i:i + 2] for i in range(len(chunk) - 1)]


def _segment_chinese(chunk: str) -> list[str]:
    seg = _jieba_cut(chunk)
    if seg is None:
        return _bigrams(chunk)
    words = [w for w in seg if len(w) >= 2]
    # jieba 若把整段切成全是单字（无 >=2 的词），退回 bigram 保召回。
    return words or _bigrams(chunk)


_JIEBA = None
_JIEBA_TRIED = False


def _jieba_cut(chunk: str):
    global _JIEBA, _JIEBA_TRIED
    if not _JIEBA_TRIED:
        _JIEBA_TRIED = True
        try:
            import jieba  # type: ignore
            jieba.setLogLevel("ERROR")
            _JIEBA = jieba
        except Exception:
            _JIEBA = None
    if _JIEBA is None:
        return None
    # cut_for_search 同时产出复合词和子词（如 数据分析 -> 数据/分析/数据分析），
    # 兼顾展示可读性与关键词召回。
    return list(_JIEBA.cut_for_search(chunk))


def keyword_score(source: str, target: str, max_points: int) -> tuple[int, list[str]]:
    source_terms = set(tokens(source))
    target_terms = set(tokens(target))
    if not target_terms:
        return 0, []
    overlap = sorted(source_terms & target_terms)
    score = min(max_points, round(max_points * len(overlap) / max(5, len(target_terms))))
    return score, overlap[:12]


def practical_score(constraint_text: str, job_text: str) -> int:
    if not constraint_text.strip():
        return 8
    score, _ = keyword_score(constraint_text, job_text, 15)
    return max(5, score)


def risk_score(job_text: str) -> tuple[int, list[str]]:
    hits = [term for term in RISK_TERMS if term in job_text]
    return max(0, 10 - len(hits) * 3), hits


def priority(score: int) -> str:
    if score >= 80:
        return "A_high_priority"
    if score >= 70:
        return "B_apply_selectively"
    if score >= 60:
        return "C_observation_pool"
    return "D_not_recommended_now"


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _format_gaps(covered: list[str], uncovered: list[str]) -> str:
    parts: list[str] = []
    if covered:
        parts.append("已覆盖: " + "、".join(covered[:8]))
    if uncovered:
        parts.append("待核对: " + "、".join(uncovered[:8]))
    parts.append("学历/专业/证书/城市等硬性条件仍需用户人工核对")
    return "；".join(parts)


def _format_resume_focus(fit_terms: list[str], uncovered: list[str]) -> str:
    if fit_terms:
        return "突出与JD重合的真实经历关键词: " + "、".join(fit_terms[:8])
    if uncovered:
        return "JD重点但缺证据，需补强: " + "、".join(uncovered[:8])
    return "强化与JD重合的真实项目、工具、动作和结果"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--strengths", required=True)
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile_text = read_text(args.profile)
    strengths_text = read_text(args.strengths)
    profile = load_profile(profile_text)
    interest_text = profile_interest_text(profile)
    constraint_text = profile_constraint_text(profile)
    # 匹配度基于真实经历（简历/优势），不掺入意向字段。
    evidence_text = profile_text + "\n" + strengths_text

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("⚠️  评分局限性提示：")
    print("  - 本脚本只做关键词初筛，不反映真实录取概率")
    print("  - 行业差异（互联网/国企/外企/金融）需人工判断")
    print("  - 校招 vs 社招逻辑不同，脚本不区分")
    print("  - 硬性条件（学历/证书/专业）需用户人工核对")
    print()

    rows: list[dict[str, str | int]] = []
    for line in pathlib.Path(args.jobs).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        job = json.loads(line)
        job_text = " ".join(str(job.get(k, "")) for k in ["title", "company", "city", "jd_text", "hard_requirements", "nice_to_have"])
        hard_req_text = str(job.get("hard_requirements") or job.get("jd_text", ""))
        fit, fit_terms = keyword_score(evidence_text, job_text, 40)
        hard, hard_terms = keyword_score(evidence_text, hard_req_text, 20)
        # interest 衡量用户意向方向（目标岗位/行业/城市），与 fit/hard 解耦。
        interest, interest_terms = keyword_score(
            interest_text, job_text + " " + str(job.get("user_interest", "")), 15
        )
        practical = practical_score(constraint_text, job_text)
        risk, risk_hits = risk_score(job_text)
        total = fit + hard + interest + practical + risk

        hard_req_terms = set(tokens(hard_req_text))
        covered = sorted(t for t in hard_terms if t in hard_req_terms)
        uncovered = sorted(hard_req_terms - set(hard_terms))
        must_have_gaps = _format_gaps(covered, uncovered)
        resume_focus = _format_resume_focus(fit_terms, uncovered)

        rows.append({
            "job_id": job.get("job_id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "platform": job.get("platform", ""),
            "match_score": total,
            "score_note": SCORE_DISCLAIMER,
            "must_have_gaps": must_have_gaps,
            "matching_evidence": "、".join(_dedupe(fit_terms + hard_terms + interest_terms)[:12]),
            "resume_focus": resume_focus,
            "apply_priority": priority(total),
            "next_action": "用户阅读JD并手动确认是否进入简历定制" if total >= 60 else "暂不建议投递；补证据或放入观察池",
            "risk_flags": "、".join(risk_hits) if risk_hits else "无",
        })

    fieldnames = ["job_id", "title", "company", "platform", "match_score", "score_note", "must_have_gaps", "matching_evidence", "resume_focus", "apply_priority", "next_action", "risk_flags"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"已输出 {len(rows)} 条评分结果到 {output_path}")
    print("请结合实际情况人工复核后再决定是否投递。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
