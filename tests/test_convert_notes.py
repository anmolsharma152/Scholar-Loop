"""Tests for convert_notes helpers (no LLM calls)."""

from pathlib import Path

import pytest

from scripts.convert_notes import classify_topic, slugify, extract_text_pdf, extract_text_docx


class TestClassifyTopic:
    def test_dsa_keywords(self):
        text = "This is about binary search trees and graph algorithms"
        assert classify_topic(text, "algo.pdf") == "dsa"

    def test_system_design_keywords(self):
        text = "Distributed systems use load balancers and caching for scalability"
        assert classify_topic(text, "design.pdf") == "system-design"

    def test_ml_keywords(self):
        text = "Transformer neural networks use attention mechanisms"
        assert classify_topic(text, "model.pdf") == "ml-ai"

    def test_sql_keywords(self):
        text = "JOIN queries with indexes and transactions"
        assert classify_topic(text, "db.pdf") == "sql"

    def test_empty_text_falls_back_to_papers(self):
        assert classify_topic("", "unknown.pdf") == "papers"

    def test_filename_contributes_to_score(self):
        text = "random content here"
        filename = "understanding-sql-joins.pdf"
        assert classify_topic(text, filename) == "sql"

    def test_agentic_keywords(self):
        text = "Agentic AI with RAG and tool use for reasoning"
        assert classify_topic(text, "agent.pdf") == "agentic-ai"

    def test_fullstack_keywords(self):
        text = "Building with React and FastAPI with Docker"
        assert classify_topic(text, "app.pdf") == "fullstack"


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_removes_special_chars(self):
        assert slugify("Binary Search (O(log n))") == "binary-search-olog-n"

    def test_collapses_spaces_and_hyphens(self):
        assert slugify("  SQL   Joins -- Deep   ") == "sql-joins-deep"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_lowercase(self):
        assert slugify("UPPERCASE Title") == "uppercase-title"


class TestExtractTextHelpers:
    def test_pdf_nonexistent(self):
        result = extract_text_pdf(Path("/nonexistent/file.pdf"))
        assert result == ""

    def test_docx_nonexistent(self):
        result = extract_text_docx(Path("/nonexistent/file.docx"))
        assert result == ""
