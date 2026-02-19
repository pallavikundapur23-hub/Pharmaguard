"""
Main Streamlit Application for PharmaGuard
Pharmacogenomic Risk Prediction System
"""
import streamlit as st
import json
import io
from datetime import datetime
import base64
import uuid
from src.risk_predictor import RiskPredictor
from src.utils import (
    SUPPORTED_DRUGS,
    CRITICAL_GENES,
    format_risk_color,
    validate_drug_input,
)
from src.gene_models import Phenotype



# Page configuration
st.set_page_config(
    page_title="PharmaGuard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .safe { color: #00AA00; font-weight: bold; }
    .adjust { color: #FFA500; font-weight: bold; }
    .toxic { color: #DD0000; font-weight: bold; }
    .ineffective { color: #FF6600; font-weight: bold; }
    .unknown { color: #999999; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit app"""
    
    # Header
    st.title("💊 PharmaGuard")
    st.subheader("Pharmacogenomic Risk Prediction System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/250x80?text=PharmaGuard", width=250)
        st.markdown("### 📋 Quick Info")
        st.info("""
        **Analyzes:**
        - CYP2D6, CYP2C19, CYP2C9
        - SLC01B1, TPMT, DPYD
        
        **Supports 6 Drugs**
        """)
        
        st.markdown("---")
        st.markdown("### 🔗 Resources")
        st.markdown("[CPIC Guidelines](https://cpicpgx.org)")
    
    # Main content tabs
    tab1, tab3, tab4 = st.tabs(["📤 Upload & Analyze",  "📚 About", "🧪 Test"])
    
    # Tab 1: Upload & Analyze
    with tab1:
        st.markdown("### Step 1: Upload VCF File")
        uploaded_file = st.file_uploader(
            "Select VCF file (max 5MB)",
            type=["vcf"],
            help="Variant Call Format file with genomic data"
        )
        
        st.markdown("### Step 2: Select Drugs to Assess")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Option A: Preset Drugs**")
            use_preset = st.checkbox("Use predefined drugs", value=False)
        
        with col2:
            st.markdown("**Option B: Enter Any Drug(s)**")
            drug_input = st.text_input(
                "Enter drug name(s):",
                placeholder="e.g., Codeine, Warfarin, Aspirin, or any other drug",
                help="Type one drug or multiple drugs separated by commas"
            )
        
        # Process drug input
        if use_preset:
            selected_drugs = st.multiselect(
                "Select from preset:",
                SUPPORTED_DRUGS,
                default=["Codeine", "Warfarin"]
            )
        else:
            selected_drugs = validate_drug_input(drug_input) if drug_input else []
        
        # Show what will be analyzed
        if selected_drugs:
            st.info(f"📋 Will analyze: **{', '.join(selected_drugs)}**")
        
        st.markdown("---")
        
        # Analyze button
        col1, col2 = st.columns(2)
        with col1:
            analyze_button = st.button("🔍 Analyze VCF", type="primary", use_container_width=True)
        
        with col2:
            if st.button("📥 Load Sample VCF & Codeine", use_container_width=True):
                try:
                    with open("sample_vcf/example.vcf", "rb") as f:
                        sample_file = io.BytesIO(f.read())
                        sample_file.name = "example.vcf"
                    analyze_vcf(sample_file, ["Codeine"])
                except Exception as e:
                    st.error(f"Error loading sample: {str(e)}")
        
        if analyze_button:
            if not uploaded_file:
                st.error("❌ Please upload a VCF file")
            elif not selected_drugs:
                st.error("❌ Please enter at least one drug name")
            else:
                analyze_vcf(uploaded_file, selected_drugs)
    
   
    
    # Tab 3: About (renumbered from tab2)
    with tab3:
        st.markdown("### About PharmaGuard")
        st.markdown("""
        **PharmaGuard** is an AI-powered system that analyzes patient genetic data 
        to predict pharmacogenomic risks and provide personalized drug recommendations.
        
        #### How It Works
        1. **Parse VCF**: Extracts genomic variants from patient data
        2. **Map Genes**: Identifies variants in 6 critical pharmacogenes
        3. **Predict Phenotype**: Converts genotypes to metabolizer phenotypes
        4. **Assess Risk**: Determines drug safety based on genetic profile
        5. **Recommend**: Provides CPIC-aligned dosing guidance
        
        #### Genes Analyzed
        """)
        for gene in CRITICAL_GENES:
            st.markdown(f"- **{gene}**: Metabolizer of multiple drugs")
        
        st.markdown("""
        #### Risk Levels
        - 🟢 **Safe**: Normal dosing recommended
        - 🟡 **Adjust Dosage**: Dose modification needed
        - 🔴 **Toxic**: High toxicity risk; avoid or use caution
        - 🟠 **Ineffective**: Drug unlikely to be effective
        - ⚪ **Unknown**: Insufficient data
        """)
    
    # Tab 4: Test
    with tab4:
        st.markdown("### Quick Test")
        if st.button("Load Sample VCF"):
            try:
                with open("sample_vcf/example.vcf", "rb") as f:
                    sample_file = io.BytesIO(f.read())
                    sample_file.name = "example.vcf"
                
                analyze_vcf(sample_file, ["Codeine", "Warfarin", "Clopidogrel"])
            except Exception as e:
                st.error(f"Error loading sample: {str(e)}")


def analyze_vcf(uploaded_file, drugs):
    """Analyze uploaded VCF file with improved error handling"""
    
    # Validate file format
    if not uploaded_file.name.endswith('.vcf') and not uploaded_file.name.endswith('.vcf.gz'):
        st.error("❌ Invalid file format. Please upload a .vcf or .vcf.gz file")
        return
    
    # Validate file size (5 MB limit)
    file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
    if file_size_mb > 5:
        st.error(f"❌ File too large ({file_size_mb:.2f} MB). Max size is 5 MB")
        return
    
    # Check if file is empty
    if file_size_mb == 0:
        st.error("❌ File is empty. Please upload a valid VCF file")
        return
    
    # Save uploaded file temporarily
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # Validate VCF file structure
        with open(temp_path, 'r', errors='ignore') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('##fileformat=VCFv'):
                st.error("❌ Invalid VCF file format. Must contain VCFv4 header.")
                return
        
        # Run prediction
        st.info("🔄 Analyzing VCF file...")
        predictor = RiskPredictor()
        results = predictor.predict_from_vcf(temp_path, drugs)
        
        if not results['success']:
            st.error(f"❌ Analysis failed: {', '.join(results['errors'])}")
            return
        
        # Display results
        st.success("✅ Analysis complete!")
        st.markdown("---")
        
        # Genotypes & Phenotypes
        st.markdown("### 🧬 Genetic Profile")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Genotypes (called variants):**")
            genes_with_variants = [gene for gene, gt in results['genotypes'].items() if gt]
            if genes_with_variants:
                for gene in genes_with_variants:
                    gt = results['genotypes'][gene]
                    st.markdown(f"- **{gene}**: {gt}")
            else:
                st.markdown("*No variants detected*")
        
        with col2:
            st.markdown("**Phenotypes (predicted):**")
            genes_with_pheno = [gene for gene, pheno in results['phenotypes'].items() if pheno]
            if genes_with_pheno:
                for gene in genes_with_pheno:
                    pheno = results['phenotypes'][gene]
                    st.markdown(f"- **{gene}**: {pheno.value if pheno else 'Unknown'}")
            else:
                st.markdown("*No phenotypes predicted*")
        
        st.markdown("---")
        
        # Drug Risk Assessment
        st.markdown("### 💊 Drug Risk Assessment")
        
        # Organize results
        safe_drugs = []
        warning_drugs = []
        critical_drugs = []
        
        for drug, risk_rec in results['drug_risks'].items():
            risk_level = risk_rec['risk_level']
            if risk_level == "Safe":
                safe_drugs.append((drug, risk_rec))
            elif risk_level in ["Adjust Dosage", "Ineffective"]:
                warning_drugs.append((drug, risk_rec))
            else:  # Toxic or Unknown
                critical_drugs.append((drug, risk_rec))
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🟢 Safe Drugs", len(safe_drugs))
        with col2:
            st.metric("🟡 Caution Needed", len(warning_drugs))
        with col3:
            st.metric("🔴 High Risk", len(critical_drugs))
        with col4:
            st.metric("✅ Pass Rate", f"{len(safe_drugs)}/{len(results['drug_risks'])}")
        
        st.markdown("---")
        
        # Display by category
        if critical_drugs:
            st.markdown("#### 🔴 CRITICAL / HIGH RISK")
            for drug, risk_rec in critical_drugs:
                with st.expander(f"⚠️ {drug} - {risk_rec['risk_level']}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Risk Level**: `{risk_rec['risk_level']}`")
                        st.markdown(f"**Status**: ❌ FAILED")
                        st.markdown(f"**Dosing**: {risk_rec['dosing_recommendation']}")
                    with col2:
                        st.markdown(f"**Explanation**: {risk_rec['explanation']}")
                        st.markdown(f"**Monitoring**: {risk_rec['monitoring']}")
        
        if warning_drugs:
            st.markdown("#### 🟡 MODERATE RISK (Caution Needed)")
            for drug, risk_rec in warning_drugs:
                with st.expander(f"⚠️ {drug} - {risk_rec['risk_level']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Risk Level**: `{risk_rec['risk_level']}`")
                        st.markdown(f"**Status**: ⚠️ CONDITIONAL")
                        st.markdown(f"**Dosing**: {risk_rec['dosing_recommendation']}")
                    with col2:
                        st.markdown(f"**Explanation**: {risk_rec['explanation']}")
                        st.markdown(f"**Monitoring**: {risk_rec['monitoring']}")
        
        if safe_drugs:
            st.markdown("#### 🟢 SAFE (PASSED)")
            for drug, risk_rec in safe_drugs:
                with st.expander(f"✓ {drug} - {risk_rec['risk_level']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Risk Level**: `{risk_rec['risk_level']}`")
                        st.markdown(f"**Status**: ✅ PASSED")
                        st.markdown(f"**Dosing**: {risk_rec['dosing_recommendation']}")
                    with col2:
                        st.markdown(f"**Explanation**: {risk_rec['explanation']}")
                        st.markdown(f"**Monitoring**: {risk_rec['monitoring']}")
        
        st.markdown("---")
        
        # Detailed CPIC-Aligned Risk Predictions
        if results.get('detailed_risks'):
            st.markdown("### 🔬 Detailed CPIC-Aligned Risk Predictions")
            st.markdown("*Enhanced phenotype-based risk assessment with clinical guidance*")
            
            for drug, detailed_risk in results['detailed_risks'].items():
                if "error" not in detailed_risk or not detailed_risk.get("error"):
                    try:
                        gene = detailed_risk.get("gene", "Unknown")
                        phenotype = detailed_risk.get("phenotype", "Unknown")
                        risk_level = detailed_risk.get("risk_level", "Unknown")
                        details = detailed_risk.get("details", {})
                        
                        # Color coding for risk levels
                        risk_colors = {
                            "SAFE": "🟢",
                            "ADJUST_DOSAGE": "🟡",
                            "INEFFECTIVE": "🟠",
                            "TOXIC": "🔴",
                            "UNKNOWN": "⚪"
                        }
                        
                        risk_emoji = risk_colors.get(risk_level, "⚪")
                        
                        with st.expander(f"{risk_emoji} **{drug}** ({gene} → {phenotype})", expanded=False):
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.markdown(f"**Gene**: `{gene}`")
                                st.markdown(f"**Phenotype**: `{phenotype}`")
                                st.markdown(f"**Risk Level**: `{risk_level.replace('_', ' ')}`")
                                
                                if details.get("dose_adjustment") is not None:
                                    dose_adj = details.get("dose_adjustment", 0)
                                    if dose_adj == 0:
                                        st.markdown(f"**Dose Adjustment**: ⛔ Do not use")
                                    elif dose_adj > 100:
                                        st.markdown(f"**Dose Adjustment**: ⬆️ +{dose_adj-100}% increase")
                                    elif dose_adj < 100:
                                        st.markdown(f"**Dose Adjustment**: ⬇️ {100-dose_adj}% reduction")
                                    else:
                                        st.markdown(f"**Dose Adjustment**: → Standard dosing")
                            
                            with col2:
                                if details.get("cpic_evidence"):
                                    st.markdown(f"**CPIC Evidence**: `{details.get('cpic_evidence')}`")
                                
                                if details.get("reason"):
                                    st.markdown("**Clinical Reasoning**:")
                                    st.info(details.get("reason"))
                            
                            # Detailed recommendation
                            if details.get("recommendation"):
                                st.markdown("**CPIC Recommendation**:")
                                st.success(details.get("recommendation"))
                            
                            # Monitoring requirements
                            if details.get("monitoring"):
                                st.markdown("**Monitoring Requirements**:")
                                st.warning(details.get("monitoring"))
                    except Exception as e:
                        st.write(f"Details for {drug}: {detailed_risk}")
            
            st.markdown("---")
        
        # JSON Output
        st.markdown("### 📄 Structured Output (JSON)")
        json_data = json.loads(results['json_output'])
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.json(json_data)
        
        with col2:
            st.download_button(
                label="⬇️ Download JSON",
                data=results['json_output'],
                file_name=f"pharmaGuard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            # Copy to clipboard button using system clipboard
            if st.button("📋 Copy JSON", use_container_width=True):
                import subprocess
                import platform
                
                try:
                    # Copy to clipboard using system command
                    if platform.system() == "Windows":
                        # Windows: use clip command
                        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                        process.communicate(results['json_output'].encode('utf-8'))
                    elif platform.system() == "Darwin":
                        # macOS: use pbcopy
                        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                        process.communicate(results['json_output'].encode('utf-8'))
                    else:
                        # Linux: use xclip or xsel
                        try:
                            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                            process.communicate(results['json_output'].encode('utf-8'))
                        except FileNotFoundError:
                            process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                            process.communicate(results['json_output'].encode('utf-8'))
                    
                    st.success("✅ JSON copied to clipboard!")
                except Exception as e:
                    st.warning(f"Could not copy to clipboard: {str(e)}")
                    st.code(results['json_output'], language='json')
    
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
    
    finally:
        # Clean up temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)





if __name__ == "__main__":
    main()
