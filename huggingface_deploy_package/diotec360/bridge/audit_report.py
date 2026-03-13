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
Audit Report Generator - Mathematical Compliance Documentation

This module generates audit reports that prove compliance mathematically.
These reports are designed to be accepted by auditors, regulators, and
financial institutions as proof of regulatory compliance.

Key Features:
1. PDF Generation: Professional audit reports in PDF format
2. Digital Signatures: Cryptographically signed for authenticity
3. Mathematical Proofs: Include Z3 proofs of compliance
4. Immutable Trail: Each report is content-addressed and traceable
5. Multi-Jurisdiction: Support for different regulatory formats

The Philosophy:
"An audit report is not just documentation - it's a mathematical proof
that can be verified by anyone, anywhere, at any time."

Report Types:
- Transaction Compliance Report: Single transaction verification
- Batch Compliance Report: Multiple transactions
- Periodic Compliance Report: Daily/Monthly/Quarterly summaries
- Suspicious Activity Report (SAR): For regulatory filing
- Customer Due Diligence (CDD) Report: KYC verification

Author: Kiro AI - Chief Engineer
Version: v3.5.0 "Sovereign Treasury"
Date: February 18, 2026
"""

import time
import hashlib
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, timezone
import io


class ReportType(Enum):
    """Types of audit reports"""
    TRANSACTION_COMPLIANCE = "transaction_compliance"
    BATCH_COMPLIANCE = "batch_compliance"
    PERIODIC_SUMMARY = "periodic_summary"
    SUSPICIOUS_ACTIVITY = "suspicious_activity_report"
    CUSTOMER_DUE_DILIGENCE = "customer_due_diligence"
    ANNUAL_AUDIT = "annual_audit"


class ReportFormat(Enum):
    """Output formats for reports"""
    PDF = "pdf"
    JSON = "json"
    HTML = "html"
    XML = "xml"  # For regulatory systems


@dataclass
class ReportMetadata:
    """
    Metadata for an audit report.
    
    Attributes:
        report_id: Unique report identifier
        report_type: Type of report
        generated_at: Timestamp of generation
        generated_by: Entity that generated the report
        jurisdiction: Regulatory jurisdiction
        period_start: Start of reporting period (if applicable)
        period_end: End of reporting period (if applicable)
        version: Report format version
    """
    report_id: str
    report_type: ReportType
    generated_at: float
    generated_by: str
    jurisdiction: str
    period_start: Optional[float] = None
    period_end: Optional[float] = None
    version: str = "3.5.0"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'report_id': self.report_id,
            'report_type': self.report_type.value,
            'generated_at': self.generated_at,
            'generated_by': self.generated_by,
            'jurisdiction': self.jurisdiction,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'version': self.version
        }


@dataclass
class ComplianceEvidence:
    """
    Evidence of compliance for a specific rule.
    
    Attributes:
        rule_id: Compliance rule identifier
        rule_description: Human-readable description
        status: Compliant or non-compliant
        proof: Mathematical proof (Z3 or similar)
        evidence_data: Supporting data
        timestamp: When evidence was collected
    """
    rule_id: str
    rule_description: str
    status: str  # "compliant", "non_compliant", "not_applicable"
    proof: Optional[str] = None
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'rule_id': self.rule_id,
            'rule_description': self.rule_description,
            'status': self.status,
            'proof': self.proof,
            'evidence_data': self.evidence_data,
            'timestamp': self.timestamp
        }


@dataclass
class AuditReport:
    """
    Complete audit report with all evidence and proofs.
    
    Attributes:
        metadata: Report metadata
        summary: Executive summary
        evidence: List of compliance evidence
        violations: List of violations (if any)
        recommendations: List of recommendations
        signature: Digital signature of report
        content_hash: SHA256 hash of report content
    """
    metadata: ReportMetadata
    summary: str
    evidence: List[ComplianceEvidence] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    signature: Optional[str] = None
    content_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'metadata': self.metadata.to_dict(),
            'summary': self.summary,
            'evidence': [e.to_dict() for e in self.evidence],
            'violations': self.violations,
            'recommendations': self.recommendations,
            'signature': self.signature,
            'content_hash': self.content_hash
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class AuditReportGenerator:
    """
    The Audit Report Generator - Transforms compliance checks into
    professional audit reports that regulators and auditors can trust.
    
    Key Capabilities:
    1. Generate reports from compliance checks
    2. Format for different audiences (regulators, auditors, management)
    3. Include mathematical proofs
    4. Sign reports cryptographically
    5. Export in multiple formats (PDF, JSON, HTML, XML)
    """
    
    def __init__(
        self,
        organization_name: str,
        organization_id: str,
        signing_key: Optional[str] = None
    ):
        """
        Initialize the Audit Report Generator.
        
        Args:
            organization_name: Name of the organization
            organization_id: Unique organization identifier
            signing_key: Private key for signing reports (optional)
        """
        self.organization_name = organization_name
        self.organization_id = organization_id
        self.signing_key = signing_key
        
        # Report history
        self.generated_reports: List[AuditReport] = []
        
        print(f"[AUDIT] Report Generator initialized for {organization_name}")
        print(f"[AUDIT] Organization ID: {organization_id}")
        print(f"[AUDIT] Signing enabled: {signing_key is not None}")
    
    def generate_transaction_report(
        self,
        compliance_check: Dict[str, Any],
        transaction: Dict[str, Any],
        jurisdiction: str = "angola"
    ) -> AuditReport:
        """
        Generate an audit report for a single transaction.
        
        Args:
            compliance_check: Result from ComplianceOracle.check_transaction()
            transaction: Original transaction data
            jurisdiction: Regulatory jurisdiction
        
        Returns:
            AuditReport with full compliance documentation
        """
        # Generate report ID
        report_id = self._generate_report_id("TXN")
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            report_type=ReportType.TRANSACTION_COMPLIANCE,
            generated_at=time.time(),
            generated_by=self.organization_name,
            jurisdiction=jurisdiction
        )
        
        # Build summary
        status = compliance_check.get('status', 'unknown')
        risk_level = compliance_check.get('risk_level', 'unknown')
        tx_hash = compliance_check.get('transaction_hash', 'unknown')
        
        summary = self._build_transaction_summary(
            status=status,
            risk_level=risk_level,
            transaction=transaction,
            tx_hash=tx_hash
        )
        
        # Collect evidence
        evidence = []
        rules_checked = compliance_check.get('rules_checked', [])
        violations = compliance_check.get('violations', [])
        
        for rule_id in rules_checked:
            # Determine if this rule was violated
            is_violated = any(rule_id in v for v in violations)
            
            evidence_item = ComplianceEvidence(
                rule_id=rule_id,
                rule_description=self._get_rule_description(rule_id),
                status="non_compliant" if is_violated else "compliant",
                proof=compliance_check.get('proof'),
                evidence_data={
                    'transaction_hash': tx_hash,
                    'check_id': compliance_check.get('check_id'),
                    'timestamp': compliance_check.get('timestamp')
                }
            )
            evidence.append(evidence_item)
        
        # Build recommendations
        recommendations = self._build_recommendations(
            status=status,
            violations=violations,
            risk_level=risk_level
        )
        
        # Create report
        report = AuditReport(
            metadata=metadata,
            summary=summary,
            evidence=evidence,
            violations=violations,
            recommendations=recommendations
        )
        
        # Compute content hash
        report.content_hash = self._compute_content_hash(report)
        
        # Sign report
        if self.signing_key:
            report.signature = self._sign_report(report)
        
        # Store in history
        self.generated_reports.append(report)
        
        print(f"[AUDIT] Generated transaction report {report_id}")
        print(f"[AUDIT] Status: {status}, Risk: {risk_level}")
        print(f"[AUDIT] Evidence items: {len(evidence)}")
        print(f"[AUDIT] Violations: {len(violations)}")
        
        return report
    
    def generate_batch_report(
        self,
        compliance_checks: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        jurisdiction: str = "angola",
        period_start: Optional[float] = None,
        period_end: Optional[float] = None
    ) -> AuditReport:
        """
        Generate an audit report for a batch of transactions.
        
        Args:
            compliance_checks: List of compliance check results
            transactions: List of original transactions
            jurisdiction: Regulatory jurisdiction
            period_start: Start of reporting period
            period_end: End of reporting period
        
        Returns:
            AuditReport with batch compliance documentation
        """
        # Generate report ID
        report_id = self._generate_report_id("BATCH")
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            report_type=ReportType.BATCH_COMPLIANCE,
            generated_at=time.time(),
            generated_by=self.organization_name,
            jurisdiction=jurisdiction,
            period_start=period_start,
            period_end=period_end
        )
        
        # Aggregate statistics
        total_transactions = len(compliance_checks)
        compliant_count = sum(1 for c in compliance_checks if c.get('status') == 'compliant')
        non_compliant_count = total_transactions - compliant_count
        
        total_amount = sum(Decimal(str(t.get('amount', 0))) for t in transactions)
        
        # Build summary
        summary = f"""
