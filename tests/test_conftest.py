"""Shared test configuration and deterministic mocks."""

import sys
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# Mock sentence_transformers before application modules import it.
mock_module = types.ModuleType("sentence_transformers")


class MockModel:
    """Return deterministic 384-dimensional embeddings."""

    def encode(self, texts, **kwargs):
        if isinstance(texts, str):
            texts = [texts]

        vectors = []

        for text in texts:
            vector = np.zeros(384, dtype=np.float32)

            # Generate a deterministic vector from the text.
            for index, character in enumerate(text):
                vector[index % 384] += ord(character) / 1000.0

            vectors.append(vector)

        return np.array(vectors, dtype=np.float32)


class MockUtil:
    """Provide cosine similarity for mock embeddings."""

    @staticmethod
    def cos_sim(a, b):
        a = np.asarray(a, dtype=np.float32)
        b = np.asarray(b, dtype=np.float32)

        if a.ndim == 1:
            a = a.reshape(1, -1)

        if b.ndim == 1:
            b = b.reshape(1, -1)

        numerator = np.dot(a, b.T)

        a_norm = np.linalg.norm(a, axis=1, keepdims=True)
        b_norm = np.linalg.norm(b, axis=1, keepdims=True)

        denominator = a_norm * b_norm.T

        # Prevent division by zero.
        denominator = np.where(
            denominator == 0,
            1e-12,
            denominator,
        )

        return numerator / denominator


# Use __dict__ to avoid Pylance unknown-attribute warnings.
mock_module.__dict__["SentenceTransformer"] = (
    lambda *args, **kwargs: MockModel()
)
mock_module.__dict__["util"] = MockUtil

sys.modules["sentence_transformers"] = mock_module
