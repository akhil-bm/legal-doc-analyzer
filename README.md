# 📄 Legal Document Analyzer

> A sophisticated multi-agent AI system for analyzing legal contracts and agreements using Google's Agent Development Kit (ADK) and Vertex AI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google)](https://google.github.io/adk-docs/)

## 🌟 Overview

The Legal Document Analyzer is an intelligent, multi-agent system that automatically analyzes legal documents (contracts, NDAs, agreements) and provides comprehensive insights including risk assessment, obligation extraction, financial terms analysis, and actionable recommendations.

This agent uses a "Divide and Conquer" strategy, breaking down the complex task of legal analysis into smaller, manageable steps, allowing a fast and efficient model (`gemini-2.0-flash`) to perform a deep and accurate analysis.

### ✨ Key Features

- **📄 Multi-Format Support**: Analyze plain text or PDF documents seamlessly.
- **🔄 Contract Comparison**: Side-by-side comparison of two contracts with high-level insights.
- **⚖️ AI-Powered Risk Scoring**: Automated risk assessment on a 1-10 scale with severity levels.
- **🎯 AI-Powered Risk Identification**: Identifies potential risks, ambiguous language, and one-sided clauses.
- **💰 Financial Analysis**: Extracts payment terms, amounts, and schedules.
- **🤖 Multi-Agent Architecture**: A 5-step sequential workflow for detailed analysis (Extractor → Party → Financial → Risk → Reporter).
- **📊 Professional Reports**: Generates clean, human-readable Markdown reports.

## 🏗️ Architecture

The system uses a **sequential multi-agent workflow** with five specialized agents operating in a "Divide and Conquer" pipeline:

Document Input (Text or PDF) ↓ [1] Document Extractor Agent ↓ (Cleaned Text) [2] Party Identifier Agent ↓ (Parties JSON) [3] Financial Analyst Agent ↓ (Financials JSON) [4] Risk Analyst Agent ↓ (Risk JSON) [5] Report Generator Agent ↓ (Formatted Markdown Report) Final Analysis Report

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account
- Vertex AI API enabled
- Google ADK library

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/akhil-bm/legal-doc-analyzer.git
    cd legal-doc-analyzer
    ```

2.  **Create virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**
    ```bash
    cd legal_analyzer
    cp .env.example .env
    ```
    
    Edit `.env` and add your Google Cloud project details:
    ```bash
    GOOGLE_GENAI_USE_VERTEXAI=true
    GOOGLE_CLOUD_PROJECT=your-project-id-here
    GOOGLE_CLOUD_LOCATION=us-central1
    MODEL_NAME=gemini-2.0-flash
    ```

5.  **Authenticate with Google Cloud**
    ```bash
    gcloud auth application-default login
    ```

## 💻 Usage

The primary way to run the agent is through the ADK web interface.

1.  **Start the web server**
    From the `legal_analyzer` directory (where your `agent.py` is):
    ```bash
    adk web
    ```
    
2.  **Open the interface**
    Open your browser and go to the URL shown in the terminal (usually `http://127.0.0.1:8080`).

### Single Document Analysis

1.  From the `adk web` UI, make sure the `legal_document_analyzer` agent is selected.
2.  You can either:
    * **Paste Text:** Copy the text from a `test_cases/` file and paste it into the chat box.
    * **Upload PDF:** Click the paperclip 📎 icon and upload a PDF file.
3.  Press enter. The agent will run through all 5 steps and present the final, formatted report.

**Example Output:**
(Note: The output is now clean Markdown, not JSON)

