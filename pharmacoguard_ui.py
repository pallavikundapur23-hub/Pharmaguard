"""
PharmaGuard - AI-Assisted Pharmacogenomic Clinical Decision Support Dashboard
Professional clinical interface for pharmacogenomics analysis
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import json

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="PharmaGuard - Clinical Decision Support",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR PROFESSIONAL CLINICAL APPEARANCE
# ============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Custom styling for medical dashboard */
    .reportview-container {
        background: linear-gradient(135deg, #F8FAFC 0%, #F0F4F8 100%);
    }
    
    .main {
        background: linear-gradient(135deg, #F8FAFC 0%, #F0F4F8 100%);
    }
    
    /* Header styling - PROFESSIONAL */
    .header-container {
        background: linear-gradient(135deg, #003D7A 0%, #0066CC 100%);
        padding: 50px 40px;
        border-radius: 12px;
        margin: 20px 0 40px 0;
        box-shadow: 0 8px 24px rgba(0, 61, 122, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 52px;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: -1px;
        font-family: 'Inter', sans-serif;
    }
    
    .header-subtitle {
        color: #E8F0FF;
        font-size: 18px;
        font-weight: 400;
        margin: 12px 0 0 0;
        letter-spacing: 0.3px;
        opacity: 0.95;
    }
    
    .header-meta {
        color: #B8D4FF;
        font-size: 13px;
        margin-top: 16px;
        display: flex;
        gap: 24px;
        opacity: 0.85;
    }
    
    /* Section header styling */
    .section-header {
        background: white;
        padding: 20px 24px;
        border-left: 5px solid #0066CC;
        margin: 35px 0 25px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .section-header h2 {
        margin: 0;
        color: #003D7A;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        font-family: 'Inter', sans-serif;
    }
    
    .section-header p {
        margin: 6px 0 0 0;
        color: #6C757D;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Divider styling */
    .divider {
        height: 2px;
        background: linear-gradient(to right, transparent 0%, #DADFE5 20%, #DADFE5 80%, transparent 100%);
        margin: 32px 0;
        opacity: 0.6;
    }
    
    /* Card styling */
    .card {
        background: white;
        border: 1px solid #E8EDF4;
        border-radius: 10px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 24px rgba(0, 61, 122, 0.08);
        border-color: #0066CC;
        transform: translateY(-2px);
    }
    
    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #F3E5F5 100%);
        border-left: 5px solid #1976D2;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #0D47A1;
        box-shadow: 0 2px 6px rgba(25, 118, 210, 0.08);
    }
    
    /* Success box styling */
    .success-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        border-left: 5px solid #388E3C;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #1B5E20;
        box-shadow: 0 2px 6px rgba(56, 142, 60, 0.08);
    }
    
    /* Warning box styling */
    .warning-box {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFF9C4 100%);
        border-left: 5px solid #F57C00;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #E65100;
        box-shadow: 0 2px 6px rgba(245, 124, 0, 0.08);
    }
    
    /* Danger/Risk box styling */
    .danger-box {
        background: linear-gradient(135deg, #FFEBEE 0%, #FCE4EC 100%);
        border-left: 5px solid #D32F2F;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #B71C1C;
        box-shadow: 0 2px 6px rgba(211, 47, 47, 0.08);
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, white 0%, #F8FAFC 100%);
        border: 1px solid #E8EDF4;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 16px rgba(0, 61, 122, 0.1);
        border-color: #0066CC;
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #003D7A;
        margin: 12px 0 8px 0;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-label {
        font-size: 12px;
        color: #6C757D;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 40px 20px;
        border-top: 2px solid #E8EDF4;
        margin-top: 50px;
        font-size: 12px;
        color: #6C757D;
        background: white;
        line-height: 1.8;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER SECTION
# ============================================================================
with st.container():
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">💊 PharmaGuard</h1>
        <p class="header-subtitle">AI-Assisted Pharmacogenomic Clinical Decision Support</p>
        <div class="header-meta">
            <span>🏥 Clinical Dashboard v1.0</span>
            <span>⚙️ Powered by Groq LLM</span>
            <span>📊 Real-time Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# INFORMATION BOX
# ============================================================================
st.markdown("""
<div class="info-box">
    <strong>ℹ️ About PharmaGuard:</strong> This clinical decision support system analyzes pharmacogenomic 
    variants from VCF files to provide AI-assisted recommendations for drug dosing and safety monitoring.
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SECTION 0: QUICK INPUT
# ============================================================================
st.markdown('<div class="section-header"><h2>⚡ Quick Analysis</h2><p>Upload genomic data and select medications</p></div>', unsafe_allow_html=True)

