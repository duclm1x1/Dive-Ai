"""
Dive AI — CLI Interface
Standalone command-line interface for Dive AI operations.
"""
import sys, os, json, argparse, time
from typing import Optional

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def get_algo_service():
    from dive_core.algorithm_service import AlgorithmService
    return AlgorithmService()


def get_memory():
    from dive_core.memory.dive_memory import DiveMemory
    return DiveMemory()


def get_hub():
    from dive_core.marketplace.divehub import DiveHub
    return DiveHub()


def get_security():
    from dive_core.security.security_layer import SecurityLayer
    return SecurityLayer()


def cmd_chat(args):
    """Interactive chat mode."""
    print("🤿 Dive AI Chat — type 'exit' to quit")
    print("=" * 50)
    mem = get_memory()
    ctx = mem.build_system_context()
    print(f"📋 Loaded identity ({len(ctx)} chars)")
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("exit", "quit", "q"):
            break
        if not user_input:
            continue
        # Log activity
        mem.log_daily(f"Chat: {user_input[:80]}", "chat")
        print(f"🤿 Dive AI: I received your message. (Full LLM integration requires server mode)")
        print(f"   Use 'dive-cli serve' to start the full gateway server.")


def cmd_skill(args):
    """Skill management commands."""
    svc = get_algo_service()
    action = args.action

    if action == "list":
        stats = svc.get_stats()
        print(f"📦 Skills: {stats['skills_loaded']} loaded")
        skills = svc.list_skills()
        for s in skills:
            print(f"  • {s['name']} [{s.get('category', 'custom')}]")

    elif action == "execute":
        name = args.name
        inputs_str = args.inputs or "{}"
        try: inputs = json.loads(inputs_str)
        except: inputs = {"action": inputs_str}
        result = svc.execute(name, inputs)
        print(json.dumps(result, indent=2, default=str))

    elif action == "search":
        query = args.name
        results = svc.search(query)
        for r in results:
            print(f"  • {r.get('name', r.get('deployed_name', '?'))} — {r.get('description', '')[:60]}")

    elif action == "info":
        name = args.name
        info = svc.get_info(name)
        print(json.dumps(info, indent=2, default=str))


def cmd_algo(args):
    """Algorithm management commands."""
    svc = get_algo_service()
    action = args.action

    if action == "create":
        result = svc.create_algorithm(
            name=args.name,
            description=args.description or f"Auto algorithm: {args.name}",
            logic_type=args.logic_type or "transform"
        )
        print(json.dumps(result, indent=2, default=str))

    elif action == "list":
        stats = svc.get_stats()
        print(f"🧬 Algorithms: {stats['auto_algorithms_created']} created, "
              f"{stats['auto_algorithms_deployed']} deployed")
        for name, info in svc._deployed.items():
            print(f"  • {name}")

    elif action == "stats":
        print(json.dumps(svc.get_stats(), indent=2, default=str))


def cmd_hub(args):
    """DiveHub marketplace commands."""
    hub = get_hub()
    action = args.action

    if action == "list":
        skills = hub.list_published()
        print(f"📦 DiveHub: {len(skills)} published skills")
        for s in skills:
            print(f"  • {s['name']}@{s.get('version', '?')} — {s.get('description', '')[:50]}")

    elif action == "search":
        results = hub.search(args.query or "")
        for r in results:
            print(f"  • {r['name']} [{r.get('category', 'custom')}] — {r.get('description', '')[:50]}")

    elif action == "install":
        result = hub.install(args.name)
        print(json.dumps(result, indent=2, default=str))

    elif action == "publish":
        result = hub.publish(args.path, {"name": args.name, "description": args.description or ""})
        print(json.dumps(result, indent=2, default=str))

    elif action == "stats":
        print(json.dumps(hub.get_stats(), indent=2, default=str))


