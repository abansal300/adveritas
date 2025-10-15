"""
Unit tests for verdict generation module.
"""
import pytest
from app.verdicts import (
    parse_json,
    normalize_verdict,
    build_evidence_block
)


class TestParseJson:
    """Tests for JSON parsing from LLM output."""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        response = '{"label": "TRUE", "confidence": 0.9, "rationale": "Test", "sources": []}'
        result = parse_json(response)
        assert result["label"] == "TRUE"
        assert result["confidence"] == 0.9
        assert result["rationale"] == "Test"
        assert result["sources"] == []
    
    def test_parse_json_with_extra_text(self):
        """Test parsing JSON embedded in extra text."""
        response = 'Here is my analysis: {"label": "FALSE", "confidence": 0.8, "rationale": "Test", "sources": ["url"]} That is all.'
        result = parse_json(response)
        assert result["label"] == "FALSE"
        assert result["confidence"] == 0.8
        assert isinstance(result["sources"], list)
    
    def test_parse_malformed_json(self):
        """Test parsing malformed JSON returns fallback."""
        response = 'This is not JSON at all'
        result = parse_json(response)
        assert result["label"] == "UNVERIFIABLE"
        assert result["confidence"] == 0.2
        assert "Parser failed" in result["rationale"]
    
    def test_parse_json5_format(self):
        """Test parsing JSON5 format (trailing commas, etc)."""
        response = '{"label": "TRUE", "confidence": 0.9, "rationale": "Test", "sources": [],}'
        result = parse_json(response)
        assert "label" in result
        assert "confidence" in result


class TestNormalizeVerdict:
    """Tests for verdict normalization."""
    
    def test_normalize_valid_label(self):
        """Test normalization of valid label."""
        verdict = {"label": "TRUE", "confidence": 0.5, "rationale": "Test", "sources": []}
        result = normalize_verdict(verdict)
        assert result["label"] == "TRUE"
    
    def test_normalize_invalid_label(self):
        """Test normalization of invalid label defaults to UNVERIFIABLE."""
        verdict = {"label": "INVALID", "confidence": 0.5, "rationale": "Test", "sources": []}
        result = normalize_verdict(verdict)
        assert result["label"] == "UNVERIFIABLE"
    
    def test_normalize_lowercase_label(self):
        """Test normalization converts lowercase to uppercase."""
        verdict = {"label": "true", "confidence": 0.5, "rationale": "Test", "sources": []}
        result = normalize_verdict(verdict)
        assert result["label"] == "TRUE"
    
    def test_normalize_label_with_spaces(self):
        """Test normalization replaces spaces with underscores."""
        verdict = {"label": "PARTLY TRUE", "confidence": 0.5, "rationale": "Test", "sources": []}
        result = normalize_verdict(verdict)
        assert result["label"] == "PARTLY_TRUE"
    
    def test_clamp_confidence_too_high(self):
        """Test confidence clamped to maximum 1.0."""
        verdict = {"label": "TRUE", "confidence": 1.5, "rationale": "Test", "sources": []}
        result = normalize_verdict(verdict)
        assert result["confidence"] == 1.0
    
    def test_clamp_confidence_too_low(self):
        """Test confidence clamped to minimum 0.0."""
        verdict = {"label": "TRUE", "confidence": -0.5, "rationale": "Test", "sources": []}
        result = normalize_verdict(verdict)
        assert result["confidence"] == 0.0
    
    def test_normalize_sources_string_to_list(self):
        """Test normalization converts string source to list."""
        verdict = {"label": "TRUE", "confidence": 0.5, "rationale": "Test", "sources": "http://example.com"}
        result = normalize_verdict(verdict)
        assert isinstance(result["sources"], list)
        assert "http://example.com" in result["sources"]


class TestBuildEvidenceBlock:
    """Tests for evidence block formatting."""
    
    def test_build_evidence_block_empty(self):
        """Test building evidence block with empty list."""
        result = build_evidence_block([])
        assert result == ""
    
    def test_build_evidence_block_single_item(self):
        """Test building evidence block with single item."""
        evidence = [{
            "title": "Test Article",
            "url": "https://example.com",
            "snippet": "Test snippet"
        }]
        result = build_evidence_block(evidence)
        assert "Test Article" in result
        assert "https://example.com" in result
        assert "Test snippet" in result
    
    def test_build_evidence_block_multiple_items(self):
        """Test building evidence block with multiple items."""
        evidence = [
            {"title": "Article 1", "url": "https://example1.com", "snippet": "Snippet 1"},
            {"title": "Article 2", "url": "https://example2.com", "snippet": "Snippet 2"}
        ]
        result = build_evidence_block(evidence)
        assert "Article 1" in result
        assert "Article 2" in result
        assert result.count("\n") == 1  # Two items, one newline separator
    
    def test_build_evidence_block_truncates_long_snippets(self):
        """Test that long snippets are truncated to 300 chars."""
        long_snippet = "A" * 500
        evidence = [{
            "title": "Test",
            "url": "https://example.com",
            "snippet": long_snippet
        }]
        result = build_evidence_block(evidence)
        # Count actual snippet length in result (excluding formatting)
        assert len(evidence[0]["snippet"]) == 500  # Original is long
        assert "A" * 300 in result  # Truncated in output
        assert len(result) < 500  # Result is shorter than original
    
    def test_build_evidence_block_handles_missing_fields(self):
        """Test building evidence block handles missing fields gracefully."""
        evidence = [
            {"title": None, "url": None, "snippet": None},
            {"title": "Valid", "snippet": "Valid snippet"}  # Missing url
        ]
        result = build_evidence_block(evidence)
        assert isinstance(result, str)  # Should not crash
        assert "Valid" in result

