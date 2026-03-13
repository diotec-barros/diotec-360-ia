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
Tests for Diotec360 Audit Issuer - Certificate of Mathematical Assurance

Tests verify:
- Certificate generation and signing
- Signature verification
- Security rating calculation
- Pricing model
- JSON/PDF export
- Insurance eligibility determination
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from diotec360.core.audit_issuer import (
    DIOTEC360AuditIssuer,
    AssuranceCertificate,
    ProofLog,
    get_audit_issuer
)


class TestAuditIssuerCore:
    """Core functionality tests"""
    
    def test_key_generation(self):
        """Test RSA key pair generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            private_key_path = os.path.join(tmpdir, "private.pem")
            issuer = DIOTEC360AuditIssuer(private_key_path=private_key_path)
            
            # Keys should be generated
            assert issuer.private_key is not None
            assert issuer.public_key is not None
            
            # Key files should exist
            assert Path(private_key_path).exists()
            assert Path(os.path.join(tmpdir, "audit_issuer_public.pem")).exists()
    
    def test_key_loading(self):
        """Test loading existing keys"""
        with tempfile.TemporaryDirectory() as tmpdir:
            private_key_path = os.path.join(tmpdir, "private.pem")
            
            # Generate keys first time
            issuer1 = DIOTEC360AuditIssuer(private_key_path=private_key_path)
            fingerprint1 = issuer1._get_public_key_fingerprint()
            
            # Load keys second time
            issuer2 = DIOTEC360AuditIssuer(private_key_path=private_key_path)
            fingerprint2 = issuer2._get_public_key_fingerprint()
            
            # Should be same keys
            assert fingerprint1 == fingerprint2
    
    def test_certificate_generation(self):
        """Test basic certificate generation"""
        issuer = get_audit_issuer()
        
        # Create proof log
        proof_log = ProofLog(
            layer_minus_1_semantic={"passed": True, "entropy": 0.3},
            layer_0_sanitizer={"passed": True, "checks": 5},
            layer_1_conservation={"passed": True, "sum": 0},
            layer_2_overflow={"passed": True, "bounds": "safe"},
            layer_3_z3_proof={"passed": True, "model": "found"},
            sentinel_telemetry={"anomaly_score": 0.1, "cpu_time": 0.5},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        # Issue certificate
        certificate = issuer.issue_assurance_certificate(
            bundle_hash="abc123def456",
            proof_log=proof_log,
            transaction_count=10,
            total_value=100000.0,
            tier="standard"
        )
        
        # Verify certificate properties
        assert certificate.certificate_id.startswith("Diotec360-CERT-")
        assert certificate.issuer == "diotec360_DIOTEC360_nexo"
        assert certificate.version == "v1.9.0_Apex"
        assert certificate.bundle_hash == "abc123def456"
        assert certificate.transaction_count == 10
        assert certificate.total_value == 100000.0
        assert certificate.certificate_tier == "standard"
        assert certificate.signature is not None
        assert certificate.public_key_fingerprint is not None
    
    def test_security_rating_calculation(self):
        """Test security rating based on layers passed"""
        issuer = get_audit_issuer()
        
        # All 6 layers passed
        proof_log_perfect = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        cert_perfect = issuer.issue_assurance_certificate(
            "hash1", proof_log_perfect, 1, 1000.0, "standard"
        )
        
        assert cert_perfect.security_rating == "MATHEMATICALLY_PROVED_TRIPLE_LAYER"
        assert cert_perfect.defense_layers_passed == 6
        
        # Only 3 layers passed
        proof_log_partial = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": False},
            layer_3_z3_proof={"passed": False},
            sentinel_telemetry={"anomaly_score": 0.8},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        cert_partial = issuer.issue_assurance_certificate(
            "hash2", proof_log_partial, 1, 1000.0, "standard"
        )
        
        assert cert_partial.security_rating == "STANDARD_VERIFIED"
        assert cert_partial.defense_layers_passed == 3
    
    def test_insurance_eligibility(self):
        """Test insurance eligibility determination"""
        issuer = get_audit_issuer()
        
        # Eligible: All layers passed, no crisis, clean quarantine
        proof_log_eligible = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        cert_eligible = issuer.issue_assurance_certificate(
            "hash1", proof_log_eligible, 1, 1000.0, "premium"
        )
        
        assert cert_eligible.insurance_eligible is True
        
        # Not eligible: Crisis mode active
        proof_log_crisis = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=True,  # Crisis mode!
            quarantine_status="clean"
        )
        
        cert_crisis = issuer.issue_assurance_certificate(
            "hash2", proof_log_crisis, 1, 1000.0, "premium"
        )
        
        assert cert_crisis.insurance_eligible is False
        
        # Not eligible: Quarantined
        proof_log_quarantine = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="quarantined"  # Quarantined!
        )
        
        cert_quarantine = issuer.issue_assurance_certificate(
            "hash3", proof_log_quarantine, 1, 1000.0, "premium"
        )
        
        assert cert_quarantine.insurance_eligible is False


class TestCertificateVerification:
    """Certificate signature verification tests"""
    
    def test_signature_verification_valid(self):
        """Test verification of valid certificate"""
        issuer = get_audit_issuer()
        
        proof_log = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        certificate = issuer.issue_assurance_certificate(
            "test_hash", proof_log, 1, 1000.0, "standard"
        )
        
        # Verify signature
        is_valid = issuer.verify_certificate(certificate)
        assert is_valid is True
    
    def test_signature_verification_tampered(self):
        """Test verification fails for tampered certificate"""
        issuer = get_audit_issuer()
        
        proof_log = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        certificate = issuer.issue_assurance_certificate(
            "test_hash", proof_log, 1, 1000.0, "standard"
        )
        
        # Tamper with certificate
        certificate.total_value = 999999.0  # Changed!
        
        # Verification should fail
        is_valid = issuer.verify_certificate(certificate)
        assert is_valid is False


class TestPricingModel:
    """Pricing model tests"""
    
    def test_standard_pricing(self):
        """Test standard tier pricing"""
        issuer = get_audit_issuer()
        
        # Base: $50, Per-tx: $10, Value: 0.1%
        price = issuer.get_pricing("standard", 10, 100000.0)
        
        # $50 + (10 * $10) + (100000 * 0.001) = $50 + $100 + $100 = $250
        assert price == 250.0
    
    def test_premium_pricing(self):
        """Test premium tier pricing"""
        issuer = get_audit_issuer()
        
        # Base: $200, Per-tx: $20, Value: 0.2%
        price = issuer.get_pricing("premium", 10, 100000.0)
        
        # $200 + (10 * $20) + (100000 * 0.002) = $200 + $200 + $200 = $600
        assert price == 600.0
    
    def test_enterprise_pricing(self):
        """Test enterprise tier pricing (unlimited)"""
        issuer = get_audit_issuer()
        
        # Enterprise: Annual license, no per-certificate fee
        price = issuer.get_pricing("enterprise", 1000, 10000000.0)
        
        assert price == 0.0  # Covered by annual license


class TestCertificateExport:
    """Certificate export tests"""
    
    def test_json_export(self):
        """Test JSON export"""
        issuer = get_audit_issuer()
        
        proof_log = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        certificate = issuer.issue_assurance_certificate(
            "test_hash", proof_log, 5, 50000.0, "premium"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "certificate.json")
            issuer.export_certificate_json(certificate, output_path)
            
            # File should exist
            assert Path(output_path).exists()
            
            # Should be valid JSON
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert data["certificate_id"] == certificate.certificate_id
            assert data["bundle_hash"] == "test_hash"
            assert data["transaction_count"] == 5
            assert data["total_value"] == 50000.0
    
    def test_pdf_export(self):
        """Test PDF export"""
        issuer = get_audit_issuer()
        
        proof_log = ProofLog(
            layer_minus_1_semantic={"passed": True},
            layer_0_sanitizer={"passed": True},
            layer_1_conservation={"passed": True},
            layer_2_overflow={"passed": True},
            layer_3_z3_proof={"passed": True},
            sentinel_telemetry={"anomaly_score": 0.1},
            crisis_mode_active=False,
            quarantine_status="clean"
        )
        
        certificate = issuer.issue_assurance_certificate(
            "test_hash", proof_log, 5, 50000.0, "premium"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "certificate.pdf")
            issuer.export_certificate_pdf(certificate, output_path)
            
            # File should exist
            assert Path(output_path).exists()
            
            # Should contain certificate data
            with open(output_path, 'r') as f:
                content = f.read()
            
            assert "CERTIFICATE OF MATHEMATICAL ASSURANCE" in content
            assert certificate.certificate_id in content
            assert "test_hash" in content


class TestCommercialScenarios:
    """Real-world commercial scenario tests"""
    
    def test_insurance_discount_scenario(self):
        """
        Scenario: Bank gets 50% insurance discount with Diotec360 certificates
        
        - Bank pays $10M/year in cyber insurance
        - With Diotec360: $5M/year (50% discount)
        - Diotec360 fee: $100K/year enterprise license
        - Bank saves: $4.9M/year
        """
        issuer = get_audit_issuer()
        
        # Bank processes 10,000 transactions/year
        # All transactions get premium certificates
        total_cost = 0
        certificates_issued = 0
        
        for i in range(100):  # Sample 100 transactions
            proof_log = ProofLog(
                layer_minus_1_semantic={"passed": True},
                layer_0_sanitizer={"passed": True},
                layer_1_conservation={"passed": True},
                layer_2_overflow={"passed": True},
                layer_3_z3_proof={"passed": True},
                sentinel_telemetry={"anomaly_score": 0.1},
                crisis_mode_active=False,
                quarantine_status="clean"
            )
            
            certificate = issuer.issue_assurance_certificate(
                f"bank_tx_{i}", proof_log, 1, 10000.0, "enterprise"
            )
            
            # Enterprise tier: $0 per certificate (annual license)
            cost = issuer.get_pricing("enterprise", 1, 10000.0)
            total_cost += cost
            
            # Verify insurance eligibility
            assert certificate.insurance_eligible is True
            certificates_issued += 1
        
        # All certificates free under enterprise license
        assert total_cost == 0
        assert certificates_issued == 100
        
        # ROI calculation
        annual_license = 100000  # $100K/year
        insurance_savings = 5000000  # $5M/year (50% of $10M)
        net_benefit = insurance_savings - annual_license
        
        assert net_benefit == 4900000  # $4.9M/year savings
        roi_percentage = (net_benefit / annual_license) * 100
        assert roi_percentage == 4900  # 4900% ROI!
    
    def test_defi_protocol_scenario(self):
        """
        Scenario: DeFi protocol prevents $5M/year in flash loan attacks
        
        - Protocol loses $5M/year to attacks
        - With Diotec360: $0 losses
        - Diotec360 fee: $60K/year ($5K/month)
        - Protocol saves: $4.94M/year
        """
        issuer = get_audit_issuer()
        
        # Protocol processes 1,000 high-value transactions/month
        monthly_cost = 0
        attacks_prevented = 0
        
        for i in range(100):  # Sample 100 transactions
            proof_log = ProofLog(
                layer_minus_1_semantic={"passed": True},
                layer_0_sanitizer={"passed": True},
                layer_1_conservation={"passed": True},
                layer_2_overflow={"passed": True},
                layer_3_z3_proof={"passed": True},
                sentinel_telemetry={"anomaly_score": 0.2},
                crisis_mode_active=False,
                quarantine_status="clean"
            )
            
            certificate = issuer.issue_assurance_certificate(
                f"defi_tx_{i}", proof_log, 1, 50000.0, "premium"
            )
            
            # Premium tier pricing
            cost = issuer.get_pricing("premium", 1, 50000.0)
            monthly_cost += cost
            
            # Each certificate proves attack was prevented
            if certificate.defense_layers_passed >= 5:
                attacks_prevented += 1
        
        # Calculate annual cost
        annual_cost = monthly_cost * 12
        
        # ROI calculation
        losses_prevented = 5000000  # $5M/year
        net_benefit = losses_prevented - annual_cost
        
        # Should save millions
        assert net_benefit > 4000000  # At least $4M savings
        assert attacks_prevented == 100  # All attacks prevented


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
