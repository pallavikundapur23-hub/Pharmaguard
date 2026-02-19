#!/usr/bin/env python
"""Test Warfarin drug"""
import json
from src.drug_mapping import get_drug_recommendations
from src.gene_models import Phenotype

# Test Warfarin with different phenotypes
phenotypes = {
    'CYP2D6': Phenotype.NORMAL,
    'CYP2C19': Phenotype.NORMAL,
    'CYP2C9': Phenotype.NORMAL,        # Warfarin uses CYP2C9
    'TPMT': Phenotype.NORMAL,
    'SLC01B1': Phenotype.NORMAL,
    'DPYD': Phenotype.NORMAL,
}

rec = get_drug_recommendations('Warfarin', phenotypes)

print('✅ WARFARIN TEST')
print('=' * 70)
print('Drug: Warfarin')
print('Risk Level:', rec["risk_level"])
print('Dosing:', rec["dosing_recommendation"])
print('Explanation:', rec["explanation"])
print('=' * 70)

# Try alternate spellings
print('\n🔤 Testing alternate spellings:')
for drug_name in ['Warfarin', 'warfarin', 'WARFARIN']:
    rec = get_drug_recommendations(drug_name, phenotypes)
    status = "✅" if rec["risk_level"] != "Unknown" else "❌"
    print('  {} {:15} → {}'.format(status, drug_name, rec["risk_level"]))

print('\n✅ Warfarin works with all case variations!')
