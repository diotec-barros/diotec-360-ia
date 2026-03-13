"""
DIOTEC 360 IA - Universal Intent Templates
Pre-built verification logic for common use cases

"DIOTEC Inside" - Integrity as a Service

@version 1.0.0
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


# Universal Intent Templates Library
INTENT_TEMPLATES: Dict[str, IntentTemplate] = {
    "transfer": IntentTemplate(
        name="transfer",
        description="Money transfer with balance verification",
        params=["from", "to", "amount", "currency", "balance"],
        category="financial",
        logic="""
intent transfer(from: String, to: String, amount: Int, balance: Int) {
    guard {
        amount > 0;
        balance >= amount;
        from != to;
    }
    
    solve {
        balance - amount >= 0;
    }
}
        """,
        examples=[
            {
                "from": "account_123",
                "to": "account_456",
                "amount": 1000,
                "currency": "AOA",
                "balance": 5000
            }
        ]
    ),
    
    "escrow": IntentTemplate(
        name="escrow",
        description="Multi-party escrow with conditions",
        params=["buyer", "seller", "amount", "conditions"],
        category="financial",
        logic="""
intent escrow(buyer: String, seller: String, amount: Int, 
              condition1: Bool, condition2: Bool) {
    guard {
        amount > 0;
    }
    
    solve {
        (condition1 && condition2) -> release_to_seller;
        !(condition1 && condition2) -> refund_to_buyer;
    }
}
        """,
        examples=[
            {
                "buyer": "buyer_123",
                "seller": "seller_456",
                "amount": 5000,
                "conditions": ["delivery_confirmed", "quality_approved"]
            }
        ]
    ),
    
    "vote": IntentTemplate(
        name="vote",
        description="One person, one vote verification",
        params=["voterId", "candidateId", "electionId", "hasVoted", "isEligible"],
        category="governance",
        logic="""
intent vote(voterId: String, candidateId: String, 
            hasVoted: Bool, isEligible: Bool) {
    guard {
        !hasVoted;
        isEligible;
    }
    
    solve {
        vote_count_increment == 1;
    }
}
        """,
        examples=[
            {
                "voterId": "citizen_123",
                "candidateId": "candidate_456",
                "electionId": "election_2026",
                "hasVoted": False,
                "isEligible": True
            }
        ]
    ),
    
    "delivery": IntentTemplate(
        name="delivery",
        description="GPS-verified delivery confirmation",
        params=["driverId", "orderId", "gpsLat", "gpsLon", "targetLat", "targetLon", "maxDistance"],
        category="logistics",
        logic="""
intent delivery(driverId: String, orderId: String,
                currentLat: Real, currentLon: Real,
                targetLat: Real, targetLon: Real,
                maxDistance: Real) {
    guard {
        maxDistance > 0;
    }
    
    solve {
        distance(currentLat, currentLon, targetLat, targetLon) <= maxDistance;
    }
}
        """,
        examples=[
            {
                "driverId": "driver_123",
                "orderId": "order_456",
                "gpsLat": -8.8383,
                "gpsLon": 13.2344,
                "targetLat": -8.8380,
                "targetLon": 13.2340,
                "maxDistance": 0.1
            }
        ]
    ),
    
    "multisig": IntentTemplate(
        name="multisig",
        description="Multi-signature authorization",
        params=["signers", "threshold", "signatures"],
        category="financial",
        logic="""
intent multisig(totalSigners: Int, threshold: Int, 
                validSignatures: Int) {
    guard {
        threshold > 0;
        threshold <= totalSigners;
    }
    
    solve {
        validSignatures >= threshold;
    }
}
        """,
        examples=[
            {
                "signers": ["signer1", "signer2", "signer3"],
                "threshold": 2,
                "signatures": ["sig1", "sig2"]
            }
        ]
    ),
    
    "prescription": IntentTemplate(
        name="prescription",
        description="Medical prescription authorization verification",
        params=["doctorId", "patientId", "medication", "isAuthorized", "hasLicense"],
        category="healthcare",
        logic="""
