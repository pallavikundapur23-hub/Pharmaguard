"""
End-to-End Integration Test with VCF Files
Demonstrates the complete PharmaGuard workflow with real test cases
Run from backend directory: cd backend && python ../test_vcf_integration.py
"""
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.risk_predictor import RiskPredictor


def test_vcf_workflow(vcf_path: str, drugs: list, test_name: str):
    """Test a complete VCF analysis workflow"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)
    
    try:
        predictor = RiskPredictor()
        results = predictor.predict_from_vcf(vcf_path, drugs)
        
        if not results['success']:
            print(f"❌ FAILED: {results['errors']}")
            return False
        
        print(f"✅ SUCCESS: Analysis completed")
        print("\n" + "-"*80)
        print("GENOTYPES & PHENOTYPES")
        print("-"*80)
        
        # Display genotypes and phenotypes
        for gene, genotype in results['genotypes'].items():
            if genotype:
                phenotype = results['phenotypes'].get(gene)
                pheno_str = phenotype.value if phenotype else "Unknown"
                print(f"{gene:12} → {str(genotype):15} → {pheno_str}")
        
        print("\n" + "-"*80)
        print("DRUG RISK ASSESSMENT")
        print("-"*80)
        
        # Display drug risks
        for drug, risk_rec in results['drug_risks'].items():
            risk_level = risk_rec.get('risk_level', 'Unknown')
            print(f"\n{drug}:")
            print(f"  Risk Level: {risk_level}")
            print(f"  Dosing: {risk_rec.get('dosing_recommendation', 'N/A')}")
            print(f"  Monitoring: {risk_rec.get('monitoring', 'N/A')}")
        
        # Display detailed risks if available
        if results.get('detailed_risks'):
            print("\n" + "-"*80)
            print("DETAILED CPIC-ALIGNED PREDICTIONS")
            print("-"*80)
            
            for drug, detailed_risk in results['detailed_risks'].items():
                if "error" not in detailed_risk or not detailed_risk.get("error"):
                    print(f"\n{drug}:")
                    print(f"  Gene: {detailed_risk.get('gene', 'N/A')}")
                    print(f"  Phenotype: {detailed_risk.get('phenotype', 'N/A')}")
                    print(f"  Risk Level: {detailed_risk.get('risk_level', 'N/A')}")
                    
                    details = detailed_risk.get('details', {})
                    if details.get('dose_adjustment') is not None:
                        print(f"  Dose Adjustment: {details.get('dose_adjustment')}%")
                    if details.get('cpic_evidence'):
                        print(f"  CPIC Evidence: {details.get('cpic_evidence')}")
                    if details.get('reason'):
                        print(f"  Reason: {details.get('reason')[:100]}...")
        
        # Save detailed output
        output_file = f"test_output_{test_name.replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(json.loads(results['json_output']), f, indent=2)
        print(f"\n💾 Full JSON output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("PHARMAGUARD - END-TO-END VCF INTEGRATION TESTS")
    print("="*80)
    
    tests = [
        {
            "name": "Comprehensive Gene Profile",
            "vcf": "sample_vcf/comprehensive_test.vcf",
            "drugs": ["Codeine", "Warfarin", "Clopidogrel", "Azathioprine"]
        },
        {
            "name": "Codeine Toxicity Risk",
            "vcf": "sample_vcf/codeine_risk.vcf",
            "drugs": ["Codeine", "Tramadol", "Metoprolol"]
        },
        {
            "name": "Warfarin Dose Adjustment",
            "vcf": "sample_vcf/warfarin_dose.vcf",
            "drugs": ["Warfarin", "Clopidogrel"]
        },
    ]
    
    results = []
    for test in tests:
        success = test_vcf_workflow(test["vcf"], test["drugs"], test["name"])
        results.append({
            "test": test["name"],
            "status": "✅ PASS" if success else "❌ FAIL"
        })
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for result in results:
        print(f"{result['status']:10} {result['test']}")
    
    passed = sum(1 for r in results if "PASS" in r['status'])
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
