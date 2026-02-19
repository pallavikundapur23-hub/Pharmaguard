"""
Test script to validate VCF parser and risk prediction
Run: python test_parser.py
"""
import sys
from src.vcf_parser import parse_vcf_file
from src.risk_predictor import RiskPredictor
from src.gene_models import Phenotype


def test_vcf_parsing():
    """Test VCF parsing"""
    print("\n" + "="*60)
    print("TEST 1: VCF Parsing")
    print("="*60)
    
    vcf_path = "sample_vcf/example.vcf"
    success, genotypes, errors = parse_vcf_file(vcf_path)
    
    if not success:
        print(f"❌ Parsing failed: {errors}")
        return False
    
    print(f"✅ Successfully parsed: {vcf_path}")
    print(f"   Found {len([g for g in genotypes.values() if g is not None])} genes with variants")
    
    for gene, gt in genotypes.items():
        if gt:
            print(f"   - {gene}: {gt.genotype} (variants: {[str(v) for v in gt.variants]})")
    
    return True


def test_genotype_to_phenotype():
    """Test genotype-to-phenotype conversion"""
    print("\n" + "="*60)
    print("TEST 2: Genotype → Phenotype Conversion")
    print("="*60)
    
    predictor = RiskPredictor()
    
    test_cases = [
        ("CYP2D6", ("*1", "*1"), Phenotype.NORMAL),
        ("CYP2D6", ("*1", "*2"), Phenotype.NORMAL),
        ("CYP2C19", ("*1", "*2"), Phenotype.INTERMEDIATE),
        ("CYP2C9", ("*2", "*3"), Phenotype.POOR),
        ("TPMT", ("*1", "*3A"), Phenotype.INTERMEDIATE),
    ]
    
    passed = 0
    for gene, genotype, expected in test_cases:
        result = predictor.genotype_to_phenotype(gene, genotype)
        status = "✅" if result == expected else "❌"
        print(f"{status} {gene} {genotype} → {result}")
        if result == expected:
            passed += 1
    
    print(f"\nPassed {passed}/{len(test_cases)} tests")
    return passed == len(test_cases)


def test_risk_prediction():
    """Test full risk prediction pipeline"""
    print("\n" + "="*60)
    print("TEST 3: Risk Prediction Pipeline")
    print("="*60)
    
    predictor = RiskPredictor()
    drugs = ["Codeine", "Warfarin", "Clopidogrel"]
    
    results = predictor.predict_from_vcf("sample_vcf/example.vcf", drugs)
    
    if not results['success']:
        print(f"❌ Prediction failed: {results['errors']}")
        return False
    
    print("✅ Full pipeline executed successfully")
    print(f"\nPredicted drug risks:")
    for drug, risk_rec in results['drug_risks'].items():
        print(f"  {drug}: {risk_rec['risk_level']}")
        print(f"    → {risk_rec['dosing_recommendation']}")
    
    return True


def test_json_output():
    """Test JSON output generation"""
    print("\n" + "="*60)
    print("TEST 4: JSON Output")
    print("="*60)
    
    predictor = RiskPredictor()
    results = predictor.predict_from_vcf("sample_vcf/example.vcf", ["Codeine"])
    
    if not results['success']:
        print(f"❌ JSON generation failed")
        return False
    
    import json
    try:
        json_data = json.loads(results['json_output'])
        print("✅ Valid JSON generated")
        print(f"\nJSON structure:")
        print(f"  - genes: {list(json_data.get('genes', {}).keys())}")
        print(f"  - drug_recommendations: {list(json_data.get('drug_recommendations', {}).keys())}")
        print(f"\nSample output:")
        print(json.dumps(json_data, indent=2)[:500] + "...")
        return True
    except:
        print("❌ Invalid JSON")
        return False


def main():
    """Run all tests"""
    print("\n🧬 PharmaGuard VCF Parser Test Suite")
    
    tests = [
        ("VCF Parsing", test_vcf_parsing),
        ("Genotype→Phenotype", test_genotype_to_phenotype),
        ("Risk Prediction", test_risk_prediction),
        ("JSON Output", test_json_output),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to build the web app.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
