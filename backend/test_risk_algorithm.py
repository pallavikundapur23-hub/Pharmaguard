#!/usr/bin/env python3
"""
Risk Prediction Algorithm Test Suite
Tests genotype-to-phenotype conversion, phenotype-to-risk mapping, and full algorithm
"""

from src.genotype_phenotype import GenotypePhenotypeConverter
from src.phenotype_risk_mapper import PhenotypeRiskPredictor
from src.gene_models import Phenotype, RiskLevel


def test_genotype_to_phenotype():
    """Test genotype-to-phenotype conversion"""
    print("=" * 90)
    print("TEST 1: GENOTYPE-TO-PHENOTYPE CONVERSION")
    print("=" * 90)
    
    converter = GenotypePhenotypeConverter()
    
    test_cases = [
        # CYP2D6 tests
        {
            "gene": "CYP2D6",
            "diplotype": ("*1", "*1"),
            "expected": Phenotype.ULTRA_RAPID,
            "description": "Two wildtype alleles = Ultra-rapid (activity 2.0)"
        },
        {
            "gene": "CYP2D6",
            "diplotype": ("*1", "*10"),
            "expected": Phenotype.RAPID,
            "description": "One wildtype + one reduced = Rapid (activity 1.5)"
        },
        {
            "gene": "CYP2D6",
            "diplotype": ("*1", "*3"),
            "expected": Phenotype.INTERMEDIATE,
            "description": "One normal + one nonfunctional = Intermediate (activity 1.0)"
        },
        {
            "gene": "CYP2D6",
            "diplotype": ("*10", "*41"),
            "expected": Phenotype.INTERMEDIATE,
            "description": "Two reduced-function = Intermediate (activity 1.0)"
        },
        {
            "gene": "CYP2D6",
            "diplotype": ("*3", "*4"),
            "expected": Phenotype.POOR,
            "description": "Two nonfunctional = Poor (activity 0.0)"
        },
        
        # CYP2C19 tests
        {
            "gene": "CYP2C19",
            "diplotype": ("*1", "*1"),
            "expected": Phenotype.NORMAL,
            "description": "CYP2C19: Two normal = Normal (activity 2.0)"
        },
        {
            "gene": "CYP2C19",
            "diplotype": ("*1", "*2"),
            "expected": Phenotype.INTERMEDIATE,
            "description": "CYP2C19: One normal + one loss-of-function = Intermediate"
        },
        {
            "gene": "CYP2C19",
            "diplotype": ("*2", "*3"),
            "expected": Phenotype.POOR,
            "description": "CYP2C19: Two loss-of-function = Poor (activity 0.0)"
        },
        
        # CYP2C9 tests
        {
            "gene": "CYP2C9",
            "diplotype": ("*1", "*1"),
            "expected": Phenotype.NORMAL,
            "description": "CYP2C9: *1/*1 = Normal (activity 2.0, 100%)"
        },
        {
            "gene": "CYP2C9",
            "diplotype": ("*1", "*3"),
            "expected": Phenotype.POOR,
            "description": "CYP2C9: *1/*3 = Poor (activity 1.05, *3 is very low)"
        },
        
        # TPMT tests
        {
            "gene": "TPMT",
            "diplotype": ("*1", "*1"),
            "expected": Phenotype.NORMAL,
            "description": "TPMT: *1/*1 = Normal (activity 2.0)"
        },
        {
            "gene": "TPMT",
            "diplotype": ("*1", "*3A"),
            "expected": Phenotype.INTERMEDIATE,
            "description": "TPMT: *1/*3A = Intermediate (activity 1.0)"
        },
        {
            "gene": "TPMT",
            "diplotype": ("*3A", "*3C"),
            "expected": Phenotype.POOR,
            "description": "TPMT: *3A/*3C = Poor (activity 0.0)"
        },
        
        # DPYD tests
        {
            "gene": "DPYD",
            "diplotype": ("*1", "*1"),
            "expected": Phenotype.NORMAL,
            "description": "DPYD: *1/*1 = Normal (safe for 5-FU)"
        },
        {
            "gene": "DPYD",
            "diplotype": ("*1", "*2A"),
            "expected": Phenotype.INTERMEDIATE,
            "description": "DPYD: *1/*2A = Intermediate (carrier)"
        },
        {
            "gene": "DPYD",
            "diplotype": ("*2A", "*13"),
            "expected": Phenotype.POOR,
            "description": "DPYD: *2A/*13 = Poor/Deficiency (avoid 5-FU)"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        gene = test["gene"]
        diplotype = test["diplotype"]
        expected = test["expected"]
        
        actual = converter.convert_diplotype_to_phenotype(gene, diplotype)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        
        print(f"\n{i}. {status}: {test['description']}")
        print(f"   Input: {gene} {diplotype[0]}/{diplotype[1]}")
        print(f"   Expected: {expected.value}")
        print(f"   Got: {actual.value}")
        
        if actual == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'=' * 90}")
    print(f"GENOTYPE CONVERSION RESULTS: {passed} passed, {failed} failed / {len(test_cases)} total")
    print(f"{'=' * 90}\n")
    
    return passed, failed


def test_phenotype_to_risk():
    """Test phenotype-to-risk mapping"""
    print("=" * 90)
    print("TEST 2: PHENOTYPE-TO-RISK MAPPING")
    print("=" * 90)
    
    predictor = PhenotypeRiskPredictor()
    
    test_cases = [
        # CODEINE tests
        {
            "drug": "Codeine",
            "phenotype": Phenotype.ULTRA_RAPID,
            "expected_risk": RiskLevel.TOXIC,
            "description": "Codeine in Ultra-Rapid metabolizer = TOXIC"
        },
        {
            "drug": "Codeine",
            "phenotype": Phenotype.NORMAL,
            "expected_risk": RiskLevel.SAFE,
            "description": "Codeine in Normal metabolizer = SAFE"
        },
        {
            "drug": "Codeine",
            "phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.INEFFECTIVE,
            "description": "Codeine in Poor metabolizer = INEFFECTIVE"
        },
        
        # WARFARIN tests
        {
            "drug": "Warfarin",
            "phenotype": Phenotype.NORMAL,
            "expected_risk": RiskLevel.SAFE,
            "description": "Warfarin in Normal = SAFE"
        },
        {
            "drug": "Warfarin",
            "phenotype": Phenotype.INTERMEDIATE,
            "expected_risk": RiskLevel.ADJUST_DOSAGE,
            "description": "Warfarin in Intermediate = ADJUST_DOSAGE"
        },
        {
            "drug": "Warfarin",
            "phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.ADJUST_DOSAGE,
            "description": "Warfarin in Poor = ADJUST_DOSAGE (high risk)"
        },
        
        # CLOPIDOGREL tests
        {
            "drug": "Clopidogrel",
            "phenotype": Phenotype.NORMAL,
            "expected_risk": RiskLevel.SAFE,
            "description": "Clopidogrel in Normal = SAFE"
        },
        {
            "drug": "Clopidogrel",
            "phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.INEFFECTIVE,
            "description": "Clopidogrel in Poor = INEFFECTIVE (prodrug not activated)"
        },
        
        # AZATHIOPRINE tests
        {
            "drug": "Azathioprine",
            "phenotype": Phenotype.NORMAL,
            "expected_risk": RiskLevel.SAFE,
            "description": "Azathioprine in Normal = SAFE"
        },
        {
            "drug": "Azathioprine",
            "phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.TOXIC,
            "description": "Azathioprine in Poor = TOXIC (bone marrow toxicity)"
        },
        
        # FLUOROURACIL tests
        {
            "drug": "Fluorouracil",
            "phenotype": Phenotype.NORMAL,
            "expected_risk": RiskLevel.SAFE,
            "description": "Fluorouracil in Normal = SAFE"
        },
        {
            "drug": "Fluorouracil",
            "phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.TOXIC,
            "description": "Fluorouracil in Poor = TOXIC (DPYD deficiency - life-threatening)"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        drug = test["drug"]
        phenotype = test["phenotype"]
        expected = test["expected_risk"]
        
        actual, details = predictor.predict_risk(drug, phenotype)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        
        print(f"\n{i}. {status}: {test['description']}")
        print(f"   Expected: {expected.value}")
        print(f"   Got: {actual.value}")
        print(f"   Evidence: {details.get('cpic_evidence', 'N/A')}")
        
        if actual == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'=' * 90}")
    print(f"PHENOTYPE-RISK RESULTS: {passed} passed, {failed} failed / {len(test_cases)} total")
    print(f"{'=' * 90}\n")
    
    return passed, failed


def test_complete_workflow():
    """Test complete workflow: genotype → phenotype → risk"""
    print("=" * 90)
    print("TEST 3: COMPLETE WORKFLOW (Genotype → Phenotype → Risk)")
    print("=" * 90)
    
    converter = GenotypePhenotypeConverter()
    predictor = PhenotypeRiskPredictor()
    
    workflows = [
        {
            "name": "Codeine toxicity scenario",
            "drug": "Codeine",
            "gene": "CYP2D6",
            "diplotype": ("*1", "*1"),
            "expected_phenotype": Phenotype.ULTRA_RAPID,
            "expected_risk": RiskLevel.TOXIC
        },
        {
            "name": "Warfarin dose adjustment needed",
            "drug": "Warfarin",
            "gene": "CYP2C9",
            "diplotype": ("*1", "*3"),
            "expected_phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.ADJUST_DOSAGE
        },
        {
            "name": "Clopidogrel ineffective (poor metabolizer)",
            "drug": "Clopidogrel",
            "gene": "CYP2C19",
            "diplotype": ("*2", "*3"),
            "expected_phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.INEFFECTIVE
        },
        {
            "name": "5-FU severe toxicity risk (DPYD deficiency)",
            "drug": "Fluorouracil",
            "gene": "DPYD",
            "diplotype": ("*2A", "*13"),
            "expected_phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.TOXIC
        },
        {
            "name": "Azathioprine bone marrow toxicity",
            "drug": "Azathioprine",
            "gene": "TPMT",
            "diplotype": ("*3A", "*3C"),
            "expected_phenotype": Phenotype.POOR,
            "expected_risk": RiskLevel.TOXIC
        },
        {
            "name": "Standard codeine dosing (normal metabolizer)",
            "drug": "Codeine",
            "gene": "CYP2D6",
            "diplotype": ("*1", "*2"),
            "expected_phenotype": Phenotype.NORMAL,
            "expected_risk": RiskLevel.SAFE
        },
    ]
    
    passed_pheno = 0
    failed_pheno = 0
    passed_risk = 0
    failed_risk = 0
    
    for i, workflow in enumerate(workflows, 1):
        print(f"\n{'=' * 90}")
        print(f"WORKFLOW {i}: {workflow['name']}")
        print(f"{'=' * 90}")
        
        # Step 1: Genotype → Phenotype
        print(f"\n📊 Step 1: Genotype to Phenotype Conversion")
        phenotype = converter.convert_diplotype_to_phenotype(workflow['gene'], workflow['diplotype'])
        
        expected_pheno = workflow['expected_phenotype']
        pheno_status = "✅" if phenotype == expected_pheno else "❌"
        print(f"  {pheno_status} {workflow['gene']} {workflow['diplotype']} → {phenotype.value}")
        
        if phenotype == expected_pheno:
            passed_pheno += 1
        else:
            print(f"     Expected: {expected_pheno.value}")
            failed_pheno += 1
        
        # Step 2: Get detailed info
        info = converter.get_detailed_phenotype_info(workflow['gene'], workflow['diplotype'])
        print(f"     Activity Score: {info['activity_score']:.1f}")
        print(f"     Clinical: {info['clinical_relevance']}")
        
        # Step 3: Phenotype → Risk
        print(f"\n🎯 Step 2: Phenotype to Risk Mapping")
        risk, details = predictor.predict_risk(workflow['drug'], phenotype)
        
        expected_risk = workflow['expected_risk']
        risk_status = "✅" if risk == expected_risk else "❌"
        print(f"  {risk_status} {workflow['drug']} with {phenotype.value} → {risk.value}")
        
        if risk == expected_risk:
            passed_risk += 1
        else:
            print(f"     Expected: {expected_risk.value}")
            failed_risk += 1
        
        print(f"     Recommendation: {details.get('recommendation', 'N/A')}")
        print(f"     Dose: {details.get('dose_adjustment', 'N/A')}")
        print(f"     CPIC Evidence: {details.get('cpic_evidence', 'N/A')}")
    
    print(f"\n{'=' * 90}")
    print(f"WORKFLOW RESULTS:")
    print(f"  Phenotype Conversion: {passed_pheno} passed, {failed_pheno} failed")
    print(f"  Risk Prediction: {passed_risk} passed, {failed_risk} failed")
    print(f"{'=' * 90}\n")
    
    return passed_pheno + passed_risk, failed_pheno + failed_risk


def test_edge_cases():
    """Test edge cases and error handling"""
    print("=" * 90)
    print("TEST 4: EDGE CASES & ERROR HANDLING")
    print("=" * 90)
    
    converter = GenotypePhenotypeConverter()
    predictor = PhenotypeRiskPredictor()
    
    passed = 0
    failed = 0
    
    # Test 1: Unknown gene
    print("\n1. Unknown gene handling")
    pheno = converter.convert_diplotype_to_phenotype("UNKNOWN_GENE", ("*1", "*1"))
    if pheno == Phenotype.NORMAL:
        print("   ✅ PASS: Unknown gene defaults to NORMAL phenotype")
        passed += 1
    else:
        print("   ❌ FAIL: Should default to NORMAL")
        failed += 1
    
    # Test 2: Unknown drug
    print("\n2. Unknown drug handling")
    risk, details = predictor.predict_risk("ASPIRIN", Phenotype.NORMAL)
    if risk == RiskLevel.UNKNOWN:
        print("   ✅ PASS: Unknown drug returns UNKNOWN risk")
        passed += 1
    else:
        print("   ❌ FAIL: Should return UNKNOWN")
        failed += 1
    
    # Test 3: Case sensitivity in predictor summary
    print("\n3. Risk summary generation")
    summary = predictor.get_risk_summary("Codeine", Phenotype.POOR)
    if "INEFFECTIVE" in summary:
        print(f"   ✅ PASS: Summary correctly identifies ineffective: {summary}")
        passed += 1
    else:
        print(f"   ❌ FAIL: Summary should show INEFFECTIVE")
        failed += 1
    
    # Test 4: Batch conversion
    print("\n4. Batch genotype conversion")
    gene_diplotypes = {
        "CYP2D6": ("*1", "*1"),
        "CYP2C19": ("*1", "*2"),
        "TPMT": ("*1", "*1")
    }
    results = converter.convert_batch_diplotypes(gene_diplotypes)
    if len(results) == 3 and all(p for p in results.values()):
        print(f"   ✅ PASS: Batch conversion successful")
        for gene, pheno in results.items():
            print(f"      {gene}: {pheno.value}")
        passed += 1
    else:
        print("   ❌ FAIL: Batch conversion failed")
        failed += 1
    
    print(f"\n{'=' * 90}")
    print(f"EDGE CASE RESULTS: {passed} passed, {failed} failed / 4 total")
    print(f"{'=' * 90}\n")
    
    return passed, failed


def main():
    """Run all tests"""
    print("\n" + "=" * 90)
    print("RISK PREDICTION ALGORITHM - COMPREHENSIVE TEST SUITE")
    print("=" * 90 + "\n")
    
    total_passed = 0
    total_failed = 0
    
    # Test 1
    p, f = test_genotype_to_phenotype()
    total_passed += p
    total_failed += f
    
    # Test 2
    p, f = test_phenotype_to_risk()
    total_passed += p
    total_failed += f
    
    # Test 3
    p, f = test_complete_workflow()
    total_passed += p
    total_failed += f
    
    # Test 4
    p, f = test_edge_cases()
    total_passed += p
    total_failed += f
    
    # SUMMARY
    print("=" * 90)
    print("FINAL TEST SUMMARY")
    print("=" * 90)
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"📊 Total Tests: {total_passed + total_failed}")
    success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print("=" * 90 + "\n")
    
    status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"⚠️ {total_failed} TESTS FAILED"
    print(status)


if __name__ == "__main__":
    main()
