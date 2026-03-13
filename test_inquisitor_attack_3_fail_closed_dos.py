"""
Test Inquisitor Attack 3: Fail-Closed DoS Exploitation

This test demonstrates how an attacker can exploit the fail-closed policy
to cause denial of service by sending transactions that force Z3 to timeout.

Attack Vector:
1. Create NP-complete constraints that force Z3 to timeout
2. Send multiple such transactions
3. Measure CPU time consumed by Judge
4. Calculate amplification ratio (attacker cost vs defender cost)

Expected Result: VULNERABILITY CONFIRMED (DoS amplification)

Author: Diotec360-Inquisitor (Red-Team Mode)
Date: February 22, 2026
"""

import pytest
import time
from diotec360.core.judge import DIOTEC360Judge


def create_np_complete_intent(num_vars: int = 50):
    """
    Create an intent with NP-complete constraints.
    
    This forces Z3 to explore a large search space, likely timing out.
    
    Args:
        num_vars: Number of variables (complexity increases exponentially)
    
    Returns:
        Intent dictionary with NP-complete constraints
    """
    # Create variables
    vars = [f'x{i}' for i in range(num_vars)]
    
    # Create constraints that form a 3-SAT problem (NP-complete)
    constraints = []
    post_conditions = []
    
    # Add complex interdependencies
    for i in range(num_vars):
        for j in range(i+1, min(i+5, num_vars)):
            for k in range(j+1, min(j+5, num_vars)):
                # 3-SAT clause: (xi OR xj OR xk)
                # Encoded as: xi + xj + xk >= 1
                post_conditions.append(f'{vars[i]} + {vars[j]} + {vars[k]} >= 1')
    
    # Add bounds
    for var in vars:
        constraints.append(f'{var} >= 0')
        constraints.append(f'{var} <= 1')
    
    return {
        'params': [{'name': var, 'type': 'int'} for var in vars],
        'constraints': constraints,
        'post_conditions': post_conditions
    }


def test_fail_closed_dos_single_transaction():
    """
    Test DoS attack with a single NP-complete transaction.
    
    Attack Scenario:
    1. Create NP-complete intent
    2. Submit to Judge
    3. Measure time to rejection
    4. Confirm Z3 timeout and fail-closed rejection
    """
    # Create Judge
    judge = DIOTEC360Judge(intent_map={}, enable_moe=False)
    
    # Create NP-complete intent
    intent_name = 'dos_attack_intent'
    intent = create_np_complete_intent(num_vars=30)
    judge.intent_map[intent_name] = intent
    
    print(f"\n🔍 [ATTACK 3] Fail-Closed DoS - Single Transaction")
    print(f"  Intent: {intent_name}")
    print(f"  Variables: {len(intent['params'])}")
    print(f"  Constraints: {len(intent['constraints'])}")
    print(f"  Post-conditions: {len(intent['post_conditions'])}")
    
    # Measure time to rejection
    start_time = time.time()
    
    result = judge.verify_logic(intent_name)
    
    end_time = time.time()
    elapsed_ms = (end_time - start_time) * 1000
    
    print(f"\n  Result: {result['status']}")
    print(f"  Message: {result['message']}")
    print(f"  Elapsed Time: {elapsed_ms:.0f}ms")
    
    # Analysis
    if result['status'] == 'REJECTED' and 'FAIL-CLOSED' in result['message']:
        print(f"  🚨 FAIL-CLOSED TRIGGERED: Z3 timeout detected")
        print(f"  ⚠️  Attacker cost: ~0ms (send transaction)")
        print(f"  ⚠️  Defender cost: {elapsed_ms:.0f}ms (Z3 timeout)")
        print(f"  ⚠️  Amplification ratio: 1:{elapsed_ms:.0f}")
    else:
        print(f"  ⚠️  Unexpected result: {result['status']}")
    
    # Confirm fail-closed rejection
    assert result['status'] == 'REJECTED', "Transaction should be rejected"
    assert 'FAIL-CLOSED' in result['message'] or 'unknown' in result['message'].lower(), \
        "Should be fail-closed rejection"
    
    # Confirm significant time consumption
    assert elapsed_ms > 1000, f"Should consume significant time (got {elapsed_ms:.0f}ms)"


