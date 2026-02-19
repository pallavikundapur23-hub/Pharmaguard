"""
CPIC Dosing Rules Database
Clinical Pharmacogenetics Implementation Consortium (CPIC) Guidelines
Hardcoded lookup table for evidence-based dosing recommendations
"""

from src.gene_models import Phenotype

# CPIC Dosing Rules Database
# Format: (drug_name, phenotype) -> {dosing_info}
CPIC_DOSING_RULES = {
    # ============================================================================
    # CODEINE - CYP2D6 Metabolizer
    # ============================================================================
    ("Codeine", Phenotype.ULTRA_RAPID): {
        "dosing_recommendation": "NOT RECOMMENDED - Risk of toxicity at normal doses. Use alternative analgesic.",
        "strength": "Strong",
        "clinical_guidance": "Ultra-rapid metabolizers produce high amounts of morphine from codeine, increasing risk of overdose and side effects.",
        "monitoring": "If must use: Monitor closely for respiratory depression, oversedation, and toxicity signs.",
        "cpic_level": "1A",
        "ref": "PharmGKB CPIC Codeine/CYP2D6"
    },
    ("Codeine", Phenotype.RAPID): {
        "dosing_recommendation": "Normal dose with consideration for increased effect. Monitor response closely.",
        "strength": "Moderate",
        "clinical_guidance": "Rapid metabolizers may achieve therapeutic levels faster. Standard dosing may produce higher drug effects.",
        "monitoring": "Monitor for increased side effects; dose reduction may be considered.",
        "cpic_level": "2A",
        "ref": "PharmGKB CPIC Codeine/CYP2D6"
    },
    ("Codeine", Phenotype.NORMAL): {
        "dosing_recommendation": "Use normal recommended dose (15-60 mg every 4-6 hours as needed).",
        "strength": "Strong",
        "clinical_guidance": "Normal metabolizers: Standard dosing expected to produce therapeutic effect.",
        "monitoring": "Standard opioid monitoring for pain control and side effects.",
        "cpic_level": "1A",
        "ref": "PharmGKB CPIC Codeine/CYP2D6"
    },
    ("Codeine", Phenotype.INTERMEDIATE): {
        "dosing_recommendation": "Consider higher than normal dose or shorter dosing intervals. Standard dose may be inadequate.",
        "strength": "Moderate",
        "clinical_guidance": "Reduced metabolism leads to lower morphine conversion (10-20% reduction).",
        "monitoring": "Monitor pain control; increase dose if inadequate response.",
        "cpic_level": "2A",
        "ref": "PharmGKB CPIC Codeine/CYP2D6"
    },
    ("Codeine", Phenotype.POOR): {
        "dosing_recommendation": "NOT RECOMMENDED - Ineffective at standard doses. Use alternative analgesic.",
        "strength": "Strong",
        "clinical_guidance": "Poor metabolizers have little-to-no morphine formation, making codeine ineffective for pain relief.",
        "monitoring": "If used despite recommendation: Monitor for lack of pain relief.",
        "cpic_level": "1A",
        "ref": "PharmGKB CPIC Codeine/CYP2D6"
    },
    ("Codeine", Phenotype.NO_FUNCTION): {
        "dosing_recommendation": "NOT RECOMMENDED - Completely ineffective. Use alternative analgesic.",
        "strength": "Strong",
        "clinical_guidance": "Complete loss of CYP2D6 function prevents morphine formation.",
        "monitoring": "Not applicable - use alternative pain management.",
        "cpic_level": "1A",
        "ref": "PharmGKB CPIC Codeine/CYP2D6"
    },

    # ============================================================================
    # WARFARIN - CYP2C9 and VKORC1
    # ============================================================================
    ("Warfarin", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard initiation: 5-10 mg daily. Adjust based on INR response.",
        "strength": "Strong",
        "clinical_guidance": "Normal metabolizers: Use standard dosing protocol with frequent INR monitoring.",
        "monitoring": "INR monitoring at baseline, 2-7 days after initiation, then weekly x 1-2 weeks, then at 1-4 week intervals.",
        "cpic_level": "1A",
        "ref": "CPIC Warfarin/CYP2C9/VKORC1 Guidelines"
    },
    ("Warfarin", Phenotype.INTERMEDIATE): {
        "dosing_recommendation": "Consider 25-50% dose reduction. Initiate lower dose (2.5-5 mg daily).",
        "strength": "Moderate",
        "clinical_guidance": "Intermediate metabolizers require dose adjustment; increased sensitivity to warfarin.",
        "monitoring": "More frequent INR monitoring (2-3x weekly initially).",
        "cpic_level": "2A",
        "ref": "CPIC Warfarin/CYP2C9/VKORC1 Guidelines"
    },
    ("Warfarin", Phenotype.POOR): {
        "dosing_recommendation": "Avoid or use with extreme caution - 40-60% dose reduction. Start 0.5-2 mg daily.",
        "strength": "Strong",
        "clinical_guidance": "Poor metabolizers have high bleeding risk at standard doses.",
        "monitoring": "Very frequent INR monitoring (daily-every other day) until stable.",
        "cpic_level": "1A",
        "ref": "CPIC Warfarin/CYP2C9/VKORC1 Guidelines"
    },

    # ============================================================================
    # CLOPIDOGREL - CYP2C19 Prodrug Activation
    # ============================================================================
    ("Clopidogrel", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard loading: 300-600 mg; Maintenance: 75 mg daily.",
        "strength": "Strong",
        "clinical_guidance": "Normal metabolizers: Standard dosing provides therapeutic antiplatelet effect.",
        "monitoring": "Monitor for bleeding; assessment of antiplatelet response if high-risk patient.",
        "cpic_level": "1A",
        "ref": "CPIC Clopidogrel/CYP2C19 Guidelines"
    },
    ("Clopidogrel", Phenotype.INTERMEDIATE): {
        "dosing_recommendation": "Consider alternative P2Y12 inhibitor (prasugrel, ticagrelor) or increase maintenance dose to 150 mg daily.",
        "strength": "Moderate",
        "clinical_guidance": "Intermediate metabolizers have reduced antiplatelet effect; may not achieve therapeutic levels.",
        "monitoring": "Assess response; consider platelet function testing.",
        "cpic_level": "2B",
        "ref": "CPIC Clopidogrel/CYP2C19 Guidelines"
    },
    ("Clopidogrel", Phenotype.POOR): {
        "dosing_recommendation": "NOT RECOMMENDED - Use alternative P2Y12 inhibitor (prasugrel 5-10 mg, ticagrelor 60-90 mg).",
        "strength": "Strong",
        "clinical_guidance": "Poor metabolizers have minimal antiplatelet effect; increased stent thrombosis risk.",
        "monitoring": "If unable to use alternatives: High-intensity antiplatelet monitoring required.",
        "cpic_level": "1A",
        "ref": "CPIC Clopidogrel/CYP2C19 Guidelines"
    },

    # ============================================================================
    # SIMVASTATIN - SLCO1B1 Transporter
    # ============================================================================
    ("Simvastatin", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard dosing: 10-40 mg daily. Maximum: 80 mg daily.",
        "strength": "Strong",
        "clinical_guidance": "Normal transporters allow standard statin dosing.",
        "monitoring": "Monitor lipid levels at 4-12 weeks, then annually. Assess for muscle symptoms.",
        "cpic_level": "1A",
        "ref": "CPIC Simvastatin/SLCO1B1 Guidelines"
    },
    ("Simvastatin", Phenotype.INTERMEDIATE): {
        "dosing_recommendation": "Consider dose reduction or alternative statin. Max 20 mg daily.",
        "strength": "Moderate",
        "clinical_guidance": "Reduced transporter function increases statin levels; myopathy risk increased.",
        "monitoring": "Monitor CK levels baseline; assess for muscle pain/weakness.",
        "cpic_level": "2A",
        "ref": "CPIC Simvastatin/SLCO1B1 Guidelines"
    },
    ("Simvastatin", Phenotype.POOR): {
        "dosing_recommendation": "Avoid simvastatin or use with extreme caution at lowest dose. Consider pravastatin/rosuvastatin.",
        "strength": "Strong",
        "clinical_guidance": "Impaired transporter = significantly elevated statin levels = high myopathy risk.",
        "monitoring": "If used: Baseline CK, monthly monitoring x 3 months, then quarterly.",
        "cpic_level": "1A",
        "ref": "CPIC Simvastatin/SLCO1B1 Guidelines"
    },

    # ============================================================================
    # AZATHIOPRINE - TPMT Metabolizer
    # ============================================================================
    ("Azathioprine", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard dose dosing: 1-2.5 mg/kg/day in divided doses.",
        "strength": "Strong",
        "clinical_guidance": "Normal TPMT activity allows standard immunosuppressive dosing.",
        "monitoring": "CBC with differential weekly x 8-12 weeks, then monthly. Monitor for myelosuppression.",
        "cpic_level": "1A",
        "ref": "CPIC Azathioprine/TPMT Guidelines"
    },
    ("Azathioprine", Phenotype.INTERMEDIATE): {
        "dosing_recommendation": "Reduce dose to 25-50% of normal. Start low and titrate based on response.",
        "strength": "Strong",
        "clinical_guidance": "Intermediate activity: Increased accumulation of toxic 6-TGN metabolites.",
        "monitoring": "CBC weekly x 4-6 weeks; monitor for infections, bleeding, severe anemia.",
        "cpic_level": "1A",
        "ref": "CPIC Azathioprine/TPMT Guidelines"
    },
    ("Azathioprine", Phenotype.POOR): {
        "dosing_recommendation": "Strongly consider AVOIDING or use at 10% of normal dose if no alternatives.",
        "strength": "Strong",
        "clinical_guidance": "Very high risk of severe bone marrow toxicity and life-threatening infections.",
        "monitoring": "If absolutely necessary: Daily CBC monitoring, consider G-CSF support.",
        "cpic_level": "1A",
        "ref": "CPIC Azathioprine/TPMT Guidelines"
    },

    # ============================================================================
    # FLUOROURACIL - DPYD Deficiency
    # ============================================================================
    ("Fluorouracil", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard chemotherapy dosing per protocol (typically 400-500 mg/m² IV).",
        "strength": "Strong",
        "clinical_guidance": "Normal DPYD activity allows standard 5-FU dosing.",
        "monitoring": "Standard oncology monitoring: CBC weekly, blood cultures if febrile.",
        "cpic_level": "1A",
        "ref": "CPIC Fluorouracil/DPYD Guidelines"
    },
    ("Fluorouracil", Phenotype.INTERMEDIATE): {
        "dosing_recommendation": "Reduce dose by 25-50%. Start at 50-75% of standard dose.",
        "strength": "Moderate",
        "clinical_guidance": "Partial DPYD deficiency increases 5-FU toxicity risk.",
        "monitoring": "Close monitoring for severe toxicity: mucositis, myelosuppression, diarrhea.",
        "cpic_level": "2A",
        "ref": "CPIC Fluorouracil/DPYD Guidelines"
    },
    ("Fluorouracil", Phenotype.POOR): {
        "dosing_recommendation": "NOT RECOMMENDED - Consider alternative chemotherapy if possible.",
        "strength": "Strong",
        "clinical_guidance": "High risk of severe, potentially fatal toxicity (mucositis, cardiotoxicity, sepsis).",
        "monitoring": "If unavoidable: Intensive monitoring; consider dose reduction to 25-50% with close daily monitoring.",
        "cpic_level": "1A",
        "ref": "CPIC Fluorouracil/DPYD Guidelines"
    },

    # ============================================================================
    # METOPROLOL - CYP2D6 Metabolizer
    # ============================================================================
    ("Metoprolol", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard dosing: 25-190 mg daily in divided doses.",
        "strength": "Strong",
        "clinical_guidance": "Normal metabolizers: Standard beta-blocker dosing effective.",
        "monitoring": "Monitor heart rate, blood pressure, exercise tolerance.",
        "cpic_level": "2B",
        "ref": "PharmGKB CYP2D6 Metabolizers"
    },
    ("Metoprolol", Phenotype.POOR): {
        "dosing_recommendation": "Reduce dose by 25-50%. Consider alternative beta-blocker (atenolol, bisoprolol).",
        "strength": "Moderate",
        "clinical_guidance": "Poor metabolizers may accumulate metoprolol; increased side effects.",
        "monitoring": "Monitor for bradycardia, hypotension, fatigue.",
        "cpic_level": "2B",
        "ref": "PharmGKB CYP2D6 Metabolizers"
    },

    # ============================================================================
    # AMITRIPTYLINE - CYP2D6 and CYP2C19 Metabolizers
    # ============================================================================
    ("Amitriptyline", Phenotype.NORMAL): {
        "dosing_recommendation": "Standard initiation: 25-50 mg at bedtime. Typical maintenance: 75-150 mg daily.",
        "strength": "Strong",
        "clinical_guidance": "Normal metabolizers via both CYP2D6 and CYP2C19; standard dosing appropriate.",
        "monitoring": "Monitor for anticholinergic effects, cardiac conduction, therapeutic response.",
        "cpic_level": "2B",
        "ref": "PharmGKB Tricyclic Antidepressants Metabolism"
    },
    ("Amitriptyline", Phenotype.POOR): {
        "dosing_recommendation": "Start low (10-25 mg) at bedtime. Titrate slowly.",
        "strength": "Moderate",
        "clinical_guidance": "Poor metabolism in CYP2D6/CYP2C19 increases drug accumulation and side effects.",
        "monitoring": "Close monitoring for anticholinergic effects, sedation, orthostatic hypotension, arrhythmias.",
        "cpic_level": "2B",
        "ref": "PharmGKB Tricyclic Antidepressants Metabolism"
    },
}

