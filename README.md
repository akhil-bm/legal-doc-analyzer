# 📄 Legal Document Analyzer

> A sophisticated multi-agent AI system for analyzing legal contracts and agreements using Google's Agent Development Kit (ADK) and Vertex AI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google)](https://google.github.io/adk-docs/)

## 🌟 Overview

The Legal Document Analyzer is an intelligent, multi-agent system that automatically analyzes legal documents (contracts, NDAs, agreements) and provides comprehensive insights including risk assessment, obligation extraction, financial terms analysis, and actionable recommendations.

### ✨ Key Features

- **📄 Multi-Format Support**: Analyze plain text or PDF documents seamlessly
- **🔄 Contract Comparison**: Side-by-side comparison of two contracts with detailed insights
- **⚖️ Risk Scoring**: Automated risk assessment on a 1-10 scale with severity levels
- **🎯 Clause Detection**: Identifies 9 types of key clauses (Termination, Liability, Confidentiality, etc.)
- **💰 Financial Analysis**: Extracts payment terms, amounts, and schedules
- **🤖 Multi-Agent Architecture**: 4 specialized agents working in sequence (Extractor → Identifier → Risk Analyzer → Reporter)
- **📊 Professional Reports**: Generates structured JSON reports with comprehensive analysis

## 🏗️ Architecture

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

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account
- Vertex AI API enabled
- Google ADK library

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akhil-bm/legal-doc-analyzer.git
   cd legal-doc-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cd legal_analyzer
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google Cloud project details:
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=true
   GOOGLE_CLOUD_PROJECT=your-project-id-here
   GOOGLE_CLOUD_LOCATION=us-central1
   MODEL_NAME=gemini-2.0-flash-exp
   ```

5. **Authenticate with Google Cloud**
   ```bash
   gcloud auth application-default login
   ```

## 💻 Usage

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

## ⚠️ Rate Limits & Troubleshooting

### Understanding Rate Limits

Vertex AI enforces request rate limits to ensure fair usage and system stability:
- **Free Tier**: ~60 requests per minute
- **Standard Tier**: Higher limits available on request
- **Each GCP project**: Has independent quotas

### Rate Limit Error (429 RESOURCE_EXHAUSTED)

If you encounter this error:

```json
{"error": "429 RESOURCE_EXHAUSTED"}
```

**This is normal and temporary!** Here's what it means and how to handle it:

#### Cause
- You've exceeded the requests-per-minute limit for your GCP project
- Common during extensive testing or rapid successive queries
- Rate limits are per-project, not global

#### Solutions

**1. Wait and Retry (Quickest)**
```bash
# Wait 5-10 minutes for rate limit to reset
# Then try your query again
```

**2. Check Your Quota**
- Visit [Google Cloud Console → IAM & Admin → Quotas](https://console.cloud.google.com/iam-admin/quotas)
- Search for "Vertex AI API"
- View current usage and limits

**3. Request Quota Increase**
For production use or extensive testing:
- Go to GCP Console → Quotas
- Select "Vertex AI API requests per minute"
- Click "Edit Quotas" and request higher limits
- Approval typically takes 24-48 hours

**4. Use Alternative Model**
If you need immediate access, try a different model with separate quotas:

Edit your `.env` file:
```bash
MODEL_NAME=gemini-1.5-flash  # Alternative model
```

### For Reviewers & Testers

**Good news!** If you're testing this agent:
- ✅ Each GCP project has **independent rate limits**
- ✅ Fresh projects start with **unused quotas**
- ✅ Standard testing (5-10 queries) **won't hit limits**
- ✅ You're using **your own credentials**, not affected by others' usage

**Expected Usage:**
```
Light testing:    2-5 queries   → No issues ✅
Moderate testing: 10-15 queries → No issues ✅
Heavy testing:    50+ queries   → May hit limit ⚠️ (wait 5 min)
```

### Best Practices

1. **Space out your queries** - Wait 1-2 seconds between tests
2. **Use test cases** - Pre-written test cases in `test_cases/` folder
3. **Monitor usage** - Check GCP Console for quota status
4. **Plan for production** - Request quota increases before deployment

### Still Having Issues?

- Check [Vertex AI Error Codes](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429)
- Verify your GCP credentials: `gcloud auth application-default login`
- Ensure Vertex AI API is enabled in your project
- Check project billing status

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

## 🤝 Contributing

This project was developed as part of a Google ADK competition. Contributions, issues, and feature requests are welcome!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Akhil BM**
- GitHub: [@akhil-bm](https://github.com/akhil-bm)
- Repository: [legal-doc-analyzer](https://github.com/akhil-bm/legal-doc-analyzer)

## 🙏 Acknowledgments

- Google ADK Team for the amazing framework
- Vertex AI for powerful AI capabilities
- Google Cloud Platform for infrastructure

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review [Google ADK Documentation](https://google.github.io/adk-docs/)
3. Open an issue in this repository
4. Check [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

---

**Built with ❤️ using Google ADK and Vertex AI**