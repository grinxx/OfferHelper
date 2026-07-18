#!/usr/bin/env python3
"""Regression tests for normalize_jobs parsing."""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import normalize_jobs as nj  # noqa: E402


class ParseMarkdownTableTests(unittest.TestCase):
    def test_basic_table(self):
        text = (
            "| platform | company | title | city |\n"
            "| --- | --- | --- | --- |\n"
            "| Boss直聘 | 示例科技 | 产品运营实习生 | 深圳 |\n"
        )
        rows = nj.parse_markdown_table(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["company"], "示例科技")
        self.assertEqual(rows[0]["city"], "深圳")

    def test_short_row_is_padded(self):
        text = (
            "| platform | company | title | city |\n"
            "| --- | --- | --- | --- |\n"
            "| Boss直聘 | 示例科技 |\n"
        )
        rows = nj.parse_markdown_table(text)
        self.assertEqual(rows[0]["title"], "")
        self.assertEqual(rows[0]["city"], "")

    def test_no_table_returns_empty(self):
        self.assertEqual(nj.parse_markdown_table("just some text"), [])

    def test_table_without_separator_keeps_first_data_row(self):
        # 用户漏写 |---| 分隔行时，首个数据行不能被当成分隔行丢弃（回归 E）。
        text = (
            "| platform | company | title | city |\n"
            "| Boss直聘 | 示例科技 | 产品运营实习生 | 深圳 |\n"
        )
        rows = nj.parse_markdown_table(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["company"], "示例科技")

    def test_is_separator_row(self):
        self.assertTrue(nj._is_separator_row(["---", ":--", "--:", ":-:"]))
        self.assertFalse(nj._is_separator_row(["Boss直聘", "示例科技"]))
        self.assertFalse(nj._is_separator_row([]))


class ParseTextBlocksTests(unittest.TestCase):
    def test_blocks_split_by_separator(self):
        text = (
            "平台: Boss直聘\n公司: A公司\n岗位: 运营\n"
            "\n---\n"
            "平台: 猎聘\n公司: B公司\n岗位: 产品\n"
        )
        rows = nj.parse_text_blocks(text)
        companies = [r.get("company") for r in rows]
        self.assertIn("A公司", companies)
        self.assertIn("B公司", companies)

    def test_first_heading_block_is_kept(self):
        # 文件以 ### 开头的第一个块必须被解析，且标题行不混入 jd_text（回归 #7）。
        text = (
            "### 岗位一\n平台: Boss直聘\n公司: A公司\n"
            "\n### 岗位二\n平台: 猎聘\n公司: B公司\n"
        )
        rows = nj.parse_text_blocks(text)
        companies = [r.get("company") for r in rows]
        self.assertIn("A公司", companies)
        self.assertIn("B公司", companies)
        # 所有块的处理方式一致：标题行被剥离。
        for r in rows:
            self.assertNotIn("###", r["jd_text"])


class FieldAliasTests(unittest.TestCase):
    def test_chinese_aliases(self):
        row = {"公司": "示例科技", "职位": "运营", "城市": "深圳"}
        self.assertEqual(nj.first_value(row, "company"), "示例科技")
        self.assertEqual(nj.first_value(row, "title"), "运营")
        self.assertEqual(nj.first_value(row, "city"), "深圳")

    def test_stable_job_id(self):
        record = {"platform": "p", "company": "c", "title": "t", "city": "", "url": "", "jd_text": ""}
        self.assertEqual(nj.make_id(record), nj.make_id(dict(record)))


if __name__ == "__main__":
    unittest.main()
