# tests/conftest.py

import sys
from pathlib import Path

# Add src/ to Python path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
