import tiktoken


def compact_context(chunks: list[str], max_tokens: int = 4_000) -> str:
    encoding = tiktoken.get_encoding("cl100k_base")
    selected: list[str] = []
    used = 0
    for chunk in chunks:
        tokens = encoding.encode(chunk)
        if used + len(tokens) > max_tokens:
            break
        selected.append(chunk)
        used += len(tokens)
    return "\n\n".join(selected)
