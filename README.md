# 📄 Legal Document Analyzer

> A sophisticated multi-agent AI system for analyzing legal contracts and agreements using Google's Agent Development Kit (ADK) and Vertex AI.


##  Overview

The Legal Document Analyzer is an intelligent, multi-agent system that automatically analyzes legal documents (contracts, NDAs, agreements) and provides comprehensive insights including risk assessment, obligation extraction, financial terms analysis, and actionable recommendations.

###  Key Features

- **Multi-Format Support**: Analyze plain text or PDF documents seamlessly
- **Contract Comparison**: Side-by-side comparison of two contracts with detailed insights
- **Risk Scoring**: Automated risk assessment on a 1-10 scale with severity levels
- **Clause Detection**: Identifies 9 types of key clauses (Termination, Liability, Confidentiality, etc.)
- **Financial Analysis**: Extracts payment terms, amounts, and schedules
- **Multi-Agent Architecture**: 4 specialized agents working in sequence (Extractor → Identifier → Risk Analyzer → Reporter)
- **Professional Reports**: Generates structured JSON reports with comprehensive analysis

##  Architecture

The system uses a **sequential multi-agent workflow** with four specialized agents:

```
Document Input
    ↓
[1] Document Extractor Agent
    ↓ (parties, dates, obligations, financial terms)
[2] Clause Identifier Agent  
    ↓ (9 clause types: termination, liability, confidentiality, etc.)
[3] Risk Analyzer Agent
    ↓ (risk score 1-10, severity level, flags)
[4] Reporter Agent
    ↓ (final structured report)
Final Analysis Report
```

### Supported Clause Types
- Termination clauses
- Limitation of liability
- Confidentiality/NDA
- Intellectual property rights
- Payment terms
- Warranties
- Indemnification
- Dispute resolution
- Non-compete

##  Getting Started

### Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account
- Vertex AI API enabled
- Google ADK library

### Installation

1. **Clone the repository**
   
   git clone https://github.com/yourusername/legal-doc-analyzer.git
   cd legal-doc-analyzer
   

2. **Create virtual environment**
   bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   

3. **Install dependencies**
   bash
   pip install -r requirements.txt
   

4. **Set up environment variables**
   bash
   cd legal_analyzer
   cp .env.example .env
   
   
   Edit `.env` and add your Google Cloud project details:
   bash
   GOOGLE_GENAI_USE_VERTEXAI=true
   GOOGLE_CLOUD_PROJECT=adk-finops
   GOOGLE_CLOUD_LOCATION=us-central1
   MODEL_NAME=gemini-2.0-flash-exp
   

5. **Authenticate with Google Cloud**
   bash
   gcloud auth application-default login
   

##  Usage

### Single Document Analysis

```bash
cd legal_analyzer
python agent.py analyze
```

When prompted, choose option 1 and enter your document text or path to PDF file.

**Example Output:**
```json
{
  "document_summary": {
    "parties": ["Company A", "Company B"],
    "effective_date": "2025-01-01",
    "contract_type": "Service Agreement"
  },
  "risk_assessment": {
    "overall_risk_score": 6,
    "severity": "Medium",
    "flags": ["High liability cap", "Long confidentiality period"]
  },
  "clauses_identified": {
    "Termination": "30 days written notice",
    "Liability": "$100,000 cap"
  },
  "recommendations": [
    "Review liability cap amount",
    "Clarify IP ownership terms"
  ]
}
```

### Contract Comparison

```bash
cd legal_analyzer
python agent.py compare
```

Provide two contracts to compare side-by-side with detailed analysis of differences.

### Test Cases

The repository includes 5 diverse test cases demonstrating different contract types:

```bash
test_cases/
├── test_case_1_nda.txt                   # Non-Disclosure Agreement
├── test_case_2_vendor_service.txt        # Vendor Service Agreement
├── test_case_3_commercial_lease.txt      # Commercial Lease Agreement
├── test_case_4_partnership.txt           # Partnership Agreement
└── test_case_5_software_license.txt      # Software License Agreement
```

Run any test case:
```bash
cat test_cases/test_case_1_nda.txt
# Copy output and paste when prompted by agent
```

## 📁 Project Structure

```
legal-doc-analyzer/
├── legal_analyzer/
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # Main agent implementation
│   ├── .env.example          # Environment template
│   └── .env                  # Your config (not in Git)
├── test_cases/               # 5 diverse test contracts
├── requirements.txt          # Python dependencies
├── .gitignore               # Git exclusions
└── README.md                # This file
```

## 🧪 Testing

To test the system:

1. Start with a simple contract (test_case_1_nda.txt)
2. Progress to more complex agreements
3. Try the comparison feature with two different contracts
4. Test PDF upload functionality

## 🛠️ Technologies Used

- **Google ADK** - Agent Development Kit for multi-agent orchestration
- **Vertex AI** - Google's unified AI platform
- **Gemini 2.0 Flash** - Large language model
- **Python 3.10+** - Programming language
- **PyPDF2** - PDF text extraction

## 🔐 Security & Privacy

- API keys and credentials are never committed to Git (via `.gitignore`)
- All sensitive data stored in `.env` file
- Example configuration provided in `.env.example`




**Your Name**
- GitHub: [@akhil-bm](https://github.com/akhil-bm)
