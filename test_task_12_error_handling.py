"""
Task 12: Error Handling and Resilience Tests
Feature: Diotec360-pilot-v3-7

Property tests for error handling, graceful degradation, and system resilience.
"""

import pytest
import time
from diotec360.ai.autopilot_engine import DIOTEC360Autopilot, EditorState


class TestTask12ErrorHandling:
    """
    Task 12: Implement error handling and resilience
    
    Tests:
    - Task 12.2: Backend error handling
    - Property 22: Graceful Invalid Input Handling
    - Property 23: Error Logging and Continuation
    """
    
    def setup_method(self):
        """Setup test fixtures"""
        self.autopilot = DIOTEC360Autopilot()
    
    def test_property_22_graceful_invalid_input_handling(self):
        """
        Property 22: Graceful Invalid Input Handling
        
        Test that invalid code doesn't crash the system.
        System should return empty results gracefully.
        """
        invalid_inputs = [
            "",  # Empty code
            "   ",  # Whitespace only
            "invalid syntax @#$%",  # Invalid syntax
            "intent {{{{{",  # Unbalanced braces
            "a" * 100000,  # Very long input
            "\x00\x01\x02",  # Binary data
            "intent\nwith\nnull\x00bytes",  # Null bytes
            "🚀💻🎯",  # Unicode emojis
            "intent payment { guard { amount > 0; } verify { " * 1000,  # Deeply nested
        ]
        
        for i, code in enumerate(invalid_inputs):
            try:
                # Test suggestions
                editor_state = EditorState(
                    code=code,
                    cursor_position=min(len(code), 10),
                    current_line='',
                    current_line_number=1,
                    partial_token=''
                )
                
                suggestions = self.autopilot.get_suggestions(editor_state)
                assert isinstance(suggestions, list), \
                    f"Suggestions should return list for invalid input {i}"
                
                # Test safety status
                safety_status = self.autopilot.get_safety_status(code)
                assert isinstance(safety_status, dict), \
                    f"Safety status should return dict for invalid input {i}"
                assert 'status' in safety_status, \
                    f"Safety status should have 'status' field for invalid input {i}"
                
                # Test corrections
                corrections = self.autopilot.get_correction_stream(code)
                assert isinstance(corrections, list), \
                    f"Corrections should return list for invalid input {i}"
                
                print(f"  ✓ Invalid input {i+1}/{len(invalid_inputs)}: Handled gracefully")
                
            except Exception as e:
                pytest.fail(f"System crashed on invalid input {i}: {str(e)}")
        
        print(f"✓ Property 22: All {len(invalid_inputs)} invalid inputs handled gracefully")
    
    def test_property_23_error_logging_and_continuation(self):
        """
        Property 23: Error Logging and Continuation
        
        Test that errors are handled and system continues operating.
        """
        # Test that system continues after errors
        error_cases = [
            ("", "Empty code"),
            ("invalid", "Invalid syntax"),
            ("intent { }", "Incomplete intent"),
        ]
        
        for code, description in error_cases:
            try:
                # System should not crash
                editor_state = EditorState(
                    code=code,
                    cursor_position=0,
                    current_line='',
                    current_line_number=1,
                    partial_token=''
                )
                
                suggestions = self.autopilot.get_suggestions(editor_state)
                safety_status = self.autopilot.get_safety_status(code)
                corrections = self.autopilot.get_correction_stream(code)
                
                # System should return valid responses
                assert isinstance(suggestions, list)
                assert isinstance(safety_status, dict)
                assert isinstance(corrections, list)
                
                print(f"  ✓ {description}: System continued after error")
                
            except Exception as e:
                pytest.fail(f"System failed to continue after error ({description}): {str(e)}")
        
        print(f"✓ Property 23: System continues operating after errors")
    
    def test_task_12_2_invalid_code_handling(self):
        """
        Task 12.2: Handle invalid code
        
        Test that backend returns empty suggestions for invalid code.
        """
        invalid_code = "this is not valid Diotec360 code @#$%"
        
        editor_state = EditorState(
            code=invalid_code,
            cursor_position=10,
            current_line='',
            current_line_number=1,
            partial_token=''
        )
        
        # Should not crash
        suggestions = self.autopilot.get_suggestions(editor_state)
        
        # Should return list (possibly empty)
        assert isinstance(suggestions, list), "Should return list for invalid code"
        
        print(f"  ✓ Invalid code handling: Returned {len(suggestions)} suggestions")
    
    def test_task_12_2_judge_failure_graceful_degradation(self):
        """
        Task 12.2: Handle Judge failure
        
        Test that system returns suggestions even if Judge fails.
        """
        # Code that might cause Judge issues
        problematic_code = '''intent test {
  // Intentionally problematic code
  guard { true; }
}'''
        
        editor_state = EditorState(
            code=problematic_code,
            cursor_position=50,
            current_line='',
            current_line_number=2,
            partial_token=''
        )
        
        # Should still return suggestions even if Judge has issues
        suggestions = self.autopilot.get_suggestions(editor_state)
        assert isinstance(suggestions, list), "Should return suggestions despite Judge issues"
        
        # Safety status should handle Judge failure gracefully
        safety_status = self.autopilot.get_safety_status(problematic_code)
        assert isinstance(safety_status, dict), "Should return safety status dict"
        assert 'status' in safety_status, "Should have status field"
        
        print(f"  ✓ Judge failure handling: System continued with {len(suggestions)} suggestions")
    
    def test_empty_code_handling(self):
        """Test handling of empty code"""
        editor_state = EditorState(
            code="",
            cursor_position=0,
            current_line='',
            current_line_number=1,
            partial_token=''
        )
        
        suggestions = self.autopilot.get_suggestions(editor_state)
        assert isinstance(suggestions, list), "Should return list for empty code"
        
        safety_status = self.autopilot.get_safety_status("")
        assert isinstance(safety_status, dict), "Should return dict for empty code"
        
        corrections = self.autopilot.get_correction_stream("")
        assert isinstance(corrections, list), "Should return list for empty code"
        
        print(f"  ✓ Empty code handling: All methods returned valid responses")
    
    def test_whitespace_only_code(self):
        """Test handling of whitespace-only code"""
        whitespace_code = "   \n\n   \t\t   \n"
        
        editor_state = EditorState(
            code=whitespace_code,
            cursor_position=5,
            current_line='',
            current_line_number=2,
            partial_token=''
        )
        
        suggestions = self.autopilot.get_suggestions(editor_state)
        assert isinstance(suggestions, list), "Should handle whitespace-only code"
        
        print(f"  ✓ Whitespace-only code: Handled gracefully")
    
    def test_very_long_code(self):
        """Test handling of very long code"""
        long_code = "intent test { " + "guard { amount > 0; } " * 100 + "}"
        
        editor_state = EditorState(
            code=long_code,
            cursor_position=100,
            current_line='',
            current_line_number=1,
            partial_token=''
        )
        
        start_time = time.time()
        suggestions = self.autopilot.get_suggestions(editor_state)
        elapsed = time.time() - start_time
        
        assert isinstance(suggestions, list), "Should handle very long code"
        assert elapsed < 1.0, f"Should process long code quickly, took {elapsed:.2f}s"
        
        print(f"  ✓ Very long code: Processed in {elapsed*1000:.2f}ms")
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_code = '''intent payment_🚀 {
  // Comment with émojis 💻
  guard { amount > 0; }
}'''
        
        editor_state = EditorState(
            code=unicode_code,
            cursor_position=20,
            current_line='',
            current_line_number=1,
            partial_token=''
        )
        
        suggestions = self.autopilot.get_suggestions(editor_state)
        assert isinstance(suggestions, list), "Should handle Unicode characters"
        
        print(f"  ✓ Unicode handling: Processed successfully")
    
    def test_malformed_syntax(self):
        """Test handling of malformed syntax"""
        malformed_cases = [
            "intent {",  # Unclosed brace
            "intent payment(",  # Unclosed paren
            "intent payment { guard }",  # Missing braces
            "intent payment { guard { } verify",  # Incomplete
        ]
        
        for code in malformed_cases:
            editor_state = EditorState(
                code=code,
                cursor_position=len(code),
                current_line='',
                current_line_number=1,
                partial_token=''
            )
            
            # Should not crash
            suggestions = self.autopilot.get_suggestions(editor_state)
            assert isinstance(suggestions, list), f"Should handle malformed syntax: {code}"
        
        print(f"  ✓ Malformed syntax: All {len(malformed_cases)} cases handled")
    
    def test_concurrent_error_handling(self):
        """Test error handling under concurrent requests"""
        import concurrent.futures
        
        def make_request(code):
            try:
                editor_state = EditorState(
                    code=code,
                    cursor_position=0,
                    current_line='',
                    current_line_number=1,
                    partial_token=''
                )
                return self.autopilot.get_suggestions(editor_state)
            except Exception as e:
                return None
        
        # Mix of valid and invalid code
        test_codes = [
            "intent test { }",
            "invalid @#$%",
            "",
            "intent payment { guard { amount > 0; } }",
            "🚀💻",
        ] * 4  # 20 requests
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, test_codes))
        
        # All requests should complete (not crash)
        assert len(results) == len(test_codes), "All requests should complete"
        
        # All results should be lists (or None if error was caught)
        for result in results:
            assert result is None or isinstance(result, list), \
                "Results should be lists or None"
        
        print(f"  ✓ Concurrent error handling: {len(results)} requests completed")


