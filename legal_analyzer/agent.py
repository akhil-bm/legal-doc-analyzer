"""
Legal Document Analyzer Agent with PDF Support and Comparison Feature

A sophisticated multi-agent system that analyzes legal documents (contracts, agreements)
from both text and PDF formats, producing structured analysis including key parties, 
dates, financial terms, obligations, risks, and plain language summaries.

Also supports comparing two contracts side-by-side.
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
    """
    Extracts text from PDF file content.
    
    Args:
        pdf_content: Binary content of the PDF file
        
    Returns:
        str: Extracted text from all pages
    """
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


# ============================================================================
# AGENT 1: DOCUMENT EXTRACTOR (ENHANCED WITH PDF SUPPORT)
# ============================================================================

def extract_document_text(document_text: Optional[str] = None, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Extracts and cleans text from a legal document (text or PDF format).
    
    This function handles both plain text input and PDF file uploads.
    It cleans the text and prepares it for further analysis.
    
    Args:
        document_text: The raw text content (if provided directly)
        tool_context: ADK tool context (for accessing uploaded artifacts)
        
    Returns:
        dict: Contains status, cleaned text, and document metadata
    """
    extracted_text = ""
    source_type = "text"
    
    # Check if there are uploaded PDF files
    if tool_context:
        try:
            artifacts = tool_context.list_artifacts()
            
            # Look for PDF files
            pdf_files = [f for f in artifacts if f.lower().endswith('.pdf')]
            
            if pdf_files:
                # Process the first PDF file found
                pdf_filename = pdf_files[0]
                print(f"Processing PDF file: {pdf_filename}")
                
                # Load the PDF artifact
                pdf_artifact = tool_context.load_artifact(pdf_filename)
                
                if pdf_artifact and hasattr(pdf_artifact, 'inline_data'):
                    # Extract bytes from the artifact
                    pdf_bytes = pdf_artifact.inline_data.data
                    extracted_text = extract_text_from_pdf(pdf_bytes)
                    source_type = "pdf"
                    print(f"Extracted {len(extracted_text)} characters from PDF")
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            # Fall back to text input if PDF processing fails
            pass
    
    # If no PDF was processed, use the provided text
    if not extracted_text and document_text:
        extracted_text = document_text
        source_type = "text"
    
    # Validate we have content
    if not extracted_text or len(extracted_text.strip()) < 50:
        return {
            "status": "error",
            "message": "Document text is too short or empty. Please provide a valid legal document (text or PDF).",
            "cleaned_text": "",
            "word_count": 0,
            "char_count": 0,
            "source_type": source_type
        }
    
    # Clean the text
    cleaned = extracted_text.strip()
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Remove special characters that might interfere
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
    
    word_count = len(cleaned.split())
    char_count = len(cleaned)
    
    return {
        "status": "success",
        "message": f"Document extracted and cleaned successfully from {source_type.upper()}",
        "cleaned_text": cleaned,
        "word_count": word_count,
        "char_count": char_count,
        "source_type": source_type,
        "extracted_at": datetime.now().isoformat()
    }


# ============================================================================
# AGENT 2: CLAUSE IDENTIFIER
# ============================================================================

