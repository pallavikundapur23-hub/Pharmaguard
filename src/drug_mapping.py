"""
Drug-gene-phenotype mapping based on CPIC guidelines
Maps gene phenotypes to drug risk levels
"""
from typing import Dict, List, Tuple
from src.gene_models import RiskLevel, Phenotype
from src.cpic_dosing_rules import get_cpic_dosing, CPIC_PHLEBOTOMY_RULES


# Common alternate spellings and case variations for drugs
DRUG_ALIASES = {
    # Warfarin variants
    "warfarin": "Warfarin",
    "warfarine": "Warfarin",
    "coumarin": "Warfarin",
    "coumarine": "Warfarin",
    
    # Codeine variants
    "codeine": "Codeine",
    "tylenol 3": "Codeine",
    
    # Clopidogrel variants
    "clopidogrel": "Clopidogrel",
    "clopidogel": "Clopidogrel",
    "plavix": "Clopidogrel",
    
    # Simvastatin variants
    "simvastatin": "Simvastatin",
    "simvastine": "Simvastatin",
    "zocor": "Simvastatin",
    
    # Azathioprine variants
    "azathioprine": "Azathioprine",
    "azathioprine": "Azathioprine",
    "imuran": "Azathioprine",
    "aza": "Azathioprine",
    
    # Fluorouracil variants
    "fluorouracil": "Fluorouracil",
    "fluorouracile": "Fluorouracil",
    "5fu": "Fluorouracil",
    "5-fu": "Fluorouracil",
    "adrucil": "Fluorouracil",
    
    # Metoprolol variants
    "metoprolol": "Metoprolol",
    "metaprolol": "Metoprolol",
    "lopressor": "Metoprolol",
    
    # Amitriptyline variants
    "amitriptyline": "Amitriptyline",
    "amitrityline": "Amitriptyline",
    "elavil": "Amitriptyline",
}

# Drug to genes mapping
DRUG_GENE_MAP = {
    "Codeine": ["CYP2D6"],
    "Warfarin": ["CYP2C9", "VKORC1"],
    "Clopidogrel": ["CYP2C19"],
    "Simvastatin": ["CYP3A4", "SLCO1B1"],
    "Azathioprine": ["TPMT"],
    "Fluorouracil": ["DPYD"],
    "Metoprolol": ["CYP2D6"],
    "Amitriptyline": ["CYP2D6", "CYP2C19"],
    "Tacrolimus": ["CYP3A5"],
    "Phenytoin": ["CYP2C9", "HLA-B"],
}


# Risk assessment rules: (gene, phenotype) -> drug risk mapping
PHENOTYPE_RISK_MAP = {
    # Codeine - CYP2D6 metabolizer
    ("CYP2D6", "Codeine"): {
        Phenotype.ULTRA_RAPID: RiskLevel.TOXIC,
        Phenotype.RAPID: RiskLevel.ADJUST_DOSAGE,
        Phenotype.NORMAL: RiskLevel.SAFE,
        Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
        Phenotype.POOR: RiskLevel.INEFFECTIVE,
        Phenotype.NO_FUNCTION: RiskLevel.INEFFECTIVE,
    },
    
    # Warfarin - CYP2C9 metabolizer
    ("CYP2C9", "Warfarin"): {
        Phenotype.NORMAL: RiskLevel.SAFE,
        Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
        Phenotype.POOR: RiskLevel.ADJUST_DOSAGE,
    },
    
    # Clopidogrel - CYP2C19 metabolizer (prodrug)
    ("CYP2C19", "Clopidogrel"): {
        Phenotype.NORMAL: RiskLevel.SAFE,
        Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
        Phenotype.POOR: RiskLevel.INEFFECTIVE,
    },
    
    # Simvastatin - SLCO1B1
    ("SLC01B1", "Simvastatin"): {
        Phenotype.NORMAL: RiskLevel.SAFE,
        Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
        Phenotype.POOR: RiskLevel.ADJUST_DOSAGE,
    },
    
    # Azathioprine - TPMT metabolizer
    ("TPMT", "Azathioprine"): {
        Phenotype.NORMAL: RiskLevel.SAFE,
        Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
        Phenotype.POOR: RiskLevel.TOXIC,
    },
    
    # Fluorouracil - DPYD (deficiency causes toxicity)
    ("DPYD", "Fluorouracil"): {
        Phenotype.NORMAL: RiskLevel.SAFE,
        Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
        Phenotype.POOR: RiskLevel.TOXIC,
    },
}


