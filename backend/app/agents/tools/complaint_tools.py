"""LangChain tool definitions for the AI Copilot.

Three mandatory tools:
1. log_complaint — Extract fields from natural language and populate the form
2. edit_complaint — Update specific fields from user corrections
3. (document extraction is handled by parsing the file first, then calling log_complaint)
"""
from langchain_core.tools import tool
from typing import Optional


@tool
def log_complaint(
    complaint_source: Optional[str] = None,
    customer_name: Optional[str] = None,
    product_name: Optional[str] = None,
    product_strength: Optional[str] = None,
    batch_number: Optional[str] = None,
    manufacturing_date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    quantity_affected: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    complaint_type: Optional[str] = None,
    complaint_date: Optional[str] = None,
    complaint_description: Optional[str] = None,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    next_action: Optional[str] = None,
    justification: Optional[str] = None,
    risk_factors: Optional[list[str]] = None,
) -> str:
    """Log a new customer complaint by extracting ALL relevant details from the user's message.
    
    Use this tool when the user describes a NEW complaint. Extract every field you can find
    from their message. Also assess the risk: determine severity (minor/major/critical),
    priority (low/medium/high/urgent), recommended next action, and justification.
    
    Rules:
    - complaint_description: write a detailed 2-3 sentence professional summary including reporter, product, defect, quantity, and dates.
    - complaint_source: phone, email, letter, portal, sales_rep, or pharmacy. If the reporter is a pharmacy, hospital, or clinic, use 'pharmacy'.
    - customer_name: Always extract the reporting entity name (e.g., 'Apollo Pharmacy' from 'Apollo Pharmacy reported...')
    - complaint_type: product_quality, packaging, adverse_event, delivery, documentation, or other
    - complaint_date: If not explicitly mentioned, use today's date in YYYY-MM-DD format.
    - severity: minor (trivial cosmetic, no product impact), major (any product quality defect like discoloration, chipping, broken seals, contamination suspicion), critical (adverse event/health risk/patient safety)
    - priority: based on severity + quantity + patient exposure risk
    - next_action: For major, use 'Route to QA Investigation & Issue Replacement'. For critical, use 'Initiate field alert'.
    - justification: Provide a detailed root cause hypothesis.
    - Normalize dates to YYYY-MM-DD format
    - Only extract what is explicitly stated. Never fabricate values.
    """
    # Build the result dict — only include non-None fields
    field_updates = {}
    risk_assessment = {}
    
    field_map = {
        "complaint_source": complaint_source,
        "customer_name": customer_name,
        "product_name": product_name,
        "product_strength": product_strength,
        "batch_number": batch_number,
        "manufacturing_date": manufacturing_date,
        "expiry_date": expiry_date,
        "quantity_affected": quantity_affected,
        "quantity_unit": quantity_unit,
        "complaint_type": complaint_type,
        "complaint_date": complaint_date,
        "complaint_description": complaint_description,
    }
    
    for k, v in field_map.items():
        if v is not None:
            field_updates[k] = v
    
    if severity:
        risk_assessment["severity"] = severity
    if priority:
        risk_assessment["priority"] = priority
        field_updates["priority"] = priority
    if severity:
        field_updates["initial_severity"] = severity
    if next_action:
        risk_assessment["next_action"] = next_action
    if justification:
        risk_assessment["justification"] = justification
    if risk_factors:
        risk_assessment["risk_factors"] = risk_factors
    
    import json
    return json.dumps({
        "action": "log",
        "field_updates": field_updates,
        "risk_assessment": risk_assessment,
    })


@tool
def edit_complaint(
    complaint_source: Optional[str] = None,
    customer_name: Optional[str] = None,
    product_name: Optional[str] = None,
    product_strength: Optional[str] = None,
    batch_number: Optional[str] = None,
    manufacturing_date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    quantity_affected: Optional[float] = None,
    quantity_unit: Optional[str] = None,
    complaint_type: Optional[str] = None,
    complaint_date: Optional[str] = None,
    complaint_description: Optional[str] = None,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    next_action: Optional[str] = None,
    justification: Optional[str] = None,
    risk_factors: Optional[list[str]] = None,
) -> str:
    """Edit specific fields of an existing complaint based on user corrections.
    
    Use this tool when the user wants to CORRECT or UPDATE specific fields of an already
    logged complaint. Only provide the fields that need to change — all other fields
    will be preserved as-is.
    
    Example: "Sorry, the batch number is BMX24602 and affected quantity is 48 capsules"
    → Only update batch_number and quantity_affected, keep everything else.
    
    If the correction affects risk assessment (e.g., changing severity-related info),
    also update the risk assessment fields.
    """
    field_updates = {}
    risk_assessment = {}
    
    field_map = {
        "complaint_source": complaint_source,
        "customer_name": customer_name,
        "product_name": product_name,
        "product_strength": product_strength,
        "batch_number": batch_number,
        "manufacturing_date": manufacturing_date,
        "expiry_date": expiry_date,
        "quantity_affected": quantity_affected,
        "quantity_unit": quantity_unit,
        "complaint_type": complaint_type,
        "complaint_date": complaint_date,
        "complaint_description": complaint_description,
    }
    
    for k, v in field_map.items():
        if v is not None:
            field_updates[k] = v
    
    if severity:
        risk_assessment["severity"] = severity
        field_updates["initial_severity"] = severity
    if priority:
        risk_assessment["priority"] = priority
        field_updates["priority"] = priority
    if next_action:
        risk_assessment["next_action"] = next_action
    if justification:
        risk_assessment["justification"] = justification
    if risk_factors:
        risk_assessment["risk_factors"] = risk_factors
    
    import json
    return json.dumps({
        "action": "edit",
        "field_updates": field_updates,
        "risk_assessment": risk_assessment,
    })


# List of all tools for the copilot agent
COPILOT_TOOLS = [log_complaint, edit_complaint]
