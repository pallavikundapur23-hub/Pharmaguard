"""
Test imports for the application
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from src.risk_predictor import RiskPredictor
    print("✓ RiskPredictor imported successfully")
except Exception as e:
    print(f"✗ Failed to import RiskPredictor: {e}")
    sys.exit(1)

try:
    from src.llm_explainer import LLMExplainer
    print("✓ LLMExplainer imported successfully")
except Exception as e:
    print(f"✗ Failed to import LLMExplainer: {e}")
    sys.exit(1)

try:
    from src.llm_integration import get_explainer
    print("✓ LLM Integration imported successfully")
except Exception as e:
    print(f"✗ Failed to import LLM Integration: {e}")
    sys.exit(1)

try:
    explainer = get_explainer()
    print("✓ LLM Explainer initialized successfully")
    print(f"  Provider: {'Groq' if explainer.llm and explainer.llm.provider == 'groq' else 'OpenAI/Fallback'}")
except Exception as e:
    print(f"⚠ Warning: LLM Explainer could not be fully initialized (may need API key): {e}")

print("\n✓ All critical imports working!")
