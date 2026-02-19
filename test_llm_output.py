"""
Test the LLM-integrated output generation
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.risk_predictor import RiskPredictor
from src.gene_models import Phenotype, RiskLevel

def test_llm_integrated_output():
    """Test that the output includes LLM-generated explanations."""
    
    print("=" * 80)
    print("TESTING LLM-INTEGRATED OUTPUT")
    print("=" * 80)
    
    # Initialize predictor
    print("\nInitializing RiskPredictor...")
    predictor = RiskPredictor()
    print(f"✓ LLM Available: {predictor.llm_available}")
    
    # Create test data
    print("\nPreparing test data...")
    test_genotypes = {
        "CYP2D6": ("*1", "*1"),  # Ultra-Rapid Metabolizer
        "CYP2C19": ("*1", "*1"),  # Normal Metabolizer
    }
    
    test_phenotypes = {
        "CYP2D6": Phenotype.ULTRA_RAPID,
        "CYP2C19": Phenotype.NORMAL,
    }
    
    test_drug_risks = {
        "Codeine": {
            "drug": "Codeine",
            "risk_level": "Toxic",
            "explanation": "Ultra-rapid metabolizers convert codeine excessively",
            "dosing_recommendation": "Avoid",
            "monitoring": "Monitor closely",
            "cpic_level": "1A",
            "strength": "Strong",
            "clinical_guidance": "Ultra-rapid metabolizers produce excessive morphine",
            "reference": "PharmGKB CPIC Codeine/CYP2D6"
        }
    }
    
    # Generate JSON output
    print("\nGenerating LLM-integrated output...")
    json_output = predictor._generate_json_output(
        test_genotypes,
        test_phenotypes,
        test_drug_risks
    )
    
    # Parse and display
    try:
        output_data = json.loads(json_output)
        
        print("\n✓ JSON output generated successfully")
        print("\n" + "=" * 80)
        print("LLM-INTEGRATED OUTPUT SAMPLE")
        print("=" * 80)
        
        # Pretty print the first drug assessment
        if output_data:
            drug_assessment = output_data[0]
            
            # Display key sections
            print(f"\nDrug: {drug_assessment['drug'].upper()}")
            print(f"Patient ID: {drug_assessment['patient_id']}")
            print(f"\nRisk Assessment: {drug_assessment['risk_assessment']['risk_label']}")
            print(f"Severity: {drug_assessment['risk_assessment']['severity']}")
            
            print(f"\nCPIC Level: {drug_assessment['cpic_guidelines']['recommendation_level']}")
            print(f"Strength: {drug_assessment['cpic_guidelines']['strength_of_recommendation']}")
            
            print("\n" + "-" * 80)
            print("PHARMACOGENOMIC PROFILE")
            print("-" * 80)
            profile = drug_assessment['pharmacogenomic_profile']
            print(f"Primary Gene: {profile['primary_gene']}")
            print(f"Diplotype: {profile['diplotype']}")
            print(f"Phenotype: {profile['phenotype']}")
            
            print("\nDetected Variants:")
            for variant in profile['detected_variants']:
                print(f"  • {variant['gene']}: {variant['genotype']} → {variant['phenotype']}")
                if 'llm_explanation' in variant:
                    print(f"    LLM: {variant['llm_explanation'][:100]}...")
            
            print("\n" + "-" * 80)
            print("LLM-GENERATED EXPLANATIONS")
            print("-" * 80)
            llm_exp = drug_assessment['llm_generated_explanation']
            
            print(f"\nVariant Interpretation:")
            if llm_exp['variant_interpretation']:
                print(f"  {llm_exp['variant_interpretation'][:150]}...")
            else:
                print("  (No interpretation from LLM)")
            
            print(f"\nRisk Explanation:")
            if llm_exp['risk_explanation']:
                print(f"  {llm_exp['risk_explanation'][:150]}...")
            else:
                print("  (No explanation from LLM)")
            
            print(f"\nDosing Recommendation:")
            print(f"  {llm_exp['dosing_recommendation'][:100]}...")
            
            print(f"\nMonitoring Guidance:")
            print(f"  {llm_exp['monitoring_guidance'][:100]}...")
            
            print(f"\nSource: {llm_exp['source']}")
            
            print("\n" + "-" * 80)
            print("QUALITY METRICS")
            print("-" * 80)
            metrics = drug_assessment['quality_metrics']
            print(f"LLM Used: {metrics['llm_used']}")
            print(f"LLM Provider: {metrics['llm_provider']}")
            print(f"LLM Model: {metrics['llm_model']}")
            print(f"LLM Cached: {metrics['llm_cached']}")
            print(f"Explanation Quality: {metrics['explanation_quality']}")
            
            # Verify quality
            print("\n" + "=" * 80)
            print("VERIFICATION")
            print("=" * 80)
            
            checks = [
                ("LLM explanations generated", len(llm_exp['variant_interpretation']) > 0 or len(llm_exp['risk_explanation']) > 0),
                ("Variant interpretation provided", len(llm_exp['variant_interpretation']) > 20),
                ("Risk explanation provided", len(llm_exp['risk_explanation']) > 20),
                ("Dosing recommendation provided", len(llm_exp['dosing_recommendation']) > 10),
                ("Quality metrics included", metrics['llm_used'] is not None),
                ("Cache status tracked", metrics['llm_cached'] is not None),
            ]
            
            passed = 0
            for check_name, result in checks:
                status = "✓" if result else "✗"
                print(f"{status} {check_name}")
                if result:
                    passed += 1
            
            print(f"\nTests Passed: {passed}/{len(checks)}")
            
            if passed == len(checks):
                print("\n🎉 ALL TESTS PASSED! LLM integration is working correctly!")
                return True
            else:
                print(f"\n⚠️  {len(checks) - passed} check(s) failed")
                return False
        else:
            print("✗ No output data generated")
            return False
            
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse JSON output: {e}")
        print(f"\nRaw output (first 500 chars):\n{json_output[:500]}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_llm_integrated_output()
    sys.exit(0 if success else 1)
