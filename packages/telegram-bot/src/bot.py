from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from config.settings import get_settings
import logging
import httpx
import os
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

class GenealogyBot:
    def __init__(self):
        self.application = None
        self.backend_url = settings.backend_service_url
        self.ingestion_url = settings.ingestion_service_url
        self.headers = {
            "Authorization": f"Bearer {settings.backend_api_key}"
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        await update.message.reply_text(
            "Welcome to Genealogy Bot! 👋\n\n"
            "I can help you import genealogical data through various methods:\n\n"
            "📝 *Text messages* - Describe your family information\n"
            "🎤 *Voice messages* - Tell your family stories\n"
            "📷 *Images/PDFs* - Upload family documents or photos with text\n"
            "👥 *Contacts* - Send me vCard/CardDAV files\n\n"
            "Commands:\n"
            "/start - Show this help message\n"
            "/help - Show detailed help\n"
            "/status - Check your import status\n",
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await update.message.reply_text(
            "📚 *Genealogy Data Import Guide*\n\n"
            "1. **Text Format**: Simply type information like:\n"
            "   'My grandfather John Smith was born in 1920 in London'\n\n"
            "2. **Voice Messages**: Record family stories, names, dates\n\n"
            "3. **Documents**: Upload PDF documents or images of documents\n\n"
            "4. **Contacts**: Share vCard files with contact info\n\n"
            "The AI will extract and organize the data automatically! 🤖",
            parse_mode="Markdown"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        await update.message.reply_text("Processing your message... ⏳")
        
        try:
            async with httpx.AsyncClient() as client:
                # Send to ingestion service
                response = await client.post(
                    f"{self.ingestion_url}/api/ingest/text",
                    json={
                        "content": message_text,
                        "content_type": "text",
                        "source_type": "telegram",
                        "source_id": str(user_id)
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    entities = data.get('extracted_entities', [])
                    
                    if entities:
                        message = "✅ *Successfully extracted the following information:*\n\n"
                        for entity in entities:
                            entity_type = entity['entity_type']
                            confidence = entity['confidence']
                            message += f"🏷️ *{entity_type}* (Confidence: {confidence:.0%})\n"
                            for key, value in entity['data'].items():
                                if value:
                                    message += f"  • {key}: {value}\n"
                            message += "\n"
                        
                        await update.message.reply_text(message, parse_mode="Markdown")
                    else:
                        await update.message.reply_text(
                            "ℹ️ No genealogical information found in your message. "
                            "Try providing names, dates, places, or relationships!"
                        )
                else:
                    await update.message.reply_text("❌ Error processing message. Please try again.")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("Downloading and processing your voice message... 🎤")
        
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_path = f"./uploads/{user_id}_voice_{voice_file.file_id}.ogg"
            os.makedirs("./uploads", exist_ok=True)
            await voice_file.download_to_drive(voice_path)
            
            async with httpx.AsyncClient() as client:
                with open(voice_path, 'rb') as f:
                    response = await client.post(
                        f"{self.ingestion_url}/api/ingest/voice",
                        files={"file": f},
                        timeout=60
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    entities = data.get('extracted_entities', [])
                    transcript = data.get('raw_response', '')
                    
                    message = f"📝 *Transcript:*\n{transcript}\n\n"
                    
                    if entities:
                        message += "✅ *Extracted Information:*\n\n"
                        for entity in entities:
                            entity_type = entity['entity_type']
                            confidence = entity['confidence']
                            message += f"🏷️ *{entity_type}* (Confidence: {confidence:.0%})\n"
                            for key, value in entity['data'].items():
                                if value:
                                    message += f"  • {key}: {value}\n"
                            message += "\n"
                    
                    await update.message.reply_text(message, parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ Error processing voice message.")
            
            # Cleanup
            os.remove(voice_path)
        
        except Exception as e:
            logger.error(f"Error processing voice: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle documents (PDF, images)"""
        user_id = update.effective_user.id
        document = update.message.document
        
        if document:
            await update.message.reply_text("Downloading and processing your document... 📄")
            
            try:
                # Download document
                doc_file = await document.get_file()
                doc_path = f"./uploads/{user_id}_{document.file_id}"
                os.makedirs("./uploads", exist_ok=True)
                await doc_file.download_to_drive(doc_path)
                
                # Determine file type and send to appropriate endpoint
                file_ext = os.path.splitext(document.file_name)[1].lower()
                
                if file_ext == '.pdf':
                    endpoint = "/api/ingest/pdf"
                elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    endpoint = "/api/ingest/image"
                else:
                    os.remove(doc_path)
                    await update.message.reply_text(
                        "❌ Unsupported file format. Supported: PDF, JPG, PNG, GIF, BMP"
                    )
                    return
                
                async with httpx.AsyncClient() as client:
                    with open(doc_path, 'rb') as f:
                        response = await client.post(
                            f"{self.ingestion_url}{endpoint}",
                            files={"file": f},
                            timeout=60
                        )
                    
                    if response.status_code == 200:
                        data = response.json()
                        entities = data.get('extracted_entities', [])
                        
                        message = "✅ *Successfully processed document*\n\n"
                        
                        if entities:
                            for entity in entities:
                                entity_type = entity['entity_type']
                                confidence = entity['confidence']
                                message += f"🏷️ *{entity_type}* (Confidence: {confidence:.0%})\n"
                                for key, value in entity['data'].items():
                                    if value:
                                        message += f"  • {key}: {value}\n"
                        
                        await update.message.reply_text(message, parse_mode="Markdown")
                    else:
                        await update.message.reply_text("❌ Error processing document.")
                
                os.remove(doc_path)
            
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def setup(self):
        """Setup bot handlers"""
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        
        # Commands
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        
        return self.application

async def main():
    """Start the bot"""
    bot = GenealogyBot()
    app = bot.setup()
    
    # Start polling
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
