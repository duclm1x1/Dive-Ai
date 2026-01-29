# Dive Coder v14 Skills Pack (Clawdbot plugin)

This plugin ships Dive Coder skills for Clawdbot.

## Install

```bash
# from the directory containing this plugin folder
clawdbot plugins install ./clawdbot_plugin_dive_coder_v14_4
clawdbot plugins enable dive-coder-v14

clawdbot plugins info dive-coder-v14
clawdbot skills list | grep dive-coder
```

## Config (optional)

In your Clawdbot config:

```json
{
  "plugins": {
    "entries": {
      "dive-coder-v14": {
        "enabled": true,
        "config": {
          "repoRoot": "/abs/path/to/DiveCoder_v14_4_enterprise_rag_native",
          "pythonPath": ".shared/vibe-coder-v13",
          "ragKbDir": ".vibe/kb"
        }
      }
    }
  }
}
```
