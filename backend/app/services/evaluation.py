import re
from typing import Iterable
import uuid

def citation_coverage(answer_markdown: str, citation_count: int) -> float:
    text = answer_markdown.strip()
    if not text:
        return 0.0
    if citation_count <= 0:
        return 0.0

    sentences = [s.strip() for s in re.split(r"[.!?]\s+", text) if s.strip()]
    n = max(1, len(sentences))

    # Base: citations per sentence (capped)
    base = min(1.0, citation_count / n)

    # Penalize very long answers with low citation density
    length_penalty = 1.0
    if len(text) > 1200 and citation_count < 3:
        length_penalty = 0.7
    if len(text) > 2500 and citation_count < 5:
        length_penalty = 0.5

    return max(0.0, min(1.0, base * length_penalty))

def citations_in_retrieval_ratio(cited_ids: Iterable[uuid.UUID], retrieved_ids: Iterable[uuid.UUID]) -> float:
    rset = set(retrieved_ids)
    cset = set(cited_ids)
    if not cset:
        return 0.0
    return sum(1 for c in cset if c in rset) / len(cset)