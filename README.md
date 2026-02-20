🧬 PharmaGuard
AI‑Powered Pharmacogenomic Risk Assessment System (CPIC‑Aligned Clinical Decision Support)
PharmaGuard is an AI-driven pharmacogenomics platform that analyzes patient genetic profiles and predicts drug safety, toxicity risk, and dosing recommendations based on CPIC (Clinical Pharmacogenetics Implementation Consortium) guidelines.

It enables precision medicine by transforming raw genetic data into actionable clinical insights.

🔗 Live Demo
👉 https://pharmaguard-434k.onrender.com/

🎥 LinkedIn Demo Video
👉 https://www.linkedin.com/posts/madhugna-yelchuri-97b595338_riftxpwioi-hackathon-24hourchallenge-activity-7430422321384996865-avQw?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAFTNvC8BmyPfdO7tTdWsSkbBKip8D5H4zKI&utm_campaign=copy_link

🏗 Architecture Overview
🔄 System Workflow
Patient genetic data input (VCF / structured JSON)

Variant extraction & gene normalization

CPIC-based gene–drug mapping engine

Phenotype interpretation layer

Risk classification (Safe / Caution / High Risk)

Structured clinical recommendation output

Streamlit-based visualization dashboard

🧠 Core Modules
Gene–Drug Mapping Engine

CPIC Rules Engine

6‑Gene Validation System

Risk Scoring Module

JSON Clinical Output Generator

Frontend Visualization Layer

🛠 Tech Stack
👨‍💻 Programming
Python

🌐 Frameworks
Streamlit (Frontend)

FastAPI (API layer – if applicable)

🧬 Genomics & Clinical Data
CPIC Guidelines

PharmGKB Reference Data

📊 Libraries
Pandas

JSON

Pydantic (if used)

🔧 Tools
Git & GitHub

VS Code

Virtual Environment (venv)

💻 Installation Instructions
1️⃣ Clone Repository
git clone https://github.com/pallavikundapur23-hub/Pharmaguard.git
cd Pharmaguard
2️⃣ Create Virtual Environment
python -m venv venv
3️⃣ Activate Environment
Windows:

venv\Scripts\activate
Mac/Linux:

source venv/bin/activate
4️⃣ Install Dependencies
pip install -r requirements.txt
5️⃣ Run Application
streamlit run app.py
🔌 API Documentation
🔹 Endpoint: Analyze Drug Risk
POST /analyze

📥 Request Body
{
  "patient_id": "PATIENT_001",
  "genes": {
    "CYP2D6": "*1/*1",
    "CYP2C19": "*1/*2",
    "CYP2C9": "*1/*1",
    "TPMT": "*1/*1",
    "SLCO1B1": "*1/*5",
    "DPYD": "*1/*1"
  },
  "drugs": ["Codeine", "Clopidogrel", "Warfarin"]
}
📤 Response Example
{
  "drug": "Codeine",
  "risk_label": "High Risk",
  "severity": "Critical",
  "recommendation": "Avoid use due to CYP2D6 Ultra-Rapid Metabolizer phenotype."
}
🧪 Usage Examples
Example 1 – Codeine Toxicity
Input: CYP2D6 Ultra-Rapid Metabolizer
Output: High risk → Avoid use

Example 2 – Clopidogrel
Input: CYP2C19 Normal Metabolizer
Output: Safe → Standard dosing

Example 3 – 6-Gene Panel Validation
Validated Genes:

CYP2D6

CYP2C19

CYP2C9

TPMT

SLCO1B1

DPYD

🚀 Key Features
✔ CPIC‑Aligned Clinical Recommendations
✔ Automated Gene–Drug Interaction Mapping
✔ 6‑Gene Pharmacogenomic Panel Support
✔ Structured Clinical JSON Output
✔ Risk Stratification Engine
✔ Interactive Dashboard

🔮 Future Improvements
Expand drug coverage

Integrate EHR systems

Deploy REST API for hospital use

Add machine learning optimization

Clinical validation studies

👥 Team Members
Pallavi P Kundapur – Backend Development & API Integration

Charishma P D – CPIC Mapping & Risk Logic Implementation

Madhugna Yelchuri– Gene Validation & JSON Structuring
