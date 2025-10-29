"""
Master Test Runner

Executes all backend test suites in logical order with proper error handling
and comprehensive reporting.

Test Organization:
- User Management: Database and API tests for user operations
- Resource Management: Database and API tests for resource operations  
- Session Management: Database and API tests for authentication/sessions
- Reservation System: Database and API tests for reservation lifecycle

Usage:
    python3 -m backend.tests.run_all_tests
"""

import sys
import os
import time
from pathlib import Path

# Color constants
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def run_test_module(module_name, description):
    """Run a test module and return success status"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Running {description}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        # Import and run the test module
        module = __import__(f'backend.tests.{module_name}', fromlist=[''])
        
        # Get all test functions from the module
        test_functions = [getattr(module, name) for name in dir(module) 
                         if name.startswith('test_') and callable(getattr(module, name))]
        
        if hasattr(module, '__main__') and module_name in sys.modules:
            # If module has __main__ section, execute it
            exec(compile(open(f'backend/tests/{module_name}.py').read(), f'{module_name}.py', 'exec'))
        else:
            # Otherwise run individual test functions
            for test_func in test_functions:
                test_func()
        
        print(f"\n{GREEN}✓ {description} - ALL TESTS PASSED{RESET}")
        return True
        
    except Exception as e:
        print(f"\n{RED}✗ {description} - TESTS FAILED: {str(e)}{RESET}")
        return False

def main():
    """Run all backend test suites"""
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}RESERVIA BACKEND TEST SUITE{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    start_time = time.time()
    
    # Test suites in logical order
    test_suites = [
        ('test_session_management', 'Session Management Tests'),
        ('test_user_management', 'User Management Tests'),
        ('test_resource_management', 'Resource Management Tests'),
        ('test_reservation_system', 'Reservation System Tests'),
        ('test_expiration_system', 'Expiration System Tests'),
        ('test_integration_script', 'Integration Script Tests'),
    ]
    
    results = []
    
    for module_name, description in test_suites:
        success = run_test_module(module_name, description)
        results.append((description, success))
        
        if not success:
            print(f"\n{YELLOW}Continuing with remaining test suites...{RESET}")
    
    # Summary report
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TEST EXECUTION SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = f"{GREEN}PASSED{RESET}" if success else f"{RED}FAILED{RESET}"
        print(f"  {description:<40} {status}")
    
    print(f"\n{BLUE}Results: {passed}/{total} test suites passed{RESET}")
    print(f"{BLUE}Duration: {duration:.2f} seconds{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 ALL TEST SUITES PASSED! 🎉{RESET}")
        return 0
    else:
        print(f"\n{RED}❌ {total - passed} TEST SUITE(S) FAILED{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())