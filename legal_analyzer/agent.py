"""
Legal Document Analyzer Agent (Gemini-2.0-Flash Version)

A multi-agent system that analyzes legal documents by breaking the
problem into small, sequential steps that the 'flash' model can handle.

**Version 3: With Markdown Formatting and clean final output**
"""

import os
import re
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import ToolContext
from pypdf import PdfReader

# Load environment variables
load_dotenv()


# ============================================================================
# PDF PROCESSING UTILITIES 
# ============================================================================

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extracts text from PDF file content."""
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


# ============================================================================
# DOCUMENT EXTRACTOR TOOL 
# ============================================================================

def extract_document_text(document_text: Optional[str] = None, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """Extracts and cleans text from a legal document (text or PDF format)."""
    extracted_text = ""
    source_type = "text"
    
    if tool_context:
        try:
            artifacts = tool_context.list_artifacts()
            pdf_files = [f for f in artifacts if f.lower().endswith('.pdf')]
            
            if pdf_files:
                pdf_filename = pdf_files[0]
                print(f"Processing PDF file: {pdf_filename}")
                pdf_artifact = tool_context.load_artifact(pdf_filename)
                
                if pdf_artifact and hasattr(pdf_artifact, 'inline_data'):
                    pdf_bytes = pdf_artifact.inline_data.data
                    extracted_text = extract_text_from_pdf(pdf_bytes)
                    source_type = "pdf"
                    print(f"Extracted {len(extracted_text)} characters from PDF")
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            pass
    
    if not extracted_text and document_text:
        extracted_text = document_text
        source_type = "text"
    
    if not extracted_text or len(extracted_text.strip()) < 50:
        return {
            "status": "error",
            "message": "Document text is too short or empty. Please provide a valid legal document (text or PDF).",
            "cleaned_text": "",
        }
    
    cleaned = extracted_text.strip()
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n+', '\n', cleaned)
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
    
    return {
        "status": "success",
        "message": f"Document extracted and cleaned successfully from {source_type.upper()}",
        "cleaned_text": cleaned,
        "source_type": source_type,
        "extracted_at": datetime.now().isoformat()
    }


# ============================================================================
# AGENT DEFINITIONS ("Divide and Conquer" with Flash)
# ============================================================================

# Agent 1: Document Extractor (Unchanged)
extractor_agent = Agent(
    name="document_extractor",
    model="gemini-2.0-flash",
    description="Extracts and cleans text from legal documents (text or PDF format)",
    instruction="""You are a document extraction specialist with PDF processing capabilities.
    1. Check for PDF files or text input.
    2. Call the extract_document_text function.
    3. Return the extraction result exactly as provided by the function.
    4. Do not add any commentary or additional text.""",
    tools=[extract_document_text],
    output_key="extraction_result"
)

# Agent 2: Party Identifier (UPDATED PROMPT)
party_agent = Agent(
    name="party_identifier_agent",
    model="gemini-2.0-flash",
    description="Identifies the main parties from the document text",
    instruction="""You are a legal analyst. You will receive an 'extraction_result'.
    Look at the 'extraction_result.cleaned_text'.
    Identify ALL main legal parties of the agreement (e.g., "CloudTech Solutions Inc.", "Global Retail Enterprises LLC", "Jessica Williams").
    Do NOT include individual signatory names *unless* they are a named party (like in a partnership agreement).
    
    You MUST return ONLY a valid JSON object in this format:
    {"parties": ["Full Party Name 1", "Full Party Name 2", "...etc"]}
    """,
    output_key="party_result"
)

# Agent 3: Financial Analyst (Unchanged)
financial_agent = Agent(
    name="financial_agent",
    model="gemini-2.0-flash",
    description="Identifies key financial terms from the document text",
    instruction="""You are a financial analyst. You will receive an 'extraction_result'.
    Look at the 'extraction_result.cleaned_text'.
    Identify the key financial terms, like total contract value and payment schedule.
    
    You MUST return ONLY a valid JSON object in this format:
    {"financial_terms": ["Total fee of $450,000", "$90,000 Initial Deposit", "Payment due 15 business days of invoice"]}
    """,
    output_key="financial_result"
)

# Agent 4: Risk Analyst 
risk_agent = Agent(
    name="risk_analyst_agent",
    model="gemini-2.0-flash",
    description="Identifies risks and missing clauses from the text",
    instruction="""You are a risk analyst. You will receive an 'extraction_result'.
    Look at the 'extraction_result.cleaned_text'.
    1. Identify any present or missing critical clauses: "Limitation of Liability", "Indemnification", "Dispute Resolution", "Termination", "Confidentiality".
    2. Assign a risk score (0-10) and level (Low, Medium, High). A missing 'Limitation of Liability' is a high risk (e.g., 8/10). A standard doc with all clauses is low (e.g., 2/10).
    3. List the top 2-3 risks.
    
    You MUST return ONLY a valid JSON object in this format:
    {
      "risks": [
        {"severity": "Low", "description": "Document includes standard clauses (Liability, Indemnification, etc.)"},
        {"severity": "Medium", "description": "Termination for convenience clause requires a long 60-day notice."}
      ],
      "risk_score": 3,
      "risk_level": "Low"
    }
    """,
    output_key="risk_result"
)

# Agent 5: Report Generator (UPDATED with Markdown)
report_generator_agent = Agent(
    name="report_generator_agent",
    model="gemini-2.0-flash",
    description="Generates the final report by combining all analysis parts",
    instruction=f"""You are a final report generator. You will receive several JSON inputs: 'party_result', 'financial_result', and 'risk_result'.
    Your job is to assemble these pieces into a single, comprehensive **Markdown** report for the user.
    Do NOT make up new information. Only use the data provided in the inputs.
    Use headings (`##`), bolding (`**...**`), and bullet points (`*`) for clarity.
    
    You MUST format your *entire* response as the final report. Do not add any other text or JSON.

