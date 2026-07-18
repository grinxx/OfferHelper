#!/usr/bin/env python3
"""Regression tests for score_job_matches scoring helpers."""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import score_job_matches as sc  # noqa: E402


class TokenizeTests(unittest.TestCase):
    def test_english_tokens(self):
        toks = set(sc.tokens("Python SQL Excel"))
        self.assertIn("python", toks)
        self.assertIn("excel", toks)

    def test_chinese_bigrams_enable_partial_overlap(self):
        # "数据分析" 与 "数据的分析" 应通过 bigram 共享 "数据"。
        source = set(sc.tokens("数据分析"))
        target = set(sc.tokens("数据的分析能力"))
        self.assertTrue(source & target, "expected bigram overlap between the two phrases")

    def test_short_noise_filtered(self):
        self.assertEqual(sc.tokens("a 的"), [])

    def test_bigram_fallback_when_no_segmenter(self):
        # 无论是否装 jieba，bigram fallback 本身必须能产生重叠 token。
        self.assertIn("数据", sc._bigrams("数据分析"))
        self.assertEqual(sc._bigrams("x"), [])


class KeywordScoreTests(unittest.TestCase):
    def test_empty_target_scores_zero(self):
        score, terms = sc.keyword_score("anything", "", 40)
        self.assertEqual(score, 0)
        self.assertEqual(terms, [])

    def test_overlap_bounded_by_max(self):
        score, _ = sc.keyword_score("python sql excel data", "python sql excel data", 40)
        self.assertLessEqual(score, 40)
        self.assertGreater(score, 0)

    def test_long_jd_not_penalized(self):
        # 命中 REFERENCE_TERMS 个关键词即接近满分，长 JD 的额外无关词不应压低分数。
        skills = " ".join(f"skill{i}" for i in range(sc.REFERENCE_TERMS))
        noise = " ".join(f"noise{i}" for i in range(50))
        score, _ = sc.keyword_score(skills, skills + " " + noise, 40)
        self.assertGreaterEqual(score, 36)

    def test_short_jd_requires_full_coverage(self):
        # 短 JD 分母取自身词数：只命中一半关键词只能拿一半分。
        score, _ = sc.keyword_score("python", "python sql", 40)
        self.assertEqual(score, 20)


class PriorityTests(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(sc.priority(85), "A_high_priority")
        self.assertEqual(sc.priority(75), "B_apply_selectively")
        self.assertEqual(sc.priority(65), "C_observation_pool")
        self.assertEqual(sc.priority(40), "D_not_recommended_now")


class RiskScoreTests(unittest.TestCase):
    def test_clean_job(self):
        score, hits = sc.risk_score("正常的产品运营岗位")
        self.assertEqual(score, 10)
        self.assertEqual(hits, [])

    def test_risky_job(self):
        score, hits = sc.risk_score("无经验高薪，先交费培训贷")
        self.assertLess(score, 10)
        self.assertTrue(hits)


class LoadProfileTests(unittest.TestCase):
    NESTED = (
        'name_or_alias: "示例同学"\n'
        "education:\n"
        '  school: "示例大学"\n'
        '  major: "信息管理"\n'
        "target_roles:\n"
        '  - "AI 应用实习生"\n'
        '  - "产品运营实习生"\n'
        "preferred_industries:\n"
        '  - "AI 应用"\n'
        "constraints:\n"
        '  job_type: "实习"\n'
        '  availability: "2周内"\n'
    )

    def test_interest_text_uses_roles_and_industries(self):
        profile = sc.load_profile(self.NESTED)
        interest = sc.profile_interest_text(profile)
        self.assertIn("产品运营实习生", interest)
        self.assertIn("AI 应用", interest)
        # 兴趣信号不应包含学校这类无关字段。
        self.assertNotIn("示例大学", interest)

    def test_constraint_text_uses_constraints(self):
        profile = sc.load_profile(self.NESTED)
        constraint = sc.profile_constraint_text(profile)
        self.assertIn("实习", constraint)
        self.assertIn("2周内", constraint)

    def test_experience_text_uses_education_only(self):
        # 经历信号只取教育背景，不能混入 target_roles / preferred_industries 意向字段，
        # 否则"我想投这个岗位"会被误算成"我有相关经历"。
        profile = sc.load_profile(self.NESTED)
        experience = sc.profile_experience_text(profile)
        self.assertIn("示例大学", experience)
        self.assertIn("信息管理", experience)
        self.assertNotIn("产品运营实习生", experience)
        self.assertNotIn("AI 应用", experience)


class FormatGapsTests(unittest.TestCase):
    def test_hard_not_specified_adds_manual_check_note(self):
        note = sc._format_gaps([], [], hard_specified=False)
        self.assertIn("JD未单列硬性要求", note)

    def test_hard_specified_omits_that_note(self):
        note = sc._format_gaps(["python"], ["sql"], hard_specified=True)
        self.assertNotIn("JD未单列硬性要求", note)
        self.assertIn("已覆盖", note)
        self.assertIn("待核对", note)


if __name__ == "__main__":
    unittest.main()
