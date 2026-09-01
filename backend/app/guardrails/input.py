from backend.app.schemas import ResearchRequest


def validate_request(request: ResearchRequest) -> ResearchRequest:
    request.question = " ".join(request.question.split())
    return request
