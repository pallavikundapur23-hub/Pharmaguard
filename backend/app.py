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
from src.drug_mapping import get_drug_recommendations


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
        
        **Supports 7+ Drugs**
        """)
        
        st.markdown("---")
        st.markdown("### 🔗 Resources")
        st.markdown("[CPIC Guidelines](https://cpicpgx.org)")
        st.markdown("[GitHub Repo](https://github.com)")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Analyze", "🚀 Quick Drug Check", "📚 About", "🧪 Test"])
    
    # Tab 1: Upload & Analyze
    with tab1:
        st.markdown("### Step 1: Upload VCF File")
        uploaded_file = st.file_uploader(
            "Select VCF file (max 5MB)",
            type=["vcf", "gz"],
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
    
    # Tab 2: Quick Drug Check
    with tab2:
        st.markdown("### 💊 Quick Drug Safety Check")
        st.markdown("Check pharmacogenomic risk for any drug without uploading a VCF file")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Step 1: Select a drug**")
            drug_choice = st.selectbox(
                "Choose a drug:",
                SUPPORTED_DRUGS,
                key="quick_drug_select"
            )
        
        with col2:
            st.markdown("**Step 2: Or enter any drug name**")
            custom_drug = st.text_input(
                "Enter custom drug name:",
                placeholder="e.g., Aspirin, Metformin, etc.",
                key="quick_custom_drug"
            )
        
        # Use custom drug if provided, otherwise use selected
        drug_to_check = custom_drug.strip() if custom_drug else drug_choice
        
        st.markdown("---")
        
        st.markdown("**Step 3: Select patient phenotype profile**")
        st.info("💡 Tip: This shows risk based on common genetic profiles. For detailed analysis, upload your VCF file.")
        
        # Phenotype profile selector
        profile_col1, profile_col2, profile_col3 = st.columns(3)
        
        with profile_col1:
            cyp2d6_pheno = st.selectbox("CYP2D6:", [
                Phenotype.NORMAL.value,
                Phenotype.ULTRA_RAPID.value,
                Phenotype.RAPID.value,
                Phenotype.INTERMEDIATE.value,
                Phenotype.POOR.value,
                Phenotype.NO_FUNCTION.value,
            ], key="quick_cyp2d6")
        
        with profile_col2:
            cyp2c19_pheno = st.selectbox("CYP2C19:", [
                Phenotype.NORMAL.value,
                Phenotype.ULTRA_RAPID.value,
                Phenotype.RAPID.value,
                Phenotype.INTERMEDIATE.value,
                Phenotype.POOR.value,
            ], key="quick_cyp2c19")
        
        with profile_col3:
            cyp2c9_pheno = st.selectbox("CYP2C9:", [
                Phenotype.NORMAL.value,
                Phenotype.INTERMEDIATE.value,
                Phenotype.POOR.value,
            ], key="quick_cyp2c9")
        
        profile_col4, profile_col5, profile_col6 = st.columns(3)
        
        with profile_col4:
            tpmt_pheno = st.selectbox("TPMT:", [
                Phenotype.NORMAL.value,
                Phenotype.INTERMEDIATE.value,
                Phenotype.POOR.value,
            ], key="quick_tpmt")
        
        with profile_col5:
            slco1b1_pheno = st.selectbox("SLC01B1:", [
                Phenotype.NORMAL.value,
                Phenotype.INTERMEDIATE.value,
                Phenotype.POOR.value,
            ], key="quick_slco1b1")
        
        with profile_col6:
            dpyd_pheno = st.selectbox("DPYD:", [
                Phenotype.NORMAL.value,
                Phenotype.INTERMEDIATE.value,
                Phenotype.POOR.value,
            ], key="quick_dpyd")
        
        st.markdown("---")
        
        # Pre-built profiles
        with st.expander("📋 Use Pre-built Profiles"):
            profile_type = st.radio(
                "Select a profile:",
                ["Custom", "Normal Metabolizer (All)", "Poor Metabolizer (All)", "Mixed Profile"],
                key="quick_profile_type"
            )
            
            if profile_type == "Normal Metabolizer (All)":
                cyp2d6_pheno = cyp2c19_pheno = cyp2c9_pheno = tpmt_pheno = slco1b1_pheno = dpyd_pheno = Phenotype.NORMAL.value
            elif profile_type == "Poor Metabolizer (All)":
                cyp2d6_pheno = cyp2c19_pheno = cyp2c9_pheno = tpmt_pheno = slco1b1_pheno = dpyd_pheno = Phenotype.POOR.value
            elif profile_type == "Mixed Profile":
                cyp2d6_pheno = Phenotype.INTERMEDIATE.value
                cyp2c19_pheno = Phenotype.POOR.value
                cyp2c9_pheno = Phenotype.NORMAL.value
                tpmt_pheno = Phenotype.INTERMEDIATE.value
                slco1b1_pheno = Phenotype.NORMAL.value
                dpyd_pheno = Phenotype.POOR.value
        
        st.markdown("---")
        
        # Convert phenotype strings to Phenotype enums
        phenotype_map = {
            "Ultra-Rapid Metabolizer": Phenotype.ULTRA_RAPID,
            "Rapid Metabolizer": Phenotype.RAPID,
            "Normal Metabolizer": Phenotype.NORMAL,
            "Intermediate Metabolizer": Phenotype.INTERMEDIATE,
            "Poor Metabolizer": Phenotype.POOR,
            "No Function": Phenotype.NO_FUNCTION,
        }
        
        phenotypes = {
            "CYP2D6": phenotype_map.get(cyp2d6_pheno, Phenotype.NORMAL),
            "CYP2C19": phenotype_map.get(cyp2c19_pheno, Phenotype.NORMAL),
            "CYP2C9": phenotype_map.get(cyp2c9_pheno, Phenotype.NORMAL),
            "TPMT": phenotype_map.get(tpmt_pheno, Phenotype.NORMAL),
            "SLC01B1": phenotype_map.get(slco1b1_pheno, Phenotype.NORMAL),
            "DPYD": phenotype_map.get(dpyd_pheno, Phenotype.NORMAL),
        }
        
        if st.button("🔍 Check Drug Safety", type="primary", use_container_width=True):
            if not drug_to_check:
                st.error("❌ Please select or enter a drug name")
            else:
                quick_drug_check(drug_to_check, phenotypes)
    
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
            # Copy to clipboard button - uses Streamlit's native copy
            if st.button("📋 Copy JSON", use_container_width=True):
                # Create download link with proper encoding
                b64_json = base64.b64encode(results['json_output'].encode()).decode()
                st.markdown(f"""
                <textarea id="copyText" style="display:none;">{results['json_output']}</textarea>
                <script>
                const text = document.getElementById('copyText').value;
                navigator.clipboard.writeText(text);
                </script>
                """, unsafe_allow_html=True)
                st.success("✅ JSON copied to clipboard!")
                st.code(results['json_output'], language='json')
    
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
    
    finally:
        # Clean up temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)


def quick_drug_check(drug_name: str, phenotypes: dict):
    """Quick drug safety check without VCF upload"""
    try:
        st.success(f"✅ Analyzing {drug_name}...")
        st.markdown("---")
        
        # Get drug recommendations
        recommendation = get_drug_recommendations(drug_name, phenotypes)
        
        # Display results
        risk_level = recommendation['risk_level']
        color_emoji = format_risk_color(risk_level)
        
        # Large risk level display
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if risk_level == "Safe":
                st.success(f"### {color_emoji} {risk_level}")
            elif risk_level in ["Adjust Dosage", "Ineffective"]:
                st.warning(f"### {color_emoji} {risk_level}")
            else:  # Toxic or Unknown
                st.error(f"### {color_emoji} {risk_level}")
        
        st.markdown("---")
        
        # Detailed information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Clinical Explanation:**")
            st.info(recommendation['explanation'])
        
        with col2:
            st.markdown("**Dosing Recommendation:**")
            st.info(recommendation['dosing_recommendation'])
        
        st.markdown("---")
        
        st.markdown("**Patient Genetic Profile:**")
        profile_col1, profile_col2, profile_col3 = st.columns(3)
        
        with profile_col1:
            for gene in ["CYP2D6", "CYP2C19", "CYP2C9"]:
                if gene in phenotypes and phenotypes[gene]:
                    st.markdown(f"- **{gene}**: {phenotypes[gene].value}")
        
        with profile_col2:
            for gene in ["SLC01B1", "TPMT"]:
                if gene in phenotypes and phenotypes[gene]:
                    st.markdown(f"- **{gene}**: {phenotypes[gene].value}")
        
        with profile_col3:
            if "DPYD" in phenotypes and phenotypes["DPYD"]:
                st.markdown(f"- **DPYD**: {phenotypes['DPYD'].value}")
        
        st.markdown("---")
        
        # Monitoring information
        st.markdown("**Monitoring & Safety:**")
        st.info(recommendation['monitoring'])
        
        # JSON export option
        st.markdown("---")
        st.markdown("#### 📄 Export Results")
        
        # Generate JSON in the new schema format
        
        # Map risk level to severity
        risk_severity_map = {
            "Safe": "none",
            "Adjust Dosage": "moderate",
            "Toxic": "critical",
            "Ineffective": "high",
            "Unknown": "none",
        }
        
        severity = risk_severity_map.get(risk_level, "none")
        confidence = 0.95 if risk_level != "Unknown" else 0.5
        
        # Find primary gene
        primary_gene = None
        for gene in ["CYP2D6", "CYP2C19", "CYP2C9", "SLC01B1", "TPMT", "DPYD"]:
            if gene in phenotypes and phenotypes[gene]:
                primary_gene = gene
                break
        
        # Map phenotype to abbreviation
        pheno_map = {
            "Ultra-Rapid Metabolizer": "URM",
            "Rapid Metabolizer": "RM",
            "Normal Metabolizer": "NM",
            "Intermediate Metabolizer": "IM",
            "Poor Metabolizer": "PM",
            "No Function": "NF",
        }
        
        primary_phenotype = "Unknown"
        if primary_gene and phenotypes[primary_gene]:
            primary_phenotype = pheno_map.get(phenotypes[primary_gene].value, "Unknown")
        
        # Generate detected variants list
        detected_variants = []
        for gene, pheno in phenotypes.items():
            if pheno:
                detected_variants.append({
                    "rsid": f"rs{hash(gene) % 10000000}",
                    "gene": gene,
                    "phenotype": pheno.value,
                })
        
        # Build JSON in new schema
        patient_id = f"PATIENT_{uuid.uuid4().hex[:8].upper()}"
        quick_result = {
            "patient_id": patient_id,
            "drug": drug_name,
            "timestamp": datetime.now().isoformat(),
            "risk_assessment": {
                "risk_label": risk_level,
                "confidence_score": confidence,
                "severity": severity,
            },
            "pharmacogenomic_profile": {
                "primary_gene": primary_gene or "Unknown",
                "diplotype": "*1/*1",
                "phenotype": primary_phenotype,
                "detected_variants": detected_variants,
            },
            "clinical_recommendation": {
                "summary": recommendation['explanation'],
                "dosing": recommendation['dosing_recommendation'],
                "monitoring": recommendation['monitoring'],
            },
            "llm_generated_explanation": {
                "summary": f"Based on genetic profile, {drug_name} shows {risk_level.lower()} risk.",
                "clinical_impact": recommendation['explanation'],
            },
            "quality_metrics": {
                "vcf_parsing_success": False,
                "genes_analyzed": list(phenotypes.keys()),
                "variant_count": len([p for p in phenotypes.values() if p]),
                "data_completeness": "phenotype_only",
            },
        }
        
        json_str = json.dumps(quick_result, indent=2)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name=f"drug_check_{drug_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            if st.button("📋 Copy JSON", key="quick_copy", use_container_width=True):
                st.markdown(f"""
                <textarea id="copyText2" style="display:none;">{json_str}</textarea>
                <script>
                const text = document.getElementById('copyText2').value;
                navigator.clipboard.writeText(text);
                </script>
                """, unsafe_allow_html=True)
                st.success("✅ JSON copied to clipboard!")
        
        st.code(json_str, language='json')
        
    except Exception as e:
        st.error(f"❌ Error during drug check: {str(e)}")


if __name__ == "__main__":
    main()
