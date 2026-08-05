from app.services.chunking import chunk_text


def test_chunk_text_short_text_stays_single():
    text = "第一段。\n\n第二段。"
    chunks = chunk_text(text, chunk_size=800, chunk_overlap=120)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_splits_long_text():
    paragraph = "内容" * 500
    chunks = chunk_text(paragraph, chunk_size=200, chunk_overlap=20)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 200 for chunk in chunks)


def test_chunk_text_preserves_content():
    text = "第一条规则。\n\n第二条规则。\n\n第三条规则。"
    joined = "".join(chunk_text(text, chunk_size=10, chunk_overlap=0))
    assert "第一条规则" in joined
    assert "第二条规则" in joined
    assert "第三条规则" in joined
