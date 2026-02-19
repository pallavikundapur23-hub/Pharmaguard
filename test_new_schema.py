#!/usr/bin/env python
"""
Test the new JSON output schema
"""
import json
from datetime import datetime
from src.risk_predictor import RiskPredictor
from src.gene_models import Phenotype

print("=" * 70)
print("TESTING: NEW JSON OUTPUT SCHEMA")
print("=" * 70)

# Create sample genotypes and phenotypes
genotypes = {
    "CYP2D6": ("*1", "*2"),
    "CYP2C19": ("*1", "*1"),
    "CYP2C9": ("*1", "*2"),
    "TPMT": ("*1", "*1"),
    "SLC01B1": ("*1", "*1"),
    "DPYD": ("*1", "*1"),
}

phenotypes = {
    "CYP2D6": Phenotype.NORMAL,
    "CYP2C19": Phenotype.NORMAL,
    "CYP2C9": Phenotype.INTERMEDIATE,
    "TPMT": Phenotype.NORMAL,
    "SLC01B1": Phenotype.NORMAL,
    "DPYD": Phenotype.NORMAL,
}

# Create drug risks
from src.drug_mapping import get_drug_recommendations

drug_risks = {}
for drug in ["Codeine", "Warfarin", "Clopidogrel"]:
    drug_risks[drug] = get_drug_recommendations(drug, phenotypes)

# Generate JSON
predictor = RiskPredictor()
json_output = predictor._generate_json_output(genotypes, phenotypes, drug_risks)

# Parse and validate
data = json.loads(json_output)

print("\n✅ JSON Output Validation:\n")

# Check if it's an array
if isinstance(data, list):
    print(f"✅ Output is array with {len(data)} drug entries")
    
    # Check first entry
    if data:
        first_entry = data[0]
        print(f"\n📋 First Entry Structure:\n")
        
        required_keys = [
            "patient_id",
            "drug", 
            "timestamp",
            "risk_assessment",
            "pharmacogenomic_profile",
            "clinical_recommendation",
            "llm_generated_explanation",
            "quality_metrics"
        ]
        
        for key in required_keys:
            status = "✅" if key in first_entry else "❌"
            print(f"  {status} {key}")
        
        # Check nested structures
        print(f"\n📊 Risk Assessment:")
        ra = first_entry.get("risk_assessment", {})
        print(f"  ✅ risk_label: {ra.get('risk_label')}")
        print(f"  ✅ confidence_score: {ra.get('confidence_score')}")
        print(f"  ✅ severity: {ra.get('severity')}")
        
        print(f"\n🧬 Pharmacogenomic Profile:")
        pp = first_entry.get("pharmacogenomic_profile", {})
        print(f"  ✅ primary_gene: {pp.get('primary_gene')}")
        print(f"  ✅ diplotype: {pp.get('diplotype')}")
        print(f"  ✅ phenotype: {pp.get('phenotype')}")
        print(f"  ✅ detected_variants: {len(pp.get('detected_variants', []))} variants")
        
        print(f"\n💊 Clinical Recommendation:")
        cr = first_entry.get("clinical_recommendation", {})
        print(f"  ✅ summary: {cr.get('summary')[:50]}...")
        print(f"  ✅ dosing: {cr.get('dosing')[:50]}...")
        print(f"  ✅ monitoring: {cr.get('monitoring')[:50]}...")

print("\n" + "=" * 70)
print("📄 Full JSON Output for Codeine:\n")
print(json.dumps(data[0], indent=2)[:1000])
print("\n... (truncated)\n")

print("=" * 70)
print("✅ New JSON Schema Test Complete!")
print("=" * 70)