def test_fail_closed_dos_amplification():
    """
    Test DoS amplification with multiple transactions.
    
    Attack Scenario:
    1. Send 10 NP-complete transactions
    2. Measure total CPU time consumed
    3. Calculate amplification ratio
    4. Confirm DoS vulnerability
    """
    # Create Judge
    judge = DIOTEC360Judge(intent_map={}, enable_moe=False)
    
    num_attacks = 10
    total_elapsed_ms = 0
    
    print(f"\n🔍 [ATTACK 3] Fail-Closed DoS - Amplification Test")
    print(f"  Number of attacks: {num_attacks}")
    
    for i in range(num_attacks):
        # Create unique NP-complete intent
        intent_name = f'dos_attack_{i}'
        intent = create_np_complete_intent(num_vars=25)
        judge.intent_map[intent_name] = intent
        
        # Measure time to rejection
        start_time = time.time()
        result = judge.verify_logic(intent_name)
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        total_elapsed_ms += elapsed_ms
        
        print(f"  Attack {i+1}: {result['status']} ({elapsed_ms:.0f}ms)")
    
    # Analysis
    avg_elapsed_ms = total_elapsed_ms / num_attacks
    attacker_cost_ms = 0.1  # Negligible cost to send transaction
    amplification_ratio = avg_elapsed_ms / attacker_cost_ms
    
    print(f"\n  📊 DoS Amplification Analysis:")
    print(f"  Total CPU time consumed: {total_elapsed_ms:.0f}ms")
    print(f"  Average time per attack: {avg_elapsed_ms:.0f}ms")
    print(f"  Attacker cost per attack: {attacker_cost_ms:.1f}ms")
    print(f"  Amplification ratio: 1:{amplification_ratio:.0f}")
    
    if amplification_ratio > 100:
        print(f"  🚨 CRITICAL VULNERABILITY: Amplification ratio > 100")
        print(f"  ⚠️  Attacker can cause significant DoS with minimal cost")
    
    # Confirm DoS vulnerability
    assert amplification_ratio > 100, \
        f"DoS amplification should be significant (got 1:{amplification_ratio:.0f})"


def test_fail_closed_dos_with_rate_limiting():
    """
    Test proposed mitigation: Rate limiting.
    
    Mitigation Strategy:
    - Limit transactions per second per identity
    - Reject transactions that exceed rate limit
    - Cost: O(1) per transaction
    """
    # Create Judge
    judge = DIOTEC360Judge(intent_map={}, enable_moe=False)
    
    # Simulate rate limiter
    rate_limit_per_second = 5
    rate_limit_window_ms = 1000
    
    # Track transaction timestamps per identity
    identity_timestamps = {}
    
    def check_rate_limit(identity: str) -> bool:
        """Check if identity exceeds rate limit"""
        now = time.time() * 1000  # milliseconds
        
        if identity not in identity_timestamps:
            identity_timestamps[identity] = []
        
        # Remove old timestamps outside window
        identity_timestamps[identity] = [
            ts for ts in identity_timestamps[identity]
            if now - ts < rate_limit_window_ms
        ]
        
        # Check if rate limit exceeded
        if len(identity_timestamps[identity]) >= rate_limit_per_second:
            return False  # Rate limit exceeded
        
        # Add current timestamp
        identity_timestamps[identity].append(now)
        return True  # Rate limit OK
    
    print(f"\n🛡️  [MITIGATION] Rate Limiting Test")
    print(f"  Rate limit: {rate_limit_per_second} tx/second")
    
    # Simulate attack with rate limiting
    identity = 'attacker_1'
    num_attacks = 20
    accepted = 0
    rejected_by_rate_limit = 0
    rejected_by_judge = 0
    
    for i in range(num_attacks):
        # Check rate limit BEFORE invoking Judge
        if not check_rate_limit(identity):
            rejected_by_rate_limit += 1
            print(f"  Attack {i+1}: REJECTED by rate limiter (0ms)")
            continue
        
        # Rate limit OK - proceed to Judge
        intent_name = f'dos_attack_{i}'
        intent = create_np_complete_intent(num_vars=25)
        judge.intent_map[intent_name] = intent
        
        start_time = time.time()
        result = judge.verify_logic(intent_name)
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        if result['status'] == 'REJECTED':
            rejected_by_judge += 1
            print(f"  Attack {i+1}: REJECTED by Judge ({elapsed_ms:.0f}ms)")
        else:
            accepted += 1
            print(f"  Attack {i+1}: ACCEPTED ({elapsed_ms:.0f}ms)")
    
    # Analysis
    print(f"\n  📊 Rate Limiting Results:")
    print(f"  Total attacks: {num_attacks}")
    print(f"  Rejected by rate limiter: {rejected_by_rate_limit}")
    print(f"  Rejected by Judge: {rejected_by_judge}")
    print(f"  Accepted: {accepted}")
    
    # Calculate CPU time saved
    avg_judge_time_ms = 2000  # Assume 2 second timeout
    cpu_time_saved_ms = rejected_by_rate_limit * avg_judge_time_ms
    
    print(f"  CPU time saved: {cpu_time_saved_ms:.0f}ms")
    print(f"  Mitigation effectiveness: {rejected_by_rate_limit / num_attacks * 100:.0f}%")
    
    # Confirm mitigation effectiveness
    assert rejected_by_rate_limit > 0, "Rate limiter should reject some attacks"
    assert rejected_by_rate_limit / num_attacks > 0.5, \
        "Rate limiter should reject majority of attacks"


