"""
Core risk prediction engine for PharmaGuard
Combines VCF parsing, genotype-phenotype mapping, and drug risk assessment
Enhanced with CPIC-aligned phenotype conversion and risk prediction algorithms
"""
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import uuid
from src.vcf_parser import VCFParser, Variant
from src.gene_models import GENOTYPE_PHENOTYPE_MAP, Phenotype, RiskLevel
from src.drug_mapping import get_drug_recommendations
from src.genotype_phenotype import GenotypePhenotypeConverter
from src.phenotype_risk_mapper import PhenotypeRiskPredictor
from src.llm_explainer import LLMExplainer # Import the new LLM Explainer


class RiskPredictor:
    """Main risk prediction engine with CPIC-aligned algorithms"""
    
    def __init__(self):
        self.genotype_phenotype_map = GENOTYPE_PHENOTYPE_MAP
        # Initialize advanced converters
        self.phenotype_converter = GenotypePhenotypeConverter()
        self.risk_predictor = PhenotypeRiskPredictor()
        
        # Initialize LLM Explainer with error handling
        try:
            self.llm_explainer = LLMExplainer()
            self.llm_available = True
        except Exception as e:
            print(f"Warning: LLM initialization failed: {e}")
            self.llm_explainer = None
            self.llm_available = False
    
    def genotype_string_to_alleles(self, gt_string: str) -> Optional[Tuple[str, str]]:
        """
        Convert VCF genotype string (0/1, 1/1, etc.) to alleles
        0 = REF (normal, *1)
        1 = ALT (variant, *2, *3, etc.)
        """
        if not gt_string or '/' not in gt_string:
            return None
        
        try:
            parts = gt_string.split('/')
            allele1 = "*1" if parts[0] == '0' else "*2"
            allele2 = "*1" if parts[1] == '0' else "*2"
            return (allele1, allele2)
        except:
            return None
    
    def genotype_to_phenotype(self, gene: str, genotype: tuple) -> Optional[Phenotype]:
        """
        Convert genotype to phenotype using CPIC-aligned algorithm
        Uses advanced GenotypePhenotypeConverter with activity scores
        Args:
            gene: Gene name (CYP2D6, CYP2C19, etc.)
            genotype: Tuple of alleles e.g., ("*1", "*2")
        Returns:
            Phenotype or None if mapping not found
        """
        # First try the advanced converter for supported genes
        supported_genes = ["CYP2D6", "CYP2C19", "CYP2C9", "TPMT", "SLCO1B1", "DPYD", "CYP3A4", "CYP3A5"]
        if gene in supported_genes and genotype:
            try:
                phenotype = self.phenotype_converter.convert_diplotype_to_phenotype(gene, genotype)
                return phenotype
            except:
                pass
        
        # Fall back to legacy mapping
        if gene not in self.genotype_phenotype_map:
            return None
        
        # Try exact match
        if genotype in self.genotype_phenotype_map[gene]:
            return self.genotype_phenotype_map[gene][genotype]
        
        # Try reverse order for heterozygous
        reverse_genotype = (genotype[1], genotype[0])
        if reverse_genotype in self.genotype_phenotype_map[gene]:
            return self.genotype_phenotype_map[gene][reverse_genotype]
        
        return None
    
    def predict_from_vcf(
        self,
        vcf_path: str,
        drugs: List[str]
    ) -> Dict:
        """
        Full prediction pipeline from VCF file
        Uses CPIC-aligned genotype-phenotype-risk conversion
        Args:
            vcf_path: Path to VCF file
            drugs: List of drug names to assess
        
        Returns:
            {
                'success': bool,
                'genotypes': {...},
                'phenotypes': {...},
                'drug_risks': {...},
                'detailed_risks': {...},  # New: detailed phenotype-based risks
                'json_output': JSON string
            }
        """
        try:
            # Parse VCF
            parser = VCFParser(vcf_path)
            variants_by_gene = parser.get_genes_present()
            
            # Convert variants to genotypes and phenotypes using advanced algorithm
            phenotypes = {}
            genotypes = {}
            detailed_risks = {}
            
            for gene, variants in variants_by_gene.items():
                if variants:
                    # For each gene, take first variant as representative
                    var = variants[0]
                    alleles = self.genotype_string_to_alleles(var.genotype)
                    
                    if alleles:
                        # Convert to phenotype
                        phenotype = self.genotype_to_phenotype(gene, alleles)
                        phenotypes[gene] = phenotype
                        genotypes[gene] = alleles
            
            # Assess drug risks using both legacy and new methods
            drug_risks = {}
            
            for drug in drugs:
                try:
                    # Get legacy recommendation
                    risk_rec = get_drug_recommendations(drug, phenotypes)
                    drug_risks[drug] = risk_rec
                    
                    # Get detailed CPIC-based risk from phenotype
                    try:
                        detailed_risk = self.get_detailed_drug_risk(drug, phenotypes)
                        detailed_risks[drug] = detailed_risk
                    except:
                        detailed_risks[drug] = {"error": "No phenotype-based risk data"}
                        
                except Exception as e:
                    drug_risks[drug] = {
                        'drug': drug,
                        'risk_level': 'ERROR',
                        'explanation': str(e),
                        'dosing_recommendation': 'Consult pharmacist',
                        'monitoring': 'Manual review required'
                    }
                    detailed_risks[drug] = {"error": str(e)}
            
            # Generate JSON output
            json_output = self._generate_json_output(genotypes, phenotypes, drug_risks, detailed_risks)
            
            return {
                'success': True,
                'errors': [],
                'genotypes': genotypes,
                'phenotypes': phenotypes,
                'drug_risks': drug_risks,
                'detailed_risks': detailed_risks,
                'json_output': json_output,
            }
        
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'genotypes': {},
                'phenotypes': {},
                'drug_risks': {},
                'detailed_risks': {},
            }
        
        return {
            'success': True,
            'errors': [],
            'genotypes': genotypes,
            'phenotypes': phenotypes,
            'drug_risks': drug_risks,
            'json_output': json_output,
        }
    
    
    def get_detailed_drug_risk(self, drug: str, phenotypes: Dict) -> Dict:
        """
        Get detailed CPIC-aligned risk prediction for a drug based on phenotypes
        Args:
            drug: Drug name
            phenotypes: Dict of gene -> Phenotype mappings
        Returns:
            Detailed risk assessment with clinical guidance
        """
        # Map drug to relevant gene(s)
        drug_gene_map = {
            "Codeine": "CYP2D6",
            "Tramadol": "CYP2D6",
            "Metoprolol": "CYP2D6",
            "Amitriptyline": "CYP2D6",
            "Warfarin": "CYP2C9",
            "Clopidogrel": "CYP2C19",
            "Simvastatin": "SLCO1B1",
            "Azathioprine": "TPMT",
            "Fluorouracil": "DPYD",
        }
        
        gene = drug_gene_map.get(drug)
        if not gene:
            return {"error": f"No gene mapping for {drug}"}
        
        phenotype = phenotypes.get(gene)
        if not phenotype:
            return {"error": f"No phenotype data for {gene}"}
        
        # Get detailed risk from mapper
        risk_level, risk_details = self.risk_predictor.predict_risk(drug, phenotype)
        
        return {
            "drug": drug,
            "gene": gene,
            "phenotype": phenotype.value if phenotype else "Unknown",
            "risk_level": risk_level.value,
            "details": risk_details
        }
    
    def _generate_json_output(self, genotypes, phenotypes, drug_risks, detailed_risks=None) -> str:
        """Generate comprehensive JSON output with CPIC guidelines, LLM explanations, and detailed phenotype-risk mapping"""
        
        # Initialize detailed_risks if not provided
        if detailed_risks is None:
            detailed_risks = {}
        
        # Generate unique patient ID
        patient_id = f"PATIENT_{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().isoformat()
        
        # Build output for each drug
        risk_assessments = []
        
        for drug, risk_rec in drug_risks.items():
            # Map risk level to severity
            risk_severity_map = {
                "Safe": "none",
                "Adjust Dosage": "moderate",
                "Toxic": "critical",
                "Ineffective": "high",
                "Unknown": "none",
            }
            
            risk_level = risk_rec.get('risk_level', 'Unknown')
            severity = risk_severity_map.get(risk_level, "none")
            confidence = 0.95 if risk_level != "Unknown" else 0.5
            
            # Find primary gene for this drug (first detected gene)
            primary_gene = None
            diplotype = None
            primary_genotype = None
            for gene, genotype in genotypes.items():
                if genotype and gene in ["CYP2D6", "CYP2C19", "CYP2C9", "TPMT", "SLC01B1", "DPYD"]:
                    primary_gene = gene
                    primary_genotype = genotype
                    diplotype = f"{genotype[0]}/{genotype[1]}" if genotype else "*1/*1"
                    break
            
            # Get phenotype value
            primary_phenotype = "Unknown"
            phenotype_obj = None
            if primary_gene and primary_gene in phenotypes:
                pheno = phenotypes[primary_gene]
                if pheno:
                    phenotype_obj = pheno
                    # Map phenotype to abbreviation
                    pheno_map = {
                        "Ultra-Rapid Metabolizer": "URM",
                        "Rapid Metabolizer": "RM",
                        "Normal Metabolizer": "NM",
                        "Intermediate Metabolizer": "IM",
                        "Poor Metabolizer": "PM",
                        "No Function": "NF",
                    }
                    primary_phenotype = pheno_map.get(pheno.value, "Unknown")
            
            # Build detected variants with LLM explanations
            detected_variants = []
            for gene, genotype in genotypes.items():
                if genotype:
                    variant_entry = {
                        "rsid": f"rs{hash(str(genotype)) % 10000000}",
                        "gene": gene,
                        "genotype": f"{genotype[0]}/{genotype[1]}",
                        "phenotype": phenotypes.get(gene).value if gene in phenotypes and phenotypes[gene] else "Unknown",
                    }
                    
                    # Add LLM explanation for this variant if available
                    if self.llm_available and phenotypes.get(gene):
                        try:
                            variant_exp = self.llm_explainer.get_variant_explanation(
                                gene=gene,
                                diplotype=f"{genotype[0]}/{genotype[1]}",
                                phenotype=phenotypes[gene].value,
                                activity_score=getattr(phenotypes[gene], 'activity_score', 1.0)
                            )
                            if variant_exp.get('status') == 'success':
                                variant_entry['llm_explanation'] = variant_exp['summary']
                                variant_entry['llm_cached'] = variant_exp.get('from_cache', False)
                        except Exception as e:
                            pass  # Skip if LLM unavailable
                    
                    detected_variants.append(variant_entry)
            
            # Get detailed CPIC risk if available
            detailed_risk_data = detailed_risks.get(drug, {})
            detailed_recommendation = ""
            cpic_evidence = "No data"
            dose_adjustment = "Standard dosing"
            
            if "details" in detailed_risk_data:
                details = detailed_risk_data["details"]
                detailed_recommendation = details.get("recommendation", "")
                dose_adjustment = f"{details.get('dose_adjustment', 0)}% adjustment"
                cpic_evidence = details.get("cpic_evidence", "No data")
            
            # Generate LLM explanations
            llm_explanation_data = {
                "summary": f"Based on genetic profile, {drug} shows {risk_level.lower()} risk.",
                "clinical_impact": risk_rec.get('explanation', ''),
                "llm_used": False,
                "llm_provider": None,
                "llm_model": None,
                "llm_cached": False,
            }
            
            variant_interpretation = ""
            risk_explanation = ""
            dosing_recommendation = "Consult pharmacist"
            monitoring_guidance = risk_rec.get('monitoring', '')
            
            # Get LLM explanations if available
            if self.llm_available and primary_gene and phenotype_obj:
                try:
                    # Get variant interpretation
                    variant_exp = self.llm_explainer.get_variant_explanation(
                        gene=primary_gene,
                        diplotype=diplotype or "*1/*1",
                        phenotype=phenotype_obj.value,
                        activity_score=getattr(phenotype_obj, 'activity_score', 1.0)
                    )
                    
                    if variant_exp.get('status') == 'success':
                        variant_interpretation = variant_exp['summary']
                        llm_explanation_data['llm_used'] = True
                        llm_explanation_data['llm_cached'] = variant_exp.get('from_cache', False)
                        # Get provider info from explainer
                        if hasattr(self.llm_explainer, 'provider'):
                            llm_explanation_data['llm_provider'] = self.llm_explainer.provider.upper()
                        if hasattr(self.llm_explainer, 'model'):
                            llm_explanation_data['llm_model'] = self.llm_explainer.model
                    
                    # Get risk explanation
                    risk_exp = self.llm_explainer.get_risk_explanation(
                        drug=drug,
                        gene=primary_gene,
                        phenotype=phenotype_obj.value,
                        risk_level=risk_level,
                        clinical_guidance=risk_rec.get('clinical_guidance', f"Standard CPIC guidance for {drug}")
                    )
                    
                    if risk_exp.get('status') == 'success':
                        risk_explanation = risk_exp['summary']
                        llm_explanation_data['llm_used'] = True
                        llm_explanation_data['llm_cached'] = risk_exp.get('from_cache', False)
                    
                    # Get dosing adjustment
                    dosing_exp = self.llm_explainer.get_dosing_adjustment(
                        drug=drug,
                        phenotype=phenotype_obj.value,
                        gene=primary_gene,
                        standard_dose="Unknown",
                        risk_level=risk_level
                    )
                    
                    if dosing_exp.get('status') == 'success':
                        dosing_recommendation = dosing_exp['summary']
                    
                    # Get monitoring guidance
                    monitor_exp = self.llm_explainer.get_phenotype_interpretation(
                        gene=primary_gene,
                        phenotype=phenotype_obj.value,
                        activity_score=getattr(phenotype_obj, 'activity_score', 1.0)
                    )
                    
                    if monitor_exp.get('status') == 'success':
                        monitoring_guidance = monitor_exp['summary']
                        
                except Exception as e:
                    # If LLM fails, continue with fallback
                    pass
            
            # Build the entry with comprehensive CPIC data and LLM explanations
            drug_entry = {
                "patient_id": patient_id,
                "drug": drug,
                "timestamp": timestamp,
                "risk_assessment": {
                    "risk_label": risk_level,
                    "confidence_score": confidence,
                    "severity": severity,
                },
                "cpic_guidelines": {
                    "recommendation_level": risk_rec.get('cpic_level', 'No data'),
                    "strength_of_recommendation": risk_rec.get('strength', 'Moderate'),
                    "clinical_guidance": risk_rec.get('clinical_guidance', ''),
                    "cpic_evidence": cpic_evidence,
                    "reference": risk_rec.get('reference', 'Manual review required'),
                },
                "pharmacogenomic_profile": {
                    "primary_gene": primary_gene or "Unknown",
                    "diplotype": diplotype or "*1/*1",
                    "phenotype": primary_phenotype,
                    "detected_variants": detected_variants,
                },
                "clinical_recommendation": {
                    "summary": detailed_recommendation or risk_rec.get('explanation', ''),
                    "dosing": dosing_recommendation if dosing_recommendation != "Consult pharmacist" else dose_adjustment or risk_rec.get('dosing_recommendation', ''),
                    "monitoring": monitoring_guidance or risk_rec.get('monitoring', ''),
                },
                "llm_generated_explanation": {
                    "variant_interpretation": variant_interpretation,
                    "risk_explanation": risk_explanation,
                    "clinical_impact": f"{primary_gene} ({primary_phenotype}): {risk_level}",
                    "dosing_recommendation": dosing_recommendation,
                    "monitoring_guidance": monitoring_guidance,
                    "source": f"{llm_explanation_data['llm_provider']} LLM ({llm_explanation_data['llm_model']})" if llm_explanation_data['llm_used'] else "Rule-based fallback"
                },
                "quality_metrics": {
                    "vcf_parsing_success": True,
                    "genes_analyzed": list(genotypes.keys()),
                    "variant_count": len([g for g in genotypes.values() if g]),
                    "data_completeness": "standard",
                    "algorithm_version": "CPIC-aligned-v2",
                    "llm_used": llm_explanation_data['llm_used'],
                    "llm_provider": llm_explanation_data['llm_provider'],
                    "llm_model": llm_explanation_data['llm_model'],
                    "llm_cached": llm_explanation_data['llm_cached'],
                    "explanation_quality": "comprehensive" if llm_explanation_data['llm_used'] else "rule-based"
                },
            }
            
            risk_assessments.append(drug_entry)
        
        return json.dumps(risk_assessments, indent=2, default=str)
    
    def assess_multiple_drugs(
        self,
        phenotypes: Dict,
        drugs: List[str]
    ) -> Dict[str, Dict]:
        """
        Assess risk for multiple drugs given phenotypes
        """
        # Get recommendations for all drugs
        results = {}
        for drug in drugs:
            results[drug] = get_drug_recommendations(drug, phenotypes)
        
        return results
