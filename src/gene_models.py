"""
Gene and variant data models for pharmacogenomics
"""
from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass


class Phenotype(Enum):
    """Metabolizer phenotype classifications"""
    ULTRA_RAPID = "Ultra-Rapid Metabolizer"
    RAPID = "Rapid Metabolizer"
    NORMAL = "Normal Metabolizer"
    INTERMEDIATE = "Intermediate Metabolizer"
    POOR = "Poor Metabolizer"
    NO_FUNCTION = "No Function"


class RiskLevel(Enum):
    """Drug risk classification"""
    SAFE = "Safe"
    ADJUST_DOSAGE = "Adjust Dosage"
    TOXIC = "Toxic"
    INEFFECTIVE = "Ineffective"
    UNKNOWN = "Unknown"


@dataclass
class Variant:
    """Represents a genetic variant"""
    chrom: str
    pos: int
    ref: str
    alt: str
    rsid: str = None
    
    def __str__(self):
        return f"{self.chrom}:{self.pos} {self.ref}>{self.alt}"


@dataclass
class Gene:
    """Represents a pharmacogene"""
    name: str
    chromosome: str
    start_pos: int
    end_pos: int
    variants: Dict[str, List[str]] = None  # {rsid: [alleles]}
    
    def __post_init__(self):
        if self.variants is None:
            self.variants = {}


# Define the 6 critical genes
CRITICAL_GENES = {
    "CYP2D6": Gene(
        name="CYP2D6",
        chromosome="22",
        start_pos=41497879,
        end_pos=41506955,
        variants={
            "rs1065852": ["G", "A"],  # *2 allele
            "rs3892097": ["A", "G"],  # *9 allele
            "rs5030655": ["C", "T"],  # *5 allele
            "rs1058164": ["A", "G"],  # *41 allele
        }
    ),
    "CYP2C19": Gene(
        name="CYP2C19",
        chromosome="10",
        start_pos=96522463,
        end_pos=96541932,
        variants={
            "rs4244285": ["G", "A"],  # *2 allele
            "rs4986893": ["A", "G"],  # *3 allele
            "rs28399504": ["C", "T"],  # *4 allele
        }
    ),
    "CYP2C9": Gene(
        name="CYP2C9",
        chromosome="10",
        start_pos=94942207,
        end_pos=94988321,
        variants={
            "rs1799853": ["C", "T"],  # *2 allele
            "rs1057910": ["A", "C"],  # *3 allele
        }
    ),
    "SLC01B1": Gene(
        name="SLC01B1",
        chromosome="12",
        start_pos=21370500,
        end_pos=21375000,
        variants={
            "rs4149056": ["C", "T"],  # c.521T>C
        }
    ),
    "TPMT": Gene(
        name="TPMT",
        chromosome="6",
        start_pos=18130920,
        end_pos=18143550,
        variants={
            "rs1142345": ["C", "T"],  # G238C (*2)
            "rs1800460": ["A", "G"],  # A460G (*3A)
            "rs1800462": ["G", "A"],  # G719A (*3B, *3C)
        }
    ),
    "DPYD": Gene(
        name="DPYD",
        chromosome="1",
        start_pos=97714245,
        end_pos=97760548,
        variants={
            "rs3918290": ["G", "A"],  # IVS14+1G>A (*2A)
            "rs55886062": ["T", "C"],  # D949V (*13)
            "rs67376798": ["A", "G"],  # 2846A>G (*4)
        }
    ),
}


@dataclass
class GenotypePhenotype:
    """Maps genotypes to phenotypes"""
    gene: str
    phenotype: Phenotype
    allele_combinations: List[str]


# Simplified genotype-phenotype mappings (CPIC guidelines)
GENOTYPE_PHENOTYPE_MAP = {
    "CYP2D6": {
        ("*1", "*1"): Phenotype.NORMAL,
        ("*1", "*2"): Phenotype.NORMAL,
        ("*1", "*40"): Phenotype.INTERMEDIATE,
        ("*1", "*5"): Phenotype.INTERMEDIATE,
        ("*1", "*41"): Phenotype.INTERMEDIATE,
        ("*2", "*2"): Phenotype.NORMAL,
        ("*4", "*4"): Phenotype.POOR,
        ("*5", "*5"): Phenotype.POOR,
        ("*1", "*4"): Phenotype.INTERMEDIATE,
    },
    "CYP2C19": {
        ("*1", "*1"): Phenotype.NORMAL,
        ("*1", "*2"): Phenotype.INTERMEDIATE,
        ("*1", "*3"): Phenotype.INTERMEDIATE,
        ("*2", "*2"): Phenotype.POOR,
        ("*2", "*3"): Phenotype.POOR,
        ("*3", "*3"): Phenotype.POOR,
    },
    "CYP2C9": {
        ("*1", "*1"): Phenotype.NORMAL,
        ("*1", "*2"): Phenotype.INTERMEDIATE,
        ("*1", "*3"): Phenotype.INTERMEDIATE,
        ("*2", "*2"): Phenotype.INTERMEDIATE,
        ("*2", "*3"): Phenotype.POOR,
        ("*3", "*3"): Phenotype.POOR,
    },
    "TPMT": {
        ("*1", "*1"): Phenotype.NORMAL,
        ("*1", "*2"): Phenotype.INTERMEDIATE,
        ("*1", "*3A"): Phenotype.INTERMEDIATE,
        ("*2", "*2"): Phenotype.POOR,
        ("*2", "*3A"): Phenotype.POOR,
        ("*3A", "*3A"): Phenotype.POOR,
    },
    # SLC01B1 and DPYD are not metabolizer genes, will have custom mapping
}


CRITICAL_GENE_NAMES: Set[str] = set(CRITICAL_GENES.keys())