```markdown
## 📄 LEGAL DOCUMENT ANALYSIS REPORT
---

### 🎯 EXECUTIVE SUMMARY
* **Risk Level:** Low
* **Risk Score:** 3/10
* **Analysis Date:** 2025-11-02 15:30:00

### 📋 KEY PARTIES & OBLIGATIONS
* **CloudTech Solutions Inc.:** Primary obligations include providing services and maintaining confidentiality.
* **Global Retail Enterprises LLC:** Primary obligations include making payments and maintaining confidentiality.

### 💰 FINANCIAL TERMS
* Total fee of $450,000
* $90,000 Initial Deposit
* $135,000 Phase 1 Completion
* $135,000 Phase 2 Completion
* $90,000 Phase 3 & Final Delivery
* Payment due 15 business days of invoice
* Late payment interest charge of 1.5% per month

### ⚠️  IDENTIFIED RISKS
1.  **Document includes standard clauses (Liability, Indemnification, etc.)** [Low Severity]
2.  **Termination for convenience clause requires a long 60-day notice.** [Medium Severity]

### 💡 RECOMMENDATIONS
1.  Based on the risk score of **3**, this document is considered **Low risk**.
2.  Review the identified risks, especially any missing critical clauses.
3.  Always have legal counsel review contracts before execution.

---
> **Disclaimer:** This is an automated analysis. Please consult with legal counsel for professional advice before making any decisions.
Contract Comparison
In the adk web UI, paste your comparison request in the following format:

Compare these contracts:

CONTRACT A:
[paste first contract text here]

CONTRACT B:
[paste second contract text here]
The contract_comparison_agent will be triggered and will return a side-by-side Markdown report.

Test Cases
The repository includes 5 diverse test cases demonstrating different contract types:

test_cases/
├── test_case_1_nda.txt              # Non-Disclosure Agreement
├── test_case_2_vendor_service.txt   # Vendor Service Agreement
├── test_case_3_commercial_lease.txt   # Commercial Lease Agreement
├── test_case_4_partnership.txt        # Partnership Agreement
└── test_case_5_software_license.txt   # Software License Agreement
Run any test case:

Bash

# Open any test case file, copy its contents, and paste it into the adk web UI
📁 Project Structure
legal-doc-analyzer/
├── legal_analyzer/
│   ├── __init__.py         # Package initialization
│   ├── agent.py            # Main agent implementation
│   ├── .env.example        # Environment template
│   └── .env                # Your config (not in Git)
├── test_cases/             # 5 diverse test contracts
├── requirements.txt        # Python dependencies
├── .gitignore              # Git exclusions
└── README.md               # This file
⚠️ Rate Limits & Troubleshooting
Understanding Rate Limits
Vertex AI enforces request rate limits to ensure fair usage and system stability:

Free Tier: ~60 requests per minute

Standard Tier: Higher limits available on request

Each GCP project: Has independent quotas

Rate Limit Error (429 RESOURCE_EXHAUSTED)
If you encounter this error:

JSON

{"error": "429 RESOURCE_EXHAUSTED"}
This is normal and temporary! Here's what it means and how to handle it:

Cause
You've exceeded the requests-per-minute limit for your GCP project

Common during extensive testing or rapid successive queries

Rate limits are per-project, not global

Solutions
1. Wait and Retry (Quickest)

Bash

# Wait 5-10 minutes for rate limit to reset
# Then try your query again
2. Check Your Quota

Visit Google Cloud Console → IAM & Admin → Quotas

Search for "Vertex AI API"

View current usage and limits

3. Request Quota Increase For production use or extensive testing:

Go to GCP Console → Quotas

Select "Vertex AI API requests per minute"

Click "Edit Quotas" and request higher limits

Approval typically takes 24-48 hours

For Reviewers & Testers
Good news! If you're testing this agent:

✅ Each GCP project has independent rate limits

✅ Fresh projects start with unused quotas

✅ Standard testing (5-10 queries) won't hit limits

✅ You're using your own credentials, not affected by others' usage

Expected Usage:

Light testing:     2-5 queries   → No issues ✅
Moderate testing: 10-15 queries  → No issues ✅
Heavy testing:     50+ queries   → May hit limit ⚠️ (wait 5 min)
Still Having Issues?
Check Vertex AI Error Codes

Verify your GCP credentials: gcloud auth application-default login

Ensure Vertex AI API is enabled in your project

Check project billing status

🛠️ Technologies Used
Google ADK - Agent Development Kit for multi-agent orchestration

Vertex AI - Google's unified AI platform

Gemini 2.0 Flash - Large language model

Python 3.10+ - Programming language

pypdf - PDF text extraction

🔐 Security & Privacy
API keys and credentials are never committed to Git (via .gitignore)

All sensitive data stored in .env file

Example configuration provided in .env.example

👤 Author
Akhil BM

GitHub: @akhil-bm

Repository: legal-doc-analyzer