# Two-column input layout
col_upload, col_drugs = st.columns(2)

# LEFT COLUMN: VCF FILE UPLOAD
with col_upload:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**📁 Select VCF File**")
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    
    vcf_file = st.file_uploader(
        "Upload VCF File",
        type=["vcf"],
        help="Upload a VCF (Variant Call Format) file containing genetic variants (max 5MB)",
        label_visibility="collapsed"
    )
    
    if vcf_file:
        st.markdown(f"""
        <div class="success-box">
            ✓ <strong>File loaded:</strong> {vcf_file.name} ({vcf_file.size:,} bytes)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <p style="color: #666; font-size: 13px; text-align: center; margin: 10px 0;">
        <strong>Drag & drop your VCF file</strong><br>
        or click to browse
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN: DRUG SELECTION
with col_drugs:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**💊 Select Medications**")
    
    selected_drugs_quick = st.multiselect(
        "Choose drugs to analyze",
        [
            "CODEINE",
            "WARFARIN",
            "CLOPIDOGREL",
            "SIMVASTATIN",
            "AZATHIOPRINE",
            "FLUOROURACIL"
        ],
        default=["CODEINE"],
        help="Select one or more medications for pharmacogenetic analysis",
        label_visibility="collapsed"
    )
    
    # Display selected drugs count
    if selected_drugs_quick:
        st.markdown(f"""
        <div style="margin-top: 12px; padding: 10px; background-color: #E8F5E9; border-radius: 4px; text-align: center;">
            <strong style="color: #388E3C;">✓ {len(selected_drugs_quick)} medication(s) selected</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-top: 12px; padding: 10px; background-color: #FFF3E0; border-radius: 4px; text-align: center;">
            <strong style="color: #F57C00;">⚠ Please select at least one medication</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# FULL-WIDTH ANALYZE BUTTON
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Check if both inputs are provided
analysis_ready = vcf_file is not None and len(selected_drugs_quick) > 0

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    analyze_clicked = st.button(
        "🔬 Analyze Patient",
        use_container_width=True,
        disabled=not analysis_ready,
        help="Click to start pharmacogenomics analysis" if analysis_ready else "Please upload VCF and select medications"
    )

with col2:
    st.empty()

with col3:
    st.empty()

# Loading spinner when clicked
if analyze_clicked:
    with st.spinner("🔄 Analyzing genetic variants..."):
        st.markdown("""
        <div class="info-box">
            <strong>⏳ Analysis in Progress:</strong> Processing VCF file and generating pharmacogenetic insights...
            This may take a moment.
        </div>
        """, unsafe_allow_html=True)
    
    # Placeholder for future analysis results
    st.success("✓ Analysis complete! Results will display below.")

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Application Settings")
    st.divider()
    
    # Analysis settings
    st.markdown("**Analysis Options**")
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Quick Analysis", "Comprehensive Analysis", "Risk Assessment Only"],
        help="Select the depth of analysis to perform"
    )
    
    include_llm = st.checkbox(
        "Include AI Explanations",
        value=True,
        help="Generate detailed LLM-powered explanations"
    )
    
    st.divider()
    
    # Display settings
    st.markdown("**Display Settings**")
    show_advanced = st.checkbox(
        "Show Advanced Metrics",
        value=False,
        help="Display detailed statistical metrics"
    )
    
    color_scheme = st.selectbox(
        "Color Scheme",
        ["Professional", "High Contrast", "Dark Mode"],
        help="Choose display appearance"
    )
    
    st.divider()
    
    # Info section
    st.markdown("**ℹ️ About**")
    st.caption("""
    **PharmaGuard v1.0**
    
    Clinical pharmacogenomics decision support system.
    
    For clinical inquiries contact your pharmacogenomics specialist.
    """)