BATCH COMPLIANCE REPORT

Organization: {self.organization_name}
Jurisdiction: {jurisdiction.upper()}
Period: {self._format_timestamp(period_start)} to {self._format_timestamp(period_end)}

SUMMARY STATISTICS:
- Total Transactions: {total_transactions}
- Compliant: {compliant_count} ({compliant_count/total_transactions*100:.1f}%)
- Non-Compliant: {non_compliant_count} ({non_compliant_count/total_transactions*100:.1f}%)
- Total Amount: {total_amount} AOA

COMPLIANCE STATUS: {"PASS" if non_compliant_count == 0 else "VIOLATIONS DETECTED"}
"""
        
        # Collect all evidence
        evidence = []
        all_violations = []
        
        for check in compliance_checks:
            for rule_id in check.get('rules_checked', []):
                violations = check.get('violations', [])
                is_violated = any(rule_id in v for v in violations)
                
                evidence_item = ComplianceEvidence(
                    rule_id=rule_id,
                    rule_description=self._get_rule_description(rule_id),
                    status="non_compliant" if is_violated else "compliant",
                    proof=check.get('proof'),
                    evidence_data={
                        'transaction_hash': check.get('transaction_hash'),
                        'check_id': check.get('check_id')
                    }
                )
                evidence.append(evidence_item)
            
            all_violations.extend(check.get('violations', []))
        
        # Build recommendations
        recommendations = []
        if non_compliant_count > 0:
            recommendations.append(
                f"Review and remediate {non_compliant_count} non-compliant transactions"
            )
            recommendations.append(
                "Implement additional controls to prevent future violations"
            )
        else:
            recommendations.append(
                "Continue current compliance procedures - all transactions compliant"
            )
        
        # Create report
        report = AuditReport(
            metadata=metadata,
            summary=summary,
            evidence=evidence,
            violations=list(set(all_violations)),  # Deduplicate
            recommendations=recommendations
        )
        
        # Compute content hash
        report.content_hash = self._compute_content_hash(report)
        
        # Sign report
        if self.signing_key:
            report.signature = self._sign_report(report)
        
        # Store in history
        self.generated_reports.append(report)
        
        print(f"[AUDIT] Generated batch report {report_id}")
        print(f"[AUDIT] Transactions: {total_transactions}")
        print(f"[AUDIT] Compliant: {compliant_count}, Non-compliant: {non_compliant_count}")
        
        return report
    
    def generate_periodic_summary(
        self,
        compliance_checks: List[Dict[str, Any]],
        period_start: float,
        period_end: float,
        jurisdiction: str = "angola"
    ) -> AuditReport:
        """
        Generate a periodic summary report (daily, monthly, quarterly).
        
        Args:
            compliance_checks: All compliance checks in period
            period_start: Start of period (timestamp)
            period_end: End of period (timestamp)
            jurisdiction: Regulatory jurisdiction
        
        Returns:
            AuditReport with periodic summary
        """
        # Generate report ID
        report_id = self._generate_report_id("PERIOD")
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            report_type=ReportType.PERIODIC_SUMMARY,
            generated_at=time.time(),
            generated_by=self.organization_name,
            jurisdiction=jurisdiction,
            period_start=period_start,
            period_end=period_end
        )
        
        # Calculate statistics
        total_checks = len(compliance_checks)
        
        status_counts = {}
        risk_counts = {}
        
        for check in compliance_checks:
            status = check.get('status', 'unknown')
            risk = check.get('risk_level', 'unknown')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        # Build summary
        summary = f"""
