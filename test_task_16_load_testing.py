"""
Task 16.1: Load Testing Script for Diotec360-Pilot v3.7

This script simulates 10 concurrent users making autocomplete requests
to measure response times under load and monitor resource usage.

Requirements: 10.5
"""

import asyncio
import time
import statistics
import psutil
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


if os.environ.get('DIOTEC360_OFFLINE', '').lower() in {'1', 'true', 'yes', 'on'} or \
    os.environ.get('DIOTEC360_TEST_MODE', '').lower() in {'1', 'true', 'yes', 'on'}:
    import pytest
    pytest.skip("offline mode", allow_module_level=True)

# Import the API endpoint
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.autopilot import router, SuggestionsRequest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@dataclass
class LoadTestResult:
    """Results from a single request"""
    user_id: int
    request_num: int
    response_time_ms: float
    status_code: int
    success: bool
    timestamp: float


@dataclass
class LoadTestSummary:
    """Summary statistics from load test"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    concurrent_users: int
    test_duration_seconds: float
    cpu_usage_percent: float
    memory_usage_mb: float


# Sample Diotec360 code for testing
SAMPLE_CODES = [
    """intent payment {
    guard amount > 0
    verify balance_after == balance_before - amount
}""",
    """intent transfer {
    guard sender.balance >= amount
    guard amount > 0
    verify sender.balance_after == sender.balance_before - amount
}""",
    """intent swap {
    guard token_a_amount > 0
    guard token_b_amount > 0
    verify conservation
}""",
    """intent deposit {
    guard amount > 0
    verify vault.balance_after == vault.balance_before + amount
}""",
    """intent withdraw {
    guard amount <= balance
    verify balance_after == balance_before - amount
}"""
]


async def simulate_user(user_id: int, num_requests: int) -> List[LoadTestResult]:
    """
    Simulate a single user making multiple autocomplete requests.
    
    Args:
        user_id: Unique identifier for this user
        num_requests: Number of requests this user should make
        
    Returns:
        List of LoadTestResult objects
    """
    results = []
    
    for req_num in range(num_requests):
        # Select a sample code
        code = SAMPLE_CODES[req_num % len(SAMPLE_CODES)]
        cursor_position = len(code) // 2  # Middle of the code
        
        # Create request
        request_data = {
            "code": code,
            "cursor_position": cursor_position
        }
        
        # Measure response time
        start_time = time.time()
        try:
            response = client.post("/api/autopilot/suggestions", json=request_data)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            success = response.status_code == 200
            
            results.append(LoadTestResult(
                user_id=user_id,
                request_num=req_num,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                success=success,
                timestamp=start_time
            ))
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            results.append(LoadTestResult(
                user_id=user_id,
                request_num=req_num,
                response_time_ms=response_time_ms,
                status_code=500,
                success=False,
                timestamp=start_time
            ))
        
        # Small delay between requests (simulate typing)
        await asyncio.sleep(0.5)
    
    return results


async def run_load_test(num_users: int = 10, requests_per_user: int = 10) -> LoadTestSummary:
    """
    Run load test with multiple concurrent users.
    
    Args:
        num_users: Number of concurrent users to simulate
        requests_per_user: Number of requests each user makes
        
    Returns:
        LoadTestSummary with statistics
    """
    print(f"\n{'='*60}")
    print(f"Starting Load Test: {num_users} concurrent users")
    print(f"Requests per user: {requests_per_user}")
    print(f"Total requests: {num_users * requests_per_user}")
    print(f"{'='*60}\n")
    
    # Get initial resource usage
    process = psutil.Process()
    initial_cpu = process.cpu_percent(interval=1)
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Start load test
    start_time = time.time()
    
    # Create tasks for all users
    tasks = [simulate_user(user_id, requests_per_user) for user_id in range(num_users)]
    
    # Run all users concurrently
    all_results = await asyncio.gather(*tasks)
    
    # Flatten results
    results: List[LoadTestResult] = []
    for user_results in all_results:
        results.extend(user_results)
    
    end_time = time.time()
    test_duration = end_time - start_time
    
    # Get final resource usage
    final_cpu = process.cpu_percent(interval=1)
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    avg_cpu = (initial_cpu + final_cpu) / 2
    avg_memory = (initial_memory + final_memory) / 2
    
    # Calculate statistics
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]
    
    if successful_results:
        response_times = [r.response_time_ms for r in successful_results]
        
        summary = LoadTestSummary(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            avg_response_time_ms=statistics.mean(response_times),
            p50_response_time_ms=statistics.median(response_times),
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times),
            min_response_time_ms=min(response_times),
            max_response_time_ms=max(response_times),
            requests_per_second=len(results) / test_duration,
            concurrent_users=num_users,
            test_duration_seconds=test_duration,
            cpu_usage_percent=avg_cpu,
            memory_usage_mb=avg_memory
        )
    else:
        # All requests failed
        summary = LoadTestSummary(
            total_requests=len(results),
            successful_requests=0,
            failed_requests=len(failed_results),
            avg_response_time_ms=0,
            p50_response_time_ms=0,
            p95_response_time_ms=0,
            p99_response_time_ms=0,
            min_response_time_ms=0,
            max_response_time_ms=0,
            requests_per_second=0,
            concurrent_users=num_users,
            test_duration_seconds=test_duration,
            cpu_usage_percent=avg_cpu,
            memory_usage_mb=avg_memory
        )
    
    return summary


def print_summary(summary: LoadTestSummary):
    """Print load test summary in a readable format"""
    print(f"\n{'='*60}")
    print("LOAD TEST RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Test Configuration:")
    print(f"  Concurrent Users: {summary.concurrent_users}")
    print(f"  Total Requests: {summary.total_requests}")
    print(f"  Test Duration: {summary.test_duration_seconds:.2f}s")
    print()
    
    print(f"Request Results:")
    print(f"  Successful: {summary.successful_requests} ({summary.successful_requests/summary.total_requests*100:.1f}%)")
    print(f"  Failed: {summary.failed_requests} ({summary.failed_requests/summary.total_requests*100:.1f}%)")
    print(f"  Throughput: {summary.requests_per_second:.2f} req/s")
    print()
    
    print(f"Response Times (ms):")
    print(f"  Average: {summary.avg_response_time_ms:.2f}")
    print(f"  Median (P50): {summary.p50_response_time_ms:.2f}")
    print(f"  P95: {summary.p95_response_time_ms:.2f}")
    print(f"  P99: {summary.p99_response_time_ms:.2f}")
    print(f"  Min: {summary.min_response_time_ms:.2f}")
    print(f"  Max: {summary.max_response_time_ms:.2f}")
    print()
    
    print(f"Resource Usage:")
    print(f"  CPU: {summary.cpu_usage_percent:.1f}%")
    print(f"  Memory: {summary.memory_usage_mb:.1f} MB")
    print()
    
    # Check if performance targets are met
    print(f"Performance Targets:")
    target_p95 = 250  # ms
    if summary.p95_response_time_ms <= target_p95:
        print(f"  ✓ P95 < {target_p95}ms: PASS ({summary.p95_response_time_ms:.2f}ms)")
    else:
        print(f"  ✗ P95 < {target_p95}ms: FAIL ({summary.p95_response_time_ms:.2f}ms)")
    
    if summary.successful_requests == summary.total_requests:
        print(f"  ✓ All requests successful: PASS")
    else:
        print(f"  ✗ All requests successful: FAIL ({summary.failed_requests} failures)")
    
    print(f"\n{'='*60}\n")


def save_results(summary: LoadTestSummary, filename: str = "load_test_results.json"):
    """Save load test results to JSON file"""
    results_dict = {
        "timestamp": datetime.now().isoformat(),
        "total_requests": summary.total_requests,
        "successful_requests": summary.successful_requests,
        "failed_requests": summary.failed_requests,
        "avg_response_time_ms": summary.avg_response_time_ms,
        "p50_response_time_ms": summary.p50_response_time_ms,
        "p95_response_time_ms": summary.p95_response_time_ms,
        "p99_response_time_ms": summary.p99_response_time_ms,
        "min_response_time_ms": summary.min_response_time_ms,
        "max_response_time_ms": summary.max_response_time_ms,
        "requests_per_second": summary.requests_per_second,
        "concurrent_users": summary.concurrent_users,
        "test_duration_seconds": summary.test_duration_seconds,
        "cpu_usage_percent": summary.cpu_usage_percent,
        "memory_usage_mb": summary.memory_usage_mb
    }
    
    with open(filename, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"Results saved to {filename}")


async def main():
    """Main entry point for load testing"""
    # Run load test with 10 concurrent users
    summary = await run_load_test(num_users=10, requests_per_user=10)
    
    # Print results
    print_summary(summary)
    
    # Save results
    save_results(summary)
    
    # Return summary for testing
    return summary


if __name__ == "__main__":
    # Run the load test
    summary = asyncio.run(main())
    
    # Exit with appropriate code
    if summary.p95_response_time_ms <= 250 and summary.failed_requests == 0:
        print("✓ Load test PASSED")
        exit(0)
    else:
        print("✗ Load test FAILED")
        exit(1)
