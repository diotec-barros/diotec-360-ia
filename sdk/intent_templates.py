"""
DIOTEC 360 IA - Universal Intent Templates (FLAT-LOGIC)
Pre-built verification logic for common use cases

"DIOTEC Inside" - Integrity as a Service

@version 1.0.0 - FLAT-LOGIC (No 'let', parser-compatible)
@author DIOTEC 360 IA Engineering Team
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class IntentTemplate:
    """Represents a universal intent template"""
    name: str
    description: str
    params: List[str]
    logic: str
    category: str
    examples: List[Dict[str, Any]]


def get_template(intent_name: str) -> Optional[IntentTemplate]:
    """Get template by name"""
    templates = {
        "transfer": IntentTemplate(
            name="transfer",
            description="Money transfer with balance verification",
            params=["from", "to", "amount", "currency", "balance"],
            category="financial",
            logic="",
            examples=[{"from": "ACC001", "to": "ACC002", "amount": 1000, "currency": "AOA", "balance": 5000}]
        ),
        "escrow": IntentTemplate(
            name="escrow",
            description="Multi-party escrow",
            params=["buyer", "seller", "arbiter", "amount", "currency"],
            category="financial",
            logic="",
            examples=[{"buyer": "buyer_123", "seller": "seller_456", "arbiter": "arbiter_789", "amount": 50000, "currency": "AOA"}]
        ),
        "multisig": IntentTemplate(
            name="multisig",
            description="Multi-signature authorization",
            params=["signers", "threshold", "signed"],
            category="financial",
            logic="",
            examples=[{"signers": ["s1", "s2", "s3"], "threshold": 2, "signed": ["s1", "s2"]}]
        ),
        "loan": IntentTemplate(
            name="loan",
            description="Loan calculation",
            params=["principal", "rate", "term", "currency"],
            category="financial",
            logic="",
            examples=[{"principal": 100000, "rate": 5, "term": 12, "currency": "AOA"}]
        ),
        "vote": IntentTemplate(
            name="vote",
            description="One person, one vote",
            params=["voter_id", "proposal_id", "vote", "voted_before"],
            category="governance",
            logic="",
            examples=[{"voter_id": "voter_123", "proposal_id": "prop_456", "vote": "yes", "voted_before": False}]
        ),
        "delivery": IntentTemplate(
            name="delivery",
            description="GPS-based delivery confirmation",
            params=["package_id", "gps_lat", "gps_lon", "target_lat", "target_lon", "tolerance_meters"],
            category="logistics",
            logic="",
            examples=[{"package_id": "PKG123", "gps_lat": -8.8383, "gps_lon": 13.2344, "target_lat": -8.8400, "target_lon": 13.2350, "tolerance_meters": 100}]
        ),
    }
    return templates.get(intent_name)


def list_templates(category: Optional[str] = None) -> List[IntentTemplate]:
    """List all templates, optionally filtered by category"""
    all_templates = [
        get_template("transfer"),
        get_template("escrow"),
        get_template("multisig"),
        get_template("loan"),
        get_template("vote"),
        get_template("delivery"),
    ]
    
    if category:
        return [t for t in all_templates if t and t.category == category]
    return [t for t in all_templates if t]


def get_categories() -> List[str]:
    """Get all available categories"""
    return ["financial", "governance", "logistics"]


def validate_params(intent_name: str, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate that all required parameters are provided"""
    template = get_template(intent_name)
    
    if not template:
        return False, f"Unknown intent: {intent_name}"
    
    missing_params = [p for p in template.params if p not in params]
    
    if missing_params:
        return False, f"Missing required parameters: {', '.join(missing_params)}"
    
    return True, None


def instantiate_template(intent_name: str, params: Dict[str, Any]) -> Optional[str]:
    """
    Instantiate a template with user parameters - FLAT-LOGIC v2.1
    Returns the Aethel code ready for Z3 verification
    
    FLAT-LOGIC v2.1 Rules (CRITICAL FIX):
    - No 'let' declarations
    - Correct Aethel structure: guard {} verify {} solve {}
    - guard: Pre-conditions (assumptions)
    - verify: Post-conditions to be verified
    - solve: Metadata (priority, target)
    - Only variable names in verify blocks (NO LITERALS)
    - Parser only accepts NAME tokens, not NUMBER tokens
    - Z3 Judge will substitute actual values during verification
    """
    template = get_template(intent_name)
    
    if not template:
        return None
    
    # TRANSFER: Bank transfer with balance verification
    if intent_name == "transfer":
        code = f"""
intent transfer(from: String, to: String, amount: Int, balance: Int) {{
    guard {{
        amount > 0;
        balance >= amount;
        from != to;
    }}
    
    solve {{
        priority: security;
        target: ledger;
    }}
    
    verify {{
        balance >= amount;
    }}
}}
"""
        return code
    
    # ESCROW: Multi-party escrow
    elif intent_name == "escrow":
        code = f"""
intent escrow(buyer: String, seller: String, arbiter: String, amount: Int) {{
    guard {{
        amount > 0;
        buyer != seller;
        arbiter != buyer;
        arbiter != seller;
    }}
    
    solve {{
        priority: security;
        target: ledger;
    }}
    
    verify {{
        amount > 0;
    }}
}}
"""
        return code
    
    # MULTISIG: Multi-signature authorization
    elif intent_name == "multisig":
        code = f"""
intent multisig(threshold: Int, signed_count: Int) {{
    guard {{
        threshold > 0;
        signed_count >= 0;
    }}
    
    solve {{
        priority: security;
        target: ledger;
    }}
    
    verify {{
        signed_count >= threshold;
    }}
}}
"""
        return code
    
    # LOAN: Loan calculation
    elif intent_name == "loan":
        code = f"""
intent loan(principal: Int, rate: Int, term: Int) {{
    guard {{
        principal > 0;
        rate > 0;
        term > 0;
    }}
    
    solve {{
        priority: security;
        target: ledger;
    }}
    
    verify {{
        principal > 0;
        rate > 0;
        term > 0;
    }}
}}
"""
        return code
    
    # VOTE: One person, one vote
    elif intent_name == "vote":
        code = f"""
intent vote(voterId: String, proposalId: String, hasVoted: Int) {{
    guard {{
        hasVoted == 0;
    }}
    
    solve {{
        priority: security;
        target: ledger;
    }}
    
    verify {{
        hasVoted == 0;
    }}
}}
"""
        return code
    
    # DELIVERY: GPS-based delivery confirmation
    elif intent_name == "delivery":
        code = f"""
intent delivery(packageId: String, distance: Int, tolerance: Int) {{
    guard {{
        distance >= 0;
        tolerance > 0;
    }}
    
    solve {{
        priority: security;
        target: ledger;
    }}
    
    verify {{
        distance <= tolerance;
    }}
}}
"""
        return code
    
    # Default: return empty template
    return ""


# Export all
__all__ = [
    'IntentTemplate',
    'get_template',
    'list_templates',
    'get_categories',
    'validate_params',
    'instantiate_template'
]
