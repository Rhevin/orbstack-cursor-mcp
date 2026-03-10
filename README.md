# OrbStack MCP Server (Python)

An MCP server that lets Cursor, Claude Desktop, and other AI tools manage your OrbStack Docker containers, Linux VMs, and Kubernetes clusters.

## 32 Tools Included

- **Docker Containers** — list, run, stop, start, restart, remove, logs, exec, inspect, stats
- **Docker Images** — list, pull, remove
- **Docker Compose** — up, down, ps
- **Docker System** — prune, disk usage
- **Docker Networks & Volumes** — list, create
- **OrbStack Linux VMs** — list, start, stop, create, delete, run commands, info
- **Kubernetes** — get resources, describe, logs, apply manifests

## Prerequisites

- [OrbStack](https://orbstack.dev/) installed and running
- Python 3.10+
- `docker` and `orb` commands working in your terminal

## Install

```bash
cd orbstack-mcp-python
pip install -r requirements.txt
```

Or with uv:
```bash
uv pip install -r requirements.txt
```

## Setup with Cursor

Add to `.cursor/mcp.json` in your project root (or global Cursor settings):

```json
{
  "mcpServers": {
    "orbstack": {
      "command": "python3",
      "args": ["/FULL/PATH/TO/orbstack-mcp-python/server.py"]
    }
  }
}
```

## Setup with Cursor and UV

```json
{
  "mcpServers": {
    "orbstack": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "python", "/FULL/PATH/TO/orbstack-mcp-python/server.py""]
    }
  }
}
```

## Setup with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "orbstack": {
      "command": "python3",
      "args": ["/FULL/PATH/TO/orbstack-mcp-python/server.py"]
    }
  }
}
```

## Setup with Claude Code

```bash
claude mcp add orbstack python3 /FULL/PATH/TO/orbstack-mcp-python/server.py
```

## Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python3 server.py
```

## License

MIT
