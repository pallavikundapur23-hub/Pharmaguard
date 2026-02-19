"""
LLM Explainer wrapper for PharmaGuard
Re-exports the LLMExplainer from backend for use in src modules
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = str(Path(__file__).parent.parent / "backend" / "src")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import from backend
from llm_explainer import LLMExplainer

__all__ = ['LLMExplainer']
