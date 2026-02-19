"""
VCF (Variant Call Format) Parser - Manual implementation without external genomics libraries
Parses standard VCF v4.2 files for pharmacogenomic analysis
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Variant:
    """Represents a genetic variant from VCF"""
    chrom: str
    pos: int
    ref: str
    alt: str
    gene: str
    rs_id: Optional[str] = None
    genotype: str = "0/0"  # Default: homozygous reference
    quality: float = 0.0
    info: Dict[str, str] = None

    def __post_init__(self):
        if self.info is None:
            self.info = {}

    def __repr__(self):
        return f"Variant({self.gene}:{self.rs_id} {self.ref}→{self.alt} GT:{self.genotype})"


class VCFParser:
    """Parse VCF files for pharmacogenomic variants"""

    # Map chromosomes to critical genes
    GENE_CHROMOSOMES = {
        "CYP2D6": "22",
        "CYP2C19": "10",
        "CYP2C9": "10",
        "SLC01B1": "12",
        "TPMT": "6",
        "DPYD": "1",
    }

    # Common variant positions (simplified for demo - use CPIC reference in production)
    KNOWN_VARIANTS = {
        "CYP2D6": {
            "rs1065852": ("22", 42126499),
            "rs5030655": ("22", 42130692),
            "rs5030867": ("22", 42131889),
        },
        "CYP2C19": {
            "rs4244285": ("10", 96541616),
            "rs4986893": ("10", 96541857),
            "rs12248560": ("10", 96545410),
        },
        "CYP2C9": {
            "rs1799853": ("10", 94938996),
            "rs1057910": ("10", 94942758),
        },
        "SLC01B1": {
            "rs4149056": ("12", 21370535),
        },
        "TPMT": {
            "rs1142345": ("6", 18130722),
            "rs1800460": ("6", 18131875),
            "rs1800462": ("6", 18140475),
        },
        "DPYD": {
            "rs3918290": ("1", 97915614),
            "rs55886062": ("1", 98348885),
            "rs67376798": ("1", 98403947),
        },
    }

    def __init__(self, filepath: str):
        """Initialize parser with VCF file path"""
        self.filepath = filepath
        self.header = {}
        self.variants: List[Variant] = []
        self._parse()

    def _parse(self):
        """Parse VCF file"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Parse header lines
                if line.startswith('##'):
                    self._parse_header_line(line)
                    continue

                # Parse column header
                if line.startswith('#CHROM'):
                    self.header['columns'] = line[1:].split('\t')
                    continue

                # Parse variant lines
                if not line.startswith('#'):
                    variant = self._parse_variant_line(line)
                    if variant:
                        self.variants.append(variant)

        except FileNotFoundError:
            print(f"Error: File {self.filepath} not found")
            self.variants = []

    def _parse_header_line(self, line: str):
        """Parse VCF header metadata"""
        if '=' in line:
            key, value = line[2:].split('=', 1)
            if key not in self.header:
                self.header[key] = []
            self.header[key].append(value)

    def _parse_variant_line(self, line: str) -> Optional[Variant]:
        """Parse a single variant line"""
        fields = line.split('\t')

        if len(fields) < 10:
            return None

        chrom, pos, rs_id, ref, alt, qual, filt, info, fmt, sample = fields[:10]

        # Extract gene from annotation (simplified)
        gene = self._extract_gene(chrom, int(pos), rs_id)

        if not gene:
            return None

        # Parse INFO field
        info_dict = self._parse_info_field(info)

        # Parse genotype from sample column
        genotype = self._parse_genotype(fmt, sample)

        try:
            variant = Variant(
                chrom=chrom,
                pos=int(pos),
                ref=ref,
                alt=alt,
                gene=gene,
                rs_id=rs_id if rs_id != '.' else None,
                genotype=genotype,
                quality=float(qual) if qual != '.' else 0.0,
                info=info_dict
            )
            return variant
        except (ValueError, IndexError):
            return None

    def _parse_info_field(self, info_str: str) -> Dict[str, str]:
        """Parse INFO field into key-value pairs"""
        info_dict = {}
        if info_str == '.':
            return info_dict

        for item in info_str.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                info_dict[key] = value
            else:
                info_dict[item] = True

        return info_dict

    def _parse_genotype(self, fmt_str: str, sample_str: str) -> str:
        """Extract genotype from FORMAT and sample columns"""
        if ':' not in fmt_str or ':' not in sample_str:
            return "0/0"

        format_fields = fmt_str.split(':')
        sample_fields = sample_str.split(':')

        if len(format_fields) > 0 and len(sample_fields) > 0:
            if format_fields[0] == 'GT':
                return sample_fields[0]

        return "0/0"

    def _extract_gene(self, chrom: str, pos: int, rs_id: str) -> Optional[str]:
        """Determine gene from chromosome and position"""
        # First check if RS ID matches known variants
        if rs_id != '.':
            for gene, variants in self.KNOWN_VARIANTS.items():
                if rs_id in variants:
                    return gene

        # Fallback: match by chromosome
        for gene, gene_chrom in self.GENE_CHROMOSOMES.items():
            if chrom == gene_chrom or chrom == f"chr{gene_chrom}":
                return gene

        return None

    def get_variants(self, gene: Optional[str] = None) -> List[Variant]:
        """Get variants, optionally filtered by gene"""
        if gene:
            return [v for v in self.variants if v.gene == gene]
        return self.variants

    def get_genes_present(self) -> Dict[str, List[Variant]]:
        """Return variants grouped by gene"""
        genes_dict = {}
        for variant in self.variants:
            if variant.gene not in genes_dict:
                genes_dict[variant.gene] = []
            genes_dict[variant.gene].append(variant)
        return genes_dict

    def summary(self) -> Dict:
        """Get summary statistics"""
        genes = self.get_genes_present()
        return {
            "total_variants": len(self.variants),
            "genes_found": list(genes.keys()),
            "variants_per_gene": {gene: len(vars) for gene, vars in genes.items()}
        }


def validate_vcf(filepath: str) -> Tuple[bool, str]:
    """Quick validation that file is VCF format"""
    try:
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('##fileformat=VCFv'):
                return False, "Invalid VCF header"
            return True, "Valid VCF"
    except FileNotFoundError:
        return False, "File not found"
    except Exception as e:
        return False, str(e)
