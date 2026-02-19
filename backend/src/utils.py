"""
Utility functions for PharmaGuard
"""
import os
import json
from typing import List, Optional
import streamlit as st


SUPPORTED_DRUGS = [
    "Codeine",
    "Warfarin",
    "Clopidogrel",
    "Simvastatin",
    "Azathioprine",
    "Fluorouracil",
    "Metoprolol",
    "Amitriptyline",
]

CRITICAL_GENES = [
    "CYP2D6",
    "CYP2C19",
    "CYP2C9",
    "SLC01B1",
    "TPMT",
    "DPYD",
]


def validate_vcf_filename(filename: str) -> bool:
    """Check if filename is valid VCF"""
    return filename.endswith('.vcf') or filename.endswith('.vcf.gz')


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


def is_valid_file_size(file_path: str, max_size_mb: int = 5) -> bool:
    """Check if file is within size limit"""
    return get_file_size_mb(file_path) <= max_size_mb


def format_risk_color(risk_level: str) -> str:
    """Return color code for risk level"""
    color_map = {
        "Safe": "🟢",
        "Adjust Dosage": "🟡",
        "Toxic": "🔴",
        "Ineffective": "🟠",
        "Unknown": "⚪",
    }
    return color_map.get(risk_level, "⚪")


def save_json_output(data: dict, output_path: str) -> bool:
    """Save prediction results to JSON"""
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving JSON: {str(e)}")
        return False


def load_sample_vcf_info() -> List[dict]:
    """Get information about sample VCF files"""
    return [
        {
            "name": "Example VCF",
            "description": "Sample VCF with CYP2D6 and CYP2C19 variants",
            "path": "sample_vcf/example.vcf",
        }
    ]


def create_risk_explanation(risk_level: str, gene: str, phenotype: str) -> str:
    """Create clinical explanation for risk level"""
    explanations = {
        "Safe": f"No special precautions needed based on {gene} ({phenotype})",
        "Adjust Dosage": f"Dose adjustment recommended based on {gene} {phenotype} status",
        "Toxic": f"Drug may cause toxicity in {gene} {phenotype} patients; consider alternatives",
        "Ineffective": f"Drug may be ineffective in {gene} {phenotype} patients; consider alternatives",
    }
    return explanations.get(risk_level, "Consult with pharmacist")


def format_json_for_display(json_str: str) -> str:
    """Format JSON string for pretty display"""
    try:
        data = json.loads(json_str)
        return json.dumps(data, indent=2)
    except:
        return json_str


def validate_drug_input(drug_input: str) -> List[str]:
    """
    Parse drug input (comma-separated or multi-select)
    Returns list of valid drug names
    """
    if isinstance(drug_input, list):
        return drug_input
    
    # Split by comma and clean
    drugs = [d.strip() for d in drug_input.split(',')]
    return [d for d in drugs if d]
