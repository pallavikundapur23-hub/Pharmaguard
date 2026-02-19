"""
Advanced Risk Prediction Algorithm
Sophisticated pharmacogenomic risk assessment with multiple factors and scoring
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math
from src.gene_models import Phenotype, RiskLevel


@dataclass
class ActivityScore:
    """
    Represents metabolic activity based on alleles
    
    Activity scores determine how active a metabolizer is:
    - Wildtype (*1): 1.0 activity units
    - Loss-of-function (*3, *4, etc.): 0.0 activity units
    - Reduced function (*10, *41): 0.5 activity units
    """
    wildtype_activity: float = 1.0      # *1 allele
    reduced_activity: float = 0.5        # *10, *41, *17, etc.
    no_function: float = 0.0             # *3, *4, *5, *6, *7, etc.


@dataclass
class RiskScore:
    """Risk assessment with granular scoring"""
    risk_level: RiskLevel
    raw_score: float                     # 0-100 scale
    confidence: float                    # 0-1 (confidence in prediction)
    severity: str                        # none/low/moderate/high/critical
    clinical_significance: str           # brief explanation
    recommendation_strength: str         # Strong/Moderate/Weak
    

class RiskPredictionAlgorithm:
    """
    Advanced risk prediction algorithm that considers:
    - Allele contributions (activity scores)
    - Phenotype strength
    - Drug sensitivity to phenotype variations
    - Multi-gene interactions
    - Data quality and confidence
    - CPIC guidelines alignment
    """
    
    # Gene-specific activity scores
    ACTIVITY_SCORES = {
        "CYP2D6": {
            "*1": 1.0,      # Wildtype/normal function
            "*2": 1.0,      # Normal function
            "*3": 0.0,      # Nonfunctional
            "*4": 0.0,      # Nonfunctional
            "*5": 0.0,      # Deletion
            "*6": 0.0,      # Nonfunctional
            "*7": 0.0,      # Nonfunctional
            "*8": 0.0,      # Nonfunctional
            "*9": 0.5,      # Reduced function
            "*10": 0.5,     # Reduced function
            "*17": 0.5,     # Reduced function
            "*29": 0.5,     # Reduced function
            "*41": 0.5,     # Reduced function (splicing)
        },
        "CYP2C19": {
            "*1": 1.0,      # Wildtype
            "*2": 0.0,      # Loss of function
            "*3": 0.0,      # Loss of function
            "*4": 0.0,      # Loss of function
            "*5": 0.0,      # Loss of function
            "*6": 0.0,      # Loss of function
            "*7": 0.0,      # Loss of function
            "*8": 1.0,      # Increased function
            "*17": 1.0,     # Increased function
        },
        "CYP2C9": {
            "*1": 1.0,      # Wildtype
            "*2": 0.8,      # Reduced (~60-75% activity)
            "*3": 0.05,     # Reduced (5-10% activity)
            "*4": 0.5,      # Reduced
            "*5": 0.2,      # Reduced
            "*6": 0.0,      # No function
            "*11": 0.8,     # Reduced
        },
        "TPMT": {
            "*1": 1.0,      # Wildtype/normal
            "*2": 0.0,      # Low activity
            "*3A": 0.0,     # Low activity
            "*3B": 0.0,     # Low activity
            "*3C": 0.0,     # Low activity
            "*4": 1.0,      # Normal (variant of *1)
            "*5": 0.0,      # No function
            "*6": 0.0,      # No function
        },
        "SLCO1B1": {
            "*1A": 1.0,     # High transporterfunction
            "*1B": 1.0,     # High transporter function
            "*5": 0.0,      # Loss of function
            "*15": 0.5,     # Reduced function
            "*17": 0.5,     # Reduced function
        },
        "DPYD": {
            "*1": 1.0,      # Normal enzyme function
            "*2A": 0.0,     # Deficiency (nonfunctional)
            "*13": 0.0,     # Deficiency
            "*1A": 1.0,     # Normal variant
        },
    }
    
    # Drug sensitivity multipliers
    # How sensitive is each drug to phenotype variation
    DRUG_SENSITIVITY = {
        "Codeine": {
            "gene": "CYP2D6",
            "sensitivity": 1.0,        # Very sensitive to CYP2D6
            "requires_conversion": True,  # Prodrug needing metabolism
        },
        "Warfarin": {
            "gene": "CYP2C9",
            "sensitivity": 0.9,        # Highly sensitive
            "requires_conversion": False,
        },
        "Clopidogrel": {
            "gene": "CYP2C19",
            "sensitivity": 1.0,        # Extremely sensitive (prodrug)
            "requires_conversion": True,
        },
        "Simvastatin": {
            "gene": "SLCO1B1",
            "sensitivity": 0.85,       # Moderately sensitive (transporter)
            "requires_conversion": False,
        },
        "Azathioprine": {
            "gene": "TPMT",
            "sensitivity": 1.0,        # Very sensitive
            "requires_conversion": False,
        },
        "Fluorouracil": {
            "gene": "DPYD",
            "sensitivity": 1.0,        # Extremely sensitive (toxicity)
            "requires_conversion": False,
        },
        "Metoprolol": {
            "gene": "CYP2D6",
            "sensitivity": 0.7,        # Moderately sensitive
            "requires_conversion": False,
        },
        "Amitriptyline": {
            "gene": "CYP2D6",
            "sensitivity": 0.8,        # Moderately-highly sensitive
            "requires_conversion": False,
        },
    }
    
    def __init__(self):
        self.activity_scores = self.ACTIVITY_SCORES
        self.drug_sensitivity = self.DRUG_SENSITIVITY
    
    def calculate_activity_score(
        self,
        gene: str,
        diplotype: Tuple[str, str]
    ) -> Tuple[float, str]:
        """
        Calculate total metabolic activity for a diplotype
        
        Args:
            gene: Gene name (CYP2D6, CYP2C19, etc.)
            diplotype: Tuple of alleles like ("*1", "*3")
        
        Returns:
            (activity_score: 0-2.0, phenotype_description)
        
        Examples:
            (*1/*1) = 1.0 + 1.0 = 2.0 (Ultra-rapid if duplicated)
            (*1/*3) = 1.0 + 0.0 = 1.0 (Intermediate)
            (*3/*4) = 0.0 + 0.0 = 0.0 (Poor metabolizer)
            (*1/*10) = 1.0 + 0.5 = 1.5 (Rapid)
        """
        if gene not in self.activity_scores:
            return 1.0, f"Activity data not available for {gene}"
        
        scores_dict = self.activity_scores[gene]
        allele1, allele2 = diplotype
        
        # Get activity for each allele (default to 1.0 if unknown)
        activity1 = scores_dict.get(allele1, 1.0)
        activity2 = scores_dict.get(allele2, 1.0)
        
        total_activity = activity1 + activity2
        
        # Determine phenotype from activity
        phenotype = self._activity_to_phenotype(total_activity, gene)
        
        return total_activity, phenotype
    
    def _activity_to_phenotype(self, activity: float, gene: str) -> str:
        """Convert activity score to phenotype description"""
        
        # Standard CYP450 cutoffs
        if gene in ["CYP2D6", "CYP2C19"]:
            if activity >= 1.75:
                return "Ultra-Rapid Metabolizer"
            elif activity >= 1.25:
                return "Rapid Metabolizer"
            elif activity >= 0.75:
                return "Normal Metabolizer"
            elif activity >= 0.25:
                return "Intermediate Metabolizer"
            else:
                return "Poor Metabolizer"
        
        # CYP2C9 has different cutoffs (less impact from *2)
        elif gene == "CYP2C9":
            if activity >= 1.8:
                return "Normal Metabolizer"
            elif activity >= 1.0:
                return "Intermediate Metabolizer"
            else:
                return "Poor Metabolizer"
        
        # TPMT metabolizer status
        elif gene == "TPMT":
            if activity >= 1.6:
                return "Normal Metabolizer"
            elif activity >= 0.5:
                return "Intermediate Metabolizer"
            else:
                return "Poor Metabolizer"
        
        # SLCO1B1 transporter
        elif gene == "SLCO1B1":
            if activity >= 1.8:
                return "Normal Transporter"
            elif activity >= 0.9:
                return "Intermediate Transporter"
            else:
                return "Poor Transporter"
        
        # DPYD enzyme
        elif gene == "DPYD":
            if activity >= 1.8:
                return "Normal Metabolizer"
            else:
                return "DPYD Deficiency"
        
        return "Unknown Phenotype"
    
    def calculate_confidence(
        self,
        gene: str,
        activity_score: float,
        phenotype: Phenotype
    ) -> float:
        """
        Calculate confidence in the prediction (0-1)
        
        Factors:
        - Phenotype boundaries (clear vs borderline)
        - Gene data availability
        - Activity score certainty
        """
        confidence = 0.9  # Base confidence
        
        # Reduce confidence for borderline cases
        if gene in ["CYP2D6", "CYP2C19"]:
            # Borderline between phenotypes
            if 0.5 < activity_score % 0.5 < 0.4:
                confidence -= 0.1
            # Very low activity (rare alleles)
            elif activity_score < 0.3:
                confidence -= 0.05
        
        # Reduce confidence for rare phenotypes
        if phenotype in [Phenotype.ULTRA_RAPID, Phenotype.NO_FUNCTION]:
            confidence -= 0.05
        
        return max(0.5, min(1.0, confidence))  # Clamp to 0.5-1.0
    
    def calculate_drug_risk(
        self,
        drug: str,
        phenotype: Phenotype,
        activity_score: Optional[float] = None
    ) -> RiskScore:
        """
        Calculate complete risk score for drug-phenotype combination
        
        Incorporates:
        - CPIC guidelines
        - Activity score
        - Drug sensitivity
        - Confidence
        """
        
        if drug not in self.drug_sensitivity:
            # Unknown drug - graceful fallback
            return RiskScore(
                risk_level=RiskLevel.UNKNOWN,
                raw_score=50.0,
                confidence=0.3,
                severity="none",
                clinical_significance="No pharmacogenomic data available",
                recommendation_strength="Weak"
            )
        
        sensitivity = self.drug_sensitivity[drug]["sensitivity"]
        
        # Map phenotype to risk
        risk_mapping = self._get_phenotype_risk_mapping(drug)
        risk_level = risk_mapping.get(phenotype, RiskLevel.UNKNOWN)
        
        # Calculate raw score (0-100)
        raw_score = self._phenotype_to_score(phenotype, sensitivity)
        
        # Adjust for activity score if provided
        if activity_score is not None:
            raw_score = self._adjust_score_by_activity(raw_score, activity_score, drug)
        
        # Calculate confidence
        confidence = self.calculate_confidence(
            self.drug_sensitivity[drug]["gene"],
            activity_score or 1.0,
            phenotype
        )
        
        # Determine severity
        severity = self._risk_to_severity(risk_level)
        
        # Clinical significance
        clinical_sig = self._get_clinical_significance(drug, phenotype, risk_level)
        
        # Recommendation strength
        strength = self._get_recommendation_strength(risk_level)
        
        return RiskScore(
            risk_level=risk_level,
            raw_score=raw_score,
            confidence=confidence,
            severity=severity,
            clinical_significance=clinical_sig,
            recommendation_strength=strength
        )
    
    def _get_phenotype_risk_mapping(self, drug: str) -> Dict[Phenotype, RiskLevel]:
        """Get CPIC risk mapping for each phenotype"""
        
        mappings = {
            "Codeine": {
                Phenotype.ULTRA_RAPID: RiskLevel.TOXIC,
                Phenotype.RAPID: RiskLevel.ADJUST_DOSAGE,
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
                Phenotype.POOR: RiskLevel.INEFFECTIVE,
                Phenotype.NO_FUNCTION: RiskLevel.INEFFECTIVE,
            },
            "Warfarin": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
                Phenotype.POOR: RiskLevel.ADJUST_DOSAGE,
            },
            "Clopidogrel": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
                Phenotype.POOR: RiskLevel.INEFFECTIVE,
            },
            "Simvastatin": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
                Phenotype.POOR: RiskLevel.ADJUST_DOSAGE,
            },
            "Azathioprine": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
                Phenotype.POOR: RiskLevel.TOXIC,
            },
            "Fluorouracil": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.INTERMEDIATE: RiskLevel.ADJUST_DOSAGE,
                Phenotype.POOR: RiskLevel.TOXIC,
            },
            "Metoprolol": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.POOR: RiskLevel.ADJUST_DOSAGE,
            },
            "Amitriptyline": {
                Phenotype.NORMAL: RiskLevel.SAFE,
                Phenotype.POOR: RiskLevel.ADJUST_DOSAGE,
            },
        }
        
        return mappings.get(drug, {})
    
    def _phenotype_to_score(self, phenotype: Phenotype, sensitivity: float) -> float:
        """Convert phenotype to numerical risk score (0-100)"""
        
        base_scores = {
            Phenotype.ULTRA_RAPID: 20,      # Risk (toxicity)
            Phenotype.RAPID: 30,
            Phenotype.NORMAL: 50,            # Safe (baseline)
            Phenotype.INTERMEDIATE: 60,
            Phenotype.POOR: 80,              # Risk (ineffective)
            Phenotype.NO_FUNCTION: 90,
        }
        
        base = base_scores.get(phenotype, 50)
        
        # Adjust by drug sensitivity
        # High sensitivity = higher risk for non-normal phenotypes
        if phenotype != Phenotype.NORMAL:
            base += (sensitivity * 10)
        
        return min(100, max(0, base))
    
    def _adjust_score_by_activity(
        self,
        base_score: float,
        activity_score: float,
        drug: str
    ) -> float:
        """Fine-tune score based on exact activity value"""
        
        if drug not in self.drug_sensitivity:
            return base_score
        
        sensitivity = self.drug_sensitivity[drug]["sensitivity"]
        
        # Activity score of 2.0 is optimal for most drugs
        optimal_activity = 2.0
        
        # Calculate deviation from optimal
        deviation = abs(activity_score - optimal_activity) / optimal_activity
        
        # Apply sensitivity multiplier
        adjustment = deviation * sensitivity * 20  # 20 point max adjustment
        
        return min(100, max(0, base_score + adjustment))
    
    def _risk_to_severity(self, risk_level: RiskLevel) -> str:
        """Convert risk level to severity descriptor"""
        severity_map = {
            RiskLevel.SAFE: "none",
            RiskLevel.ADJUST_DOSAGE: "moderate",
            RiskLevel.TOXIC: "critical",
            RiskLevel.INEFFECTIVE: "high",
            RiskLevel.UNKNOWN: "none",
        }
        return severity_map.get(risk_level, "unknown")
    
    def _get_clinical_significance(
        self,
        drug: str,
        phenotype: Phenotype,
        risk_level: RiskLevel
    ) -> str:
        """Get clinical significance explanation"""
        
        if risk_level == RiskLevel.SAFE:
            return f"{drug} expected to be effective at standard doses for {phenotype.value}"
        elif risk_level == RiskLevel.ADJUST_DOSAGE:
            return f"{drug} dosage adjustment recommended for {phenotype.value}"
        elif risk_level == RiskLevel.TOXIC:
            return f"HIGH RISK: {drug} toxicity likely for {phenotype.value}"
        elif risk_level == RiskLevel.INEFFECTIVE:
            return f"HIGH RISK: {drug} ineffective for {phenotype.value} - alternative recommended"
        else:
            return "Clinical significance unclear - manual review recommended"
    
    def _get_recommendation_strength(self, risk_level: RiskLevel) -> str:
        """Get strength of CPIC recommendation"""
        if risk_level == RiskLevel.SAFE:
            return "Strong"
        elif risk_level == RiskLevel.ADJUST_DOSAGE:
            return "Moderate"
        elif risk_level == RiskLevel.TOXIC or risk_level == RiskLevel.INEFFECTIVE:
            return "Strong"
        else:
            return "Weak"
    
    def calculate_multi_gene_risk(
        self,
        drug: str,
        gene_phenotypes: Dict[str, Phenotype]
    ) -> RiskScore:
        """
        Calculate risk considering multiple gene contributions
        
        For drugs affected by multiple genes, use highest risk
        """
        risks = []
        
        for gene, phenotype in gene_phenotypes.items():
            if phenotype:
                risk = self.calculate_drug_risk(drug, phenotype)
                risks.append(risk)
        
        if not risks:
            return RiskScore(
                risk_level=RiskLevel.UNKNOWN,
                raw_score=50.0,
                confidence=0.3,
                severity="none",
                clinical_significance="No phenotype data",
                recommendation_strength="Weak"
            )
        
        # Return highest severity risk
        risk_hierarchy = [
            RiskLevel.TOXIC,
            RiskLevel.INEFFECTIVE,
            RiskLevel.ADJUST_DOSAGE,
            RiskLevel.SAFE,
        ]
        
        for risk_level in risk_hierarchy:
            for risk in risks:
                if risk.risk_level == risk_level:
                    return risk
        
        return risks[0]  # Fallback


def get_risk_prediction_algorithm() -> RiskPredictionAlgorithm:
    """Factory function to get algorithm instance"""
    return RiskPredictionAlgorithm()
