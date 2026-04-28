import uvicorn
from fastapi import FastAPI
from loguru import logger
from src.proxy.router import router as proxy_router
from src.dashboard.app import router as dashboard_router

app = FastAPI(
    title="Advanced Claude Proxy",
    description="Secure, sandboxed local proxy for Claude Code.",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(proxy_router)
app.include_router(dashboard_router)

def run():
    logger.info("Starting Advanced Claude Proxy...")
    uvicorn.run("src.main:app", host="127.0.0.1", port=8082, reload=True)

if __name__ == "__main__":
    run()
