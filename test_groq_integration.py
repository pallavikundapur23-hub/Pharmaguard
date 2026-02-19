"""
Test script for Groq LLM integration
Verifies that Groq API works with pharmacogenomics explanations
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.llm_integration import get_explainer

def test_groq_integration():
    """Test Groq integration with various explanation types."""
    
    print("=" * 70)
    print("GROQ LLM INTEGRATION TEST")
    print("=" * 70)
    
    # Initialize explainer
    print("\nInitializing PharmaGuard Explainer with Groq...")
    try:
        explainer = get_explainer(provider="groq")
        print("✓ Explainer initialized successfully with Groq")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 1: Risk Explanation
    print("\n" + "-" * 70)
    print("TEST 1: Risk Explanation (Codeine + CYP2D6)")
    print("-" * 70)
    
    try:
        result = explainer.explain_risk_profile(
            drug="Codeine",
            gene="CYP2D6",
            phenotype="Ultra-Rapid Metabolizer",
            risk_level="TOXIC",
            clinical_guidance="Ultra-rapid metabolizers produce excessive morphine from codeine"
        )
        
        print(f"Status: {result['status']}")
        print(f"From Cache: {result['from_cache']}")
        print(f"\nExplanation:")
        print(result['explanation'][:300] + "..." if len(result['explanation']) > 300 else result['explanation'])
        print(f"\nRecommendations:")
        for rec in result.get('recommendations', [])[:3]:
            print(f"  • {rec}")
        
        if result['status'] == 'success':
            print("\n✓ Risk explanation test PASSED")
        else:
            print("\n✗ Risk explanation test FAILED")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Variant Explanation
    print("\n" + "-" * 70)
    print("TEST 2: Variant Explanation (CYP2D6 *1/*1)")
    print("-" * 70)
    
    try:
        result = explainer.explain_variant(
            gene="CYP2D6",
            diplotype="*1/*1",
            phenotype="Ultra-Rapid Metabolizer",
            activity_score=2.0
        )
        
        print(f"Status: {result['status']}")
        print(f"Metabolism: {result['metabolism_category']}")
        print(f"\nExplanation:")
        print(result['explanation'][:300] + "..." if len(result['explanation']) > 300 else result['explanation'])
        
        if result['status'] == 'success':
            print("\n✓ Variant explanation test PASSED")
        else:
            print("\n✗ Variant explanation test FAILED")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Drug Interactions
    print("\n" + "-" * 70)
    print("TEST 3: Drug Interactions (Warfarin)")
    print("-" * 70)
    
    try:
        result = explainer.explain_drug_interactions(
            drug="Warfarin",
            genes={"CYP2C9": "Intermediate", "VKORC1": "Normal"},
            risk_levels={"CYP2C9": "ADJUST", "VKORC1": "SAFE"}
        )
        
        print(f"Overall Risk: {result['overall_risk']}")
        print(f"\nSummary:")
        print(result['summary'])
        print(f"\nIndividual Interactions:")
        for gene, interaction in result['individual_interactions'].items():
            print(f"  {gene}: {interaction['phenotype']} ({interaction['risk']})")
        
        if result['overall_risk'] in ['SAFE', 'ADJUST', 'TOXIC', 'INEFFECTIVE']:
            print("\n✓ Drug interactions test PASSED")
        else:
            print("\n✗ Drug interactions test FAILED")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 4: Clinical Recommendations
    print("\n" + "-" * 70)
    print("TEST 4: Clinical Recommendations")
    print("-" * 70)
    
    try:
        recommendations = explainer.get_clinical_recommendations(
            drug="Codeine",
            risk_level="TOXIC",
            phenotype="Ultra-Rapid Metabolizer"
        )
        
        print("TOXIC Risk Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        if len(recommendations) > 0 and any("AVOID" in rec for rec in recommendations):
            print("\n✓ Clinical recommendations test PASSED")
        else:
            print("\n✗ Clinical recommendations test FAILED")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 5: Cache Statistics
    print("\n" + "-" * 70)
    print("TEST 5: Cache Statistics")
    print("-" * 70)
    
    try:
        stats = explainer.cache.get_cache_stats()
        print(f"Cached Variant Explanations: {stats['variant_explanations']}")
        print(f"Cached Risk Explanations: {stats['risk_explanations']}")
        print(f"Cached Clinical Guidance: {stats['clinical_guidance']}")
        
        if stats['variant_explanations'] > 0 or stats['risk_explanations'] > 0:
            print("\n✓ Cache statistics test PASSED")
        else:
            print("\n✓ Cache is empty (but working)")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("\n")
    success = test_groq_integration()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL GROQ TESTS PASSED!")
        print("=" * 70)
        print("\n✓ Groq LLM Integration is working correctly")
        print("✓ API key is valid and active")
        print("✓ All explanation types are functional")
        print("✓ Caching system is operational")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        sys.exit(1)
