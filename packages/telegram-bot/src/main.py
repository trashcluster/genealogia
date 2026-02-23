from fastapi import FastAPI, Request
from config.settings import get_settings
from src.bot import GenealogyBot
from src.conversation_engine import ConversationEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Genealogy Telegram Bot",
    version="0.1.0"
)

# Initialize conversation engine
conversation_engine = ConversationEngine(
    ingestion_service_url=settings.ingestion_service_url,
    backend_service_url=settings.backend_service_url
)

bot = GenealogyBot(conversation_engine)
telegram_app = bot.setup()

@app.on_event("startup")
async def startup():
    """Initialize bot on startup"""
    await telegram_app.bot.set_webhook(settings.telegram_webhook_url)
    logger.info("Bot started with conversation engine")

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

@app.get("/conversation/{user_id}/{chat_id}")
async def get_conversation_status(user_id: str, chat_id: str):
    """Get conversation status for debugging"""
    try:
        status = await conversation_engine.get_conversation_status(user_id, chat_id)
        return {"status": status}
    except Exception as e:
        logger.error(f"Error getting conversation status: {e}")
        return {"error": str(e)}

@app.delete("/conversation/{user_id}/{chat_id}")
async def end_conversation(user_id: str, chat_id: str):
    """End conversation"""
    try:
        success = await conversation_engine.end_conversation(user_id, chat_id)
        return {"ended": success}
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "conversation_engine": "active",
        "active_conversations": len(conversation_engine.active_conversations)
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Genealogy Telegram Bot with Interactive Conversation",
        "version": "0.1.0"
    }
