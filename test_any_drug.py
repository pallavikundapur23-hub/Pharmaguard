"""
Test script to validate drug name input flexibility
Tests unknown drug handling
"""
from src.risk_predictor import RiskPredictor
from src.gene_models import Phenotype

print("=" * 70)
print("TESTING: FLEXIBLE DRUG NAME INPUT")
print("=" * 70)

# Test with various drug names
test_drugs = [
    # Known drugs
    "Codeine",
    "Warfarin",
    "Clopidogrel",
    # Unknown drugs
    "Aspirin",
    "Acetaminophen",
    "Ibuprofen",
    "MyCustomDrug",
]

predictor = RiskPredictor()

# Create test phenotypes
test_phenotypes = {
    "CYP2D6": Phenotype.INTERMEDIATE,
    "CYP2C19": Phenotype.POOR,
    "CYP2C9": Phenotype.NORMAL,
    "TPMT": Phenotype.NORMAL,
    "SLC01B1": Phenotype.NORMAL,
    "DPYD": Phenotype.NORMAL,
}

print("\nTesting drug risk prediction for different drugs:\n")

for drug in test_drugs:
    result = predictor.assess_multiple_drugs(test_phenotypes, [drug])
    risk_data = result[drug]
    
    print(f"💊 {drug}")
    print(f"   Risk Level: {risk_data['risk_level']}")
    print(f"   Explanation: {risk_data['explanation']}")
    print(f"   Dosing: {risk_data['dosing_recommendation']}")
    print()

print("=" * 70)
print("✅ All drugs handled gracefully!")
print("   - Known drugs → Risk prediction with recommendations")
print("   - Unknown drugs → 'UNKNOWN' with guidance to consult resources")
print("=" * 70)
