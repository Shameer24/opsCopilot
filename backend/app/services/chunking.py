from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChunkItem:
    text: str
    chunk_index: int
    line_start: Optional[int]
    line_end: Optional[int]
    char_start: Optional[int]
    char_end: Optional[int]
    page_start: Optional[int] = None
    page_end: Optional[int] = None


def chunk_text_lines(
    text: str,
    max_chars: int = 2200,
    overlap_chars: int = 200,
) -> List[ChunkItem]:
    """
    Chunk by lines to preserve operational/log structure.
    We pack lines until max_chars, then start next chunk with overlap.
    """
    lines = text.splitlines()
    chunks: List[ChunkItem] = []

    buf: List[str] = []
    buf_len = 0
    start_line = 1
    char_cursor = 0
    chunk_index = 0

    def flush(end_line: int, end_char: int) -> None:
        nonlocal chunk_index
        if not buf:
            return
        chunk_text = "\n".join(buf).strip()
        if not chunk_text:
            return
        # approximate char offsets
        chunk_char_end = end_char
        chunk_char_start = max(0, chunk_char_end - len(chunk_text))
        chunks.append(
            ChunkItem(
                text=chunk_text,
                chunk_index=chunk_index,
                line_start=start_line,
                line_end=end_line,
                char_start=chunk_char_start,
                char_end=chunk_char_end,
            )
        )
        chunk_index += 1

    for i, line in enumerate(lines, start=1):
        # +1 for newline
        line_len = len(line) + 1
        if buf_len + line_len > max_chars and buf:
            # flush current
            flush(i - 1, char_cursor)
            # overlap: keep last overlap_chars from previous buffer
            joined = "\n".join(buf)
            tail = joined[-overlap_chars:] if overlap_chars > 0 else ""
            buf = [tail] if tail else []
            buf_len = len(tail)
            start_line = i  # new chunk line start is approximate for overlapped text
        buf.append(line)
        buf_len += line_len
        char_cursor += line_len

    flush(len(lines), char_cursor)
    return chunks