class DrugGeneMapper:
    """Maps drugs to relevant genes and predicts risk"""
    
    def __init__(self):
        self.drug_gene_map = DRUG_GENE_MAP
        self.risk_map = PHENOTYPE_RISK_MAP
    
    def get_relevant_genes(self, drug_name: str) -> List[str]:
        """Get genes relevant to a drug, with alternate spelling support"""
        # First check for alternate spellings
        normalized_input = drug_name.lower().strip()
        if normalized_input in DRUG_ALIASES:
            drug_name = DRUG_ALIASES[normalized_input]
        
        # Try exact case-insensitive match
        for key in self.drug_gene_map:
            if key.lower() == drug_name.lower():
                return self.drug_gene_map[key]
        
        # Return empty list if not found (will be handled gracefully)
        return []
    
    def register_drug(self, drug_name: str, genes: List[str]):
        """Register a new drug with genes mapping"""
        self.drug_gene_map[drug_name] = genes
    
    def predict_drug_risk(
        self,
        drug_name: str,
        gene_phenotypes: Dict[str, Phenotype]
    ) -> Tuple[RiskLevel, str]:
        """
        Predict drug risk based on gene phenotypes
        Returns: (risk_level, explanation)
        """
        # Normalize drug name using aliases
        normalized_input = drug_name.lower().strip()
        if normalized_input in DRUG_ALIASES:
            drug_name = DRUG_ALIASES[normalized_input]
        
        relevant_genes = self.get_relevant_genes(drug_name)
        
        if not relevant_genes:
            # For unknown drugs, return UNKNOWN with guidance
            return RiskLevel.UNKNOWN, f"No pharmacogenomic data available for '{drug_name}'. Consult clinical pharmacist or CPIC guidelines."
        
        # Assess each relevant gene
        risks = []
        explanations = []
        
        for gene in relevant_genes:
            if gene not in gene_phenotypes or gene_phenotypes[gene] is None:
                explanations.append(f"{gene}: No variant data available")
                continue
            
            phenotype = gene_phenotypes[gene]
            key = (gene, drug_name)
            
            if key in self.risk_map:
                risk = self.risk_map[key].get(phenotype, RiskLevel.UNKNOWN)
                risks.append(risk)
                explanations.append(
                    f"{gene} ({phenotype.value}): {risk.value}"
                )
            else:
                explanations.append(f"{gene}: No CPIC mapping for {drug_name} - manual review recommended")
        
        # Determine overall risk (take most severe)
        if not risks:
            return RiskLevel.UNKNOWN, " | ".join(explanations)
        
        risk_hierarchy = [
            RiskLevel.TOXIC,
            RiskLevel.INEFFECTIVE,
            RiskLevel.ADJUST_DOSAGE,
            RiskLevel.SAFE,
            RiskLevel.UNKNOWN,
        ]
        
        for risk in risk_hierarchy:
            if risk in risks:
                return risk, " | ".join(explanations)
        
        return RiskLevel.UNKNOWN, " | ".join(explanations)


def get_drug_recommendations(
    drug_name: str,
    phenotypes: Dict[str, Phenotype]
) -> Dict:
    """
    Get comprehensive drug recommendations using CPIC dosing database
    Returns: {risk_level, explanation, dosing_recommendation, monitoring, cpic_level, strength}
    """
    mapper = DrugGeneMapper()
    
    # Normalize drug name
    normalized_input = drug_name.lower().strip()
    if normalized_input in DRUG_ALIASES:
        canonical_drug_name = DRUG_ALIASES[normalized_input]
    else:
        canonical_drug_name = drug_name
    
    risk_level, explanation = mapper.predict_drug_risk(canonical_drug_name, phenotypes)
    
    # Get phenotypes for the relevant genes
    relevant_genes = mapper.get_relevant_genes(canonical_drug_name)
    primary_phenotype = None
    
    if relevant_genes:
        primary_gene = relevant_genes[0]  # Use primary gene for CPIC lookup
        if primary_gene in phenotypes:
            primary_phenotype = phenotypes[primary_gene]
    
    # Retrieve CPIC dosing rules
    cpic_rule = None
    if primary_phenotype:
        cpic_rule = get_cpic_dosing(canonical_drug_name, primary_phenotype)
    
    # Build recommendation from CPIC data if available
    if cpic_rule:
        return {
            "drug": canonical_drug_name,
            "risk_level": risk_level.value,
            "explanation": explanation,
            "dosing_recommendation": cpic_rule.get("dosing_recommendation", "Consult pharmacist"),
            "strength": cpic_rule.get("strength", "Moderate"),
            "clinical_guidance": cpic_rule.get("clinical_guidance", ""),
            "monitoring": cpic_rule.get("monitoring", "Standard monitoring"),
            "cpic_level": cpic_rule.get("cpic_level", "2B"),
            "reference": cpic_rule.get("ref", "CPIC Guidelines"),
        }
    else:
        # Fallback for drugs without CPIC rules in database
        return {
            "drug": canonical_drug_name,
            "risk_level": risk_level.value,
            "explanation": explanation,
            "dosing_recommendation": "Consult pharmacist for dosing guidance",
            "monitoring": "Monitor for adverse effects; adjust if needed",
            "cpic_level": "No data",
            "reference": "Manual review required"
        }
