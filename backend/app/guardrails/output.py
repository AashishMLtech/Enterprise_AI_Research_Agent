from backend.app.schemas import Claim, VerificationResult


def verify_claims(claims: list[Claim]) -> VerificationResult:
    reasons = []
    for claim in claims:
        if not claim.evidence_ids:
            claim.confidence = "UNVERIFIED"
            reasons.append(f"{claim.claim_id} has no supporting evidence")
    return VerificationResult(passed=not reasons, reasons=reasons, claims=claims)