# ============================================================================
# SECTION 1: PATIENT INFORMATION
# ============================================================================
st.markdown('<div class="section-header"><h2>👤 Patient Information</h2><p>Enter or import patient clinical data</p></div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    patient_id = st.text_input("Patient ID", placeholder="MRN or ID", help="Medical record number")

with col2:
    age = st.number_input("Age (years)", min_value=0, max_value=150, step=1, help="Patient age")

with col3:
    gender = st.selectbox("Gender", ["Not Specified", "Male", "Female", "Other"], help="Biological sex")

with col4:
    ethnicity = st.selectbox("Ethnicity", ["Not Specified", "European", "African", "Asian", "Hispanic", "Other"], help="Reported ancestry")

st.markdown('</div>', unsafe_allow_html=True)

# Additional patient info
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Clinical Indication**")
    clinical_indication = st.text_area(
        "Primary diagnosis or indication",
        placeholder="e.g., Hypertension, Depression, Pain management...",
        height=90,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Current Medications**")
    current_meds = st.text_area(
        "Current medications",
        placeholder="List current medications separated by commas...",
        height=90,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 2: GENOMIC DATA UPLOAD
# ============================================================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header"><h2>🧬 Genomic Data Input</h2><p>Upload VCF file or select from database</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Upload VCF File**")
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a VCF file",
        type=["vcf", "txt"],
        help="Upload a VCF (Variant Call Format) file",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div class="success-box">
            ✓ File uploaded: <strong>{uploaded_file.name}</strong> ({uploaded_file.size} bytes)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <p style="color: #666; font-size: 14px;">
        <strong>Supported Formats:</strong> VCF 4.0+<br>
        <strong>File Size Limit:</strong> 50 MB<br>
        <strong>No files uploaded yet</strong>
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Or Select from Database**")
    
    # Sample VCF files available
    sample_files = ["Select a sample...", "Codeine Risk Profile", "Warfarin Dosing", "Comprehensive Panel"]
    selected_sample = st.selectbox("Sample VCF Files", sample_files, label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("**Analysis Parameters**")
    gene_panel = st.multiselect(
        "Gene Panel",
        ["CYP2D6", "CYP2C9", "CYP2C19", "TPMT", "SLCO1B1", "DPYD"],
        default=["CYP2D6", "CYP2C9", "CYP2C19", "TPMT", "SLCO1B1", "DPYD"],
        help="Select genes to analyze (6-gene CPIC panel)"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 3: DRUG SELECTION
# ============================================================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header"><h2>💊 Drug Selection</h2><p>Select medications for analysis</p></div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("**Medications to Analyze**")
    selected_drugs = st.multiselect(
        "Drug List",
        ["Codeine", "Warfarin", "Clopidogrel", "Omeprazole", "Venlafaxine", "Metoprolol", "Rosuvastatin"],
        default=["Codeine", "Warfarin"],
        help="Select medications to analyze for this patient",
        label_visibility="collapsed"
    )
    st.caption(f"✓ Selected: {len(selected_drugs)} medication(s)")

with col2:
    st.markdown("**Quick Drug Search**")
    drug_search = st.text_input(
        "Search for drug",
        placeholder="Type drug name...",
        help="Search drug database",
        label_visibility="collapsed"
    )
    
    if drug_search:
        st.caption(f"🔍 Searching for: **{drug_search}**")
    
    st.markdown("---")
    
    # CPIC guidelines info
    st.markdown("""
    <div class="info-box">
    <strong>CPIC Guidelines:</strong> Analysis based on latest CPIC 
    (Clinical Pharmacogenetics Implementation Consortium) recommendations.
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ACTION BUTTONS
# ============================================================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    analyze_button = st.button(
        "🔬 Start Analysis",
        use_container_width=True,
        help="Run pharmacogenomics analysis"
    )

with col2:
    save_button = st.button(
        "💾 Save Session",
        use_container_width=True,
        help="Save current session data"
    )

with col3:
    reset_button = st.button(
        "🔄 Reset Form",
        use_container_width=True,
        help="Clear all inputs"
    )

# Initialize session state for analysis results
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False

if analyze_button:
    st.session_state.show_loading = True
    st.session_state.analysis_complete = True

if save_button:
    st.markdown("""
    <div class="success-box">
        ✓ <strong>Session saved:</strong> Patient data and analysis parameters saved to database.
    </div>
    """, unsafe_allow_html=True)

if reset_button:
    st.markdown("""
    <div class="info-box">
        ℹ️ <strong>Form reset:</strong> All fields cleared. Ready for new patient data.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SECTION 4: RESULTS DASHBOARD (Shows when analysis completes)
# ============================================================================
if st.session_state.analysis_complete:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if st.session_state.show_loading:
        with st.spinner("🔬 Analyzing pharmacogenomic data... Processing genetic variants and generating clinical recommendations..."):
            import time
            time.sleep(3)  # Simulate processing time
        st.session_state.show_loading = False
    
    st.markdown('<div class="section-header"><h2>📊 Analysis Results</h2><p>Comprehensive pharmacogenomics findings and clinical recommendations</p></div>', unsafe_allow_html=True)
    
    # Results Dashboard - Two Columns
    col_left, col_right = st.columns(2, gap="large")
    
    # LEFT COLUMN: GENETIC PROFILE
    with col_left:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #0066CC;">
            <div style="padding: 0 0 15px 0; border-bottom: 1px solid #E0E0E0;">
                <h3 style="margin: 0; color: #003D7A; font-size: 18px;">🧬 Genetic Profile</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Gene Profile Metrics
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Gene Detected</div>
                <div style="font-size: 28px; font-weight: 700; color: #003D7A; margin: 10px 0;">CYP2D6</div>
                <div style="font-size: 12px; color: #666;">Cytochrome P450</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_g2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Confidence Score</div>
                <div style="font-size: 28px; font-weight: 700; color: #28A745; margin: 10px 0;">98.5%</div>
                <div style="font-size: 12px; color: #666;">High Confidence</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Phenotype Section
        st.markdown("""
        <div style="padding: 15px 0;">
            <div style="font-size: 14px; font-weight: 600; color: #003D7A; margin-bottom: 10px;">Phenotype Classification</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="success-box">
            <strong>Ultra-Rapid Metabolizer (UM)</strong><br>
            <small>Genotype: *1/*1 (Two functional alleles)</small><br>
            <small>Metabolic Activity: 200% of normal</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Genetic Details
        st.markdown("""
        <div style="padding: 15px; background-color: #F8F9FA; border-radius: 6px; margin-top: 15px;">
            <div style="font-size: 13px; font-weight: 600; color: #003D7A; margin-bottom: 8px;">Allele Information</div>
            <div style="font-size: 13px; color: #333; line-height: 1.6;">
                <strong>Allele 1:</strong> *1 (Wild-type, functional)<br>
                <strong>Allele 2:</strong> *1 (Wild-type, functional)<br>
                <strong>Zygosity:</strong> Homozygous
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # RIGHT COLUMN: RISK ASSESSMENT
    with col_right:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #DC3545;">
            <div style="padding: 0 0 15px 0; border-bottom: 1px solid #E0E0E0;">
                <h3 style="margin: 0; color: #003D7A; font-size: 18px;">⚠️ Risk Assessment</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk Level Badge and Description
        st.markdown("""
        <div style="text-align: center; padding: 20px 15px; background-color: #FFEBEE; border-radius: 6px; margin: 15px 0; border: 1px solid #FFCDD2;">
            <div style="font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">Risk Level</div>
            <div style="font-size: 42px; font-weight: 700; color: #DC3545; margin: 10px 0;">⚠️ HIGH</div>
            <div style="font-size: 14px; color: #B71C1C; font-weight: 500;">Significant Drug Interaction Risk</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk Factors
        st.markdown("""
        <div style="padding: 15px 0;">
            <div style="font-size: 14px; font-weight: 600; color: #003D7A; margin-bottom: 10px;">Risk Factors</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="danger-box">
            <strong>This metabolizer phenotype may result in:</strong><br>
            <small>• Subtherapeutic drug levels at standard doses<br>
            • Increased need for higher drug concentrations<br>
            • Potential treatment failure with standard dosing<br>
            • Monitor carefully for therapeutic efficacy</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk Summary
        st.markdown("""
        <div style="padding: 15px; background-color: #FFF3E0; border-radius: 6px; margin-top: 15px; border-left: 3px solid #F57C00;">
            <div style="font-size: 12px; font-weight: 600; color: #E65100; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Clinical Recommendation</div>
            <div style="font-size: 13px; color: #BF360C; line-height: 1.6;">
                <strong>Dosage Adjustment Required:</strong> Consider dose increase up to 150% of standard dosing. Recommend therapeutic drug monitoring if available. Coordinate with pharmacy and clinical team.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================================
    # AI CLINICAL EXPLANATION SECTION
    # ============================================================================
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h2>🤖 AI Clinical Explanation</h2><p>AI-generated comprehensive clinical insights and recommendations</p></div>', unsafe_allow_html=True)
    
    # LLM-Generated Clinical Explanation
    llm_explanation = """
    **Pharmacogenetic Analysis Summary**
    
    The CYP2D6*1/*1 genotype identifies an ultra-rapid metabolizer (UM) phenotype. This genetic profile is particularly significant for medications that are pro-drugs or are metabolized by the CYP2D6 enzyme, especially opioid analgesics like codeine.
    
    **Genetic Interpretation:**
    The patient carries two wild-type (*1) alleles of the CYP2D6 gene, both encoding fully functional enzyme. This results in substantially increased metabolic activity—approximately 200% of normal activity levels. The ultra-rapid metabolism of CYP2D6 substrates means that codeine is rapidly converted to active metabolites, particularly morphine.
    
    **Clinical Implications for Codeine:**
    - **Increased Drug Effect:** Faster conversion of codeine to morphine results in higher morphine concentrations
    - **Toxicity Risk:** Even at standard doses, ultra-rapid metabolizers face increased risk of opioid-related adverse effects
    - **Safety Concerns:** Potential for respiratory depression, severe sedation, and overdose at therapeutic doses
    - **Treatment Failure:** At higher doses intended for UM patients, risk of toxicity becomes substantial
    
    **Recommended Clinical Action:**
    1. **First-line recommendation:** Consider alternative analgesics that do not depend on CYP2D6 metabolism (NSAIDs, non-opioid analgesics)
    2. **If opioid necessary:** Implement therapeutic drug monitoring (TDM) or pharmacokinetic testing to guide individualized dosing
    3. **Patient counseling:** Inform patient of increased sensitivity to opioids and heightened toxicity risk
    4. **Monitoring protocol:** Frequent clinical assessments for signs of opioid toxicity (excessive sedation, respiratory changes)
    5. **Interdisciplinary coordination:** Work with pharmacy, pain management, and primary care team
    
    **Evidence Quality:** Strong recommendation from Clinical Pharmacogenetics Implementation Consortium (CPIC)
    Guideline classification: One-star phenotype-based recommendation with moderate-to-strong evidence
    """
    
    st.info(llm_explanation)
    
    # ============================================================================
    # CLINICAL RECOMMENDATION SECTION
    # ============================================================================
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h2>👨‍⚕️ Clinical Recommendation</h2><p>CPIC-based actionable recommendation for clinical care</p></div>', unsafe_allow_html=True)
    
    # Doctor's Recommendation Panel - Green Success Box
    st.markdown("""
    <div class="success-box" style="padding: 20px; border-left: 5px solid #28A745; background-color: #D4EDDA; border-radius: 6px; font-size: 15px; line-height: 1.7;">
        <div style="font-size: 16px; font-weight: 700; color: #155724; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;">
            ✓ CPIC Recommendation: STRONG
        </div>
        <div style="color: #155724; margin-bottom: 15px;">
            <strong>Primary Recommendation:</strong><br>
            For patients with the CYP2D6 ultra-rapid metabolizer phenotype being considered for codeine therapy, 
            <strong>it is recommended to choose an alternative analgesic medication</strong> that is not metabolized by CYP2D6, 
            such as morphine, tramadol, or non-opioid analgesics (NSAIDs, acetaminophen).
        </div>
        <div style="color: #155724; margin-bottom: 15px;">
            <strong>Rationale:</strong><br>
            Ultra-rapid metabolizers of codeine face substantially increased risk of opioid-related adverse effects, 
            including overdose toxicity, at standard dosing regimens. The benefit of codeine pain relief is likely to be 
            diminished while the risk of toxicity is substantially increased.
        </div>
        <div style="color: #155724; margin-bottom: 15px;">
            <strong>Strength of Evidence:</strong><br>
            <span style="background-color: rgba(40, 167, 69, 0.2); padding: 2px 8px; border-radius: 3px; font-weight: 600;">
                ★ STRONG Evidence | One-star recommendation
            </span>
        </div>
        <div style="color: #155724; border-top: 1px solid #a7c7ba; padding-top: 15px;">
            <strong>Next Steps:</strong><br>
            1. Counsel patient on opioid sensitivity due to CYP2D6 genetics<br>
            2. Document pharmacogenetic findings in medical record<br>
            3. Coordinate with pain management and pharmacy teams<br>
            4. Consider alternative analgesic strategy based on clinical indication<br>
            5. Schedule follow-up to monitor treatment response and safety
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # DRUG-SPECIFIC MONITORING SECTIONS
    # ============================================================================
    
    # INR Monitoring Section - Only show if WARFARIN is selected
    if "WARFARIN" in selected_drugs_quick:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><h2>🩸 INR Monitoring (Warfarin)</h2><p>International Normalized Ratio monitoring guidelines for warfarin therapy</p></div>', unsafe_allow_html=True)
        
        # INR Monitoring Information Box
        st.markdown("""
        <div class="warning-box" style="padding: 20px; border-left: 5px solid #FFA500; background-color: #FFF3CD; border-radius: 6px; font-size: 15px; line-height: 1.7;">
            <div style="font-size: 16px; font-weight: 700; color: #856404; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;">
                📋 INR Target Range
            </div>
            <div style="color: #856404; margin-bottom: 20px;">
                <div style="font-size: 24px; font-weight: 700; color: #FF6B35; text-align: center; padding: 15px; background-color: rgba(255, 107, 53, 0.1); border-radius: 6px; margin-bottom: 15px;">
                    Target INR: 2.0 – 3.0
                </div>
            </div>
            <div style="color: #856404; margin-bottom: 15px;">
                <strong>Monitoring Recommendation:</strong><br>
                For patients initiating warfarin therapy, baseline INR should be obtained prior to treatment initiation. 
                During the induction phase (first 5-7 days), INR should be monitored every 2-3 days. Once therapeutic goals are achieved, 
                INR monitoring frequency can be reduced to every 2-4 weeks for stable patients. For patients with additional risk factors 
                or dose changes, more frequent monitoring (every 1-2 weeks) is warranted.
            </div>
            <div style="color: #856404; margin-bottom: 15px;">
                <strong>Clinical Actions Based on INR:</strong><br>
                • <strong>INR < 2.0:</strong> Subtherapeutic - Increase warfarin dose or frequency<br>
                • <strong>INR 2.0–3.0:</strong> Therapeutic - Continue current dose, maintain monitoring schedule<br>
                • <strong>INR 3.0–4.0:</strong> Supratherapeutic - Reduce dose or hold dose, increase monitoring<br>
                • <strong>INR > 4.0:</strong> High bleeding risk - Consider vitamin K supplementation, hold warfarin, urgent reassessment
            </div>
            <div style="color: #856404; border-top: 1px solid #d4a574; padding-top: 15px;">
                <strong>Important Considerations:</strong><br>
                1. Pharmacogenetic variants (CYP2C9, VKORC1) may affect warfarin sensitivity and dosing requirements<br>
                2. Multiple drug-drug interactions can increase bleeding risk (ASA, NSAIDs, antibiotics)<br>
                3. Dietary vitamin K intake should remain consistent to avoid INR fluctuations<br>
                4. Patient education on bleeding precautions and medication adherence is essential<br>
                5. Genetics-guided dosing algorithms may improve warfarin dose prediction and safety
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Results tabs below the cards
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Detailed Results", "Recommendations", "Reports", "JSON Output"])

    with tab1:
        st.markdown("""
        <div class="card">
            <strong>Analysis Summary</strong><br><br>
            Patient genetic analysis completed successfully. 
            The CYP2D6 gene shows an ultra-rapid metabolizer phenotype which significantly impacts drug metabolism for codeine and related medications.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Genes Analyzed</div>
                <div class="metric-value">1</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Variants Found</div>
                <div class="metric-value">2</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Drugs Analyzed</div>
                <div class="metric-value">1</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        **Clinical Recommendations:**
        
        1. **Codeine Metabolism:** Ultra-rapid metabolizers may experience subtherapeutic effects at standard doses
        2. **Dosing Strategy:** Consider therapeutic drug monitoring or pharmacogenomic-guided dosing
        3. **Follow-up:** Monitor patient response closely and adjust dosing based on clinical efficacy
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Report Generation**")
            report_format = st.selectbox(
                "Report Format",
                ["PDF", "HTML", "Text"],
                help="Select output format",
                label_visibility="collapsed"
            )
            download_btn = st.button("📥 Download Report", use_container_width=True)
        
        with col2:
            st.markdown("**Report Templates**")
            template = st.selectbox(
                "Template",
                ["Clinical Summary", "Detailed Analysis", "Executive Summary"],
                help="Choose report template",
                label_visibility="collapsed"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab5:
        st.markdown("""
        <div class="card" style="padding-bottom: 10px;">
            <h3 style="margin-top: 0; color: #003D7A; font-size: 18px;">📋 Structured Analysis Output</h3>
            <p style="color: #666; margin-bottom: 15px;">Complete analysis results in JSON format for integration with other systems and clinical workflows.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create sample JSON structure with all 6 CPIC drugs
        analysis_json = {
            "analysis_metadata": {
                "analysis_id": "PG-2026-02-20-001",
                "analysis_date": "2026-02-20",
                "analysis_type": "Pharmacogenomics - 6 Gene Panel",
                "clinical_version": "CPIC v2.0+"
            },
            "patient_info": {
                "patient_id": "PT-001",
                "age": 45,
                "gender": "Not specified",
                "medical_record_status": "Active"
            },
            "genetic_analysis": {
                "genes_analyzed": [
                    {"gene_name": "CYP2D6", "chromosome": "22", "genotype": "*1/*2", "phenotype": "Intermediate Metabolizer"},
                    {"gene_name": "CYP2C9", "chromosome": "10", "genotype": "*1/*2", "phenotype": "Intermediate Metabolizer"},
                    {"gene_name": "CYP2C19", "chromosome": "10", "genotype": "*1/*2", "phenotype": "Intermediate Metabolizer"},
                    {"gene_name": "TPMT", "chromosome": "6", "genotype": "*1/*2", "phenotype": "Intermediate Activity"},
                    {"gene_name": "SLCO1B1", "chromosome": "12", "genotype": "*1/*2", "phenotype": "Decreased Function"},
                    {"gene_name": "DPYD", "chromosome": "1", "genotype": "*1/*2", "phenotype": "Decreased Activity"}
                ]
            },
            "drug_analysis": {
                "medications_analyzed": [
                    {"drug_name": "CODEINE", "primary_metabolizer": "CYP2D6", "risk_level": "MODERATE", "recommendation": "Adjust Dosage"},
                    {"drug_name": "WARFARIN", "primary_metabolizer": "CYP2C9", "risk_level": "MODERATE", "recommendation": "Adjust Dosage"},
                    {"drug_name": "CLOPIDOGREL", "primary_metabolizer": "CYP2C19", "risk_level": "MODERATE", "recommendation": "Alternative Preferred"},
                    {"drug_name": "SIMVASTATIN", "primary_metabolizer": "SLCO1B1", "risk_level": "MODERATE", "recommendation": "Reduce Dose"},
                    {"drug_name": "AZATHIOPRINE", "primary_metabolizer": "TPMT", "risk_level": "MODERATE", "recommendation": "Adjust Dosage"},
                    {"drug_name": "FLUOROURACIL", "primary_metabolizer": "DPYD", "risk_level": "MODERATE", "recommendation": "Adjust Dosage"}
                ]
            },
            "clinical_recommendations": [
                {"drug": "CODEINE", "recommendation": "CYP2D6 IM - Consider higher dose or shorter intervals", "cpic_level": "2A"},
                {"drug": "WARFARIN", "recommendation": "CYP2C9 IM - Reduce initial dose to 5-7 mg daily", "cpic_level": "1A"},
                {"drug": "CLOPIDOGREL", "recommendation": "CYP2C19 IM - Consider prasugrel or ticagrelor", "cpic_level": "2B"},
                {"drug": "SIMVASTATIN", "recommendation": "SLCO1B1 decreased - Max 5 mg daily", "cpic_level": "2B"},
                {"drug": "AZATHIOPRINE", "recommendation": "TPMT IM - Reduce dose 25-50%", "cpic_level": "1A"},
                {"drug": "FLUOROURACIL", "recommendation": "DPYD decreased - Reduce dose 25-50%", "cpic_level": "2A"}
            ],
            "monitoring_guidelines": {
                "warfarin_monitoring": {
                    "applies": True,
                    "target_inr_range": "2.0-3.0",
                    "monitoring_schedule": "Baseline, 2-7 days, weekly x 1-2 weeks, then every 1-4 weeks"
                }
            },
            "analysis_quality": {
                "genes_with_adequate_coverage": 1,
                "variants_detected": 2,
                "analysis_status": "Complete",
                "quality_flags": []
            }
        }
        
        # Display JSON with st.json()
        st.json(analysis_json)
        
        # Store JSON string in session state for copy button
        json_str = json.dumps(analysis_json, indent=2)
        st.session_state.json_to_copy = json_str
        
        # Button row for download and copy
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        
        col_download, col_copy, col_format = st.columns([1, 1, 2])
        
        with col_download:
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"analysis_PG-2026-02-20-001.json",
                mime="application/json",
                use_container_width=True,
                help="Download the analysis results as a JSON file"
            )
        
        with col_copy:
            # Copy to clipboard button using Streamlit
            if st.button("📋 Copy JSON", use_container_width=True, help="Copy JSON to clipboard"):
                import subprocess
                import platform
                
                try:
                    # Copy to clipboard using system command
                    if platform.system() == "Windows":
                        # Windows: use clip command
                        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                        process.communicate(json_str.encode('utf-8'))
                    elif platform.system() == "Darwin":
                        # macOS: use pbcopy
                        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                        process.communicate(json_str.encode('utf-8'))
                    else:
                        # Linux: use xclip or xsel
                        try:
                            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                            process.communicate(json_str.encode('utf-8'))
                        except FileNotFoundError:
                            process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                            process.communicate(json_str.encode('utf-8'))
                    
                    st.success("✅ JSON copied to clipboard!")
                except Exception as e:
                    st.warning(f"Could not copy to clipboard: {str(e)}")
                    st.code(json_str, language='json')
        
        with col_format:
            st.markdown("""
            <div style="padding: 10px; background-color: #F8F9FA; border-radius: 4px; border: 1px solid #E0E0E0; font-size: 13px; color: #666;">
                <strong>Export Format:</strong> JSON (v1.0)<br>
                <strong>Records:</strong> 1 analysis<br>
                <strong>File Size:</strong> ~2 KB
            </div>
            """, unsafe_allow_html=True)

else:
    # Show placeholder when no analysis has been run
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h2>📊 Analysis Results</h2><p>Pharmacogenomics findings and recommendations</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    **No analysis results yet.**
    
    Click "Start Analysis" to run pharmacogenomics analysis on the uploaded genomic data.
    Results will appear here with:
    - Genotype/Phenotype interpretations
    - Risk assessments per drug
    - Clinical recommendations
    - AI-generated explanations
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Detailed Results", "Recommendations", "Reports", "JSON Output"])

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Genes Analyzed</div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Variants Found</div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Drugs Analyzed</div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Clinical Recommendations:** Analysis results pending...")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Report Generation**")
        report_format = st.selectbox(
            "Report Format",
            ["PDF", "HTML", "Text"],
            help="Select output format",
            label_visibility="collapsed"
        )
        download_btn = st.button("📥 Download Report", use_container_width=True, disabled=True)
    
    with col2:
        st.markdown("**Report Templates**")
        template = st.selectbox(
            "Template",
            ["Clinical Summary", "Detailed Analysis", "Executive Summary"],
            help="Choose report template",
            label_visibility="collapsed"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown("""
    <div class="card" style="padding-bottom: 10px;">
        <h3 style="margin-top: 0; color: #003D7A; font-size: 18px;">📋 Structured Analysis Output</h3>
        <p style="color: #666; margin-bottom: 15px;">Complete analysis results in JSON format for integration with other systems and clinical workflows.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card" style="text-align: center; min-height: 300px; display: flex; align-items: center; justify-content: center;">
        <div>
            <p style="color: #999; font-size: 16px;">JSON output will appear here after analysis is complete.</p>
            <p style="color: #CCC; font-size: 14px;">Click "Analyze Patient" to generate structured output.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>
    <strong>PharmaGuard v1.0</strong> | AI-Assisted Pharmacogenomic Clinical Decision Support<br>
    © 2026 RIFT Clinical Systems | Based on CPIC Guidelines and Latest Pharmacogenomics Evidence<br>
    <em>For Research and Clinical Use Only | Not Intended for diagnosis or treatment decisions without professional oversight</em>
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INFO SECTION IN SIDEBAR
# ============================================================================
with st.sidebar:
    st.divider()
    st.markdown("### 📚 Resources")
    if st.button("📖 CPIC Guidelines"):
        st.info("Link to CPIC (cpicpgx.org)")
    
    if st.button("❓ Help & Documentation"):
        st.info("Opens help documentation")
    
    st.divider()
    st.markdown("### 🎯 Quick Start")
    st.caption("""
    1. Enter patient information
    2. Upload VCF or select sample
    3. Choose medications
    4. Click "Start Analysis"
    5. Review results & recommendations
    """)
