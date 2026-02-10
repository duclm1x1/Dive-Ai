# Dive AI Self-Modification - API Testing Guide

## 🧪 Test Self-Modification Endpoints

The gateway proxy now exposes self-modification capabilities via REST API!

---

## Available Endpoints

### 1. Analyze Code

```http
POST http://localhost:8765/dive/analyze
Content-Type: application/json

{
  "module_path": "desktop-app/backend/llm/connections.py"
}
```

**Response**:

```json
{
  "success": true,
  "module": "desktop-app/backend/llm/connections.py",
  "purpose": "V98 API Client for Claude models",
  "complexity": 6.5,
  "issues": [
    {"type": "performance", "line": 134, "description": "Synchronous requests", "severity": "medium"}
  ],
  "suggestions": [
    "Use async/await for HTTP requests",
    "Add connection pooling"
  ]
}
```

---

### 2. Fix Bug

```http
POST http://localhost:8765/dive/fix-bug
Content-Type: application/json

{
  "module_path": "desktop-app/backend/llm/connections.py",
  "bug_description": "Synchronous HTTP requests cause slowdowns",
  "apply_fix": false
}
```

**Response** (Preview mode):

```json
{
  "success": true,
  "module": "desktop-app/backend/llm/connections.py",  
  "bug": "Synchronous HTTP requests cause slowdowns",
  "applied": false,
  "diff": "--- a/connections.py\n+++ b/connections.py\n@@ -134,7 +134,7 @@\n-        response = requests.post(...)\n+        response = await httpx.AsyncClient().post(...)",
  "preview": "Fix generated. Set apply_fix=true to apply."
}
```

**Apply the fix**:

```json
{
  "module_path": "desktop-app/backend/llm/connections.py",
  "bug_description": "Synchronous HTTP requests cause slowdowns",
  "apply_fix": true
}
```

---

### 3. Optimize Code

```http
POST http://localhost:8765/dive/optimize
Content-Type: application/json

{
  "module_path": "desktop-app/backend/llm/v98_algorithm.py",
  "optimization_goal": "Reduce execution time by 30%",
  "apply_changes": false
}
```

---

### 4. Add Feature

```http
POST http://localhost:8765/dive/add-feature
Content-Type: application/json

{
  "module_path": "desktop-app/backend/llm/v98_algorithm.py",
  "feature_description": "Add caching for repeated requests",
  "apply_changes": false
}
```

---

## PowerShell Testing

### Test 시 Analyze:

```powershell
$body = @{
    module_path = "desktop-app/backend/llm/connections.py"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8765/dive/analyze" -Method Post -Body $body -ContentType "application/json"
```

### Test Fix Bug

```powershell
$body = @{
    module_path = "desktop-app/backend/llm/connections.py"
    bug_description = "Synchronous requests are slow"
    apply_fix = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8765/dive/fix-bug" -Method Post -Body $body -ContentType "application/json"
```

---

## UI-TARS Integration

Once you configure UI-TARS, you can use natural language:

### Via Chat

```
"Analyze the connections.py module"
→ Calls /dive/analyze

"Fix the slow request bug in connections.py"
→ Calls /dive/fix-bug

"Optimize v98_algorithm.py for speed"
→ Calls /dive/optimize

"Add caching to the algorithm system"
→ Calls /dive/add-feature
```

---

## Safety Features

1. **Preview Mode** (default):
   - `apply_fix=false`, `apply_changes=false`
   - Shows what would change (diff)
   - Doesn't modify files

2. **Apply Mode**:
   - `apply_fix=true`, `apply_changes=true`
   - Creates backup automatically
   - Tests in sandbox
   - Applies changes

3. **Protected Files**:
   - Cannot modify:
     - `Launch-UI-TARS.bat`
     - `.env`
     - `self_modification/self_modification_engine.py`

4. **Automatic Backups**:
   - Stored in `.backups/`
   - Timestamped
   - Can rollback

---

## Example Workflow

### 1. Analyze Code

```powershell
# Find issues
curl http://localhost:8765/dive/analyze -X POST -H "Content-Type: application/json" -d '{"module_path": "desktop-app/backend/llm/connections.py"}'
```

### 2. Preview Fix

```powershell
# See what the fix would look like
curl http://localhost:8765/dive/fix-bug -X POST -H "Content-Type: application/json" -d '{
  "module_path": "desktop-app/backend/llm/connections.py",
  "bug_description": "Add async support",
  "apply_fix": false
}'
```

### 3. Apply Fix

```powershell
# Apply the fix (creates backup)
curl http://localhost:8765/dive/fix-bug -X POST -H "Content-Type: application/json" -d '{
  "module_path": "desktop-app/backend/llm/connections.py",
  "bug_description": "Add async support",
  "apply_fix": true
}'
```

### 4. Check Backup

```powershell
ls "D:\Antigravity\Dive AI\.backups\"
```

---

## Ready to Test

Gateway proxy is running with self-modification enabled. Try analyzing a module first!
