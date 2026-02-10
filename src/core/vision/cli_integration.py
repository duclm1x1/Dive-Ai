#!/usr/bin/env python3
"""
CLI Integration Layer - Tích hợp CLI commands vào Dive Coder
Cho phép thực thi bất kỳ CLI command nào
"""

import subprocess
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import shlex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CLICommand:
    """CLI Command definition"""
    name: str
    executable: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    timeout: int = 300
    shell: bool = False

class CLIIntegration:
    """CLI Integration - Tích hợp CLI commands"""
    
    def __init__(self):
        """Initialize CLI Integration"""
        self.commands: Dict[str, CLICommand] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.command_stats: Dict[str, Dict[str, int]] = {}
        logger.info("✅ CLI Integration initialized")
    
    def register_command(self, name: str, executable: str, 
                        args: List[str] = None, env: Optional[Dict] = None,
                        cwd: Optional[str] = None, timeout: int = 300,
                        shell: bool = False) -> bool:
        """Register CLI command"""
        try:
            command = CLICommand(
                name=name,
                executable=executable,
                args=args or [],
                env=env,
                cwd=cwd,
                timeout=timeout,
                shell=shell
            )
            
            self.commands[name] = command
            self.command_stats[name] = {"executions": 0, "success": 0, "failed": 0}
            
            logger.info(f"✅ Registered command: {name} ({executable})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to register command: {str(e)}")
            return False
    
    def execute(self, command_name: str, args: Optional[List[str]] = None,
               capture_output: bool = True, **kwargs) -> Dict[str, Any]:
        """Execute CLI command"""
        
        if command_name not in self.commands:
            error = f"Command '{command_name}' not found"
            logger.error(f"❌ {error}")
            return {"status": "error", "error": error}
        
        cmd_def = self.commands[command_name]
        
        # Build command
        cmd_args = cmd_def.args.copy()
        if args:
            cmd_args.extend(args)
        
        full_command = [cmd_def.executable] + cmd_args
        
        logger.info(f"📤 Executing: {' '.join(full_command)}")
        
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run(
                full_command,
                capture_output=capture_output,
                text=True,
                timeout=cmd_def.timeout,
                env=cmd_def.env,
                cwd=cmd_def.cwd,
                shell=cmd_def.shell,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            
            output = {
                "status": "success" if result.returncode == 0 else "failed",
                "command": command_name,
                "full_command": " ".join(full_command),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time
            }
            
            # Record execution
            self._record_execution(command_name, output)
            
            if result.returncode == 0:
                logger.info(f"✅ Command executed successfully ({execution_time:.2f}s)")
            else:
                logger.warning(f"⚠️  Command failed with return code {result.returncode}")
            
            return output
        
        except subprocess.TimeoutExpired:
            error = f"Command timed out after {cmd_def.timeout}s"
            logger.error(f"❌ {error}")
            self._record_execution(command_name, {"status": "timeout", "error": error})
            return {"status": "error", "error": error}
        
        except Exception as e:
            logger.error(f"❌ Execution failed: {str(e)}")
            self._record_execution(command_name, {"status": "error", "error": str(e)})
            return {"status": "error", "error": str(e)}
    
    def execute_pipeline(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a pipeline of commands"""
        logger.info(f"\n📋 Executing pipeline of {len(commands)} commands...")
        
        results = []
        for i, cmd in enumerate(commands, 1):
            cmd_name = cmd.get("name")
            args = cmd.get("args", [])
            
            logger.info(f"\n[{i}/{len(commands)}] Executing {cmd_name}...")
            
            result = self.execute(cmd_name, args)
            results.append(result)
            
            # Stop if command fails
            if result.get("status") != "success":
                logger.warning(f"⚠️  Pipeline stopped at command {i}")
                break
        
        return results
    
    def _record_execution(self, command_name: str, result: Dict[str, Any]):
        """Record command execution"""
        execution_record = {
            "command": command_name,
            "timestamp": datetime.now().isoformat(),
            "status": result.get("status"),
            "returncode": result.get("returncode", -1),
            "execution_time": result.get("execution_time", 0)
        }
        
        self.execution_history.append(execution_record)
        
        if command_name in self.command_stats:
            self.command_stats[command_name]["executions"] += 1
            if result.get("status") == "success":
                self.command_stats[command_name]["success"] += 1
            else:
                self.command_stats[command_name]["failed"] += 1
    
    def get_command_list(self) -> List[Dict[str, Any]]:
        """Get list of registered commands"""
        return [
            {
                "name": cmd.name,
                "executable": cmd.executable,
                "args": cmd.args,
                "timeout": cmd.timeout,
                "stats": self.command_stats.get(cmd.name, {})
            }
            for cmd in self.commands.values()
        ]
    
    def get_cli_stats(self) -> Dict[str, Any]:
        """Get CLI statistics"""
        total_executions = sum(stats["executions"] for stats in self.command_stats.values())
        total_success = sum(stats["success"] for stats in self.command_stats.values())
        total_failed = sum(stats["failed"] for stats in self.command_stats.values())
        
        return {
            "total_commands": len(self.commands),
            "total_executions": total_executions,
            "total_success": total_success,
            "total_failed": total_failed,
            "success_rate": f"{(total_success / total_executions * 100):.1f}%" if total_executions > 0 else "N/A",
            "command_stats": self.command_stats,
            "recent_executions": self.execution_history[-10:]  # Last 10 executions
        }
    
    def print_cli_info(self):
        """Print CLI information"""
        print("\n" + "="*80)
        print("CLI INTEGRATION - INFORMATION")
        print("="*80)
        
        print("\n📋 Registered Commands:")
        for cmd in self.get_command_list():
            print(f"  • {cmd['name']} ({cmd['executable']})")
            print(f"    Args: {cmd['args']}")
            print(f"    Stats: Executions={cmd['stats'].get('executions', 0)}, Success={cmd['stats'].get('success', 0)}, Failed={cmd['stats'].get('failed', 0)}")
        
        stats = self.get_cli_stats()
        print(f"\n📊 CLI Statistics:")
        print(f"  Total Commands: {stats['total_commands']}")
        print(f"  Total Executions: {stats['total_executions']}")
        print(f"  Success Rate: {stats['success_rate']}")
        print("="*80)

class CLICommandBuilder:
    """Helper to build CLI commands"""
    
    @staticmethod
    def build_git_command(operation: str, *args) -> str:
        """Build git command"""
        return f"git {operation} {' '.join(args)}"
    
    @staticmethod
    def build_docker_command(operation: str, *args) -> str:
        """Build docker command"""
        return f"docker {operation} {' '.join(args)}"
    
    @staticmethod
    def build_python_command(script: str, *args) -> str:
        """Build python command"""
        return f"python3 {script} {' '.join(args)}"
    
    @staticmethod
    def build_shell_command(command: str) -> str:
        """Build shell command"""
        return command

def main():
    """Test CLI Integration"""
    
    cli = CLIIntegration()
    
    # Register commands
    cli.register_command("echo", "echo", ["Hello from CLI"])
    cli.register_command("pwd", "pwd", [])
    cli.register_command("ls", "ls", ["-la"])
    
    print("\n🔄 Testing CLI Integration...\n")
    
    # Execute commands
    result1 = cli.execute("echo")
    print(f"Echo: {result1['stdout'].strip()}")
    
    result2 = cli.execute("pwd")
    print(f"PWD: {result2['stdout'].strip()}")
    
    result3 = cli.execute("ls")
    print(f"LS output:\n{result3['stdout'][:200]}...")
    
    # Print CLI info
    cli.print_cli_info()

if __name__ == "__main__":
    main()