def get_cpic_dosing(drug_name: str, phenotype) -> dict:
    """
    Retrieve CPIC dosing rules for a drug-phenotype combination
    
    Args:
        drug_name: Name of the drug
        phenotype: Phenotype enum value
    
    Returns:
        dict with dosing information, or None if not found
    """
    key = (drug_name, phenotype)
    return CPIC_DOSING_RULES.get(key)

def get_all_cpic_drugs() -> list:
    """Get list of all drugs in CPIC database"""
    drugs = set()
    for (drug_name, _) in CPIC_DOSING_RULES.keys():
        drugs.add(drug_name)
    return sorted(list(drugs))

def get_cpic_phenotypes_for_drug(drug_name: str) -> list:
    """Get all phenotypes in CPIC database for a specific drug"""
    phenotypes = []
    for (drug, pheno) in CPIC_DOSING_RULES.keys():
        if drug.lower() == drug_name.lower():
            phenotypes.append(pheno)
    return phenotypes

# Phlebotomy reference guide
CPIC_PHLEBOTOMY_RULES = {
    "Codeine": {
        "testing_gene": "CYP2D6",
        "test_method": "Genotyping (DNA-based)",
        "phenotypes": ["Ultra-Rapid", "Rapid", "Normal", "Intermediate", "Poor", "No Function"],
        "clinical_significance": "High - affects drug efficacy and toxicity risk",
        "pretest_counseling": "Genetic test will determine how your body processes codeine"
    },
    "Warfarin": {
        "testing_genes": ["CYP2C9", "VKORC1"],
        "test_method": "Genotyping (DNA-based)",
        "clinical_significance": "High - significant impact on anticoagulation dosing",
        "pretest_counseling": "Genetic variants affect how your body processes warfarin"
    },
    "Clopidogrel": {
        "testing_gene": "CYP2C19",
        "test_method": "Genotyping (DNA-based)",
        "clinical_significance": "High - affects drug activation and cardiovascular outcomes",
        "pretest_counseling": "Your genes affect how well clopidogrel works for you"
    },
    "Simvastatin": {
        "testing_gene": "SLCO1B1",
        "test_method": "Genotyping (DNA-based)",
        "clinical_significance": "High - affects muscle toxicity risk",
        "pretest_counseling": "Genetic variant affects statin liver transport"
    },
    "Azathioprine": {
        "testing_gene": "TPMT",
        "test_method": "Genotyping or phenotyping (RBC assay)",
        "clinical_significance": "High - affects bone marrow toxicity risk",
        "pretest_counseling": "Important: Test predicts severe drug reactions"
    },
    "Fluorouracil": {
        "testing_gene": "DPYD",
        "test_method": "Genotyping or phenotyping (DPD enzyme test)",
        "clinical_significance": "Critical - prevents life-threatening toxicity",
        "pretest_counseling": "Mandatory before starting: Test prevents severe chemotherapy toxicity"
    },
}

