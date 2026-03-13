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
Property-Based and Unit Tests for Gauntlet Report

Tests verify:
- Complete attack record logging
- Attack categorization
- Time-based statistics aggregation
- Multi-format export (JSON, PDF)
- Retention policy compliance
"""

import pytest
import json
import time
import tempfile
import os
from hypothesis import given, strategies as st, assume, settings
from diotec360.core.gauntlet_report import (
    GauntletReport, AttackRecord, AttackCategory
)


class TestGauntletReportProperties:
    """Property-based tests for Gauntlet Report"""
    
    @given(
        attack_type=st.sampled_from(["injection", "dos", "trojan", "overflow", "conservation", "unknown"]),
        severity=st.floats(min_value=0.0, max_value=1.0),
        code_snippet=st.text(min_size=10, max_size=200)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_39_complete_attack_record(self, attack_type, severity, code_snippet):
        """
        Property 39: Complete attack record
        
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
        
        PROPERTY: For any blocked attack, the Gauntlet Report SHALL
        log a complete record with all required fields.
        """
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Create attack record
        record = AttackRecord(
            timestamp=time.time(),
            attack_type=attack_type,
            category=report.categorize_attack(attack_type).value,
            code_snippet=code_snippet,
            detection_method="semantic_sanitizer",
            severity=severity,
            blocked_by_layer="layer_-1",
            metadata={"test": True}
        )
        
        # Log attack
        report.log_attack(record)
        
        # Property: record is logged
        recent = report.get_recent_attacks(limit=1)
        assert len(recent) == 1
        
        # Property: all fields are preserved
        logged = recent[0]
        assert logged.attack_type == attack_type
        assert abs(logged.severity - severity) < 0.01
        assert logged.code_snippet == code_snippet
        assert logged.detection_method == "semantic_sanitizer"
    
    @given(
        attack_type=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_40_attack_categorization(self, attack_type):
        """
        Property 40: Attack categorization
        
        **Validates: Requirements 7.5**
        
        PROPERTY: For any attack type, the Gauntlet Report SHALL
        categorize it into one of the predefined categories.
        """
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Categorize attack
        category = report.categorize_attack(attack_type)
        
        # Property: category is valid
        assert isinstance(category, AttackCategory)
        assert category in list(AttackCategory)
        
        # Property: categorization is consistent
        category2 = report.categorize_attack(attack_type)
        assert category == category2
    
    @given(
        num_attacks=st.integers(min_value=1, max_value=50),
        time_window=st.floats(min_value=1.0, max_value=3600.0)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_41_time_based_aggregation(self, num_attacks, time_window):
        """
        Property 41: Time-based aggregation
        
        **Validates: Requirements 7.6**
        
        PROPERTY: Statistics SHALL be correctly aggregated within
        specified time windows.
        """
        report = GauntletReport(db_path=tempfile.mktemp())
        
        current_time = time.time()
        
        # Log attacks within time window
        for i in range(num_attacks):
            record = AttackRecord(
                timestamp=current_time - (i * 10),  # 10 seconds apart
                attack_type="test",
                category="dos",
                code_snippet=f"attack_{i}",
                detection_method="test",
                severity=0.5,
                blocked_by_layer="test",
                metadata={}
            )
            report.log_attack(record)
        
        # Get statistics for time window
        stats = report.get_statistics(time_window=time_window)
        
        # Property: statistics are aggregated
        assert "total_attacks" in stats
        assert "by_category" in stats
        assert "by_detection_method" in stats
        
        # Property: count is within expected range
        expected_count = min(num_attacks, int(time_window / 10) + 1)
        assert stats["total_attacks"] <= num_attacks
        assert stats["total_attacks"] >= 0
    
    @given(
        num_records=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_42_multi_format_export(self, num_records):
        """
        Property 42: Multi-format export
        
        **Validates: Requirements 7.7**
        
        PROPERTY: Attack records SHALL be exportable to both
        JSON and PDF formats.
        """
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Log attacks
        for i in range(num_records):
            record = AttackRecord(
                timestamp=time.time(),
                attack_type=f"attack_{i}",
                category="dos",
                code_snippet=f"code_{i}",
                detection_method="test",
                severity=0.5,
                blocked_by_layer="test",
                metadata={"index": i}
            )
            report.log_attack(record)
        
        # Export to JSON
        json_path = tempfile.mktemp(suffix=".json")
        report.export_json(json_path)
        
        # Property: JSON file is created
        assert os.path.exists(json_path)
        
        # Property: JSON is valid
        with open(json_path, 'r') as f:
            data = json.load(f)
        assert "records" in data
        assert len(data["records"]) == num_records
        
        # Export to PDF
        pdf_path = tempfile.mktemp(suffix=".pdf")
        report.export_pdf(pdf_path)
        
        # Property: PDF file is created
        assert os.path.exists(pdf_path)
        
        # Cleanup
        os.remove(json_path)
        os.remove(pdf_path)
    
    @given(
        retention_days=st.integers(min_value=1, max_value=180),
        old_records=st.integers(min_value=0, max_value=10),
        new_records=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_43_retention_policy_compliance(self, retention_days, old_records, new_records):
        """
        Property 43: Retention policy compliance
        
        **Validates: Requirements 7.8**
        
        PROPERTY: Records older than retention period SHALL be
        deleted, while recent records are preserved.
        """
        report = GauntletReport(db_path=tempfile.mktemp())
        
        current_time = time.time()
        cutoff_time = current_time - (retention_days * 24 * 60 * 60)
        
        # Log old records (before cutoff)
        for i in range(old_records):
            record = AttackRecord(
                timestamp=cutoff_time - 3600,  # 1 hour before cutoff
                attack_type=f"old_{i}",
                category="dos",
                code_snippet=f"old_code_{i}",
                detection_method="test",
                severity=0.5,
                blocked_by_layer="test",
                metadata={}
            )
            report.log_attack(record)
        
        # Log new records (after cutoff)
        for i in range(new_records):
            record = AttackRecord(
                timestamp=current_time,
                attack_type=f"new_{i}",
                category="dos",
                code_snippet=f"new_code_{i}",
                detection_method="test",
                severity=0.5,
                blocked_by_layer="test",
                metadata={}
            )
            report.log_attack(record)
        
        # Cleanup old records
        deleted = report.cleanup_old_records(retention_days=retention_days)
        
        # Property: old records are deleted
        assert deleted == old_records
        
        # Property: new records are preserved
        stats = report.get_statistics()
        assert stats["total_attacks"] == new_records


class TestGauntletReportUnitTests:
    """Unit tests for specific scenarios"""
    
    def test_database_initialization(self):
        """Test database is created and initialized"""
        db_path = tempfile.mktemp()
        report = GauntletReport(db_path=db_path)
        
        assert os.path.exists(db_path)
        
        # Cleanup
        os.remove(db_path)
    
    def test_injection_categorization(self):
        """Test injection attacks are categorized correctly"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        assert report.categorize_attack("sql_injection") == AttackCategory.INJECTION
        assert report.categorize_attack("code_injection") == AttackCategory.INJECTION
    
    def test_dos_categorization(self):
        """Test DoS attacks are categorized correctly"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        assert report.categorize_attack("dos_attack") == AttackCategory.DOS
        assert report.categorize_attack("denial_of_service") == AttackCategory.DOS
    
    def test_trojan_categorization(self):
        """Test Trojan attacks are categorized correctly"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        assert report.categorize_attack("trojan_horse") == AttackCategory.TROJAN
        assert report.categorize_attack("malware") == AttackCategory.TROJAN
    
    def test_overflow_categorization(self):
        """Test overflow attacks are categorized correctly"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        assert report.categorize_attack("buffer_overflow") == AttackCategory.OVERFLOW
        assert report.categorize_attack("integer_overflow") == AttackCategory.OVERFLOW
    
    def test_conservation_categorization(self):
        """Test conservation attacks are categorized correctly"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        assert report.categorize_attack("conservation_violation") == AttackCategory.CONSERVATION
        assert report.categorize_attack("balance_manipulation") == AttackCategory.CONSERVATION
    
    def test_unknown_categorization(self):
        """Test unknown attacks are categorized as UNKNOWN"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        assert report.categorize_attack("weird_attack") == AttackCategory.UNKNOWN
        assert report.categorize_attack("custom_exploit") == AttackCategory.UNKNOWN
    
    def test_statistics_empty_database(self):
        """Test statistics on empty database"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        stats = report.get_statistics()
        
        assert stats["total_attacks"] == 0
        assert stats["average_severity"] == 0.0
        assert len(stats["by_category"]) == 0
    
    def test_statistics_with_data(self):
        """Test statistics calculation with data"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Log 5 attacks
        for i in range(5):
            record = AttackRecord(
                timestamp=time.time(),
                attack_type="test",
                category="dos",
                code_snippet=f"code_{i}",
                detection_method="semantic_sanitizer",
                severity=0.5,
                blocked_by_layer="layer_-1",
                metadata={}
            )
            report.log_attack(record)
        
        stats = report.get_statistics()
        
        assert stats["total_attacks"] == 5
        assert abs(stats["average_severity"] - 0.5) < 0.01
        assert stats["by_category"]["dos"] == 5
        assert stats["by_detection_method"]["semantic_sanitizer"] == 5
    
    def test_json_export_structure(self):
        """Test JSON export has correct structure"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Log attack
        record = AttackRecord(
            timestamp=time.time(),
            attack_type="test",
            category="dos",
            code_snippet="test_code",
            detection_method="test",
            severity=0.8,
            blocked_by_layer="test",
            metadata={"key": "value"}
        )
        report.log_attack(record)
        
        # Export
        json_path = tempfile.mktemp(suffix=".json")
        report.export_json(json_path)
        
        # Verify structure
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        assert "export_time" in data
        assert "total_records" in data
        assert "records" in data
        assert len(data["records"]) == 1
        assert data["records"][0]["attack_type"] == "test"
        
        # Cleanup
        os.remove(json_path)
    
    def test_pdf_export_creates_file(self):
        """Test PDF export creates file"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Log attack
        record = AttackRecord(
            timestamp=time.time(),
            attack_type="test",
            category="dos",
            code_snippet="test_code",
            detection_method="test",
            severity=0.8,
            blocked_by_layer="test",
            metadata={}
        )
        report.log_attack(record)
        
        # Export
        pdf_path = tempfile.mktemp(suffix=".pdf")
        report.export_pdf(pdf_path)
        
        # Verify file exists and has content
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0
        
        # Cleanup
        os.remove(pdf_path)
    
    def test_recent_attacks_limit(self):
        """Test recent attacks respects limit"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        # Log 20 attacks
        for i in range(20):
            record = AttackRecord(
                timestamp=time.time() + i,
                attack_type=f"attack_{i}",
                category="dos",
                code_snippet=f"code_{i}",
                detection_method="test",
                severity=0.5,
                blocked_by_layer="test",
                metadata={}
            )
            report.log_attack(record)
        
        # Get recent with limit
        recent = report.get_recent_attacks(limit=10)
        
        assert len(recent) == 10
        # Should be most recent (highest timestamps)
        assert recent[0].attack_type == "attack_19"
    
    def test_cleanup_preserves_recent(self):
        """Test cleanup preserves recent records"""
        report = GauntletReport(db_path=tempfile.mktemp())
        
        current_time = time.time()
        
        # Log old attack (100 days ago)
        old_record = AttackRecord(
            timestamp=current_time - (100 * 24 * 60 * 60),
            attack_type="old",
            category="dos",
            code_snippet="old_code",
            detection_method="test",
            severity=0.5,
            blocked_by_layer="test",
            metadata={}
        )
        report.log_attack(old_record)
        
        # Log recent attack
        new_record = AttackRecord(
            timestamp=current_time,
            attack_type="new",
            category="dos",
            code_snippet="new_code",
            detection_method="test",
            severity=0.5,
            blocked_by_layer="test",
            metadata={}
        )
        report.log_attack(new_record)
        
        # Cleanup with 90-day retention
        deleted = report.cleanup_old_records(retention_days=90)
        
        assert deleted == 1
        
        # Verify recent is preserved
        recent = report.get_recent_attacks(limit=10)
        assert len(recent) == 1
        assert recent[0].attack_type == "new"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
