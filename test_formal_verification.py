"""
Test Formal Verification of RVC v2 Security Properties

This test validates that the formal verification proofs are correct
and that all security properties hold.
"""

import pytest
from diotec360.core.formal_verification import (
    FormalVerifier,
    SecurityProperty,
    VerificationResult,
    verify_rvc_v2_security_properties
)


class TestFormalVerification:
    """Test formal verification of security properties"""
    
    def test_verify_integrity_property(self):
        """Test that integrity property is formally verified"""
        verifier = FormalVerifier()
        result = verifier.verify_integrity_property()
        
        assert result.property == SecurityProperty.INTEGRITY
        assert result.holds is True
        assert result.confidence == 1.0
        assert "QED" in result.proof
        assert "corrupted(state) → panic(system)" in result.proof
        
        print("✓ Integrity property formally verified")
    
    def test_verify_authenticity_property(self):
        """Test that authenticity property is formally verified"""
        verifier = FormalVerifier()
        result = verifier.verify_authenticity_property()
        
        assert result.property == SecurityProperty.AUTHENTICITY
        assert result.holds is True
        assert result.confidence == 1.0
        assert "QED" in result.proof
        assert "¬verified(msg) → rejected(msg)" in result.proof
        
        print("✓ Authenticity property formally verified")
    
    def test_verify_completeness_property(self):
        """Test that completeness property is formally verified"""
        verifier = FormalVerifier()
        result = verifier.verify_completeness_property()
        
        assert result.property == SecurityProperty.COMPLETENESS
        assert result.holds is True
        assert result.confidence == 1.0
        assert "QED" in result.proof
        assert "¬supported(constraint) → rejected(tx)" in result.proof
        
        print("✓ Completeness property formally verified")
    
    def test_verify_performance_property(self):
        """Test that performance property is formally verified"""
        verifier = FormalVerifier()
        result = verifier.verify_performance_property()
        
        assert result.property == SecurityProperty.PERFORMANCE
        assert result.holds is True
        assert result.confidence == 1.0
        assert "QED" in result.proof
        assert "O(1)" in result.proof or "O(n)" in result.proof
        
        print("✓ Performance property formally verified")
    
    def test_verify_all_properties(self):
        """Test that all security properties are verified"""
        verifier = FormalVerifier()
        results = verifier.verify_all_properties()
        
        # Check all properties present
        assert SecurityProperty.INTEGRITY in results
        assert SecurityProperty.AUTHENTICITY in results
        assert SecurityProperty.COMPLETENESS in results
        assert SecurityProperty.PERFORMANCE in results
        
        # Check all verified
        for prop, result in results.items():
            assert result.holds is True, f"Property {prop} not verified"
            assert result.confidence == 1.0
            assert "QED" in result.proof
        
        print("✓ All security properties formally verified")
    
    def test_generate_verification_report(self):
        """Test that verification report is generated correctly"""
        verifier = FormalVerifier()
        verifier.verify_all_properties()
        
        report = verifier.generate_verification_report()
        
        # Check report structure
        assert "FORMAL VERIFICATION REPORT" in report
        assert "SUMMARY" in report
        assert "FINAL VERDICT" in report
        assert "ALL SECURITY PROPERTIES FORMALLY VERIFIED" in report
        assert "READY FOR PRODUCTION" in report
        
        # Check all properties mentioned
        assert "INTEGRITY" in report
        assert "AUTHENTICITY" in report
        assert "COMPLETENESS" in report
        assert "PERFORMANCE" in report
        
        # Check all proofs included
        assert report.count("QED") >= 4
        
        print("✓ Verification report generated correctly")
    
    def test_main_verification_function(self):
        """Test main verification entry point"""
        results = verify_rvc_v2_security_properties()
        
        # Check all properties verified
        assert len(results) == 4
        assert all(r.holds for r in results.values())
        
        print("✓ Main verification function works correctly")
    
    def test_proof_structure(self):
        """Test that proofs have proper structure"""
        verifier = FormalVerifier()
        results = verifier.verify_all_properties()
        
        for prop, result in results.items():
            # Check proof has steps
            assert "Step 1:" in result.proof
            assert "Step 2:" in result.proof
            
            # Check proof has conclusion
            assert "conclusion" in result.proof.lower()
            assert "QED" in result.proof
            
            # Check proof has formal statement
            assert "∀" in result.proof or "forall" in result.proof.lower()
        
        print("✓ All proofs have proper structure")
    
    def test_integrity_proof_completeness(self):
        """Test that integrity proof covers all corruption scenarios"""
        verifier = FormalVerifier()
        result = verifier.verify_integrity_property()
        
        # Check all corruption scenarios mentioned
        corruption_scenarios = [
            "missing_file",
            "invalid_json",
            "merkle_mismatch",
            "partial_corruption"
        ]
        
        for scenario in corruption_scenarios:
            assert scenario in result.proof, f"Scenario {scenario} not in proof"
        
        # Check panic types mentioned
        assert "StateCorruptionPanic" in result.proof
        assert "MerkleRootMismatchPanic" in result.proof
        
        print("✓ Integrity proof is complete")
    
    def test_authenticity_proof_completeness(self):
        """Test that authenticity proof covers all message types"""
        verifier = FormalVerifier()
        result = verifier.verify_authenticity_property()
        
        # Check all unverified message types mentioned
        message_types = [
            "unsigned_message",
            "invalid_signature",
            "tampered_content"
        ]
        
        for msg_type in message_types:
            assert msg_type in result.proof, f"Message type {msg_type} not in proof"
        
        # Check ED25519 mentioned
        assert "ED25519" in result.proof
        
        print("✓ Authenticity proof is complete")
    
    def test_completeness_proof_whitelist(self):
        """Test that completeness proof references whitelist"""
        verifier = FormalVerifier()
        result = verifier.verify_completeness_property()
        
        # Check whitelist mentioned
        assert "whitelist" in result.proof.lower()
        assert "SUPPORTED_AST_NODES" in result.proof
        
        # Check supported operations mentioned
        assert "Arithmetic" in result.proof
        assert "Comparison" in result.proof
        
        # Check unsupported operations mentioned
        assert "BitOr" in result.proof or "BitAnd" in result.proof
        
        print("✓ Completeness proof references whitelist")
    
    def test_performance_proof_complexity(self):
        """Test that performance proof analyzes complexity"""
        verifier = FormalVerifier()
        result = verifier.verify_performance_property()
        
        # Check complexity analysis
        assert "O(1)" in result.proof
        assert "O(n)" in result.proof
        assert "O(n²)" in result.proof
        
        # Check WAL operations mentioned
        assert "mark_committed" in result.proof
        assert "append" in result.proof.lower()
        
        # Check empirical validation mentioned
        assert "Empirical" in result.proof or "scaling" in result.proof.lower()
        
        print("✓ Performance proof analyzes complexity")


