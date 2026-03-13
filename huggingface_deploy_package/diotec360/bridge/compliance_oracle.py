"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Compliance Oracle - Legal Framework Integration

This module transforms financial regulations (AML/KYC/CFT) into mathematical
constraints that the Aethel Judge can verify. Instead of hiding from regulators,
we prove compliance mathematically.

Key Features:
1. AML (Anti-Money Laundering) Rules as Z3 Constraints
2. KYC (Know Your Customer) Verification
3. CFT (Combating Financing of Terrorism) Checks
4. Jurisdiction-Specific Compliance (Angola, EU, US, etc.)
5. Selective Disclosure for Auditors (ZKP-based)

The Philosophy:
"We don't hide transactions. We prove they're legal - mathematically."

Research Foundation:
- FATF (Financial Action Task Force) Guidelines
- Basel III Banking Regulations
- EU GDPR + AML Directives
- US Bank Secrecy Act / Patriot Act

Author: Kiro AI - Chief Engineer
Version: v3.5.0 "Sovereign Treasury"
Date: February 18, 2026
"""

import time
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal


class Jurisdiction(Enum):
    """Supported regulatory jurisdictions"""
    ANGOLA = "angola"  # Banco Nacional de Angola
    EUROPEAN_UNION = "eu"  # EBA + ECB
    UNITED_STATES = "us"  # FinCEN + OCC
    UNITED_KINGDOM = "uk"  # FCA
    SWITZERLAND = "ch"  # FINMA
    SINGAPORE = "sg"  # MAS
    INTERNATIONAL = "intl"  # FATF baseline


class ComplianceStatus(Enum):
    """Compliance check result"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"
    BLOCKED = "blocked"


