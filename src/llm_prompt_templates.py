"""
Pre-built prompt templates for LLM explanations
Avoids complex prompt engineering by using standardized, tested templates
"""
from typing import Dict, Optional
from enum import Enum


class PromptTemplate(Enum):
    """Available prompt templates."""
    VARIANT_EXPLANATION = "variant_explanation"
    RISK_EXPLANATION = "risk_explanation"
    DOSING_ADJUSTMENT = "dosing_adjustment"
    DRUG_SUMMARY = "drug_summary"
    PHENOTYPE_INTERPRETATION = "phenotype_interpretation"


PROMPT_TEMPLATES = {
    PromptTemplate.VARIANT_EXPLANATION.value: """
Explain the genetic profile for the '{gene}' gene:
- Diplotype: {diplotype}
- Phenotype: {phenotype}
- Activity Score: {activity_score}

Provide a clear explanation that includes:
1. What this diplotype means (in simple terms)
2. How the activity score relates to the phenotype
3. General implications for drug metabolism ({phenotype} = faster/slower processing)

Keep to 120-150 words. Use patient-friendly language.
""",

    PromptTemplate.RISK_EXPLANATION.value: """
Explain the pharmacogenomic risk for drug-gene interaction:

Drug: {drug}
Gene: {gene}
Phenotype: {phenotype}
Risk Level: {risk_level}
Clinical Context: {clinical_guidance}

Provide:
1. Clear summary of the interaction and why it matters
2. Specific impact of '{phenotype}' phenotype on {drug} metabolism
3. Why this is classified as '{risk_level}' risk
4. Key patient safety points

Keep under 180 words. Use clear, medical but accessible language.
""",

    PromptTemplate.DOSING_ADJUSTMENT.value: """
Provide dosing guidance based on pharmacogenomics:

Drug: {drug}
Patient Phenotype: {phenotype}
Gene: {gene}
Standard Dose: {standard_dose}
Risk Assessment: {risk_level}

Explain:
1. How the phenotype affects dose metabolism
2. Recommended dose adjustment (if any)
3. Monitoring recommendations
4. Key warning signs to watch for

Keep under 200 words. Emphasize safety.
""",

    PromptTemplate.DRUG_SUMMARY.value: """
Provide a pharmacogenomic summary for {drug}:

Key Genes: {genes}
Patient's Phenotypes: {phenotypes}
Overall Risk: {overall_risk}

Include:
1. How {drug} is metabolized in the body
2. Key genetic factors that affect its safety/efficacy
3. Summary of patient's risk profile
4. General recommendations

Keep under 200 words. Make it informative but concise.
""",

    PromptTemplate.PHENOTYPE_INTERPRETATION.value: """
Interpret the pharmacogenomic phenotype:

Gene: {gene}
Phenotype: {phenotype}
Activity Score: {activity_score}

Explain:
1. What this phenotype means for drug metabolism
2. Which drugs are commonly affected by this phenotype
3. General metabolism pattern (fast, slow, affected)
4. Clinical significance

Keep under 150 words. Use clear terminology.
"""
}


class PromptBuilder:
    """Builder for constructing prompts from templates."""
    
    def __init__(self):
        """Initialize the prompt builder."""
        self.system_role = "You are an expert pharmacogenomics assistant. Provide clear, accurate, and clinically relevant explanations. Avoid medical jargon where possible, but be precise."
    
    def build_variant_explanation(self, gene: str, diplotype: str, phenotype: str, activity_score: float) -> str:
        """Build variant explanation prompt."""
        template = PROMPT_TEMPLATES[PromptTemplate.VARIANT_EXPLANATION.value]
        return template.format(
            gene=gene,
            diplotype=diplotype,
            phenotype=phenotype,
            activity_score=f"{activity_score:.2f}"
        ).strip()
    
    def build_risk_explanation(self, drug: str, gene: str, phenotype: str, 
                              risk_level: str, clinical_guidance: str) -> str:
        """Build risk explanation prompt."""
        template = PROMPT_TEMPLATES[PromptTemplate.RISK_EXPLANATION.value]
        return template.format(
            drug=drug,
            gene=gene,
            phenotype=phenotype,
            risk_level=risk_level,
            clinical_guidance=clinical_guidance
        ).strip()
    
    def build_dosing_adjustment(self, drug: str, phenotype: str, gene: str,
                               standard_dose: str, risk_level: str) -> str:
        """Build dosing adjustment prompt."""
        template = PROMPT_TEMPLATES[PromptTemplate.DOSING_ADJUSTMENT.value]
        return template.format(
            drug=drug,
            phenotype=phenotype,
            gene=gene,
            standard_dose=standard_dose,
            risk_level=risk_level
        ).strip()
    
    def build_drug_summary(self, drug: str, genes: list, phenotypes: list, 
                          overall_risk: str) -> str:
        """Build drug summary prompt."""
        template = PROMPT_TEMPLATES[PromptTemplate.DRUG_SUMMARY.value]
        return template.format(
            drug=drug,
            genes=", ".join(genes),
            phenotypes=", ".join(phenotypes),
            overall_risk=overall_risk
        ).strip()
    
    def build_phenotype_interpretation(self, gene: str, phenotype: str, 
                                      activity_score: float) -> str:
        """Build phenotype interpretation prompt."""
        template = PROMPT_TEMPLATES[PromptTemplate.PHENOTYPE_INTERPRETATION.value]
        return template.format(
            gene=gene,
            phenotype=phenotype,
            activity_score=f"{activity_score:.2f}"
        ).strip()
    
    def get_system_role(self) -> str:
        """Get the system role for LLM."""
        return self.system_role
    
    @staticmethod
    def get_available_templates() -> Dict[str, str]:
        """Get all available templates."""
        return PROMPT_TEMPLATES.copy()
