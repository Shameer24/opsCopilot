# app/services/llm.py
import json
import logging
import re
from typing import Any, Dict, List

import httpx

from app.core.config import settings

logger = logging.getLogger("opscopilot.llm")

_OPENAI_SYSTEM = (
    "You are OpsCopilot.\n"
    "Use ONLY the provided SOURCES.\n"
    "If the sources do not contain the answer, say what is missing.\n"
    "Return strict JSON with two keys: "
    "\"answer_markdown\" (string, GitHub-flavored Markdown) and "
    "\"cited_chunk_ids\" (array of strings — UUIDs from the CHUNK_ID values in SOURCES).\n"
    "Do not include any text outside the JSON object.\n"
)


def _extract_chunk_ids(sources_block: str) -> List[str]:
    ids: List[str] = []
    for line in sources_block.splitlines():
        if line.startswith("[CHUNK_ID="):
            try:
                chunk_id_part = line.split("CHUNK_ID=", 1)[1]
                chunk_id = chunk_id_part.split("]")[0].strip()
                ids.append(chunk_id)
            except Exception:
                pass
    return ids


def _extract_json(text: str) -> dict:
    """Robustly parse JSON from LLM text output (handles prose, code fences, etc.)."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def _fallback_excerpt_answer(question: str, sources_block: str) -> Dict[str, Any]:
    cited_ids = _extract_chunk_ids(sources_block)
    parts = sources_block.split("\n---\n") if sources_block else []
    excerpts: List[str] = []
    for p in parts[:3]:
        lines = p.splitlines()
        if len(lines) < 2:
            continue
        body = "\n".join(lines[1:]).strip()
        if body:
            excerpts.append(body[:900] + ("…" if len(body) > 900 else ""))

    md = "### Answer (retrieval-only)\n\n"
    if excerpts:
        md += "**Most relevant excerpts:**\n\n"
        for i, ex in enumerate(excerpts, 1):
            md += f"{i}. {ex}\n\n"
        md += "**Note:** LLM unavailable or timed out — showing retrieval excerpts only.\n"
    else:
        md += "No relevant sources were retrieved.\n"

    return {
        "answer_markdown": md.strip(),
        "cited_chunk_ids": cited_ids[:10],
        "_provider": "local",
        "_model": "retrieval-only",
        "_usage": None,
    }


class LLMClient:
    def answer_with_citations(self, question: str, sources_block: str) -> Dict[str, Any]:
        provider = (settings.LLM_PROVIDER or "local").lower().strip()
        logger.debug("llm_provider_selected", extra={"provider": provider})

        if not sources_block.strip():
            return _fallback_excerpt_answer(question, sources_block)

        if provider == "openai":
            return self._call_openai(question, sources_block)
        if provider == "ollama":
            return self._call_ollama(question, sources_block)
        return _fallback_excerpt_answer(question, sources_block)

    # ------------------------------------------------------------------
    def _call_openai(self, question: str, sources_block: str) -> Dict[str, Any]:
        try:
            from openai import OpenAI  # imported lazily so it's optional
        except ImportError:
            logger.error("openai_package_missing")
            return _fallback_excerpt_answer(question, sources_block)

        if not settings.OPENAI_API_KEY:
            logger.error("openai_api_key_missing")
            return _fallback_excerpt_answer(question, sources_block)

        user = f"QUESTION:\n{question}\n\nSOURCES:\n{sources_block}\n\nReturn JSON only."
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": _OPENAI_SYSTEM},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content or "{}"
            parsed: Dict[str, Any] = _extract_json(content)
            logger.debug("openai_response_parsed", extra={"cited": len(parsed.get("cited_chunk_ids", []))})
            parsed.setdefault("answer_markdown", "")
            parsed.setdefault("cited_chunk_ids", [])
            parsed["_provider"] = "openai"
            parsed["_model"] = settings.CHAT_MODEL
            parsed["_usage"] = completion.usage.model_dump() if completion.usage else None
            return parsed
        except Exception:
            logger.exception("openai_call_failed")
            return _fallback_excerpt_answer(question, sources_block)

    # ------------------------------------------------------------------
    def _call_ollama(self, question: str, sources_block: str) -> Dict[str, Any]:
        system = (
            "You are OpsCopilot.\n"
            "Use ONLY the provided SOURCES.\n"
            "If the sources do not contain the answer, say what is missing.\n"
            "Return strict JSON: {answer_markdown: string, cited_chunk_ids: string[]}.\n"
            "cited_chunk_ids must be a subset of the CHUNK_ID values present in SOURCES.\n"
        )
        user = f"QUESTION:\n{question}\n\nSOURCES:\n{sources_block}\n\nReturn JSON only."

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": 8192},
        }

        try:
            with httpx.Client(timeout=300.0) as client:
                r = client.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload)
                r.raise_for_status()
                data = r.json()

            content = (data.get("message") or {}).get("content") or "{}"
            parsed: Dict[str, Any] = _extract_json(content)
            logger.debug("ollama_response_parsed", extra={"cited": len(parsed.get("cited_chunk_ids", []))})
            parsed.setdefault("answer_markdown", "")
            parsed.setdefault("cited_chunk_ids", [])
            parsed["_provider"] = "ollama"
            parsed["_model"] = settings.OLLAMA_MODEL
            parsed["_usage"] = data.get("usage")
            return parsed
        except Exception:
            logger.exception("ollama_call_failed")
            return _fallback_excerpt_answer(question, sources_block)


llm_client = LLMClient()