"""
End-to-End Test: Process VCF file with LLM-integrated output
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.risk_predictor import RiskPredictor

def test_vcf_with_llm():
    """Test processing a VCF file and generating LLM-integrated output."""
    
    print("=" * 80)
    print("END-TO-END TEST: VCF PROCESSING WITH LLM EXPLANATIONS")
    print("=" * 80)
    
    # Use the comprehensive test VCF
    vcf_path = "sample_vcf/comprehensive_test.vcf"
    
    if not Path(vcf_path).exists():
        print(f"\n✗ VCF file not found: {vcf_path}")
        return False
    
    print(f"\nUsing VCF: {vcf_path}")
    
    # Initialize predictor
    print("Initializing RiskPredictor...")
    predictor = RiskPredictor()
    print(f"✓ LLM Available: {predictor.llm_available}")
    
    # Process VCF
    print(f"\nProcessing VCF file...")
    try:
        result = predictor.predict_from_vcf(
            vcf_path, 
            drugs=["Codeine", "Warfarin", "Clopidogrel"]
        )
        
        if result is None:
            print("✗ No result from predict_from_vcf")
            return False
        
        print("✓ VCF processing complete")
        
        # Parse JSON output
        try:
            json_data = json.loads(result['json_output'])
            print(f"✓ JSON output generated with {len(json_data)} drug assessments")
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse JSON: {e}")
            return False
        
        # Analyze first drug assessment
        if json_data:
            assessment = json_data[0]
            print("\n" + "=" * 80)
            print("SAMPLE DRUG ASSESSMENT")
            print("=" * 80)
            
            print(f"\nDrug: {assessment['drug']}")
            print(f"Risk Level: {assessment['risk_assessment']['risk_label']}")
            
            llm_exp = assessment['llm_generated_explanation']
            print(f"\nLLM-Generated Content:")
            print(f"  Source: {llm_exp['source']}")
            print(f"  Variant Interpretation: {len(llm_exp['variant_interpretation'])} chars")
            print(f"  Risk Explanation: {len(llm_exp['risk_explanation'])} chars")
            print(f"  Dosing Recommendation: {len(llm_exp['dosing_recommendation'])} chars")
            print(f"  Monitoring Guidance: {len(llm_exp['monitoring_guidance'])} chars")
            
            metrics = assessment['quality_metrics']
            print(f"\nQuality Metrics:")
            print(f"  LLM Used: {metrics['llm_used']}")
            print(f"  Provider: {metrics['llm_provider']}")
            print(f"  Model: {metrics['llm_model']}")
            print(f"  Cached: {metrics['llm_cached']}")
            print(f"  Quality: {metrics['explanation_quality']}")
            
            # Get cache stats
            cache_stats = predictor.llm_explainer.get_cache_stats() if predictor.llm_available else {}
            if cache_stats:
                print(f"\nCache Statistics:")
                print(f"  Total Cached: {cache_stats.get('total_cached', 0)}")
                print(f"  Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")
                print(f"  DB Size: {cache_stats.get('db_size_mb', 0):.2f} MB")
            
            print("\n" + "=" * 80)
            print("VERIFICATION")
            print("=" * 80)
            
            checks = [
                ("JSON output valid", isinstance(json_data, list)),
                ("Drug assessments exist", len(json_data) > 0),
                ("LLM explanations present", len(llm_exp['variant_interpretation']) > 20),
                ("Quality metrics tracked", metrics['llm_used'] is True),
                ("Cache working", metrics['llm_cached'] in [True, False]),
                ("Provider identified", metrics['llm_provider'] is not None),
            ]
            
            passed = sum(1 for _, result in checks if result)
            for check_name, result in checks:
                status = "✓" if result else "✗"
                print(f"{status} {check_name}")
            
            print(f"\nTests Passed: {passed}/{len(checks)}")
            
            if passed == len(checks):
                print("\n🎉 END-TO-END TEST PASSED! VCF processing with LLM is working!")
                return True
            else:
                print(f"\n⚠️  {len(checks) - passed} check(s) failed")
                return False
        else:
            print("✗ No drug assessments in output")
            return False
            
    except Exception as e:
        print(f"✗ Error during VCF processing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_vcf_with_llm()
    sys.exit(0 if success else 1)
