# Advanced Claude Proxy 🛡️

A highly secure, deeply context-aware local proxy for Claude Code and other local LLMs. Built with Constitutional AI principles and an advanced developer-centric UX inspired by Cursor.

## Why this is better than standard local proxies?

### 1. Bulletproof Security (Anthropic Philosophy)
- **Sandboxed Execution:** The agent runs inside an isolated Docker container, protecting your host machine from dangerous commands.
- **Constitutional Guardian:** A built-in filter prevents the execution of malicious commands (`rm -rf /`, fork bombs, etc.) before they even reach the sandbox.
- **Secret Vault:** API keys are not stored in plaintext `.env` files. Instead, they are securely managed by your OS's encrypted keyring.
- **Authenticated Proxy:** The local FastAPI server requires JWT authentication, preventing SSRF attacks or malicious local software from hijacking your proxy.

### 2. Deep Context (Cursor Philosophy)
- **Vector Memory (RAG):** Integrates LanceDB to automatically index your codebase. The agent can instantly recall relevant files without needing explicit prompts.
- **Multi-Agent Architecture:** Routes simple tasks to fast models (like Llama 3) and complex logic to heavy models (like DeepSeek V3 or Claude 3.5 Sonnet).

### 3. Human-in-the-Loop Dashboard
- Includes a built-in web dashboard (served by FastAPI) to view the agent's "thoughts" in real-time.
- Approve or reject terminal commands visually with a single click.

## Installation & Setup

1. Make sure you have `docker` running.
2. Ensure you have `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
3. Clone this repository and sync dependencies:
```bash
uv sync
```
4. Build the sandbox image:
```bash
docker build -t advanced-claude-sandbox:latest -f Dockerfile.sandbox .
```

## Running the Proxy

```bash
uv run advanced-claude-proxy
```

Then open your browser at `http://127.0.0.1:8082` to view the Dashboard.
