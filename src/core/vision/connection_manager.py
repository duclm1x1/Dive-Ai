#!/usr/bin/env python3
"""
Connection Manager - Test and Verify All Connections
Integrates and tests Universal Gateway, CLI Integration, and Transmission Optimizer
"""

import json
import logging
from datetime import datetime

# Import all components
from universal_gateway import UniversalGateway
from cli_integration import CLIIntegration
from transmission_optimizer import TransmissionOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages and tests all connection components"""
    
    def __init__(self):
        """Initialize Connection Manager"""
        self.gateway = UniversalGateway()
        self.cli = CLIIntegration()
        self.optimizer = TransmissionOptimizer()
        self.test_results = {}
        logger.info("✅ Connection Manager initialized")
    
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("\n" + "="*80)
        logger.info("RUNNING ALL CONNECTION TESTS")
        logger.info("="*80)
        
        self.test_universal_gateway()
        self.test_cli_integration()
        self.test_transmission_optimizer()
        self.test_integrated_pipeline()
        
        self.print_final_report()
    
    def test_universal_gateway(self):
        """Test Universal API Gateway"""
        logger.info("\n" + "-"*80)
        logger.info("TEST 1: UNIVERSAL API GATEWAY")
        logger.info("-"*80)
        
        self.gateway.register_api("jsonplaceholder", "rest", "https://jsonplaceholder.typicode.com")
        result = self.gateway.call("jsonplaceholder", method="GET", endpoint="/posts/1")
        
        if result.get("status") == "success" and result.get("status_code") == 200:
            logger.info("✅ API Gateway Test: PASSED")
            self.test_results["api_gateway"] = {"status": "PASSED", "details": "Successfully called REST API"}
        else:
            logger.error("❌ API Gateway Test: FAILED")
            self.test_results["api_gateway"] = {"status": "FAILED", "details": result.get("error")}
    
    def test_cli_integration(self):
        """Test CLI Integration"""
        logger.info("\n" + "-"*80)
        logger.info("TEST 2: CLI INTEGRATION")
        logger.info("-"*80)
        
        self.cli.register_command("echo_test", "echo", ["Hello from CLI Integration"])
        result = self.cli.execute("echo_test")
        
        if result.get("status") == "success" and "Hello" in result.get("stdout", ""):
            logger.info("✅ CLI Integration Test: PASSED")
            self.test_results["cli_integration"] = {"status": "PASSED", "details": "Successfully executed echo command"}
        else:
            logger.error("❌ CLI Integration Test: FAILED")
            self.test_results["cli_integration"] = {"status": "FAILED", "details": result.get("error")}
    
    def test_transmission_optimizer(self):
        """Test Transmission Optimizer"""
        logger.info("\n" + "-"*80)
        logger.info("TEST 3: TRANSMISSION OPTIMIZER")
        logger.info("-"*80)
        
        self.optimizer.enable_compression("gzip")
        self.optimizer.enable_caching()
        self.optimizer.enable_deduplication()
        
        test_data = {"key": "value", "data": "a" * 1000}
        data_str = json.dumps(test_data)
        original_size = len(data_str.encode())
        
        optimized_data = self.optimizer.optimize(test_data)
        optimized_size = len(optimized_data)
        
        if optimized_size < original_size:
            logger.info("✅ Transmission Optimizer Test: PASSED")
            self.test_results["transmission_optimizer"] = {"status": "PASSED", "details": f"Compressed data from {original_size} to {optimized_size} bytes"}
        else:
            logger.error("❌ Transmission Optimizer Test: FAILED")
            self.test_results["transmission_optimizer"] = {"status": "FAILED", "details": "Compression failed to reduce size"}
    
    def test_integrated_pipeline(self):
        """Test an integrated pipeline"""
        logger.info("\n" + "-"*80)
        logger.info("TEST 4: INTEGRATED PIPELINE")
        logger.info("-"*80)
        
        try:
            # 1. Fetch data from API
            logger.info("[Pipeline 1/3] Fetching data from API...")
            api_result = self.gateway.call("jsonplaceholder", method="GET", endpoint="/users")
            if api_result.get("status") != "success":
                raise Exception("API call failed")
            
            # 2. Process data with CLI (simulate by echoing the number of users)
            logger.info("[Pipeline 2/3] Processing data with CLI...")
            num_users = len(api_result["data"])
            self.cli.register_command("process_data", "echo", [f"Processed {num_users} users."])
            cli_result = self.cli.execute("process_data")
            if cli_result.get("status") != "success":
                raise Exception("CLI execution failed")
            
            # 3. Optimize the result for transmission
            logger.info("[Pipeline 3/3] Optimizing result...")
            final_output = {"api_data": api_result["data"], "cli_output": cli_result["stdout"]}
            optimized_output = self.optimizer.optimize(final_output)
            
            logger.info("✅ Integrated Pipeline Test: PASSED")
            self.test_results["integrated_pipeline"] = {"status": "PASSED", "details": "Successfully executed API -> CLI -> Optimizer pipeline"}
        
        except Exception as e:
            logger.error(f"❌ Integrated Pipeline Test: FAILED - {str(e)}")
            self.test_results["integrated_pipeline"] = {"status": "FAILED", "details": str(e)}
    
    def print_final_report(self):
        """Print the final test report"""
        print("\n" + "="*80)
        print("BASE SKILL CONNECTION - FINAL TEST REPORT")
        print("="*80)
        
        all_passed = True
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result["details"]
            icon = "✅" if status == "PASSED" else "❌"
            print(f"{icon} {test_name.replace('_', ' ').title()}: {status}")
            print(f"   -> {details}")
            if status != "PASSED":
                all_passed = False
        
        print("-"*80)
        if all_passed:
            print("\n🎉 SUCCESS: All components of the Base Skill Connection are working correctly!")
        else:
            print("\n🔥 FAILURE: Some components failed the integration test.")
        print("="*80)

if __name__ == "__main__":
    manager = ConnectionManager()
    manager.run_all_tests()
