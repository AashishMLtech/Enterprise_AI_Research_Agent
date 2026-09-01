"""Small Wikipedia-backed retrieval connector for the research scaffold."""

from urllib.parse import quote
from html.parser import HTMLParser

import httpx

from backend.app.schemas import EvidenceRecord


class _SearchResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._field: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = attributes.get("class", "") or ""
        if tag == "a" and "result__a" in classes:
            if self._current:
                self.results.append(self._current)
            self._current = {"url": attributes.get("href", "") or ""}
            self._field = "title"
        elif self._current and "result__snippet" in classes:
            self._field = "text"

    def handle_data(self, data: str) -> None:
        if self._current and self._field:
            self._current[self._field] = self._current.get(self._field, "") + data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current and self._field == "title":
            self._field = None

    def finish(self) -> None:
        if self._current:
            self.results.append(self._current)
            self._current = None


def _retrieve_duckduckgo(question: str, industry: str, limit: int) -> list[EvidenceRecord]:
    parser = _SearchResultParser()
    headers = {"User-Agent": "Mozilla/5.0 enterprise-ai-research-agent/0.1"}
    with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
        response = client.get("https://html.duckduckgo.com/html/", params={"q": question})
        response.raise_for_status()
    parser.feed(response.text)
    parser.finish()
    return [
        EvidenceRecord(
            evidence_id=f"web-{index + 1}",
            text=f"{item.get('title', '').strip()}: {item.get('text', '').strip()}",
            source_id=item["url"],
            industry=industry,
            relevance_score=round(1.0 - index / max(1, limit), 2),
            quality_score=0.6,
        )
        for index, item in enumerate(parser.results[:limit])
        if item.get("url") and item.get("text")
    ]


def retrieve_evidence(question: str, industry: str, limit: int = 5) -> list[EvidenceRecord]:
    """Find short, source-linked excerpts without requiring another package."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": question,
        "srlimit": limit,
        "format": "json",
        "utf8": 1,
    }
    headers = {"User-Agent": "enterprise-ai-research-agent/0.1"}
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = client.get("https://en.wikipedia.org/w/api.php", params=params)
            response.raise_for_status()
    except httpx.HTTPError:
        return _retrieve_duckduckgo(question, industry, limit)

    with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
        pages = response.json().get("query", {}).get("search", [])
        evidence: list[EvidenceRecord] = []
        for index, page in enumerate(pages):
            title = page.get("title", "").strip()
            if not title:
                continue
            summary_response = client.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
            )
            if summary_response.is_error:
                continue
            summary = summary_response.json().get("extract", "").strip()
            if summary:
                evidence.append(EvidenceRecord(
                    evidence_id=f"wiki-{index + 1}",
                    text=summary,
                    source_id=f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}",
                    industry=industry,
                    relevance_score=round(1.0 - index / max(1, limit), 2),
                    quality_score=0.75,
                ))
        return evidence