def cmd_memory(args):
    """Memory management commands."""
    mem = get_memory()
    action = args.action

    if action == "status":
        print(json.dumps(mem.get_status(), indent=2, default=str))

    elif action == "read":
        content = mem.read(args.key)
        print(content)

    elif action == "search":
        results = mem.search(args.query)
        for r in results:
            print(f"  [{r['source']}] {r['doc_id']}: {r['snippet'][:80]}")

    elif action == "daily":
        content = mem.read_daily()
        print(content or "(No entries today)")

    elif action == "logs":
        logs = mem.list_daily_logs()
        for l in logs:
            print(f"  📅 {l}")


def cmd_security(args):
    """Security commands."""
    sec = get_security()
    action = args.action

    if action == "scan":
        if os.path.isdir(args.path):
            result = sec.scan_directory(args.path)
        else:
            result = sec.scan_skill(args.path)
        print(json.dumps(result, indent=2, default=str))

    elif action == "check":
        result = sec.check_injection(args.text)
        print(json.dumps(result, indent=2, default=str))

    elif action == "audit":
        entries = sec.get_audit_log()
        for e in entries:
            print(f"  [{e['timestamp'][:19]}] {e['event']}: {json.dumps(e.get('details', {}))[:60]}")

    elif action == "stats":
        print(json.dumps(sec.get_stats(), indent=2, default=str))


def cmd_status(args):
    """System status."""
    print("🤿 Dive AI System Status")
    print("=" * 50)
    try:
        svc = get_algo_service()
        stats = svc.get_stats()
        print(f"  Skills: {stats['skills_loaded']} loaded")
        print(f"  Algorithms: {stats['auto_algorithms_created']} created, {stats['auto_algorithms_deployed']} deployed")
    except Exception as e:
        print(f"  AlgorithmService: {e}")

    try:
        mem = get_memory()
        status = mem.get_status()
        print(f"  Memory files: {len(status['identity_files'])}")
        print(f"  Daily logs: {status['daily_logs_count']}")
    except Exception as e:
        print(f"  Memory: {e}")

    try:
        hub = get_hub()
        stats = hub.get_stats()
        print(f"  DiveHub: {stats['total_published']} published, {stats['total_installed']} installed")
    except Exception as e:
        print(f"  DiveHub: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="dive-cli",
        description="🤿 Dive AI Command Line Interface",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # chat
    subparsers.add_parser("chat", help="Interactive chat mode")

    # skill
    sp_skill = subparsers.add_parser("skill", help="Skill management")
    sp_skill.add_argument("action", choices=["list", "execute", "search", "info"])
    sp_skill.add_argument("--name", "-n", default="")
    sp_skill.add_argument("--inputs", "-i", default="{}")

    # algo
    sp_algo = subparsers.add_parser("algo", help="Algorithm management")
    sp_algo.add_argument("action", choices=["create", "list", "stats"])
    sp_algo.add_argument("--name", "-n", default="")
    sp_algo.add_argument("--description", "-d", default="")
    sp_algo.add_argument("--logic-type", "-l", default="transform")

    # hub
    sp_hub = subparsers.add_parser("hub", help="DiveHub marketplace")
    sp_hub.add_argument("action", choices=["list", "search", "install", "publish", "stats"])
    sp_hub.add_argument("--name", "-n", default="")
    sp_hub.add_argument("--query", "-q", default="")
    sp_hub.add_argument("--path", "-p", default="")
    sp_hub.add_argument("--description", "-d", default="")

    # memory
    sp_mem = subparsers.add_parser("memory", help="Memory management")
    sp_mem.add_argument("action", choices=["status", "read", "search", "daily", "logs"])
    sp_mem.add_argument("--key", "-k", default="user")
    sp_mem.add_argument("--query", "-q", default="")

    # security
    sp_sec = subparsers.add_parser("security", help="Security tools")
    sp_sec.add_argument("action", choices=["scan", "check", "audit", "stats"])
    sp_sec.add_argument("--path", "-p", default=".")
    sp_sec.add_argument("--text", "-t", default="")

    # status
    subparsers.add_parser("status", help="System status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "chat": cmd_chat, "skill": cmd_skill, "algo": cmd_algo,
        "hub": cmd_hub, "memory": cmd_memory, "security": cmd_security,
        "status": cmd_status,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