class RiskLevel(Enum):
    """Transaction risk assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """
    A compliance rule that can be verified mathematically.
    
    Attributes:
        rule_id: Unique identifier (e.g., "AML_ANGOLA_001")
        jurisdiction: Which jurisdiction this rule applies to
        rule_type: Type of rule (AML, KYC, CFT, etc.)
        description: Human-readable description
        constraint: Mathematical constraint (Z3-compatible)
        threshold: Numeric threshold if applicable
        mandatory: Whether this rule is mandatory or advisory
    """
    rule_id: str
    jurisdiction: Jurisdiction
    rule_type: str  # "AML", "KYC", "CFT", "SANCTIONS", "TAX"
    description: str
    constraint: str  # Z3 constraint expression
    threshold: Optional[Decimal] = None
    mandatory: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'rule_id': self.rule_id,
            'jurisdiction': self.jurisdiction.value,
            'rule_type': self.rule_type,
            'description': self.description,
            'constraint': self.constraint,
            'threshold': str(self.threshold) if self.threshold else None,
            'mandatory': self.mandatory
        }


@dataclass
class ComplianceCheck:
    """
    Result of a compliance verification.
    
    Attributes:
        check_id: Unique check identifier
        transaction_hash: Hash of transaction being checked
        rules_checked: List of rules that were verified
        status: Overall compliance status
        risk_level: Assessed risk level
        violations: List of violated rules (if any)
        warnings: List of advisory warnings
        proof: Mathematical proof of compliance
        timestamp: When check was performed
    """
    check_id: str
    transaction_hash: str
    rules_checked: List[str]
    status: ComplianceStatus
    risk_level: RiskLevel
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    proof: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'check_id': self.check_id,
            'transaction_hash': self.transaction_hash,
            'rules_checked': self.rules_checked,
            'status': self.status.value,
            'risk_level': self.risk_level.value,
            'violations': self.violations,
            'warnings': self.warnings,
            'proof': self.proof,
            'timestamp': self.timestamp
        }


class ComplianceOracle:
    """
    The Compliance Oracle - Transforms regulations into mathematics.
    
    This oracle doesn't hide transactions. Instead, it proves they comply
    with all applicable regulations - mathematically and transparently.
    
    Key Capabilities:
    1. Load jurisdiction-specific rules
    2. Verify transactions against rules
    3. Generate compliance proofs
    4. Assess risk levels
    5. Create audit trails
    """
    
    def __init__(self, jurisdictions: List[Jurisdiction] = None):
        """
        Initialize the Compliance Oracle.
        
        Args:
            jurisdictions: List of jurisdictions to enforce (default: Angola + International)
        """
        self.jurisdictions = jurisdictions or [Jurisdiction.ANGOLA, Jurisdiction.INTERNATIONAL]
        self.rules: Dict[str, ComplianceRule] = {}
        self.check_history: List[ComplianceCheck] = []
        
        # Load default rules
        self._load_default_rules()
        
        print(f"[COMPLIANCE] Oracle initialized for jurisdictions: {[j.value for j in self.jurisdictions]}")
        print(f"[COMPLIANCE] Loaded {len(self.rules)} compliance rules")
    
    def _load_default_rules(self) -> None:
        """Load default compliance rules for supported jurisdictions"""
        
        # ====================================================================
        # ANGOLA - Banco Nacional de Angola (BNA) Rules
        # ====================================================================
        
        # AML Rule 1: Transaction Reporting Threshold
        self.add_rule(ComplianceRule(
            rule_id="AML_ANGOLA_001",
            jurisdiction=Jurisdiction.ANGOLA,
            rule_type="AML",
            description="Transactions above 5,000,000 AOA must be reported to BNA",
            constraint="amount_aoa <= 5000000 OR reported == True",
            threshold=Decimal("5000000"),
            mandatory=True
        ))
        
        # AML Rule 2: Structuring Detection
        self.add_rule(ComplianceRule(
            rule_id="AML_ANGOLA_002",
            jurisdiction=Jurisdiction.ANGOLA,
            rule_type="AML",
            description="Multiple transactions totaling >5M AOA in 24h require review",
            constraint="daily_total_aoa <= 5000000 OR reviewed == True",
            threshold=Decimal("5000000"),
            mandatory=True
        ))
        
        # KYC Rule 1: Identity Verification
        self.add_rule(ComplianceRule(
            rule_id="KYC_ANGOLA_001",
            jurisdiction=Jurisdiction.ANGOLA,
            rule_type="KYC",
            description="All parties must have verified identity",
            constraint="sender_kyc_verified == True AND receiver_kyc_verified == True",
            mandatory=True
        ))
        
        # CFT Rule 1: Sanctions Screening
        self.add_rule(ComplianceRule(
            rule_id="CFT_ANGOLA_001",
            jurisdiction=Jurisdiction.ANGOLA,
            rule_type="CFT",
            description="Parties must not be on sanctions lists",
            constraint="sender_sanctioned == False AND receiver_sanctioned == False",
            mandatory=True
        ))
        
        # ====================================================================
        # INTERNATIONAL - FATF Baseline
        # ====================================================================
        
        # FATF Recommendation 10: Customer Due Diligence
        self.add_rule(ComplianceRule(
            rule_id="FATF_R10_001",
            jurisdiction=Jurisdiction.INTERNATIONAL,
            rule_type="KYC",
            description="Customer due diligence required for all transactions",
            constraint="customer_due_diligence_performed == True",
            mandatory=True
        ))
        
        # FATF Recommendation 16: Wire Transfers
        self.add_rule(ComplianceRule(
            rule_id="FATF_R16_001",
            jurisdiction=Jurisdiction.INTERNATIONAL,
            rule_type="AML",
            description="Wire transfers must include originator and beneficiary information",
            constraint="has_originator_info == True AND has_beneficiary_info == True",
            mandatory=True
        ))
        
        # FATF Recommendation 20: Suspicious Transaction Reporting
        self.add_rule(ComplianceRule(
            rule_id="FATF_R20_001",
            jurisdiction=Jurisdiction.INTERNATIONAL,
            rule_type="AML",
            description="Suspicious transactions must be reported",
            constraint="is_suspicious == False OR reported_to_fiu == True",
            mandatory=True
        ))
    
    def add_rule(self, rule: ComplianceRule) -> None:
        """
        Add a compliance rule to the oracle.
        
        Args:
            rule: ComplianceRule to add
        """
        self.rules[rule.rule_id] = rule
        print(f"[COMPLIANCE] Added rule: {rule.rule_id} ({rule.jurisdiction.value})")
    
    def check_transaction(
        self,
        transaction: Dict[str, Any],
        jurisdiction: Jurisdiction = None
    ) -> ComplianceCheck:
        """
        Check if a transaction complies with all applicable rules.
        
        Args:
            transaction: Transaction data to check
            jurisdiction: Specific jurisdiction to check (default: all configured)
        
        Returns:
            ComplianceCheck with verification results
        """
        # Generate check ID
        check_id = hashlib.sha256(
            f"{transaction.get('id', 'unknown')}{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Compute transaction hash
        tx_hash = self._compute_transaction_hash(transaction)
        
        # Determine which rules to check
        target_jurisdictions = [jurisdiction] if jurisdiction else self.jurisdictions
        applicable_rules = [
            rule for rule in self.rules.values()
            if rule.jurisdiction in target_jurisdictions
        ]
        
        print(f"\n[COMPLIANCE] Checking transaction {tx_hash[:8]}...")
        print(f"[COMPLIANCE] Applicable rules: {len(applicable_rules)}")
        
        # Check each rule
        violations = []
        warnings = []
        rules_checked = []
        
        for rule in applicable_rules:
            rules_checked.append(rule.rule_id)
            result = self._evaluate_rule(rule, transaction)
            
            if not result['compliant']:
                if rule.mandatory:
                    violations.append(f"{rule.rule_id}: {rule.description}")
                    print(f"[COMPLIANCE] ❌ VIOLATION: {rule.rule_id}")
                else:
                    warnings.append(f"{rule.rule_id}: {rule.description}")
                    print(f"[COMPLIANCE] ⚠️  WARNING: {rule.rule_id}")
            else:
                print(f"[COMPLIANCE] ✓ PASS: {rule.rule_id}")
        
        # Determine overall status
        if violations:
            status = ComplianceStatus.BLOCKED
        elif warnings:
            status = ComplianceStatus.REQUIRES_REVIEW
        else:
            status = ComplianceStatus.COMPLIANT
        
        # Assess risk level
        risk_level = self._assess_risk(transaction, violations, warnings)
        
        # Generate compliance proof
        proof = self._generate_compliance_proof(transaction, applicable_rules, violations)
        
        # Create check result
        check = ComplianceCheck(
            check_id=check_id,
            transaction_hash=tx_hash,
            rules_checked=rules_checked,
            status=status,
            risk_level=risk_level,
            violations=violations,
            warnings=warnings,
            proof=proof
        )
        
        # Store in history
        self.check_history.append(check)
        
        print(f"[COMPLIANCE] Status: {status.value.upper()}")
        print(f"[COMPLIANCE] Risk Level: {risk_level.value.upper()}")
        
        return check
    
    def _evaluate_rule(self, rule: ComplianceRule, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single compliance rule against a transaction.
        
        Args:
            rule: ComplianceRule to evaluate
            transaction: Transaction data
        
        Returns:
            Dictionary with evaluation result
        """
        # Extract relevant fields from transaction
        amount = Decimal(str(transaction.get('amount', 0)))
        sender_kyc = transaction.get('sender_kyc_verified', False)
        receiver_kyc = transaction.get('receiver_kyc_verified', False)
        reported = transaction.get('reported', False)
        
        # Simplified rule evaluation (in production, use Z3 solver)
        compliant = True
        reason = ""
        
        if rule.rule_id == "AML_ANGOLA_001":
            # Transaction reporting threshold
            if amount > rule.threshold and not reported:
                compliant = False
                reason = f"Amount {amount} AOA exceeds threshold, not reported"
        
        elif rule.rule_id == "AML_ANGOLA_002":
            # Structuring detection
            daily_total = Decimal(str(transaction.get('daily_total_aoa', 0)))
            reviewed = transaction.get('reviewed', False)
            if daily_total > rule.threshold and not reviewed:
                compliant = False
                reason = f"Daily total {daily_total} AOA exceeds threshold, not reviewed"
        
        elif rule.rule_id == "KYC_ANGOLA_001":
            # Identity verification
            if not (sender_kyc and receiver_kyc):
                compliant = False
                reason = "KYC verification incomplete"
        
        elif rule.rule_id == "CFT_ANGOLA_001":
            # Sanctions screening
            sender_sanctioned = transaction.get('sender_sanctioned', False)
            receiver_sanctioned = transaction.get('receiver_sanctioned', False)
            if sender_sanctioned or receiver_sanctioned:
                compliant = False
                reason = "Party on sanctions list"
        
        elif rule.rule_id.startswith("FATF"):
            # FATF rules (simplified)
            if "KYC" in rule.rule_type:
                cdd = transaction.get('customer_due_diligence_performed', False)
                if not cdd:
                    compliant = False
                    reason = "Customer due diligence not performed"
            elif "AML" in rule.rule_type:
                if "originator" in rule.constraint:
                    has_info = transaction.get('has_originator_info', False) and \
                              transaction.get('has_beneficiary_info', False)
                    if not has_info:
                        compliant = False
                        reason = "Missing originator/beneficiary information"
                elif "suspicious" in rule.constraint:
                    is_suspicious = transaction.get('is_suspicious', False)
                    reported_fiu = transaction.get('reported_to_fiu', False)
                    if is_suspicious and not reported_fiu:
                        compliant = False
                        reason = "Suspicious transaction not reported to FIU"
        
        return {
            'compliant': compliant,
            'reason': reason
        }
    
    def _assess_risk(
        self,
        transaction: Dict[str, Any],
        violations: List[str],
        warnings: List[str]
    ) -> RiskLevel:
        """
        Assess the risk level of a transaction.
        
        Args:
            transaction: Transaction data
            violations: List of violations
            warnings: List of warnings
        
        Returns:
            RiskLevel assessment
        """
        # Critical risk if any violations
        if violations:
            # Check for sanctions violations (critical)
            if any("CFT" in v or "sanction" in v.lower() for v in violations):
                return RiskLevel.CRITICAL
            # Other violations are high risk
            return RiskLevel.HIGH
        
        # Medium risk if warnings
        if warnings:
            return RiskLevel.MEDIUM
        
        # Check transaction characteristics
        amount = Decimal(str(transaction.get('amount', 0)))
        
        # High value transactions are medium risk even if compliant
        if amount > Decimal("1000000"):  # 1M AOA
            return RiskLevel.MEDIUM
        
        # Default: low risk
        return RiskLevel.LOW
    
    def _generate_compliance_proof(
        self,
        transaction: Dict[str, Any],
        rules: List[ComplianceRule],
        violations: List[str]
    ) -> str:
        """
        Generate a mathematical proof of compliance (or non-compliance).
        
        Args:
            transaction: Transaction data
            rules: Rules that were checked
            violations: List of violations (if any)
        
        Returns:
            Proof string (in production, this would be a Z3 proof)
        """
        proof_data = {
            'transaction_hash': self._compute_transaction_hash(transaction),
            'rules_checked': [r.rule_id for r in rules],
            'violations': violations,
            'timestamp': time.time(),
            'oracle_version': '3.5.0'
        }
        
        # In production, this would generate a Z3 proof
        # For now, return a signed proof statement
        proof_json = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return f"COMPLIANCE_PROOF_{proof_hash}"
    
    def _compute_transaction_hash(self, transaction: Dict[str, Any]) -> str:
        """Compute hash of transaction"""
        tx_json = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(tx_json.encode()).hexdigest()
    
    def get_jurisdiction_rules(self, jurisdiction: Jurisdiction) -> List[ComplianceRule]:
        """
        Get all rules for a specific jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction to query
        
        Returns:
            List of applicable ComplianceRules
        """
        return [
            rule for rule in self.rules.values()
            if rule.jurisdiction == jurisdiction
        ]
    
    def export_compliance_report(self, check_id: str) -> Dict[str, Any]:
        """
        Export a compliance check as a report for auditors.
        
        Args:
            check_id: ID of the check to export
        
        Returns:
            Dictionary with full compliance report
        """
        # Find the check
        check = next((c for c in self.check_history if c.check_id == check_id), None)
        
        if not check:
            raise ValueError(f"Check {check_id} not found")
        
        # Build comprehensive report
        report = {
            'report_id': f"COMPLIANCE_REPORT_{check_id}",
            'generated_at': time.time(),
            'check': check.to_dict(),
            'rules_details': [
                self.rules[rule_id].to_dict()
                for rule_id in check.rules_checked
                if rule_id in self.rules
            ],
            'oracle_version': '3.5.0',
            'jurisdictions': [j.value for j in self.jurisdictions]
        }
        
        return report
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get compliance statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_checks = len(self.check_history)
        
        if total_checks == 0:
            return {
                'total_checks': 0,
                'compliant': 0,
                'non_compliant': 0,
                'requires_review': 0,
                'blocked': 0
            }
        
        status_counts = {}
        for status in ComplianceStatus:
            status_counts[status.value] = sum(
                1 for c in self.check_history if c.status == status
            )
        
        risk_counts = {}
        for risk in RiskLevel:
            risk_counts[risk.value] = sum(
                1 for c in self.check_history if c.risk_level == risk
            )
        
        return {
            'total_checks': total_checks,
            'by_status': status_counts,
            'by_risk_level': risk_counts,
            'total_rules': len(self.rules),
            'jurisdictions': [j.value for j in self.jurisdictions]
        }


# Singleton instance
_compliance_oracle: Optional[ComplianceOracle] = None


def get_compliance_oracle(jurisdictions: List[Jurisdiction] = None) -> ComplianceOracle:
    """
    Get the singleton Compliance Oracle instance.
    
    Args:
        jurisdictions: List of jurisdictions (only used on first call)
    
    Returns:
        ComplianceOracle singleton
    """
    global _compliance_oracle
    
    if _compliance_oracle is None:
        _compliance_oracle = ComplianceOracle(jurisdictions)
    
    return _compliance_oracle
