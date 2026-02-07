"""
Dive AI CLI - Orchestrator 512 Agents Commands
Commands for managing and executing tasks across 512 Dive Agents
"""

import click
import json
import sys
import asyncio

# Import orchestrator
try:
    from ...core.orchestrator.orchestrator_512_agents import Orchestrator512Agents
except ImportError:
    Orchestrator512Agents = None


@click.group()
def orchestrator():
    """Orchestrator 512 Agents operations"""
    pass


@orchestrator.command()
def status():
    """Get orchestrator status"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        status = orchestrator.get_orchestrator_status()
        
        click.echo(json.dumps(status, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@orchestrator.command()
@click.argument('num_tasks', type=int)
@click.option('--parallel', type=int, default=512, help='Max parallel tasks')
def execute_tasks(num_tasks, parallel):
    """Execute N tasks in parallel across agents"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        
        # Create dummy tasks
        tasks = [{"id": i, "type": "code_generation"} for i in range(num_tasks)]
        
        click.echo(f"Executing {num_tasks} tasks with {parallel} parallel agents...")
        
        # Execute
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(orchestrator.execute_parallel_tasks(tasks))
        
        click.echo(json.dumps(result, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@orchestrator.command()
@click.argument('cluster_id')
def cluster_status(cluster_id):
    """Get status of specific cluster"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        
        if cluster_id not in orchestrator.clusters:
            click.echo(f"Error: Cluster '{cluster_id}' not found", err=True)
            sys.exit(1)
        
        cluster = orchestrator.clusters[cluster_id]
        status = cluster.get_status()
        
        click.echo(json.dumps(status, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@orchestrator.command()
@click.argument('agent_id')
def agent_info(agent_id):
    """Get info about specific agent"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        agent_info = orchestrator.get_agent_details(agent_id)
        
        if not agent_info:
            click.echo(f"Error: Agent '{agent_id}' not found", err=True)
            sys.exit(1)
        
        click.echo(json.dumps(agent_info, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@orchestrator.command()
def list_agents():
    """List all agents"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        agents = orchestrator.get_all_agents()
        
        agent_list = [agent.to_dict() for agent in agents]
        
        result = {
            "total_agents": len(agent_list),
            "agents": agent_list[:10]  # Show first 10
        }
        
        click.echo(json.dumps(result, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@orchestrator.command()
@click.argument('target_count', type=int)
def scale(target_count):
    """Scale agent count"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        result = orchestrator.scale_agents(target_count)
        
        click.echo(json.dumps(result, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@orchestrator.command()
def idle_agents():
    """Get count of idle agents"""
    if not Orchestrator512Agents:
        click.echo("Error: Orchestrator not available", err=True)
        sys.exit(1)
    
    try:
        orchestrator = Orchestrator512Agents()
        idle = orchestrator.get_idle_agents()
        
        result = {
            "idle_agents": len(idle),
            "total_agents": orchestrator.total_agents,
            "utilization": (orchestrator.total_agents - len(idle)) / orchestrator.total_agents * 100
        }
        
        click.echo(json.dumps(result, indent=2))
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    orchestrator()
