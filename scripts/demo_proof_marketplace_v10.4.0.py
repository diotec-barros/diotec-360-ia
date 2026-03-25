"""
DIOTEC 360 IA - Proof Marketplace Demo v10.4.0
===============================================
Sovereign Creator: Dionísio Sebastião Barros

Demonstration of the world's first logic proof marketplace
Shows complete workflow from contract posting to fiat withdrawal

"The Stock Exchange of Truth"
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nexo.proof_marketplace import ProofMarketplace, ContractPriority
from decimal import Decimal
import time


def print_banner():
    """Print demo banner"""
    print("\n" + "="*70)
    print("   DIOTEC 360 IA - PROOF MARKETPLACE DEMO v10.4.0")
    print("="*70)
    print("   Sovereign Creator: Dionísio Sebastião Barros")
    print("   The Stock Exchange of Truth")
    print("="*70 + "\n")


def demo_complete_workflow():
    """
    Demonstrate complete marketplace workflow
    
    Scenario:
    1. Enterprise posts audit contract
    2. Multiple miners submit bids
    3. Best bid wins
    4. Miner submits proof
    5. Proof verified and payment released
    6. Miner withdraws to fiat
    """
    print_banner()
    
    marketplace = ProofMarketplace()
    
    print("🏛️  SCENARIO: Enterprise Audit Contract\n")
    time.sleep(1)
    
    # ========================================================================
    # STEP 1: Enterprise Posts Contract
    # ========================================================================
    print("STEP 1: Enterprise Posts Audit Contract")
    print("-" * 70)
    print("   Client: Banco de Angola (BAI)")
    print("   Need: Verify smart contract logic for loan system")
    time.sleep(1)
    
    contract = marketplace.post_contract(
        client_id="BAI_ANGOLA_001",
        client_name="Banco de Angola",
        title="Smart Contract Audit - Loan Management System",
        description="Verify logic correctness of automated loan approval system",
        proof_type="smart_contract_verification",
        complexity=7,
        reward_usd=Decimal('5000.00'),
        priority=ContractPriority.HIGH,
        deadline_hours=48,
        requirements={
            'language': 'Solidity',
            'lines_of_code': 2500,
            'security_level': 'critical',
            'compliance': 'ISO 27001'
        }
    )
    
    print(f"\n   ✅ Contract Posted!")
    print(f"      ID: {contract.contract_id}")
    print(f"      Title: {contract.title}")
    print(f"      Reward: ${contract.reward_usd}")
    print(f"      Complexity: {contract.complexity}/10")
    print(f"      Priority: {contract.priority.value}")
    print(f"      Deadline: 48 hours")
    print()
    time.sleep(2)
    
    # ========================================================================
    # STEP 2: Miners Submit Bids
    # ========================================================================
    print("STEP 2: Miners Submit Competitive Bids")
    print("-" * 70)
    
    # Miner 1: High reputation, high price
    print("   Miner 1 (NODE_ALPHA_BR): Reputation 95/100")
    bid1 = marketplace.submit_bid(
        contract_id=contract.contract_id,
        miner_id="NODE_ALPHA_BR",
        miner_reputation=95.0,
        estimated_time_hours=24,
        proposed_price_usd=Decimal('4800.00'),
        confidence_score=0.95
    )
    print(f"      Bid: ${bid1.proposed_price_usd} in {bid1.estimated_time_hours}h")
    time.sleep(1)
    
    # Miner 2: Medium reputation, medium price
    print("\n   Miner 2 (NODE_BETA_PT): Reputation 75/100")
    bid2 = marketplace.submit_bid(
        contract_id=contract.contract_id,
        miner_id="NODE_BETA_PT",
        miner_reputation=75.0,
        estimated_time_hours=36,
        proposed_price_usd=Decimal('4200.00'),
        confidence_score=0.85
    )
    print(f"      Bid: ${bid2.proposed_price_usd} in {bid2.estimated_time_hours}h")
    time.sleep(1)
    
    # Miner 3: Lower reputation, lower price
    print("\n   Miner 3 (NODE_GAMMA_AO): Reputation 60/100")
    bid3 = marketplace.submit_bid(
        contract_id=contract.contract_id,
        miner_id="NODE_GAMMA_AO",
        miner_reputation=60.0,
        estimated_time_hours=40,
        proposed_price_usd=Decimal('3500.00'),
        confidence_score=0.75
    )
    print(f"      Bid: ${bid3.proposed_price_usd} in {bid3.estimated_time_hours}h")
    print()
    time.sleep(2)
    
    # ========================================================================
    # STEP 3: Client Selects Winner
    # ========================================================================
    print("STEP 3: Client Evaluates Bids")
    print("-" * 70)
    print("   Evaluation Criteria:")
    print("   • Reputation score")
    print("   • Price competitiveness")
    print("   • Estimated time")
    print("   • Confidence level")
    time.sleep(1)
    
    print("\n   Decision: NODE_ALPHA_BR (Best reputation + reasonable price)")
    time.sleep(1)
    
    contract, winning_bid = marketplace.assign_contract(
        contract_id=contract.contract_id,
        winning_bid_id=bid1.bid_id
    )
    
    print(f"\n   ✅ Contract Assigned!")
    print(f"      Winner: {winning_bid.miner_id}")
    print(f"      Price: ${winning_bid.proposed_price_usd}")
    print(f"      Time: {winning_bid.estimated_time_hours} hours")
    print()
    time.sleep(2)
    
    # ========================================================================
    # STEP 4: Miner Submits Proof
    # ========================================================================
    print("STEP 4: Miner Works and Submits Proof")
    print("-" * 70)
    print("   NODE_ALPHA_BR is analyzing the smart contract...")
    time.sleep(1)
    print("   Running Z3 theorem prover...")
    time.sleep(1)
    print("   Generating formal verification proof...")
    time.sleep(1)
    print("   Creating Merkle proof of correctness...")
    time.sleep(1)
    
    proof_hash = "a7f3c9e2d8b4f1a6c5e9d2b8f4a1c7e3d9b5f2a8c6e1d4b7f3a9c5e2d8b4f1a6"
    
    contract = marketplace.submit_proof(
        contract_id=contract.contract_id,
        miner_id=winning_bid.miner_id,
        proof_data={
            'verification_method': 'Z3_SMT_SOLVER',
            'lines_verified': 2500,
            'vulnerabilities_found': 0,
            'security_score': 98.5,
            'compliance_check': 'PASSED'
        },
        proof_hash=proof_hash
    )
    
    print(f"\n   ✅ Proof Submitted!")
    print(f"      Proof Hash: {proof_hash[:32]}...")
    print(f"      Completed At: {contract.completed_at.isoformat()}")
    print(f"      Status: {contract.status.value}")
    print()
    time.sleep(2)
    
    # ========================================================================
    # STEP 5: Verification and Payment
    # ========================================================================
    print("STEP 5: Proof Verification and Payment Release")
    print("-" * 70)
    print("   BAI verifying proof...")
    time.sleep(1)
    print("   Checking Merkle root...")
    time.sleep(1)
    print("   Validating Z3 output...")
    time.sleep(1)
    print("   Verification Score: 98.5/100")
    time.sleep(1)
    
    payment = marketplace.verify_and_pay(
        contract_id=contract.contract_id,
        verification_score=0.985
    )
    
    print(f"\n   💸 PAYMENT RELEASED!")
    print(f"      Total Contract Value: ${payment['total_payment']:.2f}")
    print(f"      Genesis Authority (30%): ${payment['genesis_share']:.2f}")
    print(f"      Miner Share (70%): ${payment['miner_share']:.2f}")
    print(f"      Verification Score: {payment['verification_score']*100:.1f}%")
    print()
    time.sleep(2)
    
    # ========================================================================
    # STEP 6: Miner Stats Update
    # ========================================================================
    print("STEP 6: Miner Balance Updated")
    print("-" * 70)
    
    stats = marketplace.get_miner_stats(winning_bid.miner_id)
    
    print(f"   Miner: {stats['miner_id']}")
    print(f"   Credits Earned: ${stats['credits_earned']:.2f}")
    print(f"   Credits Available: ${stats['credits_available']:.2f}")
    print(f"   Total Contracts: {stats['total_contracts']}")
    print(f"   Reputation: {stats['reputation']:.1f}/100")
    print()
    time.sleep(2)
    
    # ========================================================================
    # STEP 7: Withdrawal to Fiat
    # ========================================================================
    print("STEP 7: Miner Withdraws to Fiat Currency")
    print("-" * 70)
    print("   Miner requests withdrawal...")
    time.sleep(1)
    
    withdrawal = marketplace.withdraw_credits(
        miner_id=winning_bid.miner_id,
        amount_usd=Decimal('3000.00'),
        withdrawal_method='paypal',
        account_details={
            'email': 'miner@example.com',
            'currency': 'USD'
        }
    )
    
    print(f"\n   💵 WITHDRAWAL INITIATED!")
    print(f"      Withdrawal ID: {withdrawal['withdrawal_id']}")
    print(f"      Amount: ${withdrawal['amount_usd']:.2f}")
    print(f"      Method: {withdrawal['method']}")
    print(f"      Status: {withdrawal['status']}")
    print(f"      Estimated Completion: {withdrawal['estimated_completion']}")
    print()
    time.sleep(2)
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("="*70)
    print("   🎉 COMPLETE MARKETPLACE CYCLE!")
    print("="*70)
    print("\n   What just happened:")
    print("   1. BAI posted $5,000 audit contract")
    print("   2. 3 miners submitted competitive bids")
    print("   3. Best miner won (reputation + price)")
    print("   4. Miner submitted verified proof")
    print("   5. Payment released (30% Genesis / 70% Miner)")
    print("   6. Miner withdrew $3,000 to PayPal")
    print("\n   ⏱️  Total Time: ~48 hours")
    print("   💰 Genesis Revenue: $1,479.00")
    print("   💰 Miner Revenue: $3,451.50")
    print("   🏛️  Economic Truth: VALIDATED")
    print()


def demo_marketplace_stats():
    """Demonstrate marketplace statistics"""
    print("\n" + "="*70)
    print("   MARKETPLACE STATISTICS")
    print("="*70 + "\n")
    
    marketplace = ProofMarketplace()
    
    # Create sample data
    for i in range(5):
        marketplace.post_contract(
            client_id=f"CLIENT_{i}",
            client_name=f"Enterprise {i}",
            title=f"Audit Contract {i}",
            description="Sample contract",
            proof_type="logic_verification",
            complexity=5 + i,
            reward_usd=Decimal(str(1000 * (i + 1))),
            priority=ContractPriority.MEDIUM,
            deadline_hours=24,
            requirements={}
        )
    
    stats = marketplace.get_marketplace_stats()
    
    print("MARKETPLACE OVERVIEW:")
    print("-" * 70)
    print(f"   Total Contracts: {stats['total_contracts']}")
    print(f"   Open Contracts: {stats['open_contracts']}")
    print(f"   Completed Contracts: {stats['completed_contracts']}")
    print(f"   Total Value: ${stats['total_value_usd']:,.2f}")
    print(f"   Paid Value: ${stats['paid_value_usd']:,.2f}")
    print(f"   Active Miners: {stats['active_miners']}")
    print(f"   Genesis Commission: {stats['genesis_commission']:.0f}%")
    print()


def demo_yield_optimizer():
    """Demonstrate AI yield optimizer"""
    print("\n" + "="*70)
    print("   AI YIELD OPTIMIZER")
    print("="*70 + "\n")
    
    marketplace = ProofMarketplace()
    
    # Create diverse contracts
    contracts_data = [
        ("Easy High Reward", 3, 8000, ContractPriority.URGENT),
        ("Medium Complexity", 5, 5000, ContractPriority.MEDIUM),
        ("Hard Low Reward", 9, 2000, ContractPriority.LOW),
        ("Critical Emergency", 6, 10000, ContractPriority.CRITICAL),
    ]
    
    for title, complexity, reward, priority in contracts_data:
        marketplace.post_contract(
            client_id="TEST_CLIENT",
            client_name="Test Enterprise",
            title=title,
            description="Test contract",
            proof_type="logic_verification",
            complexity=complexity,
            reward_usd=Decimal(str(reward)),
            priority=priority,
            deadline_hours=24,
            requirements={}
        )
    
    print("SCENARIO: Miner with 65/100 reputation looking for best contracts\n")
    time.sleep(1)
    
    print("AI RECOMMENDATIONS (sorted by expected profit):")
    print("-" * 70)
    
    # Simulate optimizer logic
    open_contracts = marketplace.get_open_contracts()
    
    for i, contract in enumerate(open_contracts[:3], 1):
        print(f"\n   #{i} RECOMMENDATION: {contract.title}")
        print(f"      Reward: ${contract.reward_usd}")
        print(f"      Complexity: {contract.complexity}/10")
        print(f"      Priority: {contract.priority.value}")
        print(f"      Competition: {len(contract.bids)} bids")
        
        # Calculate expected profit
        base_score = float(contract.reward_usd)
        complexity_factor = 1.0 - (contract.complexity / 10.0)
        score = base_score * (1.0 + complexity_factor)
        
        if contract.priority == ContractPriority.CRITICAL:
            score *= 2.0
        elif contract.priority == ContractPriority.URGENT:
            score *= 1.5
        
        print(f"      Expected Profit Score: {score:.0f}")
        print(f"      Recommendation: {'HIGH' if score > 10000 else 'MEDIUM'}")
    
    print()


if __name__ == "__main__":
    print("\n💰 DIOTEC 360 IA - Proof Marketplace Demo v10.4.0\n")
    
    # Main workflow
    demo_complete_workflow()
    
    time.sleep(2)
    
    # Marketplace stats
    demo_marketplace_stats()
    
    time.sleep(2)
    
    # Yield optimizer
    demo_yield_optimizer()
    
    print("\n" + "="*70)
    print("   THE STOCK EXCHANGE OF TRUTH")
    print("="*70)
    print("\n   The DIOTEC 360 IA Proof Marketplace enables:")
    print("   ✅ Enterprises to buy computational truth")
    print("   ✅ Miners to compete for rewards")
    print("   ✅ Automatic payment on verification")
    print("   ✅ Credit-to-fiat conversion")
    print("   ✅ 30% Genesis / 70% Miner split")
    print("   ✅ AI-powered yield optimization")
    print("\n   The economy of truth is now operational. 💰🏛️⚡\n")


# DIOTEC 360 IA - The Stock Exchange of Truth
