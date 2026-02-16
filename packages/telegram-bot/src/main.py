from fastapi import FastAPI, Request
from config.settings import get_settings
from src.bot import GenealogyBot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Genealogy Telegram Bot",
    version="0.1.0"
)

bot = GenealogyBot()
telegram_app = bot.setup()

@app.on_event("startup")
async def startup():
    """Initialize bot on startup"""
    await telegram_app.bot.set_webhook(settings.telegram_webhook_url)
    logger.info("Bot started")

@app.post("/telegram/webhook")
async def handle_telegram(request: Request):
    """Handle Telegram webhook"""
    try:
        data = await request.json()
        update = telegram_app.update_queue.get(data)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return {"status": "error"}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Genealogy Telegram Bot",
        "version": "0.1.0"
    }
