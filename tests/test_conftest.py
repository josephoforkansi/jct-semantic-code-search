# tests/conftest.py

import sys
import types
from pathlib import Path
import numpy as np

# =========================
# 🔥 FORCE ADD SRC TO PATH
# =========================
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

# Debug (optional, remove later)
print("DEBUG sys.path:", sys.path)


# =========================
# 🔥 MOCK sentence_transformers EARLY
# =========================
mock_module = types.ModuleType("sentence_transformers")


class MockModel:
    def encode(self, texts, **kwargs):
        if isinstance(texts, list):
            return np.array([[len(t)] for t in texts])
        return np.array([len(texts)])


class MockUtil:
    @staticmethod
    def cos_sim(a, b):
        return np.dot(a, b.T) / (
            np.linalg.norm(a) * np.linalg.norm(b, axis=1)
        )


mock_module.SentenceTransformer = lambda *args, **kwargs: MockModel()
mock_module.util = MockUtil

sys.modules["sentence_transformers"] = mock_module