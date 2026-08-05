from dataclasses import dataclass


@dataclass
class ChunkItem:
    content: str
    page_number: int | None = None


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[str]:
    """按段落切分文本，尽量保持语义完整并带少量重叠。"""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(para) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long_paragraph(para, chunk_size, chunk_overlap))
            continue

        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            tail = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            current = f"{tail}\n\n{para}" if tail else para

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk.strip()]


def _split_long_paragraph(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        parts.append(text[start:end])
        if end == len(text):
            break
        next_start = max(end - chunk_overlap, start + 1)
        start = next_start
    return parts
