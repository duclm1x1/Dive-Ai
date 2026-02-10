"""Database Skill -- SQLite queries, schema, import/export."""
import sqlite3, json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class DatabaseSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="database", description="Database: SQLite queries, schema, insert, export",
            category=SkillCategory.DATA, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "db": {"type": "string"},
                          "query": {"type": "string"}, "table": {"type": "string"}, "data": {"type": "list"}},
            output_schema={"rows": "list", "columns": "list", "affected": "integer"},
            tags=["database", "sql", "sqlite", "query", "table", "schema", "db"],
            trigger_patterns=[r"database\s+", r"sql\s+", r"query\s+", r"db\s+"],
            combo_compatible=["file-manager", "data-analyzer", "slack-bot"],
            combo_position="any")

    def _db_path(self, db=None):
        if db: return db
        d = os.path.expanduser("~/.dive-ai/databases")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "default.db")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "query")
        db = self._db_path(inputs.get("db"))
        try:
            if action == "query":
                q = inputs.get("query", "")
                if not q: return AlgorithmResult("failure", None, {"error": "query required"})
                conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row
                cur = conn.cursor(); cur.execute(q)
                if q.strip().upper().startswith(("SELECT", "PRAGMA", "EXPLAIN")):
                    rows = [dict(r) for r in cur.fetchall()[:500]]
                    cols = [d[0] for d in cur.description] if cur.description else []
                    conn.close()
                    return AlgorithmResult("success", {"rows": rows, "columns": cols, "count": len(rows)}, {"skill": "database"})
                conn.commit(); affected = cur.rowcount; conn.close()
                return AlgorithmResult("success", {"affected": affected}, {"skill": "database"})

            elif action == "tables":
                conn = sqlite3.connect(db); cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tables = [r[0] for r in cur.fetchall()]; conn.close()
                return AlgorithmResult("success", {"tables": tables, "count": len(tables), "db": db}, {"skill": "database"})

            elif action == "schema":
                table = inputs.get("table", "")
                conn = sqlite3.connect(db); cur = conn.cursor()
                if table:
                    cur.execute(f"PRAGMA table_info({table})")
                    cols = [{"name": r[1], "type": r[2], "pk": bool(r[5])} for r in cur.fetchall()]
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]; conn.close()
                    return AlgorithmResult("success", {"table": table, "columns": cols, "row_count": count}, {"skill": "database"})
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cur.fetchall()]; result = {}
                for t in tables:
                    cur.execute(f"PRAGMA table_info({t})")
                    result[t] = [{"name": r[1], "type": r[2]} for r in cur.fetchall()]
                conn.close()
                return AlgorithmResult("success", {"schemas": result}, {"skill": "database"})

            elif action == "create":
                table = inputs.get("table", ""); columns = inputs.get("columns", {})
                if not table or not columns: return AlgorithmResult("failure", None, {"error": "table and columns required"})
                col_defs = ", ".join([f"{k} {v}" for k, v in columns.items()])
                conn = sqlite3.connect(db); conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})")
                conn.commit(); conn.close()
                return AlgorithmResult("success", {"created": table, "columns": list(columns.keys())}, {"skill": "database"})

            elif action == "insert":
                table = inputs.get("table", ""); data = inputs.get("data", [])
                if not table or not data: return AlgorithmResult("failure", None, {"error": "table and data required"})
                conn = sqlite3.connect(db); cur = conn.cursor(); count = 0
                for row in data[:1000]:
                    cols = ", ".join(row.keys()); placeholders = ", ".join(["?" for _ in row])
                    cur.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", list(row.values())); count += 1
                conn.commit(); conn.close()
                return AlgorithmResult("success", {"inserted": count, "table": table}, {"skill": "database"})

            elif action == "export":
                table = inputs.get("table", "")
                if not table: return AlgorithmResult("failure", None, {"error": "table required"})
                fp = inputs.get("file", os.path.expanduser(f"~/.dive-ai/databases/{table}_{int(time.time())}.json"))
                conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row; cur = conn.cursor()
                cur.execute(f"SELECT * FROM {table}"); rows = [dict(r) for r in cur.fetchall()]; conn.close()
                with open(fp, "w") as f: json.dump(rows, f, indent=2, default=str)
                return AlgorithmResult("success", {"exported": len(rows), "file": fp}, {"skill": "database"})

            return AlgorithmResult("failure", None, {"error": "action: query/tables/schema/create/insert/export"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
