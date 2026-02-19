"""
Phenotype-to-Risk Prediction Engine
Maps metabolizer phenotypes to drug-specific risks (Safe/Adjust/Toxic/Ineffective)
Implements CPIC-aligned clinical decision rules
"""

from typing import Dict, Tuple, Optional
from src.gene_models import Phenotype, RiskLevel


class PhenotypeRiskPredictor:
    """
    Maps phenotypes to drug risks
    Implements evidence-based CPIC clinical interpretation
    """
    
    # CPIC PHENOTYPE-RISK MAPPINGS FOR EACH DRUG
    PHENOTYPE_RISK_RULES = {
        # ============================================================
        # CODEINE - CYP2D6 (opioid analgesic)
        # ============================================================
        "Codeine": {
            Phenotype.ULTRA_RAPID: {
                "risk": RiskLevel.TOXIC,
                "reason": "Ultra-rapid CYP2D6 metabolizers produce excessively high morphine levels from codeine, resulting in overdose risk and potentially life-threatening side effects including respiratory depression and death",
                "recommendation": "NOT RECOMMENDED - Use alternative analgesic (e.g., morphine, hydrocodone, tramadol, acetaminophen)",
                "dose_adjustment": "0% - Do not use",
                "monitoring": "If must use despite recommendation: Monitor closely for respiratory depression, oversedation, pinpoint pupils, and toxicity",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.RAPID: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Rapid CYP2D6 metabolizers convert codeine to morphine faster than normal individuals, achieving therapeutic effect quickly but risking side effects",
                "recommendation": "Use with caution; may achieve pain relief at standard doses but monitor closely for effects",
                "dose_adjustment": "Consider standard dose initially, ready to adjust down",
                "monitoring": "Monitor for increased side effects (dizziness, nausea, constipation, drowsiness). Watch for signs of excessive morphine production",
                "cpic_evidence": "2A - Moderate"
            },
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal CYP2D6 metabolizers convert codeine to morphine at typical rates, producing therapeutic analgesic effect with expected side effect profile",
                "recommendation": "Use normal recommended dose (15-60 mg every 4-6 hours as needed for pain)",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "Standard opioid monitoring for pain control and side effects",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.INTERMEDIATE: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Intermediate CYP2D6 metabolizers have reduced morphine formation (~10-20% reduction), potentially reducing analgesic effectiveness",
                "recommendation": "Consider higher than normal dose or shorter dosing intervals; monitor pain response",
                "dose_adjustment": "120-150% of standard dose may be needed",
                "monitoring": "Assess pain control; titrate dose based on response (may need 30-60 mg per dose)",
                "cpic_evidence": "2A - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.INEFFECTIVE,
                "reason": "Poor CYP2D6 metabolizers produce little to no morphine from codeine (5-10% conversion at best), making codeine ineffective for pain relief",
                "recommendation": "NOT RECOMMENDED for pain control - Use alternative analgesic (morphine, oxycodone, hydromorphone, tramadol, or non-opioid options)",
                "dose_adjustment": "0% - Do not use",
                "monitoring": "If used despite recommendation: Monitor for complete lack of pain relief",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.NO_FUNCTION: {
                "risk": RiskLevel.INEFFECTIVE,
                "reason": "Complete loss of CYP2D6 function prevents morphine formation - codeine is completely ineffective as a prodrug",
                "recommendation": "NOT RECOMMENDED - Use direct-acting opioid or alternative analgesic",
                "dose_adjustment": "Not applicable",
                "monitoring": "Not applicable",
                "cpic_evidence": "1A - Strong"
            }
        },
        
        # ============================================================
        # WARFARIN - CYP2C9 (anticoagulant)
        # ============================================================
        "Warfarin": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal CYP2C9 metabolizers metabolize warfarin at typical rates, allowing standard dosing with INR titration",
                "recommendation": "Use standard initiation: 5-10 mg daily; adjust based on INR response",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "INR monitoring: baseline, 2-7 days after initiation, weekly x 1-2 weeks, then every 1-4 weeks",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.INTERMEDIATE: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Intermediate CYP2C9 metabolizers have reduced warfarin clearance, leading to increased drug exposure and bleeding risk",
                "recommendation": "Consider 25-50% dose reduction; initiate with 2.5-5 mg daily",
                "dose_adjustment": "50-75% of standard dose",
                "monitoring": "More frequent INR monitoring (2-3x weekly initially until stable); target INR reached more slowly",
                "cpic_evidence": "2A - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Poor CYP2C9 metabolizers have significantly impaired warfarin clearance, dramatically increasing anticoagulation effect and bleeding risk",
                "recommendation": "Avoid or use with extreme caution - 40-60% dose reduction; start 0.5-2 mg daily",
                "dose_adjustment": "40-60% dose reduction required",
                "monitoring": "Very frequent INR monitoring (daily to every other day) until stable; watch closely for signs of bleeding (hematuria, epistaxis, petechiae)",
                "cpic_evidence": "1A - Strong"
            }
        },
        
        # ============================================================
        # CLOPIDOGREL - CYP2C19 (antiplatelet - PRODRUG)
        # ============================================================
        "Clopidogrel": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal CYP2C19 metabolizers activate clopidogrel to active metabolite at normal rates, producing therapeutic antiplatelet effect",
                "recommendation": "Use standard dosing: Loading 300-600 mg, maintenance 75 mg daily",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "Monitor for bleeding; standard cardiovascular follow-up",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.INTERMEDIATE: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Intermediate CYP2C19 metabolizers have reduced activation of clopidogrel, producing lower active metabolite and reduced antiplatelet effect",
                "recommendation": "Consider alternative P2Y12 inhibitor (prasugrel 5-10 mg daily or ticagrelor 60-90 mg daily) OR increase clopidogrel to 150 mg daily",
                "dose_adjustment": "200% increase (150 mg) if continuing clopidogrel",
                "monitoring": "Assess antiplatelet response; platelet function testing helpful; higher stent thrombosis risk",
                "cpic_evidence": "2B - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.INEFFECTIVE,
                "reason": "Poor CYP2C19 metabolizers have minimal activation of clopidogrel (5-15% normal active metabolite production), resulting in minimal/no antiplatelet effect and high stent thrombosis risk",
                "recommendation": "NOT RECOMMENDED - Use alternative P2Y12 inhibitor: Prasugrel (5-10 mg daily) or Ticagrelor (60-90 mg daily). These don't require CYP2C19 activation",
                "dose_adjustment": "0% - Avoid clopidogrel",
                "monitoring": "If unable to switch: Intensive antiplatelet monitoring; dual high-dose clopidogrel therapy not recommended due to high thrombotic events",
                "cpic_evidence": "1A - Strong"
            }
        },
        
        # ============================================================
        # SIMVASTATIN - SLCO1B1 (statin - transporter)
        # ============================================================
        "Simvastatin": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal SLCO1B1 transporters efficiently move simvastatin into hepatocytes for metabolism; standard dosing produces therapeutic LDL reduction",
                "recommendation": "Use standard dosing: 10-40 mg daily (max 80 mg in non-asian populations)",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "Monitor lipid levels at 4-12 weeks, then annually; assess for muscle symptoms (myalgia)",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.INTERMEDIATE: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Intermediate SLCO1B1 function reduces hepatic uptake of simvastatin, increasing plasma levels and myopathy risk",
                "recommendation": "Consider dose reduction or switch to pravastatin/rosuvastatin; if continuing: max 20 mg daily",
                "dose_adjustment": "50% reduction maximum (20 mg)",
                "monitoring": "Baseline CK level; assess for muscle pain/weakness monthly; repeat CK if symptomatic",
                "cpic_evidence": "2A - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Poor SLCO1B1 function significantly impairs simvastatin hepatic uptake, dramatically increasing plasma levels and severe myopathy risk",
                "recommendation": "Avoid simvastatin or use minimally (5-10 mg max). Consider alternatives: pravastatin, rosuvastatin (not SLCO1B1-dependent)",
                "dose_adjustment": "75-90% reduction or avoid",
                "monitoring": "If used: Baseline CK, monthly monitoring x 3 months, then quarterly. Watch closely for muscle symptoms",
                "cpic_evidence": "1A - Strong"
            }
        },
        
        # ============================================================
        # AZATHIOPRINE - TPMT (immunosuppressant)
        # ============================================================
        "Azathioprine": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal TPMT activity allows standard azathioprine dosing with therapeutic benefit for autoimmune/inflammatory conditions",
                "recommendation": "Use standard dose: 1-2.5 mg/kg/day in divided doses",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "CBC with differential weekly x 8-12 weeks, then monthly. Watch for myelosuppression, infections, bleeding",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.INTERMEDIATE: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Intermediate TPMT activity causes accumulation of toxic 6-thioguanine nucleotides, increasing myelosuppression and infection risk",
                "recommendation": "Reduce dose 25-50% of normal; start low and titrate carefully based on response",
                "dose_adjustment": "50% reduction recommended",
                "monitoring": "CBC weekly x 4-6 weeks, then every 2 weeks. Watch closely for infections, severe anemia, platelet drops",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.TOXIC,
                "reason": "Very poor TPMT activity leads to excessive 6-thioguanine accumulation causing severe bone marrow toxicity, life-threatening infections, and potentially fatal complications",
                "recommendation": "Strongly consider avoiding or use at 10% of normal dose if no alternatives exist",
                "dose_adjustment": "90% reduction or avoid entirely",
                "monitoring": "If absolutely necessary: Daily CBC monitoring. Consider G-CSF (filgrastim) support. High-dose folinic acid rescue",
                "cpic_evidence": "1A - Strong"
            }
        },
        
        # ============================================================
        # FLUOROURACIL - DPYD (chemotherapy)
        # ============================================================
        "Fluorouracil": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal DPYD function metabolizes 5-FU efficiently; standard chemotherapy dosing produces expected efficacy with manageable toxicity",
                "recommendation": "Use standard chemotherapy protocol dosing (typically 400-500 mg/m² IV bolus or continuous)",
                "dose_adjustment": "100% - Standard dosing per protocol",
                "monitoring": "Standard oncology monitoring: CBC weekly, blood cultures if febrile, assess for mucositis/diarrhea",
                "cpic_evidence": "1A - Strong"
            },
            Phenotype.INTERMEDIATE: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Intermediate DPYD deficiency (heterozygous) increases 5-FU toxicity risk; drug accumulation leads to severe mucositis, myelosuppression, diarrhea",
                "recommendation": "Reduce dose 25-50%; start at 50-75% of standard dose",
                "dose_adjustment": "50-75% initial dose; escalate cautiously if well tolerated",
                "monitoring": "Close toxicity monitoring: mucositis grade, diarrhea (stool frequency), CBC weekly (severe drops possible)",
                "cpic_evidence": "2A - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.TOXIC,
                "reason": "DPYD deficiency (homozygous/compound heterozygous) prevents 5-FU metabolism, causing life-threatening toxicity: severe mucositis, cardiotoxicity, sepsis, potentially fatal outcomes",
                "recommendation": "NOT RECOMMENDED for standard 5-FU therapy - Consider alternative chemotherapy regimens (e.g., capecitabine at reduced dose, or non-fluoropyrimidine agents)",
                "dose_adjustment": "0% - Avoid 5-FU or use at 25-50% with intensive monitoring",
                "monitoring": "If unavoidable: Daily hospital monitoring; ICU backup. Intensive supportive care (TPN, antibiotics, blood products)",
                "cpic_evidence": "1A - Strong - MANDATORY testing recommended"
            }
        },
        
        # ============================================================
        # METOPROLOL - CYP2D6 (beta-blocker)
        # ============================================================
        "Metoprolol": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal CYP2D6 metabolizers metabolize metoprolol effectively; standard dosing achieves therapeutic effect",
                "recommendation": "Use standard dosing: 25-190 mg daily in divided doses",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "Monitor heart rate, blood pressure, exercise tolerance",
                "cpic_evidence": "2B - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Poor CYP2D6 metabolizers have reduced metoprolol clearance, leading to drug accumulation and increased side effects (bradycardia, fatigue, hypotension)",
                "recommendation": "Reduce dose 25-50%; consider alternative beta-blocker not metabolized by CYP2D6 (atenolol, bisoprolol, carvedilol)",
                "dose_adjustment": "50-75% reduction",
                "monitoring": "Monitor for bradycardia (< 50 bpm), hypotension, fatigue, dizziness",
                "cpic_evidence": "2B - Moderate"
            }
        },
        
        # ============================================================
        # AMITRIPTYLINE - CYP2D6/CYP2C19 (tricyclic antidepressant)
        # ============================================================
        "Amitriptyline": {
            Phenotype.NORMAL: {
                "risk": RiskLevel.SAFE,
                "reason": "Normal CYP2D6/CYP2C19 metabolizers metabolize amitriptyline at typical rates; standard dosing effective",
                "recommendation": "Use standard initiation: 25-50 mg at bedtime; titrate to 75-150 mg daily maintenance",
                "dose_adjustment": "100% - Standard dosing",
                "monitoring": "Monitor for anticholinergic effects (dry mouth, constipation, urinary retention), cardiac effects",
                "cpic_evidence": "2B - Moderate"
            },
            Phenotype.POOR: {
                "risk": RiskLevel.ADJUST_DOSAGE,
                "reason": "Poor CYP2D6/CYP2C19 metabolizers accumulate amitriptyline, increasing anticholinergic and cardiac toxicity risk",
                "recommendation": "Start low: 10-25 mg at bedtime; titrate slowly with close monitoring",
                "dose_adjustment": "50-75% reduction; slow titration critical",
                "monitoring": "Watch for anticholinergic side effects, orthostatic hypotension, arrhythmias, QT prolongation",
                "cpic_evidence": "2B - Moderate"
            }
        }
    }
    
    def __init__(self):
        self.rules = self.PHENOTYPE_RISK_RULES
    
    def predict_risk(
        self,
        drug: str,
        phenotype: Phenotype
    ) -> Tuple[RiskLevel, Dict]:
        """
        Predict risk for drug-phenotype combination
        
        Returns:
            (RiskLevel, dict with full details)
        """
        if drug not in self.rules:
            return RiskLevel.UNKNOWN, {
                "risk": RiskLevel.UNKNOWN,
                "reason": f"No pharmacogenomic data available for {drug}",
                "recommendation": "Consult with clinical pharmacist or pharmacogenomic specialist",
                "dose_adjustment": "Unknown",
                "monitoring": "Standard monitoring",
                "cpic_evidence": "No data"
            }
        
        drug_rules = self.rules[drug]
        
        if phenotype not in drug_rules:
            return RiskLevel.UNKNOWN, {
                "risk": RiskLevel.UNKNOWN,
                "reason": f"No mapping for {phenotype.value} on {drug}",
                "recommendation": "Consult with clinical pharmacist",
                "dose_adjustment": "Unknown",
                "monitoring": "Standard monitoring",
                "cpic_evidence": "No data"
            }
        
        rule = drug_rules[phenotype]
        return rule["risk"], rule
    
    def get_all_risks_for_drug(self, drug: str) -> Dict[Phenotype, Tuple[RiskLevel, Dict]]:
        """Get all phenotype-risk mappings for a drug"""
        if drug not in self.rules:
            return {}
        
        results = {}
        for phenotype, rule in self.rules[drug].items():
            results[phenotype] = (rule["risk"], rule)
        return results
    
    def get_risk_summary(self, drug: str, phenotype: Phenotype) -> str:
        """Get concise risk summary"""
        risk, details = self.predict_risk(drug, phenotype)
        
        if risk == RiskLevel.SAFE:
            return f"✅ {drug} is SAFE for {phenotype.value} metabolizers"
        elif risk == RiskLevel.ADJUST_DOSAGE:
            return f"⚠️ {drug} requires DOSE ADJUSTMENT for {phenotype.value} metabolizers"
        elif risk == RiskLevel.TOXIC:
            return f"🔴 HIGH RISK: {drug} is TOXIC for {phenotype.value} metabolizers"
        elif risk == RiskLevel.INEFFECTIVE:
            return f"🟠 HIGH RISK: {drug} is INEFFECTIVE for {phenotype.value} metabolizers"
        else:
            return f"⚪ {drug}: Unknown risk for {phenotype.value}"


def get_predictor() -> PhenotypeRiskPredictor:
    """Factory function"""
    return PhenotypeRiskPredictor()