# Drug interaction warnings
CPIC_INTERACTIONS = {
    ("Codeine", "CYP2D6_Inhibitor"): {
        "warning": "CYP2D6 inhibitors (fluoxetine, paroxetine, etc.) may reduce codeine efficacy",
        "recommendation": "Avoid combination or use alternative pain management"
    },
    ("Warfarin", "NSAIDs"): {
        "warning": "NSAIDs increase bleeding risk with warfarin",
        "recommendation": "Use acetaminophen; if NSAID necessary, use lowest dose for shortest duration"
    },
    ("Clopidogrel", "PPIs"): {
        "warning": "Proton pump inhibitors (omeprazole, esomeprazole) reduce clopidogrel activation",
        "recommendation": "Use H2-blocker instead (famotidine) or separate dosing times"
    },
    ("Simvastatin", "Strong_CYP3A4_Inhibitors"): {
        "warning": "Strong CYP3A4 inhibitors dramatically increase simvastatin levels",
        "recommendation": "Avoid simvastatin; use pravastatin or rosuvastatin instead"
    },
}

if __name__ == "__main__":
    # Test the database
    print("CPIC DOSING DATABASE TEST")
    print("=" * 70)
    
    from src.gene_models import Phenotype
    
    print("\n✅ Available drugs:")
    for drug in get_all_cpic_drugs():
        print(f"  - {drug}")
    
    print("\n✅ Example: Codeine dosing rules")
    print("-" * 70)
    for pheno in [Phenotype.POOR, Phenotype.INTERMEDIATE, Phenotype.NORMAL, Phenotype.ULTRA_RAPID]:
        rule = get_cpic_dosing("Codeine", pheno)
        if rule:
            print(f"\n{pheno.value}:")
            print(f"  Dosing: {rule['dosing_recommendation']}")
            print(f"  Strength: {rule['strength']}")
