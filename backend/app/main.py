import json

from fastapi import FastAPI, HTTPException

from backend.app.config import get_settings
from backend.app.guardrails.injection import contains_prompt_injection
from backend.app.guardrails.ood import detect_ood
from backend.app.guardrails.output import verify_claims
from backend.app.llm.groq_provider import GroqProvider
from backend.app.llm.router import route_task
from backend.app.retrieval.context import compact_context
from backend.app.retrieval.web_search import retrieve_evidence
from backend.app.schemas import Claim, FinalReport, ResearchRequest

app = FastAPI(title="Enterprise AI Research Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research", response_model=FinalReport)
def research(request: ResearchRequest) -> FinalReport:
    settings = get_settings()
    if contains_prompt_injection(request.question):
        raise HTTPException(status_code=400, detail="Request contains a disallowed instruction pattern")
    industry = settings.industry(request.industry)
    ood = detect_ood(request.question, industry)
    if not ood.in_distribution:
        verification = verify_claims([])
        return FinalReport(
            status="insufficient_evidence",
            summary="Insufficient reliable evidence was found to verify this request for the selected industry.",
            limitations=["Out-of-distribution request blocked before synthesis.", *ood.reasons],
            verification=verification,
        )
    try:
        evidence = retrieve_evidence(request.question, request.industry)
    except Exception as exc:
        return FinalReport(
            status="insufficient_evidence",
            summary="Evidence retrieval failed before synthesis.",
            limitations=[str(exc)],
            verification=verify_claims([]),
        )
    if not evidence:
        return FinalReport(
            status="insufficient_evidence",
            summary="No reliable evidence was found for this request.",
            limitations=["The retrieval connector returned no source excerpts."],
            verification=verify_claims([]),
        )

    evidence_text = "\n\n".join(f"[{item.evidence_id}] {item.text}" for item in evidence)
    prompt = (
        f"Question: {request.question}\n\n"
        f"Evidence:\n{compact_context([evidence_text], settings.max_context_tokens)}\n\n"
        "Return valid JSON only with this shape: "
        '{"summary":"...","claims":[{"claim_id":"claim-1",'
        '"text":"...","evidence_ids":["wiki-1"],"confidence":"HIGH"}]}'
    )
    try:
        raw = GroqProvider(settings).complete(prompt, tier=route_task("synthesis").tier)
        payload = json.loads(raw.replace("```json", "").replace("```", "").strip())
        claims = [Claim(**claim) for claim in payload.get("claims", []) if claim.get("evidence_ids")]
        verification = verify_claims(claims)
        return FinalReport(
            status="complete" if verification.passed else "insufficient_evidence",
            summary=payload.get("summary", "The available evidence was synthesized."),
            claims=claims,
            evidence=evidence,
            limitations=[] if verification.passed else verification.reasons,
            verification=verification,
        )
    except Exception as exc:
        return FinalReport(
            status="insufficient_evidence",
            summary="Evidence was retrieved, but synthesis could not be completed.",
            evidence=evidence,
            limitations=[str(exc)],
            verification=verify_claims([]),
        )
