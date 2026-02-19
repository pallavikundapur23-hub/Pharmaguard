"""
Comprehensive LLM integration for PharmaGuard
Provides complete explanation pipeline with caching and templates
"""
from typing import Dict, List, Optional, Any
from src.gene_models import Phenotype, RiskLevel
from src.llm_cache import ExplanationCache
from src.llm_prompt_templates import PromptBuilder


class PharmaGuardExplainer:
    """
    High-level interface for LLM explanations in PharmaGuard.
    Integrates caching, templates, and OpenAI API.
    """
    
    def __init__(self, llm_explainer=None):
        """
        Initialize the explainer.
        
        Args:
            llm_explainer: LLMExplainer instance (optional, will be imported if None)
        """
        self.llm = llm_explainer
        self.cache = ExplanationCache()
        self.prompt_builder = PromptBuilder()
    
    def explain_risk_profile(self, drug: str, gene: str, phenotype: str, 
                            risk_level: str, clinical_guidance: str) -> Dict[str, Any]:
        """
        Generate complete explanation for a drug-gene risk profile.
        
        Args:
            drug: Drug name
            gene: Gene name
            phenotype: Patient's phenotype
            risk_level: Assessed risk level
            clinical_guidance: Clinical context
        
        Returns:
            Dict with explanation, risk summary, and recommendations
        """
        if not self.llm:
            return self._build_fallback_explanation(drug, gene, phenotype, risk_level)
        
        result = self.llm.get_risk_explanation(drug, gene, phenotype, risk_level, clinical_guidance)
        
        return {
            "drug": drug,
            "gene": gene,
            "phenotype": phenotype,
            "risk_level": risk_level,
            "explanation": result.get("summary", ""),
            "status": result.get("status"),
            "from_cache": result.get("from_cache", False),
            "recommendations": self._get_risk_recommendations(risk_level)
        }
    
    def explain_variant(self, gene: str, diplotype: str, phenotype: str, 
                       activity_score: float) -> Dict[str, Any]:
        """
        Generate explanation for a genetic variant.
        
        Args:
            gene: Gene name
            diplotype: Diplotype (e.g., "*1/*1")
            phenotype: Resulting phenotype
            activity_score: Metabolic activity score
        
        Returns:
            Dict with variant explanation and interpretation
        """
        if not self.llm:
            return self._build_fallback_variant_explanation(gene, diplotype, phenotype, activity_score)
        
        result = self.llm.get_variant_explanation(gene, diplotype, phenotype, activity_score)
        
        return {
            "gene": gene,
            "diplotype": diplotype,
            "phenotype": phenotype,
            "activity_score": activity_score,
            "explanation": result.get("summary", ""),
            "status": result.get("status"),
            "from_cache": result.get("from_cache", False),
            "metabolism_category": self._categorize_metabolism(activity_score)
        }
    
    def explain_drug_interactions(self, drug: str, genes: Dict[str, str], 
                                 risk_levels: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for multiple gene-drug interactions.
        
        Args:
            drug: Drug name
            genes: Dict of {gene: phenotype}
            risk_levels: Dict of {gene: risk_level}
        
        Returns:
            Dict with comprehensive drug interaction explanation
        """
        explanations = {}
        max_risk = "SAFE"
        
        for gene, phenotype in genes.items():
            risk = risk_levels.get(gene, "UNKNOWN")
            
            # Update max risk
            if self._compare_risks(risk, max_risk) > 0:
                max_risk = risk
            
            # Get individual explanation
            if self.llm:
                exp = self.llm.get_risk_explanation(
                    drug, gene, phenotype, risk,
                    f"Standard CPIC guidance for {drug} and {gene}"
                )
                explanations[gene] = {
                    "phenotype": phenotype,
                    "risk": risk,
                    "explanation": exp.get("summary", "")
                }
        
        return {
            "drug": drug,
            "individual_interactions": explanations,
            "overall_risk": max_risk,
            "summary": self._build_interaction_summary(drug, explanations, max_risk)
        }
    
    def get_clinical_recommendations(self, drug: str, risk_level: str, 
                                    phenotype: str) -> List[str]:
        """
        Get clinical recommendations based on risk level.
        
        Args:
            drug: Drug name
            risk_level: Risk level
            phenotype: Patient phenotype
        
        Returns:
            List of recommendations
        """
        recommendations = {
            "TOXIC": [
                f"⚠️ AVOID {drug} - High toxicity risk",
                f"Consider alternative medications for patients with {phenotype} phenotype",
                "Refer to clinical pharmacist for alternative drug selection",
                "If {drug} is essential: Start with lowest dose and monitor closely"
            ],
            "SAFE": [
                f"✓ {drug} is safe for use",
                "Standard dosing appropriate for this phenotype",
                "Continue routine monitoring"
            ],
            "ADJUST": [
                f"⚠️ Dose adjustment needed for {drug}",
                f"Phenotype: {phenotype} - Consider dose modification",
                "Monitor for therapeutic efficacy and adverse effects",
                "Consider therapeutic drug monitoring"
            ],
            "INEFFECTIVE": [
                f"⚠️ {drug} may be ineffective",
                f"High likelihood of treatment failure due to {phenotype}",
                "Consider alternative medication with better metabolic profile",
                "Increase dose with caution and close monitoring"
            ]
        }
        
        return recommendations.get(risk_level.upper(), ["Consult with pharmacist for personalized guidance"])
    
    def _get_risk_recommendations(self, risk_level: str) -> List[str]:
        """Get general recommendations for a risk level."""
        return self.get_clinical_recommendations("", risk_level, "")
    
    def _categorize_metabolism(self, activity_score: float) -> str:
        """Categorize metabolism based on activity score."""
        if activity_score >= 1.5:
            return "Rapid/Ultra-Rapid Metabolizer"
        elif activity_score >= 0.75:
            return "Normal Metabolizer"
        elif activity_score >= 0.25:
            return "Intermediate Metabolizer"
        else:
            return "Poor Metabolizer"
    
    def _compare_risks(self, risk1: str, risk2: str) -> int:
        """
        Compare two risk levels.
        Returns: 1 if risk1 > risk2, -1 if risk1 < risk2, 0 if equal
        """
        risk_order = {"SAFE": 0, "ADJUST": 1, "INEFFECTIVE": 2, "TOXIC": 3}
        r1 = risk_order.get(risk1.upper(), 0)
        r2 = risk_order.get(risk2.upper(), 0)
        return r1 - r2
    
    def _build_fallback_explanation(self, drug: str, gene: str, phenotype: str, 
                                   risk_level: str) -> Dict[str, Any]:
        """Build fallback explanation when LLM is unavailable."""
        fallback_explanations = {
            ("TOXIC", "Ultra-Rapid Metabolizer"): f"{drug} metabolism is significantly increased in {gene} {phenotype} patients, leading to rapid drug metabolism and potential overdose if standard doses are used.",
            ("TOXIC", "Poor Metabolizer"): f"{drug} is poorly metabolized in {gene} {phenotype} patients, leading to drug accumulation and high toxicity risk.",
            ("SAFE", "Normal Metabolizer"): f"{drug} is appropriately metabolized in {gene} {phenotype} patients. Standard dosing is safe and recommended.",
            ("ADJUST", "Intermediate Metabolizer"): f"{drug} metabolism is somewhat reduced in {gene} {phenotype} patients. Dose adjustment may be beneficial.",
            ("INEFFECTIVE", "Poor Metabolizer"): f"{drug} efficacy is reduced in {gene} {phenotype} patients due to poor metabolism. Alternative medications should be considered."
        }
        
        key = (risk_level.upper(), phenotype)
        explanation = fallback_explanations.get(key, f"Clinical guidance: {drug} treatment in {gene} {phenotype} patients requires individual assessment.")
        
        return {
            "drug": drug,
            "gene": gene,
            "phenotype": phenotype,
            "risk_level": risk_level,
            "explanation": explanation,
            "status": "fallback",
            "from_cache": False
        }
    
    def _build_fallback_variant_explanation(self, gene: str, diplotype: str, 
                                           phenotype: str, activity_score: float) -> Dict[str, Any]:
        """Build fallback variant explanation when LLM is unavailable."""
        metabolism = self._categorize_metabolism(activity_score)
        explanation = f"The {gene} gene with diplotype {diplotype} results in a {phenotype} phenotype with an activity score of {activity_score:.2f}. This indicates a {metabolism} drug metabolism pattern."
        
        return {
            "gene": gene,
            "diplotype": diplotype,
            "phenotype": phenotype,
            "activity_score": activity_score,
            "explanation": explanation,
            "status": "fallback",
            "from_cache": False,
            "metabolism_category": metabolism
        }
    
    def _build_interaction_summary(self, drug: str, interactions: Dict, max_risk: str) -> str:
        """Build a summary of multiple drug-gene interactions."""
        risk_emojis = {
            "TOXIC": "⚠️",
            "ADJUST": "⚠️",
            "INEFFECTIVE": "⚠️",
            "SAFE": "✓"
        }
        
        interaction_count = len(interactions)
        emoji = risk_emojis.get(max_risk, "•")
        
        return f"{emoji} {drug} assessment across {interaction_count} gene(s): Overall risk level is {max_risk}. Individual gene-specific considerations apply."


def get_explainer(api_key: Optional[str] = None, provider: str = None) -> PharmaGuardExplainer:
    """
    Factory function to get PharmaGuard explainer instance.
    Auto-detects provider: uses Groq if available, otherwise OpenAI.
    
    Args:
        api_key: Optional API key (will auto-detect from environment)
        provider: Optional provider name ('groq' or 'openai')
    
    Returns:
        PharmaGuardExplainer instance
    """
    try:
        from backend.src.llm_explainer import LLMExplainer
        llm = LLMExplainer(api_key=api_key, provider=provider)
        return PharmaGuardExplainer(llm_explainer=llm)
    except (ImportError, ValueError) as e:
        # Return explainer without LLM if initialization fails
        print(f"Warning: LLM initialization failed: {e}")
        return PharmaGuardExplainer(llm_explainer=None)
