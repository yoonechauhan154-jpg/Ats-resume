"""Tests for text utilities."""

from app.utils.text import (
    normalize_whitespace,
    remove_masked_pii,
    tokenize,
    word_count,
    sentences,
)


def test_normalize_whitespace_collapses():
    assert normalize_whitespace("  hello   world  \n\n\n next ") == "hello world\n\nnext"


def test_remove_masked_pii():
    masked = remove_masked_pii("Email me at john.doe@example.com or call +1 555-123-4567")
    assert "[email]" in masked
    assert "[phone]" in masked


def test_tokenize():
    assert "c++" in tokenize("I know C++ and Node.js")
    assert "node.js" in tokenize("I know C++ and Node.js")


def test_word_count():
    assert word_count("one two three") == 3


def test_sentences():
    out = sentences("First sentence. Second one!\nThird?")
    assert len(out) == 3
