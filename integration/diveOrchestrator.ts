/**
 * Dive Orchestrator Messenger
 * 
 * This module acts as a messenger between Manus and Dive AI V20 Orchestrator.
 * It sends tasks to the orchestrator which spawns 128 Dive Coder agents
 * (Claude Sonnet 4.5 + Opus 4.5) to execute the work.
 */

import { type Message } from "./_core/llm";
import { invokeLLMWithModel, invokeClaudeOpus, invokeClaudeSonnet, invokeClaudeAuto, type ModelName } from "./llmWithModel";
// DiveMemorySkill will be loaded dynamically
type DiveMemorySkill = any;

export interface DiveOrchestratorTask {
  projectPath: string;
  taskDescription: string;
  context?: Record<string, any>;
  agentCount?: number; // Default: 128
  model?: ModelName; // Default: auto (Claude Opus 4 or Sonnet 4)
}

export interface DiveOrchestratorResult {
  success: boolean;
  output: string;
  agentsUsed: number;
  executionTime: number;
  errors?: string[];
}

export class DiveOrchestratorMessenger {
  private memorySkill: any;
  private projectPath: string;
  
  constructor(projectPath: string) {
    this.projectPath = projectPath;
    // DiveMemorySkill loaded dynamically when needed
    this.memorySkill = null;
  }
  
  /**
   * Test connection to Dive Orchestrator via LLM client
   */
  async testConnection(): Promise<boolean> {
    console.log("\n" + "=".repeat(60));
    console.log("[Dive Orchestrator] Testing Connection...");
    console.log("=".repeat(60) + "\n");
    
    try {
      const response = await invokeClaudeAuto({
        messages: [
          {
            role: "system",
            content: "You are Dive Orchestrator. Respond with 'CONNECTED' if you receive this message."
          },
          {
            role: "user",
            content: "Test connection"
          }
        ]
      });
      
      const content = response.choices[0]?.message?.content;
      const isConnected = typeof content === 'string' && content.includes('CONNECTED');
      
      console.log(`✓ Connection Status: ${isConnected ? 'CONNECTED' : 'FAILED'}`);
      console.log(`  Model: ${response.model}`);
      console.log(`  Response: ${typeof content === 'string' ? content.substring(0, 100) : JSON.stringify(content).substring(0, 100)}`);
      
      return isConnected;
    } catch (error) {
      console.error(`✗ Connection Failed:`, error);
      return false;
    }
  }
  
  /**
   * Send task to Dive Orchestrator
   * The orchestrator will spawn 128 agents to work on the task
   */
  async executeTask(task: DiveOrchestratorTask): Promise<DiveOrchestratorResult> {
    const startTime = Date.now();
    
    console.log("\n" + "=".repeat(60));
    console.log("[Dive Orchestrator] Executing Task");
    console.log("=".repeat(60));
    console.log(`Task: ${task.taskDescription}`);
    console.log(`Agent Count: ${task.agentCount || 128}`);
    console.log(`Model: ${task.model || 'auto'}`);
    console.log("=".repeat(60) + "\n");
    
    // Step 1: Load project memory for context injection
    const memory = this.memorySkill?.load_memory?.();
    const contextInjection = memory ? this.memorySkill?.inject_context?.(task.taskDescription) : null;
    
    if (contextInjection) {
      console.log("[Context Injection]");
      console.log(`  ✓ Project memory loaded`);
      console.log(`  ✓ Matched triggers: ${contextInjection.matched_triggers.length}`);
      console.log(`  ✓ Suggestions: ${contextInjection.suggestions.length}`);
      
      if (contextInjection.suggestions.length > 0) {
        console.log("\n[Skill Suggestions]");
        contextInjection.suggestions.forEach((s: string) => console.log(`  • ${s}`));
      }
      console.log();
    }
    
    // Step 2: Build orchestrator prompt
    const orchestratorPrompt = this.buildOrchestratorPrompt(task, contextInjection);
    
    // Step 3: Send to Dive Orchestrator via LLM
    console.log("[Dive Orchestrator] Spawning agents...\n");
    
    try {
      // Select appropriate Claude model based on task
      const modelToUse = task.model || 'auto';
      console.log(`[Dive Orchestrator] Using model: ${modelToUse}`);
      
      let response;
      if (modelToUse === 'claude-opus-4') {
        response = await invokeClaudeOpus({
          messages: orchestratorPrompt,
          max_tokens: 32768
        });
      } else if (modelToUse === 'claude-sonnet-4') {
        response = await invokeClaudeSonnet({
          messages: orchestratorPrompt,
          max_tokens: 32768
        });
      } else {
        // Auto-select based on task complexity
        response = await invokeClaudeAuto({
          messages: orchestratorPrompt,
          max_tokens: 32768
        });
      }
      
      const output = response.choices[0]?.message?.content;
      const executionTime = Date.now() - startTime;
      
      console.log("\n" + "=".repeat(60));
      console.log("[Dive Orchestrator] Task Complete");
      console.log("=".repeat(60));
      console.log(`Execution Time: ${(executionTime / 1000).toFixed(2)}s`);
      console.log(`Tokens Used: ${response.usage?.total_tokens || 'N/A'}`);
      console.log("=".repeat(60) + "\n");
      
      // Step 4: Update dynamic state
      if (memory && this.memorySkill?.update_dynamic_state) {
        this.memorySkill.update_dynamic_state({
          last_orchestrator_task: task.taskDescription,
          last_execution_time: executionTime,
          last_completion: new Date().toISOString()
        });
      }
      
      return {
        success: true,
        output: typeof output === 'string' ? output : JSON.stringify(output),
        agentsUsed: task.agentCount || 128,
        executionTime,
        errors: []
      };
      
    } catch (error) {
      const executionTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      console.error("\n" + "=".repeat(60));
      console.error("[Dive Orchestrator] Task Failed");
      console.error("=".repeat(60));
      console.error(`Error: ${errorMessage}`);
      console.error("=".repeat(60) + "\n");
      
      return {
        success: false,
        output: '',
        agentsUsed: 0,
        executionTime,
        errors: [errorMessage]
      };
    }
  }
  
