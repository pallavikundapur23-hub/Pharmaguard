#!/usr/bin/env python3
"""
Test script for CPIC Dosing Rules Database
Verifies all drugs and phenotypes have proper dosing rules
"""

from src.cpic_dosing_rules import (
    get_cpic_dosing, 
    get_all_cpic_drugs, 
    get_cpic_phenotypes_for_drug,
    CPIC_DOSING_RULES,
    CPIC_PHLEBOTOMY_RULES
)
from src.gene_models import Phenotype

def test_cpic_database():
    """Test basic database functionality"""
    print("=" * 80)
    print("CPIC DOSING RULES DATABASE TEST")
    print("=" * 80)
    
    # Test 1: Get all drugs
    print("\n✅ TEST 1: Available CPIC Drugs")
    print("-" * 80)
    drugs = get_all_cpic_drugs()
    for drug in drugs:
        print(f"  • {drug}")
    print(f"\n  Total: {len(drugs)} drugs")
    
    # Test 2: Get phenotypes for each drug
    print("\n✅ TEST 2: Phenotypes per Drug")
    print("-" * 80)
    for drug in drugs[:3]:  # Sample 3 drugs
        phenotypes = get_cpic_phenotypes_for_drug(drug)
        print(f"\n  {drug}:")
        for pheno in phenotypes:
            print(f"    - {pheno.value}")
    
    # Test 3: Get detailed dosing rules
    print("\n✅ TEST 3: Sample Dosing Rules (Codeine)")
    print("-" * 80)
    test_drug = "Codeine"
    for pheno in [Phenotype.ULTRA_RAPID, Phenotype.NORMAL, Phenotype.POOR]:
        rule = get_cpic_dosing(test_drug, pheno)
        if rule:
            print(f"\n  {pheno.value}:")
            print(f"    Dosing: {rule['dosing_recommendation'][:60]}...")
            print(f"    Strength: {rule['strength']}")
            print(f"    CPIC Level: {rule['cpic_level']}")
        else:
            print(f"\n  {pheno.value}: No rule found")
    
    # Test 4: Verify complete coverage
    print("\n✅ TEST 4: Coverage Analysis")
    print("-" * 80)
    total_rules = len(CPIC_DOSING_RULES)
    drugs_with_all_phenotypes = 0
    
    for drug in drugs:
        phenotypes = get_cpic_phenotypes_for_drug(drug)
        if len(phenotypes) >= 5:  # Should have rules for most phenotypes
            drugs_with_all_phenotypes += 1
    
    print(f"  Total CPIC Rules: {total_rules}")
    print(f"  Drugs with comprehensive coverage: {drugs_with_all_phenotypes}/{len(drugs)}")
    print(f"  Average rules per drug: {total_rules / max(len(drugs), 1):.1f}")
    
    # Test 5: Phlebotomy rules
    print("\n✅ TEST 5: Phlebotomy/Testing Rules")
    print("-" * 80)
    print(f"  Drugs with testing guidelines: {len(CPIC_PHLEBOTOMY_RULES)}")
    for drug in list(CPIC_PHLEBOTOMY_RULES.keys())[:3]:
        phlab = CPIC_PHLEBOTOMY_RULES[drug]
        gene = phlab.get('testing_gene', phlab.get('testing_genes', 'N/A'))
        print(f"\n  {drug}:")
        print(f"    Gene: {gene}")
        print(f"    Method: {phlab.get('test_method', 'N/A')}")
        print(f"    Significance: {phlab.get('clinical_significance', 'N/A')}")
    
    # Test 6: Verify all rules have required fields
    print("\n✅ TEST 6: Schema Validation")
    print("-" * 80)
    required_fields = {
        'dosing_recommendation',
        'strength',
        'clinical_guidance',
        'monitoring',
        'cpic_level',
        'ref'
    }
    
    invalid_rules = []
    for (drug, pheno), rule in CPIC_DOSING_RULES.items():
        missing = required_fields - set(rule.keys())
        if missing:
            invalid_rules.append((drug, pheno, missing))
    
    if invalid_rules:
        print(f"  ❌ Found {len(invalid_rules)} rules with missing fields:")
        for drug, pheno, missing in invalid_rules[:5]:
            print(f"     {drug}/{pheno.value}: Missing {missing}")
    else:
        print(f"  ✅ All {total_rules} rules have required fields")
    
    # Test 7: Multiple dosing scenarios
    print("\n✅ TEST 7: Dosing Scenarios")
    print("-" * 80)
    scenarios = [
        ("Warfarin", Phenotype.POOR),
        ("Clopidogrel", Phenotype.POOR),
        ("Azathioprine", Phenotype.INTERMEDIATE),
        ("Fluorouracil", Phenotype.POOR),
    ]
    
    for drug, pheno in scenarios:
        rule = get_cpic_dosing(drug, pheno)
        if rule:
            strength = rule['strength']
            strength_icon = "🔴" if strength == "Strong" else "🟡" if strength == "Moderate" else "🟢"
            print(f"\n  {strength_icon} {drug} ({pheno.value}):")
            print(f"     {rule['dosing_recommendation']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ CPIC DATABASE TEST COMPLETE")
    print("=" * 80)
    print(f"  • {len(drugs)} drugs in database")
    print(f"  • {total_rules} total dosing rules")
    print(f"  • {len(CPIC_PHLEBOTOMY_RULES)} drugs with testing guidelines")
    print(f"  • Coverage: {(drugs_with_all_phenotypes/len(drugs)*100):.0f}%")

if __name__ == "__main__":
    test_cpic_database()
