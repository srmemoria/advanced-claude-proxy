from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from src.proxy.budget import budget_manager

router = APIRouter(tags=["Dashboard"])

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    stats = budget_manager.get_stats()
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced Claude Proxy - Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #38bdf8; }}
            .card {{ background: #1e293b; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #334155; }}
            .btn {{ background: #0ea5e9; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }}
            .btn:hover {{ background: #0284c7; }}
            .btn-danger {{ background: #ef4444; }}
            .btn-danger:hover {{ background: #dc2626; }}
            .log-box {{ background: #000; padding: 1rem; border-radius: 4px; font-family: monospace; height: 300px; overflow-y: auto; color: #10b981;}}
            .budget-meter {{ background: #000; padding: 1rem; border-radius: 4px; font-family: monospace; display: flex; justify-content: space-between; }}
            .status-safe {{ color: #10b981; font-weight: bold; }}
            .status-blocked {{ color: #ef4444; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Advanced Claude Proxy</h1>
            <p>Constitutional AI & Sandboxed Execution Dashboard</p>

            <div class="card">
                <h2>💰 Budget & Token Costs</h2>
                <div class="budget-meter">
                    <span>Spent: <strong>${stats['spent']}</strong> / ${stats['limit']}</span>
                    <span>Remaining: <strong>${stats['remaining']}</strong></span>
                    <span class="status-{'safe' if stats['status'] == 'Safe' else 'blocked'}">Status: {stats['status']}</span>
                </div>
                <p style="font-size: 0.85em; color: #94a3b8;">Protects your wallet. Using local Ollama/LM Studio costs $0.00.</p>
            </div>
            
            <div class="card">
                <h2>Pending Commands (Human-in-the-Loop)</h2>
                <div style="display: flex; justify-content: space-between; align-items: center; background: #000; padding: 1rem; border-radius: 4px; font-family: monospace;">
                    <span>$ npm install react-scripts</span>
                    <div>
                        <button class="btn btn-danger">Reject</button>
                        <button class="btn">Approve</button>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Agent Live Logs</h2>
                <div class="log-box">
                    > [INFO] Indexing codebase with LanceDB...<br>
                    > [INFO] Indexed 42 files.<br>
                    > [DEBUG] Received proxy request from Claude CLI.<br>
                    > [GUARDIAN] Prompt analysis passed.<br>
                    > [ROUTER] Forwarding to DeepSeek V3...
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