intent prescription(doctorId: String, patientId: String,
                   medication: String, isAuthorized: Bool, hasLicense: Bool) {
    guard {
        isAuthorized;
        hasLicense;
    }
    
    solve {
        prescription_valid == true;
    }
}
        """,
        examples=[
            {
                "doctorId": "doctor_123",
                "patientId": "patient_456",
                "medication": "aspirin",
                "isAuthorized": True,
                "hasLicense": True
            }
        ]
    ),
    
    "anti_cheat": IntentTemplate(
        name="anti_cheat",
        description="Gaming anti-cheat memory integrity verification",
        params=["playerId", "gameId", "memoryHash", "expectedHash"],
        category="gaming",
        logic="""
intent anti_cheat(playerId: String, gameId: String,
                 memoryHash: String, expectedHash: String) {
    guard {
        memoryHash != "";
        expectedHash != "";
    }
    
    solve {
        memoryHash == expectedHash;
    }
}
        """,
        examples=[
            {
                "playerId": "player_123",
                "gameId": "match_456",
                "memoryHash": "0xabc123...",
                "expectedHash": "0xabc123..."
            }
        ]
    ),
    
    "supply_chain": IntentTemplate(
        name="supply_chain",
        description="Supply chain provenance verification",
        params=["productId", "origin", "destination", "checkpoints"],
        category="logistics",
        logic="""
intent supply_chain(productId: String, origin: String,
                   destination: String, checkpointsVisited: Int,
                   requiredCheckpoints: Int) {
    guard {
        checkpointsVisited >= 0;
        requiredCheckpoints > 0;
    }
    
    solve {
        checkpointsVisited >= requiredCheckpoints;
    }
}
        """,
        examples=[
            {
                "productId": "product_123",
                "origin": "factory_A",
                "destination": "store_B",
                "checkpoints": ["warehouse_1", "customs", "warehouse_2"]
            }
        ]
    ),
    
    "loan": IntentTemplate(
        name="loan",
        description="Loan calculation and amortization verification",
        params=["principal", "annualRate", "months", "monthlyPayment"],
        category="financial",
        logic="""
intent loan(principal: Int, annualRate: Real, months: Int,
           monthlyPayment: Real) {
    guard {
        principal > 0;
        annualRate >= 0;
        months > 0;
    }
    
    solve {
        monthlyPayment == calculate_amortization(principal, annualRate, months);
    }
}
        """,
        examples=[
            {
                "principal": 100000,
                "annualRate": 12.5,
                "months": 24,
                "monthlyPayment": 4708.33
            }
        ]
    ),
    
    "identity": IntentTemplate(
        name="identity",
        description="Digital identity verification",
        params=["userId", "biometricHash", "documentHash", "isValid"],
        category="governance",
        logic="""
intent identity(userId: String, biometricHash: String,
               documentHash: String, isValid: Bool) {
    guard {
        biometricHash != "";
        documentHash != "";
    }
    
    solve {
        isValid == verify_identity(biometricHash, documentHash);
    }
}
        """,
        examples=[
            {
                "userId": "citizen_123",
                "biometricHash": "0xbio123...",
                "documentHash": "0xdoc456...",
                "isValid": True
            }
        ]
    )
}


def get_template(intent_name: str) -> Optional[IntentTemplate]:
    """Get an intent template by name"""
    return INTENT_TEMPLATES.get(intent_name)


def list_templates(category: Optional[str] = None) -> List[IntentTemplate]:
    """List all templates, optionally filtered by category"""
    templates = list(INTENT_TEMPLATES.values())
    
    if category:
        templates = [t for t in templates if t.category == category]
    
    return templates


def get_categories() -> List[str]:
    """Get all available categories"""
    return list(set(t.category for t in INTENT_TEMPLATES.values()))


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
    Instantiate a template with user parameters
    Returns the Aethel code ready for verification
    """
    template = get_template(intent_name)
    
    if not template:
        return None
    
    # For now, return the template logic as-is
    # TODO: Substitute actual parameter values into the logic
    return template.logic


# Export all
__all__ = [
    'IntentTemplate',
    'INTENT_TEMPLATES',
    'get_template',
    'list_templates',
    'get_categories',
    'validate_params',
    'instantiate_template'
]
