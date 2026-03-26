from pathlib import Path

_cache: str | None = None


def load_soul(path: str = "soul.md") -> str:
    global _cache
    if _cache is None:
        file = Path(path)
        if file.exists():
            _cache = file.read_text(encoding="utf-8")
        else:
            _cache = "Você é um assistente prestativo. Responda em português brasileiro."
    return _cache


def reload_soul(path: str = "soul.md") -> str:
    global _cache
    _cache = None
    return load_soul(path)