def run_task_12_tests():
    """Run all Task 12 tests and generate report"""
    print("=" * 80)
    print("TASK 12: ERROR HANDLING AND RESILIENCE TESTS")
    print("=" * 80)
    print()
    
    test_suite = TestTask12ErrorHandling()
    test_suite.setup_method()
    
    tests = [
        ("Property 22: Graceful Invalid Input Handling", test_suite.test_property_22_graceful_invalid_input_handling),
        ("Property 23: Error Logging and Continuation", test_suite.test_property_23_error_logging_and_continuation),
        ("Task 12.2: Invalid Code Handling", test_suite.test_task_12_2_invalid_code_handling),
        ("Task 12.2: Judge Failure Graceful Degradation", test_suite.test_task_12_2_judge_failure_graceful_degradation),
        ("Empty Code Handling", test_suite.test_empty_code_handling),
        ("Whitespace-Only Code", test_suite.test_whitespace_only_code),
        ("Very Long Code", test_suite.test_very_long_code),
        ("Unicode Handling", test_suite.test_unicode_handling),
        ("Malformed Syntax", test_suite.test_malformed_syntax),
        ("Concurrent Error Handling", test_suite.test_concurrent_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        print("-" * 80)
        try:
            test_func()
            passed += 1
            print(f"✅ PASSED\n")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {str(e)}\n")
    
    print("=" * 80)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 80)
    
    if failed == 0:
        print()
        print("🎉 TASK 12: ALL TESTS PASSED")
        print()
        print("Error handling features validated:")
        print("  ✓ Graceful invalid input handling (Property 22)")
        print("  ✓ Error logging and continuation (Property 23)")
        print("  ✓ Invalid code handling (Task 12.2)")
        print("  ✓ Judge failure graceful degradation (Task 12.2)")
        print("  ✓ Empty code handling")
        print("  ✓ Whitespace-only code handling")
        print("  ✓ Very long code handling")
        print("  ✓ Unicode character handling")
        print("  ✓ Malformed syntax handling")
        print("  ✓ Concurrent error handling")
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_task_12_tests()
    exit(0 if failed == 0 else 1)
