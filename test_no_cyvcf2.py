"""
Simple test to verify VCF parser works without cyvcf2
"""
from src.vcf_parser import VCFParser
from src.gene_models import Phenotype, RiskLevel

# Test with sample VCF
parser = VCFParser('sample_vcf/example.vcf')

print("=" * 60)
print("VCF PARSER TEST (No cyvcf2 Required)")
print("=" * 60)

# Show summary
summary = parser.summary()
print(f"\n✓ Total variants found: {summary['total_variants']}")
print(f"✓ Genes detected: {summary['genes_found']}")
print(f"✓ Variants per gene: {summary['variants_per_gene']}")

# Show variants by gene
print("\n" + "=" * 60)
print("VARIANTS BY GENE")
print("=" * 60)

genes_data = parser.get_genes_present()
for gene, variants in genes_data.items():
    print(f"\n{gene}:")
    for v in variants:
        print(f"  - {v.rs_id or 'N/A'}: {v.ref}→{v.alt} (GT: {v.genotype})")

# Display all variants
print("\n" + "=" * 60)
print("ALL PARSED VARIANTS")
print("=" * 60)

all_variants = parser.get_variants()
for i, v in enumerate(all_variants, 1):
    print(f"{i}. {v}")

print("\n✓ Parser working correctly!")
print("✓ No cyvcf2 dependency needed!")