def test_fail_closed_dos_with_complexity_analysis():
    """
    Test proposed mitigation: Complexity analysis before Z3.
    
    Mitigation Strategy:
    - Analyze constraint complexity before invoking Z3
    - Reject constraints with exponential complexity
    - Cost: O(n) where n = number of constraints
    """
    # Create Judge
    judge = DIOTEC360Judge(intent_map={}, enable_moe=False)
    
    def analyze_complexity(intent: dict) -> tuple[bool, str]:
        """
        Analyze constraint complexity.
        
        Returns:
            (is_safe, reason)
        """
        num_vars = len(intent.get('params', []))
        num_constraints = len(intent.get('constraints', []))
        num_post_conditions = len(intent.get('post_conditions', []))
        
        # Heuristic: Reject if too many variables or constraints
        if num_vars > 50:
            return False, f"Too many variables ({num_vars} > 50)"
        
        if num_constraints > 200:
            return False, f"Too many constraints ({num_constraints} > 200)"
        
        if num_post_conditions > 200:
            return False, f"Too many post-conditions ({num_post_conditions} > 200)"
        
        # Check for known NP-complete patterns
        # (simplified - real implementation would be more sophisticated)
        for condition in intent.get('post_conditions', []):
            # Detect 3-SAT pattern: "x + y + z >= 1"
            if '+' in condition and '>=' in condition:
                parts = condition.split('>=')
                if len(parts) == 2:
                    left = parts[0].strip()
                    if left.count('+') >= 2:
                        return False, "Detected 3-SAT pattern (NP-complete)"
        
        return True, "Complexity acceptable"
    
    print(f"\n🛡️  [MITIGATION] Complexity Analysis Test")
    
    # Test with NP-complete intent
    intent_name = 'dos_attack_complex'
    intent = create_np_complete_intent(num_vars=30)
    judge.intent_map[intent_name] = intent
    
    # Analyze complexity BEFORE invoking Judge
    start_time = time.time()
    is_safe, reason = analyze_complexity(intent)
    end_time = time.time()
    
    analysis_time_ms = (end_time - start_time) * 1000
    
    print(f"  Intent: {intent_name}")
    print(f"  Complexity analysis: {is_safe}")
    print(f"  Reason: {reason}")
    print(f"  Analysis time: {analysis_time_ms:.2f}ms")
    
    if not is_safe:
        print(f"  🛡️  REJECTED by complexity analysis (saved ~2000ms)")
        print(f"  ✅ Mitigation effective: O(n) analysis prevents O(2^n) Z3 timeout")
    else:
        print(f"  ⚠️  Complexity analysis passed - proceeding to Judge")
        
        # Invoke Judge
        start_time = time.time()
        result = judge.verify_logic(intent_name)
        end_time = time.time()
        
        judge_time_ms = (end_time - start_time) * 1000
        print(f"  Judge result: {result['status']} ({judge_time_ms:.0f}ms)")
    
    # Confirm mitigation effectiveness
    assert not is_safe, "Complexity analysis should detect NP-complete pattern"
    assert analysis_time_ms < 10, "Complexity analysis should be fast (< 10ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
