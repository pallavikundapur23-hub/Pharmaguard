"""
Comprehensive test script for LLM integration system
Tests all components and verifies API connectivity
"""
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("TESTING IMPORTS...")
    print("=" * 60)
    
    try:
        from src.llm_cache import ExplanationCache
        print("✓ ExplanationCache imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ExplanationCache: {e}")
        return False
    
    try:
        from src.llm_prompt_templates import PromptBuilder, PromptTemplate
        print("✓ PromptBuilder imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PromptBuilder: {e}")
        return False
    
    try:
        from src.llm_config import LLMConfig, PromptConfig, CacheConfig
        print("✓ LLM Config modules imported successfully")
    except Exception as e:
        print(f"✗ Failed to import LLM Config: {e}")
        return False
    
    try:
        from src.llm_integration import PharmaGuardExplainer, get_explainer
        print("✓ LLM Integration modules imported successfully")
    except Exception as e:
        print(f"✗ Failed to import LLM Integration: {e}")
        return False
    
    try:
        from backend.src.llm_explainer import LLMExplainer
        print("✓ LLMExplainer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import LLMExplainer: {e}")
        return False
    
    return True


def test_cache_system():
    """Test the caching system."""
    print("\n" + "=" * 60)
    print("TESTING CACHE SYSTEM...")
    print("=" * 60)
    
    try:
        from src.llm_cache import ExplanationCache
        import tempfile
        import os
        
        # Create temporary cache
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_cache.db")
        cache = ExplanationCache(db_path)
        
        # Test variant explanation caching
        cache.cache_variant_explanation(
            "CYP2D6", "*1/*1", "Normal", 1.0,
            "This is a test explanation"
        )
        
        cached = cache.get_variant_explanation(
            "CYP2D6", "*1/*1", "Normal", 1.0
        )
        
        if cached == "This is a test explanation":
            print("✓ Variant explanation caching works correctly")
        else:
            print("✗ Variant explanation caching failed")
            return False
        
        # Test risk explanation caching
        cache.cache_risk_explanation(
            "Codeine", "CYP2D6", "Normal", "SAFE",
            "Codeine is safe for normal metabolizers"
        )
        
        cached = cache.get_risk_explanation(
            "Codeine", "CYP2D6", "Normal", "SAFE"
        )
        
        if cached == "Codeine is safe for normal metabolizers":
            print("✓ Risk explanation caching works correctly")
        else:
            print("✗ Risk explanation caching failed")
            return False
        
        # Test cache statistics
        stats = cache.get_cache_stats()
        if stats["variant_explanations"] >= 1 and stats["risk_explanations"] >= 1:
            print(f"✓ Cache statistics working: {stats}")
        else:
            print("✗ Cache statistics failed")
            return False
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"✗ Cache system test failed: {e}")
        return False


def test_prompt_templates():
    """Test prompt template system."""
    print("\n" + "=" * 60)
    print("TESTING PROMPT TEMPLATES...")
    print("=" * 60)
    
    try:
        from src.llm_prompt_templates import PromptBuilder
        
        builder = PromptBuilder()
        
        # Test variant explanation prompt
        prompt = builder.build_variant_explanation(
            "CYP2D6", "*1/*1", "Normal", 1.0
        )
        if "CYP2D6" in prompt and "*1/*1" in prompt:
            print("✓ Variant explanation prompt built correctly")
        else:
            print("✗ Variant explanation prompt build failed")
            return False
        
        # Test risk explanation prompt
        prompt = builder.build_risk_explanation(
            "Codeine", "CYP2D6", "Normal", "SAFE", "Test guidance"
        )
        if "Codeine" in prompt and "SAFE" in prompt:
            print("✓ Risk explanation prompt built correctly")
        else:
            print("✗ Risk explanation prompt build failed")
            return False
        
        # Test system role
        role = builder.get_system_role()
        if "pharmacogenomics" in role.lower():
            print("✓ System role configured correctly")
        else:
            print("✗ System role configuration failed")
            return False
        
        # Test available templates
        templates = builder.get_available_templates()
        if len(templates) > 0:
            print(f"✓ Available templates: {len(templates)}")
        else:
            print("✗ No templates available")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Prompt template test failed: {e}")
        return False