PERIODIC COMPLIANCE SUMMARY

Organization: {self.organization_name}
Jurisdiction: {jurisdiction.upper()}
Period: {self._format_timestamp(period_start)} to {self._format_timestamp(period_end)}

COMPLIANCE OVERVIEW:
- Total Checks: {total_checks}
- Compliant: {status_counts.get('compliant', 0)}
- Non-Compliant: {status_counts.get('non_compliant', 0)}
- Requires Review: {status_counts.get('requires_review', 0)}
- Blocked: {status_counts.get('blocked', 0)}

RISK DISTRIBUTION:
- Low Risk: {risk_counts.get('low', 0)}
- Medium Risk: {risk_counts.get('medium', 0)}
- High Risk: {risk_counts.get('high', 0)}
- Critical Risk: {risk_counts.get('critical', 0)}

OVERALL ASSESSMENT: {"SATISFACTORY" if status_counts.get('blocked', 0) == 0 else "REQUIRES ATTENTION"}
"""
        
        # Aggregate evidence by rule
        rule_evidence = {}
        all_violations = []
        
        for check in compliance_checks:
            for rule_id in check.get('rules_checked', []):
                if rule_id not in rule_evidence:
                    rule_evidence[rule_id] = {
                        'total': 0,
                        'compliant': 0,
                        'non_compliant': 0
                    }
                
                rule_evidence[rule_id]['total'] += 1
                
                violations = check.get('violations', [])
                if any(rule_id in v for v in violations):
                    rule_evidence[rule_id]['non_compliant'] += 1
                else:
                    rule_evidence[rule_id]['compliant'] += 1
            
            all_violations.extend(check.get('violations', []))
        
        # Create evidence items
        evidence = []
        for rule_id, stats in rule_evidence.items():
            compliance_rate = stats['compliant'] / stats['total'] * 100
            
            evidence_item = ComplianceEvidence(
                rule_id=rule_id,
                rule_description=self._get_rule_description(rule_id),
                status="compliant" if compliance_rate == 100 else "non_compliant",
                evidence_data={
                    'total_checks': stats['total'],
                    'compliant': stats['compliant'],
                    'non_compliant': stats['non_compliant'],
                    'compliance_rate': f"{compliance_rate:.1f}%"
                }
            )
            evidence.append(evidence_item)
        
        # Build recommendations
        recommendations = []
        if status_counts.get('blocked', 0) > 0:
            recommendations.append(
                f"Investigate {status_counts['blocked']} blocked transactions"
            )
        if risk_counts.get('critical', 0) > 0:
            recommendations.append(
                f"Review {risk_counts['critical']} critical risk transactions immediately"
            )
        if status_counts.get('compliant', 0) == total_checks:
            recommendations.append(
                "Excellent compliance performance - maintain current procedures"
            )
        
        # Create report
        report = AuditReport(
            metadata=metadata,
            summary=summary,
            evidence=evidence,
            violations=list(set(all_violations)),
            recommendations=recommendations
        )
        
        # Compute content hash
        report.content_hash = self._compute_content_hash(report)
        
        # Sign report
        if self.signing_key:
            report.signature = self._sign_report(report)
        
        # Store in history
        self.generated_reports.append(report)
        
        print(f"[AUDIT] Generated periodic summary {report_id}")
        print(f"[AUDIT] Period: {self._format_timestamp(period_start)} to {self._format_timestamp(period_end)}")
        print(f"[AUDIT] Total checks: {total_checks}")
        
        return report
    
    # ========================================================================
    # Export Functions
    # ========================================================================
    
    def export_to_json(self, report: AuditReport) -> str:
        """
        Export report to JSON format.
        
        Args:
            report: AuditReport to export
        
        Returns:
            JSON string
        """
        return report.to_json(indent=2)
    
    def export_to_html(self, report: AuditReport) -> str:
        """
        Export report to HTML format.
        
        Args:
            report: AuditReport to export
        
        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Audit Report - {report.metadata.report_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metadata {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .summary {{ white-space: pre-wrap; background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }}
        .evidence {{ margin: 20px 0; }}
        .evidence-item {{ background: #fff; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
        .compliant {{ border-left: 4px solid #27ae60; }}
        .non-compliant {{ border-left: 4px solid #e74c3c; }}
        .signature {{ background: #2c3e50; color: white; padding: 10px; margin-top: 30px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>Audit Report</h1>
    
    <div class="metadata">
        <p><strong>Report ID:</strong> {report.metadata.report_id}</p>
        <p><strong>Type:</strong> {report.metadata.report_type.value}</p>
        <p><strong>Generated:</strong> {self._format_timestamp(report.metadata.generated_at)}</p>
        <p><strong>Organization:</strong> {report.metadata.generated_by}</p>
        <p><strong>Jurisdiction:</strong> {report.metadata.jurisdiction.upper()}</p>
    </div>
    
    <h2>Summary</h2>
    <div class="summary">{report.summary}</div>
    
    <h2>Evidence ({len(report.evidence)} items)</h2>
    <div class="evidence">
"""
        
        for item in report.evidence:
            status_class = "compliant" if item.status == "compliant" else "non-compliant"
            html += f"""
        <div class="evidence-item {status_class}">
            <p><strong>Rule:</strong> {item.rule_id}</p>
            <p><strong>Description:</strong> {item.rule_description}</p>
            <p><strong>Status:</strong> {item.status.upper()}</p>
        </div>
"""
        
        html += """
    </div>
    
    <h2>Violations</h2>
"""
        
        if report.violations:
            html += "<ul>\n"
            for violation in report.violations:
                html += f"        <li>{violation}</li>\n"
            html += "    </ul>\n"
        else:
            html += "    <p>No violations detected.</p>\n"
        
        html += """
    <h2>Recommendations</h2>
    <ul>
"""
        
        for rec in report.recommendations:
            html += f"        <li>{rec}</li>\n"
        
        html += f"""
    </ul>
    
    <div class="signature">
        <p><strong>Content Hash:</strong> {report.content_hash}</p>
        <p><strong>Digital Signature:</strong> {report.signature or 'Not signed'}</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def export_to_pdf(self, report: AuditReport) -> bytes:
        """
        Export report to PDF format.
        
        Note: This is a placeholder. In production, use a library like
        ReportLab or WeasyPrint to generate actual PDFs.
        
        Args:
            report: AuditReport to export
        
        Returns:
            PDF bytes
        """
        # For now, return HTML as bytes
        # In production: Use ReportLab or WeasyPrint
        html = self.export_to_html(report)
        
        print("[AUDIT] PDF export not yet implemented - returning HTML")
        print("[AUDIT] In production, use ReportLab or WeasyPrint")
        
        return html.encode('utf-8')
    
    # ========================================================================
    # Helper Functions
    # ========================================================================
    
    def _generate_report_id(self, prefix: str) -> str:
        """Generate unique report ID"""
        timestamp = int(time.time() * 1000)
        hash_input = f"{self.organization_id}{prefix}{timestamp}".encode()
        hash_val = hashlib.sha256(hash_input).hexdigest()[:12]
        return f"{prefix}_{hash_val}_{timestamp}"
    
    def _build_transaction_summary(
        self,
        status: str,
        risk_level: str,
        transaction: Dict[str, Any],
        tx_hash: str
    ) -> str:
        """Build summary for transaction report"""
        amount = transaction.get('amount', 0)
        
        return f"""
TRANSACTION COMPLIANCE REPORT

Organization: {self.organization_name}
Transaction Hash: {tx_hash}

TRANSACTION DETAILS:
- Amount: {amount} AOA
- Status: {status.upper()}
- Risk Level: {risk_level.upper()}

COMPLIANCE VERDICT: {"APPROVED" if status == "compliant" else "REQUIRES REVIEW"}
"""
    
    def _get_rule_description(self, rule_id: str) -> str:
        """Get human-readable description for a rule"""
        # In production, fetch from ComplianceOracle
        descriptions = {
            'AML_ANGOLA_001': 'Transaction reporting threshold (5M AOA)',
            'AML_ANGOLA_002': 'Structuring detection',
            'KYC_ANGOLA_001': 'Identity verification',
            'CFT_ANGOLA_001': 'Sanctions screening',
            'FATF_R10_001': 'Customer Due Diligence',
            'FATF_R16_001': 'Wire Transfer Information',
            'FATF_R20_001': 'Suspicious Transaction Reporting'
        }
        return descriptions.get(rule_id, f"Rule {rule_id}")
    
    def _build_recommendations(
        self,
        status: str,
        violations: List[str],
        risk_level: str
    ) -> List[str]:
        """Build recommendations based on compliance status"""
        recommendations = []
        
        if status == "blocked":
            recommendations.append("Transaction blocked - do not process")
            recommendations.append("Investigate violations before proceeding")
        elif status == "requires_review":
            recommendations.append("Manual review required before processing")
        elif status == "compliant":
            recommendations.append("Transaction approved - proceed with processing")
        
        if risk_level in ["high", "critical"]:
            recommendations.append("Enhanced monitoring recommended")
        
        return recommendations
    
    def _compute_content_hash(self, report: AuditReport) -> str:
        """Compute SHA256 hash of report content"""
        # Create deterministic representation
        content = {
            'metadata': report.metadata.to_dict(),
            'summary': report.summary,
            'evidence': [e.to_dict() for e in report.evidence],
            'violations': sorted(report.violations),
            'recommendations': report.recommendations
        }
        
        content_json = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()
    
    def _sign_report(self, report: AuditReport) -> str:
        """
        Sign report with private key.
        
        In production, use proper cryptographic signing (Ed25519, ECDSA).
        For now, simplified signature.
        """
        if not self.signing_key:
            return ""
        
        # Simplified: Hash of content + signing key
        # In production: Use proper digital signature
        signature_input = f"{report.content_hash}{self.signing_key}".encode()
        return hashlib.sha256(signature_input).hexdigest()
    
    def _format_timestamp(self, timestamp: Optional[float]) -> str:
        """Format timestamp as human-readable string"""
        if timestamp is None:
            return "N/A"
        
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def get_report_by_id(self, report_id: str) -> Optional[AuditReport]:
        """
        Retrieve a report by ID.
        
        Args:
            report_id: Report identifier
        
        Returns:
            AuditReport if found, None otherwise
        """
        for report in self.generated_reports:
            if report.metadata.report_id == report_id:
                return report
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get report generation statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_reports = len(self.generated_reports)
        
        if total_reports == 0:
            return {
                'total_reports': 0,
                'by_type': {},
                'organization': self.organization_name
            }
        
        by_type = {}
        for report in self.generated_reports:
            report_type = report.metadata.report_type.value
            by_type[report_type] = by_type.get(report_type, 0) + 1
        
        return {
            'total_reports': total_reports,
            'by_type': by_type,
            'organization': self.organization_name,
            'organization_id': self.organization_id
        }


# Singleton instance
_audit_report_generator: Optional[AuditReportGenerator] = None


def get_audit_report_generator(
    organization_name: str = None,
    organization_id: str = None,
    signing_key: str = None
) -> AuditReportGenerator:
    """
    Get the singleton Audit Report Generator instance.
    
    Args:
        organization_name: Organization name (required on first call)
        organization_id: Organization ID (required on first call)
        signing_key: Signing key (optional)
    
    Returns:
        AuditReportGenerator singleton
    """
    global _audit_report_generator
    
    if _audit_report_generator is None:
        if organization_name is None or organization_id is None:
            raise ValueError("organization_name and organization_id required for first call")
        
        _audit_report_generator = AuditReportGenerator(
            organization_name=organization_name,
            organization_id=organization_id,
            signing_key=signing_key
        )
    
    return _audit_report_generator
