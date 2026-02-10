#!/usr/bin/env python3
"""
Dive Coder v19.5 - Setup Helper
Advanced setup automation and configuration management
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import shutil

class DiveSetupHelper:
    """Helper class for Dive Coder setup automation"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.backend_dir = self.project_dir / "backend"
        self.env_file = self.project_dir / ".env"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def print_step(self, text: str):
        """Print step"""
        print(f"\n>>> {text}")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"✅ {text}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"❌ {text}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"ℹ️  {text}")
    
    def validate_project_structure(self) -> bool:
        """Validate project structure"""
        self.print_step("Validating project structure")
        
        required_files = [".env", "backend/main.py", "package.json"]
        missing_files = []
        
        for file_path in required_files:
            full_path = self.project_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                self.print_success(f"Found: {file_path}")
        
        if missing_files:
            self.print_error(f"Missing files: {', '.join(missing_files)}")
            return False
        
        return True
    
    def check_ports(self) -> Dict[int, bool]:
        """Check if ports are available"""
        self.print_step("Checking port availability")
        
        ports = {8000: "Backend API", 3000: "Frontend", 5432: "Database"}
        available = {}
        
        for port, service in ports.items():
            try:
                result = subprocess.run(
                    f"lsof -i :{port}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                is_available = result.returncode != 0
                available[port] = is_available
                
                status = "✅ Available" if is_available else "⚠️  In use"
                print(f"  Port {port} ({service}): {status}")
            except Exception as e:
                self.print_error(f"Error checking port {port}: {e}")
                available[port] = False
        
        return available
    
    def update_env_file(self, updates: Dict[str, str]) -> bool:
        """Update environment variables in .env file"""
        self.print_step("Updating environment variables")
        
        if not self.env_file.exists():
            self.print_error(f".env file not found: {self.env_file}")
            return False
        
        try:
            # Read current env
            env_vars = {}
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            
            # Update with new values
            env_vars.update(updates)
            
            # Write back
            with open(self.env_file, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            self.print_success("Environment variables updated")
            return True
        except Exception as e:
            self.print_error(f"Error updating .env file: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        self.print_step("Installing Python dependencies")
        
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            self.print_error(f"requirements.txt not found: {requirements_file}")
            return False
        
        try:
            subprocess.run(
                ["pip3", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            self.print_success("Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Error installing Python dependencies: {e}")
            return False
    
    def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        self.print_step("Installing Node.js dependencies")
        
        package_file = self.project_dir / "package.json"
        if not package_file.exists():
            self.print_info("package.json not found, skipping Node.js dependencies")
            return True
        
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(self.project_dir),
                check=True,
                capture_output=True
            )
            self.print_success("Node.js dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Error installing Node.js dependencies: {e}")
            return False
    
    def test_backend_connection(self) -> bool:
        """Test backend API connection"""
        self.print_step("Testing backend connection")
        
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8000/api/health"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get("status") == "healthy":
                        self.print_success("Backend API is healthy")
                        return True
                except json.JSONDecodeError:
                    pass
            
            self.print_error("Backend API not responding")
            return False
        except Exception as e:
            self.print_error(f"Error testing backend: {e}")
            return False
    
    def generate_setup_summary(self) -> Dict:
        """Generate setup summary"""
        self.print_step("Generating setup summary")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "project_directory": str(self.project_dir),
            "components": {
                "backend": {
                    "status": "configured" if (self.backend_dir / "main.py").exists() else "missing",
                    "location": str(self.backend_dir)
                },
                "environment": {
                    "status": "configured" if self.env_file.exists() else "missing",
                    "location": str(self.env_file)
                },
                "frontend": {
                    "status": "configured" if (self.project_dir / "package.json").exists() else "missing",
                    "location": str(self.project_dir)
                }
            },
            "services": {
                "backend_api": "http://localhost:8000",
                "frontend": "http://localhost:3000",
                "api_docs": "http://localhost:8000/docs"
            }
        }
        
        return summary
    
    def save_summary(self, summary: Dict) -> bool:
        """Save setup summary to file"""
        try:
            summary_file = self.project_dir / "SETUP_SUMMARY.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            self.print_success(f"Setup summary saved: {summary_file}")
            return True
        except Exception as e:
            self.print_error(f"Error saving summary: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Run full setup process"""
        self.print_header("DIVE CODER v19.5 - SETUP HELPER")
        
        steps = [
            ("Validating project structure", self.validate_project_structure),
            ("Checking port availability", lambda: bool(self.check_ports())),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Installing Node.js dependencies", self.install_node_dependencies),
        ]
        
        all_passed = True
        for step_name, step_func in steps:
            try:
                if not step_func():
                    self.print_error(f"Failed: {step_name}")
                    all_passed = False
                else:
                    self.print_success(f"Completed: {step_name}")
            except Exception as e:
                self.print_error(f"Error in {step_name}: {e}")
                all_passed = False
        
        # Generate summary
        summary = self.generate_setup_summary()
        self.save_summary(summary)
        
        # Print summary
        self.print_header("SETUP SUMMARY")
        print(json.dumps(summary, indent=2))
        
        return all_passed

def main():
    parser = argparse.ArgumentParser(
        description="Dive Coder v19.5 Setup Helper"
    )
    parser.add_argument(
        "project_dir",
        help="Project directory path"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate project structure"
    )
    parser.add_argument(
        "--check-ports",
        action="store_true",
        help="Check port availability"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install dependencies"
    )
    parser.add_argument(
        "--test-backend",
        action="store_true",
        help="Test backend connection"
    )
    parser.add_argument(
        "--full-setup",
        action="store_true",
        help="Run full setup process"
    )
    parser.add_argument(
        "--update-env",
        type=str,
        help="Update environment variables (JSON format)"
    )
    
    args = parser.parse_args()
    
    helper = DiveSetupHelper(args.project_dir)
    
    if args.validate:
        helper.validate_project_structure()
    elif args.check_ports:
        helper.check_ports()
    elif args.install_deps:
        helper.install_python_dependencies()
        helper.install_node_dependencies()
    elif args.test_backend:
        helper.test_backend_connection()
    elif args.update_env:
        try:
            updates = json.loads(args.update_env)
            helper.update_env_file(updates)
        except json.JSONDecodeError:
            helper.print_error("Invalid JSON format for --update-env")
    elif args.full_setup:
        success = helper.run_full_setup()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