## 📄 LEGAL DOCUMENT ANALYSIS REPORT
---

### 🎯 EXECUTIVE SUMMARY
* **Risk Level:** [Get from risk_result.risk_level]
* **Risk Score:** [Get from risk_result.risk_score]/10
* **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📋 KEY PARTIES & OBLIGATIONS
Based on the analysis, the primary parties and their general obligations are:

[Loop through party_result.parties]
* **[Party Name]:** Primary obligations include [e.g., "providing services" or "making payments"] and maintaining confidentiality.

### 💰 FINANCIAL TERMS
[List each item from financial_result.financial_terms as a bullet point]
* [Item 1]
* [Item 2]

### ⚠️  IDENTIFIED RISKS
[List each risk from risk_result.risks as a numbered item]
1.  **[risk.description]** [[risk.severity] Severity]

### 💡 RECOMMENDATIONS
1.  Based on the risk score of **[risk_result.risk_score]**, this document is considered **[risk_result.risk_level] risk**.
2.  Review the identified risks, especially any missing critical clauses.
3.  Always have legal counsel review contracts before execution.

---
> **Disclaimer:** This is an automated analysis. Please consult with legal counsel for professional advice before making any decisions.
""",
    output_key="final_report"
)


# Agent 6: Contract Comparison Agent (UPDATED with Markdown)
comparison_agent = Agent(
    name="contract_comparison_agent",
    model="gemini-2.0-flash",
    description="Compares two legal documents side-by-side (Flash version)",
    instruction="""You are a contract comparison specialist. 

When a user provides TWO contracts to compare in this format:
   "Compare these contracts:
   
   CONTRACT A:
   [first contract text]
   
   CONTRACT B:
   [second contract text]"

You MUST:
1.  Parse the text for 'CONTRACT A' and 'CONTRACT B'.
2.  Perform a **high-level, brief** analysis.
3.  Generate a simple **Markdown** report using headings, tables, and bolding.

**OUTPUT FORMAT (CRITICAL):**
You MUST format your *entire* response as the final report. Do not add any other text.

