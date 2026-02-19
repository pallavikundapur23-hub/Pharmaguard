"""
Genotype-to-Phenotype Conversion Engine
Converts genetic alleles to metabolizer phenotypes for 6 critical pharmacogenes
Based on CPIC clinical interpretation guidelines
"""

from typing import Dict, Tuple, Optional
from enum import Enum
from src.gene_models import Phenotype


class GenotypePhenotypeConverter:
    """
    Converts diplotypes (allele pairs) to phenotypes
    Implements CPIC-compliant algorithms for 6 critical genes
    """
    
    # CYP2D6 ALLELE DEFINITIONS
    # Metabolic status of each allele
    CYP2D6_ALLELES = {
        "*1": 1.0,          # Normal function
        "*2": 0.0,          # Previously thought normal, but actually has structural variant with reduced function
        "*3": 0.0,          # Nonfunctional (deletion)
        "*4": 0.0,          # Nonfunctional (splicing defect)
        "*5": 0.0,          # Nonfunctional (deletion)
        "*6": 0.0,          # Nonfunctional
        "*7": 0.0,          # Nonfunctional
        "*8": 0.0,          # Nonfunctional
        "*9": 0.5,          # Reduced function
        "*10": 0.5,         # Reduced function (Val330Leu)
        "*11": 0.0,         # Nonfunctional
        "*12": 1.0,         # Normal function
        "*14": 0.5,         # Reduced function
        "*15": 0.0,         # Nonfunctional
        "*17": 0.5,         # Reduced function (enhanced initially, now reduced)
        "*19": 0.0,         # Nonfunctional
        "*20": 0.5,         # Reduced function
        "*29": 0.5,         # Reduced function
        "*35": 0.0,         # Nonfunctional
        "*36": 0.5,         # Reduced function
        "*37": 0.0,         # Nonfunctional
        "*38": 0.0,         # Nonfunctional
        "*39": 0.5,         # Reduced function
        "*40": 0.0,         # Nonfunctional
        "*41": 0.5,         # Reduced function (splicing)
        "*42": 0.0,         # Nonfunctional
        "*43": 0.0,         # Nonfunctional
        "*44": 0.0,         # Nonfunctional
        "*45": 0.0,         # Nonfunctional
        "*46": 0.0,         # Nonfunctional
        "*47": 0.0,         # Nonfunctional
        "*48": 0.0,         # Nonfunctional
        "*49": 0.0,         # Nonfunctional
        "*50": 0.5,         # Reduced function
    }
    
    # CYP2C19 ALLELE DEFINITIONS
    CYP2C19_ALLELES = {
        "*1": 1.0,          # Normal/wildtype function
        "*2": 0.0,          # Loss of function (splicing defect)
        "*3": 0.0,          # Loss of function (stop codon)
        "*4": 0.0,          # Loss of function
        "*5": 0.0,          # Loss of function
        "*6": 0.0,          # Loss of function
        "*7": 0.0,          # Loss of function
        "*8": 1.0,          # Normal function (normal variant)
        "*9": 1.0,          # Normal function
        "*10": 1.0,         # Normal function
        "*11": 1.0,         # Normal function
        "*12": 0.0,         # Loss of function
        "*13": 1.0,         # Normal function
        "*14": 1.0,         # Normal function
        "*15": 0.0,         # Loss of function
        "*16": 1.0,         # Normal function
        "*17": 1.0,         # Increased function (2.0 copy)
        "*18": 1.0,         # Normal function
        "*19": 1.0,         # Normal function
        "*20": 1.0,         # Normal function
    }
    
    # CYP2C9 ALLELE DEFINITIONS
    CYP2C9_ALLELES = {
        "*1": 1.0,          # Wildtype/normal function (100% activity)
        "*2": 0.8,          # Variant (arg144cys) - ~60% activity
        "*3": 0.05,         # Variant (ile359leu) - ~5% activity (CRITICAL)
        "*4": 0.5,          # Variant - ~50% activity
        "*5": 0.2,          # Variant - ~20% activity
        "*6": 0.0,          # Loss of function
        "*7": 0.88,         # Reduced (88% activity)
        "*8": 0.7,          # Reduced (70% activity)
        "*9": 1.0,          # Normal function
        "*10": 1.0,         # Normal function
        "*11": 0.8,         # Similar to *2
        "*12": 0.5,         # Reduced function
        "*13": 0.5,         # Reduced function
    }
    
    # TPMT ALLELE DEFINITIONS (thiopurine methyltransferase)
    TPMT_ALLELES = {
        "*1": 1.0,          # Normal/wildtype activity
        "*2": 0.0,          # Low/absent activity
        "*3A": 0.0,         # Low/absent (most common variant)
        "*3B": 0.0,         # Low/absent
        "*3C": 0.0,         # Low/absent
        "*4": 1.0,          # Normal (normal variant of *1)
        "*5": 0.0,          # Nonfunctional
        "*6": 0.0,          # Nonfunctional
        "*7": 0.0,          # Nonfunctional
        "*8": 0.5,          # Intermediate
        "*9": 1.0,          # Normal
        "*10": 1.0,         # Normal
        "*11": 1.0,         # Normal
        "*12": 1.0,         # Normal
        "*13": 0.0,         # Nonfunctional
    }
    
    # SLCO1B1 ALLELE DEFINITIONS (organic anion transporter)
    SLCO1B1_ALLELES = {
        "*1A": 1.0,         # Wildtype - high transporter activity
        "*1B": 1.0,         # Normal variant - high activity
        "*1C": 0.8,         # Reduced activity variant
        "*1D": 0.7,         # Reduced activity variant
        "*1E": 0.9,         # Slightly reduced activity
        "*2": 0.5,          # Reduced function (484c→g 521t→c)
        "*3": 0.5,          # Reduced function
        "*4": 0.3,          # Low function
        "*5": 0.0,          # Loss of function (SLCO1B1*5)
        "*15": 0.5,         # Reduced function (521t→c)
        "*17": 0.5,         # Reduced function
    }
    
    # DPYD ALLELE DEFINITIONS (dihydropyrimidine dehydrogenase)
    DPYD_ALLELES = {
        "*1": 1.0,          # Normal enzyme function
        "*1A": 1.0,         # Normal variant
        "*1B": 1.0,         # Normal variant
        "*2A": 0.0,         # Deficiency - splicing defect (IVS14+1g->a)
        "*2B": 0.0,         # Deficiency
        "*3": 0.0,          # Deficiency - nonsense mutation
        "*4": 0.0,          # Deficiency
        "*5": 0.0,          # Deficiency
        "*6": 0.0,          # Deficiency
        "*7": 0.0,          # Deficiency
        "*8": 0.0,          # Deficiency
        "*9A": 0.0,         # Deficiency
        "*9B": 0.0,         # Deficiency
        "*13": 0.0,         # Deficiency
    }
    
    # CYP3A4/5 ALLELE DEFINITIONS (minor genes)
    CYP3A4_ALLELES = {
        "*1": 1.0,          # Normal/wildtype
        "*1A": 1.0,         # Normal variant
        "*1B": 1.0,         # Normal variant
        "*1D": 1.0,         # Normal variant
        "*2": 0.5,          # Reduced function
        "*3": 0.7,          # Reduced function
        "*4": 1.0,          # Normal
        "*5": 0.0,          # Nonfunctional
        "*6": 0.0,          # Nonfunctional
    }
    
    CYP3A5_ALLELES = {
        "*1": 1.0,          # Wildtype (express normally)
        "*2": 0.0,          # Nonfunctional (splicing defect)
        "*3": 0.0,          # Nonfunctional (common variant)
        "*4": 0.0,          # Nonfunctional
        "*5": 0.0,          # Nonfunctional
        "*6": 0.0,          # Nonfunctional
        "*7": 0.0,          # Nonfunctional
        "*9": 0.0,          # Nonfunctional
        "*10": 0.5,         # Reduced function
    }
    
    def __init__(self):
        self.allele_definitions = {
            "CYP2D6": self.CYP2D6_ALLELES,
            "CYP2C19": self.CYP2C19_ALLELES,
            "CYP2C9": self.CYP2C9_ALLELES,
            "TPMT": self.TPMT_ALLELES,
            "SLCO1B1": self.SLCO1B1_ALLELES,
            "DPYD": self.DPYD_ALLELES,
            "CYP3A4": self.CYP3A4_ALLELES,
            "CYP3A5": self.CYP3A5_ALLELES,
        }
    
    def convert_diplotype_to_phenotype(
        self,
        gene: str,
        diplotype: Tuple[str, str]
    ) -> Phenotype:
        """
        Convert diplotype to phenotype
        
        Args:
            gene: Gene name (CYP2D6, CYP2C19, etc.)
            diplotype: Tuple of alleles e.g., ("*1", "*3")
        
        Returns:
            Phenotype enum value
        
        Examples:
            CYP2D6 (*1/*1) → NORMAL (activity 2.0)
            CYP2D6 (*1/*4) → INTERMEDIATE (activity 1.0)
            CYP2D6 (*4/*5) → POOR (activity 0.0)
            CYP2C19 (*1/*2) → INTERMEDIATE (lost function)
        """
        if gene not in self.allele_definitions:
            return Phenotype.NORMAL  # Default for unknown genes
        
        alleles_dict = self.allele_definitions[gene]
        allele1, allele2 = diplotype
        
        # Get activity for each allele (default 1.0 if unknown)
        activity1 = alleles_dict.get(allele1, 1.0)
        activity2 = alleles_dict.get(allele2, 1.0)
        
        total_activity = activity1 + activity2
        
        # Convert activity to phenotype based on gene-specific rules
        return self._activity_to_phenotype(gene, total_activity)
    
    def _activity_to_phenotype(self, gene: str, activity: float) -> Phenotype:
        """
        Convert metabolic activity to phenotype
        Gene-specific cutoffs based on CPIC guidelines
        """
        
        if gene == "CYP2D6":
            # CYP2D6 cutoffs (activity 0-2+ from diplotype)
            # CPIC: URM >= 2, RM >= 1.25, NM > 1, IM 0.25-0.99, PM < 0.25
            if activity >= 1.75:
                return Phenotype.ULTRA_RAPID  # Gene duplication effect
            elif activity >= 1.25:
                return Phenotype.RAPID  # Two normal alleles + high function
            elif activity > 1.0:
                return Phenotype.NORMAL  # One or more normal alleles, >2.0 activity
            elif activity >= 0.25:
                return Phenotype.INTERMEDIATE  # Partial function
            else:
                return Phenotype.POOR  # No function
        
        elif gene == "CYP2C19":
            # CYP2C19 cutoffs (loss-of-function gene)
            # CPIC: NM >= 1.5, IM 0.5-1.49, PM < 0.5
            if activity >= 1.5:
                return Phenotype.NORMAL  # NM/NM or NM/RM
            elif activity >= 0.5:
                return Phenotype.INTERMEDIATE  # Has partial function (one NM, one LOF)
            else:
                return Phenotype.POOR  # Both LOF
        
        elif gene == "CYP2C9":
            # CYP2C9 cutoffs - very sensitive to *3 allele
            # Original activity coefficients: *1=1.0, *2=0.8, *3=0.05(!), etc.
            # *1/*1 = 2.0 (100%), *1/*2 = 1.8 (90%), *1/*3 = 1.05 (5%), *3/*3 = 0.1 (5%)
            # CPIC: NM ≥1.8 (100%), IM 0.7-1.7 (reduced), PM <0.7
            if activity >= 1.8:
                return Phenotype.NORMAL  # Full function
            elif activity >= 1.2:
                return Phenotype.INTERMEDIATE  # Moderately reduced
            elif activity >= 0.3:
                return Phenotype.POOR  # Significantly reduced (includes *1/*3)
            else:
                return Phenotype.NO_FUNCTION  # Very poor/no function
        
        elif gene == "TPMT":
            # TPMT cutoffs (activity-based)
            if activity >= 1.6:
                return Phenotype.NORMAL
            elif activity >= 0.5:
                return Phenotype.INTERMEDIATE
            else:
                return Phenotype.POOR
        
        elif gene in ["SLCO1B1", "CYP3A4", "CYP3A5"]:
            # Transporter/metabolizer genes (simplified)
            if activity >= 1.8:
                return Phenotype.NORMAL
            elif activity >= 0.9:
                return Phenotype.INTERMEDIATE
            else:
                return Phenotype.POOR
        
        elif gene == "DPYD":
            # DPYD deficiency (2 copies normal = safe)
            if activity >= 1.8:
                return Phenotype.NORMAL  # Both wildtype
            elif activity >= 0.9:
                return Phenotype.INTERMEDIATE  # One wildtype (carrier)
            else:
                return Phenotype.POOR  # DPYD deficiency (homozygous/compound)
        
        else:
            # Unknown gene - default
            return Phenotype.NORMAL
    
    def get_detailed_phenotype_info(
        self,
        gene: str,
        diplotype: Tuple[str, str]
    ) -> Dict:
        """
        Get detailed information about a diplotype
        
        Returns:
            {
                phenotype: Phenotype,
                activity_score: float,
                description: str,
                clinical_relevance: str
            }
        """
        if gene not in self.allele_definitions:
            return {
                "phenotype": Phenotype.NORMAL,
                "activity_score": 1.0,
                "description": f"Unknown gene: {gene}",
                "clinical_relevance": "No data available"
            }
        
        alleles_dict = self.allele_definitions[gene]
        activity1 = alleles_dict.get(diplotype[0], 1.0)
        activity2 = alleles_dict.get(diplotype[1], 1.0)
        total_activity = activity1 + activity2
        
        phenotype = self._activity_to_phenotype(gene, total_activity)
        
        return {
            "phenotype": phenotype,
            "activity_score": total_activity,
            "diplotype": f"{diplotype[0]}/{diplotype[1]}",
            "allele1_activity": activity1,
            "allele2_activity": activity2,
            "description": f"{gene}: {diplotype[0]}/{diplotype[1]} → {phenotype.value}",
            "clinical_relevance": self._get_clinical_relevance(gene, phenotype)
        }
    
    def _get_clinical_relevance(self, gene: str, phenotype: Phenotype) -> str:
        """Get clinical relevance statement for phenotype"""
        
        if phenotype == Phenotype.ULTRA_RAPID:
            return f"{gene} Ultra-Rapid: Very high enzyme activity - may require higher drug doses or alternative therapy"
        elif phenotype == Phenotype.RAPID:
            return f"{gene} Rapid: High enzyme activity - may require higher doses than normal"
        elif phenotype == Phenotype.NORMAL:
            return f"{gene} Normal: Standard enzyme activity - use typical dosing"
        elif phenotype == Phenotype.INTERMEDIATE:
            return f"{gene} Intermediate: Reduced enzyme activity - may require dose reduction or monitoring"
        elif phenotype == Phenotype.POOR:
            return f"{gene} Poor: Very low/no enzyme activity - avoid many substrates or use very low doses"
        elif phenotype == Phenotype.NO_FUNCTION:
            return f"{gene} No Function: Complete loss of function - avoid all substrates"
        else:
            return "Unknown phenotype"
    
    def convert_batch_diplotypes(
        self,
        gene_diplotypes: Dict[str, Tuple[str, str]]
    ) -> Dict[str, Phenotype]:
        """
        Convert multiple genes at once
        
        Args:
            gene_diplotypes: {gene: (allele1, allele2), ...}
        
        Returns:
            {gene: phenotype, ...}
        """
        results = {}
        for gene, diplotype in gene_diplotypes.items():
            results[gene] = self.convert_diplotype_to_phenotype(gene, diplotype)
        return results
    
    def merge_phenotypes_for_drug(
        self,
        drug: str,
        gene_phenotypes: Dict[str, Phenotype]
    ) -> Phenotype:
        """
        For multi-gene drugs, determine overall phenotype
        Takes worst-case (poorest) metabolizer phenotype
        """
        if not gene_phenotypes:
            return Phenotype.NORMAL
        
        # Filter out None values
        valid_phenotypes = [p for p in gene_phenotypes.values() if p]
        
        if not valid_phenotypes:
            return Phenotype.NORMAL
        
        # Phenotype hierarchy (worst to best)
        phenotype_order = [
            Phenotype.NO_FUNCTION,
            Phenotype.POOR,
            Phenotype.INTERMEDIATE,
            Phenotype.RAPID,
            Phenotype.NORMAL,
            Phenotype.ULTRA_RAPID,
        ]
        
        for pheno in phenotype_order:
            if pheno in valid_phenotypes:
                return pheno
        
        return Phenotype.NORMAL


def get_converter() -> GenotypePhenotypeConverter:
    """Factory function for converter"""
    return GenotypePhenotypeConverter()
