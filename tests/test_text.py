"""Tests for text processing functions (extract_title, strip_h1, render_markdown)."""

import markdown

from agent.send_daily import extract_title, strip_h1, render_markdown, format_note_section


class TestExtractTitle:
    def test_basic(self):
        content = "# Binary Search\n\nSome content"
        assert extract_title(content) == "Binary Search"

    def test_no_h1(self):
        content = "## Subheading\n\nNo H1 here"
        assert extract_title(content) == ""

    def test_extra_whitespace(self):
        content = "#    Spaced Out   \n\ncontent"
        assert extract_title(content) == "Spaced Out"

    def test_empty_content(self):
        assert extract_title("") == ""


class TestStripH1:
    def test_removes_first_h1(self):
        content = "# Title\n\nBody text\n\n## Subheading"
        result = strip_h1(content)
        assert "# Title" not in result
        assert result.startswith("Body text")

    def test_removes_trailing_blanks(self):
        content = "# Title\n\n\n\nBody"
        result = strip_h1(content)
        assert result == "Body"

    def test_no_h1_unchanged(self):
        content = "## Sub\n\nBody"
        assert strip_h1(content) == content

    def test_only_h1(self):
        assert strip_h1("# Lone Title") == ""

    def test_multiple_h1_only_first_removed(self):
        content = "# First\nBody\n# Second"
        result = strip_h1(content)
        assert "First" not in result
        assert "# Second" in result


class TestRenderMarkdown:
    def test_paragraph(self):
        result = render_markdown("Hello world")
        assert "<p>" in result

    def test_code_block(self):
        result = render_markdown("```python\nx = 1\n```")
        assert "<code>" in result or "<pre>" in result

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = render_markdown(md)
        assert "<table>" in result

    def test_empty(self):
        assert render_markdown("") == ""


class TestFormatNoteSection:
    def test_basic_section(self):
        row = {"topic": "dsa", "difficulty": "medium", "title": "Binary Search"}
        html = format_note_section(row, "<p>content</p>")
        assert 'class="note-section"' in html
        assert "dsa" in html
        assert "medium" in html
        assert "Binary Search" in html
        assert "<p>content</p>" in html

    def test_none_difficulty_defaults(self):
        row = {"topic": "ml-ai", "difficulty": None, "title": "Test"}
        html = format_note_section(row, "<p>x</p>")
        assert "medium" in html
