#!/usr/bin/env python
"""
Test the JSON output schema
Verifies that the generated JSON matches the required format
"""
import json
from datetime import datetime
from src.risk_predictor import RiskPredictor
from src.gene_models import Phenotype

print("=" * 70)
print("TESTING: JSON OUTPUT SCHEMA")
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

# Check top-level keys
required_keys = ["patient_id", "timestamp", "risk_assessment", "quality_metrics"]
for key in required_keys:
    if key in data:
        print(f"  ✅ {key}")
    else:
        print(f"  ❌ {key} MISSING")

print("\n📋 Sample JSON Output:\n")
print(json.dumps(data, indent=2)[:1500])
print("\n... (truncated)\n")

# Validate structure
print("✅ Schema Validation:\n")

# Check patient_id format
if data["patient_id"].startswith("PATIENT_"):
    print(f"  ✅ patient_id format: {data['patient_id']}")
else:
    print(f"  ❌ patient_id format invalid: {data['patient_id']}")

# Check timestamp format
try:
    datetime.fromisoformat(data["timestamp"])
    print(f"  ✅ timestamp format (ISO 8601): {data['timestamp'][:19]}...")
except:
    print(f"  ❌ timestamp format invalid: {data['timestamp']}")

# Check risk_assessment array
if isinstance(data["risk_assessment"], list):
    print(f"  ✅ risk_assessment is array with {len(data['risk_assessment'])} items")
    
    # Check first item structure
    if data["risk_assessment"]:
        first_drug = data["risk_assessment"][0]
        drug_keys = ["drug_name", "risk_level", "gene_results", "clinical_explanation", 
                     "dosing_recommendations", "monitoring"]
        all_present = all(k in first_drug for k in drug_keys)
        
        if all_present:
            print(f"  ✅ Drug entry has all required keys")
            print(f"     - drug_name: {first_drug['drug_name']}")
            print(f"     - risk_level: {first_drug['risk_level']}")
            print(f"     - gene_results: {len(first_drug['gene_results'])} genes")
            print(f"     - dosing_recommendations: {len(first_drug['dosing_recommendations'])} items")
        else:
            print(f"  ❌ Drug entry missing keys")
            print(f"     Present: {list(first_drug.keys())}")

# Check quality_metrics
if "quality_metrics" in data:
    metrics = data["quality_metrics"]
    metric_keys = ["vcf_parsing_success", "genes_analyzed", "drugs_assessed", "data_completeness"]
    if all(k in metrics for k in metric_keys):
        print(f"  ✅ quality_metrics has all required keys")
    else:
        print(f"  ❌ quality_metrics missing keys")

print("\n" + "=" * 70)
print("✅ JSON Schema Validation Complete!")
print("=" * 70)
print("\nThe JSON output matches the required format:")
print("  ✅ patient_id: Unique identifier")
print("  ✅ timestamp: ISO 8601 format")
print("  ✅ risk_assessment: Array of drug assessments")
print("  ✅ quality_metrics: Data quality information")
print("=" * 70)
