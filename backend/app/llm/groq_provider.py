from backend.app.config import Settings
from groq import Groq


class GroqProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def complete(self, prompt: str, *, tier: int) -> str:
        if not self.settings.groq_api_key:
            raise RuntimeError("Groq provider is not configured")
        client = Groq(api_key=self.settings.groq_api_key)
        model = self._accessible_model(client, tier)
        completion = client.chat.completions.create(
            model=model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Answer only from the supplied evidence. Do not invent facts or sources."},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content or ""

    def _accessible_model(self, client: Groq, tier: int) -> str:
        preferred = self.settings.groq_model if tier > 1 else self.settings.groq_fast_model
        try:
            available = {model.id for model in client.models.list().data}
        except Exception:
            # Let the completion request provide the useful provider error if
            # the model-list endpoint is unavailable.
            return preferred

        candidates = [
            preferred,
            self.settings.groq_fast_model,
            "openai/gpt-oss-20b",
            "llama-3.1-8b-instant",
        ]
        for candidate in candidates:
            if candidate in available:
                return candidate
        raise RuntimeError("No accessible Groq text model is available for this API key")
