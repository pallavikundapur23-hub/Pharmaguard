"""
Test: Demonstrate complete API workflow for frontend integration
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.risk_predictor import RiskPredictor

def test_complete_api_workflow():
    """Test the complete API workflow suitable for frontend integration."""
    
    print("=" * 80)
    print("API WORKFLOW TEST: Complete Frontend Integration")
    print("=" * 80)
    
    # Initialize predictor
    print("\n1. Initializing RiskPredictor...")
    predictor = RiskPredictor()
    print(f"   ✓ LLM Available: {predictor.llm_available}")
    print(f"   ✓ Provider: Groq API")
    
    # Test 1: VCF file path
    print("\n2. Processing VCF file...")
    vcf_path = "sample_vcf/warfarin_dose.vcf"
    drugs = ["Warfarin"]
    
    result = predictor.predict_from_vcf(vcf_path, drugs)
    
    if result is None:
        print("   ✗ Failed to process VCF")
        return False
    
    print(f"   ✓ Result keys: {list(result.keys())}")
    
    # Test 2: Parse JSON output
    print("\n3. Parsing JSON output...")
    try:
        json_data = json.loads(result['json_output'])
        print(f"   ✓ Valid JSON generated")
        print(f"   ✓ {len(json_data)} drug assessments found")
    except:
        print("   ✗ Invalid JSON")
        return False
    
    # Test 3: Verify structure
    print("\n4. Verifying output structure...")
    assessment = json_data[0]
    
    required_fields = [
        'patient_id', 'drug', 'risk_assessment',
        'pharmacogenomic_profile', 'cpic_guidelines',
        'llm_generated_explanation', 'quality_metrics'
    ]
    
    missing = [f for f in required_fields if f not in assessment]
    if missing:
        print(f"   ✗ Missing fields: {missing}")
        return False
    
    print(f"   ✓ All required top-level fields present")
    
    # Test 4: LLM explanations
    print("\n5. Verifying LLM explanations...")
    llm = assessment['llm_generated_explanation']
    
    llm_fields = ['variant_interpretation', 'risk_explanation', 
                  'dosing_recommendation', 'monitoring_guidance', 'source']
    
    missing_llm = [f for f in llm_fields if f not in llm or not llm[f]]
    if missing_llm:
        print(f"   ✗ Missing LLM fields: {missing_llm}")
        return False
    
    print(f"   ✓ All LLM explanation fields present and populated")
    
    # Test 5: Quality metrics
    print("\n6. Verifying quality metrics...")
    metrics = assessment['quality_metrics']
    
    metric_fields = ['llm_used', 'llm_provider', 'llm_model', 
                     'llm_cached', 'explanation_quality']
    
    missing_metrics = [f for f in metric_fields if f not in metrics]
    if missing_metrics:
        print(f"   ✗ Missing metric fields: {missing_metrics}")
        return False
    
    print(f"   ✓ All quality metric fields present")
    
    # Test 6: Display sample data for frontend
    print("\n7. Sample data for frontend display:")
    print(f"\n   Drug: {assessment['drug']}")
    print(f"   Risk Level: {assessment['risk_assessment']['risk_label']}")
    print(f"   Severity: {assessment['risk_assessment']['severity']}")
    
    profile = assessment['pharmacogenomic_profile']
    print(f"\n   Gene: {profile['primary_gene']}")
    print(f"   Genotype: {profile['diplotype']}")
    print(f"   Phenotype: {profile['phenotype']}")
    
    print(f"\n   CPIC Recommendation: {assessment['cpic_guidelines']['recommendation_level']}")
    print(f"   Strength: {assessment['cpic_guidelines']['strength_of_recommendation']}")
    
    print(f"\n   Variant Interpretation (first 100 chars):")
    print(f"   '{llm['variant_interpretation'][:100]}...'")
    
    print(f"\n   Risk Explanation (first 100 chars):")
    print(f"   '{llm['risk_explanation'][:100]}...'")
    
    # Test 7: Variant details
    print(f"\n8. Variant details:")
    for variant in profile['detected_variants']:
        print(f"   • {variant['gene']}: {variant['genotype']}")
        if 'llm_explanation' in variant and variant['llm_explanation']:
            print(f"     LLM: {variant['llm_explanation'][:80]}...")
    
    # Test 8: Cache statistics
    print(f"\n9. Cache statistics:")
    if predictor.llm_available:
        cache_stats = predictor.llm_explainer.get_cache_stats()
        print(f"   Total cached: {cache_stats.get('total_cached', 0)}")
        print(f"   Hit rate: {cache_stats.get('hit_rate', 0):.1%}")
        print(f"   Database size: {cache_stats.get('db_size_mb', 0):.2f} MB")
    
    # Final verification
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    checks = [
        ("VCF file processed", result is not None),
        ("JSON output valid", isinstance(json_data, list)),
        ("Structure complete", len(missing) == 0),
        ("LLM explanations present", len(missing_llm) == 0),
        ("Quality metrics present", len(missing_metrics) == 0),
        ("Data suitable for frontend", all([
            assessment.get('drug'),
            assessment.get('risk_assessment', {}).get('risk_label'),
            assessment.get('llm_generated_explanation', {}).get('variant_interpretation')
        ])),
    ]
    
    passed = sum(1 for _, result in checks if result)
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    print(f"\nTests Passed: {passed}/{len(checks)}")
    
    if passed == len(checks):
        print("\n" + "=" * 80)
        print("🎉 API WORKFLOW TEST PASSED!")
        print("=" * 80)
        print("\nThe system is ready for:")
        print("  ✓ Frontend integration (Streamlit app)")
        print("  ✓ Production deployment")
        print("  ✓ User-facing API endpoints")
        print("  ✓ LLM-enhanced explanations in all outputs")
        return True
    else:
        print(f"\n⚠️  {len(checks) - passed} check(s) failed")
        return False


if __name__ == "__main__":
    success = test_complete_api_workflow()
    sys.exit(0 if success else 1)
