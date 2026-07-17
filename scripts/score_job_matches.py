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


def simple_yaml_values(text: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        stripped = line.strip().strip("-").strip().strip('"').strip("'")
        if not stripped or stripped.endswith(":"):
            continue
        if ":" in stripped:
            stripped = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        if stripped:
            values.append(stripped)
    return values


def tokens(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9+#.]+|[一-鿿]{2,}", text.lower())
    return [w for w in words if len(w.strip()) >= 2]


def keyword_score(source: str, target: str, max_points: int) -> tuple[int, list[str]]:
    source_terms = set(tokens(source))
    target_terms = set(tokens(target))
    if not target_terms:
        return 0, []
    overlap = sorted(source_terms & target_terms)
    score = min(max_points, round(max_points * len(overlap) / max(5, len(target_terms))))
    return score, overlap[:12]


def practical_score(profile_values: list[str], job_text: str) -> int:
    if not profile_values:
        return 8
    joined = " ".join(profile_values)
    score, _ = keyword_score(joined, job_text, 15)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--strengths", required=True)
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile_text = read_text(args.profile)
    strengths_text = read_text(args.strengths)
    profile_values = simple_yaml_values(profile_text)
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
        fit, fit_terms = keyword_score(evidence_text, job_text, 40)
        hard, hard_terms = keyword_score(evidence_text, str(job.get("hard_requirements") or job.get("jd_text", "")), 20)
        interest, interest_terms = keyword_score(" ".join(profile_values), job_text + " " + str(job.get("user_interest", "")), 15)
        practical = practical_score(profile_values, job_text)
        risk, risk_hits = risk_score(job_text)
        total = fit + hard + interest + practical + risk
        rows.append({
            "job_id": job.get("job_id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "platform": job.get("platform", ""),
            "match_score": total,
            "score_note": SCORE_DISCLAIMER,
            "must_have_gaps": "硬性条件需用户人工核对（学历/专业/证书/城市）",
            "matching_evidence": "、".join((fit_terms + hard_terms + interest_terms)[:12]),
            "resume_focus": "强化与JD重合的真实项目、工具、动作和结果",
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