def identify_key_clauses(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifies key clauses, parties, dates, and financial terms in the document.
    
    Args:
        extraction_result: The result from the document extraction step
        
    Returns:
        dict: Contains identified parties, dates, amounts, and clause types
    """
    if extraction_result.get("status") == "error":
        return extraction_result
    
    text = extraction_result.get("cleaned_text", "")
    
    if not text:
        return {
            "status": "error",
            "message": "No text available for clause identification"
        }
    
    # Initialize results
    parties = []
    dates = []
    financial_terms = []
    key_clauses = []
    
    # Identify parties
    party_patterns = [
        r'(?:between|by and between)\s+([A-Z][A-Za-z\s&,\.]+?)\s+(?:and|,)',
        r'"([A-Z][A-Za-z\s&,\.]+?)"\s+\(["\']?(?:Client|Provider|Vendor|Contractor|Party|Company|Licensor|Licensee|Landlord|Tenant|Partner)["\']?\)',
        r'(?:Party|Client|Vendor|Provider|Licensor|Licensee|Landlord|Tenant|Partner)\s*[A-Z]?:\s*([A-Z][A-Za-z\s&,\.]+?)(?:\.|,|\n)'
    ]
    
    for pattern in party_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean_party = match.strip().rstrip('.,')
            if clean_party and len(clean_party) > 2 and clean_party not in parties:
                parties.append(clean_party)
    
    # Identify dates
    date_patterns = [
        (r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', 'date'),
        (r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b', 'date'),
        (r'(?:deadline|due date|effective date|start date|end date|termination date|commencement date|expiration date):\s*([^\n\.]+)', 'deadline')
    ]
    
    for pattern, date_type in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1]
            dates.append({
                "date": match.strip(),
                "type": date_type,
                "context": "identified in document"
            })
    
    # Identify financial terms
    amount_patterns = [
        r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:USD|dollars))?',
        r'(?:amount|payment|fee|cost|price|compensation|salary|rent):\s*\$?\s*[\d,]+(?:\.\d{2})?',
        r'(?:total|sum)(?:\s+of)?\s*\$?\s*[\d,]+(?:\.\d{2})?'
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            financial_terms.append({
                "amount": match.strip(),
                "context": "financial term identified"
            })
    
    # Identify key clause types
    clause_keywords = {
        "Termination": ["termination", "terminate", "cancellation", "cancel agreement"],
        "Liability": ["liability", "indemnification", "indemnify", "hold harmless"],
        "Confidentiality": ["confidential", "non-disclosure", "proprietary information"],
        "Payment": ["payment terms", "invoice", "compensation", "consideration"],
        "Intellectual Property": ["intellectual property", "IP rights", "copyright", "trademark"],
        "Dispute Resolution": ["arbitration", "mediation", "dispute resolution", "jurisdiction"],
        "Force Majeure": ["force majeure", "acts of god", "unforeseeable circumstances"],
        "Non-Compete": ["non-compete", "non-competition", "restrictive covenant"],
        "Warranty": ["warranty", "warranties", "represent and warrant"]
    }
    
    for clause_type, keywords in clause_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                key_clauses.append({
                    "type": clause_type,
                    "keyword": keyword,
                    "present": True
                })
                break
    
    # Determine document type
    doc_type = "Unknown"
    if "employment" in text.lower() or "employee" in text.lower():
        doc_type = "Employment Agreement"
    elif "service" in text.lower() and "provider" in text.lower():
        doc_type = "Service Agreement"
    elif "purchase" in text.lower() or "sale" in text.lower():
        doc_type = "Purchase Agreement"
    elif "lease" in text.lower() or "rent" in text.lower():
        doc_type = "Lease Agreement"
    elif "non-disclosure" in text.lower() or "confidentiality" in text.lower():
        doc_type = "NDA (Non-Disclosure Agreement)"
    elif "partnership" in text.lower() or "partner" in text.lower():
        doc_type = "Partnership Agreement"
    elif "license" in text.lower() and "software" in text.lower():
        doc_type = "Software License Agreement"
    else:
        doc_type = "General Contract/Agreement"
    
    return {
        "status": "success",
        "message": "Key clauses identified successfully",
        "document_type": doc_type,
        "parties": parties[:5] if len(parties) > 0 else ["Party information not clearly identified"],
        "dates": dates[:10],
        "financial_terms": financial_terms[:10],
        "key_clauses": key_clauses,
        "total_parties": len(parties),
        "total_dates": len(dates),
        "total_financial_terms": len(financial_terms),
        "analyzed_at": datetime.now().isoformat()
    }


# ============================================================================
# AGENT 3: RISK ANALYZER
# ============================================================================

def analyze_risks_and_obligations(clause_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes obligations and identifies potential risks in the document.
    
    Args:
        clause_result: The result from the clause identification step
        
    Returns:
        dict: Contains obligations, risks, and recommendations
    """
    if clause_result.get("status") == "error":
        return clause_result
    
    key_clauses = clause_result.get("key_clauses", [])
    parties = clause_result.get("parties", [])
    financial_terms = clause_result.get("financial_terms", [])
    dates = clause_result.get("dates", [])
    doc_type = clause_result.get("document_type", "Unknown")
    
    # Analyze obligations
    obligations = []
    
    if len(parties) > 0:
        for party in parties[:3]:
            party_obligations = {
                "party": party,
                "obligations": []
            }
            
            if "Payment" in [c["type"] for c in key_clauses]:
                party_obligations["obligations"].append(
                    "Financial obligations as per payment terms specified in the agreement"
                )
            
            if "Confidentiality" in [c["type"] for c in key_clauses]:
                party_obligations["obligations"].append(
                    "Maintain confidentiality of proprietary information"
                )
            
            if "Termination" in [c["type"] for c in key_clauses]:
                party_obligations["obligations"].append(
                    "Comply with termination notice requirements and procedures"
                )
            
            if len(party_obligations["obligations"]) == 0:
                party_obligations["obligations"].append(
                    "Obligations to be reviewed in detail within the document"
                )
            
            obligations.append(party_obligations)
    
    # Identify risks
    risks = []
    risk_score = 0
    
    # Risk 1: Missing critical clauses
    critical_clauses = ["Termination", "Liability", "Dispute Resolution"]
    present_critical = [c["type"] for c in key_clauses]
    missing_clauses = [c for c in critical_clauses if c not in present_critical]
    
    if missing_clauses:
        risks.append({
            "type": "Missing Critical Clauses",
            "severity": "High",
            "description": f"The following critical clauses are missing: {', '.join(missing_clauses)}",
            "impact": "May lead to disputes or unclear terms in case of conflicts"
        })
        risk_score += 3
    
    # Risk 2: Unclear parties
    if len(parties) == 0 or "not clearly identified" in str(parties).lower():
        risks.append({
            "type": "Unclear Party Identification",
            "severity": "High",
            "description": "Parties to the agreement are not clearly identified",
            "impact": "May cause enforceability issues"
        })
        risk_score += 3
    
    # Risk 3: No financial terms
    if len(financial_terms) == 0:
        risks.append({
            "type": "No Financial Terms",
            "severity": "Medium",
            "description": "No clear financial terms or amounts identified",
            "impact": "May lead to payment disputes"
        })
        risk_score += 2
    
    # Risk 4: No dates/deadlines
    if len(dates) == 0:
        risks.append({
            "type": "No Dates or Deadlines",
            "severity": "Medium",
            "description": "No specific dates or deadlines identified",
            "impact": "Unclear timeline for obligations and deliverables"
        })
        risk_score += 2
    
    # Risk 5: No liability clause
    if "Liability" not in present_critical:
        risks.append({
            "type": "No Liability Clause",
            "severity": "High",
            "description": "No indemnification or liability limitations identified",
            "impact": "Unlimited liability exposure"
        })
        risk_score += 3
    
    # If no risks identified, add a positive note
    if len(risks) == 0:
        risks.append({
            "type": "Low Risk",
            "severity": "Low",
            "description": "Document appears to have standard clauses",
            "impact": "Minimal immediate concerns identified"
        })
    
    # Cap risk score at 10
    risk_score = min(risk_score, 10)
    
    # Generate recommendations
    recommendations = []
    
    if missing_clauses:
        recommendations.append(
            f"Consider adding the following clauses: {', '.join(missing_clauses)}"
        )
    
    if risk_score >= 7:
        recommendations.append(
            "High risk document - Strongly recommend legal review before signing"
        )
    elif risk_score >= 4:
        recommendations.append(
            "Medium risk - Review and clarify identified concerns"
        )
    else:
        recommendations.append(
            "Low risk - Standard review recommended"
        )
    
    if len(parties) < 2:
        recommendations.append(
            "Clearly identify all parties with full legal names and addresses"
        )
    
    if len(financial_terms) == 0:
        recommendations.append(
            "Ensure all payment terms, amounts, and schedules are clearly specified"
        )
    
    recommendations.append(
        "Always have legal counsel review contracts before execution"
    )
    
    return {
        "status": "success",
        "message": "Risk analysis completed successfully",
        "obligations": obligations,
        "risks": risks,
        "missing_clauses": missing_clauses,
        "risk_score": risk_score,
        "risk_level": "High" if risk_score >= 7 else "Medium" if risk_score >= 4 else "Low",
        "recommendations": recommendations,
        "analyzed_at": datetime.now().isoformat()
    }


# ============================================================================
# AGENT 4: REPORT GENERATOR
# ============================================================================

def generate_analysis_report(risk_result: Dict[str, Any]) -> str:
    """
    Generates a comprehensive, structured analysis report.
    
    Args:
        risk_result: The result from the risk analysis step
        
    Returns:
        str: A formatted analysis report
    """
    if risk_result.get("status") == "error":
        return f"❌ Error: {risk_result.get('message', 'Unable to generate report')}"
    
    obligations = risk_result.get("obligations", [])
    risks = risk_result.get("risks", [])
    risk_score = risk_result.get("risk_score", 0)
    risk_level = risk_result.get("risk_level", "Unknown")
    recommendations = risk_result.get("recommendations", [])
    
    # Build the report
    report = "=" * 80 + "\n"
    report += "📄 LEGAL DOCUMENT ANALYSIS REPORT\n"
    report += "=" * 80 + "\n\n"
    
    # Executive Summary
    report += "🎯 EXECUTIVE SUMMARY\n"
    report += "-" * 80 + "\n"
    report += f"Risk Level: {risk_level}\n"
    report += f"Risk Score: {risk_score}/10\n"
    report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "\n"
    
    # Obligations Section
    report += "📋 PARTY OBLIGATIONS\n"
    report += "-" * 80 + "\n"
    if len(obligations) > 0:
        for idx, obligation_set in enumerate(obligations, 1):
            party = obligation_set.get("party", "Unknown Party")
            party_obligations = obligation_set.get("obligations", [])
            report += f"\n{idx}. {party}:\n"
            for obl in party_obligations:
                report += f"   • {obl}\n"
    else:
        report += "No specific obligations identified.\n"
    report += "\n"
    
    # Risks Section
    report += "⚠️  IDENTIFIED RISKS\n"
    report += "-" * 80 + "\n"
    if len(risks) > 0:
        for idx, risk in enumerate(risks, 1):
            risk_type = risk.get("type", "Unknown")
            severity = risk.get("severity", "Unknown")
            description = risk.get("description", "No description")
            impact = risk.get("impact", "No impact stated")
            
            report += f"\n{idx}. {risk_type} [{severity} Severity]\n"
            report += f"   Description: {description}\n"
            report += f"   Impact: {impact}\n"
    else:
        report += "No significant risks identified.\n"
    report += "\n"
    
    # Recommendations Section
    report += "💡 RECOMMENDATIONS\n"
    report += "-" * 80 + "\n"
    if len(recommendations) > 0:
        for idx, rec in enumerate(recommendations, 1):
            report += f"{idx}. {rec}\n"
    else:
        report += "No specific recommendations at this time.\n"
    report += "\n"
    
    # Footer
    report += "=" * 80 + "\n"
    report += "⚖️  This is an automated analysis. Please consult with legal counsel\n"
    report += "   for professional advice before making any decisions.\n"
    report += "=" * 80 + "\n"
    
    return report


# ============================================================================
# CONTRACT COMPARISON FUNCTIONALITY
# ============================================================================

def compare_two_documents(document_a_text: str, document_b_text: str) -> str:
    """
    Compares two legal documents and generates a side-by-side comparison report.
    
    Args:
        document_a_text: Full text of the first contract
        document_b_text: Full text of the second contract
        
    Returns:
        str: A formatted comparison report showing differences and similarities
    """
    
    # Analyze Document A
    print("Analyzing Document A...")
    extraction_a = extract_document_text(document_a_text)
    if extraction_a.get("status") == "error":
        return f"❌ Error analyzing Document A: {extraction_a.get('message')}"
    
    clause_a = identify_key_clauses(extraction_a)
    if clause_a.get("status") == "error":
        return f"❌ Error identifying clauses in Document A: {clause_a.get('message')}"
    
    risk_a = analyze_risks_and_obligations(clause_a)
    if risk_a.get("status") == "error":
        return f"❌ Error analyzing risks in Document A: {risk_a.get('message')}"
    
    # Analyze Document B
    print("Analyzing Document B...")
    extraction_b = extract_document_text(document_b_text)
    if extraction_b.get("status") == "error":
        return f"❌ Error analyzing Document B: {extraction_b.get('message')}"
    
    clause_b = identify_key_clauses(extraction_b)
    if clause_b.get("status") == "error":
        return f"❌ Error identifying clauses in Document B: {clause_b.get('message')}"
    
    risk_b = analyze_risks_and_obligations(clause_b)
    if risk_b.get("status") == "error":
        return f"❌ Error analyzing risks in Document B: {risk_b.get('message')}"
    
    # Generate comparison report
    report = "=" * 90 + "\n"
    report += "🔄 CONTRACT COMPARISON REPORT\n"
    report += "=" * 90 + "\n\n"
    
    # Executive Summary Comparison
    report += "📊 EXECUTIVE SUMMARY COMPARISON\n"
    report += "-" * 90 + "\n"
    report += f"{'Metric':<30} {'Document A':<30} {'Document B':<30}\n"
    report += "-" * 90 + "\n"
    
    doc_type_a = clause_a.get("document_type", "Unknown")
    doc_type_b = clause_b.get("document_type", "Unknown")
    report += f"{'Document Type:':<30} {doc_type_a:<30} {doc_type_b:<30}\n"
    
    risk_level_a = risk_a.get("risk_level", "Unknown")
    risk_level_b = risk_b.get("risk_level", "Unknown")
    report += f"{'Risk Level:':<30} {risk_level_a:<30} {risk_level_b:<30}\n"
    
    risk_score_a = risk_a.get("risk_score", 0)
    risk_score_b = risk_b.get("risk_score", 0)
    report += f"{'Risk Score:':<30} {risk_score_a}/10{'':<25} {risk_score_b}/10{'':<25}\n"
    
    word_count_a = extraction_a.get("word_count", 0)
    word_count_b = extraction_b.get("word_count", 0)
    report += f"{'Word Count:':<30} {word_count_a:<30} {word_count_b:<30}\n"
    
    parties_a = len(clause_a.get("parties", []))
    parties_b = len(clause_b.get("parties", []))
    report += f"{'Number of Parties:':<30} {parties_a:<30} {parties_b:<30}\n"
    
    report += "\n"
    
    # Risk Comparison
    report += "⚖️  RISK LEVEL COMPARISON\n"
    report += "-" * 90 + "\n"
    
    if risk_score_a < risk_score_b:
        report += f"✅ Document A has LOWER risk (Score: {risk_score_a}/10) compared to Document B (Score: {risk_score_b}/10)\n"
        report += f"   Difference: {risk_score_b - risk_score_a} points\n"
    elif risk_score_a > risk_score_b:
        report += f"✅ Document B has LOWER risk (Score: {risk_score_b}/10) compared to Document A (Score: {risk_score_a}/10)\n"
        report += f"   Difference: {risk_score_a - risk_score_b} points\n"
    else:
        report += f"⚖️  Both documents have EQUAL risk (Score: {risk_score_a}/10)\n"
    
    report += "\n"
    
    # Financial Terms Comparison
    report += "💰 FINANCIAL TERMS COMPARISON\n"
    report += "-" * 90 + "\n"
    
    financial_a = clause_a.get("financial_terms", [])
    financial_b = clause_b.get("financial_terms", [])
    
    report += f"Document A: {len(financial_a)} financial terms identified\n"
    if len(financial_a) > 0:
        for idx, term in enumerate(financial_a[:3], 1):
            report += f"   {idx}. {term.get('amount', 'N/A')}\n"
    
    report += f"\nDocument B: {len(financial_b)} financial terms identified\n"
    if len(financial_b) > 0:
        for idx, term in enumerate(financial_b[:3], 1):
            report += f"   {idx}. {term.get('amount', 'N/A')}\n"
    
    report += "\n"
    
    # Key Clauses Comparison
    report += "📋 KEY CLAUSES COMPARISON\n"
    report += "-" * 90 + "\n"
    
    clauses_a = set([c["type"] for c in clause_a.get("key_clauses", [])])
    clauses_b = set([c["type"] for c in clause_b.get("key_clauses", [])])
    
    common_clauses = clauses_a.intersection(clauses_b)
    only_in_a = clauses_a - clauses_b
    only_in_b = clauses_b - clauses_a
    
    report += f"✅ Clauses in BOTH documents ({len(common_clauses)}):\n"
    if common_clauses:
        for clause in sorted(common_clauses):
            report += f"   • {clause}\n"
    else:
        report += "   None\n"
    
    report += f"\n📄 Clauses ONLY in Document A ({len(only_in_a)}):\n"
    if only_in_a:
        for clause in sorted(only_in_a):
            report += f"   • {clause}\n"
    else:
        report += "   None\n"
    
    report += f"\n📄 Clauses ONLY in Document B ({len(only_in_b)}):\n"
    if only_in_b:
        for clause in sorted(only_in_b):
            report += f"   • {clause}\n"
    else:
        report += "   None\n"
    
    report += "\n"
    
    # Missing Critical Clauses Comparison
    report += "⚠️  MISSING CRITICAL CLAUSES\n"
    report += "-" * 90 + "\n"
    
    missing_a = risk_a.get("missing_clauses", [])
    missing_b = risk_b.get("missing_clauses", [])
    
    report += f"Document A missing: {', '.join(missing_a) if missing_a else 'None'}\n"
    report += f"Document B missing: {', '.join(missing_b) if missing_b else 'None'}\n"
    
    report += "\n"
    
    # Recommendations
    report += "💡 COMPARATIVE RECOMMENDATIONS\n"
    report += "-" * 90 + "\n"
    
    if risk_score_a < risk_score_b:
        report += "1. Document A appears to be the better option from a risk perspective\n"
        report += f"2. Document B has {risk_score_b - risk_score_a} more risk points\n"
    elif risk_score_a > risk_score_b:
        report += "1. Document B appears to be the better option from a risk perspective\n"
        report += f"2. Document A has {risk_score_a - risk_score_b} more risk points\n"
    else:
        report += "1. Both documents have similar risk profiles\n"
    
    if only_in_a and not only_in_b:
        report += "3. Document A has more comprehensive clause coverage\n"
    elif only_in_b and not only_in_a:
        report += "3. Document B has more comprehensive clause coverage\n"
    
    if len(financial_a) > len(financial_b):
        report += "4. Document A has more detailed financial terms\n"
    elif len(financial_b) > len(financial_a):
        report += "4. Document B has more detailed financial terms\n"
    
    report += "5. Always consult with legal counsel before choosing between contracts\n"
    
    report += "\n"
    
    # Footer
    report += "=" * 90 + "\n"
    report += "⚖️  This is an automated comparison. Professional legal advice is strongly recommended.\n"
    report += "=" * 90 + "\n"
    
    return report


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# Agent 1: Document Extractor (Enhanced with PDF Support)
extractor_agent = Agent(
    name="document_extractor",
    model="gemini-2.0-flash",
    description="Extracts and cleans text from legal documents (text or PDF format)",
    instruction="""You are a document extraction specialist with PDF processing capabilities. Your job is to:
    
1. Check if a PDF file has been uploaded using the artifact system
2. If a PDF is found, extract text from it
3. If no PDF, use the provided document text
4. Call the extract_document_text function (it handles both automatically)
5. Return the extraction result exactly as provided by the function
6. Do not add any commentary or additional text

You can process both plain text and PDF documents seamlessly.""",
    tools=[extract_document_text],
    output_key="extraction_result"
)

# Agent 2: Clause Identifier
identifier_agent = Agent(
    name="clause_identifier",
    model="gemini-2.0-flash",
    description="Identifies key clauses, parties, dates, and financial terms",
    instruction="""You are a legal clause identification specialist. Your job is to:

1. Take the extraction_result from the previous step
2. Call the identify_key_clauses function with the extraction result
3. Return the identification result exactly as provided by the function
4. Do not add any commentary or additional text

Focus on accurately identifying parties, dates, financial terms, and key clause types.""",
    tools=[identify_key_clauses],
    output_key="clause_result"
)

# Agent 3: Risk Analyzer
risk_agent = Agent(
    name="risk_analyzer",
    model="gemini-2.0-flash",
    description="Analyzes obligations and identifies risks in the document",
    instruction="""You are a legal risk analysis specialist. Your job is to:

1. Take the clause_result from the previous step
2. Call the analyze_risks_and_obligations function with the clause result
3. Return the risk analysis result exactly as provided by the function
4. Do not add any commentary or additional text

Focus on identifying potential risks, obligations, and providing actionable recommendations.""",
    tools=[analyze_risks_and_obligations],
    output_key="risk_result"
)

# Agent 4: Report Generator
generator_agent = Agent(
    name="report_generator",
    model="gemini-2.0-flash",
    description="Generates a comprehensive analysis report",
    instruction="""You are the FINAL agent in the workflow.

1. Call generate_analysis_report with the risk_result
2. The function returns a complete formatted report
3. IMMEDIATELY present the entire report to the user in the main chat
4. Do NOT just store it - SHOW it to the user
5. This completes the analysis

The report is the final deliverable - make sure the user sees it!""",
    tools=[generate_analysis_report],
    output_key="final_report"
)

# Agent 5: Contract Comparison Agent
comparison_agent = Agent(
    name="contract_comparison_agent",
    model="gemini-2.0-flash",
    description="Compares two legal documents side-by-side and generates a comparison report",
    instruction="""You are a contract comparison specialist. 

When a user provides TWO contracts to compare:

1. The user will provide contracts in this format:
   "Compare these contracts:
   
   CONTRACT A:
   [first contract text]
   
   CONTRACT B:
   [second contract text]"

2. You MUST call the compare_two_documents function with both contract texts
3. Extract the text after "CONTRACT A:" and before "CONTRACT B:" as document_a_text
4. Extract the text after "CONTRACT B:" as document_b_text
5. Return ONLY the comparison report generated by the function
6. Do not add any commentary or additional text

The function will analyze both documents and create a comprehensive side-by-side comparison showing:
- Risk level differences
- Financial terms comparison
- Clause coverage comparison
- Recommendations on which is better

CRITICAL: You must extract the two contract texts from the user's message and pass them separately to the function.""",
    tools=[compare_two_documents]
)


# ============================================================================
# SEQUENTIAL WORKFLOW
# ============================================================================

legal_analysis_workflow = SequentialAgent(
    name="legal_analysis_workflow",
    description="Sequential workflow for analyzing legal documents (text or PDF) through extraction, identification, risk analysis, and reporting",
    sub_agents=[
        extractor_agent,
        identifier_agent,
        risk_agent,
        generator_agent
    ]
)


# ============================================================================
# ROOT AGENT
# ============================================================================

root_agent = Agent(
    name="legal_document_analyzer",
    model="gemini-2.0-flash",
    description="Professional legal document analyzer that processes text and PDF documents, extracts key information, identifies risks, and generates comprehensive reports. Also supports comparing two contracts side-by-side.",
    instruction="""You are a professional Legal Document Analyzer assistant with PDF processing and comparison capabilities.

SINGLE DOCUMENT ANALYSIS:
When a user provides ONE legal document:
- If they upload a PDF file, it will be automatically detected and processed
- If they paste text directly, it will be processed as text
- Transfer to the legal_analysis_workflow to process through all stages
- Present the final analysis report

COMPARING TWO DOCUMENTS:
When a user wants to compare TWO contracts:
- They should format their request like:
  "Compare these contracts:
  
  CONTRACT A:
  [paste first contract]
  
  CONTRACT B:
  [paste second contract]"
  
- Transfer to the contract_comparison_agent
- It will analyze both and generate a side-by-side comparison report

Always be professional, accurate, and helpful in your analysis.

SUPPORTED FORMATS:
• Plain text (paste directly)
• PDF files (upload using attachment button)
• Two-document comparison (paste both with labels)""",
    sub_agents=[legal_analysis_workflow, comparison_agent]
)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Legal Document Analyzer Agent - Ready!")
    print("=" * 80)
    print("\nThis agent analyzes legal documents and provides:")
    print("  ✓ Key parties identification")
    print("  ✓ Important dates and deadlines")
    print("  ✓ Financial terms extraction")
    print("  ✓ Risk assessment")
    print("  ✓ Comprehensive analysis report")
    print("\n📄 SUPPORTED FEATURES:")
    print("  • Single document analysis (text or PDF)")
    print("  • Side-by-side contract comparison")
    print("  • Risk scoring and recommendations")
    print("\nRun 'adk web' from the parent directory to use the web interface")
    print("=" * 80)