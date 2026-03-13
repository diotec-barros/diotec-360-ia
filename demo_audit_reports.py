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
Demo: Audit Report Generator - Mathematical Compliance Documentation

This demo shows how the Audit Report Generator transforms compliance checks
into professional audit reports that regulators and auditors can trust.

Scenarios:
1. Single Transaction Report: Generate report for one transaction
2. Batch Report: Generate report for multiple transactions
3. Periodic Summary: Generate daily/monthly summary
4. Export Formats: JSON, HTML, PDF

Author: Kiro AI
Date: February 18, 2026
"""

import time
from decimal import Decimal

from diotec360.bridge.compliance_oracle import (
    ComplianceOracle,
    Jurisdiction,
    ComplianceStatus,
    RiskLevel
)
from diotec360.bridge.audit_report import (
    AuditReportGenerator,
    ReportType,
    ReportFormat
)


def demo_single_transaction_report():
    """Demo 1: Generate report for a single transaction"""
    print("\n" + "="*80)
    print("DEMO 1: SINGLE TRANSACTION AUDIT REPORT")
    print("="*80)
    
    # Initialize systems
    oracle = ComplianceOracle(jurisdictions=[Jurisdiction.ANGOLA, Jurisdiction.INTERNATIONAL])
    generator = AuditReportGenerator(
        organization_name="DIOTEC 360",
        organization_id="DIOTEC360_AO",
        signing_key="demo_signing_key_12345"
    )
    
    # Create a compliant transaction
    transaction = {
        'id': 'TXN_001',
        'amount': 1000000,  # 1M AOA (below threshold)
        'sender_kyc_verified': True,
        'receiver_kyc_verified': True,
        'sender_sanctioned': False,
        'receiver_sanctioned': False,
        'customer_due_diligence_performed': True,
        'has_originator_info': True,
        'has_beneficiary_info': True,
        'is_suspicious': False
    }
    
    # Check compliance
    print("\n[STEP 1] Checking transaction compliance...")
    check = oracle.check_transaction(transaction, Jurisdiction.ANGOLA)
    
    # Generate audit report
    print("\n[STEP 2] Generating audit report...")
    report = generator.generate_transaction_report(
        compliance_check=check.to_dict(),
        transaction=transaction,
        jurisdiction="angola"
    )
    
    # Display report
    print("\n[STEP 3] Audit Report Generated:")
    print(f"  Report ID: {report.metadata.report_id}")
    print(f"  Type: {report.metadata.report_type.value}")
    print(f"  Status: {check.status.value}")
    print(f"  Risk Level: {check.risk_level.value}")
    print(f"  Evidence Items: {len(report.evidence)}")
    print(f"  Violations: {len(report.violations)}")
    print(f"  Content Hash: {report.content_hash}")
    print(f"  Signed: {report.signature is not None}")
    
    # Export to JSON
    print("\n[STEP 4] Exporting to JSON...")
    json_report = generator.export_to_json(report)
    print(f"  JSON size: {len(json_report)} bytes")
    
    # Export to HTML
    print("\n[STEP 5] Exporting to HTML...")
    html_report = generator.export_to_html(report)
    print(f"  HTML size: {len(html_report)} bytes")
    
    # Save HTML to file
    with open('audit_report_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("  ✅ Saved to: audit_report_demo.html")
    
    print("\n✅ Demo 1 Complete: Single transaction report generated and exported")
    
    return report


def demo_batch_report():
    """Demo 2: Generate report for a batch of transactions"""
    print("\n" + "="*80)
    print("DEMO 2: BATCH COMPLIANCE AUDIT REPORT")
    print("="*80)
    
    # Initialize systems
    oracle = ComplianceOracle(jurisdictions=[Jurisdiction.ANGOLA])
    generator = AuditReportGenerator(
        organization_name="DIOTEC 360",
        organization_id="DIOTEC360_AO",
        signing_key="demo_signing_key_12345"
    )
    
    # Create batch of transactions (mix of compliant and non-compliant)
    transactions = [
        # Compliant transaction
        {
            'id': 'TXN_001',
            'amount': 1000000,
            'sender_kyc_verified': True,
            'receiver_kyc_verified': True,
            'sender_sanctioned': False,
            'receiver_sanctioned': False
        },
        # Non-compliant: Above threshold, not reported
        {
            'id': 'TXN_002',
            'amount': 6000000,  # Above 5M threshold
            'reported': False,  # Not reported!
            'sender_kyc_verified': True,
            'receiver_kyc_verified': True,
            'sender_sanctioned': False,
            'receiver_sanctioned': False
        },
        # Compliant transaction
        {
            'id': 'TXN_003',
            'amount': 500000,
            'sender_kyc_verified': True,
            'receiver_kyc_verified': True,
            'sender_sanctioned': False,
            'receiver_sanctioned': False
        },
        # Non-compliant: KYC not verified
        {
            'id': 'TXN_004',
            'amount': 2000000,
            'sender_kyc_verified': False,  # KYC missing!
            'receiver_kyc_verified': True,
            'sender_sanctioned': False,
            'receiver_sanctioned': False
        },
        # Compliant transaction
        {
            'id': 'TXN_005',
            'amount': 750000,
            'sender_kyc_verified': True,
            'receiver_kyc_verified': True,
            'sender_sanctioned': False,
            'receiver_sanctioned': False
        }
    ]
    
    # Check all transactions
    print("\n[STEP 1] Checking batch of transactions...")
    checks = []
    for i, tx in enumerate(transactions, 1):
        print(f"  Checking transaction {i}/{len(transactions)}...")
        check = oracle.check_transaction(tx)
        checks.append(check.to_dict())
    
    # Generate batch report
    print("\n[STEP 2] Generating batch audit report...")
    period_start = time.time() - 86400  # 24 hours ago
    period_end = time.time()
    
    report = generator.generate_batch_report(
        compliance_checks=checks,
        transactions=transactions,
        jurisdiction="angola",
        period_start=period_start,
        period_end=period_end
    )
    
    # Display report
    print("\n[STEP 3] Batch Report Generated:")
    print(f"  Report ID: {report.metadata.report_id}")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Evidence Items: {len(report.evidence)}")
    print(f"  Violations: {len(report.violations)}")
    print(f"  Recommendations: {len(report.recommendations)}")
    
    # Show violations
    if report.violations:
        print("\n  Violations Detected:")
        for violation in report.violations:
            print(f"    - {violation}")
    
    # Export to HTML
    print("\n[STEP 4] Exporting to HTML...")
    html_report = generator.export_to_html(report)
    with open('batch_report_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("  ✅ Saved to: batch_report_demo.html")
    
    print("\n✅ Demo 2 Complete: Batch report generated with violations detected")
    
    return report


def demo_periodic_summary():
    """Demo 3: Generate periodic summary report"""
    print("\n" + "="*80)
    print("DEMO 3: PERIODIC COMPLIANCE SUMMARY")
    print("="*80)
    
    # Initialize systems
    oracle = ComplianceOracle(jurisdictions=[Jurisdiction.ANGOLA, Jurisdiction.INTERNATIONAL])
    generator = AuditReportGenerator(
        organization_name="DIOTEC 360",
        organization_id="DIOTEC360_AO",
        signing_key="demo_signing_key_12345"
    )
    
    # Simulate a day's worth of transactions
    print("\n[STEP 1] Simulating daily transactions...")
    
    checks = []
    
    # Generate 20 transactions with varying compliance
    for i in range(20):
        # Most transactions are compliant
        is_compliant = i % 5 != 0  # 80% compliant
        
        tx = {
            'id': f'TXN_{i:03d}',
            'amount': 500000 + (i * 100000),
            'sender_kyc_verified': is_compliant,
            'receiver_kyc_verified': is_compliant,
            'sender_sanctioned': False,
            'receiver_sanctioned': False,
            'customer_due_diligence_performed': is_compliant,
            'has_originator_info': is_compliant,
            'has_beneficiary_info': is_compliant,
            'is_suspicious': False
        }
        
        check = oracle.check_transaction(tx)
        checks.append(check.to_dict())
    
    print(f"  Generated {len(checks)} compliance checks")
    
    # Generate periodic summary
    print("\n[STEP 2] Generating periodic summary...")
    period_start = time.time() - 86400  # 24 hours ago
    period_end = time.time()
    
    report = generator.generate_periodic_summary(
        compliance_checks=checks,
        period_start=period_start,
        period_end=period_end,
        jurisdiction="angola"
    )
    
    # Display report
    print("\n[STEP 3] Periodic Summary Generated:")
    print(f"  Report ID: {report.metadata.report_id}")
    print(f"  Period: Last 24 hours")
    print(f"  Total Checks: {len(checks)}")
    print(f"  Evidence Items: {len(report.evidence)}")
    print(f"  Violations: {len(report.violations)}")
    
    # Show summary
    print("\n  Summary:")
    print(report.summary)
    
    # Export to HTML
    print("\n[STEP 4] Exporting to HTML...")
    html_report = generator.export_to_html(report)
    with open('periodic_summary_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("  ✅ Saved to: periodic_summary_demo.html")
    
    # Show statistics
    print("\n[STEP 5] Generator Statistics:")
    stats = generator.get_statistics()
    print(f"  Total Reports Generated: {stats['total_reports']}")
    print(f"  By Type:")
    for report_type, count in stats['by_type'].items():
        print(f"    - {report_type}: {count}")
    
    print("\n✅ Demo 3 Complete: Periodic summary generated")
    
    return report


def demo_report_verification():
    """Demo 4: Verify report integrity"""
    print("\n" + "="*80)
    print("DEMO 4: REPORT INTEGRITY VERIFICATION")
    print("="*80)
    
    # Initialize systems
    oracle = ComplianceOracle(jurisdictions=[Jurisdiction.ANGOLA])
    generator = AuditReportGenerator(
        organization_name="DIOTEC 360",
        organization_id="DIOTEC360_AO",
        signing_key="demo_signing_key_12345"
    )
    
    # Create transaction and generate report
    print("\n[STEP 1] Generating report...")
    transaction = {
        'id': 'TXN_VERIFY',
        'amount': 1000000,
        'sender_kyc_verified': True,
        'receiver_kyc_verified': True,
        'sender_sanctioned': False,
        'receiver_sanctioned': False
    }
    
    check = oracle.check_transaction(transaction)
    report = generator.generate_transaction_report(
        compliance_check=check.to_dict(),
        transaction=transaction,
        jurisdiction="angola"
    )
    
    print(f"  Report ID: {report.metadata.report_id}")
    print(f"  Content Hash: {report.content_hash}")
    print(f"  Signature: {report.signature[:32]}...")
    
    # Verify integrity
    print("\n[STEP 2] Verifying report integrity...")
    
    # Recompute content hash
    import hashlib
    import json
    
    content = {
        'metadata': report.metadata.to_dict(),
        'summary': report.summary,
        'evidence': [e.to_dict() for e in report.evidence],
        'violations': sorted(report.violations),
        'recommendations': report.recommendations
    }
    
    recomputed_hash = hashlib.sha256(
        json.dumps(content, sort_keys=True).encode()
    ).hexdigest()
    
    if recomputed_hash == report.content_hash:
        print("  ✅ Content hash verified - report has not been tampered with")
    else:
        print("  ❌ Content hash mismatch - report may have been modified")
    
    # Retrieve report by ID
    print("\n[STEP 3] Retrieving report by ID...")
    retrieved = generator.get_report_by_id(report.metadata.report_id)
    
    if retrieved:
        print(f"  ✅ Report retrieved successfully")
        print(f"  Report ID: {retrieved.metadata.report_id}")
        print(f"  Type: {retrieved.metadata.report_type.value}")
    else:
        print(f"  ❌ Report not found")
    
    print("\n✅ Demo 4 Complete: Report integrity verified")
    
    return report


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("AUDIT REPORT GENERATOR - COMPREHENSIVE DEMO")
    print("="*80)
    print("\nThis demo shows how the Audit Report Generator transforms")
    print("compliance checks into professional audit reports.")
    print("\nKey Features:")
    print("  1. Single Transaction Reports")
    print("  2. Batch Compliance Reports")
    print("  3. Periodic Summaries")
    print("  4. Multiple Export Formats (JSON, HTML, PDF)")
    print("  5. Digital Signatures")
    print("  6. Content Integrity Verification")
    
    try:
        # Run all demos
        report1 = demo_single_transaction_report()
        report2 = demo_batch_report()
        report3 = demo_periodic_summary()
        report4 = demo_report_verification()
        
        # Final summary
        print("\n" + "="*80)
        print("ALL DEMOS COMPLETE")
        print("="*80)
        print("\n✅ Generated Reports:")
        print(f"  1. Single Transaction: {report1.metadata.report_id}")
        print(f"  2. Batch Report: {report2.metadata.report_id}")
        print(f"  3. Periodic Summary: {report3.metadata.report_id}")
        print(f"  4. Verification Test: {report4.metadata.report_id}")
        
        print("\n✅ Exported Files:")
        print("  - audit_report_demo.html")
        print("  - batch_report_demo.html")
        print("  - periodic_summary_demo.html")
        
        print("\n🏛️ The Audit Report Generator is operational!")
        print("   Professional compliance documentation ready for regulators.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
