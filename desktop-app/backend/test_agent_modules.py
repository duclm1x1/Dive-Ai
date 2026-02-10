"""Quick test: verify all new modules import and work correctly."""
import sys
sys.path.insert(0, '.')

# Test 1: pc_operator
from pc_operator import pc_operator
print(f"[OK] pc_operator imported, allowed={pc_operator.allowed}")
pc_operator.set_allowed(True)
assert pc_operator.allowed == True
pc_operator.set_allowed(False)
print("[OK] pc_operator.set_allowed works")

# Test 2: action_executor
from action_executor import ActionExecutor
ae = ActionExecutor(pc_operator=pc_operator, app_path='.')

# Test parsing
assert ae.has_actions("<execute_command>dir</execute_command>") == True
assert ae.has_actions("hello world") == False
assert ae.has_actions('<click x="100" y="200"/>') == True
assert ae.has_actions('<screenshot/>') == True
assert ae.has_actions('<read_file>test.py</read_file>') == True
print("[OK] ActionExecutor.has_actions works")

# Test executing a command
results = ae.parse_and_execute("<execute_command>echo hello</execute_command>", automation_allowed=False)
assert len(results) == 1
assert results[0].action == "execute_command"
assert results[0].success == True
assert "hello" in results[0].output
print(f"[OK] execute_command result: {results[0].output.strip()}")

# Test PC control blocked when not allowed
results = ae.parse_and_execute('<click x="100" y="200"/>', automation_allowed=False)
assert results[0].success == False
assert "disabled" in results[0].error.lower() or "PC control" in results[0].error
print(f"[OK] PC control blocked when disabled: {results[0].error}")

# Test self_debug action
results = ae.parse_and_execute('<self_debug target="gateway_server.py" issue="test"/>', automation_allowed=False)
assert results[0].success == True
print(f"[OK] self_debug read gateway_server.py ({len(results[0].output)} chars)")

# Test format results
formatted = ae.format_results_for_display(results)
assert "Actions Executed" in formatted
print("[OK] format_results_for_display works")

# Test 3: agent_loop
from agent_loop import AgentLoop, AgentStatus
al = AgentLoop(pc_operator=pc_operator, action_executor=ae, llm_chat_fn=None)
assert al.status == AgentStatus.IDLE
al.stop()
assert al.status == AgentStatus.STOPPED
status = al.get_status()
assert status["status"] == "stopped"
print("[OK] AgentLoop status management works")

print("\n" + "="*50)
print("ALL TESTS PASSED! Ready to restart gateway.")
print("="*50)
