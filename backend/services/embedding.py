"""
Local embedding service using sentence-transformers.
Runs entirely on CPU — no internet, no API key.
"""
# TODO Phase 8 — initialise model lazily on first call

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from config import settings
        _model = SentenceTransformer(settings.embed_model)
    return _model

def embed(text: str) -> list[float]:
    """Embed a single string. Returns list of floats."""
    model = get_model()
    return model.encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings efficiently."""
    model = get_model()
    return model.encode(texts).tolist()