## 🔄 CONTRACT COMPARISON REPORT (Flash Analysis)
---

### 📊 HIGH-LEVEL COMPARISON

| Metric          | Document A                     | Document B                     |
|:----------------|:-------------------------------|:-------------------------------|
| **Est. Risk** | **[Score A]/10 ([Level A])** | **[Score B]/10 ([Level B])** |
| Est. Value      | [Value A, or "Not specified"]  | [Value B, or "Not specified"]  |

### ⚖️  KEY OBSERVATIONS
* [Brief note on risk. e.g., "Doc A seems lower risk as it includes a Liability clause."]
* [Brief note on clauses. e.g., "Both docs contain Confidentiality clauses."]
* [Brief note on financials. e.g., "Doc B has a higher contract value."]

### 💡 RECOMMENDATION
1.  Based on this brief analysis, **[e.g., "Document A appears more favorable"]**.
2.  Please review [e.g., "the missing clauses in Document B"].
3.  Always consult with legal counsel for a full professional review.

---
> **Disclaimer:** This is an automated, high-level analysis.
""",
)

# ============================================================================
# NEW AGENT: FINAL RESPONDER
# This agent's only job is to "unpack" the report from the workflow state.
# ============================================================================
final_responder_agent = Agent(
    name="final_responder_agent",
    model="gemini-2.0-flash",
    description="Presents the final formatted report string to the user",
    instruction="""You will be given a pre-formatted string. 
    This string is the final report.
    You MUST output this string EXACTLY as you receive it.
    Do not add any text, commentary, or formatting.
    Just repeat the string.""",
    output_key="final_formatted_report"
)


# ============================================================================
# SEQUENTIAL WORKFLOW 
# ============================================================================

legal_analysis_workflow = SequentialAgent(
    name="legal_analysis_workflow",
    description="Sequential workflow for analyzing legal documents using a 'divide and conquer' flash-model approach.",
    sub_agents=[
        extractor_agent,
        party_agent,
        financial_agent,
        risk_agent,
        report_generator_agent  # This is the 5th and final step of the workflow
    ]
    # The output of this workflow will be a dict containing "final_report"
)


# ============================================================================
# ROOT AGENT 
# ============================================================================

root_agent = Agent(
    name="legal_document_analyzer",
    model="gemini-2.0-flash",
    description="Professional legal document analyzer that processes text and PDF documents, extracts key information, identifies risks, and generates comprehensive reports. Also supports comparing two contracts side-by-side.",
    instruction="""You are a professional Legal Document Analyzer assistant.

SINGLE DOCUMENT ANALYSIS:
1.  First, transfer to the `legal_analysis_workflow`. This workflow will run 5 steps and return a state dictionary.
2.  This dictionary will contain a key named `final_report`, which holds the fully formatted Markdown report as a string.
3.  Next, transfer to the `final_responder_agent`.
4.  Pass the `final_report` string (which you get from the workflow's output) to the `final_responder_agent`.
5.  This agent will then present the clean, formatted report to the user.

COMPARING TWO DOCUMENTS:
When a user wants to compare TWO contracts:
- They should format their request like:
  "Compare these contracts:
  
  CONTRACT A:
  [paste first contract]
  
  CONTRACT B:
  [paste second contract]"
  
- Transfer to the `contract_comparison_agent`.
- This agent will return the formatted comparison report directly.

Always be professional, accurate, and helpful.
""",
    sub_agents=[
        legal_analysis_workflow, 
        comparison_agent,
        final_responder_agent  # Added the final responder
    ]
)


# ============================================================================
# MAIN ENTRY POINT 
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Legal Document Analyzer Agent - Ready! (v3: Formatted Output)")
    print("=" * 80)
    print("\nThis agent analyzes legal documents and provides:")
    print("  ✓ Key parties identification")
    print("  ✓ Financial terms extraction")
    print("  ✓ Risk assessment")
    print("  ✓ Clean, formatted Markdown report")
    print("\nRun 'adk web' from the parent directory to use the web interface")
    print("=" * 80)