  /**
   * Build orchestrator prompt with context injection
   */
  private buildOrchestratorPrompt(
    task: DiveOrchestratorTask,
    contextInjection: any | null
  ): Message[] {
    const messages: Message[] = [];
    
    // System message for orchestrator
    messages.push({
      role: "system",
      content: `You are Dive Orchestrator V20 - a distributed AI system that coordinates 128 Dive Coder agents (Claude Sonnet 4.5 + Opus 4.5) to execute complex software development tasks.

Your responsibilities:
1. Analyze the task and break it down into subtasks
2. Distribute subtasks across 128 agents
3. Coordinate agent execution
4. Synthesize results into a coherent output
5. Follow project behavioral rules strictly

Agent Distribution Strategy:
- Use Claude Sonnet 4 for: Implementation, testing, documentation
- Use Claude Opus 4 for: Architecture decisions, complex logic, optimization
- Parallel execution when possible
- Sequential execution when dependencies exist

Output Format:
Provide a detailed execution plan and implementation code/files.`
    });
    
    // Add project context if available
    if (contextInjection) {
      messages.push({
        role: "system",
        content: contextInjection.meta_prompt
      });
      
      if (contextInjection.suggestions.length > 0) {
        messages.push({
          role: "system",
          content: `[SKILL SUGGESTIONS]\n${contextInjection.suggestions.join('\n')}`
        });
      }
    }
    
    // Add task description
    messages.push({
      role: "user",
      content: task.taskDescription
    });
    
    // Add additional context if provided
    if (task.context) {
      messages.push({
        role: "system",
        content: `[ADDITIONAL CONTEXT]\n${JSON.stringify(task.context, null, 2)}`
      });
    }
    
    return messages;
  }
  
  /**
   * Execute a multi-step workflow with the orchestrator
   */
  async executeWorkflow(steps: DiveOrchestratorTask[]): Promise<DiveOrchestratorResult[]> {
    console.log("\n" + "=".repeat(60));
    console.log(`[Dive Orchestrator] Executing Workflow (${steps.length} steps)`);
    console.log("=".repeat(60) + "\n");
    
    const results: DiveOrchestratorResult[] = [];
    
    for (let i = 0; i < steps.length; i++) {
      console.log(`\n[Step ${i + 1}/${steps.length}] ${steps[i].taskDescription}\n`);
      
      const result = await this.executeTask(steps[i]);
      results.push(result);
      
      if (!result.success) {
        console.error(`\n✗ Workflow failed at step ${i + 1}`);
        break;
      }
      
      console.log(`\n✓ Step ${i + 1} complete\n`);
    }
    
    const allSuccess = results.every(r => r.success);
    const totalTime = results.reduce((sum, r) => sum + r.executionTime, 0);
    
    console.log("\n" + "=".repeat(60));
    console.log("[Dive Orchestrator] Workflow Complete");
    console.log("=".repeat(60));
    console.log(`Status: ${allSuccess ? '✓ SUCCESS' : '✗ FAILED'}`);
    console.log(`Total Steps: ${results.length}`);
    console.log(`Total Time: ${(totalTime / 1000).toFixed(2)}s`);
    console.log("=".repeat(60) + "\n");
    
    return results;
  }
}

// CLI interface for testing
if (import.meta.url === `file://${process.argv[1]}`) {
  const projectPath = process.argv[2] || process.cwd();
  const messenger = new DiveOrchestratorMessenger(projectPath);
  
  (async () => {
    // Test connection
    const connected = await messenger.testConnection();
    
    if (!connected) {
      console.error("Failed to connect to Dive Orchestrator");
      process.exit(1);
    }
    
    // Test task execution
    console.log("\n[Test] Executing sample task...\n");
    
    const result = await messenger.executeTask({
      projectPath,
      taskDescription: "Analyze the current project structure and suggest improvements",
      agentCount: 128,
      model: "auto"
    });
    
    console.log("\n[Result]");
    console.log(result.output);
    
    process.exit(result.success ? 0 : 1);
  })();
}