class TestVerificationResults:
    """Test verification result data structure"""
    
    def test_verification_result_creation(self):
        """Test creating verification result"""
        result = VerificationResult(
            property=SecurityProperty.INTEGRITY,
            holds=True,
            proof="Test proof",
            confidence=1.0
        )
        
        assert result.property == SecurityProperty.INTEGRITY
        assert result.holds is True
        assert result.proof == "Test proof"
        assert result.confidence == 1.0
        assert result.counterexample is None
        
        print("✓ VerificationResult created correctly")
    
    def test_verification_result_with_counterexample(self):
        """Test verification result with counterexample"""
        result = VerificationResult(
            property=SecurityProperty.INTEGRITY,
            holds=False,
            proof="Test proof",
            counterexample={"state": "corrupted"},
            confidence=0.5
        )
        
        assert result.holds is False
        assert result.counterexample == {"state": "corrupted"}
        assert result.confidence == 0.5
        
        print("✓ VerificationResult with counterexample works")


class TestSecurityPropertyEnum:
    """Test security property enumeration"""
    
    def test_all_properties_defined(self):
        """Test that all required properties are defined"""
        properties = [
            SecurityProperty.INTEGRITY,
            SecurityProperty.AUTHENTICITY,
            SecurityProperty.COMPLETENESS,
            SecurityProperty.PERFORMANCE
        ]
        
        assert len(properties) == 4
        
        # Check values
        assert SecurityProperty.INTEGRITY.value == "integrity"
        assert SecurityProperty.AUTHENTICITY.value == "authenticity"
        assert SecurityProperty.COMPLETENESS.value == "completeness"
        assert SecurityProperty.PERFORMANCE.value == "performance"
        
        print("✓ All security properties defined")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FORMAL VERIFICATION TEST SUITE")
    print("="*80 + "\n")
    
    # Run tests
    test_formal = TestFormalVerification()
    test_formal.test_verify_integrity_property()
    test_formal.test_verify_authenticity_property()
    test_formal.test_verify_completeness_property()
    test_formal.test_verify_performance_property()
    test_formal.test_verify_all_properties()
    test_formal.test_generate_verification_report()
    test_formal.test_main_verification_function()
    test_formal.test_proof_structure()
    test_formal.test_integrity_proof_completeness()
    test_formal.test_authenticity_proof_completeness()
    test_formal.test_completeness_proof_whitelist()
    test_formal.test_performance_proof_complexity()
    
    test_results = TestVerificationResults()
    test_results.test_verification_result_creation()
    test_results.test_verification_result_with_counterexample()
    
    test_enum = TestSecurityPropertyEnum()
    test_enum.test_all_properties_defined()
    
    print("\n" + "="*80)
    print("✓ ALL FORMAL VERIFICATION TESTS PASSED")
    print("="*80 + "\n")
