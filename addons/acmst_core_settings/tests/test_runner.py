# -*- coding: utf-8 -*-

"""
ACMST Core Settings Test Runner

This script provides a comprehensive test runner for the ACMST Core Settings module.
It includes unit tests, integration tests, performance tests, and security tests.

Usage:
    python test_runner.py [--verbose] [--performance] [--security] [--all]

Options:
    --verbose: Enable verbose output
    --performance: Run performance tests only
    --security: Run security tests only
    --all: Run all tests (default)
"""

import sys
import os
import time
import argparse
from unittest import TestLoader, TextTestRunner, TestSuite

# Add the addons path to sys.path
addons_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, addons_path)

def run_tests(test_type='all', verbose=False):
    """Run tests based on the specified type"""
    
    # Test modules to run
    test_modules = {
        'unit': [
            'test_acmst_university',
            'test_acmst_college', 
            'test_acmst_program_type',
            'test_acmst_batch_creation_wizard'
        ],
        'performance': [
            'test_performance'
        ],
        'security': [
            'test_security'
        ]
    }
    
    if test_type == 'all':
        modules_to_run = []
        for module_list in test_modules.values():
            modules_to_run.extend(module_list)
    else:
        modules_to_run = test_modules.get(test_type, [])
    
    if not modules_to_run:
        print(f"No tests found for type: {test_type}")
        return False
    
    # Create test suite
    loader = TestLoader()
    suite = TestSuite()
    
    for module_name in modules_to_run:
        try:
            module = __import__(module_name)
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            print(f"Loaded {tests.countTestCases()} tests from {module_name}")
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
        except Exception as e:
            print(f"Error loading {module_name}: {e}")
    
    if suite.countTestCases() == 0:
        print("No tests to run")
        return False
    
    # Run tests
    print(f"\nRunning {suite.countTestCases()} tests...")
    print("=" * 50)
    
    start_time = time.time()
    runner = TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    
    return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='ACMST Core Settings Test Runner')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    parser.add_argument('--security', action='store_true',
                       help='Run security tests only')
    parser.add_argument('--unit', action='store_true',
                       help='Run unit tests only')
    parser.add_argument('--all', action='store_true', default=True,
                       help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # Determine test type
    if args.performance:
        test_type = 'performance'
    elif args.security:
        test_type = 'security'
    elif args.unit:
        test_type = 'unit'
    else:
        test_type = 'all'
    
    print("ACMST Core Settings Test Runner")
    print("=" * 50)
    print(f"Test type: {test_type}")
    print(f"Verbose: {args.verbose}")
    print("=" * 50)
    
    # Run tests
    success = run_tests(test_type, args.verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
