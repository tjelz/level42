#!/usr/bin/env python3
"""
Integration test runner for x402-Agent Framework.

This script runs integration tests with proper environment setup and reporting.
It can run tests against real testnets or with mocked services.
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any


def setup_test_environment(use_testnet: bool = False):
    """Set up environment for integration testing."""
    # Set test environment variables
    os.environ["X402_TEST_MODE"] = "true"
    os.environ["X402_DEBUG"] = "true"
    
    if use_testnet:
        # Use actual testnet endpoints
        os.environ["X402_BASE_RPC_URL"] = "https://goerli.base.org"
        os.environ["X402_SOLANA_RPC_URL"] = "https://api.devnet.solana.com"
        print("🌐 Using testnet endpoints for integration tests")
    else:
        # Use mocked services
        os.environ["X402_MOCK_NETWORKS"] = "true"
        print("🔧 Using mocked services for integration tests")


def run_tests(test_pattern: str = None, verbose: bool = True, coverage: bool = True) -> int:
    """Run integration tests with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    cmd.append("tests/integration/")
    
    # Add test pattern if specified
    if test_pattern:
        cmd.extend(["-k", test_pattern])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=x402_agent",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/integration"
        ])
    
    # Add markers for integration tests
    cmd.extend(["-m", "integration"])
    
    # Add output formatting
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--strict-config"
    ])
    
    print(f"🧪 Running command: {' '.join(cmd)}")
    
    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    end_time = time.time()
    
    print(f"\n⏱️  Tests completed in {end_time - start_time:.2f} seconds")
    
    return result.returncode


def run_specific_test_suites():
    """Run specific test suites with different configurations."""
    test_suites = [
        {
            "name": "End-to-End Tests",
            "pattern": "test_e2e",
            "description": "Complete user workflows"
        },
        {
            "name": "Network Integration Tests",
            "pattern": "test_networks",
            "description": "Blockchain network integration"
        },
        {
            "name": "Multi-Agent Tests",
            "pattern": "TestMultiAgentIntegration",
            "description": "Agent swarm coordination"
        },
        {
            "name": "External API Tests",
            "pattern": "TestExternalAPIIntegration",
            "description": "External API integration"
        }
    ]
    
    results = {}
    
    for suite in test_suites:
        print(f"\n{'='*60}")
        print(f"🧪 Running {suite['name']}")
        print(f"📝 {suite['description']}")
        print(f"{'='*60}")
        
        result = run_tests(
            test_pattern=suite["pattern"],
            verbose=True,
            coverage=False
        )
        
        results[suite["name"]] = result
        
        if result == 0:
            print(f"✅ {suite['name']} passed")
        else:
            print(f"❌ {suite['name']} failed")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Suite Summary")
    print(f"{'='*60}")
    
    for suite_name, result in results.items():
        status = "✅ PASSED" if result == 0 else "❌ FAILED"
        print(f"{suite_name}: {status}")
    
    # Overall result
    overall_result = 0 if all(result == 0 for result in results.values()) else 1
    
    if overall_result == 0:
        print("\n🎉 All integration test suites passed!")
    else:
        print("\n💥 Some integration test suites failed!")
    
    return overall_result


def check_dependencies():
    """Check if required dependencies are available."""
    required_packages = [
        "pytest",
        "pytest-cov",
        "requests",
        "web3"
    ]
    
    optional_packages = [
        "solana",
        "solders"
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install -e '.[dev]'")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("Some tests may be skipped. Install with: pip install -e '.[solana]'")
    
    print("✅ All required dependencies available")
    return True


def main():
    """Main entry point for integration test runner."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for x402-Agent Framework"
    )
    
    parser.add_argument(
        "--testnet",
        action="store_true",
        help="Use real testnet endpoints instead of mocks"
    )
    
    parser.add_argument(
        "--pattern", "-k",
        type=str,
        help="Run tests matching this pattern"
    )
    
    parser.add_argument(
        "--suites",
        action="store_true",
        help="Run specific test suites separately"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    print("🚀 x402-Agent Framework Integration Test Runner")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Setup test environment
    setup_test_environment(use_testnet=args.testnet)
    
    # Run tests
    if args.suites:
        result = run_specific_test_suites()
    else:
        result = run_tests(
            test_pattern=args.pattern,
            verbose=not args.quiet,
            coverage=not args.no_coverage
        )
    
    # Final result
    if result == 0:
        print("\n🎉 Integration tests completed successfully!")
    else:
        print("\n💥 Integration tests failed!")
        print("Check the output above for details.")
    
    return result


if __name__ == "__main__":
    sys.exit(main())