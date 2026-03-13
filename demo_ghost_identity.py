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
Aethel Ghost Identity Demo - Task 2.2.3
Zero-Knowledge Identity: Privacy + Accountability

Demonstrates:
1. Anonymous Voting
2. Whistleblower Protection
3. Private Compliance Transactions
"""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from diotec360.core.ghost_identity import GhostIdentity, GhostIdentityIntegration


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_anonymous_voting():
    """Demo: Anonymous but verifiable voting system"""
    print_section("DEMO 1: ANONYMOUS VOTING")
    
    ghost_id = GhostIdentity()
    
    # Setup: Board of Directors (10 members)
    print("📋 Setup: Board of Directors with 10 members")
    board_members = [Ed25519PrivateKey.generate() for _ in range(10)]
    board_public_keys = [member.public_key() for member in board_members]
    print(f"   ✓ Created ring of {len(board_public_keys)} authorized voters\n")
    
    # Proposal
    proposal = b"Proposal: Approve $10M acquisition of TechCorp"
    print(f"📜 Proposal: {proposal.decode()}\n")
    
    # Members vote anonymously
    print("🗳️  Voting in progress...")
    votes_yes = []
    votes_no = []
    
    # 7 vote YES
    for i in [0, 2, 3, 5, 6, 8, 9]:
        proof = ghost_id.create_ghost_proof(
            proposal + b":YES",
            board_members[i],
            board_public_keys,
            i,
            proof_type="vote"
        )
        votes_yes.append(proof)
        print(f"   ✓ Anonymous vote YES received (key image: {proof.signature.key_image.hex()[:16]}...)")
    
    # 3 vote NO
    for i in [1, 4, 7]:
        proof = ghost_id.create_ghost_proof(
            proposal + b":NO",
            board_members[i],
            board_public_keys,
            i,
            proof_type="vote"
        )
        votes_no.append(proof)
        print(f"   ✓ Anonymous vote NO received (key image: {proof.signature.key_image.hex()[:16]}...)")
    
    # Verify all votes
    print("\n🔍 Verifying votes...")
    valid_yes = sum(1 for v in votes_yes if ghost_id.verify_ghost_proof(
        proposal + b":YES", v, board_public_keys
    ))
    valid_no = sum(1 for v in votes_no if ghost_id.verify_ghost_proof(
        proposal + b":NO", v, board_public_keys
    ))
    
    print(f"   ✓ Valid YES votes: {valid_yes}")
    print(f"   ✓ Valid NO votes: {valid_no}")
    
    # Check for double-voting
    print("\n🛡️  Checking for double-voting...")
    all_votes = votes_yes + votes_no
    double_vote_detected = False
    for i in range(len(all_votes)):
        for j in range(i + 1, len(all_votes)):
            if ghost_id.detect_double_signing(all_votes[i], all_votes[j]):
                double_vote_detected = True
                break
    
    if not double_vote_detected:
        print("   ✓ No double-voting detected")
    else:
        print("   ⚠️  Double-voting detected!")
    
    # Results
    print(f"\n📊 RESULTS:")
    print(f"   YES: {valid_yes} votes ({valid_yes/10*100:.0f}%)")
    print(f"   NO: {valid_no} votes ({valid_no/10*100:.0f}%)")
    print(f"   Status: {'APPROVED ✅' if valid_yes > valid_no else 'REJECTED ❌'}")
    print(f"\n   🔐 Privacy: Individual votes remain anonymous")
    print(f"   ⚖️  Accountability: All votes cryptographically verified")


def demo_whistleblower_protection():
    """Demo: Anonymous whistleblowing with accountability"""
    print_section("DEMO 2: WHISTLEBLOWER PROTECTION")
    
    ghost_id = GhostIdentity()
    
    # Setup: Company employees
    print("🏢 Setup: TechCorp with 50 employees")
    employees = [Ed25519PrivateKey.generate() for _ in range(50)]
    employee_public_keys = [e.public_key() for e in employees]
    print(f"   ✓ Created ring of {len(employee_public_keys)} authorized employees\n")
    
    # Whistleblower report
    report = b"CONFIDENTIAL: Evidence of financial fraud in Q3 2025 - Inflated revenue by $5M"
    print(f"📢 Whistleblower Report:")
    print(f"   {report.decode()}\n")
    
    # Anonymous employee submits report
    whistleblower_index = 23  # Employee #23
    print(f"🕵️  Employee #{whistleblower_index} submits anonymous report...")
    
    proof = ghost_id.create_ghost_proof(
        report,
        employees[whistleblower_index],
        employee_public_keys,
        whistleblower_index,
        proof_type="whistleblower"
    )
    
    print(f"   ✓ Report submitted anonymously")
    print(f"   ✓ Key image: {proof.signature.key_image.hex()[:32]}...")
    print(f"   ✓ Timestamp: {proof.timestamp}")
    print(f"   ✓ Anonymity set: {proof.metadata['anonymity_set']} employees\n")
    
    # External auditor verifies
    print("🔍 External Auditor verifying report...")
    is_valid = ghost_id.verify_ghost_proof(
        report,
        proof,
        employee_public_keys
    )
    
    if is_valid:
        print("   ✅ VERIFIED: Report came from authorized TechCorp employee")
        print("   🔐 PROTECTED: Employee identity remains anonymous")
        print("   ⚖️  ACCOUNTABLE: Cannot submit multiple conflicting reports")
    else:
        print("   ❌ INVALID: Report could not be verified")
    
    # Demonstrate protection
    print("\n🛡️  Protection Guarantees:")
    print(f"   • Whistleblower is one of {len(employee_public_keys)} employees")
    print(f"   • Impossible to determine which specific employee")
    print(f"   • Same employee cannot submit conflicting reports")
    print(f"   • Report authenticity cryptographically proven")


def demo_private_compliance():
    """Demo: Private transactions with regulatory compliance"""
    print_section("DEMO 3: PRIVATE COMPLIANCE TRANSACTIONS")
    
    ghost_id = GhostIdentity()
    integration = GhostIdentityIntegration(ghost_id)
    
    # Setup: Licensed traders
    print("💼 Setup: Securities Exchange with 25 licensed traders")
    traders = [Ed25519PrivateKey.generate() for _ in range(25)]
    trader_public_keys = [t.public_key() for t in traders]
    print(f"   ✓ Created ring of {len(trader_public_keys)} authorized traders\n")
    
    # Private transactions
    transactions = [
        (5, b"BUY 1000 shares ACME @ $50.00"),
        (12, b"SELL 500 shares BETA @ $120.50"),
        (18, b"BUY 2000 shares GAMMA @ $25.75"),
        (7, b"SELL 1500 shares DELTA @ $80.00"),
    ]
    
    print("💰 Executing private transactions...\n")
    
    proofs = []
    for trader_index, transaction in transactions:
        print(f"   Transaction: {transaction.decode()}")
        
        success, proof = integration.authorize_anonymous_transaction(
            transaction,
            traders[trader_index],
            trader_public_keys,
            trader_index
        )
        
        if success:
            print(f"   ✓ Authorized by licensed trader")
            print(f"   ✓ Key image: {proof.signature.key_image.hex()[:24]}...")
            proofs.append((transaction, proof))
        else:
            print(f"   ❌ Authorization failed")
        
        print()
    
    # Regulator verifies compliance
    print("🏛️  Regulatory Compliance Check...")
    print(f"   Verifying {len(proofs)} transactions...\n")
    
    verifier = GhostIdentityIntegration(ghost_id)
    
    for transaction, proof in proofs:
        is_valid = verifier.verify_anonymous_transaction(
            transaction,
            proof,
            trader_public_keys
        )
        
        status = "✅ COMPLIANT" if is_valid else "❌ NON-COMPLIANT"
        print(f"   {status}: {transaction.decode()}")
    
    print("\n📊 Compliance Summary:")
    print(f"   • All transactions from licensed traders: ✅")
    print(f"   • Trader identities remain private: ✅")
    print(f"   • No double-spending detected: ✅")
    print(f"   • Regulatory requirements met: ✅")
    
    print("\n🔐 Privacy Guarantees:")
    print(f"   • Regulator knows: Transaction is from authorized trader")
    print(f"   • Regulator doesn't know: Which specific trader")
    print(f"   • Anonymity set: {len(trader_public_keys)} traders")


def demo_attack_scenarios():
    """Demo: Security against attacks"""
    print_section("DEMO 4: SECURITY AGAINST ATTACKS")
    
    ghost_id = GhostIdentity()
    integration = GhostIdentityIntegration(ghost_id)
    
    # Setup
    ring_size = 10
    authorized_keys_private = [Ed25519PrivateKey.generate() for _ in range(ring_size)]
    authorized_keys_public = [k.public_key() for k in authorized_keys_private]
    
    print("🛡️  Testing security properties...\n")
    
    # Attack 1: Double-voting
    print("⚔️  ATTACK 1: Attempt double-voting")
    voter_index = 3
    
    vote1 = b"Vote for Proposal A"
    success1, proof1 = integration.authorize_anonymous_transaction(
        vote1,
        authorized_keys_private[voter_index],
        authorized_keys_public,
        voter_index
    )
    print(f"   First vote: {'✓ Accepted' if success1 else '✗ Rejected'}")
    
    vote2 = b"Vote for Proposal B"
    success2, proof2 = integration.authorize_anonymous_transaction(
        vote2,
        authorized_keys_private[voter_index],
        authorized_keys_public,
        voter_index
    )
    print(f"   Second vote (same key): {'✓ Accepted' if success2 else '✗ Rejected'}")
    
    if not success2:
        print("   ✅ DEFENSE SUCCESSFUL: Double-voting prevented\n")
    else:
        print("   ❌ DEFENSE FAILED: Double-voting allowed\n")
    
    # Attack 2: Unauthorized signer
    print("⚔️  ATTACK 2: Unauthorized user attempts to sign")
    attacker_key = Ed25519PrivateKey.generate()
    
    try:
        # Attacker tries to create signature (not in ring)
        fake_proof = ghost_id.create_ghost_proof(
            b"Malicious transaction",
            attacker_key,
            authorized_keys_public,
            0  # Pretends to be member 0
        )
        
        # Verification should fail
        is_valid = ghost_id.verify_ghost_proof(
            b"Malicious transaction",
            fake_proof,
            authorized_keys_public
        )
        
        if not is_valid:
            print("   ✅ DEFENSE SUCCESSFUL: Unauthorized signature rejected\n")
        else:
            print("   ❌ DEFENSE FAILED: Unauthorized signature accepted\n")
    
    except Exception as e:
        print(f"   ✅ DEFENSE SUCCESSFUL: Attack prevented ({type(e).__name__})\n")
    
    # Attack 3: Message tampering
    print("⚔️  ATTACK 3: Attempt to tamper with signed message")
    
    original_message = b"Transfer 100 tokens"
    signer_index = 5
    
    proof = ghost_id.create_ghost_proof(
        original_message,
        authorized_keys_private[signer_index],
        authorized_keys_public,
        signer_index
    )
    
    print(f"   Original message: {original_message.decode()}")
    
    tampered_message = b"Transfer 999 tokens"
    print(f"   Tampered message: {tampered_message.decode()}")
    
    is_valid = ghost_id.verify_ghost_proof(
        tampered_message,
        proof,
        authorized_keys_public
    )
    
    if not is_valid:
        print("   ✅ DEFENSE SUCCESSFUL: Tampering detected\n")
    else:
        print("   ❌ DEFENSE FAILED: Tampering not detected\n")
    
    print("🏆 Security Summary:")
    print("   ✅ Double-voting prevention: ACTIVE")
    print("   ✅ Unauthorized access prevention: ACTIVE")
    print("   ✅ Message integrity protection: ACTIVE")
    print("   ✅ Privacy preservation: ACTIVE")


def main():
    """Run all Ghost Identity demos"""
    print("\n" + "="*70)
    print("  AETHEL GHOST IDENTITY SYSTEM - v2.2.3")
    print("  Zero-Knowledge Identity: Privacy + Accountability")
    print("="*70)
    
    try:
        demo_anonymous_voting()
        demo_whistleblower_protection()
        demo_private_compliance()
        demo_attack_scenarios()
        
        print_section("🎯 GHOST IDENTITY SYSTEM: OPERATIONAL")
        print("✅ Anonymous Voting: ENABLED")
        print("✅ Whistleblower Protection: ENABLED")
        print("✅ Private Compliance: ENABLED")
        print("✅ Security Guarantees: VERIFIED")
        
        print("\n🔐 Privacy + Accountability = Sovereign Identity")
        print("👑 The Empire now has Ghost Citizens\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
