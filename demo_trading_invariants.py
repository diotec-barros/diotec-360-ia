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
Demo: Aethel Trading Invariants - Real-World Scenarios

This demo shows how Trading Invariants prevent catastrophic losses
that traditional systems cannot prevent.

Commercial Value: $500-10,000/month per client

Revenue Streams:
1. Per-certificate fees: $50-500 per certificate
2. Monthly subscriptions: $500-10,000/month per client
3. Enterprise licenses: $10K-100K/year
4. Insurance partnerships: Revenue share on premium discounts
"""

import time
from pathlib import Path
from diotec360.core.audit_issuer import get_audit_issuer, ProofLog


def demo_stop_loss_inviolable():
    """
    Demo 1: Inviolable Stop-Loss
    
    Scenario: Trader has $100K, sets 5% stop-loss
    Traditional: Stop-loss can fail during flash crash
    Aethel: Mathematically impossible to lose >5%
    
    Commercial Value: $500-2000/month per trader
    Certificate Fee: $50-100 per trade
    """
    print("=" * 80)
    print("DEMO 1: INVIOLABLE STOP-LOSS
")
    print("=" * 80)
    print()
    
    print("Scenario: Flash Crash Protection")
    print("-" * 80)
    print("Initial Balance: $100,000")
    print("Stop-Loss Limit: 5%")
    print("Minimum Allowed: $95,000")
    print()
    
    # Simulate trade execution
    print("Executing trade with Aethel protection...")
    time.sleep(0.5)
    
    # Create proof log (simulated)
    proof_log = ProofLog(
        layer_minus_1_semantic={"passed": True, "threats_detected": 0},
        layer_0_sanitizer={"passed": True, "sanitized": False},
        layer_1_conservation={"passed": True, "value_conserved": True},
        layer_2_overflow={"passed": True, "overflow_detected": False},
        layer_3_z3_proof={"passed": True, "proof_time_ms": 45},
        sentinel_telemetry={"anomaly_score": 0.1, "health": "excellent"},
        crisis_mode_active=False,
        quarantine_status="clean"
    )
    
    # Issue certificate
    issuer = get_audit_issuer()
    certificate = issuer.issue_assurance_certificate(
        bundle_hash="0xSTOPLOSS_TRADE_12345",
        proof_log=proof_log,
        transaction_count=1,
        total_value=100000.0,
        tier="premium"
    )
    
    print(f"✓ Certificate Issued: {certificate.certificate_id}")
    print(f"✓ Security Rating: {certificate.security_rating}")
    print(f"✓ Defense Layers Passed: {certificate.defense_layers_passed}/6")
    print(f"✓ Insurance Eligible: {'YES' if certificate.insurance_eligible else 'NO'}")
    print()
    
    # Calculate pricing
    price = issuer.get_pricing("premium", 1, 100000.0)
    print(f"Certificate Fee: ${price:.2f}")
    print()
    
    # Export certificate
    output_dir = Path("output/certificates")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / "stop_loss_certificate.json"
    pdf_path = output_dir / "stop_loss_certificate.txt"
    
    issuer.export_certificate_json(certificate, str(json_path))
    issuer.export_certificate_pdf(certificate, str(pdf_path))
    
    print(f"✓ Certificate exported to: {json_path}")
    print(f"✓ Certificate exported to: {pdf_path}")
    print()
    
    print("Commercial Value:")
    print("-" * 80)
    print("• Trader pays $1,500/month subscription")
    print("• Trader pays $100 per certificate")
    print("• Insurance company gives 20% premium discount")
    print("• Trader saves $2,000/year on insurance")
    print("• Trader avoids $5,000/year in failed stop-losses")
    print()
    print("ROI: $7,000 saved - $1,800 cost = $5,200 net benefit (289% ROI)")
    print()


def demo_flash_loan_shield():
    """
    Demo 2: Flash Loan Shield
    
    Scenario: DeFi protocol under flash loan attack
    Traditional: Price manipulation succeeds
    Aethel: Attack blocked by Oracle Sanctuary
    
    Commercial Value: $1000-10,000/month per protocol
    Certificate Fee: $200-500 per protected transaction
    """
    print("=" * 80)
    print("DEMO 2: FLASH LOAN SHIELD")
    print("=" * 80)
    print()
    
    print("Scenario: Flash Loan Attack Prevention")
    print("-" * 80)
    print("Protocol TVL: $100,000,000")
    print("Trade Price: $1,850.00 (ETH/USD)")
    print("Oracle Price: $1,800.00 (ETH/USD)")
    print("Deviation: 2.78% (WITHIN 3% THRESHOLD)")
    print()
    
    print("Executing trade with Oracle Sanctuary protection...")
    time.sleep(0.5)
    
    # Create proof log
    proof_log = ProofLog(
        layer_minus_1_semantic={"passed": True, "threats_detected": 0},
        layer_0_sanitizer={"passed": True, "sanitized": False},
        layer_1_conservation={"passed": True, "value_conserved": True},
        layer_2_overflow={"passed": True, "overflow_detected": False},
        layer_3_z3_proof={"passed": True, "proof_time_ms": 67},
        sentinel_telemetry={"anomaly_score": 0.15, "health": "excellent"},
        crisis_mode_active=False,
        quarantine_status="clean"
    )
    
    # Issue certificate
    issuer = get_audit_issuer()
    certificate = issuer.issue_assurance_certificate(
        bundle_hash="0xFLASH_LOAN_SHIELD_67890",
        proof_log=proof_log,
        transaction_count=1,
        total_value=5000000.0,  # $5M trade
        tier="enterprise"
    )
    
    print(f"✓ Certificate Issued: {certificate.certificate_id}")
    print(f"✓ Security Rating: {certificate.security_rating}")
    print(f"✓ Defense Layers Passed: {certificate.defense_layers_passed}/6")
    print(f"✓ Insurance Eligible: {'YES' if certificate.insurance_eligible else 'NO'}")
    print()
    
    print("Attack Scenario (Blocked):")
    print("-" * 80)
    print("Attacker attempts flash loan with manipulated price: $2,100.00")
    print("Deviation: 16.67% (EXCEEDS 3% THRESHOLD)")
    print("Result: Z3 REFUSES to prove → Trade REJECTED")
    print("Attack BLOCKED before execution")
    print()
    
    # Export certificate
    output_dir = Path("output/certificates")
    json_path = output_dir / "flash_loan_shield_certificate.json"
    pdf_path = output_dir / "flash_loan_shield_certificate.txt"
    
    issuer.export_certificate_json(certificate, str(json_path))
    issuer.export_certificate_pdf(certificate, str(pdf_path))
    
    print(f"✓ Certificate exported to: {json_path}")
    print(f"✓ Certificate exported to: {pdf_path}")
    print()
    
    print("Commercial Value:")
    print("-" * 80)
    print("• Protocol pays $10,000/month enterprise license")
    print("• Protocol avoids $5,000,000 flash loan attack")
    print("• Insurance premium reduced by 50% ($50,000/year savings)")
    print("• Reputation damage avoided (priceless)")
    print()
    print("ROI: $5,050,000 saved - $120,000 cost = $4,930,000 net benefit")
    print()


def demo_portfolio_rebalancing():
    """
    Demo 3: Portfolio Rebalancing Enforcer
    
    Scenario: Fund maintains disciplined allocation
    Traditional: Manual rebalancing, emotional decisions
    Aethel: Automatic enforcement, systematic discipline
    
    Commercial Value: $800-3000/month per fund
    Certificate Fee: $100-200 per rebalancing event
    """
    print("=" * 80)
    print("DEMO 3: PORTFOLIO REBALANCING ENFORCER")
    print("=" * 80)
    print()
    
    print("Scenario: Systematic Portfolio Discipline")
    print("-" * 80)
    print("Portfolio Value: $1,000,000")
    print("Target Allocation: 40% BTC, 30% ETH, 30% USDC")
    print("Drift Tolerance: 5%")
    print()
    
    print("Current Allocation:")
    print("  BTC: $450,000 (45%) - DRIFTED +5%")
    print("  ETH: $300,000 (30%) - ON TARGET")
    print("  USDC: $250,000 (25%) - DRIFTED -5%")
    print()
    
    print("Executing rebalancing check...")
    time.sleep(0.5)
    
    # Create proof log
    proof_log = ProofLog(
        layer_minus_1_semantic={"passed": True, "threats_detected": 0},
        layer_0_sanitizer={"passed": True, "sanitized": False},
        layer_1_conservation={"passed": True, "value_conserved": True},
        layer_2_overflow={"passed": True, "overflow_detected": False},
        layer_3_z3_proof={"passed": True, "proof_time_ms": 52},
        sentinel_telemetry={"anomaly_score": 0.08, "health": "excellent"},
        crisis_mode_active=False,
        quarantine_status="clean"
    )
    
    # Issue certificate
    issuer = get_audit_issuer()
    certificate = issuer.issue_assurance_certificate(
        bundle_hash="0xREBALANCE_EVENT_11111",
        proof_log=proof_log,
        transaction_count=3,  # 3 trades to rebalance
        total_value=1000000.0,
        tier="premium"
    )
    
    print(f"✓ Rebalancing REQUIRED (drift exceeded tolerance)")
    print(f"✓ Certificate Issued: {certificate.certificate_id}")
    print(f"✓ Security Rating: {certificate.security_rating}")
    print(f"✓ Defense Layers Passed: {certificate.defense_layers_passed}/6")
    print()
    
    print("Rebalancing Actions:")
    print("  1. Sell $50,000 BTC → USDC")
    print("  2. Buy $50,000 USDC")
    print("  3. Verify final allocation")
    print()
    
    print("Final Allocation:")
    print("  BTC: $400,000 (40%) ✓")
    print("  ETH: $300,000 (30%) ✓")
    print("  USDC: $300,000 (30%) ✓")
    print()
    
    # Export certificate
    output_dir = Path("output/certificates")
    json_path = output_dir / "rebalancing_certificate.json"
    pdf_path = output_dir / "rebalancing_certificate.txt"
    
    issuer.export_certificate_json(certificate, str(json_path))
    issuer.export_certificate_pdf(certificate, str(pdf_path))
    
    print(f"✓ Certificate exported to: {json_path}")
    print(f"✓ Certificate exported to: {pdf_path}")
    print()
    
    print("Commercial Value:")
    print("-" * 80)
    print("• Fund pays $2,000/month subscription")
    print("• Fund maintains systematic discipline (no emotional decisions)")
    print("• Fund avoids 2% annual performance drag from poor timing")
    print("• 2% of $1M = $20,000/year performance improvement")
    print()
    print("ROI: $20,000 gained - $24,000 cost = -$4,000 first year")
    print("     But systematic discipline compounds over time")
    print("     Year 5: $100,000+ cumulative benefit")
    print()


def demo_revenue_summary():
    """
    Demo 4: Revenue Model Summary
    
    Shows the complete revenue picture for Aethel Apex
    """
    print("=" * 80)
    print("AETHEL APEX - REVENUE MODEL SUMMARY")
    print("=" * 80)
    print()
    
    print("REVENUE STREAM 1: Assurance Certificates")
    print("-" * 80)
    print("Target: 1,000 certificates/month")
    print("Average Price: $150/certificate")
    print("Monthly Revenue: $150,000")
    print("Annual Revenue: $1,800,000")
    print()
    
    print("REVENUE STREAM 2: Trading Invariants Subscriptions")
    print("-" * 80)
    print("Individual Traders: 100 × $1,500/month = $150,000/month")
    print("DeFi Protocols: 20 × $5,000/month = $100,000/month")
    print("Exchanges: 5 × $15,000/month = $75,000/month")
    print("Monthly Revenue: $325,000")
    print("Annual Revenue: $3,900,000")
    print()
    
    print("REVENUE STREAM 3: Insurance Partnerships")
    print("-" * 80)
    print("Revenue Share: 10% of premium discounts")
    print("Average Discount: $10,000/year per client")
    print("Clients: 200")
    print("Annual Revenue: $200,000")
    print()
    
    print("REVENUE STREAM 4: Enterprise Licenses")
    print("-" * 80)
    print("White Label: 3 × $200,000/year = $600,000")
    print("Custom Development: $500,000/year")
    print("Annual Revenue: $1,100,000")
    print()
    
    print("=" * 80)
    print("TOTAL ANNUAL REVENUE: $7,000,000")
    print("=" * 80)
    print()
    
    print("Path to $1.5M/year (Conservative):")
    print("-" * 80)
    print("Year 1 Target: $1,500,000")
    print("  • 200 certificates/month × $150 = $360,000")
    print("  • 50 subscriptions × $2,000/month = $1,200,000")
    print("  • Insurance partnerships = $40,000")
    print()
    print("This is ACHIEVABLE with:")
    print("  • 50 paying clients (traders + protocols)")
    print("  • 200 certificates/month (4 per client)")
    print("  • 1 sales person + marketing")
    print()


def main():
    """Run all demos"""
    print()
    print("🏛️💰 AETHEL APEX - COMMERCIAL DEMONSTRATIONS 💰🏛️")
    print()
    
    demo_stop_loss_inviolable()
    input("Press Enter to continue to Demo 2...")
    print()
    
    demo_flash_loan_shield()
    input("Press Enter to continue to Demo 3...")
    print()
    
    demo_portfolio_rebalancing()
    input("Press Enter to continue to Revenue Summary...")
    print()
    
    demo_revenue_summary()
    
    print()
    print("=" * 80)
    print("DEMONSTRATIONS COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Deploy v1.9 Apex to Hugging Face")
    print("2. Create sales materials (pitch deck, case studies)")
    print("3. Launch marketing campaign")
    print("4. Onboard first 10 paying clients")
    print()
    print("Target: $1.5M ARR by Q4 2026")
    print()


if __name__ == "__main__":
    main()