def test_config_system():
    """Test configuration system."""
    print("\n" + "=" * 60)
    print("TESTING CONFIGURATION SYSTEM...")
    print("=" * 60)
    
    try:
        from src.llm_config import LLMConfig, PromptConfig, CacheConfig
        import os
        
        # Check if API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and len(api_key) > 10:
            print("✓ OPENAI_API_KEY is configured")
        else:
            print("✗ OPENAI_API_KEY not found or invalid")
            return False
        
        # Test LLMConfig
        try:
            config = LLMConfig.for_testing()
            print("✓ LLMConfig for_testing() works")
        except Exception as e:
            print(f"✗ LLMConfig configuration failed: {e}")
            return False
        
        # Test PromptConfig
        role = PromptConfig.get_system_role("risk_explanation")
        tokens = PromptConfig.get_max_tokens("risk_explanation")
        temp = PromptConfig.get_temperature("risk_explanation")
        
        if role and tokens > 0 and 0 < temp < 2:
            print("✓ PromptConfig is properly configured")
        else:
            print("✗ PromptConfig configuration failed")
            return False
        
        # Test CacheConfig
        ttl = CacheConfig.get_ttl("variant_explanations")
        max_entries = CacheConfig.get_max_entries("variant_explanations")
        
        if ttl > 0 and max_entries > 0:
            print("✓ CacheConfig is properly configured")
        else:
            print("✗ CacheConfig configuration failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_explainer_interface():
    """Test high-level explainer interface."""
    print("\n" + "=" * 60)
    print("TESTING EXPLAINER INTERFACE...")
    print("=" * 60)
    
    try:
        from src.llm_integration import PharmaGuardExplainer
        
        # Test fallback mode (no LLM)
        explainer = PharmaGuardExplainer(llm_explainer=None)
        
        # Test explain_risk_profile
        result = explainer.explain_risk_profile(
            "Codeine", "CYP2D6", "Ultra-Rapid Metabolizer", "TOXIC",
            "Test guidance"
        )
        
        if (result["drug"] == "Codeine" and 
            result["gene"] == "CYP2D6" and
            "explanation" in result):
            print("✓ explain_risk_profile works")
        else:
            print("✗ explain_risk_profile failed")
            return False
        
        # Test explain_variant
        result = explainer.explain_variant(
            "CYP2D6", "*1/*1", "Normal", 1.0
        )
        
        if (result["gene"] == "CYP2D6" and 
            result["metabolism_category"] == "Normal Metabolizer" and
            "explanation" in result):
            print("✓ explain_variant works")
        else:
            print("✗ explain_variant failed")
            return False
        
        # Test metabolism categorization
        categories = [
            (2.0, "Rapid/Ultra-Rapid Metabolizer"),
            (1.0, "Normal Metabolizer"),
            (0.5, "Intermediate Metabolizer"),
            (0.1, "Poor Metabolizer")
        ]
        
        all_correct = True
        for score, expected in categories:
            actual = explainer._categorize_metabolism(score)
            if actual != expected:
                print(f"✗ Metabolism categorization failed: {score} -> {actual} (expected {expected})")
                all_correct = False
        
        if all_correct:
            print("✓ Metabolism categorization works correctly")
        
        # Test clinical recommendations
        recommendations = explainer.get_clinical_recommendations(
            "Codeine", "TOXIC", "Ultra-Rapid"
        )
        
        if len(recommendations) > 0 and any("AVOID" in rec for rec in recommendations):
            print("✓ Clinical recommendations work")
        else:
            print("✗ Clinical recommendations failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Explainer interface test failed: {e}")
        return False


def test_api_connectivity():
    """Test OpenAI API connectivity."""
    print("\n" + "=" * 60)
    print("TESTING OPENAI API CONNECTIVITY...")
    print("=" * 60)
    
    try:
        from backend.src.llm_explainer import LLMExplainer
        import os
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("✗ OPENAI_API_KEY not found")
            return False
        
        # Initialize LLMExplainer
        try:
            explainer = LLMExplainer(api_key=api_key)
            print("✓ LLMExplainer initialized with API key")
        except Exception as e:
            print(f"✗ Failed to initialize LLMExplainer: {e}")
            return False
        
        # Test API call for variant explanation
        print("\n  Testing variant explanation API call...")
        result = explainer.get_variant_explanation(
            "CYP2D6", "*1/*1", "Normal Metabolizer", 1.0
        )
        
        if result["status"] == "success":
            print("✓ Variant explanation API call successful")
            print(f"  Response length: {len(result['summary'])} characters")
            if result.get("from_cache"):
                print("  (Retrieved from cache)")
        elif result["status"] == "error":
            print(f"✗ API call failed: {result['summary']}")
            return False
        
        # Test API call for risk explanation
        print("\n  Testing risk explanation API call...")
        result = explainer.get_risk_explanation(
            "Codeine", "CYP2D6", "Normal Metabolizer", "SAFE",
            "This drug is safe for normal metabolizers"
        )
        
        if result["status"] == "success":
            print("✓ Risk explanation API call successful")
            print(f"  Response length: {len(result['summary'])} characters")
            if result.get("from_cache"):
                print("  (Retrieved from cache)")
        elif result["status"] == "error":
            print(f"✗ API call failed: {result['summary']}")
            return False
        
        # Test cache stats
        stats = explainer.get_cache_stats()
        print(f"\n✓ Cache stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ API connectivity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " LLM INTEGRATION COMPREHENSIVE TEST SUITE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Imports", test_imports),
        ("Cache System", test_cache_system),
        ("Prompt Templates", test_prompt_templates),
        ("Configuration System", test_config_system),
        ("Explainer Interface", test_explainer_interface),
        ("OpenAI API Connectivity", test_api_connectivity),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            results.append((test_name, test_func()))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! LLM Integration is working correctly!")
        print("\nRequirements Met:")
        print("✓ LLM integration for explanations")
        print("✓ OpenAI API with pre-built prompt templates")
        print("✓ Caching system for variant explanations")
        print("✓ Configuration management")
        print("✓ Fallback mode for API failures")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
